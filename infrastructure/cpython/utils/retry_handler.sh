#!/bin/bash
# utils/retry_handler.sh - Retry logic and error handling for CPython Builder
# Reference: SPEC_INFRA_001
# Purpose: Robust retry mechanisms with error classification and circuit breaker

set -euo pipefail

# =============================================================================
# DEPENDENCIES
# =============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/logger.sh"

# =============================================================================
# CONSTANTS
# =============================================================================

readonly DEFAULT_MAX_RETRIES=3
readonly DEFAULT_INITIAL_DELAY=2
readonly DEFAULT_MAX_DELAY=60
readonly DEFAULT_BACKOFF_MULTIPLIER=2

# Error type constants
readonly ERROR_TYPE_TRANSIENT=1
readonly ERROR_TYPE_RECOVERABLE=2
readonly ERROR_TYPE_FATAL=3
readonly ERROR_TYPE_UNKNOWN=4

# Circuit breaker states
readonly CIRCUIT_STATE_CLOSED=0
readonly CIRCUIT_STATE_OPEN=1
readonly CIRCUIT_STATE_HALF_OPEN=2

# Circuit breaker configuration
readonly CIRCUIT_FAILURE_THRESHOLD=5
readonly CIRCUIT_RESET_TIMEOUT=60
readonly CIRCUIT_STATE_FILE="/tmp/circuit_breaker_state"

# =============================================================================
# ERROR CLASSIFICATION
# =============================================================================

# Classify error based on exit code and output
# Args: $1 - exit code, $2 - command output/error message
# Returns: ERROR_TYPE_* constant
# Example: classify_error_type 1 "Connection timed out"
classify_error_type() {
    local exit_code="$1"
    local output="$2"

    # Transient errors (network, temporary failures)
    if echo "$output" | grep -qiE "timeout|temporary failure|connection.*refused|network.*unreachable|no route to host"; then
        log_debug "Classified as TRANSIENT error"
        return $ERROR_TYPE_TRANSIENT
    fi

    if echo "$output" | grep -qiE "connection.*reset|broken pipe|socket.*closed"; then
        log_debug "Classified as TRANSIENT error"
        return $ERROR_TYPE_TRANSIENT
    fi

    # Recoverable errors (resource constraints, locks)
    if echo "$output" | grep -qiE "no space left|disk full|quota exceeded"; then
        log_debug "Classified as RECOVERABLE error"
        return $ERROR_TYPE_RECOVERABLE
    fi

    if echo "$output" | grep -qiE "dpkg.*lock|apt.*lock|resource.*busy|device.*busy"; then
        log_debug "Classified as RECOVERABLE error"
        return $ERROR_TYPE_RECOVERABLE
    fi

    # Fatal errors (permissions, missing dependencies)
    if echo "$output" | grep -qiE "permission denied|access denied|forbidden"; then
        log_debug "Classified as FATAL error"
        return $ERROR_TYPE_FATAL
    fi

    if echo "$output" | grep -qiE "not found|no such file|command not found|cannot execute"; then
        log_debug "Classified as FATAL error"
        return $ERROR_TYPE_FATAL
    fi

    if echo "$output" | grep -qiE "syntax error|parse error|invalid.*format"; then
        log_debug "Classified as FATAL error"
        return $ERROR_TYPE_FATAL
    fi

    # Special exit codes
    case $exit_code in
        127|126)
            # Command not found or not executable
            log_debug "Classified as FATAL error (exit code: $exit_code)"
            return $ERROR_TYPE_FATAL
            ;;
        137|143)
            # SIGKILL or SIGTERM
            log_debug "Classified as TRANSIENT error (killed by signal)"
            return $ERROR_TYPE_TRANSIENT
            ;;
    esac

    # Default: treat as transient (optimistic retry)
    log_debug "Classified as UNKNOWN error (will retry)"
    return $ERROR_TYPE_UNKNOWN
}

# Check if error type is retryable
# Args: $1 - error type (from classify_error_type)
# Returns: 0 if retryable, 1 if not
# Example: is_error_retryable $ERROR_TYPE_TRANSIENT
is_error_retryable() {
    local error_type="$1"

    case $error_type in
        $ERROR_TYPE_TRANSIENT|$ERROR_TYPE_RECOVERABLE|$ERROR_TYPE_UNKNOWN)
            return 0
            ;;
        $ERROR_TYPE_FATAL)
            return 1
            ;;
        *)
            return 0  # Optimistic: retry by default
            ;;
    esac
}

# =============================================================================
# BACKOFF STRATEGIES
# =============================================================================

# Calculate exponential backoff delay
# Args: $1 - attempt number (0-indexed), $2 - initial delay, $3 - max delay, $4 - multiplier
# Returns: Delay in seconds (via stdout)
# Example: delay=$(calculate_exponential_backoff 2 2 60 2)
calculate_exponential_backoff() {
    local attempt="$1"
    local initial_delay="${2:-$DEFAULT_INITIAL_DELAY}"
    local max_delay="${3:-$DEFAULT_MAX_DELAY}"
    local multiplier="${4:-$DEFAULT_BACKOFF_MULTIPLIER}"

    local delay=$initial_delay
    local i=0

    while (( i < attempt )); do
        delay=$((delay * multiplier))
        i=$((i + 1))
    done

    # Cap at max delay
    if (( delay > max_delay )); then
        delay=$max_delay
    fi

    echo "$delay"
}

# Apply jitter to delay (randomize ±20%)
# Args: $1 - base delay in seconds
# Returns: Jittered delay (via stdout)
# Example: jittered=$(apply_jitter_to_delay 10)
apply_jitter_to_delay() {
    local base_delay="$1"

    # Calculate jitter range (±20%)
    local jitter_range=$((base_delay / 5))

    # Generate random jitter (-jitter_range to +jitter_range)
    local jitter=$((RANDOM % (jitter_range * 2 + 1) - jitter_range))

    local final_delay=$((base_delay + jitter))

    # Ensure non-negative
    if (( final_delay < 0 )); then
        final_delay=0
    fi

    echo "$final_delay"
}

# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

# Initialize circuit breaker state
# Args: None
# Returns: 0 on success
initialize_circuit_breaker() {
    echo "$CIRCUIT_STATE_CLOSED:0:$(date +%s)" > "$CIRCUIT_STATE_FILE"
    log_debug "Circuit breaker initialized"
}

# Get circuit breaker state
# Returns: Circuit state via stdout (CLOSED, OPEN, HALF_OPEN)
get_circuit_breaker_state() {
    if [[ ! -f "$CIRCUIT_STATE_FILE" ]]; then
        initialize_circuit_breaker
    fi

    local state
    state=$(cut -d: -f1 "$CIRCUIT_STATE_FILE")
    echo "$state"
}

# Record operation failure for circuit breaker
# Args: None
# Returns: 0 if circuit should remain closed, 1 if should open
record_operation_failure() {
    if [[ ! -f "$CIRCUIT_STATE_FILE" ]]; then
        initialize_circuit_breaker
    fi

    local state failure_count timestamp
    IFS=: read -r state failure_count timestamp < "$CIRCUIT_STATE_FILE"

    failure_count=$((failure_count + 1))

    if (( failure_count >= CIRCUIT_FAILURE_THRESHOLD )); then
        state=$CIRCUIT_STATE_OPEN
        log_warning "Circuit breaker opened after $failure_count failures"
    fi

    echo "$state:$failure_count:$(date +%s)" > "$CIRCUIT_STATE_FILE"

    if (( state == CIRCUIT_STATE_OPEN )); then
        return 1
    fi

    return 0
}

# Record operation success for circuit breaker
# Args: None
# Returns: 0 always
record_operation_success() {
    if [[ ! -f "$CIRCUIT_STATE_FILE" ]]; then
        initialize_circuit_breaker
        return 0
    fi

    # Reset to closed state with zero failures
    echo "$CIRCUIT_STATE_CLOSED:0:$(date +%s)" > "$CIRCUIT_STATE_FILE"
    log_debug "Circuit breaker reset after success"
}

# Check if circuit breaker allows operation
# Returns: 0 if operation allowed, 1 if blocked
check_circuit_breaker_allows_operation() {
    if [[ ! -f "$CIRCUIT_STATE_FILE" ]]; then
        initialize_circuit_breaker
        return 0
    fi

    local state failure_count timestamp
    IFS=: read -r state failure_count timestamp < "$CIRCUIT_STATE_FILE"

    case $state in
        $CIRCUIT_STATE_CLOSED)
            return 0
            ;;
        $CIRCUIT_STATE_OPEN)
            local now
            now=$(date +%s)
            local elapsed=$((now - timestamp))

            if (( elapsed >= CIRCUIT_RESET_TIMEOUT )); then
                log_info "Circuit breaker entering HALF_OPEN state"
                echo "$CIRCUIT_STATE_HALF_OPEN:$failure_count:$now" > "$CIRCUIT_STATE_FILE"
                return 0
            fi

            log_warning "Circuit breaker is OPEN, blocking operation"
            return 1
            ;;
        $CIRCUIT_STATE_HALF_OPEN)
            return 0
            ;;
        *)
            return 0
            ;;
    esac
}

# Reset circuit breaker to closed state
# Args: None
# Returns: 0 always
reset_circuit_breaker() {
    initialize_circuit_breaker
    log_info "Circuit breaker manually reset"
}

# =============================================================================
# RETRY EXECUTION
# =============================================================================

# Execute command with retry logic
# Args: $1 - max attempts, $2 - operation name, $3+ - command and arguments
# Returns: 0 on success, 1 on failure after all retries
# Example: execute_with_retry 3 "Download file" wget -O file.tgz https://example.com/file.tgz
execute_with_retry() {
    local max_attempts="$1"
    local operation_name="$2"
    shift 2
    local cmd=("$@")

    local attempt=0
    local initial_delay=$DEFAULT_INITIAL_DELAY

    log_info "Starting operation: $operation_name (max attempts: $max_attempts)"

    while (( attempt < max_attempts )); do
        # Check circuit breaker
        if ! check_circuit_breaker_allows_operation; then
            log_error "Circuit breaker blocking operation: $operation_name"
            return 1
        fi

        attempt=$((attempt + 1))
        log_info "[$operation_name] Attempt $attempt/$max_attempts"

        # Execute command
        local output
        local exit_code

        if output=$("${cmd[@]}" 2>&1); then
            exit_code=0
            log_info "[$operation_name] Success on attempt $attempt"
            record_operation_success
            return 0
        else
            exit_code=$?
        fi

        # Command failed, classify error
        local error_type
        classify_error_type "$exit_code" "$output"
        error_type=$?

        log_error "[$operation_name] Failed with exit code $exit_code"
        log_debug "Error output: $output"

        # Check if error is retryable
        if ! is_error_retryable "$error_type"; then
            log_error "[$operation_name] Fatal error detected, aborting retries"
            record_operation_failure
            return 1
        fi

        # Calculate delay if more attempts remain
        if (( attempt < max_attempts )); then
            local base_delay
            base_delay=$(calculate_exponential_backoff $((attempt - 1)) "$initial_delay" "$DEFAULT_MAX_DELAY" "$DEFAULT_BACKOFF_MULTIPLIER")

            local delay
            delay=$(apply_jitter_to_delay "$base_delay")

            log_warning "[$operation_name] Retrying in ${delay}s..."
            sleep "$delay"
        else
            record_operation_failure
        fi
    done

    log_error "[$operation_name] Failed after $max_attempts attempts"
    return 1
}

# Execute command with simple retry (no circuit breaker)
# Args: $1 - max attempts, $2 - operation name, $3+ - command and arguments
# Returns: 0 on success, 1 on failure
# Example: execute_with_simple_retry 3 "Test connection" ping -c 1 google.com
execute_with_simple_retry() {
    local max_attempts="$1"
    local operation_name="$2"
    shift 2
    local cmd=("$@")

    local attempt=0

    while (( attempt < max_attempts )); do
        attempt=$((attempt + 1))

        if "${cmd[@]}" >/dev/null 2>&1; then
            log_debug "[$operation_name] Success on attempt $attempt"
            return 0
        fi

        if (( attempt < max_attempts )); then
            log_debug "[$operation_name] Failed, retry $attempt/$max_attempts"
            sleep 2
        fi
    done

    log_error "[$operation_name] Failed after $max_attempts attempts"
    return 1
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

# Get recommended retry count based on error type
# Args: $1 - error type
# Returns: Recommended retry count (via stdout)
get_recommended_retry_count() {
    local error_type="$1"

    case $error_type in
        $ERROR_TYPE_TRANSIENT)
            echo 5
            ;;
        $ERROR_TYPE_RECOVERABLE)
            echo 3
            ;;
        $ERROR_TYPE_FATAL)
            echo 0
            ;;
        *)
            echo 3
            ;;
    esac
}

# Wait with progress indicator
# Args: $1 - seconds to wait, $2 - optional message
# Returns: 0 always
wait_with_progress() {
    local seconds="$1"
    local message="${2:-Waiting}"

    log_info "$message ($seconds seconds)..."

    local i=0
    while (( i < seconds )); do
        sleep 1
        i=$((i + 1))
        if (( i % 10 == 0 )); then
            log_debug "  ... $i seconds elapsed"
        fi
    done
}