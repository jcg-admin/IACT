#!/bin/bash
# =============================================================================
# Utilidades Comunes para CPython Builder
# =============================================================================
# Referencia: SPEC_INFRA_001
# Proposito: Funciones auxiliares reutilizables para todos los scripts
# =============================================================================

# Cargar dependencias
if [ -z "$LOGGING_LOADED" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source "$SCRIPT_DIR/logging.sh"
    LOGGING_LOADED=1
fi

# Detectar version de OS
detect_os_version() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$VERSION_ID"
    else
        echo "unknown"
    fi
}

# Limpiar directorio temporal de forma segura
cleanup_temp_dir() {
    local temp_dir="$1"

    if [ -n "$temp_dir" ] && [ -d "$temp_dir" ]; then
        log_info "Limpiando archivos temporales: $temp_dir"
        rm -rf "$temp_dir"
    fi
}

# Descargar archivo con wget o curl
download_file() {
    local url="$1"
    local dest="$2"

    log_info "Descargando: $url"

    if command -v wget >/dev/null 2>&1; then
        wget -q --show-progress -O "$dest" "$url"
        return $?
    elif command -v curl >/dev/null 2>&1; then
        curl -fsSL -o "$dest" "$url"
        return $?
    else
        log_error "No se encontro wget ni curl"
        return 1
    fi
}

# Extraer tarball con validacion
extract_tarball() {
    local tarball="$1"
    local dest_dir="$2"

    if [ ! -f "$tarball" ]; then
        log_error "Tarball no encontrado: $tarball"
        return 1
    fi

    log_info "Extrayendo: $tarball"
    tar -xzf "$tarball" -C "$dest_dir"
    return $?
}

# Construir nombre de artefacto estandar
get_artifact_name() {
    local version="$1"
    local distro="$2"
    local build_number="$3"

    echo "cpython-${version}-${distro}-build${build_number}.tgz"
}

# Extraer major.minor de version (3.12.6 -> 3.12)
get_python_major_minor() {
    local version="$1"
    echo "$version" | cut -d. -f1,2
}
