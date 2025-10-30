#!/usr/bin/env bash
# =============================================================================
# IACT Vagrant - Core Utilities
# =============================================================================
# Description: Core utilities for Vagrant environment
# Author: IACT Team
# Version: 2.0.0
# Context: Vagrant-specific utilities
# =============================================================================

# Prevenir ejecucion directa
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: Este script debe ser 'sourced', no ejecutado directamente"
    echo "Uso: source ${BASH_SOURCE[0]}"
    exit 1
fi

# =============================================================================
# VARIABLES GLOBALES
# =============================================================================

# Detectar si estamos en Vagrant
readonly IACT_IN_VAGRANT="${VAGRANT:-false}"
readonly IACT_HOSTNAME="${HOSTNAME:-unknown}"

# Directorio de utilidades de Vagrant
if [[ -d "/vagrant" ]]; then
    readonly IACT_UTILS_DIR="/vagrant/infrastructure/vagrant/utils"
else
    readonly IACT_UTILS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

# Auto-cargar logging si existe
if [[ -f "${IACT_UTILS_DIR}/logging.sh" ]]; then
    source "${IACT_UTILS_DIR}/logging.sh"
fi

# =============================================================================
# CONTEXT DETECTION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_get_context
# Description: Get execution context (vagrant or local)
# Returns: String with context
# -----------------------------------------------------------------------------
iact_get_context() {
    if [[ -d "/vagrant" ]] || [[ "$IACT_IN_VAGRANT" == "true" ]]; then
        echo "vagrant"
    else
        echo "local"
    fi
}

# -----------------------------------------------------------------------------
# iact_is_vagrant
# Description: Check if running in Vagrant environment
# Returns: 0 if in Vagrant, 1 otherwise
# -----------------------------------------------------------------------------
iact_is_vagrant() {
    [[ "$(iact_get_context)" == "vagrant" ]]
}

# -----------------------------------------------------------------------------
# iact_get_project_root
# Description: Get project root directory
# Returns: String with absolute path to project root
# -----------------------------------------------------------------------------
iact_get_project_root() {
    if iact_is_vagrant; then
        echo "/vagrant"
    else
        # Asumir que estamos 3 niveles abajo: infrastructure/vagrant/utils
        echo "$(cd "$(dirname "${IACT_UTILS_DIR}")/../.." && pwd)"
    fi
}

# =============================================================================
# MODULE LOADING
# =============================================================================

# -----------------------------------------------------------------------------
# iact_source_module
# Description: Source a Vagrant utility module safely
# Arguments: $1 - module name (without .sh extension)
# Returns: 0 on success, 1 on failure
# Example: iact_source_module "validation"
# -----------------------------------------------------------------------------
iact_source_module() {
    local module_name="$1"
    local module_path="${IACT_UTILS_DIR}/${module_name}.sh"

    if [[ ! -f "$module_path" ]]; then
        echo "Error: Modulo '$module_name' no encontrado en: $module_path" >&2
        return 1
    fi

    if [[ "${IACT_LOADED_MODULES[$module_name]:-}" == "1" ]]; then
        return 0
    fi

    source "$module_path"
    declare -gA IACT_LOADED_MODULES
    IACT_LOADED_MODULES[$module_name]=1
    return 0
}

# =============================================================================
# SYSTEM INFORMATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_get_os_info
# Description: Get OS information
# Returns: String with OS name and version
# -----------------------------------------------------------------------------
iact_get_os_info() {
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        echo "${NAME} ${VERSION_ID}"
    else
        uname -s
    fi
}

# -----------------------------------------------------------------------------
# iact_get_memory_info
# Description: Get memory information in GB
# Returns: String with total memory
# -----------------------------------------------------------------------------
iact_get_memory_info() {
    local mem_kb
    mem_kb=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    local mem_gb=$((mem_kb / 1024 / 1024))
    echo "${mem_gb}GB"
}

# -----------------------------------------------------------------------------
# iact_get_disk_info
# Description: Get disk space information for root partition
# Returns: String with available/total space
# -----------------------------------------------------------------------------
iact_get_disk_info() {
    df -h / | awk 'NR==2 {print $4 " / " $2}'
}

# =============================================================================
# COMMAND VERIFICATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_command_exists
# Description: Check if a command exists
# Arguments: $1 - command name
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
iact_command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# -----------------------------------------------------------------------------
# iact_check_command_exists
# Description: Alias for iact_command_exists (backward compatibility)
# Arguments: $1 - command name
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
iact_check_command_exists() {
    iact_command_exists "$1"
}

# -----------------------------------------------------------------------------
# iact_verify_commands
# Description: Verify that required commands exist
# Arguments: $@ - list of command names
# Returns: 0 if all exist, 1 if any missing
# -----------------------------------------------------------------------------
iact_verify_commands() {
    local missing_commands=()

    for cmd in "$@"; do
        if ! iact_command_exists "$cmd"; then
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
# DATABASE CLIENT CHECKS
# =============================================================================

# -----------------------------------------------------------------------------
# iact_check_mariadb_client
# Description: Check if MariaDB/MySQL client is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_check_mariadb_client() {
    iact_command_exists "mysql"
}

# -----------------------------------------------------------------------------
# iact_check_mariadb_connect
# Description: Check if can connect to MariaDB (without password)
# Returns: 0 if can connect, 1 otherwise
# -----------------------------------------------------------------------------
iact_check_mariadb_connect() {
    mysql -e "SELECT 1;" >/dev/null 2>&1
}

# -----------------------------------------------------------------------------
# iact_check_postgres_client
# Description: Check if PostgreSQL client is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_check_postgres_client() {
    iact_command_exists "psql"
}

# =============================================================================
# FILE OPERATIONS
# =============================================================================

# -----------------------------------------------------------------------------
# iact_backup_file
# Description: Create a backup of a file with timestamp
# Arguments: $1 - file path
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
iact_backup_file() {
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
# iact_safe_copy
# Description: Safely copy file, creating backup if destination exists
# Arguments: $1 - source, $2 - destination
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
iact_safe_copy() {
    local src="$1"
    local dst="$2"

    if [[ ! -f "$src" ]]; then
        echo "Error: Archivo fuente '$src' no existe" >&2
        return 1
    fi

    # Backup if destination exists
    if [[ -f "$dst" ]]; then
        iact_backup_file "$dst" || return 1
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
# iact_service_is_running
# Description: Check if a systemd service is running
# Arguments: $1 - service name
# Returns: 0 if running, 1 otherwise
# -----------------------------------------------------------------------------
iact_service_is_running() {
    local service="$1"
    systemctl is-active --quiet "$service"
}

# -----------------------------------------------------------------------------
# iact_wait_for_service
# Description: Wait for a service to be running
# Arguments: $1 - service name, $2 - max wait time in seconds (default: 30)
# Returns: 0 if service started, 1 on timeout
# -----------------------------------------------------------------------------
iact_wait_for_service() {
    local service="$1"
    local max_wait="${2:-30}"
    local counter=0

    while [[ $counter -lt $max_wait ]]; do
        if iact_service_is_running "$service"; then
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
# iact_check_connectivity
# Description: Check internet connectivity
# Arguments: $1 - host to ping (default: 8.8.8.8)
# Returns: 0 if connected, 1 otherwise
# -----------------------------------------------------------------------------
iact_check_connectivity() {
    local host="${1:-8.8.8.8}"
    ping -c 1 -W 2 "$host" >/dev/null 2>&1
}

# -----------------------------------------------------------------------------
# iact_wait_for_port
# Description: Wait for a port to be available
# Arguments: $1 - host, $2 - port, $3 - max wait time (default: 30)
# Returns: 0 if port is available, 1 on timeout
# -----------------------------------------------------------------------------
iact_wait_for_port() {
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
# iact_trim
# Description: Trim whitespace from string
# Arguments: $1 - string to trim
# Returns: Trimmed string via stdout
# -----------------------------------------------------------------------------
iact_trim() {
    local str="$1"
    # Remove leading whitespace
    str="${str#"${str%%[![:space:]]*}"}"
    # Remove trailing whitespace
    str="${str%"${str##*[![:space:]]}"}"
    echo "$str"
}

# -----------------------------------------------------------------------------
# iact_to_lower
# Description: Convert string to lowercase
# Arguments: $1 - string
# Returns: Lowercase string via stdout
# -----------------------------------------------------------------------------
iact_to_lower() {
    echo "$1" | tr '[:upper:]' '[:lower:]'
}

# -----------------------------------------------------------------------------
# iact_to_upper
# Description: Convert string to uppercase
# Arguments: $1 - string
# Returns: Uppercase string via stdout
# -----------------------------------------------------------------------------
iact_to_upper() {
    echo "$1" | tr '[:lower:]' '[:upper:]'
}

# =============================================================================
# INITIALIZATION
# =============================================================================

# Declare global array for loaded modules
declare -gA IACT_LOADED_MODULES
IACT_LOADED_MODULES["core"]=1

# Export main functions
export -f iact_get_context
export -f iact_is_vagrant
export -f iact_get_project_root
export -f iact_source_module
export -f iact_command_exists
export -f iact_check_command_exists
export -f iact_verify_commands
export -f iact_check_mariadb_client
export -f iact_check_mariadb_connect
export -f iact_check_postgres_client
export -f iact_service_is_running
export -f iact_wait_for_service
export -f iact_check_connectivity