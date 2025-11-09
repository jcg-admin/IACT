---
id: CASSANDRA-INSTALLATION-GUIDE
tipo: guia
categoria: infrastructure
fecha: 2025-11-07
version: 1.0.0
propietario: platform-lead
relacionados: ["../logging/README.md", "../../docs/gobernanza/ai/DORA_CASSANDRA_INTEGRATION.md"]
---

# Guia de Instalacion Cassandra Cluster

Guia completa para instalar y configurar un cluster Cassandra de 3 nodos para centralized logging (Capa 3 Observability).

---

## 1. Prerrequisitos

### Hardware Minimo (por nodo)

| Recurso | Desarrollo | Produccion |
|---------|------------|------------|
| CPU | 2 cores | 8 cores |
| RAM | 4 GB | 32 GB |
| Disk | 50 GB SSD | 500 GB SSD |
| Network | 100 Mbps | 1 Gbps |

### Software

```bash
# Opcion 1: Docker (Recomendado para desarrollo)
docker --version       # >= 20.10
docker-compose --version  # >= 1.29

# Opcion 2: Systemd (Recomendado para produccion)
java -version          # OpenJDK 11 or 17
python3 --version      # >= 3.11
```

---

## 2. Instalacion

### Opcion 1: Docker Compose (Desarrollo)

```bash
# 1. Instalar cluster (3 nodos)
./scripts/cassandra/install-cassandra.sh docker

# Esto ejecuta:
# - docker-compose up -d (cassandra-1, cassandra-2, cassandra-3)
# - Espera a que cluster este ready
# - Ejecuta cassandra_schema_setup.py (keyspace + tables)

# 2. Verificar cluster status
docker exec cassandra-1 nodetool status

# Output esperado:
# Datacenter: datacenter1
# Status=Up/Down
# State=Normal/Leaving/Joining/Moving
# --  Address     Load       Tokens  Owns    Host ID
# UN  172.20.0.2  100 KB     256     33.3%   <uuid>  cassandra-1
# UN  172.20.0.3  100 KB     256     33.3%   <uuid>  cassandra-2
# UN  172.20.0.4  100 KB     256     33.3%   <uuid>  cassandra-3

# 3. Verificar keyspace y tables
docker exec -it cassandra-1 cqlsh -e "DESCRIBE KEYSPACE logging;"

# 4. Detener cluster
docker-compose -f docker-compose.cassandra.yml down

# 5. Reiniciar cluster
docker-compose -f docker-compose.cassandra.yml up -d
```

#### Endpoints Docker

| Nodo | CQL Port | JMX Port | Connection String |
|------|----------|----------|-------------------|
| cassandra-1 | 9042 | 7199 | localhost:9042 |
| cassandra-2 | 9043 | 7200 | localhost:9043 |
| cassandra-3 | 9044 | 7201 | localhost:9044 |

---

### Opcion 2: Systemd Nativo (Produccion)

```bash
# 1. Instalar Cassandra (single node primero)
sudo ./scripts/cassandra/install-cassandra.sh systemd

# Esto ejecuta:
# - apt-get install cassandra
# - systemctl start cassandra
# - Ejecuta cassandra_schema_setup.py

# 2. Verificar status
sudo systemctl status cassandra
nodetool status

# 3. Para cluster multi-nodo, actualizar configuracion
sudo nano /etc/cassandra/cassandra.yaml

# Actualizar:
# seeds: "node1-ip,node2-ip,node3-ip"
# listen_address: <this-node-ip>
# rpc_address: <this-node-ip>

# 4. Reiniciar Cassandra
sudo systemctl restart cassandra

# 5. Verificar cluster
nodetool status
```

---

## 3. Configuracion Django

### Agregar Cassandra Handler a settings.py

```bash
# Ejecutar script de configuracion
./scripts/cassandra/configure-django.sh api/callcentersite/callcentersite/settings/production.py

# Esto agrega:
# - CASSANDRA_LOGGING configuration
# - CassandraLogHandler a LOGGING['handlers']
# - Loggers para django, analytics, etl, reports

# Actualizar contact_points manualmente
nano api/callcentersite/callcentersite/settings/production.py

# Cambiar:
CASSANDRA_LOGGING = {
    'contact_points': [
        '10.0.1.10',  # cassandra-1 IP
        '10.0.1.11',  # cassandra-2 IP
        '10.0.1.12',  # cassandra-3 IP
    ],
    # ... resto de config
}
```

### Crear directorio de logs

```bash
sudo mkdir -p /var/log/iact
sudo chown www-data:www-data /var/log/iact
```

### Reiniciar Django

```bash
# Systemd
sudo systemctl restart iact-django

# Gunicorn
sudo systemctl restart gunicorn

# Development server
python api/callcentersite/manage.py runserver
```

### Test logging

```bash
cd api/callcentersite

# Test manual
python manage.py shell
>>> import logging
>>> logger = logging.getLogger('analytics')
>>> logger.info('Test log from Django shell', extra={'request_id': '123'})
>>> exit()

# Verificar en Cassandra
docker exec -it cassandra-1 cqlsh -e "SELECT * FROM logging.application_logs WHERE logger = 'analytics' LIMIT 5;"
```

---

## 4. Infrastructure Logs Daemon

### Instalar systemd service

```bash
# 1. Copiar script y service
sudo cp scripts/logging/infrastructure_logs_daemon.py /opt/iact/scripts/logging/
sudo cp scripts/logging/infrastructure-logs-daemon.service /etc/systemd/system/

# 2. Actualizar contact_points en service file
sudo nano /etc/systemd/system/infrastructure-logs-daemon.service

# Cambiar:
--cassandra-hosts cassandra-1.internal cassandra-2.internal cassandra-3.internal

# A IPs reales:
--cassandra-hosts 10.0.1.10 10.0.1.11 10.0.1.12

# 3. Reload systemd y start service
sudo systemctl daemon-reload
sudo systemctl start infrastructure-logs-daemon
sudo systemctl enable infrastructure-logs-daemon

# 4. Verificar status
sudo systemctl status infrastructure-logs-daemon

# 5. Ver logs
sudo journalctl -u infrastructure-logs-daemon -f

# 6. Health check
curl http://localhost:9090/health

# Output esperado:
{
  "status": "healthy",
  "stats": {
    "logs_tailed": 1234,
    "logs_written": 1200,
    "batches_written": 12,
    "errors": 0,
    "start_time": "2025-11-07T10:30:00Z"
  },
  "cassandra_stats": {
    "logs_written": 1200,
    "batches_written": 12,
    "errors": 0
  },
  "queue_size": 34
}
```

---

## 5. Cron Jobs (Maintenance + Alerting)

### Setup cron jobs

```bash
# 1. Ejecutar script setup
./scripts/cassandra/setup-cron-jobs.sh

# Esto instala:
# - Error alerting (every 5 min)
# - Compaction stats (daily 2 AM)
# - Repair (weekly Sunday 3 AM)
# - Cleanup (monthly 1st 4 AM)
# - Disk monitoring (daily 1 AM)
# - Log rotation (daily 5 AM)

# 2. Configurar Slack webhook
echo 'export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL' | sudo tee -a /etc/environment

# 3. Verificar cron jobs
sudo crontab -u www-data -l

# 4. Ver logs de cron jobs
tail -f /var/log/iact/alert-cron.log
tail -f /var/log/iact/compaction.log
tail -f /var/log/iact/repair.log
```

---

## 6. Monitoring y Mantenimiento

### Nodetool Commands

```bash
# Cluster status
nodetool status

# Compaction stats
nodetool compactionstats

# Table stats
nodetool tablestats logging.application_logs

# Repair (manual)
nodetool repair -pr logging

# Cleanup old SSTables
nodetool clearsnapshot logging

# Disk usage
du -sh /var/lib/cassandra/data/logging/

# JMX metrics
nodetool info
```

### CQL Queries

```bash
# Connect to Cassandra
docker exec -it cassandra-1 cqlsh

# Query logs (last 24h)
SELECT * FROM logging.application_logs
WHERE log_date = '2025-11-07'
LIMIT 100;

# Count logs by level
SELECT level, COUNT(*) as count
FROM logging.application_logs
WHERE log_date = '2025-11-07'
GROUP BY level;

# Query by request_id
SELECT * FROM logging.application_logs
WHERE log_date = '2025-11-07'
AND request_id = '123e4567-e89b-12d3-a456-426614174000';

# Query infrastructure logs
SELECT * FROM logging.infrastructure_logs
WHERE log_date = '2025-11-07'
AND source = '/var/log/nginx/error.log'
LIMIT 50;
```

---

## 7. Troubleshooting

### Problema: Cluster no inicia

```bash
# Verificar logs
docker logs cassandra-1

# Error comun: Out of memory
# Solucion: Reducir MAX_HEAP_SIZE en docker-compose.yml

# Error comun: Port already in use
# Solucion: Cambiar ports en docker-compose.yml
```

### Problema: Nodos no se unen al cluster

```bash
# Verificar seeds
docker exec cassandra-1 cat /etc/cassandra/cassandra.yaml | grep seeds

# Verificar network
docker network inspect iact-logging-cluster_cassandra-network

# Reiniciar nodos uno por uno
docker restart cassandra-1
sleep 60
docker restart cassandra-2
sleep 60
docker restart cassandra-3
```

### Problema: Logs no aparecen en Cassandra

```bash
# Verificar Django settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.LOGGING['handlers']['cassandra'])

# Verificar conexion Cassandra desde Django
>>> from cassandra.cluster import Cluster
>>> cluster = Cluster(['localhost'])
>>> session = cluster.connect('logging')
>>> rows = session.execute("SELECT COUNT(*) FROM application_logs")
>>> print(rows.one())

# Verificar logs del daemon
sudo journalctl -u infrastructure-logs-daemon -n 100
```

### Problema: Disco lleno

```bash
# Verificar TTL esta activo
docker exec -it cassandra-1 cqlsh -e "DESCRIBE TABLE logging.application_logs;"
# Debe mostrar: default_time_to_live = 7776000

# Forzar compaction
nodetool compact logging

# Reducir TTL (si necesario)
docker exec -it cassandra-1 cqlsh -e "ALTER TABLE logging.application_logs WITH default_time_to_live = 2592000;"  # 30 dias
```

---

## 8. Performance Tuning

### Write Performance

```bash
# Aumentar batch size (Django)
CASSANDRA_LOGGING = {
    'batch_size': 500,  # Default: 100
    'batch_timeout': 2.0,  # Default: 1.0
}

# Aumentar concurrent writes (Cassandra)
# En cassandra.yaml:
concurrent_writes: 64  # Default: 32
```

### Read Performance

```bash
# Agregar secondary indexes (si queries frecuentes)
docker exec -it cassandra-1 cqlsh -e "CREATE INDEX idx_custom ON logging.application_logs (custom_field);"

# Aumentar cache sizes (cassandra.yaml)
row_cache_size_in_mb: 1024
key_cache_size_in_mb: 512
```

### Disk I/O

```bash
# Cambiar compaction strategy (si muchos writes)
docker exec -it cassandra-1 cqlsh -e "ALTER TABLE logging.application_logs WITH compaction = {'class': 'LeveledCompactionStrategy'};"

# Monitorear I/O
iostat -x 5
```

---

## 9. Backup y Restore

### Snapshot (Backup)

```bash
# Crear snapshot
nodetool snapshot logging -t backup-$(date +%Y%m%d)

# Listar snapshots
nodetool listsnapshots

# Location: /var/lib/cassandra/data/logging/*/snapshots/

# Copiar snapshot a storage externo
tar -czf cassandra-backup-$(date +%Y%m%d).tar.gz /var/lib/cassandra/data/logging/*/snapshots/backup-$(date +%Y%m%d)
aws s3 cp cassandra-backup-*.tar.gz s3://backups-bucket/cassandra/
```

### Restore

```bash
# 1. Detener Cassandra
sudo systemctl stop cassandra

# 2. Restaurar snapshot
cd /var/lib/cassandra/data/logging/
rm -rf application_logs-*/
tar -xzf /tmp/cassandra-backup-20251107.tar.gz -C .

# 3. Iniciar Cassandra
sudo systemctl start cassandra

# 4. Refresh tables
nodetool refresh logging application_logs
```

---

## 10. Uninstall

### Docker

```bash
# Detener y eliminar containers
docker-compose -f docker-compose.cassandra.yml down -v

# Eliminar imagenes
docker rmi cassandra:4.1

# Eliminar volumes (CUIDADO: Elimina datos!)
docker volume rm cassandra-1-data cassandra-2-data cassandra-3-data
```

### Systemd

```bash
# Detener service
sudo systemctl stop cassandra
sudo systemctl disable cassandra

# Desinstalar package
sudo apt-get remove --purge cassandra

# Eliminar datos (CUIDADO!)
sudo rm -rf /var/lib/cassandra
sudo rm -rf /etc/cassandra
```

---

## 11. Referencias

- Cassandra 4.1 Docs: https://cassandra.apache.org/doc/4.1/
- Python Driver: https://docs.datastax.com/en/developer/python-driver/
- Docker Image: https://hub.docker.com/_/cassandra
- DORA Integration: ../../docs/gobernanza/ai/DORA_CASSANDRA_INTEGRATION.md
- Logging Scripts: ../logging/README.md

---

**Creado**: 2025-11-07
**Version**: 1.0.0
**Propietario**: Platform Lead
**Soporte**: platform-lead@company.com
