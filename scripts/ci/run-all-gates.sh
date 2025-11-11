#!/bin/bash
# run-all-gates.sh
#
# Ejecuta todos los gates de PromptOps en secuencia
#
# Uso:
#   ./run-all-gates.sh [--fail-fast] [--verbose]
#
# Flags:
#   --fail-fast: Detener en el primer gate que falle
#   --verbose: Output detallado de cada gate
#
# Exit codes:
#   0 - Todos los gates pasaron
#   1 - Uno o más gates fallaron
#   2 - Error de configuración

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funciones auxiliares
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_section() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Parse flags
FAIL_FAST=false
VERBOSE=false

for arg in "$@"; do
    case $arg in
        --fail-fast)
            FAIL_FAST=true
            ;;
        --verbose)
            VERBOSE=true
            ;;
    esac
done

# Encontrar raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

log_info "Project root: $PROJECT_ROOT"
log_info "Fail-fast: $FAIL_FAST"
log_info "Verbose: $VERBOSE"

# Activar entorno virtual si existe
if [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    log_info "Activating virtual environment"
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    log_info "Activating virtual environment"
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Array para tracking de resultados
declare -a GATE_RESULTS
TOTAL_GATES=0
PASSED_GATES=0
FAILED_GATES=0

# Función para ejecutar un gate
run_gate() {
    local gate_name=$1
    local gate_script=$2

    log_section "Running Gate: $gate_name"

    TOTAL_GATES=$((TOTAL_GATES + 1))

    if [ ! -f "$gate_script" ]; then
        log_error "Gate script not found: $gate_script"
        GATE_RESULTS+=("$gate_name: SKIP (script not found)")
        return 1
    fi

    # Hacer script ejecutable
    chmod +x "$gate_script"

    # Ejecutar gate
    if [ "$VERBOSE" = true ]; then
        "$gate_script"
    else
        "$gate_script" > /dev/null 2>&1
    fi

    local exit_code=$?

    if [ $exit_code -eq 0 ]; then
        log_info "$gate_name: PASS"
        GATE_RESULTS+=("$gate_name: PASS")
        PASSED_GATES=$((PASSED_GATES + 1))
        return 0
    else
        log_error "$gate_name: FAIL (exit code: $exit_code)"
        GATE_RESULTS+=("$gate_name: FAIL")
        FAILED_GATES=$((FAILED_GATES + 1))

        if [ "$FAIL_FAST" = true ]; then
            log_error "Fail-fast enabled, stopping execution"
            exit 1
        fi

        return 1
    fi
}

# ============================================
# CRITICAL GATES (must pass)
# ============================================

# Gate 1: DB Router - CRITICAL (IVR read-only)
run_gate "db-router" "$SCRIPT_DIR/gate-db-router.sh"

# Gate 2: Project Restrictions - CRITICAL
run_gate "restrictions" "$SCRIPT_DIR/gate-restrictions.sh"

# ============================================
# COMPLIANCE GATES
# ============================================

# Gate 3: Route Lint (permissions)
run_gate "route-lint" "$SCRIPT_DIR/gate-route-lint.sh"

# Gate 4: No Emojis
run_gate "no-emojis" "$SCRIPT_DIR/gate-no-emojis.sh"

# Gate 5: Documentation Structure
run_gate "docs-structure" "$SCRIPT_DIR/gate-docs-structure.sh"

# ============================================
# FUTURE GATES (TODO: implementar)
# ============================================
# run_gate "audit-contract" "$SCRIPT_DIR/gate-audit-contract.sh"
# run_gate "permission-coverage" "$SCRIPT_DIR/gate-permission-coverage.sh"
# run_gate "migration-validator" "$SCRIPT_DIR/gate-migration.sh"
# run_gate "api-contract" "$SCRIPT_DIR/gate-api-contract.sh"

# ============================================
# Reporte Final
# ============================================

log_section "Final Report"

echo ""
echo "Total Gates: $TOTAL_GATES"
echo -e "${GREEN}Passed: $PASSED_GATES${NC}"
echo -e "${RED}Failed: $FAILED_GATES${NC}"
echo ""

log_info "Individual Results:"
for result in "${GATE_RESULTS[@]}"; do
    if [[ $result == *"PASS"* ]]; then
        echo -e "  ${GREEN}[OK]${NC} $result"
    elif [[ $result == *"FAIL"* ]]; then
        echo -e "  ${RED}[ERROR]${NC} $result"
    else
        echo -e "  ${YELLOW}[SKIP]${NC} $result"
    fi
done

echo ""

if [ $FAILED_GATES -eq 0 ]; then
    log_info "All gates passed!"
    exit 0
else
    log_error "$FAILED_GATES gate(s) failed"
    exit 1
fi
