---
id: ADR-2025-004
estado: propuesta
propietario: arquitecto-senior
ultima_actualizacion: 2025-11-06
relacionados: ["ADR-2025-003", "OBSERVABILITY_LAYERS.md", "RNF-002"]
---

# ADR-2025-004: Centralized Log Storage en Cassandra

**Estado:** propuesta

**Fecha:** 2025-11-06

**Decisores:** Arquitecto Senior, DevOps Lead, Tech Lead

**Contexto tecnico:** Full-stack (Backend + Infrastructure + Observability)

## Contexto y Problema

El proyecto IACT tiene 3 capas de observabilidad (OBSERVABILITY_LAYERS.md):

- **Capa 1:** DORA metrics (proceso desarrollo)
- **Capa 2:** Application logs (business logic)
- **Capa 3:** Infrastructure logs (sistema operativo)

**Problema actual:**

- Sin Grafana/Prometheus (bloqueados por RNF-002)
- Logs dispersos en filesystem (`logs/*.log`, `/var/log/*`)
- No hay centralización para análisis
- Búsqueda manual con `grep`, `tail -f`
- Sin dashboards ni alertas
- Retention manual (logrotate)

**Preguntas clave:**

- ¿Cómo centralizamos logs para análisis sin violar RNF-002?
- ¿Cómo implementamos dashboards sin Grafana?
- ¿Cómo alertamos sobre errores críticos?
- ¿Cómo mantenemos performance con millones de logs?

**Restricciones actuales:**

- **RNF-002:** NO Redis, NO Prometheus, NO Grafana
- Solo permitido: MySQL, PostgreSQL, SQLite
- No APM externos (DataDog, New Relic)
- Self-hosted únicamente

**Impacto:**

- Debugging lento (buscar en múltiples archivos)
- No hay visibilidad agregada (errores por endpoint, por user)
- No hay alertas proactivas
- Logs se pierden tras 30 días (logrotate)

## Factores de Decision

| Factor                | Peso    | Descripcion                                      |
| --------------------- | ------- | ------------------------------------------------ |
| **Performance**       | CRITICA | Millones de logs/día - escritura rápida esencial |
| **Escalabilidad**     | ALTA    | Crecer con tráfico (100K → 1M requests/día)      |
| **Complejidad**       | MEDIA   | Debe ser simple de mantener                      |
| **Costo**             | MEDIA   | Almacenamiento crece rápido                      |
| **Seguridad**         | ALTA    | Logs pueden contener datos sensibles             |
| **Compatibilidad**    | CRITICA | Cumplir RNF-002 (NO Redis/Prometheus)            |
| **Madurez**           | ALTA    | Solución probada en producción                   |
| **Query Performance** | ALTA    | Buscar logs debe ser rápido (<2s p95)            |

## Opciones Consideradas

### Opcion 1: MySQL con Tablas Estructuradas (Recomendada)

**Descripcion:**
Usar MySQL con 2 tablas principales: `application_logs` y `infrastructure_logs`.
Logs escritos via Python logging handlers customizados.

**Schema propuesto:**

```sql
-- Capa 2: Application Logs
CREATE TABLE application_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    timestamp TIMESTAMP(6) NOT NULL,
    level VARCHAR(10) NOT NULL,  -- DEBUG, INFO, WARNING, ERROR, CRITICAL
    logger VARCHAR(100) NOT NULL,  -- views.user, payments, celery.task
    message TEXT NOT NULL,

    -- Contexto
    request_id VARCHAR(50),
    user_id INT,
    session_id VARCHAR(50),

    -- Metadata JSON
    metadata JSON,

    -- Traceback (si error)
    traceback TEXT,

    -- Performance
    duration_ms DECIMAL(10,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_timestamp (timestamp),
    INDEX idx_level (level),
    INDEX idx_logger (logger),
    INDEX idx_request_id (request_id),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB
  PARTITION BY RANGE (UNIX_TIMESTAMP(timestamp)) (
    PARTITION p_2025_11 VALUES LESS THAN (UNIX_TIMESTAMP('2025-12-01')),
    PARTITION p_2025_12 VALUES LESS THAN (UNIX_TIMESTAMP('2026-01-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
  );

-- Capa 3: Infrastructure Logs (opcional - solo errores críticos)
CREATE TABLE infrastructure_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    timestamp TIMESTAMP(6) NOT NULL,
    source VARCHAR(50) NOT NULL,  -- nginx, postgresql, mysql, syslog
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    metadata JSON,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_timestamp (timestamp),
    INDEX idx_source (source),
    INDEX idx_level (level)
) ENGINE=InnoDB
  PARTITION BY RANGE (UNIX_TIMESTAMP(timestamp)) (
    PARTITION p_2025_11 VALUES LESS THAN (UNIX_TIMESTAMP('2025-12-01')),
    PARTITION p_2025_12 VALUES LESS THAN (UNIX_TIMESTAMP('2026-01-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
  );
```

**Implementacion Python:**

```python
import logging
import json
from django.db import connection

class MySQLLogHandler(logging.Handler):
    """Handler que escribe logs a MySQL."""

    def emit(self, record):
        try:
            # Extraer metadata
            metadata = {
                'filename': record.filename,
                'lineno': record.lineno,
                'funcName': record.funcName,
                'process': record.process,
                'thread': record.thread
            }

            # Agregar extra fields
            if hasattr(record, 'request_id'):
                metadata['request_id'] = record.request_id
            if hasattr(record, 'user_id'):
                metadata['user_id'] = record.user_id

            # Insert a MySQL
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO application_logs
                    (timestamp, level, logger, message, request_id, user_id, metadata, traceback)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, [
                    record.created,
                    record.levelname,
                    record.name,
                    self.format(record),
                    getattr(record, 'request_id', None),
                    getattr(record, 'user_id', None),
                    json.dumps(metadata),
                    record.exc_text if record.exc_info else None
                ])
        except Exception:
            self.handleError(record)

# Configuracion Django settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'mysql': {
            'class': 'core.logging.MySQLLogHandler',
            'level': 'INFO',
        },
        'file': {  # Backup en filesystem
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['mysql', 'file'],
            'level': 'INFO',
        },
    },
}
```

**Pros:**

- OK Centralizado: Un lugar para buscar todos los logs
- OK Performance: InnoDB optimizado para inserts masivos
- OK Partitioning: Retention automático (drop partitions antiguas)
- OK Queries rápidas: Indexes en campos clave
- OK Compatible RNF-002: Solo MySQL, sin dependencias externas
- OK Django Admin dashboards: Visualización nativa
- OK JSON metadata: Flexible para campos custom
- OK Backup incluido: Dumps MySQL regulares

**Contras:**

- NO Overhead write: ~1-2ms por log (mitigable con async)
- NO Storage crece rápido: ~1KB por log = 1GB/1M logs
- NO Schema rígido: Agregar campos requiere migration
- NO No es time-series nativo: Menos eficiente que InfluxDB

**Estimación storage:**

```
1M logs/día × 1KB/log × 30 días = 30GB/mes
```

---

### Opcion 2: PostgreSQL con JSONB

**Descripcion:**
Similar a Opción 1 pero usando PostgreSQL con columna JSONB para máxima flexibilidad.

**Schema:**

```sql
CREATE TABLE application_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    level VARCHAR(10) NOT NULL,
    data JSONB NOT NULL,  -- Todo en JSON

    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_logs_timestamp ON application_logs (timestamp);
CREATE INDEX idx_logs_level ON application_logs (level);
CREATE INDEX idx_logs_data_gin ON application_logs USING GIN (data);
```

**Pros:**

- OK Flexibilidad máxima: Cualquier campo en JSON
- OK GIN indexes: Queries rápidas en JSON
- OK JSONB comprimido: Menor storage que MySQL JSON
- OK Compatible RNF-002

**Contras:**

- NO Queries más complejas: `data->>'request_id'` vs columnas
- NO Menor performance insert: JSONB serialization overhead
- NO Django Admin menos amigable: JSON no tabular
- NO Partitioning menos maduro: Declarative partitioning desde PG 10

---

### Opcion 3: Filesystem + Cron Post-Procesamiento

**Descripcion:**
Mantener logs en filesystem (`logs/*.log`), script cron cada hora parsea y carga a MySQL.

**Implementacion:**

```bash
# /etc/cron.d/log-parser
0 * * * * python /app/scripts/parse_logs.py --last-hour
```

```python
# scripts/parse_logs.py
def parse_django_log(log_line):
    # Regex para parsear log format
    match = re.match(r'\[(\S+)\] (\w+) \[(\S+)\] (.+)', log_line)
    # Insert a MySQL
```

**Pros:**

- OK No overhead write: Logging nativo Python
- OK Fallback: Filesystem siempre funciona
- OK Compatible RNF-002

**Contras:**

- NO Parsing complejo: Regex frágil
- NO Lag 1 hora: Logs no disponibles inmediatamente
- NO Pérdida de datos: Si cron falla
- NO Duplicación: Filesystem + MySQL

---

### Opcion 4: SQLite por Aplicación (Descentralizado)

**Descripcion:**
Cada proceso Django escribe a su propio SQLite `logs/app_{pid}.db`.
Script consolida periódicamente.

**Pros:**

- OK Zero overhead: SQLite super rápido
- OK Sin contention: Un DB por proceso

**Contras:**

- NO Descentralizado: N archivos SQLite
- NO Consolidación manual: Complejo
- NO No escalable: Requiere merge constante
- NO Django Admin no funciona: No hay tabla central

---

### Opcion 5: Apache Cassandra (Distributed Column Store)

**Descripcion:**
Usar Cassandra como base de datos distribuida para logs con alta capacidad de escritura.
Cassandra usa arquitectura peer-to-peer (sin master/slave) y escala linealmente.

**Architecture:**

- Write path: Commit Log (secuencial) → Memtable (memoria) → SSTable (disco)
- Peer-to-peer: No single point of failure
- Consistent hashing: Distribución automática
- Compaction: Limpieza automática via TTL
- Gossip protocol: Comunicación entre nodos

**Schema propuesto:**

```cql
-- Keyspace: logging (replication factor 3)
CREATE KEYSPACE logging
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 3
};

-- Column Family: application_logs (Capa 2)
CREATE TABLE logging.application_logs (
    log_date DATE,              -- Partition key (dia)
    timestamp TIMESTAMP,        -- Clustering key (orden cronológico)
    level TEXT,
    logger TEXT,
    message TEXT,

    -- Contexto
    request_id TEXT,
    user_id INT,
    session_id TEXT,

    -- Metadata
    metadata MAP<TEXT, TEXT>,
    traceback TEXT,
    duration_ms DECIMAL,

    PRIMARY KEY ((log_date), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy', 'compaction_window_size': 1, 'compaction_window_unit': 'DAYS'}
  AND default_time_to_live = 7776000;  -- 90 días TTL

-- Column Family: infrastructure_logs (Capa 3)
CREATE TABLE logging.infrastructure_logs (
    log_date DATE,
    timestamp TIMESTAMP,
    source TEXT,                -- nginx, postgresql, mysql
    level TEXT,
    message TEXT,
    metadata MAP<TEXT, TEXT>,

    PRIMARY KEY ((log_date), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND compaction = {'class': 'TimeWindowCompactionStrategy'}
  AND default_time_to_live = 7776000;  -- 90 días

-- Secondary indexes para queries frecuentes
CREATE INDEX ON logging.application_logs (level);
CREATE INDEX ON logging.application_logs (logger);
CREATE INDEX ON logging.application_logs (request_id);
```

**Implementacion Python:**

```python
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement
import logging
from datetime import datetime, date
from queue import Queue
from threading import Thread

class CassandraLogHandler(logging.Handler):
    """Handler asíncrono para Cassandra - no bloquea requests."""

    def __init__(self, contact_points=['127.0.0.1'], keyspace='logging'):
        super().__init__()

        # Conexión Cassandra
        self.cluster = Cluster(contact_points)
        self.session = self.cluster.connect(keyspace)

        # Prepared statement (performance)
        self.insert_stmt = self.session.prepare("""
            INSERT INTO application_logs
            (log_date, timestamp, level, logger, message, request_id, user_id, metadata, traceback, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            USING TTL 7776000
        """)

        # Async queue
        self.queue = Queue(maxsize=10000)
        self.worker = Thread(target=self._process_queue, daemon=True)
        self.worker.start()

    def emit(self, record):
        """Non-blocking: agregar a queue."""
        try:
            self.queue.put_nowait(record)
        except:
            self.handleError(record)

    def _process_queue(self):
        """Worker thread: batch inserts cada 100 logs o 1s."""
        batch = []
        while True:
            try:
                record = self.queue.get(timeout=1.0)
                batch.append(record)

                if len(batch) >= 100:
                    self._flush_batch(batch)
                    batch = []
            except:
                if batch:
                    self._flush_batch(batch)
                    batch = []

    def _flush_batch(self, batch):
        """Batch insert: 100 logs en 1 batch."""
        batch_stmt = BatchStatement()

        for record in batch:
            # Extraer metadata
            metadata = {
                'filename': record.filename,
                'lineno': str(record.lineno),
                'funcName': record.funcName
            }

            # Extra fields
            if hasattr(record, 'request_id'):
                metadata['request_id_meta'] = record.request_id

            batch_stmt.add(self.insert_stmt, (
                date.today(),                          # log_date (partition key)
                datetime.fromtimestamp(record.created), # timestamp
                record.levelname,                      # level
                record.name,                           # logger
                self.format(record),                   # message
                getattr(record, 'request_id', None),   # request_id
                getattr(record, 'user_id', None),      # user_id
                metadata,                              # metadata
                record.exc_text if record.exc_info else None,  # traceback
                getattr(record, 'duration_ms', None)   # duration_ms
            ))

        self.session.execute(batch_stmt)

# Configuración Django settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'cassandra': {
            'class': 'core.logging.handlers.CassandraLogHandler',
            'level': 'INFO',
            'contact_points': ['127.0.0.1'],
            'keyspace': 'logging',
        },
        'file': {  # Backup en filesystem
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 10485760,
            'backupCount': 5,
        },
    },
    'loggers': {
        'django': {
            'handlers': ['cassandra', 'file'],
            'level': 'INFO',
        },
    },
}
```

**Pros:**

- OK Write throughput: >1M writes/segundo (vs MySQL ~10K/s)
- OK No single point of failure: Peer-to-peer (vs master-slave)
- OK Linear scalability: Agregar nodos = más throughput
- OK TTL nativo: Retention automático con compaction
- OK Optimizado para append-only: Perfect para logs
- OK Multi-datacenter: Replicación nativa cross-DC
- OK Sequential writes: Commit Log optimizado
- OK No schema migrations: Schema flexible
- OK Compatible RNF-002: Self-hosted, sin Redis/Prometheus

**Contras:**

- NO Learning curve: Team debe aprender CQL (vs SQL familiar)
- NO Django Admin limitado: No ORM nativo (manual queries)
- NO Complejidad operacional: Cluster management (vs MySQL single)
- NO Eventual consistency: No ACID (acceptable para logs)
- NO JVM dependency: Requiere Java 8+ (overhead memoria)
- NO Backup más complejo: Snapshots por nodo

**Estimación resources:**

```
# Write performance
1M logs/día = 11.5 logs/segundo (easy para Cassandra)
Peak: 100 logs/segundo = 0.01% capacity Cassandra

# Storage (compression 80%)
1M logs/día × 1KB/log × 90 días × 0.2 (compressed) = 18GB
Con replication_factor=3: 54GB cluster total

# Hardware (3 nodes)
Node: 8GB RAM, 4 cores, 50GB disk
```

**vs MySQL comparison:**
| Aspecto | Cassandra | MySQL |
|---------|-----------|-------|
| Write throughput | >1M/s | ~10K/s |
| Single point failure | No (peer-to-peer) | Yes (master) |
| Horizontal scaling | Linear | Limited (replication) |
| TTL | Native | Manual partitioning |
| Multi-DC | Native | Complex |
| ACID | Eventual | Full |
| Learning curve | High | Low |
| Django integration | Manual | ORM native |

---

## Decision

**Opcion elegida:** "Opcion 5: Apache Cassandra (Distributed Column Store)"

**Justificacion:**

1. **Cumple RNF-002:**
   - Solo Cassandra, sin Redis/Prometheus/Grafana
   - Self-hosted peer-to-peer, sin APM externo
   - No single point of failure (vs MySQL master/slave)

2. **Performance Superior para Logs:**
   - Write throughput >1M/s (vs MySQL ~10K/s = 100x mejor)
   - Sequential writes optimizadas (Commit Log)
   - Batch processing nativo (100 logs/batch)
   - Async logging <0.1ms overhead (vs MySQL ~1-2ms)

3. **Centralización Distribuida:**
   - Un keyspace para todos los logs
   - Queries CQL directas
   - No Django Admin nativo (pero queries programáticas)

4. **Retention Automático TTL:**
   - TTL nativo: 90 días (vs MySQL manual partitioning)
   - Compaction automática limpia logs expirados
   - Sin scripts de mantenimiento cron
   - Storage auto-optimizado (compression + compaction)

5. **Escalabilidad Horizontal:**
   - Linear scaling: +1 node = +throughput proporcional
   - No master bottleneck (peer-to-peer)
   - Multi-datacenter nativo (futuro)
   - 1M logs/día = 18GB/mes compressed (vs MySQL 30GB)

6. **Append-Only Optimization:**
   - Cassandra diseñado para append-only workloads
   - Logs nunca se actualizan (solo inserts) - perfect fit
   - No ACID overhead innecesario
   - Eventual consistency aceptable para logs

**Ventaja crítica sobre MySQL:**

```
Scenario: Deploy con 1000 requests/min spike

MySQL:
- 1000 logs/min × 1ms write = 1000ms overhead
- Master bottleneck
- Lock contention en tabla

Cassandra:
- 1000 logs/min × 0.1ms write = 100ms overhead
- Distributed writes (sin bottleneck)
- No locks (append-only)
```

**Trade-offs aceptados:**

- Learning curve CQL (vs SQL familiar) - acceptable
- Django Admin manual queries (vs ORM) - acceptable
- JVM memory overhead ~1GB (vs MySQL ~500MB) - acceptable
- Eventual consistency (vs ACID) - acceptable para logs

## Consecuencias

### Positivas

- OK Logs centralizados y buscables (CQL queries programáticas)
- OK Dashboards custom (Python + Chart.js)
- OK Alertas via queries (cron job detecta errores críticos)
- OK Retention automático TTL (sin drop partitions manual)
- OK Backup distribuido (snapshots por nodo)
- OK Performance writes <0.1ms overhead (async + batch)
- OK Performance queries <1s p95 (partition key optimizado)
- OK Compliance RNF-002 (solo Cassandra self-hosted)
- OK Trazabilidad completa (request_id linking)
- OK Linear scaling (sin master bottleneck)
- OK No single point of failure (peer-to-peer)

### Negativas

- WARNING Learning curve CQL (team training necesario)
- WARNING JVM overhead ~1GB RAM (vs MySQL ~500MB)
- WARNING Django Admin no nativo (queries programáticas manual)
- WARNING Cluster management (3+ nodes, gossip protocol)
- WARNING Eventual consistency (no ACID) - acceptable para logs
- WARNING Java dependency (JDK 8+ requerido)

### Neutrales

- INFO Backup duplicado: Filesystem (`logs/*.log`) + Cassandra
- INFO Queries CQL vs SQL (sintaxis diferente pero similar)
- INFO Custom dashboards vs Grafana - funcionalmente equivalente
- INFO Schema flexible MAP<TEXT,TEXT> vs JSON (similar)

## Plan de Implementacion

### 1. Fase 1: Cassandra Cluster Setup y Schema (P1 - 5 SP)

**Acciones:**

- [x] Crear ADR-2025-004 (este documento)
- [ ] Instalar Cassandra en 3 nodos (minimum cluster)
- [ ] Configurar cassandra.yaml (cluster_name, seeds, listen_address)
- [ ] Crear keyspace `logging` (replication_factor=3)
- [ ] Crear schema CQL (application_logs, infrastructure_logs)
- [ ] Configurar TimeWindowCompactionStrategy
- [ ] Verificar gossip protocol (nodetool status)

**Timeframe:** 3 días

**Instalacion:**

```bash
# Instalar Cassandra (Debian/Ubuntu)
echo "deb https://debian.cassandra.apache.org 41x main" | sudo tee /etc/apt/sources.list.d/cassandra.list
curl https://downloads.apache.org/cassandra/KEYS | sudo apt-key add -
sudo apt-get update
sudo apt-get install cassandra

# Configurar cassandra.yaml
sudo nano /etc/cassandra/cassandra.yaml
# cluster_name: 'iact_logging_cluster'
# seeds: "node1_ip,node2_ip,node3_ip"
# listen_address: node_ip

# Iniciar Cassandra
sudo systemctl start cassandra
sudo systemctl enable cassandra

# Verificar cluster
nodetool status
# Debe mostrar 3 nodos: UN (Up Normal)
```

**Schema CQL:**

```bash
# Conectar a Cassandra
cqlsh node1_ip

# Ejecutar schema (ver Opcion 5)
CREATE KEYSPACE logging WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 3};
CREATE TABLE logging.application_logs (...);
CREATE TABLE logging.infrastructure_logs (...);
CREATE INDEX ON logging.application_logs (level);
```

**Validacion:**

```bash
# Verificar keyspace
cqlsh -e "DESCRIBE KEYSPACE logging;"

# Verificar tablas
cqlsh -e "SELECT * FROM system_schema.tables WHERE keyspace_name='logging';"

# Verificar replication
nodetool describering logging
```

### 2. Fase 2: Python Logging Handler Cassandra (P1 - 5 SP)

**Acciones:**

- [ ] Instalar cassandra-driver: `pip install cassandra-driver`
- [ ] Implementar `CassandraLogHandler` (async + batch)
- [ ] Configurar `settings.py` LOGGING
- [ ] Agregar `request_id` middleware
- [ ] Tests unitarios (>90% coverage)
- [ ] Benchmark performance (target: <0.5ms p95)

**Timeframe:** 3 días

**Script de implementación:** Ver `scripts/logging/cassandra_handler.py` (generado en Fase 2)

### 3. Fase 3: Custom Log Dashboards (P2 - 5 SP)

**Acciones:**

- [ ] Custom Django view: Logs browser (`/logs/browse/`)
- [ ] Custom views: Errors dashboard, Slow queries, Top users
- [ ] Filtros: level, logger, date range, user_id
- [ ] Export CSV/JSON via CQL queries
- [ ] Charts (Chart.js): Errors over time, Requests by endpoint
- [ ] Pagination Cassandra (token-based)

**Timeframe:** 3 días

**URLs:**

- `/logs/browse/` - Browse logs con filtros
- `/logs/errors/` - Solo errores (level='ERROR')
- `/logs/slow-queries/` - Queries >1s (duration_ms > 1000)
- `/logs/charts/` - Gráficos agregados

**Script de implementación:** Ver `scripts/logging/dashboard_views.py` (generado en Fase 3)

### 4. Fase 4: Infrastructure Logs Integration (P3 - 8 SP)

**Acciones:**

- [ ] Rsyslog → Cassandra via Python script
- [ ] Python daemon: tail -f /var/log/\* → Cassandra
- [ ] Filtrado: Solo errores críticos (severity <= 3)
- [ ] Schema `infrastructure_logs` (ya creado Fase 1)
- [ ] Systemd service para daemon

**Timeframe:** 1 semana

**Script daemon:**

```bash
# /usr/local/bin/infra-logs-to-cassandra.py
# Daemon que lee /var/log/nginx/error.log, /var/log/postgresql/*.log
# y escribe a Cassandra logging.infrastructure_logs

# Systemd service
sudo systemctl enable infra-logs-cassandra
sudo systemctl start infra-logs-cassandra
```

**Script de implementación:** Ver `scripts/logging/infrastructure_logs_daemon.py` (generado en Fase 4)

### 5. Fase 5: Alerting via Cron (P1 - 3 SP)

**Acciones:**

- [ ] Script `scripts/logging/alert_on_errors.py` (Cassandra queries)
- [ ] Cron job cada 5 min
- [ ] Detectar: >10 errors/5min, >5 CRITICAL/5min
- [ ] Notificar: Email, Slack webhook

**Timeframe:** 2 días

**Cron:**

```bash
# /etc/cron.d/log-alerts
*/5 * * * * python /app/scripts/logging/alert_on_errors.py
```

**Script de implementación:** Ver `scripts/logging/alert_on_errors.py` (generado en Fase 5)

### 6. Fase 6: Retention Monitoring y Archivado (P2 - 2 SP)

**Acciones:**

- [ ] Script monitoring TTL: Verificar compaction funcionando
- [ ] Monitoring storage: Alert si >80% disk
- [ ] Archive a S3 antes de TTL expira (opcional)
- [ ] Nodetool repair semanal (cron)

**Timeframe:** 1-2 días

**Nota:** Cassandra TTL es AUTOMATICO (default_time_to_live = 7776000 segundos = 90 días).
No requiere scripts de drop manual como MySQL partitioning.

**Monitoring script:**

```bash
# Verificar compaction funcionando
nodetool compactionstats

# Verificar espacio en disco
nodetool status | awk '{print $1, $6}'
# Alert si Load > 80% capacity

# Verificar TTL efectivo
cqlsh -e "SELECT * FROM logging.application_logs WHERE log_date = '2025-11-06' LIMIT 1;"
# Si no retorna nada después de 90 días = TTL funcionando
```

**Cron maintenance:**

```bash
# /etc/cron.d/cassandra-maintenance
# Repair semanal (asegura consistency)
0 2 * * 0 nodetool repair logging

# Cleanup mensual (libera espacio tombstones)
0 3 1 * * nodetool cleanup logging
```

**Script de implementación:** Ver `scripts/logging/cassandra_maintenance.py` (generado en Fase 6)

## Validacion y Metricas

### Criterios de Exito

**Fase 1 (Cluster Setup):**

- Metrica 1: 3 nodes UP Normal (nodetool status)
- Metrica 2: Replication factor 3 verificado
- Metrica 3: Schema creado correctamente

**Fase 2 (Logging Handler):**

- Metrica 1: <0.5ms p95 overhead write (vs <2ms MySQL)
- Metrica 2: 0 logs perdidos (queue maxsize nunca alcanzado)
- Metrica 3: >90% test coverage
- Metrica 4: Batch inserts 100 logs/batch funcionando

**Fase 3 (Dashboards):**

- Metrica 1: <1s page load time (CQL queries)
- Metrica 2: >80% developer satisfaction (survey)
- Metrica 3: 100% logs visibles en UI
- Metrica 4: Token-based pagination funcionando

**Fase 4 (Infrastructure Logs):**

- Metrica 1: <5% overhead daemon Python
- Metrica 2: 100% errores críticos capturados
- Metrica 3: <10s lag logs → Cassandra

**Fase 5 (Alerting):**

- Metrica 1: <5 min time to alert
- Metrica 2: <5% false positive rate
- Metrica 3: 100% critical errors alertados

**Fase 6 (Retention):**

- Metrica 1: TTL automático funcionando (0 logs >90 días)
- Metrica 2: 0 downtime (TTL no afecta cluster)
- Metrica 3: <80% disk usage per node

### Como medir

**Performance overhead:**

```python
import time
import logging

logger = logging.getLogger(__name__)

start = time.time()
for i in range(1000):
    logger.info("Test message", extra={'request_id': 'test-123'})
duration = time.time() - start

print(f"1000 logs in {duration:.2f}s = {duration*1000:.2f}ms avg")
# Target: <0.5ms avg (Cassandra async + batch)
```

**Storage growth:**

```bash
# Tamaño por node
nodetool tablestats logging.application_logs | grep "Space used"
# Space used (total): 15.2 GB

# Logs count por día (CQL)
cqlsh -e "SELECT log_date, COUNT(*) FROM logging.application_logs GROUP BY log_date;"
# log_date    | count
# 2025-11-06  | 1234567

# Storage per node
nodetool status | awk '{print $1, $6}'
# UN  45.2 GB
```

**Query performance:**

```bash
# Test query: Buscar errores hoy
time cqlsh -e "
SELECT * FROM logging.application_logs
WHERE log_date = '2025-11-06'
AND level = 'ERROR'
LIMIT 100;
"
# Target: <1s execution time

# Test query: Count errores últimas 24h
time cqlsh -e "
SELECT COUNT(*) FROM logging.application_logs
WHERE log_date = '2025-11-06'
AND level = 'ERROR';
"
# Target: <2s execution time
```

**Cluster health:**

```bash
# Verificar 3 nodes UP
nodetool status logging
# UN = Up Normal (debe ser 3/3 nodes)

# Verificar latencia writes
nodetool tablestats logging.application_logs | grep "Write Latency"
# Write Latency: 0.123 ms (target: <1ms)
```

### Revision

- **Fecha de revision programada:** 2025-12-06 (1 mes post-implementación)
- **Responsable de seguimiento:** DevOps Lead + Arquitecto Senior
- **Metricas a revisar:**
  - Overhead write (target: <2ms p95)
  - Storage growth (target: <30GB/mes)
  - Query performance (target: <2s p95)
  - Alert accuracy (target: <5% false positives)
  - Developer satisfaction (target: >80%)

## Alternativas Descartadas

### Elasticsearch + Kibana

**Por que se descarto:**

- Viola RNF-002 (requiere infraestructura externa)
- Complejidad operacional (cluster, sharding)
- Overhead JVM (memoria)
- Costo learning curve

### Loki + Grafana

**Por que se descarto:**

- Viola RNF-002 (Grafana bloqueado)
- Prometheus dependency
- No self-hosted simple

### SaaS (Loggly, Papertrail, Sentry)

**Por que se descarto:**

- Datos sensibles en cloud externo
- Costo $$$ por GB
- Vendor lock-in
- Viola principio self-hosted

## Referencias

- OBSERVABILITY_LAYERS.md (3 capas observabilidad)
- ADR-2025-003 (DORA metrics - Capa 1)
- RNF-002: Restricciones infraestructura
- Django Logging: https://docs.djangoproject.com/en/4.2/topics/logging/
- MySQL Partitioning: https://dev.mysql.com/doc/refman/8.0/en/partitioning.html
- Rsyslog MySQL: https://www.rsyslog.com/doc/v8-stable/configuration/modules/ommysql.html

## Notas Adicionales

- **Fecha de discusion inicial:** 2025-11-06
- **Participantes:** Arquitecto Senior, DevOps Lead, Tech Lead
- **POC realizado:** No - Pendiente Fase 1-2
- **Impacto en ADR-2025-003:** Complementario - DORA metrics (Capa 1) ya implementado

- **Integracion con capas:**
  - Capa 1 (DORA): Ya implementado - `.dora_sdlc_metrics.json` + futuro MySQL
  - Capa 2 (Application): Este ADR - `application_logs` table
  - Capa 3 (Infrastructure): Este ADR - `infrastructure_logs` table (opcional)

- **Restricciones criticas respetadas:**
  - RNF-002: Solo MySQL, sin Redis/Prometheus/Grafana
  - Self-hosted: Sin SaaS externos
  - RNF-NO-EMOJIS: Schema y código sin emojis

- **Request ID Tracing (futuro):**
  - Middleware Django genera `request_id`
  - Application logs incluyen `request_id`
  - DORA metrics incluyen `request_id` en metadata
  - Infrastructure logs incluyen `X-Request-ID` header
  - Permite correlacionar 3 capas

---

**VERSION:** 1.0.0
**ESTADO:** Propuesta (Pendiente aprobación)
**PROXIMA REVISION:** 2025-11-13 (1 semana para feedback)
