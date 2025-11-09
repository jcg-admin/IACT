#!/bin/bash
# MySQL Restore Script - TASK-036

set -e

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

echo "WARNING: This will restore MySQL database from $BACKUP_FILE"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Aborted"
    exit 1
fi

echo "Restoring MySQL backup..."

openssl enc -d -aes-256-cbc -k "${BACKUP_PASSWORD}" -in "$BACKUP_FILE" \
    | gunzip \
    | mysql

echo "MySQL restore completed successfully"
echo "Please verify database integrity"
