#!/bin/bash
# health-check.sh
#
# Test Health Check Scripts
# Replica: Infrastructure CI / Test Health Check Scripts
#
# Exit codes:
#   0 - Health checks passed
#   1 - Health checks failed

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

log_info "Running Health Check Scripts"

CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_SKIPPED=0

# Check 1: Python version
log_info "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_info "Python version: $PYTHON_VERSION"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    log_error "Python3 not found"
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check 2: Node.js version (if applicable)
log_info "Checking Node.js version..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    log_info "Node.js version: $NODE_VERSION"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    log_warn "Node.js not found (optional)"
fi

# Check 3: Database connectivity
log_info "Checking database connectivity..."
cd "$PROJECT_ROOT/api/callcentersite"

if [ -f "manage.py" ]; then
    if DB_CHECK_OUTPUT=$(python3 manage.py check --database default 2>&1); then
        log_info "Database connectivity: OK"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        log_error "Database connectivity failed"
        echo "$DB_CHECK_OUTPUT" | tail -n 20 | while IFS= read -r line; do
            log_error "    $line"
        done
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi

# Check 4: Django configuration
log_info "Checking Django configuration..."
if DJANGO_CHECK_OUTPUT=$(python3 manage.py check 2>&1); then
    log_info "Django configuration: OK"
    CHECKS_PASSED=$((CHECKS_PASSED + 1))
else
    log_error "Django configuration check failed"
    echo "$DJANGO_CHECK_OUTPUT" | tail -n 20 | while IFS= read -r line; do
        log_error "    $line"
    done
    CHECKS_FAILED=$((CHECKS_FAILED + 1))
fi

# Check 5: Required directories exist
log_info "Checking required directories..."
REQUIRED_DIRS=(
    "api/callcentersite"
    "scripts/ci"
    "docs"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        log_info "Directory exists: $dir"
        CHECKS_PASSED=$((CHECKS_PASSED + 1))
    else
        log_error "Directory missing: $dir"
        CHECKS_FAILED=$((CHECKS_FAILED + 1))
    fi
done

# Summary
echo ""
log_info "Health Check Summary"
log_info "Passed: $CHECKS_PASSED"
log_warn "Skipped: $CHECKS_SKIPPED"
log_error "Failed: $CHECKS_FAILED"

if [ $CHECKS_FAILED -eq 0 ]; then
    log_info "All health checks passed"
    exit 0
else
    log_error "Some health checks failed"
    exit 1
fi
