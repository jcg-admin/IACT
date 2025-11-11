#!/bin/bash
# Setup cron jobs for Cassandra maintenance and alerting

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="/opt/iact"
PYTHON_BIN="/usr/bin/python3"
LOG_DIR="/var/log/iact"

echo -e "${GREEN}[INFO]${NC} Setting up cron jobs for Cassandra maintenance"

# Create log directory
sudo mkdir -p "$LOG_DIR"
sudo chown www-data:www-data "$LOG_DIR"

# Create cron jobs
cat > /tmp/cassandra-cron <<EOF
# Cassandra Maintenance and Alerting Cron Jobs
# Generated: $(date)

# Error alerting (every 5 minutes)
*/5 * * * * $PYTHON_BIN $PROJECT_ROOT/scripts/logging/alert_on_errors.py --contact-points cassandra-1.internal cassandra-2.internal cassandra-3.internal --slack-webhook \${SLACK_WEBHOOK_URL} >> $LOG_DIR/alert-cron.log 2>&1

# Cassandra compaction stats (daily at 2 AM)
0 2 * * * docker exec cassandra-1 nodetool compactionstats >> $LOG_DIR/compaction.log 2>&1

# Cassandra repair (weekly on Sunday at 3 AM)
0 3 * * 0 docker exec cassandra-1 nodetool repair -pr logging >> $LOG_DIR/repair.log 2>&1

# Cassandra cleanup old SSTables (monthly on 1st at 4 AM)
0 4 1 * * docker exec cassandra-1 nodetool clearsnapshot logging >> $LOG_DIR/cleanup.log 2>&1

# Disk space monitoring (daily at 1 AM)
0 1 * * * df -h | grep cassandra >> $LOG_DIR/disk-usage.log 2>&1

# Log rotation check (daily at 5 AM)
0 5 * * * find $LOG_DIR -name "*.log" -mtime +30 -delete >> $LOG_DIR/log-rotation.log 2>&1
EOF

# Install cron jobs
sudo crontab -u www-data /tmp/cassandra-cron
rm /tmp/cassandra-cron

echo -e "${GREEN}[SUCCESS]${NC} Cron jobs installed"
echo -e "${GREEN}[INFO]${NC} Installed jobs:"
echo -e "  - Error alerting: Every 5 minutes"
echo -e "  - Compaction stats: Daily at 2 AM"
echo -e "  - Repair: Weekly Sunday at 3 AM"
echo -e "  - Cleanup: Monthly 1st at 4 AM"
echo -e "  - Disk monitoring: Daily at 1 AM"
echo -e "  - Log rotation: Daily at 5 AM"
echo ""
echo -e "${YELLOW}[IMPORTANT]${NC} Set SLACK_WEBHOOK_URL environment variable:"
echo -e "  echo 'export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL' | sudo tee -a /etc/environment"
echo ""
echo -e "${YELLOW}[VERIFY]${NC} Check cron jobs with: sudo crontab -u www-data -l"
