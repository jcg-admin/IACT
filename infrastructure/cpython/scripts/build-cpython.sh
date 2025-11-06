#!/bin/bash
#
# build-cpython.sh - Compilar CPython desde código fuente
#
# Referencia: SPEC-INFRA-001
# Propósito: Generar artefacto de CPython precompilado reproducible
#
# Uso:
#   ./build-cpython.sh <version> [build-number]
#
# Ejemplos:
#   ./build-cpython.sh 3.12.6
#   ./build-cpython.sh 3.12.6 2
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
    log_error "Uso: $0 <version> [build-number]"
    log_error "Ejemplo: $0 3.12.6 1"
    exit 1
fi

PYTHON_VERSION="$1"
BUILD_NUMBER="${2:-1}"
DISTRO="ubuntu22.04"

# Validar formato de versión (X.Y.Z)
if ! [[ "$PYTHON_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    log_error "Versión inválida: $PYTHON_VERSION"
    log_error "Formato esperado: X.Y.Z (ejemplo: 3.12.6)"
    exit 1
fi

# Extraer major.minor para directorios
PYTHON_MAJOR_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f1,2)

# Configuración
BUILD_DIR="/tmp/cpython-build"
SOURCE_DIR="$BUILD_DIR/Python-$PYTHON_VERSION"
INSTALL_PREFIX="/opt/python-$PYTHON_VERSION"
ARTIFACT_DIR="/vagrant/artifacts/cpython"
ARTIFACT_NAME="cpython-${PYTHON_VERSION}-${DISTRO}-build${BUILD_NUMBER}.tgz"
ARTIFACT_PATH="$ARTIFACT_DIR/$ARTIFACT_NAME"

log_info "=== Compilación de CPython $PYTHON_VERSION ==="
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
        log_info "Abortando compilación"
        exit 0
    fi
    rm -f "$ARTIFACT_PATH" "$ARTIFACT_PATH.sha256"
fi

# Crear directorios
log_info "Creando directorios de trabajo..."
mkdir -p "$BUILD_DIR"
mkdir -p "$ARTIFACT_DIR"

# Verificar versiones de dependencias críticas
log_info "Verificando dependencias del sistema..."
dpkg -l | grep -E "libssl-dev|libsqlite3-dev|liblzma-dev|libbz2-dev|libffi-dev" | awk '{print "  " $2 ": " $3}'

# Descargar código fuente
log_info "Descargando código fuente de Python $PYTHON_VERSION..."
cd "$BUILD_DIR"

PYTHON_URL="https://www.python.org/ftp/python/$PYTHON_VERSION/Python-$PYTHON_VERSION.tgz"

if [ -d "$SOURCE_DIR" ]; then
    log_warn "Directorio de código fuente ya existe, usando existente"
else
    log_info "Descargando desde: $PYTHON_URL"
    if ! wget -q --show-progress "$PYTHON_URL"; then
        log_error "Fallo al descargar código fuente"
        exit 1
    fi

    log_info "Extrayendo código fuente..."
    tar xzf "Python-$PYTHON_VERSION.tgz"

    if [ ! -d "$SOURCE_DIR" ]; then
        log_error "Directorio de código fuente no encontrado después de extracción"
        exit 1
    fi
fi

cd "$SOURCE_DIR"

# Configurar compilación
log_info "Configurando compilación con optimizaciones..."
log_info "Flags de configuración:"
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
    log_error "Compilación falló. Ver make.log para detalles"
    exit 1
fi

log_success "Compilación completada"

# Instalar
log_info "Instalando en $INSTALL_PREFIX..."
if ! sudo make install 2>&1 | tee make-install.log; then
    log_error "Instalación falló. Ver make-install.log para detalles"
    exit 1
fi

log_success "Instalación completada"

# Validar instalación
log_info "Validando instalación..."

if [ ! -f "$INSTALL_PREFIX/bin/python${PYTHON_MAJOR_MINOR}" ]; then
    log_error "Binario de Python no encontrado en $INSTALL_PREFIX/bin/"
    exit 1
fi

# Verificar versión
INSTALLED_VERSION=$("$INSTALL_PREFIX/bin/python${PYTHON_MAJOR_MINOR}" --version 2>&1 | awk '{print $2}')
if [ "$INSTALLED_VERSION" != "$PYTHON_VERSION" ]; then
    log_error "Versión instalada ($INSTALLED_VERSION) no coincide con esperada ($PYTHON_VERSION)"
    exit 1
fi

log_success "Versión correcta: $INSTALLED_VERSION"

# Validar módulos nativos críticos
log_info "Validando módulos nativos..."

REQUIRED_MODULES=("ssl" "sqlite3" "uuid" "lzma" "bz2" "zlib" "_ctypes")
for module in "${REQUIRED_MODULES[@]}"; do
    if "$INSTALL_PREFIX/bin/python${PYTHON_MAJOR_MINOR}" -c "import $module" 2>/dev/null; then
        log_success "  Módulo $module: OK"
    else
        log_error "  Módulo $module: FALLO"
        log_error "Módulo crítico $module no disponible"
        exit 1
    fi
done

# Verificar pip
if [ ! -f "$INSTALL_PREFIX/bin/pip${PYTHON_MAJOR_MINOR}" ]; then
    log_error "pip no encontrado"
    exit 1
fi

PIP_VERSION=$("$INSTALL_PREFIX/bin/pip${PYTHON_MAJOR_MINOR}" --version 2>&1)
log_success "pip disponible: $PIP_VERSION"

# Documentar versiones de librerías
log_info "Documentando versiones de librerías del sistema..."
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
$(for mod in "${REQUIRED_MODULES[@]}"; do echo "  - $mod"; done)
EOF

log_success "Build info guardado en $INSTALL_PREFIX/.build-info"

# Incluir LICENSE de Python (PSF)
log_info "Copiando LICENSE de Python..."
if [ -f "LICENSE" ]; then
    sudo cp LICENSE "$INSTALL_PREFIX/LICENSE"
    log_success "LICENSE copiado"
else
    log_warn "LICENSE no encontrado en código fuente"
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
log_success "=== Compilación completada exitosamente ==="
log_info "Artefacto: $ARTIFACT_PATH"
log_info "Checksum:  $ARTIFACT_PATH.sha256"
log_info "Tamaño:    $ARTIFACT_SIZE"
echo ""
log_info "Siguiente paso:"
log_info "  1. Validar artefacto: ./validate-build.sh $ARTIFACT_NAME"
log_info "  2. Publicar en GitHub Releases (manual o con gh CLI)"
log_info "  3. Actualizar artifacts/ARTIFACTS.md"
echo ""
log_info "Metadata del build guardado en: $INSTALL_PREFIX/.build-info"
