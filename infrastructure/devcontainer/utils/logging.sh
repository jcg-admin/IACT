#!/usr/bin/env bash
# infrastructure/utils/logging.sh
# Logging system for IACT Infrastructure
# Provides consistent logging functions with colors, file output, and step tracking
# Auto-initializes when sourced
#
# Version: 2.0.0
# Pattern: Idempotent execution, No silent failures

set -euo pipefail

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

IACT_LOGGING_INITIALIZED=false
IACT_LOG_FILE=""
IACT_LOG_TO_FILE=false
IACT_LOG_COLORS="${IACT_LOG_COLORS:-1}"
IACT_LOG_SCRIPT_NAME=""

# =============================================================================
# COLOR CODES
# =============================================================================

readonly COLOR_RESET='\033[0m'
readonly COLOR_RED='\033[0;31m'
readonly COLOR_GREEN='\033[0;32m'
readonly COLOR_YELLOW='\033[0;33m'
readonly COLOR_BLUE='\033[0;34m'
readonly COLOR_CYAN='\033[0;36m'
readonly COLOR_WHITE='\033[0;37m'

# =============================================================================
# INITIALIZATION FUNCTIONS
# =============================================================================

# Initialize logging system
# Detects environment and sets up log file location
# IDEMPOTENT: Can be called multiple times safely
# NO SILENT FAILURES: Reports all issues to stderr
#
# Usage: iact_init_logging
# Usage: iact_init_logging "post-create"
# Usage: iact_init_logging "verificar"
#
# Args:
#   $1 - Optional script name for specific log file
#
# Returns:
#   0 - Logging initialized successfully
iact_init_logging() {
    local script_name="${1:-}"

    # Idempotent: Skip if already initialized with same config
    if [[ "$IACT_LOGGING_INITIALIZED" == "true" ]]; then
        # If script_name provided and different, re-initialize
        if [[ -n "$script_name" ]] && [[ "$IACT_LOG_SCRIPT_NAME" != "$script_name" ]]; then
            IACT_LOGGING_INITIALIZED=false
        else
            return 0
        fi
    fi

    # Store script name
    IACT_LOG_SCRIPT_NAME="$script_name"

    # Determine log file location based on environment
    # Priority 1: Use IACT_LOG_DIR from core.sh if available
    if [[ -n "${IACT_LOG_DIR:-}" ]]; then
        if [[ -n "$script_name" ]]; then
            IACT_LOG_FILE="$IACT_LOG_DIR/${script_name}.log"
        else
            IACT_LOG_FILE="$IACT_LOG_DIR/iact.log"
        fi
    # Priority 2: DevContainer environment
    elif [[ -d "/workspaces" ]]; then
        local workspace="/workspaces/${localWorkspaceFolderBasename:-callcentersite}"
        if [[ -n "$script_name" ]]; then
            IACT_LOG_FILE="$workspace/infrastructure/devcontainer/logs/${script_name}.log"
        else
            IACT_LOG_FILE="$workspace/infrastructure/devcontainer/logs/iact.log"
        fi
    # Priority 3: Custom log directory
    elif [[ -n "${LOGS_DIR:-}" ]]; then
        if [[ -n "$script_name" ]]; then
            IACT_LOG_FILE="$LOGS_DIR/${script_name}.log"
        else
            IACT_LOG_FILE="$LOGS_DIR/iact.log"
        fi
    # Priority 4: Default location
    else
        if [[ -n "$script_name" ]]; then
            IACT_LOG_FILE="./logs/${script_name}.log"
        else
            IACT_LOG_FILE="./logs/iact.log"
        fi
    fi

    # Create log directory if needed
    local log_dir
    log_dir=$(dirname "$IACT_LOG_FILE")
    if [[ ! -d "$log_dir" ]]; then
        if ! mkdir -p "$log_dir" 2>/dev/null; then
            echo "[WARN] Could not create log directory: $log_dir" >&2
        fi
    fi

    # Try to create/touch log file
    # NO SILENT FAILURES: Explicitly report if cannot write
    if touch "$IACT_LOG_FILE" 2>/dev/null; then
        IACT_LOG_TO_FILE=true
        chmod 644 "$IACT_LOG_FILE" 2>/dev/null || true
    else
        IACT_LOG_TO_FILE=false
        echo "[WARN] Cannot write to log file: $IACT_LOG_FILE" >&2
        echo "[INFO] Logging will continue to terminal only" >&2
    fi

    IACT_LOGGING_INITIALIZED=true

    # Write initialization message
    local context_info=""
    if [[ -n "${IACT_CONTEXT:-}" ]]; then
        context_info=" (context: $IACT_CONTEXT)"
    fi
    iact_write_to_file "$(date '+%Y-%m-%d %H:%M:%S') [INIT] Logging initialized${context_info}"

    return 0
}

# Write message to log file (internal function)
# NO SILENT FAILURES: Returns error if write fails
#
# Args:
#   $1 - Message to write
#
# Returns:
#   0 - Message written successfully (or logging disabled)
#   1 - Failed to write (only if critical)
iact_write_to_file() {
    local message="$1"

    if [[ "$IACT_LOG_TO_FILE" == "true" ]] && [[ -n "$IACT_LOG_FILE" ]]; then
        if ! echo "$message" >> "$IACT_LOG_FILE" 2>/dev/null; then
            # Write failure - disable file logging to avoid spam
            IACT_LOG_TO_FILE=false
            echo "[ERROR] Failed to write to log file: $IACT_LOG_FILE" >&2
            return 1
        fi
    fi

    return 0
}

# =============================================================================
# CORE LOGGING FUNCTIONS
# =============================================================================

# Internal function to print formatted message
# Args: level, color_code, message
iact_print_message() {
    local level="$1"
    local color_code="$2"
    local message="$3"

    local timestamp
    timestamp=$(date '+%H:%M:%S')
    local file_timestamp
    file_timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Print to terminal with colors (if enabled)
    if [[ "$IACT_LOG_COLORS" == "1" ]]; then
        printf "${color_code}[%s]${COLOR_RESET} %s %s\n" "$level" "$timestamp" "$message"
    else
        printf "[%s] %s %s\n" "$level" "$timestamp" "$message"
    fi

    # Write to file without colors
    iact_write_to_file "$file_timestamp [$level] $message"
}

# =============================================================================
# PUBLIC LOGGING API
# =============================================================================

# Log info message (blue)
# Usage: iact_log_info "Starting process"
iact_log_info() {
    iact_print_message "INFO" "$COLOR_BLUE" "$1"
}

# Log success message (green)
# Usage: iact_log_success "Operation completed"
iact_log_success() {
    iact_print_message "SUCCESS" "$COLOR_GREEN" "$1"
}

# Log warning message (yellow)
# Usage: iact_log_warning "Potential issue detected"
iact_log_warning() {
    iact_print_message "WARNING" "$COLOR_YELLOW" "$1"
}

# Log error message (red)
# Usage: iact_log_error "Operation failed"
iact_log_error() {
    iact_print_message "ERROR" "$COLOR_RED" "$1" >&2
}

# Log debug message (white, only if DEBUG=true)
# Usage: iact_log_debug "Debug information"
iact_log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        iact_print_message "DEBUG" "$COLOR_WHITE" "$1"
    fi
}

# Log step with progress indicator (cyan)
# Usage: iact_log_step "1" "10" "Installing dependencies"
# Args: step_number, total_steps, message
iact_log_step() {
    local step="$1"
    local total="$2"
    local message="$3"

    local timestamp
    timestamp=$(date '+%H:%M:%S')
    local file_timestamp
    file_timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Format: [STEP 1/10] HH:MM:SS Message
    local step_label="STEP ${step}/${total}"

    # Print to terminal with colors (if enabled)
    if [[ "$IACT_LOG_COLORS" == "1" ]]; then
        printf "${COLOR_CYAN}[%s]${COLOR_RESET} %s %s\n" "$step_label" "$timestamp" "$message"
    else
        printf "[%s] %s %s\n" "$step_label" "$timestamp" "$message"
    fi

    # Write to file
    iact_write_to_file "$file_timestamp [$step_label] $message"
}

# Log header with separator lines (blue)
# Usage: iact_log_header "INSTALLATION STARTING"
iact_log_header() {
    local message="$1"
    local separator="============================================================================="
    local timestamp
    timestamp=$(date '+%H:%M:%S')
    local file_timestamp
    file_timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    # Print to terminal
    echo ""
    if [[ "$IACT_LOG_COLORS" == "1" ]]; then
        printf "${COLOR_BLUE}%s${COLOR_RESET}\n" "$separator"
        printf "${COLOR_BLUE}[HEADER]${COLOR_RESET} %s %s\n" "$timestamp" "$message"
        printf "${COLOR_BLUE}%s${COLOR_RESET}\n" "$separator"
    else
        printf "%s\n" "$separator"
        printf "[HEADER] %s %s\n" "$timestamp" "$message"
        printf "%s\n" "$separator"
    fi
    echo ""

    # Write to file
    iact_write_to_file ""
    iact_write_to_file "$separator"
    iact_write_to_file "$file_timestamp [HEADER] $message"
    iact_write_to_file "$separator"
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Show current logging configuration
# Usage: iact_show_log_config
iact_show_log_config() {
    echo "IACT Logging Configuration:"
    echo "  Initialized: $IACT_LOGGING_INITIALIZED"
    echo "  Script Name: ${IACT_LOG_SCRIPT_NAME:-[default]}"
    echo "  Log File: ${IACT_LOG_FILE:-[not set]}"
    echo "  File Logging: $IACT_LOG_TO_FILE"
    echo "  Colors: $IACT_LOG_COLORS"
    echo "  Debug Mode: ${DEBUG:-false}"
    if [[ -n "${IACT_CONTEXT:-}" ]]; then
        echo "  Context: $IACT_CONTEXT"
        echo "  Context Dir: ${IACT_CONTEXT_DIR:-[not set]}"
    fi
}

# Get current log file path
# Usage: log_file=$(iact_get_log_file)
iact_get_log_file() {
    echo "$IACT_LOG_FILE"
}

# Check if logging to file is enabled
# Usage: if iact_is_logging_to_file; then ...; fi
iact_is_logging_to_file() {
    [[ "$IACT_LOG_TO_FILE" == "true" ]]
}

# =============================================================================
# COMPATIBILITY ALIASES
# =============================================================================

# Legacy compatibility (without iact_ prefix)
# These can be used for backward compatibility if needed
log_info() { iact_log_info "$@"; }
log_success() { iact_log_success "$@"; }
log_warning() { iact_log_warning "$@"; }
log_error() { iact_log_error "$@"; }
log_debug() { iact_log_debug "$@"; }
log_step() { iact_log_step "$@"; }
log_header() { iact_log_header "$@"; }

# Additional aliases
log_warn() { iact_log_warning "$@"; }
init_logging() { iact_init_logging "$@"; }

# =============================================================================
# ERROR HANDLING HELPERS
# =============================================================================

# Log error and exit
# Usage: iact_log_and_exit 1 "Fatal error occurred"
iact_log_and_exit() {
    local exit_code="${1:-1}"
    local message="${2:-Unknown error occurred}"

    iact_log_error "$message"
    exit "$exit_code"
}

# Execute command and log result
# Usage: iact_log_command_result "apt-get update" "Package cache update"
iact_log_command_result() {
    local command="$1"
    local description="${2:-Command execution}"

    if eval "$command" >/dev/null 2>&1; then
        iact_log_success "$description completed successfully"
        return 0
    else
        local exit_code=$?
        iact_log_error "$description failed (exit code: $exit_code)"
        return $exit_code
    fi
}

# =============================================================================
# TESTING FUNCTIONS
# =============================================================================

# Test all logging functions
# Usage: iact_test_logging
iact_test_logging() {
    iact_log_header "Testing IACT Logging System"
    iact_log_info "This is an info message"
    iact_log_success "This is a success message"
    iact_log_warning "This is a warning message"
    iact_log_error "This is an error message"
    iact_log_debug "This is a debug message (only visible with DEBUG=true)"
    iact_log_step "1" "5" "This is step 1 of 5"
    iact_log_step "2" "5" "This is step 2 of 5"
    iact_show_log_config

    if iact_is_logging_to_file; then
        iact_log_info "Log file location: $(iact_get_log_file)"
    else
        iact_log_warning "File logging is disabled"
    fi
}

# =============================================================================
# AUTO-INITIALIZATION - IDEMPOTENT PATTERN
# =============================================================================

# Initialize logging step
_iact_auto_init_logging() {
    local init_step="$1"
    local init_total="$2"

    # Auto-initialize with default settings
    # Scripts can call iact_init_logging("script_name") later to customize
    if ! iact_init_logging; then
        echo "[ERROR] Failed to initialize logging system" >&2
        return 1
    fi

    return 0
}

# Array de pasos de inicialización
_LOGGING_INIT_STEPS=(
    _iact_auto_init_logging
)

# Main initialization function with auto-execution pattern
_init_logging_main() {
    local total_steps=${#_LOGGING_INIT_STEPS[@]}
    local current_step=0

    for step_function in "${_LOGGING_INIT_STEPS[@]}"; do
        ((current_step++))

        if ! $step_function $current_step $total_steps; then
            echo "[ERROR] Logging initialization failed at: $step_function" >&2
            return 1
        fi
    done

    # Success: all steps completed
    return 0
}

# Execute initialization immediately when logging.sh is sourced
# This runs ONLY if not already initialized (idempotent)
if [[ "$IACT_LOGGING_INITIALIZED" != "true" ]]; then
    if ! _init_logging_main; then
        echo "[FATAL] Logging module initialization failed" >&2
        exit 1
    fi
fi