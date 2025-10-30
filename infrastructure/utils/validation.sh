#!/usr/bin/env bash
# utils/validation.sh - System validation functions for IACT DevContainer
# Provides validation functions for system requirements, commands, ports, and environment
# Designed for DevContainer environment but works in traditional environments too

set -euo pipefail

# =============================================================================
# COMMAND VALIDATION
# =============================================================================

# Check if a command exists in PATH
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

    iact_log_error "Docker Compose not found"
    return 1
}

# Check if a Docker container is running
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
        iact_log_debug "Container health status: $health_status"
        return 1
    fi
}

# Wait for a Docker container to become healthy
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
            iact_log_debug "Container $container is healthy"
            return 0
        fi

        sleep 1
        ((counter++))
    done

    iact_log_error "Container $container did not become healthy within ${timeout}s"
    return 1
}

# =============================================================================
# DEVCONTAINER VALIDATION
# =============================================================================

# Validate complete DevContainer environment
# Checks all essential components for IACT DevContainer
#
# Usage: iact_validate_devcontainer
#
# Returns:
#   0 - All validations passed
#   1 - One or more validations failed
iact_validate_devcontainer() {
    iact_log_header "DevContainer Environment Validation"

    local validation_errors=0

    # Check if running in DevContainer
    iact_log_info "Checking DevContainer environment..."
    if [[ "$IACT_IN_DEVCONTAINER" == "true" ]]; then
        iact_log_success "Running in DevContainer"
    else
        iact_log_warning "Not running in DevContainer (this is OK for local development)"
    fi

    # Check essential commands
    iact_log_info "Checking essential commands..."
    local required_commands=("python3" "pip" "git" "curl")
    if iact_check_commands_exist "${required_commands[@]}"; then
        iact_log_success "All essential commands available"
    else
        iact_log_error "Some essential commands are missing"
        ((validation_errors++))
    fi

    # Check Docker availability (if not in DevContainer)
    if [[ "$IACT_IN_DEVCONTAINER" == "false" ]]; then
        iact_log_info "Checking Docker availability..."
        if iact_check_docker_available; then
            iact_log_success "Docker is available"
        else
            iact_log_warning "Docker is not available (required for local development)"
            ((validation_errors++))
        fi
    fi

    # Check project structure
    iact_log_info "Checking project structure..."
    if iact_check_directory_exists "$IACT_WORKSPACE_ROOT/api"; then
        iact_log_success "Project structure validated"
    else
        iact_log_error "Project structure invalid: api directory not found"
        ((validation_errors++))
    fi

    # Report results
    if [[ $validation_errors -eq 0 ]]; then
        iact_log_success "DevContainer validation passed"
        return 0
    else
        iact_log_error "DevContainer validation failed with $validation_errors errors"
        return 1
    fi
}

# =============================================================================
# SYSTEM RESOURCE VALIDATION
# =============================================================================

# Check available disk space
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
        iact_log_warning "Could not determine available disk space"
        return 0
    fi

    local available_mb=$((available_kb / 1024))

    if [[ $available_mb -ge $required_mb ]]; then
        iact_log_debug "Disk space check passed: ${available_mb}MB available (${required_mb}MB required)"
        return 0
    else
        iact_log_error "Insufficient disk space: ${available_mb}MB available, ${required_mb}MB required"
        return 1
    fi
}

# Check available memory
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
check_disk_space() { iact_check_disk_space "$@"; }
check_memory() { iact_check_memory "$@"; }

# =============================================================================
# INITIALIZATION
# =============================================================================

iact_log_debug "Validation module loaded successfully"