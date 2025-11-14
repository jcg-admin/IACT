#!/usr/bin/env bash
# =============================================================================
# IACT DevContainer - Core Utilities
# =============================================================================
# Description: Core utilities for DevContainer environment
# Author: IACT Team
# Version: 1.0.0
# Context: DevContainer-specific utilities
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

# Detectar si estamos en DevContainer
readonly IACT_IN_DEVCONTAINER="${REMOTE_CONTAINERS:-false}"
readonly IACT_HOSTNAME="${HOSTNAME:-unknown}"

# Directorio de utilidades de DevContainer
readonly IACT_UTILS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Auto-cargar logging si existe
if [[ -f "${IACT_UTILS_DIR}/logging.sh" ]]; then
    source "${IACT_UTILS_DIR}/logging.sh"
fi

# =============================================================================
# CONTEXT DETECTION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_get_context
# Description: Get execution context (codespaces, local, or remote)
# Returns: String with context
# -----------------------------------------------------------------------------
iact_get_context() {
    if [[ -n "${CODESPACES:-}" ]]; then
        echo "codespaces"
    elif [[ -n "${REMOTE_CONTAINERS:-}" ]]; then
        echo "vscode-remote"
    else
        echo "local"
    fi
}

# -----------------------------------------------------------------------------
# iact_is_codespaces
# Description: Check if running in GitHub Codespaces
# Returns: 0 if in Codespaces, 1 otherwise
# -----------------------------------------------------------------------------
iact_is_codespaces() {
    [[ "$(iact_get_context)" == "codespaces" ]]
}

# -----------------------------------------------------------------------------
# iact_is_devcontainer
# Description: Check if running in DevContainer environment
# Returns: 0 if in DevContainer, 1 otherwise
# -----------------------------------------------------------------------------
iact_is_devcontainer() {
    [[ -n "${REMOTE_CONTAINERS:-}" ]] || [[ -n "${CODESPACES:-}" ]]
}

# -----------------------------------------------------------------------------
# iact_get_project_root
# Description: Get project root directory
# Returns: String with absolute path to project root
# -----------------------------------------------------------------------------
iact_get_project_root() {
    # En DevContainer, buscar el workspace
    if [[ -n "${WORKSPACE_FOLDER:-}" ]]; then
        echo "$WORKSPACE_FOLDER"
    elif [[ -d "/workspaces" ]]; then
        # Buscar primer directorio en /workspaces
        local workspace
        workspace=$(find /workspaces -maxdepth 1 -type d ! -path /workspaces | head -n 1)
        if [[ -n "$workspace" ]]; then
            echo "$workspace"
        else
            echo "/workspaces"
        fi
    else
        # Fallback: asumir que estamos 3 niveles abajo: infrastructure/devcontainer/utils
        echo "$(cd "${IACT_UTILS_DIR}/../../.." && pwd)"
    fi
}

# =============================================================================
# MODULE LOADING
# =============================================================================

# -----------------------------------------------------------------------------
# iact_source_module
# Description: Source a DevContainer utility module safely
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
# iact_check_python
# Description: Check if Python is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_check_python() {
    iact_command_exists "python3" || iact_command_exists "python"
}

# -----------------------------------------------------------------------------
# iact_check_pip
# Description: Check if pip is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_check_pip() {
    iact_command_exists "pip3" || iact_command_exists "pip"
}

# -----------------------------------------------------------------------------
# iact_check_django
# Description: Check if Django is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_check_django() {
    python3 -c "import django" 2>/dev/null
}

# -----------------------------------------------------------------------------
# iact_check_postgres_client
# Description: Check if PostgreSQL client is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_check_postgres_client() {
    iact_command_exists "psql"
}

# -----------------------------------------------------------------------------
# iact_check_mariadb_client
# Description: Check if MariaDB/MySQL client is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_check_mariadb_client() {
    iact_command_exists "mysql"
}

# =============================================================================
# FILE OPERATIONS
# =============================================================================

# -----------------------------------------------------------------------------
# iact_backup_file
# Description: Create a backup of a file with timestamp (idempotent)
# Arguments: $1 - file path
# Returns: 0 on success, 1 on failure
# Note: Only creates backup if content differs from last backup
# -----------------------------------------------------------------------------
iact_backup_file() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        echo "Error: Archivo '$file' no existe" >&2
        return 1
    fi

    # Buscar ultimo backup existente
    local last_backup
    last_backup=$(find "$(dirname "$file")" -maxdepth 1 -name "$(basename "$file").backup.*" 2>/dev/null | sort -r | head -n 1)

    # Si existe backup y es identico, no crear otro
    if [[ -n "$last_backup" ]] && cmp -s "$file" "$last_backup"; then
        echo "Backup existente es identico, no se crea nuevo backup"
        return 0
    fi

    # Crear nuevo backup solo si contenido difiere
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
# Description: Safely copy file, only if content differs (idempotent)
# Arguments: $1 - source, $2 - destination
# Returns: 0 on success, 1 on failure
# Note: Skips copy if destination exists and is identical to source
# -----------------------------------------------------------------------------
iact_safe_copy() {
    local src="$1"
    local dst="$2"

    if [[ ! -f "$src" ]]; then
        echo "Error: Archivo fuente '$src' no existe" >&2
        return 1
    fi

    # Si destino existe y es identico, no hacer nada (idempotencia)
    if [[ -f "$dst" ]] && cmp -s "$src" "$dst"; then
        echo "Destino ya existe y es identico, no se copia: $dst"
        return 0
    fi

    # Backup if destination exists and differs
    if [[ -f "$dst" ]]; then
        if ! iact_backup_file "$dst"; then
            echo "Error: No se pudo crear backup antes de copiar" >&2
            return 1
        fi
    fi

    # Create destination directory if needed
    local dst_dir
    dst_dir=$(dirname "$dst")
    if ! mkdir -p "$dst_dir"; then
        echo "Error: No se pudo crear directorio '$dst_dir'" >&2
        return 1
    fi

    # Copy file
    if cp "$src" "$dst"; then
        echo "Archivo copiado: $src -> $dst"
        return 0
    else
        echo "Error: No se pudo copiar '$src' a '$dst'" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_file_exists
# Description: Check if a file exists
# Arguments: $1 - file path
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
iact_file_exists() {
    [[ -f "$1" ]]
}

# -----------------------------------------------------------------------------
# iact_dir_exists
# Description: Check if a directory exists
# Arguments: $1 - directory path
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
iact_dir_exists() {
    [[ -d "$1" ]]
}

# -----------------------------------------------------------------------------
# iact_create_dir
# Description: Create directory if it doesn't exist
# Arguments: $1 - directory path
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
iact_create_dir() {
    local dir="$1"

    if [[ -d "$dir" ]]; then
        return 0
    fi

    if mkdir -p "$dir"; then
        return 0
    else
        echo "Error: No se pudo crear directorio '$dir'" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_verify_file_integrity
# Description: Verify that a file exists and is not empty or corrupted
# Arguments: $1 - file path, $2 - optional: expected keyword to search
# Returns: 0 if valid, 1 if missing/empty/corrupted
# -----------------------------------------------------------------------------
iact_verify_file_integrity() {
    local file="$1"
    local expected_keyword="${2:-}"

    # File must exist
    if [[ ! -f "$file" ]]; then
        echo "Error: Archivo no existe: $file" >&2
        return 1
    fi

    # File must not be empty
    if [[ ! -s "$file" ]]; then
        echo "Error: Archivo esta vacio: $file" >&2
        return 1
    fi

    # If keyword provided, verify it exists in file
    if [[ -n "$expected_keyword" ]]; then
        if ! grep -q "$expected_keyword" "$file" 2>/dev/null; then
            echo "Error: Archivo no contiene '${expected_keyword}': $file" >&2
            return 1
        fi
    fi

    return 0
}

# -----------------------------------------------------------------------------
# iact_verify_script_executable
# Description: Verify script exists and is executable, fix if needed
# Arguments: $1 - script path
# Returns: 0 on success, 1 on failure
# Note: Auto-repairs permissions if script exists but is not executable
# -----------------------------------------------------------------------------
iact_verify_script_executable() {
    local script="$1"

    # Must exist
    if [[ ! -f "$script" ]]; then
        echo "Error: Script no existe: $script" >&2
        return 1
    fi

    # Must not be empty
    if [[ ! -s "$script" ]]; then
        echo "Error: Script esta vacio: $script" >&2
        return 1
    fi

    # Auto-repair: Make executable if not already
    if [[ ! -x "$script" ]]; then
        echo "Warning: Script no es ejecutable, reparando permisos: $script" >&2
        if chmod +x "$script"; then
            echo "Permisos reparados exitosamente: $script"
            return 0
        else
            echo "Error: No se pudo reparar permisos: $script" >&2
            return 1
        fi
    fi

    return 0
}

# =============================================================================
# SERVICE MANAGEMENT (Docker/Container context)
# =============================================================================

# -----------------------------------------------------------------------------
# iact_service_is_running
# Description: Check if a systemd service is running
# Arguments: $1 - service name
# Returns: 0 if running, 1 otherwise
# -----------------------------------------------------------------------------
iact_service_is_running() {
    local service="$1"
    systemctl is-active --quiet "$service" 2>/dev/null
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
        if nc -z "$host" "$port" 2>/dev/null || timeout 1 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
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
# DEVCONTAINER-SPECIFIC UTILITIES
# =============================================================================

# -----------------------------------------------------------------------------
# iact_get_django_project_dir
# Description: Get Django project directory
# Returns: String with path to Django project
# -----------------------------------------------------------------------------
iact_get_django_project_dir() {
    local project_root
    project_root=$(iact_get_project_root)

    # Buscar manage.py
    if [[ -f "${project_root}/api/callcentersite/manage.py" ]]; then
        echo "${project_root}/api/callcentersite"
    else
        echo ""
    fi
}

# -----------------------------------------------------------------------------
# iact_get_requirements_dir
# Description: Get requirements directory
# Returns: String with path to requirements directory
# -----------------------------------------------------------------------------
iact_get_requirements_dir() {
    local django_dir
    django_dir=$(iact_get_django_project_dir)

    if [[ -n "$django_dir" ]] && [[ -d "${django_dir}/requirements" ]]; then
        echo "${django_dir}/requirements"
    else
        echo ""
    fi
}

# =============================================================================
# INITIALIZATION
# =============================================================================

# Declare global array for loaded modules
declare -gA IACT_LOADED_MODULES
IACT_LOADED_MODULES["core"]=1

# Export main functions
export -f iact_get_context
export -f iact_is_codespaces
export -f iact_is_devcontainer
export -f iact_get_project_root
export -f iact_source_module
export -f iact_get_os_info
export -f iact_get_memory_info
export -f iact_get_disk_info
export -f iact_command_exists
export -f iact_check_command_exists
export -f iact_verify_commands
export -f iact_check_python
export -f iact_check_pip
export -f iact_check_django
export -f iact_check_postgres_client
export -f iact_check_mariadb_client
export -f iact_backup_file
export -f iact_safe_copy
export -f iact_file_exists
export -f iact_dir_exists
export -f iact_create_dir
export -f iact_verify_file_integrity
export -f iact_verify_script_executable
export -f iact_service_is_running
export -f iact_wait_for_service
export -f iact_check_connectivity
export -f iact_wait_for_port
export -f iact_trim
export -f iact_to_lower
export -f iact_to_upper
export -f iact_get_django_project_dir
export -f iact_get_requirements_dir