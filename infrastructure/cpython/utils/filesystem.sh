#!/bin/bash
# utils/filesystem.sh - Filesystem operations for CPython Builder
# Reference: SPEC_INFRA_001
# Purpose: File and directory manipulation, extraction, and cleanup utilities

set -euo pipefail

# =============================================================================
# DEPENDENCIES
# =============================================================================

# Use local module directory - prevents conflicts with calling script's SCRIPT_DIR
_MODULE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Only source logger if not already loaded (environment.sh loads it first)
if [[ -z "${_LOGGER_SH_LOADED:-}" ]]; then
    source "$_MODULE_DIR/logger.sh"
fi

# =============================================================================
# CONSTANTS
# =============================================================================

readonly CRITICAL_PATHS=("/" "/bin" "/sbin" "/usr" "/etc" "/var" "/home" "/root" "/boot")

# =============================================================================
# ARCHIVE EXTRACTION
# =============================================================================

# Extract tarball to destination directory
# Args: $1 - tarball path, $2 - destination directory
# Returns: 0 on success, 1 on failure
# Example: extract_tarball "/tmp/Python-3.12.6.tgz" "/opt/python"
extract_tarball() {
    local tarball="$1"
    local dest_dir="$2"

    # Validate tarball exists
    if [[ ! -f "$tarball" ]]; then
        log_error "Tarball not found: $tarball"
        return 1
    fi

    # Validate destination directory
    if [[ ! -d "$dest_dir" ]]; then
        log_error "Destination directory not found: $dest_dir"
        return 1
    fi

    log_info "Extracting tarball: $(basename "$tarball")"
    log_debug "Source: $tarball"
    log_debug "Destination: $dest_dir"

    # Detect compression type and extract
    if [[ "$tarball" =~ \.tar\.gz$ ]] || [[ "$tarball" =~ \.tgz$ ]]; then
        if ! tar -xzf "$tarball" -C "$dest_dir" 2>&1; then
            log_error "Failed to extract gzip tarball"
            return 1
        fi
    elif [[ "$tarball" =~ \.tar\.bz2$ ]] || [[ "$tarball" =~ \.tbz2$ ]]; then
        if ! tar -xjf "$tarball" -C "$dest_dir" 2>&1; then
            log_error "Failed to extract bzip2 tarball"
            return 1
        fi
    elif [[ "$tarball" =~ \.tar\.xz$ ]] || [[ "$tarball" =~ \.txz$ ]]; then
        if ! tar -xJf "$tarball" -C "$dest_dir" 2>&1; then
            log_error "Failed to extract xz tarball"
            return 1
        fi
    elif [[ "$tarball" =~ \.tar$ ]]; then
        if ! tar -xf "$tarball" -C "$dest_dir" 2>&1; then
            log_error "Failed to extract uncompressed tarball"
            return 1
        fi
    else
        log_error "Unsupported archive format: $tarball"
        return 1
    fi

    log_info "Extraction completed successfully"
    return 0
}

# Extract tarball and return extracted directory name
# Args: $1 - tarball path, $2 - destination directory
# Returns: Extracted directory path via stdout, exits with 1 on failure
# Example: extracted_dir=$(extract_tarball_and_get_directory "/tmp/file.tgz" "/opt")
extract_tarball_and_get_directory() {
    local tarball="$1"
    local dest_dir="$2"

    # Count directories before extraction
    local before_count
    before_count=$(find "$dest_dir" -maxdepth 1 -type d | wc -l)

    # Extract
    if ! extract_tarball "$tarball" "$dest_dir"; then
        return 1
    fi

    # Count directories after extraction
    local after_count
    after_count=$(find "$dest_dir" -maxdepth 1 -type d | wc -l)

    # Find new directory
    if (( after_count > before_count )); then
        local extracted_dir
        extracted_dir=$(find "$dest_dir" -maxdepth 1 -type d -newer "$tarball" | grep -v "^${dest_dir}$" | head -1)

        if [[ -n "$extracted_dir" ]]; then
            echo "$extracted_dir"
            return 0
        fi
    fi

    log_error "Could not determine extracted directory"
    return 1
}

# =============================================================================
# DIRECTORY MANAGEMENT
# =============================================================================

# Ensure directory exists with proper permissions
# Args: $1 - directory path, $2 - optional permissions (default 755)
# Returns: 0 on success, 1 on failure
# Example: ensure_directory_exists "/opt/python" "755"
ensure_directory_exists() {
    local dir="$1"
    local permissions="${2:-755}"

    if [[ -d "$dir" ]]; then
        log_debug "Directory already exists: $dir"
        return 0
    fi

    log_debug "Creating directory: $dir"

    if ! mkdir -p "$dir" 2>/dev/null; then
        log_error "Failed to create directory: $dir"
        return 1
    fi

    if ! chmod "$permissions" "$dir" 2>/dev/null; then
        log_warning "Failed to set permissions on directory: $dir"
    fi

    log_debug "Directory created successfully: $dir"
    return 0
}

# Create temporary directory
# Args: $1 - optional prefix (default "cpython_builder")
# Returns: Temporary directory path via stdout, exits with 1 on failure
# Example: temp_dir=$(create_temp_directory "build_")
create_temp_directory() {
    local prefix="${1:-cpython_builder}"

    local temp_dir
    temp_dir=$(mktemp -d -t "${prefix}.XXXXXXXXXX" 2>/dev/null)

    if [[ -z "$temp_dir" ]] || [[ ! -d "$temp_dir" ]]; then
        log_error "Failed to create temporary directory"
        return 1
    fi

    log_debug "Created temporary directory: $temp_dir"
    echo "$temp_dir"
    return 0
}

# =============================================================================
# FILE AND DIRECTORY CLEANUP
# =============================================================================

# Safely remove path (file or directory)
# Args: $1 - path to remove
# Returns: 0 on success, 1 on failure
# Example: remove_path_safely "/tmp/build"
remove_path_safely() {
    local path="$1"

    # Validate path is not empty
    if [[ -z "$path" ]]; then
        log_error "Cannot remove empty path"
        return 1
    fi

    # Safety check: don't delete critical system paths
    for critical_path in "${CRITICAL_PATHS[@]}"; do
        if [[ "$path" == "$critical_path" ]]; then
            log_error "Refusing to delete critical path: $path"
            return 1
        fi
    done

    # Additional safety: path must not be too short
    if [[ "${#path}" -lt 4 ]]; then
        log_error "Path too short for safe removal: $path"
        return 1
    fi

    # Check if path exists
    if [[ ! -e "$path" ]]; then
        log_debug "Path does not exist: $path"
        return 0
    fi

    log_debug "Removing path: $path"

    if ! rm -rf "$path" 2>/dev/null; then
        log_error "Failed to remove path: $path"
        return 1
    fi

    log_debug "Path removed successfully: $path"
    return 0
}

# Clean up temporary directory
# Args: $1 - temporary directory path
# Returns: 0 on success, 1 on failure
# Example: cleanup_temp_directory "$temp_dir"
cleanup_temp_directory() {
    local temp_dir="$1"

    if [[ -z "$temp_dir" ]]; then
        log_debug "No temporary directory specified"
        return 0
    fi

    if [[ ! -d "$temp_dir" ]]; then
        log_debug "Temporary directory does not exist: $temp_dir"
        return 0
    fi

    # Safety check: must contain "tmp" or "temp" in path
    if [[ ! "$temp_dir" =~ tmp ]] && [[ ! "$temp_dir" =~ temp ]]; then
        log_warning "Directory does not appear to be temporary: $temp_dir"
        log_warning "Refusing to clean up"
        return 1
    fi

    log_info "Cleaning up temporary directory: $temp_dir"

    if ! remove_path_safely "$temp_dir"; then
        return 1
    fi

    log_info "Temporary directory cleaned up successfully"
    return 0
}

# Clean up old files in directory
# Args: $1 - directory path, $2 - age in days (files older than this)
# Returns: 0 on success, 1 on failure
# Example: cleanup_old_files "/var/log/builds" 7
cleanup_old_files() {
    local dir="$1"
    local age_days="$2"

    if [[ ! -d "$dir" ]]; then
        log_error "Directory not found: $dir"
        return 1
    fi

    log_info "Cleaning up files older than $age_days days in: $dir"

    local count
    count=$(find "$dir" -type f -mtime +"$age_days" 2>/dev/null | wc -l || echo 0)

    if (( count == 0 )); then
        log_info "No old files to clean up"
        return 0
    fi

    log_info "Found $count old file(s) to remove"

    if ! find "$dir" -type f -mtime +"$age_days" -delete 2>/dev/null; then
        log_error "Failed to clean up old files"
        return 1
    fi

    log_info "Old files cleaned up successfully"
    return 0
}

# =============================================================================
# FILE OPERATIONS
# =============================================================================

# Copy file with verification
# Args: $1 - source file, $2 - destination file
# Returns: 0 on success, 1 on failure
# Example: copy_file_with_verification "/tmp/source" "/opt/dest"
copy_file_with_verification() {
    local source="$1"
    local dest="$2"

    if [[ ! -f "$source" ]]; then
        log_error "Source file not found: $source"
        return 1
    fi

    log_debug "Copying file: $source -> $dest"

    if ! cp "$source" "$dest" 2>/dev/null; then
        log_error "Failed to copy file"
        return 1
    fi

    # Verify file was copied
    if [[ ! -f "$dest" ]]; then
        log_error "Destination file not created: $dest"
        return 1
    fi

    # Verify file sizes match
    local source_size
    source_size=$(stat -c %s "$source" 2>/dev/null || echo 0)
    local dest_size
    dest_size=$(stat -c %s "$dest" 2>/dev/null || echo 0)

    if (( source_size != dest_size )); then
        log_error "File size mismatch after copy"
        log_error "Source: ${source_size} bytes, Destination: ${dest_size} bytes"
        return 1
    fi

    log_debug "File copied and verified successfully"
    return 0
}

# Move file safely
# Args: $1 - source file, $2 - destination file
# Returns: 0 on success, 1 on failure
# Example: move_file_safely "/tmp/source" "/opt/dest"
move_file_safely() {
    local source="$1"
    local dest="$2"

    if [[ ! -f "$source" ]]; then
        log_error "Source file not found: $source"
        return 1
    fi

    # Ensure destination directory exists
    local dest_dir
    dest_dir=$(dirname "$dest")
    if ! ensure_directory_exists "$dest_dir"; then
        return 1
    fi

    log_debug "Moving file: $source -> $dest"

    if ! mv "$source" "$dest" 2>/dev/null; then
        log_error "Failed to move file"
        return 1
    fi

    # Verify source is gone and destination exists
    if [[ -f "$source" ]]; then
        log_error "Source file still exists after move"
        return 1
    fi

    if [[ ! -f "$dest" ]]; then
        log_error "Destination file not created"
        return 1
    fi

    log_debug "File moved successfully"
    return 0
}

# =============================================================================
# DISK SPACE UTILITIES
# =============================================================================

# Get directory size in KB
# Args: $1 - directory path
# Returns: Size in KB via stdout, 0 on failure
# Example: size=$(get_directory_size_kb "/opt/python")
get_directory_size_kb() {
    local dir="$1"

    if [[ ! -d "$dir" ]]; then
        echo "0"
        return 1
    fi

    local size_kb
    size_kb=$(du -sk "$dir" 2>/dev/null | awk '{print $1}' || echo 0)

    echo "$size_kb"
    return 0
}

# Get available disk space in KB
# Args: $1 - path to check (default current directory)
# Returns: Available space in KB via stdout
# Example: available=$(get_available_disk_space_kb "/opt")
get_available_disk_space_kb() {
    local path="${1:-.}"

    local available_kb
    available_kb=$(df "$path" 2>/dev/null | awk 'NR==2 {print $4}' || echo 0)

    echo "$available_kb"
    return 0
}

# Check if enough disk space is available
# Args: $1 - path, $2 - required space in KB
# Returns: 0 if enough space, 1 if not
# Example: check_disk_space_available "/opt" 5242880  # 5GB
check_disk_space_available() {
    local path="$1"
    local required_kb="$2"

    local available_kb
    available_kb=$(get_available_disk_space_kb "$path")

    if (( available_kb >= required_kb )); then
        log_debug "Sufficient disk space available: ${available_kb}KB (required: ${required_kb}KB)"
        return 0
    else
        log_error "Insufficient disk space: ${available_kb}KB available, ${required_kb}KB required"
        return 1
    fi
}

# =============================================================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================================================

# Alias for backward compatibility
cleanup_temp_dir() {
    cleanup_temp_directory "$@"
}