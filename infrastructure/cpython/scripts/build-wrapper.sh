#!/bin/bash
#
# infrastructure/cpython/scripts/build-wrapper.sh - Wrapper para compilación en Vagrant
#
# Referencia: SPEC-INFRA-001
# Propósito: Facilitar compilación desde fuera de Vagrant (host → VM)
#
# Uso:
#   ./infrastructure/cpython/scripts/build-wrapper.sh <version> [build-number]
#
# Ejemplos:
#   ./infrastructure/cpython/scripts/build-wrapper.sh 3.12.6
#   ./infrastructure/cpython/scripts/build-wrapper.sh 3.12.6 2
#

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
}

# Validar argumentos
if [ $# -lt 1 ]; then
    log_error "Uso: $0 <version> [build-number]"
    log_error "Ejemplo: $0 3.12.6 1"
    exit 1
fi

PYTHON_VERSION="$1"
BUILD_NUMBER="${2:-1}"

# Detectar directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"  # 3 levels up from scripts/

VAGRANT_DIR="$PROJECT_ROOT/infrastructure/cpython"

# Verificar que existe directorio Vagrant
if [ ! -d "$VAGRANT_DIR" ]; then
    log_error "Directorio Vagrant no encontrado: $VAGRANT_DIR"
    exit 1
fi

log_info "=== Wrapper de compilación de CPython ==="
log_info "Versión: $PYTHON_VERSION"
log_info "Build number: $BUILD_NUMBER"
log_info "Vagrant dir: $VAGRANT_DIR"
echo ""

# Verificar que Vagrant está instalado
if ! command -v vagrant &> /dev/null; then
    log_error "Vagrant no está instalado"
    log_error "Instalar: https://www.vagrantup.com/downloads"
    exit 1
fi

# Verificar estado de VM
log_info "Verificando estado de VM..."
cd "$VAGRANT_DIR"

VM_STATUS=$(vagrant status --machine-readable | grep "state," | cut -d, -f4)

if [ "$VM_STATUS" != "running" ]; then
    log_info "VM no está corriendo. Iniciando..."
    if ! vagrant up; then
        log_error "Fallo al iniciar VM"
        exit 1
    fi
fi

log_success "VM está corriendo"

# Ejecutar compilación en VM
log_info "Ejecutando compilación en VM..."
echo ""

vagrant ssh -c "cd /vagrant && ./scripts/build-cpython.sh $PYTHON_VERSION $BUILD_NUMBER"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    log_success "=== Compilación completada exitosamente ==="
    log_info "Artefacto generado en: $PROJECT_ROOT/infrastructure/cpython/artifacts/"
    echo ""
    log_info "Siguiente paso:"
    log_info "  ./infrastructure/cpython/scripts/validate-wrapper.sh cpython-${PYTHON_VERSION}-ubuntu22.04-build${BUILD_NUMBER}.tgz"
else
    echo ""
    log_error "Compilación falló con código: $EXIT_CODE"
    log_info "Para debugging, conectarse a VM:"
    log_info "  cd $VAGRANT_DIR"
    log_info "  vagrant ssh"
    exit $EXIT_CODE
fi
