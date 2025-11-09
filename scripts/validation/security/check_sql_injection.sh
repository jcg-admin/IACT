#!/bin/bash
# check_sql_injection.sh
# Validator: SQL Injection vulnerabilities detection
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Only checks SQL injection patterns
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - No SQL injection vulnerabilities found
#   1 - CRITICAL: String formatting in SQL queries detected
#   2 - WARNING: Raw SQL queries found (manual review needed)

set -euo pipefail

# Constants
readonly SCRIPT_NAME="$(basename "$0")"
readonly PROJECT_ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
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
check_sql_injection() {
    local exit_code=0

    log_info "Checking for potential SQL injection vulnerabilities in ${BACKEND_PATH}..."

    if [ ! -d "$BACKEND_PATH" ]; then
        log_error "Backend path not found: ${BACKEND_PATH}"
        return 1
    fi

    # Check 1: Look for raw SQL queries (.raw or .execute)
    log_info "Checking for raw SQL queries..."

    local raw_sql_files=""

    # Use explicit exit code handling instead of || true
    if raw_sql_files=$(find "$BACKEND_PATH" -name "*.py" -type f ! -name "test_*.py" ! -name "*_test.py" -exec grep -l "\.raw\|\.execute" {} \; 2>/dev/null); then
        : # Found matches, continue
    elif [ $? -eq 1 ]; then
        : # No matches found (expected, not an error)
    else
        log_error "Error searching for raw SQL (permission denied or I/O error)"
        return 1
    fi

    if [ -n "$raw_sql_files" ]; then
        log_warning "Raw SQL queries found in the following files:"
        echo "$raw_sql_files" | while IFS= read -r file; do
            echo "  - ${file}"
            grep -n "\.raw\|\.execute" "$file" | head -3 || true
        done
        log_warning "Ensure these queries use parameterized statements"
        exit_code=2
    fi

    # Check 2: Look for dangerous string formatting in SQL queries (CRITICAL)
    log_info "Checking for string formatting in SQL queries (f-strings or .format)..."

    local format_sql_files=""

    # Use explicit exit code handling instead of || true
    if format_sql_files=$(find "$BACKEND_PATH" -name "*.py" -type f ! -name "test_*.py" ! -name "*_test.py" -exec grep -l 'f".*SELECT\|\.format.*SELECT' {} \; 2>/dev/null); then
        : # Found matches, continue
    elif [ $? -eq 1 ]; then
        : # No matches found (expected, not an error)
    else
        log_error "Error searching for string formatting in SQL (permission denied or I/O error)"
        return 1
    fi

    if [ -n "$format_sql_files" ]; then
        log_error "String formatting detected in SQL queries (SQL injection risk!)"
        echo "$format_sql_files" | while IFS= read -r file; do
            echo "  - ${file}"
            grep -n 'f".*SELECT\|\.format.*SELECT' "$file" || true
        done
        return 1
    fi

    # Final result
    if [ "$exit_code" -eq 0 ]; then
        log_success "No obvious SQL injection vulnerabilities found"
    elif [ "$exit_code" -eq 2 ]; then
        log_warning "Manual review recommended for raw SQL queries"
    fi

    return "$exit_code"
}

# Entry point
main() {
    check_sql_injection
}

main "$@"
