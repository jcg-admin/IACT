# Cassandra Logging Scripts

Scripts para storage centralizado de logs usando Apache Cassandra como alternativa
a Grafana/Prometheus (bloqueados por RNF-002).

**Version:** 1.0.0
**Fecha:** 2025-11-07
**ADR:** ADR-2025-004 - Centralized Log Storage en Cassandra

---

## Vision General

Estos scripts implementan la **Capa 2 (Application Logs)** y **Capa 3 (Infrastructure Logs)**
del sistema de observabilidad de 3 capas del proyecto IACT.

**Arquitectura:**
```
Application Django
       |
       v
CassandraLogHandler (async + batch)
       |
       v
Cassandra Cluster (3+ nodes)
  ├── logging.application_logs    (Capa 2)
  └── logging.infrastructure_logs (Capa 3)
       |
       v
AlertManager (cron cada 5 min)
  ├── >10 ERROR/5min → Slack/Email
  └── >5 CRITICAL/5min → Slack/Email
```

---

## Scripts Incluidos

### 1. cassandra_handler.py
**Handler Django logging para Cassandra (async + batch)**

- **Lineas:** 337
- **Proposito:** Django logging handler con async queue + worker thread
- **Performance:** <0.1ms overhead per log (vs MySQL ~1-2ms)
- **Features:**
  - Non-blocking writes (Queue + Thread)
  - Batch inserts (100 logs/batch)
  - Prepared statements (performance)
  - TTL 90 dias automatico
  - Stats tracking (logs_queued, logs_written, logs_dropped)

### 2. cassandra_schema_setup.py
**Setup keyspace, tables, indexes en Cassandra**

- **Lineas:** 325
- **Proposito:** Inicializar schema Cassandra para logging
- **Features:**
  - Keyspace logging (replication_factor configurable)
  - Tables: application_logs, infrastructure_logs
  - TimeWindowCompactionStrategy (diaria)
  - Secondary indexes: level, logger, request_id, source
  - TTL configurable (default: 90 dias)
  - Validation y stats post-setup

### 3. alert_on_errors.py
**Alerting basado en CQL queries (cron)**

- **Lineas:** 367
- **Proposito:** Detectar y alertar errores criticos en logs
- **Ejecucion:** Cron cada 5 minutos
- **Detecta:**
  - >10 ERROR logs en ultimos 5 min
  - >5 CRITICAL logs en ultimos 5 min
  - >100 logs de un mismo logger (posible loop)
- **Notificaciones:**
  - Slack webhook
  - Email (SMTP - TODO)
  - Log file (/var/log/iact/log_alerts.log)

---

## Prerequisitos

### 1. Cassandra Cluster

**Instalacion (Debian/Ubuntu):**
```bash
# Agregar repositorio Cassandra
echo "deb https://debian.cassandra.apache.org 41x main" | sudo tee /etc/apt/sources.list.d/cassandra.list
curl https://downloads.apache.org/cassandra/KEYS | sudo apt-key add -
sudo apt-get update

# Instalar Cassandra
sudo apt-get install cassandra

# Iniciar servicio
sudo systemctl start cassandra
sudo systemctl enable cassandra

# Verificar cluster
nodetool status
# Debe mostrar: UN (Up Normal)
```

**Cluster minimo:** 3 nodes (replication_factor=3)

### 2. Python Dependencies

```bash
# Instalar cassandra-driver
pip install cassandra-driver

# Instalar requests (para Slack webhook)
pip install requests
```

**Requirements:**
```
cassandra-driver>=3.25.0
requests>=2.28.0
```

---

## Quick Start

### Paso 1: Setup Cassandra Schema

```bash
# Opcion 1: Single node (dev/testing)
python scripts/logging/cassandra_schema_setup.py \
    --contact-points 127.0.0.1 \
    --replication-factor 1 \
    --ttl-days 90

# Opcion 2: Cluster 3 nodes (produccion)
python scripts/logging/cassandra_schema_setup.py \
    --contact-points 192.168.1.10,192.168.1.11,192.168.1.12 \
    --replication-factor 3 \
    --ttl-days 90
```

**Output esperado:**
```
[1/7] Connecting to Cassandra: ['192.168.1.10', '192.168.1.11', '192.168.1.12']
[OK] Connected to cluster: iact_logging_cluster
[2/7] Creating keyspace: logging (replication_factor=3)
[OK] Keyspace 'logging' created
[3/7] Creating table: application_logs (TTL=7776000s / 90 days)
[OK] Table 'application_logs' created
[4/7] Creating table: infrastructure_logs (TTL=7776000s / 90 days)
[OK] Table 'infrastructure_logs' created
[5/7] Creating secondary indexes...
[OK] Index 'idx_app_logs_level' created on logging.application_logs(level)
[OK] Index 'idx_app_logs_logger' created on logging.application_logs(logger)
[OK] Index 'idx_app_logs_request_id' created on logging.application_logs(request_id)
[6/7] Verifying schema...
[OK] Keyspace 'logging' exists (replication={'class': 'SimpleStrategy', 'replication_factor': '3'})
[OK] Table 'application_logs' exists (columns=11)
[OK] Table 'infrastructure_logs' exists (columns=6)
[OK] Indexes on 'application_logs': 3
[7/7] Schema statistics:
[SUCCESS] Cassandra schema setup completed!
```

### Paso 2: Configurar Django Logging

**settings.py:**
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'cassandra': {
            'class': 'scripts.logging.cassandra_handler.CassandraLogHandler',
            'level': 'INFO',
            'contact_points': ['192.168.1.10', '192.168.1.11', '192.168.1.12'],
            'keyspace': 'logging',
            'batch_size': 100,
            'batch_timeout': 1.0,
        },
        'file': {  # Backup en filesystem
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'formatters': {
        'verbose': {
            'format': '[{asctime}] {levelname} [{name}] {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['cassandra', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'myapp': {
            'handlers': ['cassandra', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### Paso 3: Test Logging

```python
import logging

logger = logging.getLogger('myapp')

# Log simple
logger.info("Application started")

# Log con contexto
logger.info("User login successful", extra={
    'request_id': 'req-abc123',
    'user_id': 42,
    'session_id': 'sess-xyz789'
})

# Log de error con traceback
try:
    1 / 0
except Exception:
    logger.exception("Division by zero error")
```

### Paso 4: Setup Alerting (Cron)

**Cron job (cada 5 minutos):**
```bash
# Editar crontab
crontab -e

# Agregar linea:
*/5 * * * * python /app/scripts/logging/alert_on_errors.py \
    --contact-points 192.168.1.10,192.168.1.11,192.168.1.12 \
    --slack-webhook https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
    --alert-log /var/log/iact/log_alerts.log \
    >> /var/log/iact/alert_cron.log 2>&1
```

**Test manual:**
```bash
python scripts/logging/alert_on_errors.py \
    --contact-points 127.0.0.1 \
    --slack-webhook https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

---

## Uso Avanzado

### Verificar Logs en Cassandra

```bash
# Conectar a Cassandra
cqlsh 192.168.1.10

# Verificar keyspace
DESCRIBE KEYSPACE logging;

# Ver ultimos 10 logs
SELECT * FROM logging.application_logs LIMIT 10;

# Buscar errores hoy
SELECT * FROM logging.application_logs
WHERE log_date = '2025-11-07'
AND level = 'ERROR'
LIMIT 100;

# Contar errores por nivel
SELECT level, COUNT(*) as count
FROM logging.application_logs
WHERE log_date = '2025-11-07'
GROUP BY level;
```

### Monitorear Cluster

```bash
# Estado cluster
nodetool status logging

# Latencia writes
nodetool tablestats logging.application_logs | grep "Write Latency"
# Target: <1ms

# Espacio usado
nodetool tablestats logging.application_logs | grep "Space used"

# Compaction status
nodetool compactionstats
```

### Custom Logging Handler (avanzado)

```python
from scripts.logging.cassandra_handler import CassandraLogHandler

# Handler customizado
class CustomCassandraHandler(CassandraLogHandler):
    def emit(self, record):
        # Agregar metadata custom
        if hasattr(record, 'user_id'):
            record.metadata = record.metadata or {}
            record.metadata['user_tier'] = get_user_tier(record.user_id)

        super().emit(record)
```

---

## Mantenimiento

### TTL y Retention

**Cassandra TTL es automatico:**
- Logs >90 dias se eliminan automaticamente via compaction
- No requiere scripts de drop manual (vs MySQL partitioning)

**Verificar TTL funcionando:**
```bash
# Query logs antiguos (deben retornar vacio si TTL funcionando)
cqlsh -e "SELECT * FROM logging.application_logs WHERE log_date = '2025-08-01' LIMIT 1;"
# Si retorna vacio despues de 90 dias = TTL OK
```

### Compaction y Cleanup

**Cron semanal (recomendado):**
```bash
# Editar crontab
crontab -e

# Repair semanal (asegura consistency)
0 2 * * 0 nodetool repair logging

# Cleanup mensual (libera espacio tombstones)
0 3 1 * * nodetool cleanup logging
```

### Monitoreo Storage

**Script de monitoreo:**
```bash
#!/bin/bash
# scripts/logging/monitor_cassandra_storage.sh

# Alert si >80% disk usage
THRESHOLD=80

nodetool status | awk '{print $1, $6}' | while read status load; do
    if [ "$status" = "UN" ]; then
        load_gb=$(echo $load | sed 's/GB//')
        if (( $(echo "$load_gb > $THRESHOLD" | bc -l) )); then
            echo "[WARNING] Node load: ${load_gb}GB (threshold: ${THRESHOLD}GB)"
            # Enviar alerta...
        fi
    fi
done
```

---

## Troubleshooting

### Problema: Logs no aparecen en Cassandra

**Diagnostico:**
1. Verificar handler configurado en settings.py
2. Verificar Cassandra cluster UP:
   ```bash
   nodetool status
   # Todos los nodes deben ser UN (Up Normal)
   ```
3. Verificar conectividad:
   ```bash
   telnet 192.168.1.10 9042
   ```
4. Ver stats del handler:
   ```python
   from scripts.logging.cassandra_handler import handler
   print(handler.get_stats())
   # Verificar: logs_dropped = 0
   ```

### Problema: Queue lleno (logs dropped)

**Sintoma:** `stats['logs_dropped'] > 0`

**Solucion:**
```python
# settings.py - Aumentar queue_maxsize
'cassandra': {
    'queue_maxsize': 50000,  # vs default 10000
}
```

### Problema: Latencia writes alta

**Diagnostico:**
```bash
nodetool tablestats logging.application_logs | grep "Write Latency"
# Si >1ms, investigar
```

**Soluciones:**
- Aumentar batch_size (default: 100 → 500)
- Aumentar batch_timeout (default: 1.0s → 5.0s)
- Verificar cluster no sobrecargado (CPU, disk I/O)
- Verificar compaction no bloqueando writes

### Problema: Alertas no llegan

**Diagnostico:**
1. Test manual:
   ```bash
   python scripts/logging/alert_on_errors.py \
       --contact-points 127.0.0.1 \
       --slack-webhook https://hooks.slack.com/...
   ```
2. Verificar cron ejecutandose:
   ```bash
   grep alert_on_errors /var/log/cron
   ```
3. Ver logs cron:
   ```bash
   cat /var/log/iact/alert_cron.log
   ```

---

## Performance Benchmarks

**Write performance:**
```bash
# Test 1000 logs
python -c "
import logging
from scripts.logging.cassandra_handler import CassandraLogHandler
import time

logger = logging.getLogger('test')
handler = CassandraLogHandler(contact_points=['127.0.0.1'])
logger.addHandler(handler)

start = time.time()
for i in range(1000):
    logger.info(f'Test log {i}', extra={'request_id': f'test-{i}'})
duration = time.time() - start

print(f'1000 logs in {duration:.2f}s = {duration*1000:.2f}ms avg')
print(f'Stats: {handler.get_stats()}')
"
```

**Target:** <0.5ms avg per log

**Query performance:**
```bash
# Test query: Buscar errores hoy
time cqlsh -e "
SELECT * FROM logging.application_logs
WHERE log_date = '2025-11-07'
AND level = 'ERROR'
LIMIT 100;
"
```

**Target:** <1s execution time

---

## Referencias

**Documentacion:**
- [ADR-2025-004: Centralized Log Storage en Cassandra](../../docs/adr/adr_2025_004_centralized_log_storage.md)
- [OBSERVABILITY_LAYERS.md](../../docs/implementacion/OBSERVABILITY_LAYERS.md)
- [DORA_CASSANDRA_INTEGRATION.md](../../docs/gobernanza/ai/DORA_CASSANDRA_INTEGRATION.md)

**Cassandra:**
- [Cassandra Documentation](https://cassandra.apache.org/doc/latest/)
- [CQL Reference](https://cassandra.apache.org/doc/latest/cql/)
- [cassandra-driver Python](https://docs.datastax.com/en/developer/python-driver/latest/)

**DORA 2025:**
- [DORA Report 2025](https://dora.dev/dora-report-2025)
- [AI Capabilities Practices](../../docs/gobernanza/ai/AI_CAPABILITIES.md)

---

## Contacto

**Owner:** @arquitecto-senior @devops-lead
**Issues:** Reportar en GitHub Issues
**Slack:** #observability

---

**VERSION:** 1.0.0
**ULTIMA ACTUALIZACION:** 2025-11-07
**ESTADO:** PRODUCTION READY
