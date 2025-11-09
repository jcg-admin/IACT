#!/bin/bash
# utils/validator.sh - Validation utilities for CPython Builder
# Reference: SPEC_INFRA_001
# Purpose: Reusable validation functions with clear error reporting

set -euo pipefail

# =============================================================================
# DEPENDENCIES
# =============================================================================

# Note: SCRIPT_DIR may be set by calling script, so don't mark as readonly
if [[ -z "${SCRIPT_DIR:-}" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi
source "$SCRIPT_DIR/logger.sh"

# =============================================================================
# CONSTANTS
# =============================================================================

readonly MIN_DISK_SPACE_KB=5242880  # 5GB minimum for builds

# =============================================================================
# COMMAND AND TOOL VALIDATION
# =============================================================================

# Validate that a command exists in PATH
# Args: $1 - command name, $2 - optional custom error message
# Returns: 0 if command exists, 1 otherwise
# Example: validate_command_exists "gcc" || exit 1
validate_command_exists() {
    local cmd="$1"
    local error_msg="${2:-Command not found: $cmd}"

    if ! command -v "$cmd" >/dev/null 2>&1; then
        log_error "$error_msg"
        return 1
    fi

    return 0
}

# Validate that multiple commands exist
# Args: $* - list of command names
# Returns: 0 if all exist, 1 if any missing
# Example: validate_commands_exist gcc make wget
validate_commands_exist() {
    local commands=("$@")
    local missing=()

    for cmd in "${commands[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing+=("$cmd")
        fi
    done

    if (( ${#missing[@]} > 0 )); then
        log_error "Missing required commands: ${missing[*]}"
        return 1
    fi

    return 0
}

# =============================================================================
# VERSION VALIDATION
# =============================================================================

# Validate Python version format (X.Y.Z)
# Args: $1 - version string
# Returns: 0 if valid format, 1 otherwise
# Example: validate_version_format "3.12.6"
validate_version_format() {
    local version="$1"

    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "Invalid version format: $version"
        log_error "Expected format: X.Y.Z (example: 3.12.6)"
        return 1
    fi

    return 0
}

# Validate semantic version format (X.Y.Z with optional pre-release)
# Args: $1 - version string
# Returns: 0 if valid, 1 otherwise
# Example: validate_semantic_version "3.12.6-beta.1"
validate_semantic_version() {
    local version="$1"

    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?$ ]]; then
        log_error "Invalid semantic version: $version"
        log_error "Expected format: X.Y.Z or X.Y.Z-prerelease"
        return 1
    fi

    return 0
}

# =============================================================================
# CHECKSUM VALIDATION
# =============================================================================

# Validate SHA256 checksum of a file
# Args: $1 - file path, $2 - checksum file path
# Returns: 0 if checksum matches, 1 otherwise
# Example: validate_sha256_checksum "file.tgz" "file.tgz.sha256"
validate_sha256_checksum() {
    local file="$1"
    local checksum_file="$2"

    # Validate inputs exist
    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi

    if [[ ! -f "$checksum_file" ]]; then
        log_error "Checksum file not found: $checksum_file"
        return 1
    fi

    # Navigate to directory for sha256sum
    local dir
    dir=$(dirname "$file")
    local filename
    filename=$(basename "$file")

    local original_dir="$PWD"

    cd "$dir" || {
        log_error "Cannot access directory: $dir"
        return 1
    }

    # Perform validation
    local result
    if result=$(sha256sum -c "$checksum_file" 2>&1); then
        if echo "$result" | grep -q "OK"; then
            cd "$original_dir" || true
            log_debug "SHA256 checksum validated successfully for $filename"
            return 0
        fi
    fi

    cd "$original_dir" || true
    log_error "SHA256 checksum validation failed for $filename"
    log_debug "Validation output: $result"
    return 1
}

# Validate MD5 checksum of a file
# Args: $1 - file path, $2 - checksum file path
# Returns: 0 if checksum matches, 1 otherwise
# Example: validate_md5_checksum "file.tgz" "file.tgz.md5"
validate_md5_checksum() {
    local file="$1"
    local checksum_file="$2"

    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi

    if [[ ! -f "$checksum_file" ]]; then
        log_error "Checksum file not found: $checksum_file"
        return 1
    fi

    local dir
    dir=$(dirname "$file")
    local filename
    filename=$(basename "$file")

    local original_dir="$PWD"

    cd "$dir" || {
        log_error "Cannot access directory: $dir"
        return 1
    }

    if md5sum -c "$checksum_file" 2>&1 | grep -q "OK"; then
        cd "$original_dir" || true
        return 0
    fi

    cd "$original_dir" || true
    log_error "MD5 checksum validation failed for $filename"
    return 1
}

# =============================================================================
# FILE AND DIRECTORY VALIDATION
# =============================================================================

# Validate that a file exists
# Args: $1 - file path, $2 - optional custom error message
# Returns: 0 if file exists, 1 otherwise
# Example: validate_file_exists "/path/to/file" || exit 1
validate_file_exists() {
    local file="$1"
    local error_msg="${2:-File not found: $file}"

    if [[ ! -f "$file" ]]; then
        log_error "$error_msg"
        return 1
    fi

    return 0
}

# Validate that a directory exists
# Args: $1 - directory path, $2 - optional custom error message
# Returns: 0 if directory exists, 1 otherwise
# Example: validate_directory_exists "/path/to/dir" || exit 1
validate_directory_exists() {
    local dir="$1"
    local error_msg="${2:-Directory not found: $dir}"

    if [[ ! -d "$dir" ]]; then
        log_error "$error_msg"
        return 1
    fi

    return 0
}

# Validate that a path exists (file or directory)
# Args: $1 - path, $2 - optional custom error message
# Returns: 0 if path exists, 1 otherwise
# Example: validate_path_exists "/path/to/something"
validate_path_exists() {
    local path="$1"
    local error_msg="${2:-Path not found: $path}"

    if [[ ! -e "$path" ]]; then
        log_error "$error_msg"
        return 1
    fi

    return 0
}

# Validate that a file is readable
# Args: $1 - file path
# Returns: 0 if readable, 1 otherwise
# Example: validate_file_readable "/etc/config"
validate_file_readable() {
    local file="$1"

    if [[ ! -f "$file" ]]; then
        log_error "File not found: $file"
        return 1
    fi

    if [[ ! -r "$file" ]]; then
        log_error "File not readable: $file"
        return 1
    fi

    return 0
}

# Validate that a directory is writable
# Args: $1 - directory path
# Returns: 0 if writable, 1 otherwise
# Example: validate_directory_writable "/var/log"
validate_directory_writable() {
    local dir="$1"

    if [[ ! -d "$dir" ]]; then
        log_error "Directory not found: $dir"
        return 1
    fi

    if [[ ! -w "$dir" ]]; then
        log_error "Directory not writable: $dir"
        return 1
    fi

    return 0
}

# =============================================================================
# PYTHON MODULE VALIDATION
# =============================================================================

# Validate that Python modules are available
# Args: $1 - python binary path, $2+ - module names
# Returns: 0 if all modules available, 1 if any missing
# Example: validate_python_modules "/usr/bin/python3" ssl sqlite3 uuid
validate_python_modules() {
    local python_bin="$1"
    shift
    local modules=("$@")
    local failed_modules=()

    # Validate python binary exists
    if ! validate_command_exists "$python_bin" "Python binary not found: $python_bin"; then
        return 1
    fi

    # Test each module
    for module in "${modules[@]}"; do
        if "$python_bin" -c "import $module" 2>/dev/null; then
            log_debug "Module $module: OK"
        else
            log_error "Module $module: FAILED"
            failed_modules+=("$module")
        fi
    done

    # Report results
    if (( ${#failed_modules[@]} > 0 )); then
        log_error "Failed Python modules: ${failed_modules[*]}"
        return 1
    fi

    log_debug "All Python modules validated successfully"
    return 0
}

# Validate Python version meets minimum requirement
# Args: $1 - python binary, $2 - minimum version (X.Y)
# Returns: 0 if meets requirement, 1 otherwise
# Example: validate_python_version_minimum "/usr/bin/python3" "3.8"
validate_python_version_minimum() {
    local python_bin="$1"
    local min_version="$2"

    if ! validate_command_exists "$python_bin"; then
        return 1
    fi

    local actual_version
    actual_version=$("$python_bin" --version 2>&1 | awk '{print $2}')

    local actual_major
    actual_major=$(echo "$actual_version" | cut -d. -f1)
    local actual_minor
    actual_minor=$(echo "$actual_version" | cut -d. -f2)

    local min_major
    min_major=$(echo "$min_version" | cut -d. -f1)
    local min_minor
    min_minor=$(echo "$min_version" | cut -d. -f2)

    if (( actual_major < min_major )) || \
       (( actual_major == min_major && actual_minor < min_minor )); then
        log_error "Python version $actual_version is below minimum $min_version"
        return 1
    fi

    log_debug "Python version $actual_version meets minimum $min_version"
    return 0
}

# =============================================================================
# DISK SPACE VALIDATION
# =============================================================================

# Validate sufficient disk space is available
# Args: $1 - path to check, $2 - minimum space in KB (optional, default 5GB)
# Returns: 0 if sufficient space, 1 otherwise
# Example: validate_disk_space "/vagrant" 10485760  # 10GB
validate_disk_space() {
    local path="${1:-.}"
    local min_space_kb="${2:-$MIN_DISK_SPACE_KB}"

    # Validate path exists
    if [[ ! -e "$path" ]]; then
        log_error "Path not found: $path"
        return 1
    fi

    # Get available space in KB
    local available_kb
    available_kb=$(df "$path" | awk 'NR==2 {print $4}')

    if (( available_kb < min_space_kb )); then
        local available_mb=$((available_kb / 1024))
        local required_mb=$((min_space_kb / 1024))
        log_error "Insufficient disk space at $path"
        log_error "Available: ${available_mb}MB, Required: ${required_mb}MB"
        return 1
    fi

    local available_mb=$((available_kb / 1024))
    log_debug "Disk space OK at $path: ${available_mb}MB available"
    return 0
}

# =============================================================================
# NETWORK VALIDATION
# =============================================================================

# Validate network connectivity
# Args: $1 - host to ping (optional, default 8.8.8.8)
# Returns: 0 if connected, 1 otherwise
# Example: validate_network_connectivity "google.com"
validate_network_connectivity() {
    local host="${1:-8.8.8.8}"

    if ping -c 1 -W 2 "$host" >/dev/null 2>&1; then
        log_debug "Network connectivity OK (tested with $host)"
        return 0
    fi

    log_error "No network connectivity (cannot reach $host)"
    return 1
}

# Validate URL is reachable
# Args: $1 - URL to check
# Returns: 0 if reachable, 1 otherwise
# Example: validate_url_reachable "https://www.python.org"
validate_url_reachable() {
    local url="$1"

    if command -v curl >/dev/null 2>&1; then
        if curl -fsSL --head "$url" >/dev/null 2>&1; then
            log_debug "URL reachable: $url"
            return 0
        fi
    elif command -v wget >/dev/null 2>&1; then
        if wget --spider -q "$url" 2>/dev/null; then
            log_debug "URL reachable: $url"
            return 0
        fi
    else
        log_error "Neither curl nor wget available for URL validation"
        return 1
    fi

    log_error "URL not reachable: $url"
    return 1
}

# =============================================================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================================================

# Alias for backward compatibility
validate_python_version() {
    validate_version_format "$@"
}

# Alias for backward compatibility
validate_checksum() {
    validate_sha256_checksum "$@"
}

# Alias for backward compatibility
validate_dir_exists() {
    validate_directory_exists "$@"
}