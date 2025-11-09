#!/bin/bash
# check_xss_protection.sh
# Validator: XSS (Cross-Site Scripting) vulnerabilities detection
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only checks XSS patterns
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - No XSS vulnerabilities found
#   2 - WARNING: Potential XSS risks found (manual review needed)

set -euo pipefail

# Constants
readonly SCRIPT_NAME="$(basename "$0")"
readonly PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
readonly BACKEND_PATH="${PROJECT_ROOT}/api/callcentersite"
readonly FRONTEND_PATH="${PROJECT_ROOT}/frontend"

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
check_xss_protection() {
    local warnings_found=0

    log_info "Checking for potential XSS vulnerabilities..."

    # Check 1: Unescaped template variables in Django templates
    log_info "Checking Django templates for unescaped variables..."

    if [ -d "$BACKEND_PATH" ]; then
        local unsafe_templates
        unsafe_templates=$(find "$BACKEND_PATH" -name "*.html" -type f ! -path "*/node_modules/*" -exec grep -l "|safe\|{% autoescape off %}" {} \; 2>/dev/null || true)

        if [ -n "$unsafe_templates" ]; then
            log_warning "Unescaped template variables found in Django templates:"
            echo "$unsafe_templates" | while IFS= read -r file; do
                echo "  - ${file}"
                grep -n "|safe\|{% autoescape off %}" "$file" | head -2 || true
            done
            log_warning "Review these files for potential XSS vulnerabilities"
            warnings_found=1
        fi
    fi

    # Check 2: Dangerous React patterns (dangerouslySetInnerHTML)
    log_info "Checking React components for dangerouslySetInnerHTML..."

    if [ -d "$FRONTEND_PATH/src" ]; then
        local dangerous_react
        dangerous_react=$(grep -r "dangerouslySetInnerHTML" "$FRONTEND_PATH/src/" 2>/dev/null || true)

        if [ -n "$dangerous_react" ]; then
            log_warning "dangerouslySetInnerHTML found in React components:"
            echo "$dangerous_react" | while IFS= read -r line; do
                echo "  ${line}"
            done
            log_warning "Ensure HTML content is properly sanitized before rendering"
            warnings_found=1
        fi
    fi

    # Final result
    if [ "$warnings_found" -eq 0 ]; then
        log_success "No XSS vulnerabilities detected"
        return 0
    else
        log_warning "XSS check completed with warnings - manual review required"
        return 2
    fi
}

# Entry point
main() {
    check_xss_protection
}

main "$@"
