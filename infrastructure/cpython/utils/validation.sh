#!/bin/bash
# =============================================================================
# Utilidades de Validacion para CPython Builder
# =============================================================================
# Referencia: SPEC_INFRA_001
# Proposito: Funciones de validacion reutilizables para todos los scripts
# =============================================================================

# Cargar logging si no esta cargado
if [ -z "$LOGGING_LOADED" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source "$SCRIPT_DIR/logging.sh"
    LOGGING_LOADED=1
fi

# Validar que un comando existe
validate_command_exists() {
    local cmd="$1"
    local error_msg="${2:-Command $cmd not found}"

    if ! command -v "$cmd" >/dev/null 2>&1; then
        log_error "$error_msg"
        return 1
    fi
    return 0
}

# Validar formato de version de Python (X.Y.Z)
validate_python_version() {
    local version="$1"

    if ! [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "Version invalida: $version"
        log_error "Formato esperado: X.Y.Z (ejemplo: 3.12.6)"
        return 1
    fi
    return 0
}

# Validar checksum SHA256
validate_checksum() {
    local file="$1"
    local checksum_file="$2"

    if [ ! -f "$file" ]; then
        log_error "Archivo no encontrado: $file"
        return 1
    fi

    if [ ! -f "$checksum_file" ]; then
        log_error "Checksum no encontrado: $checksum_file"
        return 1
    fi

    local dir=$(dirname "$file")
    local filename=$(basename "$file")

    cd "$dir"
    if ! sha256sum -c "$checksum_file" 2>&1 | grep -q "OK"; then
        log_error "Checksum SHA256 invalido"
        return 1
    fi

    return 0
}

# Validar que un archivo existe
validate_file_exists() {
    local file="$1"
    local error_msg="${2:-File not found: $file}"

    if [ ! -f "$file" ]; then
        log_error "$error_msg"
        return 1
    fi
    return 0
}

# Validar que un directorio existe
validate_dir_exists() {
    local dir="$1"
    local error_msg="${2:-Directory not found: $dir}"

    if [ ! -d "$dir" ]; then
        log_error "$error_msg"
        return 1
    fi
    return 0
}

# Validar modulos de Python
validate_python_modules() {
    local python_bin="$1"
    shift
    local modules=("$@")

    local failed_modules=()

    for module in "${modules[@]}"; do
        if "$python_bin" -c "import $module" 2>/dev/null; then
            log_success "  Modulo $module: OK"
        else
            log_error "  Modulo $module: FALLO"
            failed_modules+=("$module")
        fi
    done

    if [ ${#failed_modules[@]} -gt 0 ]; then
        log_error "Modulos fallidos: ${failed_modules[*]}"
        return 1
    fi

    return 0
}
