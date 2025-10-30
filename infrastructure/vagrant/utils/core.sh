#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - Core Utilities
# =============================================================================
# Description: Core utilities for Vagrant environment
# Author: IACT Team
# Version: 2.0.0
# Context: Vagrant-specific utilities
# =============================================================================

# Prevenir ejecución directa
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: Este script debe ser 'sourced', no ejecutado directamente"
    echo "Uso: source ${BASH_SOURCE[0]}"
    exit 1
fi

# =============================================================================
# VARIABLES GLOBALES
# =============================================================================

# Detectar si estamos en Vagrant
readonly VAGRANT_UTILS_IN_VAGRANT="${VAGRANT:-false}"
readonly VAGRANT_UTILS_HOSTNAME="${HOSTNAME:-unknown}"

# Directorio de utilidades de Vagrant
if [[ -d "/vagrant" ]]; then
    readonly VAGRANT_UTILS_DIR="/vagrant/infrastructure/vagrant/utils"
else
    readonly VAGRANT_UTILS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Auto-cargar logging si existe
if [[ -f "${VAGRANT_UTILS_DIR}/logging.sh" ]]; then
    source "${VAGRANT_UTILS_DIR}/logging.sh"
fi

# =============================================================================
# CONTEXT DETECTION
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_utils_get_context
# Description: Get execution context (vagrant or local)
# Returns: String with context
# -----------------------------------------------------------------------------
vagrant_utils_get_context() {
    if [[ -d "/vagrant" ]] || [[ "$VAGRANT_UTILS_IN_VAGRANT" == "true" ]]; then
        echo "vagrant"
    else
        echo "local"
    fi
}

# -----------------------------------------------------------------------------
# vagrant_utils_is_vagrant
# Description: Check if running in Vagrant environment
# Returns: 0 if in Vagrant, 1 otherwise
# -----------------------------------------------------------------------------
vagrant_utils_is_vagrant() {
    [[ "$(vagrant_utils_get_context)" == "vagrant" ]]
}

# -----------------------------------------------------------------------------
# vagrant_utils_get_project_root
# Description: Get project root directory
# Returns: String with absolute path to project root
# -----------------------------------------------------------------------------
vagrant_utils_get_project_root() {
    if vagrant_utils_is_vagrant; then
        echo "/vagrant"
    else
        # Asumir que estamos 3 niveles abajo: infrastructure/vagrant/utils
        echo "$(cd "$(dirname "${VAGRANT_UTILS_DIR}")/../.." && pwd)"
    fi
}

# =============================================================================
# MODULE LOADING
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_utils_source_module
# Description: Source a Vagrant utility module safely
# Arguments: $1 - module name (without .sh extension)
# Returns: 0 on success, 1 on failure
# Example: vagrant_utils_source_module "validation"
# -----------------------------------------------------------------------------
vagrant_utils_source_module() {
    local module_name="$1"
    local module_path="${VAGRANT_UTILS_DIR}/${module_name}.sh"

    if [[ ! -f "$module_path" ]]; then
        echo "Error: Modulo '$module_name' no encontrado en: $module_path" >&2
        return 1
    fi

    if [[ "${VAGRANT_UTILS_LOADED_MODULES[$module_name]:-}" == "1" ]]; then
        return 0
    fi

    source "$module_path"
    declare -gA VAGRANT_UTILS_LOADED_MODULES
    VAGRANT_UTILS_LOADED_MODULES[$module_name]=1
    return 0
}

# =============================================================================
# SYSTEM INFORMATION
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_utils_get_os_info
# Description: Get OS information
# Returns: String with OS name and version
# -----------------------------------------------------------------------------
vagrant_utils_get_os_info() {
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        echo "${NAME} ${VERSION_ID}"
    else
        uname -s
    fi
}

# -----------------------------------------------------------------------------
# vagrant_utils_get_memory_info
# Description: Get memory information in GB
# Returns: String with total memory
# -----------------------------------------------------------------------------
vagrant_utils_get_memory_info() {
    local mem_kb
    mem_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local mem_gb=$((mem_kb / 1024 / 1024))
    echo "${mem_gb}GB"
}

# -----------------------------------------------------------------------------
# vagrant_utils_get_disk_info
# Description: Get disk space information for root partition
# Returns: String with available/total space
# -----------------------------------------------------------------------------
vagrant_utils_get_disk_info() {
    df -h / | awk 'NR==2 {print $4 " / " $2}'
}

# =============================================================================
# COMMAND VERIFICATION
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_utils_command_exists
# Description: Check if a command exists
# Arguments: $1 - command name
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
vagrant_utils_command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# -----------------------------------------------------------------------------
# vagrant_utils_verify_commands
# Description: Verify that required commands exist
# Arguments: $@ - list of command names
# Returns: 0 if all exist, 1 if any missing
# -----------------------------------------------------------------------------
vagrant_utils_verify_commands() {
    local missing_commands=()

    for cmd in "$@"; do
        if ! vagrant_utils_command_exists "$cmd"; then
            missing_commands+=("$cmd")
        fi
    done

    if [[ ${#missing_commands[@]} -gt 0 ]]; then
        echo "Error: Comandos faltantes: ${missing_commands[*]}" >&2
        return 1
    fi

    return 0
}

# =============================================================================
# FILE OPERATIONS
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_utils_backup_file
# Description: Create a backup of a file with timestamp
# Arguments: $1 - file path
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
vagrant_utils_backup_file() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        echo "Error: Archivo '$file' no existe" >&2
        return 1
    fi

    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local backup="${file}.backup.${timestamp}"

    if cp "$file" "$backup"; then
        echo "Backup creado: $backup"
        return 0
    else
        echo "Error: No se pudo crear backup de '$file'" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# vagrant_utils_safe_copy
# Description: Safely copy file, creating backup if destination exists
# Arguments: $1 - source, $2 - destination
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
vagrant_utils_safe_copy() {
    local src="$1"
    local dst="$2"

    if [[ ! -f "$src" ]]; then
        echo "Error: Archivo fuente '$src' no existe" >&2
        return 1
    fi

    # Backup if destination exists
    if [[ -f "$dst" ]]; then
        vagrant_utils_backup_file "$dst" || return 1
    fi

    # Create destination directory if needed
    local dst_dir
    dst_dir=$(dirname "$dst")
    mkdir -p "$dst_dir"

    # Copy file
    if cp "$src" "$dst"; then
        echo "Archivo copiado: $src -> $dst"
        return 0
    else
        echo "Error: No se pudo copiar '$src' a '$dst'" >&2
        return 1
    fi
}

# =============================================================================
# SERVICE MANAGEMENT
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_utils_service_is_running
# Description: Check if a systemd service is running
# Arguments: $1 - service name
# Returns: 0 if running, 1 otherwise
# -----------------------------------------------------------------------------
vagrant_utils_service_is_running() {
    local service="$1"
    systemctl is-active --quiet "$service"
}

# -----------------------------------------------------------------------------
# vagrant_utils_wait_for_service
# Description: Wait for a service to be running
# Arguments: $1 - service name, $2 - max wait time in seconds (default: 30)
# Returns: 0 if service started, 1 on timeout
# -----------------------------------------------------------------------------
vagrant_utils_wait_for_service() {
    local service="$1"
    local max_wait="${2:-30}"
    local counter=0

    while [[ $counter -lt $max_wait ]]; do
        if vagrant_utils_service_is_running "$service"; then
            return 0
        fi

        sleep 1
        ((counter++))
    done

    echo "Error: Servicio '$service' no inicio en ${max_wait}s" >&2
    return 1
}

# =============================================================================
# NETWORK UTILITIES
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_utils_check_connectivity
# Description: Check internet connectivity
# Arguments: $1 - host to ping (default: 8.8.8.8)
# Returns: 0 if connected, 1 otherwise
# -----------------------------------------------------------------------------
vagrant_utils_check_connectivity() {
    local host="${1:-8.8.8.8}"
    ping -c 1 -W 2 "$host" >/dev/null 2>&1
}

# -----------------------------------------------------------------------------
# vagrant_utils_wait_for_port
# Description: Wait for a port to be available
# Arguments: $1 - host, $2 - port, $3 - max wait time (default: 30)
# Returns: 0 if port is available, 1 on timeout
# -----------------------------------------------------------------------------
vagrant_utils_wait_for_port() {
    local host="$1"
    local port="$2"
    local max_wait="${3:-30}"
    local counter=0

    while [[ $counter -lt $max_wait ]]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            return 0
        fi

        sleep 1
        ((counter++))
    done

    echo "Error: Puerto $host:$port no disponible en ${max_wait}s" >&2
    return 1
}

# =============================================================================
# STRING UTILITIES
# =============================================================================

# -----------------------------------------------------------------------------
# vagrant_utils_trim
# Description: Trim whitespace from string
# Arguments: $1 - string to trim
# Returns: Trimmed string via stdout
# -----------------------------------------------------------------------------
vagrant_utils_trim() {
    local str="$1"
    # Remove leading whitespace
    str="${str#"${str%%[![:space:]]*}"}"
    # Remove trailing whitespace
    str="${str%"${str##*[![:space:]]}"}"
    echo "$str"
}

# -----------------------------------------------------------------------------
# vagrant_utils_to_lower
# Description: Convert string to lowercase
# Arguments: $1 - string
# Returns: Lowercase string via stdout
# -----------------------------------------------------------------------------
vagrant_utils_to_lower() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

# -----------------------------------------------------------------------------
# vagrant_utils_to_upper
# Description: Convert string to uppercase
# Arguments: $1 - string
# Returns: Uppercase string via stdout
# -----------------------------------------------------------------------------
vagrant_utils_to_upper() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
}

# =============================================================================
# INITIALIZATION
# =============================================================================

# Declare global array for loaded modules
declare -gA VAGRANT_UTILS_LOADED_MODULES
VAGRANT_UTILS_LOADED_MODULES["core"]=1

# Export main functions
export -f vagrant_utils_get_context
export -f vagrant_utils_is_vagrant
export -f vagrant_utils_get_project_root
export -f vagrant_utils_source_module
export -f vagrant_utils_command_exists
export -f vagrant_utils_verify_commands
export -f vagrant_utils_service_is_running
export -f vagrant_utils_wait_for_service
export -f vagrant_utils_check_connectivity