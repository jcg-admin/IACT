#!/bin/bash
# check_email_usage.sh
# Validator: Email usage check (should use InternalMessage instead)
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only checks for email usage
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - No prohibited email usage detected
#   2 - WARNING: Email usage detected (should use InternalMessage)

set -euo pipefail

# Constants
readonly SCRIPT_NAME="$(basename "$0")"
readonly PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
readonly BACKEND_PATH="${PROJECT_ROOT}/api/callcentersite"

# Colors for output
readonly YELLOW='\033[1;33m'
readonly GREEN='\033[0;32m'
readonly NC='\033[0m' # No Color

# Logging functions
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
check_email_usage() {
    log_info "Checking for prohibited email usage..."

    if [ ! -d "$BACKEND_PATH" ]; then
        log_warning "Backend path not found: ${BACKEND_PATH}"
        return 2
    fi

    # Look for Django email functions
    # Patterns: send_mail, EmailMessage, EmailMultiAlternatives
    # Exclude lines with "# PROHIBITED" comment (documented violations)
    local email_usage=""

    # Use explicit exit code handling instead of || true
    if email_usage=$(grep -r "send_mail\|EmailMessage\|EmailMultiAlternatives" "$BACKEND_PATH"/*.py 2>/dev/null | grep -v "# PROHIBITED" | grep -v ".pyc"); then
        : # Found matches, continue
    elif [ $? -eq 1 ]; then
        : # No matches found (expected, not an error)
    else
        log_warning "Error searching for email usage (permission denied or I/O error)"
        return 2
    fi

    if [ -n "$email_usage" ]; then
        log_warning "Email usage detected in backend code:"
        echo "$email_usage" | while IFS= read -r line; do
            echo "  ${line}"
        done
        log_warning "IACT project should use InternalMessage system instead of email"
        log_warning "This is a warning, not a blocking error"
        return 2
    fi

    log_success "No prohibited email usage detected"
    return 0
}

# Entry point
main() {
    check_email_usage
}

main "$@"
