---
id: ADR-2025-004
estado: propuesta
propietario: arquitecto-senior
ultima_actualizacion: 2025-11-06
relacionados: ["ADR-2025-003", "OBSERVABILITY_LAYERS.md", "RNF-002"]
---

# ADR-2025-004: Centralized Log Storage en MySQL

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

| Factor | Peso | Descripcion |
|--------|------|-------------|
| **Performance** | CRITICA | Millones de logs/día - escritura rápida esencial |
| **Escalabilidad** | ALTA | Crecer con tráfico (100K → 1M requests/día) |
| **Complejidad** | MEDIA | Debe ser simple de mantener |
| **Costo** | MEDIA | Almacenamiento crece rápido |
| **Seguridad** | ALTA | Logs pueden contener datos sensibles |
| **Compatibilidad** | CRITICA | Cumplir RNF-002 (NO Redis/Prometheus) |
| **Madurez** | ALTA | Solución probada en producción |
| **Query Performance** | ALTA | Buscar logs debe ser rápido (<2s p95) |

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

## Decision

**Opcion elegida:** "Opcion 1: MySQL con Tablas Estructuradas"

**Justificacion:**

1. **Cumple RNF-002:**
   - Solo MySQL, sin Redis/Prometheus/Grafana
   - Self-hosted, sin APM externo

2. **Performance Aceptable:**
   - InnoDB optimizado para writes concurrentes
   - Async logging mitiga overhead (<1ms)
   - Partitioning para queries rápidas

3. **Centralización:**
   - Un lugar para buscar todos los logs
   - Django Admin dashboards nativos
   - Queries SQL directas

4. **Retention Automático:**
   - Partitioning mensual
   - Drop partitions antiguas: `ALTER TABLE ... DROP PARTITION p_2025_10`
   - Backup selectivo (últimos 3 meses)

5. **Escalabilidad:**
   - 1M logs/día = 30GB/mes (manejable)
   - Read replicas para queries pesadas (futuro)
   - Archive a S3 después de 90 días (futuro)

6. **Django Integration:**
   - Django Admin ModelAdmin nativo
   - ORM queries: `ApplicationLog.objects.filter(level='ERROR')`
   - No requiere herramientas externas

**Trade-offs aceptados:**
- Overhead write ~1-2ms (mitigable con async)
- Storage crece rápido (30GB/mes)
- Schema menos flexible que JSONB (pero más performant)

## Consecuencias

### Positivas

- OK Logs centralizados y buscables (Django Admin + SQL)
- OK Dashboards nativos (Django Admin custom views)
- OK Alertas via queries (cron job detecta errores críticos)
- OK Retention automático (drop partitions)
- OK Backup incluido (mysqldump regular)
- OK Performance queries (<2s p95 con indexes)
- OK Compliance RNF-002 (solo MySQL)
- OK Trazabilidad completa (request_id linking)

### Negativas

- WARNING Overhead write 1-2ms por log (usar async logging)
- WARNING Storage 30GB/mes (monitorear, particionar, archivar)
- WARNING Schema migrations (agregar campos requiere ALTER TABLE)
- WARNING No es time-series nativo (menos eficiente que InfluxDB)

### Neutrales

- INFO Backup duplicado: Filesystem (`logs/*.log`) + MySQL
- INFO Queries SQL vs DSL (Grafana PromQL) - trade-off aceptable
- INFO Django Admin UI vs Grafana dashboards - funcionalmente equivalente

## Plan de Implementacion

### 1. Fase 1: Schema y Migrations (P1 - 3 SP)

**Acciones:**
- [x] Crear ADR-2025-004 (este documento)
- [ ] Diseñar schema completo (application_logs, infrastructure_logs)
- [ ] Django migration: `python manage.py makemigrations`
- [ ] Agregar partitioning inicial (3 meses)
- [ ] Indexes optimizados

**Timeframe:** 2 días

**Validacion:**
```sql
-- Verificar schema
SHOW CREATE TABLE application_logs;

-- Verificar partitions
SELECT PARTITION_NAME, TABLE_ROWS
FROM INFORMATION_SCHEMA.PARTITIONS
WHERE TABLE_NAME = 'application_logs';
```

### 2. Fase 2: Python Logging Handler (P1 - 5 SP)

**Acciones:**
- [ ] Implementar `MySQLLogHandler` (async)
- [ ] Configurar `settings.py` LOGGING
- [ ] Agregar `request_id` middleware
- [ ] Tests unitarios (>90% coverage)
- [ ] Benchmark performance (target: <2ms p95)

**Timeframe:** 3 días

**Implementacion:**
```python
# core/logging/handlers.py
import asyncio
import logging
from django.db import connection
from queue import Queue
from threading import Thread

class AsyncMySQLLogHandler(logging.Handler):
    """Handler asíncrono para MySQL - no bloquea request."""

    def __init__(self):
        super().__init__()
        self.queue = Queue(maxsize=10000)
        self.worker = Thread(target=self._process_queue, daemon=True)
        self.worker.start()

    def emit(self, record):
        # Non-blocking: agregar a queue
        try:
            self.queue.put_nowait(record)
        except:
            self.handleError(record)

    def _process_queue(self):
        """Worker thread: batch inserts cada 1s o 100 logs."""
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
        """Batch insert: 100 logs en 1 query."""
        with connection.cursor() as cursor:
            cursor.executemany("""
                INSERT INTO application_logs
                (timestamp, level, logger, message, request_id, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [(/* ... */)])
```

### 3. Fase 3: Django Admin Dashboards (P2 - 5 SP)

**Acciones:**
- [ ] ModelAdmin para ApplicationLog
- [ ] Custom views: Errors dashboard, Slow queries, Top users
- [ ] Filtros: level, logger, date range, user_id
- [ ] Export CSV/JSON
- [ ] Charts (Chart.js): Errors over time, Requests by endpoint

**Timeframe:** 3 días

**URLs:**
- `/admin/logs/applicationlog/` - Lista principal
- `/admin/logs/errors/` - Solo errores
- `/admin/logs/slow-queries/` - Queries >1s
- `/admin/logs/charts/` - Gráficos

### 4. Fase 4: Infrastructure Logs Integration (P3 - 8 SP)

**Acciones:**
- [ ] Rsyslog → MySQL (nginx, postgresql)
- [ ] Filebeat → MySQL (alternativa)
- [ ] Filtrado: Solo errores críticos
- [ ] Schema `infrastructure_logs`

**Timeframe:** 1 semana

**Configuracion rsyslog:**
```bash
# /etc/rsyslog.d/50-mysql.conf
module(load="ommysql")

# Nginx errors → MySQL
if $programname == 'nginx' and $syslogseverity <= 3 then {
    action(type="ommysql"
           server="localhost"
           db="iact_db"
           uid="logger_user"
           pwd="***"
           template="INSERT INTO infrastructure_logs ...")
}
```

### 5. Fase 5: Alerting via Cron (P1 - 3 SP)

**Acciones:**
- [ ] Script `scripts/alert_on_errors.py`
- [ ] Cron job cada 5 min
- [ ] Detectar: >10 errors/min, >5 CRITICAL/min
- [ ] Notificar: Email, Slack webhook

**Timeframe:** 2 días

**Cron:**
```bash
# /etc/cron.d/log-alerts
*/5 * * * * python /app/scripts/alert_on_errors.py
```

**Script:**
```python
# scripts/alert_on_errors.py
from django.db.models import Count
from datetime import datetime, timedelta

# Contar errores últimos 5 min
five_min_ago = datetime.now() - timedelta(minutes=5)
error_count = ApplicationLog.objects.filter(
    level='ERROR',
    timestamp__gte=five_min_ago
).count()

if error_count > 10:
    send_alert(f"High error rate: {error_count} errors/5min")
```

### 6. Fase 6: Retention y Archivado (P2 - 3 SP)

**Acciones:**
- [ ] Script `scripts/manage_log_partitions.py`
- [ ] Cron mensual: Drop partitions >90 días
- [ ] Archive a S3 antes de drop (opcional)
- [ ] Monitoring storage: Alert si >80% disk

**Timeframe:** 2 días

**Script:**
```python
# scripts/manage_log_partitions.py
from django.db import connection

def drop_old_partitions(table_name, months_to_keep=3):
    """Drop partitions older than N months."""
    cutoff_date = datetime.now() - timedelta(days=30 * months_to_keep)

    with connection.cursor() as cursor:
        # List partitions
        cursor.execute(f"""
            SELECT PARTITION_NAME
            FROM INFORMATION_SCHEMA.PARTITIONS
            WHERE TABLE_NAME = '{table_name}'
            AND PARTITION_DESCRIPTION < UNIX_TIMESTAMP('{cutoff_date}')
        """)

        for (partition,) in cursor.fetchall():
            print(f"Dropping partition: {partition}")
            cursor.execute(f"""
                ALTER TABLE {table_name} DROP PARTITION {partition}
            """)
```

## Validacion y Metricas

### Criterios de Exito

**Fase 2 (Logging Handler):**
- Metrica 1: <2ms p95 overhead write
- Metrica 2: 0 logs perdidos (queue maxsize nunca alcanzado)
- Metrica 3: >90% test coverage

**Fase 3 (Dashboards):**
- Metrica 1: <2s page load time admin
- Metrica 2: >80% developer satisfaction (survey)
- Metrica 3: 100% logs visibles en UI

**Fase 4 (Infrastructure Logs):**
- Metrica 1: <5% overhead rsyslog
- Metrica 2: 100% errores críticos capturados
- Metrica 3: <10s lag logs → MySQL

**Fase 5 (Alerting):**
- Metrica 1: <5 min time to alert
- Metrica 2: <5% false positive rate
- Metrica 3: 100% critical errors alertados

**Fase 6 (Retention):**
- Metrica 1: <5 min drop partition execution time
- Metrica 2: 0 downtime durante drop
- Metrica 3: <80% disk usage (after retention)

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
# Target: <2ms avg
```

**Storage growth:**
```sql
-- Tamaño tabla
SELECT
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size (MB)"
FROM information_schema.TABLES
WHERE table_name = 'application_logs';

-- Logs por día
SELECT
    DATE(timestamp) as date,
    COUNT(*) as log_count,
    COUNT(*) * 1 / 1024 AS "MB_estimate"
FROM application_logs
WHERE timestamp >= NOW() - INTERVAL 7 DAY
GROUP BY DATE(timestamp);
```

**Query performance:**
```sql
-- Test query: Buscar errores últimas 24h
EXPLAIN SELECT * FROM application_logs
WHERE level = 'ERROR'
AND timestamp >= NOW() - INTERVAL 24 HOUR
ORDER BY timestamp DESC
LIMIT 100;

-- Target: <2s execution time
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
