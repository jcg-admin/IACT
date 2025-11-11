#!/bin/bash
# MySQL Backup Script - TASK-036
# Full and incremental backups with compression and encryption

set -e

BACKUP_DIR="/var/backups/mysql"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="mysql_backup_${DATE}.sql.gz.enc"

echo "Starting MySQL backup: $BACKUP_FILE"

# Full backup
mysqldump --all-databases \
    --single-transaction \
    --quick \
    --lock-tables=false \
    --routines \
    --triggers \
    --events \
    | gzip \
    | openssl enc -aes-256-cbc -salt -k "${BACKUP_PASSWORD}" \
    > "${BACKUP_DIR}/${BACKUP_FILE}"

echo "Backup completed: $(du -h ${BACKUP_DIR}/${BACKUP_FILE})"

# Upload to remote storage (S3, GCS, etc)
# aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}" s3://backups/mysql/

# Cleanup old backups (keep 30 days)
find "${BACKUP_DIR}" -name "mysql_backup_*.sql.gz.enc" -mtime +30 -delete

echo "MySQL backup successful"
