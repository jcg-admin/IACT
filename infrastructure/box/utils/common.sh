#!/bin/bash

# ============================================================================
# COMMON UTILITIES
# ============================================================================
# Propósito: Funciones genéricas reutilizables en todo el pipeline
# Uso: source utils/common.sh
# ============================================================================

# Convierte texto a mayúsculas
to_uppercase() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
}

# Crea un directorio si no existe
create_directory() {
    local dir="$1"
    [[ -d "$dir" ]] || mkdir -p "$dir"
}

# Crea un directorio temporal
create_temp_dir() {
    mktemp -d /tmp/bootstrap.XXXXXX
}

# Descarga un archivo desde una URL
download_file() {
    local url="$1"
    local dest="$2"
    local label="$3"
    curl -fsSL "$url" -o "$dest" || {
        echo "[ERROR] Falló la descarga de $label desde $url"
        return 1
    }
}

# Habilita y arranca un servicio
enable_service() {
    local svc="$1"
    sudo systemctl enable --now "$svc"
}
