#!/bin/bash

set -euo pipefail

# =================================================================
# GLOBAL VARIABLES
# =================================================================
LOGGING_INITIALIZED=false
LOG_FILE=""
LOG_TO_FILE=false

# =================================================================
# INITIALIZATION FUNCTIONS
# =================================================================

init_logging() {
    if [ "$LOGGING_INITIALIZED" = "true" ]; then
        return 0
    fi

    # Determine log file location
    if [ -d "/vagrant/logs" ]; then
        LOG_FILE="/vagrant/logs/bootstrap.log"
    elif [ -n "${LOGS_DIR:-}" ]; then
        LOG_FILE="$LOGS_DIR/bootstrap.log"
    else
        LOG_FILE="./logs/bootstrap.log"
    fi

    # Create log directory if needed
    local log_dir
    log_dir=$(dirname "$LOG_FILE")
    if [ ! -d "$log_dir" ]; then
        mkdir -p "$log_dir" 2>/dev/null || true
    fi

    # Try to create/touch log file
    if touch "$LOG_FILE" 2>/dev/null; then
        LOG_TO_FILE=true
        chmod 644 "$LOG_FILE" 2>/dev/null || true
    else
        LOG_TO_FILE=false
        echo "WARNING: Cannot write to log file: $LOG_FILE"
    fi

    LOGGING_INITIALIZED=true

    # Write initialization message
    write_to_file "$(date '+%Y-%m-%d %H:%M:%S') [INIT] Logging initialized"
}

write_to_file() {
    local message="$1"

    if [ "$LOG_TO_FILE" = "true" ] && [ -n "$LOG_FILE" ]; then
        echo "$message" >> "$LOG_FILE" 2>/dev/null || true
    fi
}

# =================================================================
# CORE LOGGING FUNCTIONS
# =================================================================

print_message() {
    local level="$1"
    local color="$2"
    local message="$3"

    local timestamp
    timestamp=$(date '+%H:%M:%S')
    local file_timestamp
    file_timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Print to terminal with colors
    printf "\033[0;${color}m[%s]\033[0m %s %s\n" "$level" "$timestamp" "$message"

    # Write to file without colors
    write_to_file "$file_timestamp [$level] $message"
}

# =================================================================
# PUBLIC LOGGING API
# =================================================================

log_info() {
    print_message "INFO" "34" "$1"
}

log_success() {
    print_message "SUCCESS" "32" "$1"
}

log_warning() {
    print_message "WARNING" "33" "$1"
}

log_error() {
    print_message "ERROR" "31" "$1"
}

log_debug() {
    if [ "${DEBUG:-false}" = "true" ]; then
        print_message "DEBUG" "37" "$1"
    fi
}

log_step() {
    print_message "STEP" "36" "$1"
}

log_header() {
    local message="$1"
    local separator="=========================================="
    local timestamp
    timestamp=$(date '+%H:%M:%S')
    local file_timestamp
    file_timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Print to terminal
    echo ""
    printf "\033[0;34m%s\033[0m\n" "$separator"
    printf "\033[0;34m[HEADER]\033[0m %s %s\n" "$timestamp" "$message"
    printf "\033[0;34m%s\033[0m\n" "$separator"
    echo ""

    # Write to file
    write_to_file ""
    write_to_file "$separator"
    write_to_file "$file_timestamp [HEADER] $message"
    write_to_file "$separator"
}

# =================================================================
# UTILITY FUNCTIONS
# =================================================================

show_log_config() {
    echo "Logging Configuration:"
    echo "  Initialized: $LOGGING_INITIALIZED"
    echo "  Log File: ${LOG_FILE:-[not set]}"
    echo "  File Logging: $LOG_TO_FILE"
    echo "  Debug Mode: ${DEBUG:-false}"
}

get_log_file() {
    echo "$LOG_FILE"
}

is_logging_to_file() {
    [ "$LOG_TO_FILE" = "true" ]
}

# =================================================================
# COMPATIBILITY FUNCTIONS
# =================================================================

# Legacy compatibility functions
log_warn() {
    log_warning "$@"
}

# =================================================================
# ERROR HANDLING
# =================================================================

log_and_exit() {
    local exit_code="${1:-1}"
    local message="${2:-Unknown error occurred}"

    log_error "$message"
    exit "$exit_code"
}

log_command_result() {
    local command="$1"
    local description="${2:-Command execution}"

    if eval "$command" >/dev/null 2>&1; then
        log_success "$description completed successfully"
        return 0
    else
        local exit_code=$?
        log_error "$description failed (exit code: $exit_code)"
        return $exit_code
    fi
}

# =================================================================
# TESTING FUNCTIONS
# =================================================================

test_logging() {
    log_header "Testing Logging System"
    log_info "This is an info message"
    log_success "This is a success message"
    log_warning "This is a warning message"
    log_error "This is an error message"
    log_debug "This is a debug message (only visible with DEBUG=true)"
    log_step "This is a step message"
    show_log_config

    if is_logging_to_file; then
        log_info "Log file location: $(get_log_file)"
    else
        log_warning "File logging is disabled"
    fi
}

# =================================================================
# AUTO-INITIALIZATION
# =================================================================

# Initialize logging when this script is sourced
init_logging