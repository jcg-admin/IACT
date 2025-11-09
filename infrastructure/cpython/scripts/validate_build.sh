#!/bin/bash
#
# validate_build.sh - Validar artefacto de CPython compilado
#
# Referencia: SPEC_INFRA_001
# Proposito: Verificar integridad y funcionalidad del artefacto
#
# Uso:
#   ./validate_build.sh <artifact-name>
#
# Ejemplo:
#   ./validate_build.sh cpython-3.12.6-ubuntu20.04-build1.tgz
#

set -euo pipefail

# Cargar utilidades
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-/vagrant}"

source "$SCRIPT_DIR/../utils/logging.sh" 2>/dev/null || source "$PROJECT_ROOT/utils/logging.sh"
source "$SCRIPT_DIR/../utils/validation.sh" 2>/dev/null || source "$PROJECT_ROOT/utils/validation.sh"
source "$SCRIPT_DIR/../utils/common.sh" 2>/dev/null || source "$PROJECT_ROOT/utils/common.sh"

# Cargar configuracion
if [ -f "$SCRIPT_DIR/../config/versions.conf" ]; then
    source "$SCRIPT_DIR/../config/versions.conf"
elif [ -f "$PROJECT_ROOT/config/versions.conf" ]; then
    source "$PROJECT_ROOT/config/versions.conf"
fi

# Validar argumentos
if [ $# -lt 1 ]; then
    log_error "Uso: $0 <artifact-name>"
    log_error "Ejemplo: $0 cpython-3.12.6-ubuntu20.04-build1.tgz"
    exit 1
fi

ARTIFACT_NAME="$1"
ARTIFACT_DIR="/vagrant/artifacts/cpython"
ARTIFACT_PATH="$ARTIFACT_DIR/$ARTIFACT_NAME"
ARTIFACT_CHECKSUM="$ARTIFACT_PATH.sha256"

log_info "=== Validacion de artefacto CPython ==="
log_info "Artefacto: $ARTIFACT_NAME"
echo ""

# Validacion 1: Artefacto existe
log_info "1. Verificando existencia del artefacto..."
if ! validate_file_exists "$ARTIFACT_PATH" "Artefacto no encontrado: $ARTIFACT_PATH"; then
    exit 1
fi
log_success "Artefacto existe"

# Validacion 2: Checksum existe
log_info "2. Verificando existencia de checksum..."
if ! validate_file_exists "$ARTIFACT_CHECKSUM" "Checksum no encontrado: $ARTIFACT_CHECKSUM"; then
    exit 1
fi
log_success "Checksum existe"

# Validacion 3: Verificar integridad SHA256
log_info "3. Verificando integridad SHA256..."
cd "$ARTIFACT_DIR"
if ! sha256sum -c "$ARTIFACT_NAME.sha256" 2>&1 | grep -q "OK"; then
    log_error "Checksum SHA256 invalido"
    exit 1
fi
CHECKSUM=$(cut -d' ' -f1 "$ARTIFACT_CHECKSUM")
log_success "Checksum valido: $CHECKSUM"

# Validacion 4: Tamaño razonable
log_info "4. Verificando tamaño del artefacto..."
ARTIFACT_SIZE=$(stat -f%z "$ARTIFACT_PATH" 2>/dev/null || stat -c%s "$ARTIFACT_PATH")
ARTIFACT_SIZE_MB=$((ARTIFACT_SIZE / 1024 / 1024))

if [ $ARTIFACT_SIZE_MB -lt 30 ]; then
    log_error "Artefacto muy pequeño ($ARTIFACT_SIZE_MB MB). Minimo esperado: 30 MB"
    exit 1
fi

if [ $ARTIFACT_SIZE_MB -gt 150 ]; then
    log_warn "Artefacto muy grande ($ARTIFACT_SIZE_MB MB). Maximo esperado: 150 MB"
fi

log_success "Tamaño razonable: $ARTIFACT_SIZE_MB MB"

# Validacion 5: Contenido del tarball
log_info "5. Verificando contenido del tarball..."

# Listar contenido sin extraer
TARBALL_CONTENT=$(tar tzf "$ARTIFACT_PATH" | head -20)

# Verificar que contiene opt/python-X.Y.Z/
if ! echo "$TARBALL_CONTENT" | grep -q "^opt/python-[0-9]"; then
    log_error "Tarball no contiene directorio opt/python-X.Y.Z/"
    exit 1
fi

log_success "Estructura de directorio correcta"

# Validacion 6: Extraer y verificar binarios
log_info "6. Extrayendo temporalmente para verificar binarios..."

TEST_DIR="/tmp/cpython-validate-$$"
mkdir -p "$TEST_DIR"

cd "$TEST_DIR"
if ! extract_tarball "$ARTIFACT_PATH" "$TEST_DIR"; then
    log_error "Fallo al extraer tarball"
    cleanup_temp_dir "$TEST_DIR"
    exit 1
fi

# Detectar version de Python del artefacto
PYTHON_DIR=$(find opt -maxdepth 1 -name "python-*" -type d | head -1)

if [ -z "$PYTHON_DIR" ]; then
    log_error "No se encontro directorio python-* en artefacto"
    cleanup_temp_dir "$TEST_DIR"
    exit 1
fi

PYTHON_VERSION=$(basename "$PYTHON_DIR" | sed 's/python-//')
PYTHON_MAJOR_MINOR=$(get_python_major_minor "$PYTHON_VERSION")

log_info "Version detectada: $PYTHON_VERSION"

# Verificar binario principal
PYTHON_BIN="$TEST_DIR/$PYTHON_DIR/bin/python${PYTHON_MAJOR_MINOR}"

if ! validate_file_exists "$PYTHON_BIN" "Binario de Python no encontrado: $PYTHON_BIN"; then
    cleanup_temp_dir "$TEST_DIR"
    exit 1
fi

# Hacer ejecutable
chmod +x "$PYTHON_BIN"

log_success "Binario existe y es ejecutable"

# Validacion 7: Version del binario
log_info "7. Verificando version del binario..."

# Configurar LD_LIBRARY_PATH para librerias compartidas
export LD_LIBRARY_PATH="$TEST_DIR/$PYTHON_DIR/lib:${LD_LIBRARY_PATH:-}"

BINARY_VERSION=$("$PYTHON_BIN" --version 2>&1 | awk '{print $2}')

if [ "$BINARY_VERSION" != "$PYTHON_VERSION" ]; then
    log_error "Version del binario ($BINARY_VERSION) no coincide con esperada ($PYTHON_VERSION)"
    cleanup_temp_dir "$TEST_DIR"
    exit 1
fi

log_success "Version correcta: $BINARY_VERSION"

# Validacion 8: Modulos nativos usando utilidad
log_info "8. Verificando modulos nativos criticos..."

# Usar REQUIRED_MODULES del config si existe, sino usar default
MODULES_TO_CHECK=("${REQUIRED_MODULES[@]:-ssl sqlite3 uuid lzma bz2 zlib _ctypes}")

FAILED_MODULES=()

for module in "${MODULES_TO_CHECK[@]}"; do
    if "$PYTHON_BIN" -c "import $module" 2>/dev/null; then
        log_success "  Modulo $module: OK"
    else
        log_error "  Modulo $module: FALLO"
        FAILED_MODULES+=("$module")
    fi
done

if [ ${#FAILED_MODULES[@]} -gt 0 ]; then
    log_error "Modulos fallidos: ${FAILED_MODULES[*]}"
    cleanup_temp_dir "$TEST_DIR"
    exit 1
fi

# Validacion 9: pip disponible
log_info "9. Verificando pip..."

PIP_BIN="$TEST_DIR/$PYTHON_DIR/bin/pip${PYTHON_MAJOR_MINOR}"

if ! validate_file_exists "$PIP_BIN" "pip no encontrado"; then
    cleanup_temp_dir "$TEST_DIR"
    exit 1
fi

chmod +x "$PIP_BIN"
PIP_VERSION=$("$PIP_BIN" --version 2>&1 | head -1)

log_success "pip disponible: $PIP_VERSION"

# Validacion 10: Build info
log_info "10. Verificando build info..."

BUILD_INFO="$TEST_DIR/$PYTHON_DIR/.build-info"

if [ -f "$BUILD_INFO" ]; then
    log_success "Build info presente"
    log_info "Contenido:"
    head -10 "$BUILD_INFO" | sed 's/^/  /'
else
    log_warn "Build info no encontrado (opcional)"
fi

# Validacion 11: LICENSE
log_info "11. Verificando LICENSE..."

LICENSE_FILE="$TEST_DIR/$PYTHON_DIR/LICENSE"

if [ -f "$LICENSE_FILE" ]; then
    log_success "LICENSE presente"
else
    log_warn "LICENSE no encontrado (recomendado incluirlo)"
fi

# Limpieza usando utilidad
log_info "Limpiando archivos temporales..."
cleanup_temp_dir "$TEST_DIR"

# Resumen final
echo ""
log_success "=== Validacion completada exitosamente ==="
log_info "Artefacto: $ARTIFACT_NAME"
log_info "Version:   Python $PYTHON_VERSION"
log_info "Tamaño:    $ARTIFACT_SIZE_MB MB"
log_info "Checksum:  $CHECKSUM"
echo ""
log_success "El artefacto es valido y listo para distribucion"
echo ""
log_info "Siguiente paso:"
log_info "  gh release create cpython-${PYTHON_VERSION}-build<N> \\"
log_info "    $ARTIFACT_PATH \\"
log_info "    $ARTIFACT_CHECKSUM \\"
log_info "    --title 'CPython $PYTHON_VERSION Build <N>' \\"
log_info "    --notes 'CPython precompilado para Ubuntu 20.04'"