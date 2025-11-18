#!/bin/bash
#
# Backup script para datos centralizados
#
# TASK-011: Data Centralization Layer
# Backup de MySQL (metrics) y Cassandra (logs future)
#

set -e  # Exit on error

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/var/backups/iact}"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Database configuration
MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}"
MYSQL_PORT="${MYSQL_PORT:-13306}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_DB="${MYSQL_DB:-iact_db}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting data centralization backup..."

# ============================================================================
# Backup MySQL (DORA Metrics)
# ============================================================================

echo "[INFO] Backing up MySQL DORA metrics..."

MYSQL_BACKUP="$BACKUP_DIR/dora_metrics_$DATE.sql"

# mysqldump requires password
# Options:
# 1. MYSQL_PWD environment variable
# 2. my.cnf file with credentials
# 3. Interactive prompt

if [ -n "$MYSQL_PWD" ]; then
    mysqldump -h "$MYSQL_HOST" \
              -P "$MYSQL_PORT" \
              -u "$MYSQL_USER" \
              "$MYSQL_DB" \
              dora_metrics > "$MYSQL_BACKUP" 2>/dev/null || {
        echo "[ERROR] MySQL backup failed"
        exit 1
    }
else
    echo "[WARN] MYSQL_PWD not set. Skipping MySQL backup."
    echo "[INFO] To enable MySQL backup, set MYSQL_PWD environment variable"
    MYSQL_BACKUP=""
fi

if [ -n "$MYSQL_BACKUP" ] && [ -f "$MYSQL_BACKUP" ]; then
    MYSQL_SIZE=$(stat -f%z "$MYSQL_BACKUP" 2>/dev/null || stat -c%s "$MYSQL_BACKUP")
    echo "[OK] MySQL backup completed: $MYSQL_BACKUP ($MYSQL_SIZE bytes)"
else
    echo "[SKIP] MySQL backup skipped"
fi

# ============================================================================
# Backup Cassandra (Application Logs) - Future
# ============================================================================

echo "[INFO] Cassandra backup..."

# Check if Cassandra is available
if command -v docker &> /dev/null && docker ps | grep -q cassandra; then
    echo "[INFO] Cassandra container found, creating snapshot..."

    docker exec cassandra-1 nodetool snapshot logging 2>/dev/null && {
        echo "[OK] Cassandra snapshot created"
    } || {
        echo "[WARN] Cassandra snapshot failed (container may not be running)"
    }
else
    echo "[SKIP] Cassandra not available (integration pending Q1 2026)"
fi

# ============================================================================
# Backup JSON Logs (Current)
# ============================================================================

echo "[INFO] Backing up JSON logs..."

JSON_LOG_DIR="/var/log/iact"
if [ -d "$JSON_LOG_DIR" ]; then
    JSON_BACKUP="$BACKUP_DIR/json_logs_$DATE.tar.gz"

    tar -czf "$JSON_BACKUP" -C "$JSON_LOG_DIR" . 2>/dev/null && {
        JSON_SIZE=$(stat -f%z "$JSON_BACKUP" 2>/dev/null || stat -c%s "$JSON_BACKUP")
        echo "[OK] JSON logs backup completed: $JSON_BACKUP ($JSON_SIZE bytes)"
    } || {
        echo "[WARN] JSON logs backup failed"
        JSON_BACKUP=""
    }
else
    echo "[SKIP] JSON log directory not found: $JSON_LOG_DIR"
    JSON_BACKUP=""
fi

# ============================================================================
# Create combined backup archive
# ============================================================================

echo "[INFO] Creating combined backup archive..."

FINAL_BACKUP="$BACKUP_DIR/iact_data_backup_$DATE.tar.gz"

# Compress all backups
tar -czf "$FINAL_BACKUP" -C "$BACKUP_DIR" \
    $(basename "$MYSQL_BACKUP" 2>/dev/null || true) \
    $(basename "$JSON_BACKUP" 2>/dev/null || true) \
    2>/dev/null || {
    echo "[WARN] Combined backup creation had warnings"
}

if [ -f "$FINAL_BACKUP" ]; then
    FINAL_SIZE=$(stat -f%z "$FINAL_BACKUP" 2>/dev/null || stat -c%s "$FINAL_BACKUP")
    echo "[OK] Final backup created: $FINAL_BACKUP ($FINAL_SIZE bytes)"
else
    echo "[ERROR] Final backup creation failed"
    exit 1
fi

# ============================================================================
# Cleanup old backups (retention policy)
# ============================================================================

echo "[INFO] Applying retention policy ($RETENTION_DAYS days)..."

DELETED_COUNT=0
for old_backup in $(find "$BACKUP_DIR" -name "iact_data_backup_*.tar.gz" -mtime +$RETENTION_DAYS); do
    rm -f "$old_backup"
    DELETED_COUNT=$((DELETED_COUNT + 1))
done

if [ $DELETED_COUNT -gt 0 ]; then
    echo "[OK] Deleted $DELETED_COUNT old backup(s)"
else
    echo "[INFO] No old backups to delete"
fi

# Cleanup temporary files
[ -n "$MYSQL_BACKUP" ] && [ -f "$MYSQL_BACKUP" ] && rm -f "$MYSQL_BACKUP"
[ -n "$JSON_BACKUP" ] && [ -f "$JSON_BACKUP" ] && rm -f "$JSON_BACKUP"

# ============================================================================
# Summary
# ============================================================================

echo ""
echo "=========================================="
echo "Backup Summary"
echo "=========================================="
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Backup file: $FINAL_BACKUP"
echo "Backup size: $FINAL_SIZE bytes"
echo "Retention: $RETENTION_DAYS days"
echo "=========================================="
echo ""
echo "[SUCCESS] Backup completed successfully"

exit 0
