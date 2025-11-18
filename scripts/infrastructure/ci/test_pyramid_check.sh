#!/bin/bash
#
# Test Pyramid Validation Script - Local execution
#
# Valida que la distribucion de tests siga el patron 60/30/10 (Unit/Integration/E2E)
# Puede ejecutarse localmente o desde GitHub Actions
#
# Uso:
#   ./scripts/ci/test_pyramid_check.sh
#
# Salida:
#   Imprime reporte de distribucion y falla si no cumple con limites

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    RED=''
    GREEN=''
    YELLOW=''
    NC=''
fi

log_info() {
    echo "[INFO] $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_info "Test Pyramid Validation - Starting..."

# Count Backend Tests
log_info "Counting backend tests..."

cd "$PROJECT_ROOT/api/callcentersite"

BE_UNIT=$(find . -path "*/tests/test_*.py" -type f ! -name "*integration*" ! -name "*e2e*" | wc -l)
BE_INT=$(find . -path "*/tests/test_integration_*.py" -type f | wc -l)
BE_E2E=$(find . -path "*/tests/test_e2e_*.py" -type f | wc -l)

log_info "Backend - Unit: $BE_UNIT, Integration: $BE_INT, E2E: $BE_E2E"

# Count Frontend Tests
log_info "Counting frontend tests..."

cd "$PROJECT_ROOT"

if [ -d "frontend/src" ]; then
    FE_UNIT=$(find frontend/src -name "*.test.tsx" -o -name "*.test.ts" | grep -v ".integration.test" | grep -v ".e2e.test" | wc -l)
    FE_INT=$(find frontend/src -name "*.integration.test.tsx" -o -name "*.integration.test.ts" | wc -l)
    if [ -d "frontend/e2e" ]; then
        FE_E2E=$(find frontend/e2e -name "*.spec.ts" 2>/dev/null | wc -l)
    else
        FE_E2E=0
    fi

    log_info "Frontend - Unit: $FE_UNIT, Integration: $FE_INT, E2E: $FE_E2E"
else
    log_warning "Frontend directory not found, assuming 0 tests"
    FE_UNIT=0
    FE_INT=0
    FE_E2E=0
fi

# Calculate totals
TOTAL_UNIT=$((BE_UNIT + FE_UNIT))
TOTAL_INT=$((BE_INT + FE_INT))
TOTAL_E2E=$((BE_E2E + FE_E2E))
TOTAL=$((TOTAL_UNIT + TOTAL_INT + TOTAL_E2E))

if [ $TOTAL -eq 0 ]; then
    log_error "No tests found!"
    exit 1
fi

# Calculate percentages
UNIT_PCT=$((TOTAL_UNIT * 100 / TOTAL))
INT_PCT=$((TOTAL_INT * 100 / TOTAL))
E2E_PCT=$((TOTAL_E2E * 100 / TOTAL))

echo ""
echo "============================================"
echo "TEST PYRAMID METRICS"
echo "============================================"
echo "Total Tests: $TOTAL"
echo ""
echo "Unit Tests: $TOTAL_UNIT ($UNIT_PCT%)"
echo "Integration Tests: $TOTAL_INT ($INT_PCT%)"
echo "E2E Tests: $TOTAL_E2E ($E2E_PCT%)"
echo "============================================"
echo ""

# Validate pyramid (60/30/10 rule with tolerance)
log_info "Validating Test Pyramid (Target: 60% Unit, 30% Integration, 10% E2E)..."
echo ""

VALID=true

# Unit tests should be >= 50% (allowing 10% tolerance)
if [ $UNIT_PCT -lt 50 ]; then
    log_error "Unit tests are only $UNIT_PCT% (should be >= 50%)"
    VALID=false
else
    log_success "Unit tests are $UNIT_PCT% (>= 50%)"
fi

# Integration tests should be 20-40%
if [ $INT_PCT -lt 20 ] || [ $INT_PCT -gt 40 ]; then
    log_warning "Integration tests are $INT_PCT% (should be 20-40%)"
    # Warning only, not blocking
else
    log_success "Integration tests are $INT_PCT% (20-40%)"
fi

# E2E tests should be <= 20%
if [ $E2E_PCT -gt 20 ]; then
    log_warning "E2E tests are $E2E_PCT% (should be <= 20%)"
    # Warning only, not blocking
else
    log_success "E2E tests are $E2E_PCT% (<= 20%)"
fi

echo ""

if [ "$VALID" != "true" ]; then
    echo "============================================"
    log_error "Test pyramid validation FAILED"
    echo "============================================"
    echo ""
    echo "Recommendations:"
    echo "  - Add more unit tests (target: 60%)"
    echo "  - Unit tests should test individual functions/components in isolation"
    echo "  - They should be fast and have no external dependencies"
    echo ""
    exit 1
fi

echo "============================================"
log_success "Test pyramid validation PASSED"
echo "============================================"

# Generate report file (optional)
if [ -n "$REPORT_FILE" ]; then
    log_info "Generating report file: $REPORT_FILE"

    cat > "$REPORT_FILE" <<EOF
# Test Pyramid Report

**Date**: $(date +"%Y-%m-%d %H:%M:%S")
**Total Tests**: $TOTAL

## Test Distribution

    /\\
   /  \\         E2E ($E2E_PCT%)
  /----\\
 /      \\       Integration ($INT_PCT%)
/--------\\
/          \\     Unit ($UNIT_PCT%)
/------------\\

## Targets vs Actual

| Type | Target | Actual | Status |
|------|--------|--------|--------|
| Unit | 60% | $UNIT_PCT% | $([ $UNIT_PCT -ge 50 ] && echo "[PASS]" || echo "[FAIL]") |
| Integration | 30% | $INT_PCT% | $([ $INT_PCT -ge 20 ] && [ $INT_PCT -le 40 ] && echo "[PASS]" || echo "[WARNING]") |
| E2E | 10% | $E2E_PCT% | $([ $E2E_PCT -le 20 ] && echo "[PASS]" || echo "[WARNING]") |

## Backend Breakdown

- Unit: $BE_UNIT
- Integration: $BE_INT
- E2E: $BE_E2E

## Frontend Breakdown

- Unit: $FE_UNIT
- Integration: $FE_INT
- E2E: $FE_E2E

---

Generated by test_pyramid_check.sh
EOF

    log_success "Report generated: $REPORT_FILE"
fi
