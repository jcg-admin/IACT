#!/usr/bin/env bash
# infrastructure/utils/core.sh
# Core functionality and module loader for IACT Infrastructure
# Provides: context detection, environment loading, module management, validation helpers
# This is the main entry point for all IACT infrastructure utilities
#
# Version: 2.0.0
# Author: IACT Team
# Pattern: Idempotent execution, No silent failures

set -euo pipefail

# =============================================================================
# PATH RESOLUTION
# =============================================================================

# Este módulo está en: infrastructure/utils/core.sh
readonly IACT_UTILS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Directorio infrastructure
readonly IACT_INFRASTRUCTURE_DIR="$(dirname "$IACT_UTILS_DIR")"

# Raíz del proyecto
readonly IACT_PROJECT_ROOT="$(dirname "$IACT_INFRASTRUCTURE_DIR")"

# =============================================================================
# CONTEXT DETECTION
# =============================================================================

# Detectar en qué contexto estamos ejecutando
# Soporta: devcontainer, vagrant, local
if [[ -f "/.dockerenv" ]] || grep -q docker /proc/1/cgroup 2>/dev/null; then
    # Running in Docker container (DevContainer)
    readonly IACT_CONTEXT="devcontainer"
    readonly IACT_CONTEXT_DIR="${IACT_INFRASTRUCTURE_DIR}/devcontainer"
    readonly IACT_IN_DEVCONTAINER=true
elif [[ -n "${VAGRANT:-}" ]] || [[ -f "/etc/vagrant_provisioned" ]]; then
    # Running in Vagrant VM
    readonly IACT_CONTEXT="vagrant"
    readonly IACT_CONTEXT_DIR="${IACT_INFRASTRUCTURE_DIR}/vagrant"
    readonly IACT_IN_DEVCONTAINER=false
else
    # Running locally (traditional development)
    readonly IACT_CONTEXT="local"
    readonly IACT_CONTEXT_DIR="${IACT_INFRASTRUCTURE_DIR}/local"
    readonly IACT_IN_DEVCONTAINER=false
fi

# =============================================================================
# CONTEXT-SPECIFIC DIRECTORIES
# =============================================================================

# Directorio de logs y estado según contexto
readonly IACT_LOG_DIR="${IACT_CONTEXT_DIR}/logs"
readonly IACT_STATE_DIR="${IACT_CONTEXT_DIR}/state"

# Workspace detection (DevContainer specific)
if [[ "$IACT_CONTEXT" == "devcontainer" ]] && [[ -d "/workspaces" ]]; then
    # DevContainer mounts project in /workspaces/
    readonly IACT_WORKSPACE_ROOT="/workspaces/${localWorkspaceFolderBasename:-callcentersite}"
else
    # Vagrant and local use project root directly
    readonly IACT_WORKSPACE_ROOT="$IACT_PROJECT_ROOT"
fi

# Django project directory
readonly DJANGO_PROJECT_DIR="${IACT_WORKSPACE_ROOT}/api/callcentersite"

# =============================================================================
# EXPORTS
# =============================================================================

export IACT_UTILS_DIR
export IACT_INFRASTRUCTURE_DIR
export IACT_PROJECT_ROOT
export IACT_CONTEXT
export IACT_CONTEXT_DIR
export IACT_LOG_DIR
export IACT_STATE_DIR
export IACT_WORKSPACE_ROOT
export IACT_IN_DEVCONTAINER
export DJANGO_PROJECT_DIR

# =============================================================================
# PUBLIC API: Context Queries
# =============================================================================

# Get current execution context
# Usage: context=$(iact_get_context)
# Returns: "devcontainer", "vagrant", or "local"
iact_get_context() {
    echo "$IACT_CONTEXT"
}

# Check if running in DevContainer
# Usage: if iact_is_devcontainer; then ...; fi
# Returns: 0 if in DevContainer, 1 otherwise
iact_is_devcontainer() {
    [[ "$IACT_CONTEXT" == "devcontainer" ]]
}

# Check if running in Vagrant
# Usage: if iact_is_vagrant; then ...; fi
# Returns: 0 if in Vagrant, 1 otherwise
iact_is_vagrant() {
    [[ "$IACT_CONTEXT" == "vagrant" ]]
}

# Check if running locally (outside containers)
# Usage: if iact_is_local; then ...; fi
# Returns: 0 if local, 1 otherwise
iact_is_local() {
    [[ "$IACT_CONTEXT" == "local" ]]
}

# =============================================================================
# MODULE LOADING
# =============================================================================

# Source a module from utils/
# NO SILENT FAILURES - Fails explicitly if module not found or fails to load
#
# Usage: iact_source_module "logging"
# Usage: iact_source_module "database"
#
# Args:
#   $1 - Module name (without .sh extension)
#
# Returns:
#   0 - Module loaded successfully
#   1 - Module not found or failed to load (EXPLICIT ERROR)
iact_source_module() {
    local module="$1"
    local module_file="$IACT_UTILS_DIR/${module}.sh"

    if [[ -f "$module_file" ]]; then
        # Try to source and verify it didn't fail
        if source "$module_file"; then
            return 0
        else
            echo "[ERROR] Module failed to load: $module_file" >&2
            return 1
        fi
    else
        echo "[ERROR] Module not found: $module_file" >&2
        return 1
    fi
}

# Auto-load logging module (always needed)
# This MUST succeed or the entire core fails
if ! iact_source_module "logging"; then
    echo "[FATAL] Cannot load logging module - core.sh requires logging.sh" >&2
    echo "[FATAL] Expected location: $IACT_UTILS_DIR/logging.sh" >&2
    exit 1
fi

# =============================================================================
# DIRECTORY CREATION - IDEMPOTENT
# =============================================================================

# Create context-specific directories
# Fails explicitly if directories cannot be created and are needed
_iact_create_directories() {
    local created_log=false
    local created_state=false

    # Try to create log directory
    if [[ ! -d "$IACT_LOG_DIR" ]]; then
        if mkdir -p "$IACT_LOG_DIR" 2>/dev/null; then
            created_log=true
        else
            echo "[WARN] Could not create log directory: $IACT_LOG_DIR" >&2
        fi
    fi

    # Try to create state directory
    if [[ ! -d "$IACT_STATE_DIR" ]]; then
        if mkdir -p "$IACT_STATE_DIR" 2>/dev/null; then
            created_state=true
        else
            echo "[WARN] Could not create state directory: $IACT_STATE_DIR" >&2
        fi
    fi

    # Idempotent: If directories exist, that's OK too
    return 0
}

# Execute directory creation
_iact_create_directories

# =============================================================================
# ENVIRONMENT LOADING
# =============================================================================

# Load project environment variables from .env files
# Sets defaults for development environment
#
# Usage: iact_load_project_environment
#
# Environment files searched (in order):
#   - $WORKSPACE_ROOT/api/callcentersite/.env
#   - $WORKSPACE_ROOT/.env
#   - $PROJECT_ROOT/api/callcentersite/.env
#   - $PROJECT_ROOT/.env
#
# Returns:
#   0 - Environment loaded successfully
iact_load_project_environment() {
    iact_log_debug "Loading project environment"

    # Detect environment files
    local env_files=(
        "$IACT_WORKSPACE_ROOT/api/callcentersite/.env"
        "$IACT_WORKSPACE_ROOT/.env"
        "$IACT_PROJECT_ROOT/api/callcentersite/.env"
        "$IACT_PROJECT_ROOT/.env"
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
        iact_log_debug "No environment file found, using defaults only"
    fi

    # Set defaults for PostgreSQL
    export DJANGO_DB_ENGINE="${DJANGO_DB_ENGINE:-django.db.backends.postgresql}"
    export DJANGO_DB_NAME="${DJANGO_DB_NAME:-iact_analytics}"
    export DJANGO_DB_USER="${DJANGO_DB_USER:-django_user}"
    export DJANGO_DB_PASSWORD="${DJANGO_DB_PASSWORD:-django_pass}"
    export DJANGO_DB_HOST="${DJANGO_DB_HOST:-db_postgres}"
    export DJANGO_DB_PORT="${DJANGO_DB_PORT:-5432}"

    # Set defaults for MariaDB (IVR Legacy - Read Only)
    export IVR_DB_ENGINE="${IVR_DB_ENGINE:-django.db.backends.mysql}"
    export IVR_DB_NAME="${IVR_DB_NAME:-ivr_legacy}"
    export IVR_DB_USER="${IVR_DB_USER:-django_user}"
    export IVR_DB_PASSWORD="${IVR_DB_PASSWORD:-django_pass}"
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
# NO SILENT FAILURES - Reports explicit error if cannot create marker
#
# Usage: iact_mark_installation_state "postgres"
# Usage: iact_mark_installation_state "mariadb"
#
# Returns:
#   0 - Component marked successfully
#   1 - Failed to mark component (EXPLICIT ERROR)
iact_mark_installation_state() {
    local component="$1"
    local state_file="$IACT_STATE_DIR/${component}.installed"

    # Ensure state directory exists
    if [[ ! -d "$IACT_STATE_DIR" ]]; then
        if ! mkdir -p "$IACT_STATE_DIR" 2>/dev/null; then
            iact_log_error "Cannot create state directory: $IACT_STATE_DIR"
            return 1
        fi
    fi

    # Try to create marker file with timestamp
    if date --iso-8601=seconds > "$state_file" 2>/dev/null; then
        iact_log_debug "Component marked as installed: $component"
        return 0
    else
        iact_log_error "Failed to create state marker for: $component at $state_file"
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
    local state_file="$IACT_STATE_DIR/${component}.installed"

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

# Validate root/sudo privileges (adapted for context)
# In containers, this check is relaxed as we run as non-root user
#
# Usage: iact_validate_root_privileges
#
# Returns:
#   0 - Privileges are sufficient
#   1 - Insufficient privileges (only outside containers)
iact_validate_root_privileges() {
    # In containers (DevContainer/Vagrant), we run as non-root which is sufficient
    if [[ "$IACT_CONTEXT" == "devcontainer" ]] || [[ "$IACT_CONTEXT" == "vagrant" ]]; then
        iact_log_debug "Running in $IACT_CONTEXT, root check skipped"
        return 0
    fi

    # Outside containers, check for actual root
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
# COMPATIBILITY ALIASES (for backward compatibility)
# =============================================================================

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
get_context() { iact_get_context "$@"; }
is_devcontainer() { iact_is_devcontainer "$@"; }
is_vagrant() { iact_is_vagrant "$@"; }
is_local() { iact_is_local "$@"; }

# =============================================================================
# INITIALIZATION - IDEMPOTENT AUTO-EXECUTION PATTERN
# =============================================================================

# Initialize core module
# This function runs all initialization steps
_iact_initialize_core() {
    local init_step="$1"
    local init_total="$2"

    # Verify logging is available (already loaded above)
    if ! command -v iact_log_info >/dev/null 2>&1; then
        echo "[FATAL] Logging functions not available after loading" >&2
        return 1
    fi

    # Log initialization info
    iact_log_debug "Core module initialized successfully"
    iact_log_debug "Context: $IACT_CONTEXT"
    iact_log_debug "Context Dir: $IACT_CONTEXT_DIR"
    iact_log_debug "Utils Dir: $IACT_UTILS_DIR"
    iact_log_debug "Project Root: $IACT_PROJECT_ROOT"
    iact_log_debug "Workspace: $IACT_WORKSPACE_ROOT"
    iact_log_debug "Log Dir: $IACT_LOG_DIR"
    iact_log_debug "State Dir: $IACT_STATE_DIR"
    iact_log_debug "Django Project: $DJANGO_PROJECT_DIR"

    return 0
}

# Array de pasos de inicialización
_CORE_INIT_STEPS=(
    _iact_initialize_core
)

# Main initialization function with auto-execution pattern
_init_core_main() {
    local total_steps=${#_CORE_INIT_STEPS[@]}
    local current_step=0
    local failed_steps=()

    for step_function in "${_CORE_INIT_STEPS[@]}"; do
        ((current_step++))

        if ! $step_function $current_step $total_steps; then
            failed_steps+=("$step_function")
            echo "[ERROR] Core initialization failed at: $step_function" >&2
            return 1
        fi
    done

    # Success: all steps completed
    return 0
}

# Execute initialization immediately when core.sh is sourced
if ! _init_core_main; then
    echo "[FATAL] Core module initialization failed" >&2
    exit 1
fi