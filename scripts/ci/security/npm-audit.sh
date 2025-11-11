#!/bin/bash
# npm-audit.sh
#
# NPM Security Audit
# Replica: Security Scan / NPM Security Audit
#
# Exit codes:
#   0 - No vulnerabilities
#   1 - Vulnerabilities found
#   2 - NPM not used (skip)

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

log_info "Running NPM security audit..."

# Check if package.json exists
PACKAGE_JSON_FOUND=false

if [ -f "$PROJECT_ROOT/package.json" ]; then
    PACKAGE_JSON_FOUND=true
elif [ -f "$PROJECT_ROOT/frontend/package.json" ]; then
    cd "$PROJECT_ROOT/frontend"
    PACKAGE_JSON_FOUND=true
fi

if [ "$PACKAGE_JSON_FOUND" = false ]; then
    log_warn "No package.json found - skipping NPM audit"
    exit 2
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    log_error "npm not installed"
    exit 1
fi

log_info "Running npm audit..."

# Run npm audit
if npm audit --audit-level=moderate 2>&1 | tee /tmp/npm_audit.log; then
    log_info "NPM audit passed - no vulnerabilities found"
    exit 0
else
    log_error "NPM audit found vulnerabilities"
    cat /tmp/npm_audit.log

    log_info "Attempting to fix vulnerabilities..."
    npm audit fix

    exit 1
fi
