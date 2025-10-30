#!/usr/bin/env bash
# infrastructure/utils/python.sh - PARTE 1 DE 2
# Python and Django verification functions for IACT Infrastructure
# Provides functions to verify Python, pip, Django installation and configuration
# Supports DevContainer, Vagrant, and traditional environments
#
# Version: 2.0.0
# Pattern: Idempotent execution, No silent failures
#
# INSTRUCCIONES: Este es la PARTE 1. Concatenar con PARTE 2 para archivo completo.

set -euo pipefail

# =============================================================================
# PYTHON VERIFICATION FUNCTIONS
# =============================================================================

# Check if Python 3 is available
# NO SILENT FAILURES: Reports result
#
# Usage: iact_check_python_available
#
# Returns:
#   0 - Python 3 is available
#   1 - Python 3 not found
iact_check_python_available() {
    if iact_check_command_exists "python3"; then
        iact_log_debug "Python 3 is available"
        return 0
    else
        iact_log_debug "Python 3 not found"
        return 1
    fi
}

# Get Python version
# NO SILENT FAILURES: Returns "unknown" on error
#
# Usage: version=$(iact_get_python_version)
#
# Returns:
#   Prints Python version to stdout (e.g., "3.11.5")
iact_get_python_version() {
    if ! iact_check_python_available; then
        echo "unknown"
        return 1
    fi

    python3 --version 2>&1 | awk '{print $2}'
}

# Check if Python version meets minimum requirement
# NO SILENT FAILURES: Reports exact version comparison
#
# Usage: iact_check_python_version "3.11"
# Usage: iact_check_python_version  # Uses default 3.11
#
# Args:
#   $1 - Minimum version (optional, default: 3.11)
#
# Returns:
#   0 - Version meets requirement
#   1 - Version does not meet requirement or Python not found
iact_check_python_version() {
    local min_version="${1:-3.11}"

    if ! iact_check_python_available; then
        iact_log_error "Python 3 not found - cannot check version"
        return 1
    fi

    local current_version
    current_version=$(iact_get_python_version)

    iact_log_debug "Python version: $current_version (minimum required: $min_version)"

    # Compare versions (simplified comparison for major.minor)
    local current_major current_minor
    current_major=$(echo "$current_version" | cut -d. -f1)
    current_minor=$(echo "$current_version" | cut -d. -f2)

    local required_major required_minor
    required_major=$(echo "$min_version" | cut -d. -f1)
    required_minor=$(echo "$min_version" | cut -d. -f2)

    if [[ $current_major -gt $required_major ]] || \
       [[ $current_major -eq $required_major && $current_minor -ge $required_minor ]]; then
        iact_log_debug "Python version check passed: $current_version >= $min_version"
        return 0
    else
        iact_log_error "Python version $current_version does not meet minimum $min_version"
        return 1
    fi
}

# =============================================================================
# PIP VERIFICATION FUNCTIONS
# =============================================================================

# Check if pip is installed
# NO SILENT FAILURES: Reports result
#
# Usage: iact_check_pip_installed
#
# Returns:
#   0 - pip is installed
#   1 - pip not found
iact_check_pip_installed() {
    if python3 -m pip --version >/dev/null 2>&1; then
        iact_log_debug "pip is installed"
        return 0
    else
        iact_log_debug "pip not found"
        return 1
    fi
}

# Get pip version
# NO SILENT FAILURES: Returns "unknown" on error
#
# Usage: version=$(iact_get_pip_version)
#
# Returns:
#   Prints pip version to stdout (e.g., "23.3.1")
iact_get_pip_version() {
    if ! iact_check_pip_installed; then
        echo "unknown"
        return 1
    fi

    python3 -m pip --version 2>&1 | awk '{print $2}'
}

# Check if a Python package is installed
# NO SILENT FAILURES: Reports package status and version details
#
# Usage: iact_check_python_package "django"
# Usage: iact_check_python_package "pytest" "7.0"
#
# Args:
#   $1 - Package name
#   $2 - Minimum version (optional)
#
# Returns:
#   0 - Package is installed (and meets version if specified)
#   1 - Package not installed or version too old
iact_check_python_package() {
    local package="$1"
    local min_version="${2:-}"

    if ! iact_check_pip_installed; then
        iact_log_error "pip not available - cannot check package"
        return 1
    fi

    # Check if package is installed
    if ! python3 -m pip show "$package" >/dev/null 2>&1; then
        iact_log_debug "Package not installed: $package"
        return 1
    fi

    # If no version requirement, we're done
    if [[ -z "$min_version" ]]; then
        iact_log_debug "Package installed: $package"
        return 0
    fi

    # Check version
    local installed_version
    installed_version=$(python3 -m pip show "$package" 2>/dev/null | grep "^Version:" | awk '{print $2}')

    iact_log_debug "Package $package version: $installed_version (minimum required: $min_version)"

    # Simple version comparison (works for major.minor)
    if python3 -c "from packaging import version; exit(0 if version.parse('$installed_version') >= version.parse('$min_version') else 1)" 2>/dev/null; then
        iact_log_debug "Package version check passed: $installed_version >= $min_version"
        return 0
    else
        iact_log_debug "Package version too old: $installed_version < $min_version"
        return 1
    fi
}

# Install or upgrade pip
# NO SILENT FAILURES: Reports upgrade result
#
# Usage: iact_upgrade_pip
#
# Returns:
#   0 - pip upgraded successfully
#   1 - pip upgrade failed
iact_upgrade_pip() {
    iact_log_info "Upgrading pip..."

    if python3 -m pip install --upgrade pip >/dev/null 2>&1; then
        local new_version
        new_version=$(iact_get_pip_version)
        iact_log_success "pip upgraded to version $new_version"
        return 0
    else
        iact_log_error "Failed to upgrade pip"
        return 1
    fi
}

# =============================================================================
# VIRTUAL ENVIRONMENT FUNCTIONS
# =============================================================================

# Check if running inside a virtual environment
# NO SILENT FAILURES: Reports venv status
#
# Usage: if iact_check_virtualenv_active; then ...; fi
#
# Returns:
#   0 - Running in virtual environment
#   1 - Not running in virtual environment
iact_check_virtualenv_active() {
    if [[ -n "${VIRTUAL_ENV:-}" ]]; then
        iact_log_debug "Virtual environment active: $VIRTUAL_ENV"
        return 0
    else
        iact_log_debug "No virtual environment active"
        return 1
    fi
}

# =============================================================================
# DJANGO VERIFICATION FUNCTIONS
# =============================================================================

# Check if Django is installed
# NO SILENT FAILURES: Reports Django status and version
#
# Usage: iact_check_django_installed
# Usage: iact_check_django_installed "4.2"
#
# Args:
#   $1 - Minimum version (optional, default: 4.2)
#
# Returns:
#   0 - Django is installed (and meets version if specified)
#   1 - Django not installed or version too old
iact_check_django_installed() {
    local min_version="${1:-4.2}"

    if iact_check_python_package "django" "$min_version"; then
        iact_log_debug "Django installed and meets version requirement: >= $min_version"
        return 0
    else
        iact_log_debug "Django not installed or version requirement not met: < $min_version"
        return 1
    fi
}

# Get Django version
# NO SILENT FAILURES: Returns "unknown" on error
#
# Usage: version=$(iact_get_django_version)
#
# Returns:
#   Prints Django version to stdout (e.g., "4.2.7")
iact_get_django_version() {
    if ! iact_check_python_package "django"; then
        echo "unknown"
        return 1
    fi

    python3 -c "import django; print(django.get_version())" 2>/dev/null
}

# Check Django settings module
# NO SILENT FAILURES: Reports settings validation result
#
# Usage: iact_check_django_settings
#
# Returns:
#   0 - DJANGO_SETTINGS_MODULE is set and valid
#   1 - DJANGO_SETTINGS_MODULE not set or invalid
iact_check_django_settings() {
    if [[ -z "${DJANGO_SETTINGS_MODULE:-}" ]]; then
        iact_log_error "DJANGO_SETTINGS_MODULE environment variable not set"
        return 1
    fi

    iact_log_debug "DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"

    # Try to import settings
    if python3 -c "import django; django.setup()" 2>/dev/null; then
        iact_log_debug "Django settings are valid"
        return 0
    else
        iact_log_error "Django settings are invalid or cannot be loaded"
        return 1
    fi
}

# Check if Django project directory exists
# NO SILENT FAILURES: Reports directory status
#
# Usage: iact_check_django_project_exists
# Usage: iact_check_django_project_exists "/custom/path"
#
# Args:
#   $1 - Project directory (optional, default: from DJANGO_PROJECT_DIR)
#
# Returns:
#   0 - Project directory exists and has manage.py
#   1 - Project directory does not exist or is invalid
iact_check_django_project_exists() {
    local project_dir="${1:-${DJANGO_PROJECT_DIR:-}}"

    if [[ -z "$project_dir" ]]; then
        iact_log_error "Django project directory not specified"
        return 1
    fi

    if [[ ! -d "$project_dir" ]]; then
        iact_log_error "Django project directory does not exist: $project_dir"
        return 1
    fi

    if [[ ! -f "$project_dir/manage.py" ]]; then
        iact_log_error "manage.py not found in: $project_dir"
        return 1
    fi

    iact_log_debug "Django project directory is valid: $project_dir"
    return 0
}

# Run Django management command
# NO SILENT FAILURES: Reports command execution result
#
# Usage: iact_django_manage "check"
# Usage: iact_django_manage "migrate" "--noinput"
#
# Args:
#   $@ - Django management command and arguments
#
# Returns:
#   Exit code of the Django command
iact_django_manage() {
    local project_dir="${DJANGO_PROJECT_DIR:-}"

    if [[ -z "$project_dir" ]]; then
        iact_log_error "DJANGO_PROJECT_DIR not set"
        return 1
    fi

    if ! iact_check_django_project_exists "$project_dir"; then
        iact_log_error "Django project not found at: $project_dir"
        return 1
    fi

    local cmd=("$@")
    iact_log_debug "Running Django command: python manage.py ${cmd[*]}"

    # Change to project directory and run command
    (
        cd "$project_dir" && \
        python3 manage.py "${cmd[@]}"
    )
}

# Run Django system check
# NO SILENT FAILURES: Reports check result with details
#
# Usage: iact_run_django_check
# Usage: iact_run_django_check "--deploy"
#
# Args:
#   $@ - Additional arguments for django-admin check (optional)
#
# Returns:
#   0 - Django check passed
#   1 - Django check failed
iact_run_django_check() {
    local extra_args=("$@")

    if ! iact_check_django_installed; then
        iact_log_error "Django not installed - cannot run check"
        return 1
    fi

    if ! iact_check_django_settings; then
        iact_log_error "Django settings not configured"
        return 1
    fi

    iact_log_info "Running Django system check..."

    if iact_django_manage check "${extra_args[@]}" 2>&1; then
        iact_log_success "Django system check passed"
        return 0
    else
        iact_log_error "Django system check failed"
        return 1
    fi
}

# Check if Django migrations are needed
# NO SILENT FAILURES: Reports migration status
#
# Usage: if iact_check_django_migrations_needed; then ...; fi
#
# Returns:
#   0 - Migrations are needed
#   1 - No migrations needed or error
iact_check_django_migrations_needed() {
    if ! iact_check_django_installed; then
        iact_log_error "Django not installed"
        return 1
    fi

    if ! iact_check_django_settings; then
        iact_log_error "Django settings not configured"
        return 1
    fi

    # Check if there are unapplied migrations
    if iact_django_manage showmigrations --plan 2>/dev/null | grep -q "\[ \]"; then
        iact_log_debug "Unapplied migrations detected"
        return 0
    else
        iact_log_debug "No unapplied migrations"
        return 1
    fi
}

# Run Django migrations
# NO SILENT FAILURES: Reports migration result
#
# Usage: iact_run_django_migrations
# Usage: iact_run_django_migrations "app_name"
#
# Args:
#   $1 - App name (optional, runs all migrations if not specified)
#
# Returns:
#   0 - Migrations completed successfully
#   1 - Migrations failed
iact_run_django_migrations() {
    local app="${1:-}"

    if ! iact_check_django_installed; then
        iact_log_error "Django not installed"
        return 1
    fi

    if ! iact_check_django_settings; then
        iact_log_error "Django settings not configured"
        return 1
    fi

    iact_log_info "Running Django migrations..."

    if [[ -n "$app" ]]; then
        if iact_django_manage migrate "$app" 2>&1; then
            iact_log_success "Django migrations completed for $app"
            return 0
        else
            iact_log_error "Django migrations failed for $app"
            return 1
        fi
    else
        if iact_django_manage migrate 2>&1; then
            iact_log_success "Django migrations completed"
            return 0
        else
            iact_log_error "Django migrations failed"
            return 1
        fi
    fi
}

# Collect Django static files
# NO SILENT FAILURES: Reports collection result
#
# Usage: iact_collect_django_static
#
# Returns:
#   0 - Static files collected successfully
#   1 - Collection failed
iact_collect_django_static() {
    if ! iact_check_django_installed; then
        iact_log_error "Django not installed"
        return 1
    fi

    if ! iact_check_django_settings; then
        iact_log_error "Django settings not configured"
        return 1
    fi

    iact_log_info "Collecting Django static files..."

    if iact_django_manage collectstatic --noinput 2>&1; then
        iact_log_success "Static files collected"
        return 0
    else
        iact_log_error "Failed to collect static files"
        return 1
    fi
}

# =============================================================================
# REQUIREMENTS INSTALLATION FUNCTIONS
# =============================================================================

# Install requirements from file
# NO SILENT FAILURES: Reports file status and installation result
#
# Usage: iact_install_requirements "requirements.txt"
# Usage: iact_install_requirements "requirements/dev.txt"
#
# Args:
#   $1 - Requirements file path
#
# Returns:
#   0 - Requirements installed successfully
#   1 - Installation failed or file not found
iact_install_requirements() {
    local req_file="$1"

    if ! iact_check_pip_installed; then
        iact_log_error "pip not available - cannot install requirements"
        return 1
    fi

    if [[ ! -f "$req_file" ]]; then
        iact_log_error "Requirements file not found: $req_file"
        return 1
    fi

    iact_log_info "Installing requirements from $req_file..."

    if python3 -m pip install -r "$req_file" 2>&1; then
        iact_log_success "Requirements installed from $req_file"
        return 0
    else
        iact_log_error "Failed to install requirements from $req_file"
        return 1
    fi
}

# =============================================================================
# PYTEST FUNCTIONS
# =============================================================================

# Check if pytest is installed
# NO SILENT FAILURES: Reports pytest status
#
# Usage: iact_check_pytest_installed
#
# Returns:
#   0 - pytest is installed
#   1 - pytest not installed
iact_check_pytest_installed() {
    if iact_check_python_package "pytest"; then
        iact_log_debug "pytest is installed"
        return 0
    else
        iact_log_debug "pytest not installed"
        return 1
    fi
}

# Run pytest
# NO SILENT FAILURES: Reports test execution result
#
# Usage: iact_run_pytest
# Usage: iact_run_pytest "-v" "--cov"
#
# Args:
#   $@ - Additional pytest arguments (optional)
#
# Returns:
#   0 - Tests passed
#   1 - Tests failed or pytest not installed
iact_run_pytest() {
    local pytest_args=("$@")

    if ! iact_check_pytest_installed; then
        iact_log_error "pytest not installed"
        return 1
    fi

    iact_log_info "Running pytest..."

    if python3 -m pytest "${pytest_args[@]}" 2>&1; then
        iact_log_success "Tests passed"
        return 0
    else
        iact_log_error "Tests failed"
        return 1
    fi
}

# =============================================================================
# VALIDATION FUNCTIONS - IDEMPOTENT PATTERN
# =============================================================================

# Validate Python installation
_validate_python_step() {
    local step="$1"
    local total="$2"

    iact_log_step "$step" "$total" "Checking Python installation"

    if iact_check_python_version "3.11"; then
        local py_version
        py_version=$(iact_get_python_version)
        iact_log_success "Python version: $py_version"
        return 0
    else
        iact_log_error "Python version check failed (minimum: 3.11)"
        return 1
    fi
}

# Validate pip installation
_validate_pip_step() {
    local step="$1"
    local total="$2"

    iact_log_step "$step" "$total" "Checking pip installation"

    if iact_check_pip_installed; then
        local pip_version
        pip_version=$(iact_get_pip_version)
        iact_log_success "pip version: $pip_version"
        return 0
    else
        iact_log_error "pip not installed"
        return 1
    fi
}

# Validate Django installation
_validate_django_step() {
    local step="$1"
    local total="$2"

    iact_log_step "$step" "$total" "Checking Django installation"

    if iact_check_django_installed "4.2"; then
        local django_version
        django_version=$(iact_get_django_version)
        iact_log_success "Django version: $django_version"
        return 0
    else
        iact_log_error "Django not installed or version < 4.2"
        return 1
    fi
}

# Validate Django settings
_validate_django_settings_step() {
    local step="$1"
    local total="$2"

    iact_log_step "$step" "$total" "Checking Django settings"

    if iact_check_django_settings; then
        iact_log_success "Django settings: OK"
        return 0
    else
        iact_log_warning "Django settings not configured or invalid"
        return 1
    fi
}

# Check virtual environment
_check_virtualenv_step() {
    local step="$1"
    local total="$2"

    iact_log_step "$step" "$total" "Checking virtual environment"

    if iact_check_virtualenv_active; then
        iact_log_success "Virtual environment: Active"
    else
        iact_log_warning "No virtual environment active (DevContainer doesn't require it)"
    fi

    return 0
}

# Validate complete Python/Django installation
# IDEMPOTENT: Can be run multiple times
# NO SILENT FAILURES: Reports all validation results
#
# Usage: iact_validate_python_django_installation
#
# Returns:
#   0 - All validations passed
#   1 - One or more validations failed
iact_validate_python_django_installation() {
    iact_log_header "Python/Django Installation Validation"

    # Array de pasos de validación
    local validation_steps=(
        _validate_python_step
        _validate_pip_step
        _validate_django_step
        _validate_django_settings_step
        _check_virtualenv_step
    )

    local total_steps=${#validation_steps[@]}
    local current_step=0
    local failed_steps=()

    for step_function in "${validation_steps[@]}"; do
        ((current_step++))

        if ! $step_function $current_step $total_steps; then
            # Only add to failed if it's a critical step (not warnings)
            if [[ "$step_function" != "_check_virtualenv_step" ]] && \
               [[ "$step_function" != "_validate_django_settings_step" ]]; then
                failed_steps+=("$step_function")
            fi
        fi
    done

    # Report results
    if [[ ${#failed_steps[@]} -eq 0 ]]; then
        iact_log_success "Python/Django validation passed"
        return 0
    else
        iact_log_error "Python/Django validation failed: ${#failed_steps[@]} critical step(s) failed"
        for failed_step in "${failed_steps[@]}"; do
            iact_log_error "  - $failed_step"
        done
        return 1
    fi
}

# =============================================================================
# COMPATIBILITY ALIASES
# =============================================================================

check_python_available() { iact_check_python_available "$@"; }
get_python_version() { iact_get_python_version "$@"; }
check_python_version() { iact_check_python_version "$@"; }
check_pip_installed() { iact_check_pip_installed "$@"; }
get_pip_version() { iact_get_pip_version "$@"; }
check_python_package() { iact_check_python_package "$@"; }
upgrade_pip() { iact_upgrade_pip "$@"; }
check_virtualenv_active() { iact_check_virtualenv_active "$@"; }
check_django_installed() { iact_check_django_installed "$@"; }
get_django_version() { iact_get_django_version "$@"; }
check_django_settings() { iact_check_django_settings "$@"; }
check_django_project_exists() { iact_check_django_project_exists "$@"; }
django_manage() { iact_django_manage "$@"; }
run_django_check() { iact_run_django_check "$@"; }
check_django_migrations_needed() { iact_check_django_migrations_needed "$@"; }
run_django_migrations() { iact_run_django_migrations "$@"; }
collect_django_static() { iact_collect_django_static "$@"; }
install_requirements() { iact_install_requirements "$@"; }
check_pytest_installed() { iact_check_pytest_installed "$@"; }
run_pytest() { iact_run_pytest "$@"; }
validate_python_django_installation() { iact_validate_python_django_installation "$@"; }

# =============================================================================
# INITIALIZATION - IDEMPOTENT PATTERN
# =============================================================================

# Initialize python module
_iact_init_python() {
    local init_step="$1"
    local init_total="$2"

    iact_log_debug "Python module loaded successfully"

    return 0
}

# Array de pasos de inicialización
_PYTHON_INIT_STEPS=(
    _iact_init_python
)

# Main initialization function with auto-execution pattern
_init_python_main() {
    local total_steps=${#_PYTHON_INIT_STEPS[@]}
    local current_step=0

    for step_function in "${_PYTHON_INIT_STEPS[@]}"; do
        ((current_step++))

        if ! $step_function $current_step $total_steps; then
            echo "[ERROR] Python initialization failed at: $step_function" >&2
            return 1
        fi
    done

    # Success: all steps completed
    return 0
}

# Execute initialization immediately when python.sh is sourced
if ! _init_python_main; then
    echo "[FATAL] Python module initialization failed" >&2
    exit 1
fi