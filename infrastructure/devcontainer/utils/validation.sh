#!/usr/bin/env bash
# infrastructure/utils/validation.sh
# System validation functions for IACT Infrastructure
# Provides validation functions for system requirements, commands, ports, and environment
# Works in DevContainer, Vagrant, and traditional environments
#
# Version: 2.0.0
# Pattern: Idempotent execution, No silent failures

set -euo pipefail

# =============================================================================
# COMMAND VALIDATION
# =============================================================================

# Check if a command exists in PATH
# NO SILENT FAILURES: Always reports result via logging
#
# Usage: iact_check_command_exists "python3"
# Usage: if iact_check_command_exists "docker"; then ...; fi
#
# Args:
#   $1 - Command name to check
#
# Returns:
#   0 - Command exists
#   1 - Command not found
iact_check_command_exists() {
    local command_name="$1"

    if command -v "$command_name" >/dev/null 2>&1; then
        iact_log_debug "Command found: $command_name"
        return 0
    else
        iact_log_debug "Command not found: $command_name"
        return 1
    fi
}

# Check if multiple commands exist
# NO SILENT FAILURES: Reports all missing commands explicitly
#
# Usage: iact_check_commands_exist "python3" "pip" "git"
#
# Args:
#   $@ - List of command names to check
#
# Returns:
#   0 - All commands exist
#   1 - One or more commands not found
iact_check_commands_exist() {
    local commands=("$@")
    local missing_commands=()

    for cmd in "${commands[@]}"; do
        if ! iact_check_command_exists "$cmd"; then
            missing_commands+=("$cmd")
        fi
    done

    if [[ ${#missing_commands[@]} -eq 0 ]]; then
        iact_log_debug "All required commands are available"
        return 0
    else
        iact_log_error "Missing commands: ${missing_commands[*]}"
        return 1
    fi
}

# =============================================================================
# PORT VALIDATION
# =============================================================================

# Check if a port is listening
# NO SILENT FAILURES: Always reports result
#
# Usage: iact_check_port_listening "5432"
# Usage: iact_check_port_listening "3306" "localhost"
#
# Args:
#   $1 - Port number
#   $2 - Host (optional, default: localhost)
#
# Returns:
#   0 - Port is listening
#   1 - Port is not listening
iact_check_port_listening() {
    local port="$1"
    local host="${2:-localhost}"

    if command -v nc >/dev/null 2>&1; then
        # Use nc if available
        if nc -z "$host" "$port" 2>/dev/null; then
            iact_log_debug "Port $port is listening on $host"
            return 0
        fi
    elif command -v netstat >/dev/null 2>&1; then
        # Fallback to netstat
        if netstat -tuln 2>/dev/null | grep -q ":${port} "; then
            iact_log_debug "Port $port is listening"
            return 0
        fi
    else
        # Last resort: try to connect
        if timeout 1 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null; then
            iact_log_debug "Port $port is listening on $host"
            return 0
        fi
    fi

    iact_log_debug "Port $port is not listening on $host"
    return 1
}

# =============================================================================
# ENVIRONMENT VARIABLE VALIDATION
# =============================================================================

# Check if environment variable is set and not empty
# NO SILENT FAILURES: Always logs result
#
# Usage: iact_check_environment_variable "DB_HOST"
# Usage: if iact_check_environment_variable "DEBUG"; then ...; fi
#
# Args:
#   $1 - Variable name to check
#
# Returns:
#   0 - Variable is set and not empty
#   1 - Variable is unset or empty
iact_check_environment_variable() {
    local var_name="$1"

    if [[ -n "${!var_name:-}" ]]; then
        iact_log_debug "Environment variable $var_name is set: ${!var_name}"
        return 0
    else
        iact_log_debug "Environment variable $var_name is not set or empty"
        return 1
    fi
}

# Check if multiple environment variables are set
# NO SILENT FAILURES: Reports all missing variables explicitly
#
# Usage: iact_check_environment_variables "DB_HOST" "DB_PORT" "DB_NAME"
#
# Args:
#   $@ - List of variable names to check
#
# Returns:
#   0 - All variables are set
#   1 - One or more variables are unset or empty
iact_check_environment_variables() {
    local variables=("$@")
    local missing_variables=()

    for var in "${variables[@]}"; do
        if ! iact_check_environment_variable "$var"; then
            missing_variables+=("$var")
        fi
    done

    if [[ ${#missing_variables[@]} -eq 0 ]]; then
        iact_log_debug "All required environment variables are set"
        return 0
    else
        iact_log_error "Missing environment variables: ${missing_variables[*]}"
        return 1
    fi
}

# =============================================================================
# FILE AND DIRECTORY VALIDATION
# =============================================================================

# Check if file exists and is readable
# NO SILENT FAILURES: Always reports result
#
# Usage: iact_check_file_exists "/path/to/file"
#
# Args:
#   $1 - File path to check
#
# Returns:
#   0 - File exists and is readable
#   1 - File does not exist or is not readable
iact_check_file_exists() {
    local file_path="$1"

    if [[ -f "$file_path" ]] && [[ -r "$file_path" ]]; then
        iact_log_debug "File exists and is readable: $file_path"
        return 0
    else
        iact_log_debug "File does not exist or is not readable: $file_path"
        return 1
    fi
}

# Check if directory exists and is accessible
# NO SILENT FAILURES: Always reports result
#
# Usage: iact_check_directory_exists "/path/to/dir"
#
# Args:
#   $1 - Directory path to check
#
# Returns:
#   0 - Directory exists and is accessible
#   1 - Directory does not exist or is not accessible
iact_check_directory_exists() {
    local dir_path="$1"

    if [[ -d "$dir_path" ]] && [[ -x "$dir_path" ]]; then
        iact_log_debug "Directory exists and is accessible: $dir_path"
        return 0
    else
        iact_log_debug "Directory does not exist or is not accessible: $dir_path"
        return 1
    fi
}

# =============================================================================
# DOCKER VALIDATION
# =============================================================================

# Check if Docker is available and running
# NO SILENT FAILURES: Explicitly reports what's missing
#
# Usage: iact_check_docker_available
#
# Returns:
#   0 - Docker is available and running
#   1 - Docker is not available or not running
iact_check_docker_available() {
    if ! iact_check_command_exists "docker"; then
        iact_log_error "Docker command not found"
        return 1
    fi

    if ! docker info >/dev/null 2>&1; then
        iact_log_error "Docker daemon is not running or not accessible"
        return 1
    fi

    iact_log_debug "Docker is available and running"
    return 0
}

# Check if Docker Compose is available
# NO SILENT FAILURES: Reports which compose method is available
#
# Usage: iact_check_docker_compose_available
#
# Returns:
#   0 - Docker Compose is available
#   1 - Docker Compose is not available
iact_check_docker_compose_available() {
    # Check for docker-compose command
    if iact_check_command_exists "docker-compose"; then
        iact_log_debug "docker-compose command found"
        return 0
    fi

    # Check for docker compose plugin
    if docker compose version >/dev/null 2>&1; then
        iact_log_debug "docker compose plugin found"
        return 0
    fi

    iact_log_error "Docker Compose not found (neither docker-compose nor docker compose plugin)"
    return 1
}

# Check if a Docker container is running
# NO SILENT FAILURES: Reports container status
#
# Usage: iact_check_container_running "db_postgres"
#
# Args:
#   $1 - Container name or ID
#
# Returns:
#   0 - Container is running
#   1 - Container is not running or does not exist
iact_check_container_running() {
    local container="$1"

    if ! iact_check_command_exists "docker"; then
        iact_log_error "Docker command not found"
        return 1
    fi

    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^${container}$"; then
        iact_log_debug "Container is running: $container"
        return 0
    else
        iact_log_debug "Container is not running: $container"
        return 1
    fi
}

# Check if a Docker container is healthy
# NO SILENT FAILURES: Reports actual health status
#
# Usage: iact_check_container_healthy "db_postgres"
#
# Args:
#   $1 - Container name or ID
#
# Returns:
#   0 - Container is healthy
#   1 - Container is not healthy or does not have health check
iact_check_container_healthy() {
    local container="$1"

    if ! iact_check_command_exists "docker"; then
        iact_log_error "Docker command not found"
        return 1
    fi

    local health_status
    health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")

    if [[ "$health_status" == "healthy" ]]; then
        iact_log_debug "Container is healthy: $container"
        return 0
    else
        iact_log_debug "Container health status: $health_status (container: $container)"
        return 1
    fi
}

# Wait for a Docker container to become healthy
# NO SILENT FAILURES: Reports timeout explicitly
#
# Usage: iact_wait_for_container_healthy "db_postgres" "60"
#
# Args:
#   $1 - Container name or ID
#   $2 - Timeout in seconds (optional, default: 30)
#
# Returns:
#   0 - Container became healthy
#   1 - Timeout reached
iact_wait_for_container_healthy() {
    local container="$1"
    local timeout="${2:-30}"

    iact_log_debug "Waiting for container to be healthy: $container (timeout: ${timeout}s)"

    local counter=0
    while [[ $counter -lt $timeout ]]; do
        if iact_check_container_healthy "$container"; then
            iact_log_debug "Container $container is healthy after ${counter}s"
            return 0
        fi

        sleep 1
        ((counter++))
    done

    iact_log_error "Container $container did not become healthy within ${timeout}s"
    return 1
}

# =============================================================================
# CONTEXT-AWARE VALIDATION
# =============================================================================

# Validate complete environment based on context
# Adapts validation based on IACT_CONTEXT (devcontainer/vagrant/local)
#
# Usage: iact_validate_environment
#
# Returns:
#   0 - All validations passed
#   1 - One or more validations failed
iact_validate_environment() {
    local context="${IACT_CONTEXT:-local}"

    iact_log_header "Environment Validation (Context: $context)"

    local validation_errors=0

    # Context-specific validation
    case "$context" in
        "devcontainer")
            iact_log_info "Validating DevContainer environment..."
            if iact_validate_devcontainer_context; then
                iact_log_success "DevContainer context validated"
            else
                iact_log_error "DevContainer context validation failed"
                ((validation_errors++))
            fi
            ;;
        "vagrant")
            iact_log_info "Validating Vagrant environment..."
            if iact_validate_vagrant_context; then
                iact_log_success "Vagrant context validated"
            else
                iact_log_error "Vagrant context validation failed"
                ((validation_errors++))
            fi
            ;;
        "local")
            iact_log_info "Validating local environment..."
            if iact_validate_local_context; then
                iact_log_success "Local context validated"
            else
                iact_log_error "Local context validation failed"
                ((validation_errors++))
            fi
            ;;
        *)
            iact_log_warning "Unknown context: $context"
            ((validation_errors++))
            ;;
    esac

    # Common validations
    iact_log_info "Checking essential commands..."
    local required_commands=("python3" "pip" "git" "curl")
    if iact_check_commands_exist "${required_commands[@]}"; then
        iact_log_success "All essential commands available"
    else
        iact_log_error "Some essential commands are missing"
        ((validation_errors++))
    fi

    # Check project structure
    iact_log_info "Checking project structure..."
    if [[ -n "${IACT_WORKSPACE_ROOT:-}" ]] && iact_check_directory_exists "$IACT_WORKSPACE_ROOT/api"; then
        iact_log_success "Project structure validated"
    else
        iact_log_error "Project structure invalid: api directory not found"
        ((validation_errors++))
    fi

    # Report results
    if [[ $validation_errors -eq 0 ]]; then
        iact_log_success "Environment validation passed"
        return 0
    else
        iact_log_error "Environment validation failed with $validation_errors errors"
        return 1
    fi
}

# Validate DevContainer-specific requirements
iact_validate_devcontainer_context() {
    local errors=0

    # Check if running in Docker
    if [[ -f "/.dockerenv" ]]; then
        iact_log_debug "Running in Docker container"
    else
        iact_log_warning "Not running in Docker (expected for DevContainer)"
        ((errors++))
    fi

    # Check workspace mount
    if [[ -d "/workspaces" ]]; then
        iact_log_debug "Workspace mount detected"
    else
        iact_log_warning "Workspace mount not found"
        ((errors++))
    fi

    return $errors
}

# Validate Vagrant-specific requirements
iact_validate_vagrant_context() {
    local errors=0

    # Check Vagrant marker
    if [[ -f "/etc/vagrant_provisioned" ]]; then
        iact_log_debug "Vagrant provisioned marker found"
    else
        iact_log_warning "Vagrant provisioned marker not found"
        ((errors++))
    fi

    return $errors
}

# Validate local development requirements
iact_validate_local_context() {
    local errors=0

    # Check Docker availability
    if iact_check_docker_available; then
        iact_log_debug "Docker is available for local development"
    else
        iact_log_warning "Docker not available (may be needed for containers)"
        ((errors++))
    fi

    return $errors
}

# Legacy function for backward compatibility
iact_validate_devcontainer() {
    iact_validate_environment
}

# =============================================================================
# SYSTEM RESOURCE VALIDATION
# =============================================================================

# Check available disk space
# NO SILENT FAILURES: Reports actual values
#
# Usage: iact_check_disk_space "/path" "1000"
# Usage: iact_check_disk_space "/" "5000"  # Check for 5GB
#
# Args:
#   $1 - Path to check (default: /)
#   $2 - Required space in MB (default: 1000)
#
# Returns:
#   0 - Sufficient disk space
#   1 - Insufficient disk space
iact_check_disk_space() {
    local path="${1:-/}"
    local required_mb="${2:-1000}"

    if ! command -v df >/dev/null 2>&1; then
        iact_log_warning "df command not available, skipping disk space check"
        return 0
    fi

    local available_kb
    available_kb=$(df "$path" 2>/dev/null | awk 'NR==2 {print $4}')

    if [[ -z "$available_kb" ]]; then
        iact_log_warning "Could not determine available disk space for: $path"
        return 0
    fi

    local available_mb=$((available_kb / 1024))

    if [[ $available_mb -ge $required_mb ]]; then
        iact_log_debug "Disk space check passed: ${available_mb}MB available (${required_mb}MB required)"
        return 0
    else
        iact_log_error "Insufficient disk space on $path: ${available_mb}MB available, ${required_mb}MB required"
        return 1
    fi
}

# Check available memory
# NO SILENT FAILURES: Reports actual values
#
# Usage: iact_check_memory "1024"  # Check for 1GB
#
# Args:
#   $1 - Required memory in MB (default: 512)
#
# Returns:
#   0 - Sufficient memory
#   1 - Insufficient memory
iact_check_memory() {
    local required_mb="${1:-512}"

    if ! command -v free >/dev/null 2>&1; then
        iact_log_warning "free command not available, skipping memory check"
        return 0
    fi

    local available_mb
    available_mb=$(free -m 2>/dev/null | awk 'NR==2{print $7}')

    if [[ -z "$available_mb" ]]; then
        iact_log_warning "Could not determine available memory"
        return 0
    fi

    if [[ $available_mb -ge $required_mb ]]; then
        iact_log_debug "Memory check passed: ${available_mb}MB available (${required_mb}MB required)"
        return 0
    else
        iact_log_warning "Low memory: ${available_mb}MB available, ${required_mb}MB recommended"
        return 1
    fi
}

# =============================================================================
# COMPATIBILITY ALIASES
# =============================================================================

check_command_exists() { iact_check_command_exists "$@"; }
check_commands_exist() { iact_check_commands_exist "$@"; }
check_port_listening() { iact_check_port_listening "$@"; }
check_environment_variable() { iact_check_environment_variable "$@"; }
check_environment_variables() { iact_check_environment_variables "$@"; }
check_file_exists() { iact_check_file_exists "$@"; }
check_directory_exists() { iact_check_directory_exists "$@"; }
check_docker_available() { iact_check_docker_available "$@"; }
check_docker_compose_available() { iact_check_docker_compose_available "$@"; }
check_container_running() { iact_check_container_running "$@"; }
check_container_healthy() { iact_check_container_healthy "$@"; }
wait_for_container_healthy() { iact_wait_for_container_healthy "$@"; }
validate_devcontainer() { iact_validate_devcontainer "$@"; }
validate_environment() { iact_validate_environment "$@"; }
check_disk_space() { iact_check_disk_space "$@"; }
check_memory() { iact_check_memory "$@"; }

# =============================================================================
# INITIALIZATION - IDEMPOTENT PATTERN
# =============================================================================

# Initialize validation module
_iact_init_validation() {
    local init_step="$1"
    local init_total="$2"

    iact_log_debug "Validation module loaded successfully"

    return 0
}

# Array de pasos de inicialización
_VALIDATION_INIT_STEPS=(
    _iact_init_validation
)

# Main initialization function with auto-execution pattern
_init_validation_main() {
    local total_steps=${#_VALIDATION_INIT_STEPS[@]}
    local current_step=0

    for step_function in "${_VALIDATION_INIT_STEPS[@]}"; do
        ((current_step++))

        if ! $step_function $current_step $total_steps; then
            echo "[ERROR] Validation initialization failed at: $step_function" >&2
            return 1
        fi
    done

    # Success: all steps completed
    return 0
}

# Execute initialization immediately when validation.sh is sourced
if ! _init_validation_main; then
    echo "[FATAL] Validation module initialization failed" >&2
    exit 1
fi