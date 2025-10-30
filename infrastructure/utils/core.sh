#!/usr/bin/env bash
# utils/core.sh - Core functionality and module loader for IACT DevContainer
# Provides: environment loading, component state, validation, execution helpers
# This is the main entry point for all IACT DevContainer utilities

set -euo pipefail

# =============================================================================
# SCRIPT CONFIGURATION
# =============================================================================

# Este módulo está en: infrastructure/devcontainer/utils/core.sh
readonly IACT_UTILS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Directorio que contiene los scripts (infrastructure/devcontainer)
readonly IACT_DEVCONTAINER_DIR="$(dirname "$IACT_UTILS_DIR")"

# Directorio infrastructure
readonly IACT_INFRASTRUCTURE_DIR="$(dirname "$IACT_DEVCONTAINER_DIR")"

# Raíz del proyecto
readonly IACT_PROJECT_ROOT="$(dirname "$IACT_INFRASTRUCTURE_DIR")"

# Directorio de logs y estado
readonly IACT_LOG_DIR="${IACT_DEVCONTAINER_DIR}/logs"
readonly IACT_STATE_DIR="${IACT_DEVCONTAINER_DIR}/state"

# Detect DevContainer environment
if [[ -d "/workspaces" ]]; then
    IACT_WORKSPACE_ROOT="/workspaces/${localWorkspaceFolderBasename:-callcentersite}"
    IACT_IN_DEVCONTAINER=true
else
    IACT_WORKSPACE_ROOT="$IACT_PROJECT_ROOT"
    IACT_IN_DEVCONTAINER=false
fi

# Export variables for use in other scripts
export IACT_UTILS_DIR
export IACT_DEVCONTAINER_DIR
export IACT_INFRASTRUCTURE_DIR
export IACT_PROJECT_ROOT
export IACT_WORKSPACE_ROOT
export IACT_IN_DEVCONTAINER
export IACT_LOG_DIR
export IACT_STATE_DIR

# =============================================================================
# MODULE LOADING
# =============================================================================

# Source a module from utils/
# Usage: iact_source_module "logging"
# Usage: iact_source_module "database"
#
# Returns:
#   0 - Module loaded successfully
#   1 - Module not found
iact_source_module() {
    local module="$1"
    local module_file="$IACT_UTILS_DIR/${module}.sh"

    if [[ -f "$module_file" ]]; then
        source "$module_file"
        return 0
    else
        echo "ERROR: Module not found: $module_file" >&2
        return 1
    fi
}

# Auto-load logging module (always needed)
if ! iact_source_module "logging"; then
    echo "FATAL: Cannot load logging module" >&2
    exit 1
fi

# =============================================================================
# ENVIRONMENT LOADING
# =============================================================================

# Load project environment variables from .env files
# Sets defaults for DevContainer environment
#
# Usage: iact_load_project_environment
#
# Environment files searched (in order):
#   - $WORKSPACE_ROOT/api/callcentersite/env
#   - $WORKSPACE_ROOT/api/callcentersite/.env
#   - $PROJECT_ROOT/api/callcentersite/env
#   - $PROJECT_ROOT/api/callcentersite/.env
#
# Returns:
#   0 - Environment loaded successfully
iact_load_project_environment() {
    iact_log_debug "Loading project environment"

    # Detect environment files
    local env_files=(
        "$IACT_WORKSPACE_ROOT/api/callcentersite/env"
        "$IACT_WORKSPACE_ROOT/api/callcentersite/.env"
        "$IACT_PROJECT_ROOT/api/callcentersite/env"
        "$IACT_PROJECT_ROOT/api/callcentersite/.env"
    )

    # Load first available env file
    local env_loaded=false
    for env_file in "${env_files[@]}"; do
        if [[ -f "$env_file" ]]; then
            iact_log_debug "Loading environment from: $env_file"
            set -a
            source "$env_file"
            set +a
            env_loaded=true
            break
        fi
    done

    if [[ "$env_loaded" == "false" ]]; then
        iact_log_warning "No environment file found, using defaults only"
    fi

    # Set defaults for DevContainer PostgreSQL
    export DJANGO_DB_ENGINE="${DJANGO_DB_ENGINE:-django.db.backends.postgresql}"
    export DJANGO_DB_NAME="${DJANGO_DB_NAME:-iact_analytics}"
    export DJANGO_DB_USER="${DJANGO_DB_USER:-iact_user}"
    export DJANGO_DB_PASSWORD="${DJANGO_DB_PASSWORD:-iact_password}"
    export DJANGO_DB_HOST="${DJANGO_DB_HOST:-db_postgres}"
    export DJANGO_DB_PORT="${DJANGO_DB_PORT:-5432}"

    # Set defaults for DevContainer MariaDB (IVR Legacy - Read Only)
    export IVR_DB_ENGINE="${IVR_DB_ENGINE:-django.db.backends.mysql}"
    export IVR_DB_NAME="${IVR_DB_NAME:-ivr_legacy}"
    export IVR_DB_USER="${IVR_DB_USER:-ivr_readonly}"
    export IVR_DB_PASSWORD="${IVR_DB_PASSWORD:-readonly_password}"
    export IVR_DB_HOST="${IVR_DB_HOST:-db_mariadb}"
    export IVR_DB_PORT="${IVR_DB_PORT:-3306}"

    # General settings
    export DEBUG="${DEBUG:-true}"
    export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-callcentersite.settings.development}"

    iact_log_debug "Project environment loaded successfully"
    return 0
}

# =============================================================================
# COMPONENT STATE MANAGEMENT
# =============================================================================

# Check if a component is functional
# Loads the appropriate module and runs verification
#
# Usage: iact_is_component_functional "postgres"
# Usage: iact_is_component_functional "mariadb"
# Usage: iact_is_component_functional "python"
# Usage: iact_is_component_functional "django"
#
# Returns:
#   0 - Component is functional
#   1 - Component is not functional or unknown
iact_is_component_functional() {
    local component="$1"

    case "$component" in
        "postgres")
            iact_source_module "database" >/dev/null 2>&1
            iact_check_postgres_connect
            ;;
        "mariadb")
            iact_source_module "database" >/dev/null 2>&1
            iact_check_mariadb_connect
            ;;
        "python")
            iact_source_module "python" >/dev/null 2>&1
            iact_check_python_version
            ;;
        "django")
            iact_source_module "python" >/dev/null 2>&1
            iact_check_django_installed
            ;;
        *)
            iact_log_error "Unknown component: $component"
            return 1
            ;;
    esac
}

# Mark component as installed
# Creates a marker file to track installation state
#
# Usage: iact_mark_installation_state "postgres"
# Usage: iact_mark_installation_state "mariadb"
#
# Returns:
#   0 - Component marked successfully
iact_mark_installation_state() {
    local component="$1"
    local state_dir="$IACT_WORKSPACE_ROOT/.devcontainer/state"

    mkdir -p "$state_dir" 2>/dev/null || true

    if touch "$state_dir/${component}.installed" 2>/dev/null; then
        iact_log_debug "Component marked as installed: $component"
        return 0
    else
        iact_log_warning "Could not create state marker for: $component"
        return 1
    fi
}

# Get installation state of a component
# Checks if a component has been marked as installed
#
# Usage: if iact_get_installation_state "postgres"; then
#          echo "Already installed"
#        fi
#
# Returns:
#   0 - Component is marked as installed
#   1 - Component is not marked as installed
iact_get_installation_state() {
    local component="$1"
    local state_file="$IACT_WORKSPACE_ROOT/.devcontainer/state/${component}.installed"

    if [[ -f "$state_file" ]]; then
        iact_log_debug "Component $component is marked as installed"
        return 0
    else
        iact_log_debug "Component $component is not marked as installed"
        return 1
    fi
}

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

# Validate root/sudo privileges (adapted for DevContainer)
# In DevContainer, this check is relaxed as we typically run as vscode user
#
# Usage: iact_validate_root_privileges
#
# Returns:
#   0 - Privileges are sufficient
#   1 - Insufficient privileges (only outside DevContainer)
iact_validate_root_privileges() {
    # In DevContainer, we typically run as vscode user which is sufficient
    if [[ "$IACT_IN_DEVCONTAINER" == "true" ]]; then
        iact_log_debug "Running in DevContainer, root check skipped"
        return 0
    fi

    # Outside DevContainer, check for actual root
    if [[ $EUID -ne 0 ]]; then
        iact_log_error "This script must be run with root privileges"
        iact_log_info "Try: sudo $0"
        return 1
    fi

    iact_log_debug "Root privileges confirmed"
    return 0
}

# Validate Docker environment
# Checks if we are running inside a Docker container
#
# Usage: if iact_validate_docker_environment; then
#          echo "Running in Docker"
#        fi
#
# Returns:
#   0 - Running in Docker container
#   1 - Not running in Docker container
iact_validate_docker_environment() {
    if [[ -f "/.dockerenv" ]]; then
        iact_log_debug "Docker environment confirmed"
        return 0
    fi

    # Alternative check: look for docker in cgroup
    if grep -q docker /proc/1/cgroup 2>/dev/null; then
        iact_log_debug "Docker environment confirmed (via cgroup)"
        return 0
    fi

    iact_log_debug "Not running in Docker container"
    return 1
}

# =============================================================================
# EXECUTION HELPERS
# =============================================================================

# Execute command safely with logging
# Runs a command and logs the result
#
# Usage: iact_safe_execute "Package installation" apt-get install -y package
# Usage: iact_safe_execute "Database migration" python manage.py migrate
#
# Args:
#   $1 - Description of the operation
#   $@ - Command and arguments to execute
#
# Returns:
#   Exit code of the command
iact_safe_execute() {
    local description="$1"
    shift
    local command=("$@")

    iact_log_debug "Executing: ${command[*]}"

    if "${command[@]}"; then
        iact_log_debug "$description: success"
        return 0
    else
        local exit_code=$?
        iact_log_error "$description: failed (exit code: $exit_code)"
        return $exit_code
    fi
}

# Exit with error message
# Logs an error and exits the script
#
# Usage: iact_die "Fatal error occurred"
# Usage: iact_die "Configuration file not found" 2
#
# Args:
#   $1 - Error message
#   $2 - Exit code (optional, default: 1)
iact_die() {
    local message="$1"
    local exit_code="${2:-1}"

    iact_log_error "$message"
    exit "$exit_code"
}

# =============================================================================
# WAITING FUNCTIONS
# =============================================================================

# Wait for a port to be available
# Polls a port until it responds or timeout is reached
#
# Usage: iact_wait_for_port "localhost" "5432" "30" "PostgreSQL"
# Usage: iact_wait_for_port "db_postgres" "5432" "60"
#
# Args:
#   $1 - Host (hostname or IP)
#   $2 - Port number
#   $3 - Timeout in seconds (optional, default: 30)
#   $4 - Service name for logging (optional, default: "Service")
#
# Returns:
#   0 - Port is available
#   1 - Timeout reached
iact_wait_for_port() {
    local host="$1"
    local port="$2"
    local timeout="${3:-30}"
    local service_name="${4:-Service}"

    iact_log_debug "Waiting for $service_name on $host:$port (timeout: ${timeout}s)"

    local counter=0
    while [[ $counter -lt $timeout ]]; do
        # Try to connect to the port
        if command -v nc >/dev/null 2>&1; then
            # Use nc if available
            if nc -z "$host" "$port" 2>/dev/null; then
                iact_log_debug "$service_name port $port is ready"
                return 0
            fi
        else
            # Fallback: try to open connection with timeout
            if timeout 1 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
                iact_log_debug "$service_name port $port is ready"
                return 0
            fi
        fi

        sleep 1
        ((counter++))
    done

    iact_log_error "$service_name port $port not available after ${timeout}s"
    return 1
}

# =============================================================================
# COMPATIBILITY ALIASES
# =============================================================================

# Legacy compatibility (without iact_ prefix)
load_project_environment() { iact_load_project_environment "$@"; }
is_component_functional() { iact_is_component_functional "$@"; }
mark_installation_state() { iact_mark_installation_state "$@"; }
get_installation_state() { iact_get_installation_state "$@"; }
validate_root_privileges() { iact_validate_root_privileges "$@"; }
validate_docker_environment() { iact_validate_docker_environment "$@"; }
safe_execute() { iact_safe_execute "$@"; }
die() { iact_die "$@"; }
wait_for_port() { iact_wait_for_port "$@"; }
source_module() { iact_source_module "$@"; }

# =============================================================================
# INITIALIZATION
# =============================================================================

# Verify logging is available
if ! command -v iact_log_info >/dev/null 2>&1; then
    echo "FATAL: Logging functions not available" >&2
    exit 1
fi

iact_log_debug "Core module loaded successfully"
iact_log_debug "Utils directory: $IACT_UTILS_DIR"
iact_log_debug "Project root: $IACT_PROJECT_ROOT"
iact_log_debug "Workspace root: $IACT_WORKSPACE_ROOT"
iact_log_debug "In DevContainer: $IACT_IN_DEVCONTAINER"