#!/bin/bash
# bandit-scan.sh
#
# Python Security Scan (Bandit)
# Replica: Security Scan / Python Security Scan (Bandit)
#
# Exit codes:
#   0 - No security issues
#   1 - Security issues found

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

log_info "Running Bandit security scan..."

# Activar entorno virtual si existe
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Check if bandit is installed
if ! command -v bandit &> /dev/null; then
    log_warn "Bandit not installed, attempting installation..."
    if ! pip install bandit >/tmp/bandit_install.log 2>&1; then
        log_warn "Bandit installation failed - skipping scan"
        log_warn "Installer output:\n$(tail -n 5 /tmp/bandit_install.log)"
        exit 2
    fi
fi

if ! command -v bandit &> /dev/null; then
    log_warn "Bandit still unavailable after installation attempt - skipping scan"
    exit 2
fi

# Run bandit scan
cd "$PROJECT_ROOT"

log_info "Scanning Python code for security issues..."

# Exclude common directories
EXCLUDE_DIRS="*/migrations/*,*/tests/*,*/venv/*,*/.venv/*,*/node_modules/*"

if bandit -r api/callcentersite scripts -x "$EXCLUDE_DIRS" -f screen -ll 2>&1 | tee /tmp/bandit_report.txt; then
    log_info "Bandit scan completed with no high-severity issues"

    # Check for medium/low issues
    if grep -q "Issue:" /tmp/bandit_report.txt; then
        log_warn "Found medium/low severity issues - review report"
        cat /tmp/bandit_report.txt
    fi

    exit 0
else
    log_error "Bandit found high-severity security issues"
    cat /tmp/bandit_report.txt
    exit 1
fi
