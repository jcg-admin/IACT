#!/bin/bash
# check_django_security.sh
# Validator: Django security configuration checks (IACT RNF-002 compliance)
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only checks Django security settings
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - All security checks passed
#   1 - CRITICAL: Security misconfiguration detected
#   2 - WARNING: Potential security issues found

set -euo pipefail

# Constants
readonly SCRIPT_NAME="$(basename "$0")"
readonly PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
readonly SETTINGS_FILE="${PROJECT_ROOT}/api/callcentersite/callcentersite/settings.py"
readonly BACKEND_PATH="${PROJECT_ROOT}/api/callcentersite"

# Colors for output
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly GREEN='\033[0;32m'
readonly NC='\033[0m' # No Color

# Logging functions
log_error() {
    echo -e "${RED}[FAIL]${NC} $*" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" >&2
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $*"
}

log_info() {
    echo "[INFO] $*"
}

# Check 1: Run Django deployment checks
run_django_deployment_checks() {
    log_info "Running Django deployment security checks..."

    if [ ! -d "$BACKEND_PATH" ]; then
        log_error "Backend path not found: ${BACKEND_PATH}"
        return 1
    fi

    cd "$BACKEND_PATH" || return 1

    # Run Django's built-in security checks
    if python manage.py check --deploy --settings=callcentersite.settings 2>&1; then
        log_success "Django deployment checks passed"
        return 0
    else
        log_error "Django deployment checks FAILED"
        return 1
    fi
}

# Check 2: Verify DEBUG setting
check_debug_setting() {
    log_info "Checking DEBUG setting in production..."

    if grep -q "DEBUG = True" "$SETTINGS_FILE"; then
        log_warning "DEBUG=True found in settings.py"
        log_warning "Ensure DEBUG is set to False in production environment"
        return 2
    fi

    log_success "DEBUG setting check passed"
    return 0
}

# Check 3: Verify SECRET_KEY is not hardcoded
check_secret_key() {
    log_info "Checking for hardcoded SECRET_KEY..."

    if grep -q 'SECRET_KEY = ["\x27].*["\x27]' "$SETTINGS_FILE"; then
        log_warning "SECRET_KEY appears to be hardcoded in settings.py"
        log_warning "Use environment variable for SECRET_KEY in production"
        return 2
    fi

    log_success "SECRET_KEY check passed"
    return 0
}

# Check 4: Validate session security (IACT RNF-002 compliance)
validate_session_security() {
    log_info "Validating session security (IACT RNF-002)..."

    local exit_code=0

    # IACT RNF-002: Sessions MUST use MySQL backend (NO Redis)
    if ! grep -q "django.contrib.sessions.backends.db" "$SETTINGS_FILE"; then
        log_error "SESSION_ENGINE not set to MySQL/database backend (violates RNF-002)"
        log_error "Required: SESSION_ENGINE = 'django.contrib.sessions.backends.db'"
        exit_code=1
    fi

    # IACT RNF-002: Redis is PROHIBITED
    if grep -q "redis" "$SETTINGS_FILE"; then
        log_error "Redis detected in settings.py (PROHIBITED by RNF-002)"
        log_error "IACT project must NOT use Redis for sessions or caching"
        exit_code=1
    fi

    if [ "$exit_code" -eq 0 ]; then
        log_success "Session security validated (MySQL backend, NO Redis)"
    fi

    return "$exit_code"
}

# Main validation function
check_django_security() {
    local overall_exit_code=0

    log_info "Starting Django security checks..."

    if [ ! -f "$SETTINGS_FILE" ]; then
        log_error "Settings file not found: ${SETTINGS_FILE}"
        return 1
    fi

    # Run all checks
    run_django_deployment_checks || overall_exit_code=$?
    check_debug_setting || { local code=$?; [ "$code" -gt "$overall_exit_code" ] && overall_exit_code=$code; }
    check_secret_key || { local code=$?; [ "$code" -gt "$overall_exit_code" ] && overall_exit_code=$code; }
    validate_session_security || overall_exit_code=$?

    # Final result
    if [ "$overall_exit_code" -eq 0 ]; then
        log_success "All Django security checks passed"
    elif [ "$overall_exit_code" -eq 1 ]; then
        log_error "CRITICAL Django security issues detected"
    elif [ "$overall_exit_code" -eq 2 ]; then
        log_warning "Django security checks completed with warnings"
    fi

    return "$overall_exit_code"
}

# Entry point
main() {
    check_django_security
}

main "$@"
