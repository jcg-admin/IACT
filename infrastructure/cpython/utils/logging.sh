#!/bin/bash
# =============================================================================
# Utilidades de Logging para CPython Builder
# =============================================================================
# Referencia: SPEC_INFRA_001
# Proposito: Funciones de logging reutilizables para todos los scripts
# =============================================================================

# Colores para output
export RED='\033[0;31m'
export GREEN='\033[0;32m'
export YELLOW='\033[1;33m'
export BLUE='\033[0;34m'
export CYAN='\033[0;36m'
export NC='\033[0m' # No Color

# Funciones de logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

log_step() {
    local step="$1"
    local total="$2"
    local message="$3"
    echo ""
    echo -e "${BLUE}[STEP $step/$total]${NC} $message"
}

log_header() {
    local message="$1"
    local width="${2:-70}"
    echo ""
    printf '=%.0s' $(seq 1 "$width")
    echo ""
    echo "  $message"
    printf '=%.0s' $(seq 1 "$width")
    echo ""
}

log_separator() {
    local width="${1:-70}"
    printf '=%.0s' $(seq 1 "$width")
    echo ""
}
