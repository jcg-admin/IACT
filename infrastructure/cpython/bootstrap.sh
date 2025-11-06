#!/bin/bash
set -euo pipefail

# =============================================================================
# CPython Builder - Bootstrap Script
# =============================================================================
# Referencia: SPEC_INFRA_001
# Propósito: Aprovisionar VM con dependencias de compilación de CPython
# =============================================================================

# Cargar utilidades
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-/vagrant}"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# =============================================================================
# FUNCIONES PRINCIPALES
# =============================================================================

update_system() {
    log_step 1 3 "Actualizando sistema"

    log_info "Actualizando lista de paquetes..."
    apt-get update -qq

    log_info "Actualizando paquetes del sistema..."
    apt-get upgrade -y -qq

    log_success "Sistema actualizado"
}

install_build_dependencies() {
    log_step 2 3 "Instalando dependencias de compilación de CPython"

    log_info "Instalando toolchain de compilación..."

    # Dependencias según: https://devguide.python.org/getting-started/setup-building/
    apt-get install -y -qq \
      build-essential \
      gdb \
      lcov \
      pkg-config \
      libbz2-dev \
      libffi-dev \
      libgdbm-dev \
      libgdbm-compat-dev \
      liblzma-dev \
      libncurses5-dev \
      libreadline6-dev \
      libsqlite3-dev \
      libssl-dev \
      lzma \
      lzma-dev \
      tk-dev \
      uuid-dev \
      zlib1g-dev \
      wget \
      curl \
      ca-certificates

    log_success "Dependencias de compilación instaladas"

    log_info "Versiones de librerías críticas:"
    dpkg -l | grep -E "libssl-dev|libsqlite3-dev|liblzma-dev|libbz2-dev|libffi-dev" | \
      awk '{print "  " $2 ": " $3}'
}

install_additional_tools() {
    log_step 3 3 "Instalando herramientas adicionales"

    log_info "Instalando git, vim, htop..."
    apt-get install -y -qq git vim htop

    log_success "Herramientas adicionales instaladas"
}

verify_installation() {
    log_info "Verificando instalación..."

    # Verificar GCC
    if command -v gcc >/dev/null 2>&1; then
        GCC_VERSION=$(gcc --version | head -1)
        log_success "GCC disponible: $GCC_VERSION"
    else
        log_error "GCC no encontrado"
        return 1
    fi

    # Verificar make
    if command -v make >/dev/null 2>&1; then
        MAKE_VERSION=$(make --version | head -1)
        log_success "Make disponible: $MAKE_VERSION"
    else
        log_error "Make no encontrado"
        return 1
    fi

    # Verificar librerías críticas
    CRITICAL_LIBS=("libssl-dev" "libsqlite3-dev" "liblzma-dev" "libbz2-dev" "libffi-dev")
    for lib in "${CRITICAL_LIBS[@]}"; do
        if dpkg -l | grep -q "$lib"; then
            log_success "  $lib instalado"
        else
            log_error "  $lib NO instalado"
            return 1
        fi
    done

    log_success "Verificación completada"
}

setup_directories() {
    log_info "Configurando directorios..."

    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/artifacts/cpython"

    log_success "Directorios configurados"
}

display_summary() {
    echo ""
    echo "========================================================================="
    echo "  CPython Builder - Bootstrap Completado"
    echo "========================================================================="
    echo ""
    echo "Entorno de compilación listo:"
    echo ""
    echo "  Toolchain:"
    gcc --version | head -1 | sed 's/^/    /'
    make --version | head -1 | sed 's/^/    /'
    echo ""
    echo "  Scripts disponibles:"
    echo "    ./scripts/build_cpython.sh <version> [build-number]"
    echo "    ./scripts/validate_build.sh <artifact-name>"
    echo ""
    echo "  Ejemplo de uso:"
    echo "    ./scripts/build_cpython.sh 3.12.6"
    echo ""
    echo "  Artefactos se generarán en:"
    echo "    $PROJECT_ROOT/artifacts/cpython/"
    echo ""
    echo "========================================================================="
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

main() {
    log_info "========================================================================="
    log_info "  CPython Builder - Iniciando Bootstrap"
    log_info "========================================================================="
    echo ""

    # Ejecutar pasos
    update_system
    install_build_dependencies
    install_additional_tools
    verify_installation
    setup_directories

    # Resumen
    display_summary

    log_success "Bootstrap completado exitosamente"
}

# Ejecutar main
main "$@"
