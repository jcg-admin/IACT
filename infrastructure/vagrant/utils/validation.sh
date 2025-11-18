#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - Validation Utilities
# =============================================================================
# Description: Validation utilities for Vagrant environment
# Author: IACT Team
# Version: 2.0.0
# Context: Vagrant-specific validation
# =============================================================================

# Prevenir ejecucion directa
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: Este script debe ser 'sourced', no ejecutado directamente"
    exit 1
fi

# =============================================================================
# DISK SPACE VALIDATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_validate_disk_space
# Description: Validate available disk space
# Arguments: $1 - required space in GB (default: 5)
# Returns: 0 if enough space, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_disk_space() {
    local required_gb="${1:-5}"
    local available_kb
    available_kb=$(df / | awk 'NR==2 {print $4}')
    local available_gb=$((available_kb / 1024 / 1024))

    if [[ $available_gb -lt $required_gb ]]; then
        echo "Error: Espacio insuficiente. Requerido: ${required_gb}GB, Disponible: ${available_gb}GB" >&2
        return 1
    fi

    return 0
}

# =============================================================================
# UBUNTU VERSION VALIDATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_validate_ubuntu_version
# Description: Validate Ubuntu version
# Arguments: $1 - required version (e.g., "18.04")
# Returns: 0 if correct version, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_ubuntu_version() {
    local required_version="$1"

    if [[ ! -f /etc/os-release ]]; then
        echo "Error: Archivo /etc/os-release no encontrado" >&2
        return 1
    fi

    source /etc/os-release

    if [[ "$ID" != "ubuntu" ]]; then
        echo "Error: Sistema operativo debe ser Ubuntu, detectado: $ID" >&2
        return 1
    fi

    if [[ "$VERSION_ID" != "$required_version" ]]; then
        echo "Error: Version de Ubuntu debe ser $required_version, detectado: $VERSION_ID" >&2
        return 1
    fi

    return 0
}

# =============================================================================
# NETWORK VALIDATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_validate_internet
# Description: Validate internet connectivity
# Returns: 0 if connected, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_internet() {
    local hosts=("8.8.8.8" "1.1.1.1")

    for host in "${hosts[@]}"; do
        if ping -c 1 -W 2 "$host" >/dev/null 2>&1; then
            return 0
        fi
    done

    echo "Error: Sin conectividad a internet" >&2
    return 1
}

# =============================================================================
# PACKAGE VALIDATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_validate_package_installed
# Description: Validate if a package is installed
# Arguments: $1 - package name
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_package_installed() {
    local package="$1"

    if dpkg -l "$package" 2>/dev/null | grep -q "^ii"; then
        return 0
    else
        echo "Error: Paquete '$package' no esta instalado" >&2
        return 1
    fi
}

# =============================================================================
# EXPORT
# =============================================================================

export -f iact_validate_disk_space
export -f iact_validate_ubuntu_version
export -f iact_validate_internet
export -f iact_validate_package_installed