#!/usr/bin/env bash
# =============================================================================
# IACT DevContainer - Validation Utilities
# =============================================================================
# Description: Validation utilities for DevContainer environment
# Author: IACT Team
# Version: 1.0.0
# Context: DevContainer-specific validation
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

    # Validar que required_gb es un número
    if ! [[ "$required_gb" =~ ^[0-9]+$ ]]; then
        echo "Error: Espacio requerido debe ser un número: $required_gb" >&2
        return 1
    fi

    local available_kb
    available_kb=$(df / | awk 'NR==2 {print $4}')

    if [[ -z "$available_kb" ]]; then
        echo "Error: No se pudo obtener espacio disponible en disco" >&2
        return 1
    fi

    local available_gb=$((available_kb / 1024 / 1024))

    if [[ $available_gb -lt $required_gb ]]; then
        echo "Error: Espacio insuficiente. Requerido: ${required_gb}GB, Disponible: ${available_gb}GB" >&2
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
    local hosts=("8.8.8.8" "1.1.1.1" "1.0.0.1")
    local timeout=2
    local attempts=0

    for host in "${hosts[@]}"; do
        if ping -c 1 -W "$timeout" "$host" >/dev/null 2>&1; then
            return 0
        fi
        ((attempts++))
    done

    echo "Error: Sin conectividad a internet (probados ${attempts} hosts)" >&2
    return 1
}

# -----------------------------------------------------------------------------
# iact_validate_host_reachable
# Description: Validate that a specific host is reachable
# Arguments: $1 - hostname or IP
# Returns: 0 if reachable, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_host_reachable() {
    local host="$1"

    if [[ -z "$host" ]]; then
        echo "Error: iact_validate_host_reachable requiere hostname" >&2
        return 1
    fi

    if ping -c 1 -W 2 "$host" >/dev/null 2>&1; then
        return 0
    else
        echo "Error: Host no alcanzable: $host" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_validate_port_available
# Description: Validate that a port is listening
# Arguments: $1 - host, $2 - port
# Returns: 0 if port is available, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_port_available() {
    local host="$1"
    local port="$2"

    if [[ -z "$host" ]] || [[ -z "$port" ]]; then
        echo "Error: iact_validate_port_available requiere host y port" >&2
        return 1
    fi

    # Validar que port es un número
    if ! [[ "$port" =~ ^[0-9]+$ ]]; then
        echo "Error: Port debe ser un número: $port" >&2
        return 1
    fi

    # Intentar conexión con timeout
    if timeout 2 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; then
        return 0
    else
        echo "Error: Puerto no disponible: $host:$port" >&2
        return 1
    fi
}

# =============================================================================
# FILE AND DIRECTORY VALIDATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_validate_file_exists
# Description: Validate that a file exists
# Arguments: $1 - file path
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_file_exists() {
    local file="$1"

    if [[ -z "$file" ]]; then
        echo "Error: iact_validate_file_exists requiere file path" >&2
        return 1
    fi

    if [[ -f "$file" ]]; then
        return 0
    else
        echo "Error: Archivo no existe: $file" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_validate_file_not_empty
# Description: Validate that a file exists and is not empty
# Arguments: $1 - file path
# Returns: 0 if exists and not empty, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_file_not_empty() {
    local file="$1"

    if [[ -z "$file" ]]; then
        echo "Error: iact_validate_file_not_empty requiere file path" >&2
        return 1
    fi

    if [[ ! -f "$file" ]]; then
        echo "Error: Archivo no existe: $file" >&2
        return 1
    fi

    if [[ ! -s "$file" ]]; then
        echo "Error: Archivo está vacío: $file" >&2
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# iact_validate_dir_exists
# Description: Validate that a directory exists
# Arguments: $1 - directory path
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_dir_exists() {
    local dir="$1"

    if [[ -z "$dir" ]]; then
        echo "Error: iact_validate_dir_exists requiere directory path" >&2
        return 1
    fi

    if [[ -d "$dir" ]]; then
        return 0
    else
        echo "Error: Directorio no existe: $dir" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_validate_dir_not_empty
# Description: Validate that a directory exists and is not empty
# Arguments: $1 - directory path
# Returns: 0 if exists and not empty, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_dir_not_empty() {
    local dir="$1"

    if [[ -z "$dir" ]]; then
        echo "Error: iact_validate_dir_not_empty requiere directory path" >&2
        return 1
    fi

    if [[ ! -d "$dir" ]]; then
        echo "Error: Directorio no existe: $dir" >&2
        return 1
    fi

    # Check si tiene contenido
    if [[ -z "$(ls -A "$dir" 2>/dev/null)" ]]; then
        echo "Error: Directorio está vacío: $dir" >&2
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# iact_validate_file_readable
# Description: Validate that a file exists and is readable
# Arguments: $1 - file path
# Returns: 0 if readable, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_file_readable() {
    local file="$1"

    if [[ -z "$file" ]]; then
        echo "Error: iact_validate_file_readable requiere file path" >&2
        return 1
    fi

    if [[ ! -f "$file" ]]; then
        echo "Error: Archivo no existe: $file" >&2
        return 1
    fi

    if [[ ! -r "$file" ]]; then
        echo "Error: Archivo no es legible: $file" >&2
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# iact_validate_file_writable
# Description: Validate that a file exists and is writable
# Arguments: $1 - file path
# Returns: 0 if writable, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_file_writable() {
    local file="$1"

    if [[ -z "$file" ]]; then
        echo "Error: iact_validate_file_writable requiere file path" >&2
        return 1
    fi

    if [[ ! -f "$file" ]]; then
        echo "Error: Archivo no existe: $file" >&2
        return 1
    fi

    if [[ ! -w "$file" ]]; then
        echo "Error: Archivo no es escribible: $file" >&2
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# iact_validate_file_executable
# Description: Validate that a file exists and is executable
# Arguments: $1 - file path
# Returns: 0 if executable, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_file_executable() {
    local file="$1"

    if [[ -z "$file" ]]; then
        echo "Error: iact_validate_file_executable requiere file path" >&2
        return 1
    fi

    if [[ ! -f "$file" ]]; then
        echo "Error: Archivo no existe: $file" >&2
        return 1
    fi

    if [[ ! -x "$file" ]]; then
        echo "Error: Archivo no es ejecutable: $file" >&2
        return 1
    fi

    return 0
}

# =============================================================================
# PYTHON VALIDATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_validate_python_installed
# Description: Validate that Python is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_python_installed() {
    if command -v python3 >/dev/null 2>&1; then
        return 0
    elif command -v python >/dev/null 2>&1; then
        return 0
    else
        echo "Error: Python no está instalado" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_validate_python_version
# Description: Validate Python version meets minimum requirement
# Arguments: $1 - minimum version (e.g., "3.11")
# Returns: 0 if meets requirement, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_python_version() {
    local min_version="$1"

    if [[ -z "$min_version" ]]; then
        echo "Error: iact_validate_python_version requiere versión mínima" >&2
        return 1
    fi

    if ! iact_validate_python_installed; then
        return 1
    fi

    # Obtener versión actual
    local current_version
    current_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)

    if [[ -z "$current_version" ]]; then
        echo "Error: No se pudo determinar versión de Python" >&2
        return 1
    fi

    # Comparar versiones (simple comparison for major.minor)
    local min_major min_minor current_major current_minor
    min_major=$(echo "$min_version" | cut -d. -f1)
    min_minor=$(echo "$min_version" | cut -d. -f2)
    current_major=$(echo "$current_version" | cut -d. -f1)
    current_minor=$(echo "$current_version" | cut -d. -f2)

    if [[ $current_major -lt $min_major ]] || \
       { [[ $current_major -eq $min_major ]] && [[ $current_minor -lt $min_minor ]]; }; then
        echo "Error: Python $min_version+ requerido, encontrado: $current_version" >&2
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# iact_validate_pip_installed
# Description: Validate that pip is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_pip_installed() {
    if command -v pip3 >/dev/null 2>&1; then
        return 0
    elif command -v pip >/dev/null 2>&1; then
        return 0
    else
        echo "Error: pip no está instalado" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_validate_python_package_installed
# Description: Validate that a Python package is installed
# Arguments: $1 - package name
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_python_package_installed() {
    local package="$1"

    if [[ -z "$package" ]]; then
        echo "Error: iact_validate_python_package_installed requiere nombre de paquete" >&2
        return 1
    fi

    if ! iact_validate_python_installed; then
        return 1
    fi

    if python3 -c "import ${package}" 2>/dev/null; then
        return 0
    else
        echo "Error: Paquete Python no instalado: $package" >&2
        return 1
    fi
}

# =============================================================================
# DJANGO VALIDATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_validate_django_installed
# Description: Validate that Django is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_django_installed() {
    if ! iact_validate_python_installed; then
        return 1
    fi

    if python3 -c "import django" 2>/dev/null; then
        return 0
    else
        echo "Error: Django no está instalado" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_validate_django_version
# Description: Validate Django version meets minimum requirement
# Arguments: $1 - minimum version (e.g., "4.2")
# Returns: 0 if meets requirement, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_django_version() {
    local min_version="$1"

    if [[ -z "$min_version" ]]; then
        echo "Error: iact_validate_django_version requiere versión mínima" >&2
        return 1
    fi

    if ! iact_validate_django_installed; then
        return 1
    fi

    # Obtener versión actual
    local current_version
    current_version=$(python3 -c "import django; print(django.get_version())" 2>/dev/null | cut -d. -f1,2)

    if [[ -z "$current_version" ]]; then
        echo "Error: No se pudo determinar versión de Django" >&2
        return 1
    fi

    # Comparar versiones
    local min_major min_minor current_major current_minor
    min_major=$(echo "$min_version" | cut -d. -f1)
    min_minor=$(echo "$min_version" | cut -d. -f2)
    current_major=$(echo "$current_version" | cut -d. -f1)
    current_minor=$(echo "$current_version" | cut -d. -f2)

    if [[ $current_major -lt $min_major ]] || \
       { [[ $current_major -eq $min_major ]] && [[ $current_minor -lt $min_minor ]]; }; then
        echo "Error: Django $min_version+ requerido, encontrado: $current_version" >&2
        return 1
    fi

    return 0
}

# -----------------------------------------------------------------------------
# iact_validate_django_project
# Description: Validate that a Django project exists (has manage.py)
# Arguments: $1 - project directory
# Returns: 0 if valid, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_django_project() {
    local project_dir="$1"

    if [[ -z "$project_dir" ]]; then
        echo "Error: iact_validate_django_project requiere directorio del proyecto" >&2
        return 1
    fi

    if [[ ! -d "$project_dir" ]]; then
        echo "Error: Directorio del proyecto no existe: $project_dir" >&2
        return 1
    fi

    if [[ ! -f "$project_dir/manage.py" ]]; then
        echo "Error: manage.py no encontrado en: $project_dir" >&2
        return 1
    fi

    return 0
}

# =============================================================================
# REQUIREMENTS VALIDATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_validate_requirements_file
# Description: Validate that a requirements file exists and is valid
# Arguments: $1 - requirements file path
# Returns: 0 if valid, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_requirements_file() {
    local req_file="$1"

    if [[ -z "$req_file" ]]; then
        echo "Error: iact_validate_requirements_file requiere archivo de requirements" >&2
        return 1
    fi

    if ! iact_validate_file_exists "$req_file"; then
        return 1
    fi

    if ! iact_validate_file_not_empty "$req_file"; then
        return 1
    fi

    # Validar formato básico (debe tener al menos una línea sin comentario)
    local has_packages
    has_packages=$(grep -v '^#' "$req_file" | grep -v '^$' | wc -l)

    if [[ $has_packages -eq 0 ]]; then
        echo "Error: Archivo de requirements no tiene paquetes: $req_file" >&2
        return 1
    fi

    return 0
}

# =============================================================================
# DATABASE CLIENT VALIDATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_validate_postgres_client
# Description: Validate that PostgreSQL client is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_postgres_client() {
    if command -v psql >/dev/null 2>&1; then
        return 0
    else
        echo "Error: Cliente PostgreSQL (psql) no está instalado" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_validate_mariadb_client
# Description: Validate that MariaDB/MySQL client is installed
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_mariadb_client() {
    if command -v mysql >/dev/null 2>&1; then
        return 0
    else
        echo "Error: Cliente MariaDB/MySQL (mysql) no está instalado" >&2
        return 1
    fi
}

# =============================================================================
# COMMAND VALIDATION
# =============================================================================

# -----------------------------------------------------------------------------
# iact_validate_command_exists
# Description: Validate that a command exists
# Arguments: $1 - command name
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
iact_validate_command_exists() {
    local cmd="$1"

    if [[ -z "$cmd" ]]; then
        echo "Error: iact_validate_command_exists requiere nombre de comando" >&2
        return 1
    fi

    if command -v "$cmd" >/dev/null 2>&1; then
        return 0
    else
        echo "Error: Comando no encontrado: $cmd" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_validate_commands_exist
# Description: Validate that multiple commands exist
# Arguments: $@ - list of command names
# Returns: 0 if all exist, 1 if any missing
# -----------------------------------------------------------------------------
iact_validate_commands_exist() {
    local missing_commands=()
    local all_valid=0

    if [[ $# -eq 0 ]]; then
        echo "Error: iact_validate_commands_exist requiere al menos un comando" >&2
        return 1
    fi

    for cmd in "$@"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_commands+=("$cmd")
            all_valid=1
        fi
    done

    if [[ ${#missing_commands[@]} -gt 0 ]]; then
        echo "Error: Comandos faltantes: ${missing_commands[*]}" >&2
        return 1
    fi

    return 0
}

# =============================================================================
# EXPORT
# =============================================================================

export -f iact_validate_disk_space
export -f iact_validate_internet
export -f iact_validate_host_reachable
export -f iact_validate_port_available
export -f iact_validate_file_exists
export -f iact_validate_file_not_empty
export -f iact_validate_dir_exists
export -f iact_validate_dir_not_empty
export -f iact_validate_file_readable
export -f iact_validate_file_writable
export -f iact_validate_file_executable
export -f iact_validate_python_installed
export -f iact_validate_python_version
export -f iact_validate_pip_installed
export -f iact_validate_python_package_installed
export -f iact_validate_django_installed
export -f iact_validate_django_version
export -f iact_validate_django_project
export -f iact_validate_requirements_file
export -f iact_validate_postgres_client
export -f iact_validate_mariadb_client
export -f iact_validate_command_exists
export -f iact_validate_commands_exist