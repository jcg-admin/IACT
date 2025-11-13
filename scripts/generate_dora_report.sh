#!/bin/bash
#
# Script wrapper para generar reportes DORA automaticamente
#
# Uso: ./scripts/generate_dora_report.sh
# Cron: 0 0 1 * * /path/to/scripts/generate_dora_report.sh
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
REPORTS_DIR="$PROJECT_DIR/docs/dora/reports"
LOG_DIR="${IACT_LOG_DIR:-$PROJECT_DIR/logs}" 
REPO="${1:-2-Coatl/IACT---project}"

mkdir -p "$REPORTS_DIR"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y%m")
REPORT_FILE="$REPORTS_DIR/DORA_MONTHLY_$TIMESTAMP.md"
LOG_FILE="$LOG_DIR/dora_cron.log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting DORA monthly report generation..." | tee -a "$LOG_FILE"

if [ ! -f "$PROJECT_DIR/scripts/dora_metrics.py" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: scripts/dora_metrics.py no encontrado" | tee -a "$LOG_FILE"
    exit 1
fi

python "$PROJECT_DIR/scripts/dora_metrics.py" \
    --repo "$REPO" \
    --days 30 \
    --format markdown \
    > "$REPORT_FILE"

REPORT_SIZE=$(stat -f%z "$REPORT_FILE" 2>/dev/null || stat -c%s "$REPORT_FILE")
echo "[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: Report generated at $REPORT_FILE (${REPORT_SIZE} bytes)" | tee -a "$LOG_FILE"

exit 0
