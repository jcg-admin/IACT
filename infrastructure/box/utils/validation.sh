#!/bin/bash

# ============================================================================
# VALIDATION UTILITIES
# ============================================================================
# Propósito: Verificar estado del sistema antes de instalar o configurar
# Uso: source utils/validation.sh
# ============================================================================

# Verifica si el sistema operativo es Ubuntu 20.04, 22.04 o 24.04
validate_ubuntu_version() {
    local version
    version=$(lsb_release -rs)
    [[ "$version" =~ ^(20\.04|22\.04|24\.04)$ ]]
}

# Verifica si el usuario tiene acceso sudo sin contraseña
validate_sudo() {
    sudo -n true 2>/dev/null || sudo -v
}

# Verifica espacio libre en disco (en MB)
validate_disk_space() {
    local path="$1"
    local min_mb="$2"
    local available
    available=$(df -Pm "$path" | awk 'NR==2 {print $4}')
    [[ "$available" -ge "$min_mb" ]]
}

# Verifica cantidad de RAM disponible (en MB)
validate_ram() {
    local min_mb="$1"
    local total
    total=$(free -m | awk '/^Mem:/ {print $2}')
    [[ "$total" -ge "$min_mb" ]]
}

# Verifica si todos los comandos requeridos existen
validate_commands_exist() {
    for cmd in "$@"; do
        if ! command -v "$cmd" &>/dev/null; then
            return 1
        fi
    done
    return 0
}
