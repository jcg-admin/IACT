#!/bin/bash
#
# Script wrapper para generar reportes DORA automaticamente
#
# Uso: ./scripts/generate_dora_report.sh
# Cron: 0 0 1 * * /path/to/scripts/generate_dora_report.sh
#

set -e  # Exit on error

# Configuration
PROJECT_DIR="/home/user/IACT---project"
REPORTS_DIR="$PROJECT_DIR/docs/dora/reports"
LOG_DIR="/var/log/iact"
GITHUB_TOKEN="${GITHUB_TOKEN:-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}"
REPO="2-Coatl/IACT---project"

# Create directories if not exist
mkdir -p "$REPORTS_DIR"
mkdir -p "$LOG_DIR"

# Generate timestamp
TIMESTAMP=$(date +"%Y%m")
REPORT_FILE="$REPORTS_DIR/DORA_MONTHLY_$TIMESTAMP.md"
LOG_FILE="$LOG_DIR/dora_cron.log"

# Log start
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting DORA monthly report generation..." | tee -a "$LOG_FILE"

# Execute DORA metrics script
cd "$PROJECT_DIR"

export GITHUB_TOKEN="$GITHUB_TOKEN"

python scripts/dora_metrics.py \
    --repo "$REPO" \
    --days 30 \
    --format markdown \
    > "$REPORT_FILE" 2>&1

# Check if report was generated
if [ -f "$REPORT_FILE" ]; then
    REPORT_SIZE=$(stat -f%z "$REPORT_FILE" 2>/dev/null || stat -c%s "$REPORT_FILE")
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: Report generated at $REPORT_FILE (${REPORT_SIZE} bytes)" | tee -a "$LOG_FILE"

    # Optional: Commit report to git (uncomment if needed)
    # git add "$REPORT_FILE"
    # git commit -m "automation(dora): monthly report $TIMESTAMP"
    # git push

    exit 0
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: Report file not created" | tee -a "$LOG_FILE"
    exit 1
fi
