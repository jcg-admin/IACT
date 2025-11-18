-- ============================================================================
-- INFRASTRUCTURE LOGS SCHEMA - Layer 3
-- ============================================================================
--
-- Almacena logs de infraestructura (OS/system logs) con TTL de 90 dias
--
-- Layer 3: Infrastructure Logs
--   - System logs (syslog, kernel, etc)
--   - Service logs (systemd, docker, etc)
--   - Performance metrics logs
--   - Security logs (auth, sudo, etc)
--
-- Diseñado para:
--   - Batch writes (1000 logs/batch)
--   - Alta throughput (>100K writes/s)
--   - Auto-expiracion TTL 90 dias
--   - Queries por timestamp y hostname
--
-- Relacionado: Layer 2 (application_logs) - TASK-010
-- ============================================================================

-- Crear keyspace si no existe
CREATE KEYSPACE IF NOT EXISTS logging
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
}
AND durable_writes = true;

USE logging;

-- ============================================================================
-- TABLA: infrastructure_logs
-- ============================================================================

CREATE TABLE IF NOT EXISTS infrastructure_logs (
    -- Partition key: Distribucion por hostname y fecha
    hostname TEXT,
    log_date DATE,

    -- Clustering key: Ordenamiento por timestamp descendente
    log_timestamp TIMESTAMP,
    log_id UUID,

    -- Log data
    source TEXT,              -- syslog, kernel, systemd, docker, auth, etc
    severity TEXT,            -- EMERGENCY, ALERT, CRITICAL, ERROR, WARNING, NOTICE, INFO, DEBUG
    facility TEXT,            -- kern, user, mail, daemon, auth, syslog, etc
    message TEXT,             -- Mensaje original del log

    -- Contexto adicional
    process_name TEXT,        -- Nombre del proceso
    process_id INT,           -- PID
    user_name TEXT,           -- Usuario (si aplica)

    -- Metadata
    tags SET<TEXT>,           -- Tags para categorization
    extra MAP<TEXT, TEXT>,    -- Metadata extra key-value

    -- Timestamp de ingestion
    ingested_at TIMESTAMP,

    -- Primary key
    PRIMARY KEY ((hostname, log_date), log_timestamp, log_id)
)
WITH CLUSTERING ORDER BY (log_timestamp DESC, log_id DESC)
-- TTL por defecto: 90 dias (7776000 segundos)
AND default_time_to_live = 7776000
-- Compaction strategy para time-series
AND compaction = {
    'class': 'TimeWindowCompactionStrategy',
    'compaction_window_unit': 'DAYS',
    'compaction_window_size': 1
}
-- Compression
AND compression = {
    'class': 'LZ4Compressor'
}
-- Caching
AND caching = {
    'keys': 'ALL',
    'rows_per_partition': '100'
}
-- Bloom filter
AND bloom_filter_fp_chance = 0.01
-- Comments
AND comment = 'Infrastructure logs with 90 days TTL - Layer 3';

-- ============================================================================
-- INDICES SECUNDARIOS
-- ============================================================================

-- Index por source (para queries por tipo de log)
CREATE INDEX IF NOT EXISTS idx_infra_logs_source
ON infrastructure_logs (source);

-- Index por severity (para queries por nivel)
CREATE INDEX IF NOT EXISTS idx_infra_logs_severity
ON infrastructure_logs (severity);

-- ============================================================================
-- TABLA: infrastructure_log_stats
-- ============================================================================
-- Estadisticas agregadas de logs de infraestructura

CREATE TABLE IF NOT EXISTS infrastructure_log_stats (
    -- Partition key: Tipo de agregacion
    stat_type TEXT,           -- daily, hourly, by_source, by_severity
    bucket_date DATE,

    -- Clustering key
    bucket_hour INT,          -- 0-23 (para hourly)
    dimension_value TEXT,     -- hostname, source, severity (segun stat_type)

    -- Contadores
    log_count COUNTER,

    -- Primary key
    PRIMARY KEY ((stat_type, bucket_date), bucket_hour, dimension_value)
)
WITH CLUSTERING ORDER BY (bucket_hour DESC, dimension_value ASC)
AND default_time_to_live = 7776000
AND comment = 'Infrastructure log statistics with 90 days TTL';

-- ============================================================================
-- QUERIES COMUNES
-- ============================================================================

-- 1. Obtener logs recientes de un host
-- SELECT * FROM infrastructure_logs
-- WHERE hostname = 'server-01' AND log_date = '2025-11-07'
-- LIMIT 100;

-- 2. Obtener logs de un source especifico
-- SELECT * FROM infrastructure_logs
-- WHERE hostname = 'server-01' AND log_date = '2025-11-07' AND source = 'syslog'
-- LIMIT 100;

-- 3. Obtener logs criticos
-- SELECT * FROM infrastructure_logs
-- WHERE hostname = 'server-01' AND log_date = '2025-11-07' AND severity = 'CRITICAL'
-- ALLOW FILTERING;

-- 4. Estadisticas diarias
-- SELECT * FROM infrastructure_log_stats
-- WHERE stat_type = 'daily' AND bucket_date = '2025-11-07';

-- ============================================================================
-- MANTENIMIENTO
-- ============================================================================

-- Ver TTL restante de un log
-- SELECT TTL(message) FROM infrastructure_logs
-- WHERE hostname = 'server-01' AND log_date = '2025-11-07'
-- LIMIT 1;

-- Verificar espacio usado
-- nodetool tablestats logging.infrastructure_logs

-- Compaction manual si necesario
-- nodetool compact logging infrastructure_logs

-- ============================================================================
-- NOTAS
-- ============================================================================
--
-- TTL:
--   - Configurado a 90 dias (7776000 segundos)
--   - Auto-expira automaticamente sin necesidad de cleanup manual
--   - TTL se calcula desde el momento de INSERT
--
-- Partitioning:
--   - Por hostname + fecha para distribucion uniforme
--   - Evita hot spots
--   - Permite queries eficientes por host
--
-- Clustering:
--   - Ordenamiento DESC por timestamp (logs mas recientes primero)
--   - UUID para unicidad y evitar colisiones
--
-- Compaction:
--   - TimeWindowCompactionStrategy para time-series data
--   - Window de 1 dia alineado con partitioning
--   - Optimizado para writes append-only
--
-- Indices:
--   - Solo 2 indices (source, severity)
--   - Evitar exceso de indices (penalty en writes)
--   - Usar ALLOW FILTERING con cuidado (puede ser lento)
--
-- Throughput esperado:
--   - Writes: >100K logs/second (con batch de 1000)
--   - Reads: <100ms p99 para queries recientes
--   - Storage: ~1GB por millon de logs (con compression)
--
-- Retention:
--   - 90 dias de logs en Cassandra
--   - Archive a S3/storage externo si necesario (futuro)
--   - Cold storage para compliance/auditoria
--
-- ============================================================================
