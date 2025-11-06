#!/bin/bash
#
# infrastructure/cpython/scripts/validate_wrapper.sh - Wrapper para validación en Vagrant
#
# Referencia: SPEC_INFRA_001
# Propósito: Facilitar validación desde fuera de Vagrant (host → VM)
#
# Uso:
#   ./infrastructure/cpython/scripts/validate_wrapper.sh <artifact-name>
#
# Ejemplo:
#   ./infrastructure/cpython/scripts/validate_wrapper.sh cpython-3.12.6-ubuntu22.04-build1.tgz
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
    log_error "Uso: $0 <artifact-name>"
    log_error "Ejemplo: $0 cpython-3.12.6-ubuntu22.04-build1.tgz"
    exit 1
fi

ARTIFACT_NAME="$1"

# Detectar directorio raíz del proyecto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"  # 3 levels up from scripts/

VAGRANT_DIR="$PROJECT_ROOT/infrastructure/cpython"
ARTIFACT_PATH="$PROJECT_ROOT/infrastructure/cpython/artifacts/$ARTIFACT_NAME"

# Verificar que existe artefacto
if [ ! -f "$ARTIFACT_PATH" ]; then
    log_error "Artefacto no encontrado: $ARTIFACT_PATH"
    exit 1
fi

# Verificar que existe directorio Vagrant
if [ ! -d "$VAGRANT_DIR" ]; then
    log_error "Directorio Vagrant no encontrado: $VAGRANT_DIR"
    exit 1
fi

log_info "=== Wrapper de validación de artefacto CPython ==="
log_info "Artefacto: $ARTIFACT_NAME"
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

# Ejecutar validación en VM
log_info "Ejecutando validación en VM..."
echo ""

vagrant ssh -c "cd /vagrant && ./scripts/validate_build.sh $ARTIFACT_NAME"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    log_success "=== Validación completada exitosamente ==="
    log_info "El artefacto es válido y listo para distribución"
else
    echo ""
    log_error "Validación falló con código: $EXIT_CODE"
    exit $EXIT_CODE
fi
