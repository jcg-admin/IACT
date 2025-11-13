#!/bin/bash
# npm-audit.sh
#
# NPM Security Audit
# Replica: Security Scan / NPM Security Audit
#
# Exit codes:
#   0 - No vulnerabilities
#   1 - Vulnerabilities found
#   2 - NPM not used or prerequisites missing (skip)

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

log_info "Running NPM security audit..."

# Locate package.json (support monorepos)
AUDIT_DIR=""

if [ -f "$PROJECT_ROOT/package.json" ]; then
    AUDIT_DIR="$PROJECT_ROOT"
    log_info "Found package.json in repository root"
elif [ -f "$PROJECT_ROOT/ui/package.json" ]; then
    AUDIT_DIR="$PROJECT_ROOT/ui"
    log_info "Found package.json in ui"
elif [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    AUDIT_DIR="$PROJECT_ROOT/frontend"
    log_info "Found package.json in frontend"
fi

if [ -z "$AUDIT_DIR" ]; then
    log_warn "No package.json found - skipping NPM audit"
    exit 2
fi

# Check if npm is installed
if ! command -v npm >/dev/null 2>&1; then
    log_warn "npm CLI not available - skipping audit"
    log_warn "Install Node.js/npm locally to run this check"
    exit 2
fi

log_info "Running npm audit..."

cd "$AUDIT_DIR"

AUDIT_LOG="/tmp/npm_audit.log"

if npm audit --audit-level=moderate >"$AUDIT_LOG" 2>&1; then
    log_info "NPM audit passed - no vulnerabilities found"
    exit 0
fi

if grep -E "(ENOTFOUND|ECONN|EAI_AGAIN|ENETUNREACH|network request failed)" "$AUDIT_LOG" >/dev/null 2>&1; then
    log_warn "npm audit could not reach the registry - skipping (offline environment)"
    tail -n 5 "$AUDIT_LOG" | while IFS= read -r line; do
        log_warn "    $line"
    done
    exit 2
fi

if grep -E "(ENOLOCK|requires a lockfile)" "$AUDIT_LOG" >/dev/null 2>&1; then
    log_warn "npm audit requires dependencies installed (missing lockfile) - skipping"
    tail -n 5 "$AUDIT_LOG" | while IFS= read -r line; do
        log_warn "    $line"
    done
    exit 2
fi

log_error "NPM audit found vulnerabilities or failed unexpectedly"
cat "$AUDIT_LOG"
exit 1
