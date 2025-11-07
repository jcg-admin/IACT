#!/bin/bash
# Cassandra Backup Script - TASK-036
# Snapshot-based backups

set -e

BACKUP_DIR="/var/backups/cassandra"
DATE=$(date +%Y%m%d_%H%M%S)
KEYSPACE="iact_logs"

echo "Starting Cassandra backup: $KEYSPACE"

# Create snapshot
nodetool snapshot -t "backup_${DATE}" "$KEYSPACE"

# Copy snapshot to backup dir
mkdir -p "${BACKUP_DIR}/${DATE}"
cp -r /var/lib/cassandra/data/${KEYSPACE}/*/snapshots/backup_${DATE}/* \
    "${BACKUP_DIR}/${DATE}/"

# Clear old snapshots
nodetool clearsnapshot -t "backup_${DATE}"

# Upload to remote
# aws s3 sync "${BACKUP_DIR}/${DATE}" s3://backups/cassandra/${DATE}/

echo "Cassandra backup successful"
