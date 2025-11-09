#!/bin/bash
# check_csrf_protection.sh
# Validator: CSRF (Cross-Site Request Forgery) protection verification
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only checks CSRF middleware configuration
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - CSRF protection properly configured
#   1 - CRITICAL: CSRF middleware not enabled
#   2 - WARNING: CSRF exemptions found (manual review needed)

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

# Main validation function
check_csrf_protection() {
    local exit_code=0

    log_info "Checking CSRF protection configuration..."

    # Check 1: Verify CSRF middleware is enabled in settings.py
    log_info "Verifying CSRF middleware in settings.py..."

    if [ ! -f "$SETTINGS_FILE" ]; then
        log_error "Settings file not found: ${SETTINGS_FILE}"
        return 1
    fi

    if ! grep -q "django.middleware.csrf.CsrfViewMiddleware" "$SETTINGS_FILE"; then
        log_error "CSRF middleware (CsrfViewMiddleware) NOT enabled in MIDDLEWARE"
        log_error "Add 'django.middleware.csrf.CsrfViewMiddleware' to MIDDLEWARE in settings.py"
        return 1
    fi

    log_success "CSRF middleware is enabled"

    # Check 2: Look for @csrf_exempt decorators (potential security risks)
    log_info "Checking for @csrf_exempt decorators in views..."

    local csrf_exempt_files
    csrf_exempt_files=$(find "$BACKEND_PATH" -name "*.py" -type f ! -name "test_*.py" ! -name "*_test.py" -exec grep -l "@csrf_exempt" {} \; 2>/dev/null || true)

    if [ -n "$csrf_exempt_files" ]; then
        log_warning "@csrf_exempt decorator found in the following files:"
        echo "$csrf_exempt_files" | while IFS= read -r file; do
            echo "  - ${file}"
            grep -n "@csrf_exempt" "$file" || true
        done
        log_warning "These views bypass CSRF protection - ensure they are properly secured"
        exit_code=2
    fi

    # Final result
    if [ "$exit_code" -eq 0 ]; then
        log_success "CSRF protection properly configured"
    elif [ "$exit_code" -eq 2 ]; then
        log_warning "CSRF protection enabled but exemptions found - manual review recommended"
    fi

    return "$exit_code"
}

# Entry point
main() {
    check_csrf_protection
}

main "$@"
