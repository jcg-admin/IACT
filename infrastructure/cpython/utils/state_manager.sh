#!/bin/bash
# utils/state_manager.sh - State management for CPython Builder operations
# Reference: SPEC_INFRA_001
# Purpose: Track operation completion state for idempotent builds

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

readonly DEFAULT_STATE_DIR="${PROJECT_ROOT:-.}/.build_state"
readonly STATE_DIR="${BUILD_STATE_DIR:-$DEFAULT_STATE_DIR}"
readonly STATE_FILE_EXTENSION=".done"
readonly STATE_METADATA_EXTENSION=".meta"

# =============================================================================
# STATE DIRECTORY MANAGEMENT
# =============================================================================

# Initialize state directory
# Args: $1 - optional state directory path (uses STATE_DIR if not provided)
# Returns: 0 on success, 1 on failure
# Example: initialize_state_directory "/vagrant/.build_state"
initialize_state_directory() {
    local state_path="${1:-$STATE_DIR}"

    if [[ -d "$state_path" ]]; then
        log_debug "State directory already exists: $state_path"
        return 0
    fi

    if ! mkdir -p "$state_path" 2>/dev/null; then
        log_error "Failed to create state directory: $state_path"
        return 1
    fi

    log_debug "State directory initialized: $state_path"
    return 0
}

# Get state directory path
# Returns: State directory path via stdout
# Example: state_dir=$(get_state_directory_path)
get_state_directory_path() {
    echo "$STATE_DIR"
}

# Check if state directory exists
# Returns: 0 if exists, 1 otherwise
# Example: if state_directory_exists; then ...
state_directory_exists() {
    [[ -d "$STATE_DIR" ]]
}

# =============================================================================
# OPERATION STATE MANAGEMENT
# =============================================================================

# Mark operation as complete
# Args: $1 - operation name, $2+ - optional metadata key=value pairs
# Returns: 0 on success, 1 on failure
# Example: mark_operation_complete "download_python" "version=3.12.6" "size=27MB"
mark_operation_complete() {
    local operation="$1"
    shift
    local metadata=("$@")

    # Ensure state directory exists
    if ! initialize_state_directory; then
        return 1
    fi

    local state_file="$STATE_DIR/${operation}${STATE_FILE_EXTENSION}"
    local meta_file="$STATE_DIR/${operation}${STATE_METADATA_EXTENSION}"

    # Create state file with timestamp
    local timestamp
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")

    if ! echo "$timestamp" > "$state_file" 2>/dev/null; then
        log_error "Failed to create state file: $state_file"
        return 1
    fi

    # Write metadata if provided
    if (( ${#metadata[@]} > 0 )); then
        {
            echo "timestamp=$timestamp"
            for item in "${metadata[@]}"; do
                echo "$item"
            done
        } > "$meta_file" 2>/dev/null || {
            log_warning "Failed to write metadata file: $meta_file"
        }
    fi

    log_debug "Operation marked complete: $operation"
    return 0
}

# Check if operation is complete
# Args: $1 - operation name
# Returns: 0 if complete, 1 if not complete or error
# Example: if is_operation_complete "download_python"; then ...
is_operation_complete() {
    local operation="$1"

    local state_file="$STATE_DIR/${operation}${STATE_FILE_EXTENSION}"

    if [[ -f "$state_file" ]]; then
        log_debug "Operation is complete: $operation"
        return 0
    else
        log_debug "Operation not complete: $operation"
        return 1
    fi
}

# Get operation completion timestamp
# Args: $1 - operation name
# Returns: Timestamp via stdout, empty if not complete
# Example: timestamp=$(get_operation_timestamp "download_python")
get_operation_timestamp() {
    local operation="$1"

    local state_file="$STATE_DIR/${operation}${STATE_FILE_EXTENSION}"

    if [[ -f "$state_file" ]]; then
        cat "$state_file" 2>/dev/null || echo ""
    else
        echo ""
    fi
}

# Get operation metadata
# Args: $1 - operation name, $2 - metadata key
# Returns: Metadata value via stdout, empty if not found
# Example: version=$(get_operation_metadata "download_python" "version")
get_operation_metadata() {
    local operation="$1"
    local key="$2"

    local meta_file="$STATE_DIR/${operation}${STATE_METADATA_EXTENSION}"

    if [[ -f "$meta_file" ]]; then
        grep "^${key}=" "$meta_file" 2>/dev/null | cut -d= -f2- || echo ""
    else
        echo ""
    fi
}

# Reset operation state
# Args: $1 - operation name
# Returns: 0 on success, 1 on failure
# Example: reset_operation_state "download_python"
reset_operation_state() {
    local operation="$1"

    local state_file="$STATE_DIR/${operation}${STATE_FILE_EXTENSION}"
    local meta_file="$STATE_DIR/${operation}${STATE_METADATA_EXTENSION}"

    local removed=0

    if [[ -f "$state_file" ]]; then
        if rm -f "$state_file" 2>/dev/null; then
            log_debug "Removed state file: $state_file"
            removed=1
        else
            log_error "Failed to remove state file: $state_file"
            return 1
        fi
    fi

    if [[ -f "$meta_file" ]]; then
        rm -f "$meta_file" 2>/dev/null || \
            log_warning "Failed to remove metadata file: $meta_file"
    fi

    if (( removed == 1 )); then
        log_info "Operation state reset: $operation"
    else
        log_debug "Operation state was not set: $operation"
    fi

    return 0
}

# =============================================================================
# BULK STATE OPERATIONS
# =============================================================================

# List all completed operations
# Returns: List of operation names via stdout, one per line
# Example: list_completed_operations
list_completed_operations() {
    if ! state_directory_exists; then
        return 0
    fi

    local state_files
    state_files=$(find "$STATE_DIR" -name "*${STATE_FILE_EXTENSION}" -type f 2>/dev/null || true)

    if [[ -z "$state_files" ]]; then
        return 0
    fi

    echo "$state_files" | while read -r file; do
        local basename
        basename=$(basename "$file" "$STATE_FILE_EXTENSION")
        echo "$basename"
    done
}

# Count completed operations
# Returns: Number of completed operations via stdout
# Example: count=$(count_completed_operations)
count_completed_operations() {
    if ! state_directory_exists; then
        echo 0
        return 0
    fi

    local count
    count=$(find "$STATE_DIR" -name "*${STATE_FILE_EXTENSION}" -type f 2>/dev/null | wc -l || echo 0)
    echo "$count"
}

# Clear all state (remove all completion markers)
# Returns: 0 on success, 1 on failure
# Example: clear_all_state
clear_all_state() {
    if ! state_directory_exists; then
        log_debug "State directory does not exist, nothing to clear"
        return 0
    fi

    local file_count
    file_count=$(find "$STATE_DIR" -type f 2>/dev/null | wc -l || echo 0)

    if (( file_count == 0 )); then
        log_debug "No state files to clear"
        return 0
    fi

    if ! rm -rf "${STATE_DIR:?}"/* 2>/dev/null; then
        log_error "Failed to clear state directory: $STATE_DIR"
        return 1
    fi

    log_info "All state cleared ($file_count files removed)"
    return 0
}

# Reset specific operations by pattern
# Args: $1 - pattern (glob or regex)
# Returns: 0 on success, 1 on failure
# Example: reset_operations_matching "download_*"
reset_operations_matching() {
    local pattern="$1"

    if ! state_directory_exists; then
        log_debug "State directory does not exist"
        return 0
    fi

    local count=0
    local state_files
    state_files=$(find "$STATE_DIR" -name "${pattern}${STATE_FILE_EXTENSION}" -type f 2>/dev/null || true)

    if [[ -z "$state_files" ]]; then
        log_debug "No operations matching pattern: $pattern"
        return 0
    fi

    while read -r file; do
        local basename
        basename=$(basename "$file" "$STATE_FILE_EXTENSION")
        if reset_operation_state "$basename"; then
            count=$((count + 1))
        fi
    done <<< "$state_files"

    log_info "Reset $count operation(s) matching pattern: $pattern"
    return 0
}

# =============================================================================
# STATE VALIDATION
# =============================================================================

# Validate operation state consistency
# Args: $1 - operation name
# Returns: 0 if valid, 1 if invalid
# Example: validate_operation_state "download_python"
validate_operation_state() {
    local operation="$1"

    local state_file="$STATE_DIR/${operation}${STATE_FILE_EXTENSION}"

    # Check if state file exists
    if [[ ! -f "$state_file" ]]; then
        log_debug "State file does not exist: $operation"
        return 1
    fi

    # Check if state file is readable
    if [[ ! -r "$state_file" ]]; then
        log_error "State file not readable: $state_file"
        return 1
    fi

    # Check if state file has content
    if [[ ! -s "$state_file" ]]; then
        log_error "State file is empty: $state_file"
        return 1
    fi

    # Validate timestamp format
    local timestamp
    timestamp=$(cat "$state_file" 2>/dev/null || echo "")

    if [[ ! "$timestamp" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\ [0-9]{2}:[0-9]{2}:[0-9]{2}$ ]]; then
        log_error "Invalid timestamp format in state file: $state_file"
        return 1
    fi

    log_debug "State validation passed: $operation"
    return 0
}

# Check for stale state (completed but old)
# Args: $1 - operation name, $2 - max age in seconds (default 86400 = 24h)
# Returns: 0 if fresh, 1 if stale
# Example: if is_operation_state_stale "download_python" 3600; then ...
is_operation_state_stale() {
    local operation="$1"
    local max_age_seconds="${2:-86400}"

    if ! is_operation_complete "$operation"; then
        log_debug "Operation not complete, cannot be stale: $operation"
        return 1
    fi

    local state_file="$STATE_DIR/${operation}${STATE_FILE_EXTENSION}"

    # Get file modification time
    local file_mtime
    file_mtime=$(stat -c %Y "$state_file" 2>/dev/null || echo 0)

    local current_time
    current_time=$(date +%s)

    local age=$((current_time - file_mtime))

    if (( age > max_age_seconds )); then
        log_debug "Operation state is stale: $operation (age: ${age}s)"
        return 0
    else
        log_debug "Operation state is fresh: $operation (age: ${age}s)"
        return 1
    fi
}

# =============================================================================
# REPORTING
# =============================================================================

# Generate state report
# Returns: 0 always, outputs report to stdout
# Example: generate_state_report
generate_state_report() {
    echo "=========================================="
    echo "Build State Report"
    echo "=========================================="
    echo ""

    if ! state_directory_exists; then
        echo "State directory does not exist."
        echo "No operations have been tracked."
        return 0
    fi

    local total_count
    total_count=$(count_completed_operations)

    if (( total_count == 0 )); then
        echo "No operations completed."
        return 0
    fi

    echo "Total completed operations: $total_count"
    echo ""
    echo "Completed operations:"
    echo "----------------------------------------"

    local operations
    operations=$(list_completed_operations)

    while read -r operation; do
        [[ -z "$operation" ]] && continue

        local timestamp
        timestamp=$(get_operation_timestamp "$operation")

        local version
        version=$(get_operation_metadata "$operation" "version")

        if [[ -n "$version" ]]; then
            echo "  - $operation (completed: $timestamp, version: $version)"
        else
            echo "  - $operation (completed: $timestamp)"
        fi
    done <<< "$operations"

    echo ""
}

# Export state to JSON format
# Returns: 0 on success, JSON output to stdout
# Example: export_state_to_json > state.json
export_state_to_json() {
    echo "{"
    echo "  \"state_directory\": \"$STATE_DIR\","
    echo "  \"total_operations\": $(count_completed_operations),"
    echo "  \"operations\": ["

    local first=1
    local operations
    operations=$(list_completed_operations)

    while read -r operation; do
        [[ -z "$operation" ]] && continue

        if (( first == 0 )); then
            echo ","
        fi
        first=0

        local timestamp
        timestamp=$(get_operation_timestamp "$operation")

        echo -n "    {"
        echo -n "\"name\": \"$operation\", "
        echo -n "\"timestamp\": \"$timestamp\""
        echo -n "}"
    done <<< "$operations"

    echo ""
    echo "  ]"
    echo "}"
}