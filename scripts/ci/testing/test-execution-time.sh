#!/bin/bash
# test-execution-time.sh
#
# Validate Test Execution Time
# Replica: Test Pyramid Validation / Validate Test Execution Time
#
# Exit codes:
#   0 - Test execution time is acceptable
#   1 - Tests are too slow

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

log_info "Validating test execution time..."

cd "$PROJECT_ROOT/api/callcentersite"

# Activar entorno virtual
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Run tests with timing
log_info "Running tests with timing analysis..."

START_TIME=$(date +%s)

if pytest -v --durations=10 2>&1 | tee /tmp/test_timing.log; then
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))

    log_info "Total test duration: ${DURATION}s"

    # Extract slowest tests
    echo ""
    log_info "Slowest tests:"
    grep "slowest" /tmp/test_timing.log -A 10 || true

    # Check for slow tests (> 5s)
    SLOW_TESTS=$(grep -c "s call" /tmp/test_timing.log | grep -E "[5-9]\.[0-9]+s|[0-9]{2,}\.[0-9]+s" || echo "0")

    if [ "$SLOW_TESTS" -gt 0 ]; then
        log_warn "Found $SLOW_TESTS slow tests (>5s)"
    fi

    # Overall time threshold: 2 minutes for all tests
    if [ $DURATION -gt 120 ]; then
        log_error "Test suite is too slow (${DURATION}s > 120s)"
        exit 1
    else
        log_info "Test execution time is acceptable"
        exit 0
    fi
else
    log_error "Tests failed"
    exit 1
fi
