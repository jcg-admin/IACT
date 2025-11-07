#!/bin/bash
#
# build_cpython.sh - Compilar CPython desde codigo fuente
#
# Referencia: SPEC_INFRA_001
# Proposito: Generar artefacto de CPython precompilado reproducible
#
# Uso:
#   ./build_cpython.sh <version> [build-number]
#
# Ejemplos:
#   ./build_cpython.sh 3.12.6
#   ./build_cpython.sh 3.12.6 2
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
    log_error "Uso: $0 <version> [build-number]"
    log_error "Ejemplo: $0 3.12.6 1"
    exit 1
fi

PYTHON_VERSION="$1"
BUILD_NUMBER="${2:-${DEFAULT_BUILD_NUMBER:-1}}"
DISTRO="${DISTRO:-ubuntu22.04}"

# Validar formato de version usando utilidad
if ! validate_python_version "$PYTHON_VERSION"; then
    exit 1
fi

# Extraer major.minor para directorios usando utilidad
PYTHON_MAJOR_MINOR=$(get_python_major_minor "$PYTHON_VERSION")

# Configuracion
BUILD_DIR="/tmp/cpython-build"
SOURCE_DIR="$BUILD_DIR/Python-$PYTHON_VERSION"
INSTALL_PREFIX="/opt/python-$PYTHON_VERSION"
ARTIFACT_DIR="/vagrant/artifacts/cpython"
ARTIFACT_NAME=$(get_artifact_name "$PYTHON_VERSION" "$DISTRO" "$BUILD_NUMBER")
ARTIFACT_PATH="$ARTIFACT_DIR/$ARTIFACT_NAME"

log_info "=== Compilacion de CPython $PYTHON_VERSION ==="
log_info "Build number: $BUILD_NUMBER"
log_info "Distro: $DISTRO"
log_info "Artefacto: $ARTIFACT_NAME"
echo ""

# Verificar que no existe artefacto previo
if [ -f "$ARTIFACT_PATH" ]; then
    log_warn "Artefacto ya existe: $ARTIFACT_PATH"
    read -p "¿Sobrescribir? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Abortando compilacion"
        exit 0
    fi
    rm -f "$ARTIFACT_PATH" "$ARTIFACT_PATH.sha256"
fi

# Crear directorios
log_info "Creando directorios de trabajo..."
mkdir -p "$BUILD_DIR"
mkdir -p "$ARTIFACT_DIR"

# Verificar versiones de dependencias criticas
log_info "Verificando dependencias del sistema..."
dpkg -l | grep -E "libssl-dev|libsqlite3-dev|liblzma-dev|libbz2-dev|libffi-dev" | awk '{print "  " $2 ": " $3}'

# Descargar codigo fuente
log_info "Descargando codigo fuente de Python $PYTHON_VERSION..."
cd "$BUILD_DIR"

PYTHON_URL="${PYTHON_DOWNLOAD_BASE:-https://www.python.org/ftp/python}/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"

if [ -d "$SOURCE_DIR" ]; then
    log_warn "Directorio de codigo fuente ya existe, usando existente"
else
    log_info "Descargando desde: $PYTHON_URL"
    if ! wget -q --show-progress "$PYTHON_URL"; then
        log_error "Fallo al descargar codigo fuente"
        exit 1
    fi

    log_info "Extrayendo codigo fuente..."
    tar xzf "Python-$PYTHON_VERSION.tgz"

    if [ ! -d "$SOURCE_DIR" ]; then
        log_error "Directorio de codigo fuente no encontrado despues de extraccion"
        exit 1
    fi
fi

cd "$SOURCE_DIR"

# Configurar compilacion
log_info "Configurando compilacion con optimizaciones..."
log_info "Flags de configuracion:"
log_info "  --prefix=$INSTALL_PREFIX"
log_info "  --enable-optimizations (PGO)"
log_info "  --with-lto (Link-Time Optimization)"
log_info "  --enable-shared"
log_info "  --with-system-ffi"
echo ""

# Limpiar build anterior si existe
if [ -f "Makefile" ]; then
    log_info "Limpiando build anterior..."
    make distclean || true
fi

# Ejecutar configure
./configure \
    --prefix="$INSTALL_PREFIX" \
    --enable-optimizations \
    --with-lto \
    --enable-shared \
    --with-system-ffi \
    --enable-loadable-sqlite-extensions \
    2>&1 | tee configure.log

# Compilar
log_info "Compilando Python (esto puede tardar 10-15 minutos con PGO)..."
log_info "Usando $(nproc) cores en paralelo..."
echo ""

# make con progress
if ! make -j"$(nproc)" 2>&1 | tee make.log; then
    log_error "Compilacion fallo. Ver make.log para detalles"
    exit 1
fi

log_success "Compilacion completada"

# Instalar
log_info "Instalando en $INSTALL_PREFIX..."
if ! sudo make install 2>&1 | tee make-install.log; then
    log_error "Instalacion fallo. Ver make-install.log para detalles"
    exit 1
fi

log_success "Instalacion completada"

# Validar instalacion
log_info "Validando instalacion..."

if ! validate_file_exists "$INSTALL_PREFIX/bin/python${PYTHON_MAJOR_MINOR}" "Binario de Python no encontrado"; then
    exit 1
fi

# Verificar version
INSTALLED_VERSION=$("$INSTALL_PREFIX/bin/python${PYTHON_MAJOR_MINOR}" --version 2>&1 | awk '{print $2}')
if [ "$INSTALLED_VERSION" != "$PYTHON_VERSION" ]; then
    log_error "Version instalada ($INSTALLED_VERSION) no coincide con esperada ($PYTHON_VERSION)"
    exit 1
fi

log_success "Version correcta: $INSTALLED_VERSION"

# Validar modulos nativos criticos usando utilidad
log_info "Validando modulos nativos..."

# Usar REQUIRED_MODULES del config si existe, sino usar default
MODULES_TO_CHECK=("${REQUIRED_MODULES[@]:-ssl sqlite3 uuid lzma bz2 zlib _ctypes}")

if ! validate_python_modules "$INSTALL_PREFIX/bin/python${PYTHON_MAJOR_MINOR}" "${MODULES_TO_CHECK[@]}"; then
    log_error "Fallo validacion de modulos"
    exit 1
fi

# Verificar pip
if ! validate_file_exists "$INSTALL_PREFIX/bin/pip${PYTHON_MAJOR_MINOR}" "pip no encontrado"; then
    exit 1
fi

PIP_VERSION=$("$INSTALL_PREFIX/bin/pip${PYTHON_MAJOR_MINOR}" --version 2>&1)
log_success "pip disponible: $PIP_VERSION"

# Documentar versiones de librerias
log_info "Documentando versiones de librerias del sistema..."
cat > "$INSTALL_PREFIX/.build-info" <<EOF
CPython Build Information
=========================

Version: $PYTHON_VERSION
Build Number: $BUILD_NUMBER
Distro: $DISTRO
Build Date: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Build Host: $(hostname)

System Libraries:
$(dpkg -l | grep -E "libssl-dev|libsqlite3-dev|liblzma-dev|libbz2-dev|libffi-dev" | awk '{print $2 ": " $3}')

Configure Flags:
  --prefix=$INSTALL_PREFIX
  --enable-optimizations
  --with-lto
  --enable-shared
  --with-system-ffi
  --enable-loadable-sqlite-extensions

Validated Modules:
$(for mod in "${MODULES_TO_CHECK[@]}"; do echo "  - $mod"; done)
EOF

log_success "Build info guardado en $INSTALL_PREFIX/.build-info"

# Incluir LICENSE de Python (PSF)
log_info "Copiando LICENSE de Python..."
if [ -f "LICENSE" ]; then
    sudo cp LICENSE "$INSTALL_PREFIX/LICENSE"
    log_success "LICENSE copiado"
else
    log_warn "LICENSE no encontrado en codigo fuente"
fi

# Empaquetar artefacto
log_info "Empaquetando artefacto..."

cd /opt
if ! sudo tar czf "$ARTIFACT_PATH" "python-$PYTHON_VERSION"; then
    log_error "Fallo al crear tarball"
    exit 1
fi

# Ajustar permisos
sudo chown vagrant:vagrant "$ARTIFACT_PATH" 2>/dev/null || chown "$(whoami):$(whoami)" "$ARTIFACT_PATH"

ARTIFACT_SIZE=$(du -h "$ARTIFACT_PATH" | cut -f1)
log_success "Artefacto creado: $ARTIFACT_PATH ($ARTIFACT_SIZE)"

# Generar checksum SHA256
log_info "Generando checksum SHA256..."
cd "$ARTIFACT_DIR"
sha256sum "$ARTIFACT_NAME" > "$ARTIFACT_NAME.sha256"

CHECKSUM=$(cut -d' ' -f1 "$ARTIFACT_NAME.sha256")
log_success "Checksum: $CHECKSUM"

# Resumen final
echo ""
log_success "=== Compilacion completada exitosamente ==="
log_info "Artefacto: $ARTIFACT_PATH"
log_info "Checksum:  $ARTIFACT_PATH.sha256"
log_info "Tamaño:    $ARTIFACT_SIZE"
echo ""
log_info "Siguiente paso:"
log_info "  1. Validar artefacto: ./validate_build.sh $ARTIFACT_NAME"
log_info "  2. Publicar en GitHub Releases (manual o con gh CLI)"
log_info "  3. Actualizar artifacts/ARTIFACTS.md"
echo ""
log_info "Metadata del build guardado en: $INSTALL_PREFIX/.build-info"
