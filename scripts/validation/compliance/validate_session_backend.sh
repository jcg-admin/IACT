#!/bin/bash
# validate_session_backend.sh
# Validator: Session backend must use MySQL (IACT RNF-002 compliance)
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only validates session backend
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - Session backend correctly configured (MySQL)
#   1 - CRITICAL: Session backend not using MySQL (violates RNF-002)

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
validate_session_backend() {
    log_info "Validating session backend configuration (IACT RNF-002)..."

    if [ ! -d "$SETTINGS_PATH" ]; then
        log_error "Settings path not found: ${SETTINGS_PATH}"
        return 1
    fi

    # IACT RNF-002: SESSION_ENGINE must be django.contrib.sessions.backends.db (MySQL)
    if ! grep -q "django.contrib.sessions.backends.db" "$SETTINGS_PATH"/settings*.py; then
        log_error "SESSION_ENGINE not set to MySQL/database backend"
        log_error "Required: SESSION_ENGINE = 'django.contrib.sessions.backends.db'"
        log_error "IACT RNF-002: Sessions MUST use MySQL, NOT Redis or other backends"
        return 1
    fi

    log_success "Session backend correctly configured (MySQL) - RNF-002 compliant"
    return 0
}

# Entry point
main() {
    validate_session_backend
}

main "$@"
