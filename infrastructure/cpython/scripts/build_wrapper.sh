#!/bin/bash
#
# infrastructure/cpython/scripts/build_wrapper.sh - Wrapper para compilacion en Vagrant
#
# Referencia: SPEC_INFRA_001
# Proposito: Facilitar compilacion desde fuera de Vagrant (host → VM)
#
# Uso:
#   ./infrastructure/cpython/scripts/build_wrapper.sh <version> [build-number]
#
# Ejemplos:
#   ./infrastructure/cpython/scripts/build_wrapper.sh 3.12.6
#   ./infrastructure/cpython/scripts/build_wrapper.sh 3.12.6 2
#

set -euo pipefail

# Cargar utilidades
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

source "$SCRIPT_DIR/../utils/logging.sh" 2>/dev/null || {
    # Fallback si estamos fuera de la VM
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    NC='\033[0m'
    log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
    log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
    log_error() { echo -e "${RED}[ERROR]${NC} $*"; }
}

# Validar argumentos
if [ $# -lt 1 ]; then
    log_error "Uso: $0 <version> [build-number]"
    log_error "Ejemplo: $0 3.12.6 1"
    exit 1
fi

PYTHON_VERSION="$1"
BUILD_NUMBER="${2:-1}"

# Detectar directorio raiz del proyecto
VAGRANT_DIR="$PROJECT_ROOT/infrastructure/cpython"

# Verificar que existe directorio Vagrant
if [ ! -d "$VAGRANT_DIR" ]; then
    log_error "Directorio Vagrant no encontrado: $VAGRANT_DIR"
    exit 1
fi

log_info "=== Wrapper de compilacion de CPython ==="
log_info "Version: $PYTHON_VERSION"
log_info "Build number: $BUILD_NUMBER"
log_info "Vagrant dir: $VAGRANT_DIR"
echo ""

# Verificar que Vagrant esta instalado
if ! command -v vagrant &> /dev/null; then
    log_error "Vagrant no esta instalado"
    log_error "Instalar: https://www.vagrantup.com/downloads"
    exit 1
fi

# Verificar estado de VM
log_info "Verificando estado de VM..."
cd "$VAGRANT_DIR"

VM_STATUS=$(vagrant status --machine-readable | grep "state," | cut -d, -f4)

if [ "$VM_STATUS" != "running" ]; then
    log_info "VM no esta corriendo. Iniciando..."
    if ! vagrant up; then
        log_error "Fallo al iniciar VM"
        exit 1
    fi
fi

log_success "VM esta corriendo"

# Ejecutar compilacion en VM
log_info "Ejecutando compilacion en VM..."
echo ""

vagrant ssh -c "cd /vagrant && ./scripts/build_cpython.sh $PYTHON_VERSION $BUILD_NUMBER"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    log_success "=== Compilacion completada exitosamente ==="
    log_info "Artefacto generado en: $PROJECT_ROOT/infrastructure/cpython/artifacts/"
    echo ""
    log_info "Siguiente paso:"
    log_info "  ./infrastructure/cpython/scripts/validate_wrapper.sh cpython-${PYTHON_VERSION}-ubuntu22.04-build${BUILD_NUMBER}.tgz"
else
    echo ""
    log_error "Compilacion fallo con codigo: $EXIT_CODE"
    log_info "Para debugging, conectarse a VM:"
    log_info "  cd $VAGRANT_DIR"
    log_info "  vagrant ssh"
    exit $EXIT_CODE
fi
