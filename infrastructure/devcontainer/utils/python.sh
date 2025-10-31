#!/usr/bin/env bash
# =============================================================================
# IACT DevContainer - Python Utilities
# =============================================================================
# Description: Python, pip, and Django utilities for DevContainer environment
# Author: IACT Team
# Version: 1.0.0
# Context: DevContainer-specific Python operations
# =============================================================================

# Prevenir ejecucion directa
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    echo "Error: Este script debe ser 'sourced', no ejecutado directamente"
    exit 1
fi

# =============================================================================
# PYTHON BASICS
# =============================================================================

# -----------------------------------------------------------------------------
# iact_python_get_command
# Description: Get the correct Python command (python3 or python)
# Returns: Python command via stdout
# -----------------------------------------------------------------------------
iact_python_get_command() {
    if command -v python3 >/dev/null 2>&1; then
        echo "python3"
    elif command -v python >/dev/null 2>&1; then
        echo "python"
    else
        echo ""
    fi
}

# -----------------------------------------------------------------------------
# iact_python_get_version
# Description: Get Python version
# Returns: Version string (e.g., "3.11.5") via stdout, or empty if not installed
# -----------------------------------------------------------------------------
iact_python_get_version() {
    local python_cmd
    python_cmd=$(iact_python_get_command)

    if [[ -z "$python_cmd" ]]; then
        return 1
    fi

    $python_cmd --version 2>&1 | awk '{print $2}'
}

# -----------------------------------------------------------------------------
# iact_python_get_version_short
# Description: Get Python version in short format (major.minor)
# Returns: Version string (e.g., "3.11") via stdout
# -----------------------------------------------------------------------------
iact_python_get_version_short() {
    local version
    version=$(iact_python_get_version)

    if [[ -z "$version" ]]; then
        return 1
    fi

    echo "$version" | cut -d. -f1,2
}

# =============================================================================
# PIP UTILITIES
# =============================================================================

# -----------------------------------------------------------------------------
# iact_pip_get_command
# Description: Get the correct pip command (pip3 or pip)
# Returns: Pip command via stdout
# -----------------------------------------------------------------------------
iact_pip_get_command() {
    if command -v pip3 >/dev/null 2>&1; then
        echo "pip3"
    elif command -v pip >/dev/null 2>&1; then
        echo "pip"
    else
        echo ""
    fi
}

# -----------------------------------------------------------------------------
# iact_pip_install_package
# Description: Install a Python package using pip (idempotent)
# Arguments: $1 - package name (e.g., "django" or "django>=4.2")
# Returns: 0 on success, 1 on failure
# Note: Idempotent - skips if already installed with correct version
# -----------------------------------------------------------------------------
iact_pip_install_package() {
    local package="$1"

    if [[ -z "$package" ]]; then
        echo "Error: iact_pip_install_package requiere nombre de paquete" >&2
        return 1
    fi

    local pip_cmd
    pip_cmd=$(iact_pip_get_command)

    if [[ -z "$pip_cmd" ]]; then
        echo "Error: pip no está instalado" >&2
        return 1
    fi

    # Instalar/actualizar paquete
    if $pip_cmd install --upgrade "$package" 2>&1; then
        return 0
    else
        echo "Error: No se pudo instalar paquete: $package" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_pip_install_requirements
# Description: Install packages from requirements file (idempotent)
# Arguments: $1 - requirements file path
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
iact_pip_install_requirements() {
    local req_file="$1"

    if [[ -z "$req_file" ]]; then
        echo "Error: iact_pip_install_requirements requiere archivo de requirements" >&2
        return 1
    fi

    if [[ ! -f "$req_file" ]]; then
        echo "Error: Archivo de requirements no existe: $req_file" >&2
        return 1
    fi

    local pip_cmd
    pip_cmd=$(iact_pip_get_command)

    if [[ -z "$pip_cmd" ]]; then
        echo "Error: pip no está instalado" >&2
        return 1
    fi

    # Instalar desde requirements
    if $pip_cmd install -r "$req_file" 2>&1; then
        return 0
    else
        echo "Error: No se pudo instalar desde: $req_file" >&2
        return 1
    fi
}

# -----------------------------------------------------------------------------
# iact_pip_package_installed
# Description: Check if a Python package is installed
# Arguments: $1 - package name
# Returns: 0 if installed, 1 otherwise
# -----------------------------------------------------------------------------
iact_pip_package_installed() {
    local package="$1"

    if [[ -z "$package" ]]; then
        echo "Error: iact_pip_package_installed requiere nombre de paquete" >&2
        return 1
    fi

    local python_cmd
    python_cmd=$(iact_python_get_command)

    if [[ -z "$python_cmd" ]]; then
        echo "Error: Python no está instalado" >&2
        return 1
    fi

    # Intentar importar el paquete
    $python_cmd -c "import ${package}" 2>/dev/null
}

# -----------------------------------------------------------------------------
# iact_pip_freeze
# Description: Get list of installed packages
# Returns: List of packages via stdout
# -----------------------------------------------------------------------------
iact_pip_freeze() {
    local pip_cmd
    pip_cmd=$(iact_pip_get_command)

    if [[ -z "$pip_cmd" ]]; then
        echo "Error: pip no está instalado" >&2
        return 1
    fi

    $pip_cmd freeze 2>/dev/null
}

# -----------------------------------------------------------------------------
# iact_pip_list_outdated
# Description: Get list of outdated packages
# Returns: List of outdated packages via stdout
# -----------------------------------------------------------------------------
iact_pip_list_outdated() {
    local pip_cmd
    pip_cmd=$(iact_pip_get_command)

    if [[ -z "$pip_cmd" ]]; then
        echo "Error: pip no está instalado" >&2
        return 1
    fi

    $pip_cmd list --outdated 2>/dev/null
}

# =============================================================================
# DJANGO UTILITIES
# =============================================================================

# -----------------------------------------------------------------------------
# iact_django_get_version
# Description: Get Django version
# Returns: Version string (e.g., "4.2.5") via stdout, or empty if not installed
# -----------------------------------------------------------------------------
iact_django_get_version() {
    local python_cmd
    python_cmd=$(iact_python_get_command)

    if [[ -z "$python_cmd" ]]; then
        return 1
    fi

    $python_cmd -c "import django; print(django.get_version())" 2>/dev/null
}

# -----------------------------------------------------------------------------
# iact_django_get_version_short
# Description: Get Django version in short format (major.minor)
# Returns: Version string (e.g., "4.2") via stdout
# -----------------------------------------------------------------------------
iact_django_get_version_short() {
    local version
    version=$(iact_django_get_version)

    if [[ -z "$version" ]]; then
        return 1
    fi

    echo "$version" | cut -d. -f1,2
}

# -----------------------------------------------------------------------------
# iact_django_management_command
# Description: Run a Django management command
# Arguments: $1 - project directory (with manage.py), $2+ - command and args
# Returns: Exit code of the command
# Example: iact_django_management_command "/app" migrate --noinput
# -----------------------------------------------------------------------------
iact_django_management_command() {
    if [[ $# -lt 2 ]]; then
        echo "Error: iact_django_management_command requiere project_dir y comando" >&2
        return 1
    fi

    local project_dir="$1"
    shift
    local command=("$@")

    if [[ ! -d "$project_dir" ]]; then
        echo "Error: Directorio del proyecto no existe: $project_dir" >&2
        return 1
    fi

    if [[ ! -f "$project_dir/manage.py" ]]; then
        echo "Error: manage.py no encontrado en: $project_dir" >&2
        return 1
    fi

    local python_cmd
    python_cmd=$(iact_python_get_command)

    if [[ -z "$python_cmd" ]]; then
        echo "Error: Python no está instalado" >&2
        return 1
    fi

    # Ejecutar comando desde el directorio del proyecto
    (cd "$project_dir" && $python_cmd manage.py "${command[@]}")
}

# -----------------------------------------------------------------------------
# iact_django_migrate
# Description: Run Django migrations (idempotent)
# Arguments: $1 - project directory, $2 - database alias (optional)
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
iact_django_migrate() {
    local project_dir="$1"
    local database="${2:-default}"

    if [[ -z "$project_dir" ]]; then
        echo "Error: iact_django_migrate requiere project directory" >&2
        return 1
    fi

    if [[ "$database" == "default" ]]; then
        iact_django_management_command "$project_dir" migrate --noinput
    else
        iact_django_management_command "$project_dir" migrate --database="$database" --noinput
    fi
}

# -----------------------------------------------------------------------------
# iact_django_collectstatic
# Description: Collect static files (idempotent)
# Arguments: $1 - project directory
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
iact_django_collectstatic() {
    local project_dir="$1"

    if [[ -z "$project_dir" ]]; then
        echo "Error: iact_django_collectstatic requiere project directory" >&2
        return 1
    fi

    iact_django_management_command "$project_dir" collectstatic --noinput --clear
}

# -----------------------------------------------------------------------------
# iact_django_check
# Description: Run Django system check
# Arguments: $1 - project directory
# Returns: 0 if all checks pass, 1 otherwise
# -----------------------------------------------------------------------------
iact_django_check() {
    local project_dir="$1"

    if [[ -z "$project_dir" ]]; then
        echo "Error: iact_django_check requiere project directory" >&2
        return 1
    fi

    iact_django_management_command "$project_dir" check
}

# -----------------------------------------------------------------------------
# iact_django_showmigrations
# Description: Show migration status
# Arguments: $1 - project directory, $2 - database alias (optional)
# Returns: 0 on success, 1 on failure
# -----------------------------------------------------------------------------
iact_django_showmigrations() {
    local project_dir="$1"
    local database="${2:-default}"

    if [[ -z "$project_dir" ]]; then
        echo "Error: iact_django_showmigrations requiere project directory" >&2
        return 1
    fi

    if [[ "$database" == "default" ]]; then
        iact_django_management_command "$project_dir" showmigrations
    else
        iact_django_management_command "$project_dir" showmigrations --database="$database"
    fi
}

# -----------------------------------------------------------------------------
# iact_django_has_pending_migrations
# Description: Check if there are pending migrations
# Arguments: $1 - project directory, $2 - database alias (optional)
# Returns: 0 if has pending migrations, 1 if all applied
# -----------------------------------------------------------------------------
iact_django_has_pending_migrations() {
    local project_dir="$1"
    local database="${2:-default}"

    if [[ -z "$project_dir" ]]; then
        echo "Error: iact_django_has_pending_migrations requiere project directory" >&2
        return 1
    fi

    local output
    if [[ "$database" == "default" ]]; then
        output=$(iact_django_management_command "$project_dir" showmigrations 2>&1)
    else
        output=$(iact_django_management_command "$project_dir" showmigrations --database="$database" 2>&1)
    fi

    # Buscar migraciones sin aplicar (líneas con [ ] en lugar de [X])
    if echo "$output" | grep -q "^\s*\[ \]"; then
        return 0  # Hay migraciones pendientes
    else
        return 1  # Todas las migraciones aplicadas
    fi
}

# -----------------------------------------------------------------------------
# iact_django_createsuperuser_noninteractive
# Description: Create Django superuser non-interactively (idempotent)
# Arguments: $1 - project directory, $2 - username, $3 - email, $4 - password
# Returns: 0 on success, 1 on failure
# Note: Skips if user already exists
# -----------------------------------------------------------------------------
iact_django_createsuperuser_noninteractive() {
    local project_dir="$1"
    local username="$2"
    local email="$3"
    local password="$4"

    if [[ -z "$project_dir" ]] || [[ -z "$username" ]] || [[ -z "$email" ]] || [[ -z "$password" ]]; then
        echo "Error: iact_django_createsuperuser_noninteractive requiere todos los parámetros" >&2
        return 1
    fi

    local python_cmd
    python_cmd=$(iact_python_get_command)

    if [[ -z "$python_cmd" ]]; then
        echo "Error: Python no está instalado" >&2
        return 1
    fi

    # Script Python para crear superuser idempotente
    local python_script="
import os
import django
os.chdir('$project_dir')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$username').exists():
    User.objects.create_superuser('$username', '$email', '$password')
    print('Superuser created: $username')
else:
    print('Superuser already exists: $username')
"

    $python_cmd -c "$python_script" 2>&1
}

# -----------------------------------------------------------------------------
# iact_django_wait_for_db
# Description: Wait for Django to be able to connect to database
# Arguments: $1 - project directory, $2 - max wait seconds (default: 60)
# Returns: 0 if database ready, 1 on timeout
# -----------------------------------------------------------------------------
iact_django_wait_for_db() {
    local project_dir="$1"
    local max_wait="${2:-60}"
    local counter=0

    if [[ -z "$project_dir" ]]; then
        echo "Error: iact_django_wait_for_db requiere project directory" >&2
        return 1
    fi

    # Validar que max_wait es un número
    if ! [[ "$max_wait" =~ ^[0-9]+$ ]]; then
        echo "Error: max_wait debe ser un número: $max_wait" >&2
        return 1
    fi

    while [[ $counter -lt $max_wait ]]; do
        # Intentar Django check que incluye conexión a DB
        if iact_django_management_command "$project_dir" check --database default >/dev/null 2>&1; then
            return 0
        fi

        sleep 1
        ((counter++))
    done

    echo "Error: Django no pudo conectar a base de datos en ${max_wait}s" >&2
    return 1
}

# =============================================================================
# VIRTUAL ENVIRONMENT UTILITIES (opcional)
# =============================================================================

# -----------------------------------------------------------------------------
# iact_venv_exists
# Description: Check if a virtual environment exists
# Arguments: $1 - venv directory
# Returns: 0 if exists, 1 otherwise
# -----------------------------------------------------------------------------
iact_venv_exists() {
    local venv_dir="$1"

    if [[ -z "$venv_dir" ]]; then
        echo "Error: iact_venv_exists requiere directorio de venv" >&2
        return 1
    fi

    [[ -d "$venv_dir" ]] && [[ -f "$venv_dir/bin/activate" ]]
}

# -----------------------------------------------------------------------------
# iact_venv_is_active
# Description: Check if a virtual environment is currently active
# Returns: 0 if active, 1 otherwise
# -----------------------------------------------------------------------------
iact_venv_is_active() {
    [[ -n "${VIRTUAL_ENV:-}" ]]
}

# =============================================================================
# EXPORT
# =============================================================================

export -f iact_python_get_command
export -f iact_python_get_version
export -f iact_python_get_version_short
export -f iact_pip_get_command
export -f iact_pip_install_package
export -f iact_pip_install_requirements
export -f iact_pip_package_installed
export -f iact_pip_freeze
export -f iact_pip_list_outdated
export -f iact_django_get_version
export -f iact_django_get_version_short
export -f iact_django_management_command
export -f iact_django_migrate
export -f iact_django_collectstatic
export -f iact_django_check
export -f iact_django_showmigrations
export -f iact_django_has_pending_migrations
export -f iact_django_createsuperuser_noninteractive
export -f iact_django_wait_for_db
export -f iact_venv_exists
export -f iact_venv_is_active