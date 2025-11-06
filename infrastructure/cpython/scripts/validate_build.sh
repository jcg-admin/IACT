#!/bin/bash
#
# validate_build.sh - Validar artefacto de CPython compilado
#
# Referencia: SPEC_INFRA_001
# Propósito: Verificar integridad y funcionalidad del artefacto
#
# Uso:
#   ./validate_build.sh <artifact-name>
#
# Ejemplo:
#   ./validate_build.sh cpython-3.12.6-ubuntu22.04-build1.tgz
#

set -euo pipefail

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

# Validar argumentos
if [ $# -lt 1 ]; then
    log_error "Uso: $0 <artifact-name>"
    log_error "Ejemplo: $0 cpython-3.12.6-ubuntu22.04-build1.tgz"
    exit 1
fi

ARTIFACT_NAME="$1"
ARTIFACT_DIR="/vagrant/artifacts/cpython"
ARTIFACT_PATH="$ARTIFACT_DIR/$ARTIFACT_NAME"
ARTIFACT_CHECKSUM="$ARTIFACT_PATH.sha256"

log_info "=== Validación de artefacto CPython ==="
log_info "Artefacto: $ARTIFACT_NAME"
echo ""

# Validación 1: Artefacto existe
log_info "1. Verificando existencia del artefacto..."
if [ ! -f "$ARTIFACT_PATH" ]; then
    log_error "Artefacto no encontrado: $ARTIFACT_PATH"
    exit 1
fi
log_success "Artefacto existe"

# Validación 2: Checksum existe
log_info "2. Verificando existencia de checksum..."
if [ ! -f "$ARTIFACT_CHECKSUM" ]; then
    log_error "Checksum no encontrado: $ARTIFACT_CHECKSUM"
    exit 1
fi
log_success "Checksum existe"

# Validación 3: Verificar integridad SHA256
log_info "3. Verificando integridad SHA256..."
cd "$ARTIFACT_DIR"
if ! sha256sum -c "$ARTIFACT_NAME.sha256" 2>&1 | grep -q "OK"; then
    log_error "Checksum SHA256 inválido"
    exit 1
fi
CHECKSUM=$(cut -d' ' -f1 "$ARTIFACT_CHECKSUM")
log_success "Checksum válido: $CHECKSUM"

# Validación 4: Tamaño razonable
log_info "4. Verificando tamaño del artefacto..."
ARTIFACT_SIZE=$(stat -f%z "$ARTIFACT_PATH" 2>/dev/null || stat -c%s "$ARTIFACT_PATH")
ARTIFACT_SIZE_MB=$((ARTIFACT_SIZE / 1024 / 1024))

if [ $ARTIFACT_SIZE_MB -lt 30 ]; then
    log_error "Artefacto muy pequeño ($ARTIFACT_SIZE_MB MB). Mínimo esperado: 30 MB"
    exit 1
fi

if [ $ARTIFACT_SIZE_MB -gt 150 ]; then
    log_warn "Artefacto muy grande ($ARTIFACT_SIZE_MB MB). Máximo esperado: 150 MB"
fi

log_success "Tamaño razonable: $ARTIFACT_SIZE_MB MB"

# Validación 5: Contenido del tarball
log_info "5. Verificando contenido del tarball..."

# Listar contenido sin extraer
TARBALL_CONTENT=$(tar tzf "$ARTIFACT_PATH" | head -20)

# Verificar que contiene opt/python-X.Y.Z/
if ! echo "$TARBALL_CONTENT" | grep -q "^opt/python-[0-9]"; then
    log_error "Tarball no contiene directorio opt/python-X.Y.Z/"
    exit 1
fi

log_success "Estructura de directorio correcta"

# Validación 6: Extraer y verificar binarios
log_info "6. Extrayendo temporalmente para verificar binarios..."

TEST_DIR="/tmp/cpython-validate-$$"
mkdir -p "$TEST_DIR"

cd "$TEST_DIR"
tar xzf "$ARTIFACT_PATH"

# Detectar versión de Python del artefacto
PYTHON_DIR=$(find opt -maxdepth 1 -name "python-*" -type d | head -1)

if [ -z "$PYTHON_DIR" ]; then
    log_error "No se encontró directorio python-* en artefacto"
    rm -rf "$TEST_DIR"
    exit 1
fi

PYTHON_VERSION=$(basename "$PYTHON_DIR" | sed 's/python-//')
PYTHON_MAJOR_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f1,2)

log_info "Versión detectada: $PYTHON_VERSION"

# Verificar binario principal
PYTHON_BIN="$TEST_DIR/$PYTHON_DIR/bin/python${PYTHON_MAJOR_MINOR}"

if [ ! -f "$PYTHON_BIN" ]; then
    log_error "Binario de Python no encontrado: $PYTHON_BIN"
    rm -rf "$TEST_DIR"
    exit 1
fi

# Hacer ejecutable
chmod +x "$PYTHON_BIN"

log_success "Binario existe y es ejecutable"

# Validación 7: Versión del binario
log_info "7. Verificando versión del binario..."

# Configurar LD_LIBRARY_PATH para librerías compartidas
export LD_LIBRARY_PATH="$TEST_DIR/$PYTHON_DIR/lib:${LD_LIBRARY_PATH:-}"

BINARY_VERSION=$("$PYTHON_BIN" --version 2>&1 | awk '{print $2}')

if [ "$BINARY_VERSION" != "$PYTHON_VERSION" ]; then
    log_error "Versión del binario ($BINARY_VERSION) no coincide con esperada ($PYTHON_VERSION)"
    rm -rf "$TEST_DIR"
    exit 1
fi

log_success "Versión correcta: $BINARY_VERSION"

# Validación 8: Módulos nativos
log_info "8. Verificando módulos nativos críticos..."

REQUIRED_MODULES=("ssl" "sqlite3" "uuid" "lzma" "bz2" "zlib" "_ctypes")
FAILED_MODULES=()

for module in "${REQUIRED_MODULES[@]}"; do
    if "$PYTHON_BIN" -c "import $module" 2>/dev/null; then
        log_success "  Módulo $module: OK"
    else
        log_error "  Módulo $module: FALLO"
        FAILED_MODULES+=("$module")
    fi
done

if [ ${#FAILED_MODULES[@]} -gt 0 ]; then
    log_error "Módulos fallidos: ${FAILED_MODULES[*]}"
    rm -rf "$TEST_DIR"
    exit 1
fi

# Validación 9: pip disponible
log_info "9. Verificando pip..."

PIP_BIN="$TEST_DIR/$PYTHON_DIR/bin/pip${PYTHON_MAJOR_MINOR}"

if [ ! -f "$PIP_BIN" ]; then
    log_error "pip no encontrado"
    rm -rf "$TEST_DIR"
    exit 1
fi

chmod +x "$PIP_BIN"
PIP_VERSION=$("$PIP_BIN" --version 2>&1 | head -1)

log_success "pip disponible: $PIP_VERSION"

# Validación 10: Build info
log_info "10. Verificando build info..."

BUILD_INFO="$TEST_DIR/$PYTHON_DIR/.build-info"

if [ -f "$BUILD_INFO" ]; then
    log_success "Build info presente"
    log_info "Contenido:"
    head -10 "$BUILD_INFO" | sed 's/^/  /'
else
    log_warn "Build info no encontrado (opcional)"
fi

# Validación 11: LICENSE
log_info "11. Verificando LICENSE..."

LICENSE_FILE="$TEST_DIR/$PYTHON_DIR/LICENSE"

if [ -f "$LICENSE_FILE" ]; then
    log_success "LICENSE presente"
else
    log_warn "LICENSE no encontrado (recomendado incluirlo)"
fi

# Limpieza
log_info "Limpiando archivos temporales..."
rm -rf "$TEST_DIR"

# Resumen final
echo ""
log_success "=== Validación completada exitosamente ==="
log_info "Artefacto: $ARTIFACT_NAME"
log_info "Versión:   Python $PYTHON_VERSION"
log_info "Tamaño:    $ARTIFACT_SIZE_MB MB"
log_info "Checksum:  $CHECKSUM"
echo ""
log_success "El artefacto es válido y listo para distribución"
echo ""
log_info "Siguiente paso:"
log_info "  gh release create cpython-${PYTHON_VERSION}-build<N> \\"
log_info "    $ARTIFACT_PATH \\"
log_info "    $ARTIFACT_CHECKSUM \\"
log_info "    --title 'CPython $PYTHON_VERSION Build <N>' \\"
log_info "    --notes 'CPython precompilado para Ubuntu 22.04'"
