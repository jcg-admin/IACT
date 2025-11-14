#!/bin/bash
# test-pyramid.sh
#
# Analyze Test Pyramid
# Replica: Test Pyramid Validation / Analyze Test Pyramid
#
# Exit codes:
#   0 - Test pyramid is balanced
#   1 - Test pyramid is unbalanced

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

log_info "Analyzing test pyramid..."

cd "$PROJECT_ROOT/api/callcentersite"

# Activar entorno virtual
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Count tests by type
log_info "Counting tests by type..."

# Unit tests (mark: unit)
UNIT_TESTS=$(pytest --co -m unit 2>/dev/null | grep "<Function" | wc -l)

# Integration tests (mark: integration)
INTEGRATION_TESTS=$(pytest --co -m integration 2>/dev/null | grep "<Function" | wc -l)

# E2E tests (mark: e2e)
E2E_TESTS=$(pytest --co -m e2e 2>/dev/null | grep "<Function" | wc -l)

# Total tests
TOTAL_TESTS=$((UNIT_TESTS + INTEGRATION_TESTS + E2E_TESTS))

if [ $TOTAL_TESTS -eq 0 ]; then
    log_warn "No tests found with pyramid marks"
    exit 1
fi

# Calculate percentages
UNIT_PCT=$(awk "BEGIN {printf \"%.1f\", ($UNIT_TESTS / $TOTAL_TESTS) * 100}")
INTEGRATION_PCT=$(awk "BEGIN {printf \"%.1f\", ($INTEGRATION_TESTS / $TOTAL_TESTS) * 100}")
E2E_PCT=$(awk "BEGIN {printf \"%.1f\", ($E2E_TESTS / $TOTAL_TESTS) * 100}")

# Display results
echo ""
log_info "Test Pyramid Analysis"
echo "Total Tests: $TOTAL_TESTS"
echo ""
echo "Unit Tests:        $UNIT_TESTS ($UNIT_PCT%)"
echo "Integration Tests: $INTEGRATION_TESTS ($INTEGRATION_PCT%)"
echo "E2E Tests:         $E2E_TESTS ($E2E_PCT%)"
echo ""

# Validate pyramid (ideal ratios: 70% unit, 20% integration, 10% e2e)
PYRAMID_VALID=true

# Check unit tests should be > 50%
if (( $(awk "BEGIN {print ($UNIT_PCT < 50)}") )); then
    log_warn "Unit tests should be > 50% (current: $UNIT_PCT%)"
    PYRAMID_VALID=false
fi

# Check e2e tests should be < 20%
if (( $(awk "BEGIN {print ($E2E_PCT > 20)}") )); then
    log_warn "E2E tests should be < 20% (current: $E2E_PCT%)"
    PYRAMID_VALID=false
fi

if [ "$PYRAMID_VALID" = true ]; then
    log_info "Test pyramid is balanced"
    exit 0
else
    log_error "Test pyramid is unbalanced"
    exit 1
fi
