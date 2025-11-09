#!/bin/bash
# Purpose: Centralized logging with timestamps, no colors, file output support

set -euo pipefail

# =============================================================================
# CONSTANTS
# =============================================================================

readonly LOG_FILE="${LOG_FILE:-}"
readonly LOG_LEVEL="${LOG_LEVEL:-INFO}"

# Log levels (for filtering)
readonly LOG_LEVEL_DEBUG=0
readonly LOG_LEVEL_INFO=1
readonly LOG_LEVEL_WARNING=2
readonly LOG_LEVEL_ERROR=3
readonly LOG_LEVEL_FATAL=4

# =============================================================================
# PRIVATE FUNCTIONS
# =============================================================================

# Generate timestamp in ISO 8601 format
# Returns: Current timestamp as YYYY-MM-DD HH:MM:SS
_get_timestamp() {
    date +"%Y-%m-%d %H:%M:%S"
}

# Get numeric level for comparison
# Args: $1 - level name (DEBUG, INFO, WARNING, ERROR, FATAL)
# Returns: Numeric level value
_get_numeric_level() {
    local level="$1"

    case "$level" in
        DEBUG)   echo $LOG_LEVEL_DEBUG ;;
        INFO)    echo $LOG_LEVEL_INFO ;;
        WARNING) echo $LOG_LEVEL_WARNING ;;
        ERROR)   echo $LOG_LEVEL_ERROR ;;
        FATAL)   echo $LOG_LEVEL_FATAL ;;
        *)       echo $LOG_LEVEL_INFO ;;
    esac
}

# Check if message should be logged based on level
# Args: $1 - message level
# Returns: 0 if should log, 1 if should skip
_should_log() {
    local msg_level="$1"

    local msg_level_num
    msg_level_num=$(_get_numeric_level "$msg_level")

    local current_level_num
    current_level_num=$(_get_numeric_level "$LOG_LEVEL")

    if (( msg_level_num >= current_level_num )); then
        return 0
    else
        return 1
    fi
}

# Write log message to stdout and optionally to file
# Args: $1 - level, $2+ - message
_write_log() {
    local level="$1"
    shift
    local message="$*"

    local timestamp
    timestamp=$(_get_timestamp)

    local formatted_message="[$timestamp] [$level] $message"

    # Write to stdout/stderr
    if [[ "$level" == "ERROR" ]] || [[ "$level" == "FATAL" ]]; then
        echo "$formatted_message" >&2
    else
        echo "$formatted_message"
    fi

    # Write to file if configured
    if [[ -n "$LOG_FILE" ]]; then
        echo "$formatted_message" >> "$LOG_FILE" 2>/dev/null || true
    fi
}

# =============================================================================
# PUBLIC LOGGING FUNCTIONS
# =============================================================================

# Log informational message
# Args: $* - message to log
# Example: log_info "Starting process"
log_info() {
    _should_log "INFO" || return 0
    _write_log "INFO" "$@"
}

# Log warning message
# Args: $* - message to log
# Example: log_warning "Deprecation notice"
log_warning() {
    _should_log "WARNING" || return 0
    _write_log "WARNING" "$@"
}

# Log error message
# Args: $* - message to log
# Example: log_error "Operation failed"
log_error() {
    _should_log "ERROR" || return 0
    _write_log "ERROR" "$@"
}

# Log fatal error message
# Args: $* - message to log
# Example: log_fatal "Critical failure, aborting"
log_fatal() {
    _should_log "FATAL" || return 0
    _write_log "FATAL" "$@"
}

# Log debug message (only when LOG_LEVEL=DEBUG)
# Args: $* - message to log
# Example: log_debug "Variable value: $var"
log_debug() {
    _should_log "DEBUG" || return 0
    _write_log "DEBUG" "$@"
}

# =============================================================================
# PROGRESS AND FORMATTING FUNCTIONS
# =============================================================================

# Log progress step
# Args: $1 - current step number, $2 - total steps, $3 - step description
# Example: log_step 1 3 "Installing dependencies"
log_step() {
    local current="$1"
    local total="$2"
    local description="$3"

    echo ""
    _write_log "INFO" "[STEP $current/$total] $description"
}

# Log header with separator
# Args: $1 - header text, $2 - optional width (default 70)
# Example: log_header "Build Starting" 80
log_header() {
    local message="$1"
    local width="${2:-70}"

    echo ""
    printf '=%.0s' $(seq 1 "$width")
    echo ""
    echo "  $message"
    printf '=%.0s' $(seq 1 "$width")
    echo ""
}

# Log separator line
# Args: $1 - optional width (default 70)
# Example: log_separator 80
log_separator() {
    local width="${1:-70}"
    printf '=%.0s' $(seq 1 "$width")
    echo ""
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Initialize log file with header
# Args: $1 - log file path (optional, uses LOG_FILE if not provided)
# Example: initialize_log_file "/var/log/build.log"
initialize_log_file() {
    local log_path="${1:-$LOG_FILE}"

    if [[ -z "$log_path" ]]; then
        return 0
    fi

    local log_dir
    log_dir=$(dirname "$log_path")

    # Ensure directory exists
    if [[ ! -d "$log_dir" ]]; then
        mkdir -p "$log_dir" 2>/dev/null || {
            echo "WARNING: Cannot create log directory: $log_dir" >&2
            return 1
        }
    fi

    # Write header
    {
        echo "================================================================================"
        echo "Log initialized: $(_get_timestamp)"
        echo "Script: ${0##*/}"
        echo "PID: $$"
        echo "User: ${USER:-unknown}"
        echo "PWD: $PWD"
        echo "================================================================================"
        echo ""
    } >> "$log_path" 2>/dev/null || {
        echo "WARNING: Cannot write to log file: $log_path" >&2
        return 1
    }

    return 0
}

# Log command execution with output capture
# Args: $1 - description, $2+ - command to execute
# Example: log_command_execution "Installing packages" apt-get install -y curl
log_command_execution() {
    local description="$1"
    shift
    local cmd=("$@")

    log_info "Executing: $description"
    log_debug "Command: ${cmd[*]}"

    local output
    local exit_code

    if output=$("${cmd[@]}" 2>&1); then
        exit_code=0
        log_debug "Command succeeded"
        if [[ -n "$output" ]]; then
            log_debug "Output: $output"
        fi
    else
        exit_code=$?
        log_error "Command failed with exit code: $exit_code"
        if [[ -n "$output" ]]; then
            log_error "Output: $output"
        fi
    fi

    return $exit_code
}

# =============================================================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================================================

# Alias for backward compatibility (log_warn -> log_warning)
log_warn() {
    log_warning "$@"
}

# Alias for backward compatibility (log_success -> log_info)
# Note: success is just informational logging
log_success() {
    log_info "$@"
}