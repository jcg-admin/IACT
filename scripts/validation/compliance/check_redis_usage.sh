#!/bin/bash
# check_redis_usage.sh
# Validator: NO Redis usage (IACT RNF-002 compliance)
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only checks for Redis usage
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - No Redis usage detected
#   1 - CRITICAL: Redis usage detected (violates RNF-002)

set -euo pipefail

# Constants
readonly SCRIPT_NAME="$(basename "$0")"
readonly PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
readonly SETTINGS_PATH="${PROJECT_ROOT}/api/callcentersite"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly NC='\033[0m' # No Color

# Logging functions
log_error() {
    echo -e "${RED}[FAIL]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $*"
}

log_info() {
    echo "[INFO] $*"
}

# Main validation function
check_redis_usage() {
    log_info "Validating NO Redis usage (IACT RNF-002)..."

    if [ ! -d "$SETTINGS_PATH" ]; then
        log_error "Settings path not found: ${SETTINGS_PATH}"
        return 1
    fi

    local redis_found=false

    # Check 1: Look for 'redis' keyword in settings files
    log_info "Checking for 'redis' in settings files..."
    if grep -r "redis" "$SETTINGS_PATH"/settings*.py 2>/dev/null; then
        log_error "Redis detected in settings (PROHIBITED by RNF-002)"
        redis_found=true
    fi

    # Check 2: Look for 'django_redis' package
    log_info "Checking for 'django_redis' package..."
    if grep -r "django_redis" "$SETTINGS_PATH"/settings*.py 2>/dev/null; then
        log_error "django_redis package detected (PROHIBITED by RNF-002)"
        redis_found=true
    fi

    # Check 3: Look for Redis in requirements.txt
    if [ -f "$PROJECT_ROOT/api/requirements.txt" ]; then
        if grep -i "redis" "$PROJECT_ROOT/api/requirements.txt" 2>/dev/null; then
            log_error "Redis package found in requirements.txt (PROHIBITED by RNF-002)"
            redis_found=true
        fi
    fi

    # Final result
    if [ "$redis_found" = true ]; then
        log_error "IACT RNF-002 VIOLATION: Redis is PROHIBITED"
        log_error "Use MySQL for sessions and caching"
        return 1
    else
        log_success "No Redis usage detected - RNF-002 compliant"
        return 0
    fi
}

# Entry point
main() {
    check_redis_usage
}

main "$@"
