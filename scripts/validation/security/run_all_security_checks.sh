#!/bin/bash
# run_all_security_checks.sh
# Orchestrator: Executes all security validation scripts
#
# CONSTITUTION COMPLIANCE:
#   Rule 1: Single Responsibility - Orchestrates security checks only
#   Rule 3: Explicit Error Handling - set -euo pipefail
#   Rule 5: Clean Code Naming - Descriptive function and variable names
#
# EXIT CODES:
#   0 - All security checks passed
#   1 - CRITICAL security checks failed
#   2 - Warnings found (manual review needed)

set -euo pipefail

# Constants
readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Colors for output
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Logging functions
log_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}$*${NC}"
    echo -e "${BLUE}======================================${NC}"
}

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

# Run a single security check
run_security_check() {
    local check_name="$1"
    local check_script="$2"

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    echo ""
    log_header "[${TOTAL_CHECKS}] Running: ${check_name}"

    if [ ! -x "$check_script" ]; then
        log_error "Script not executable: ${check_script}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi

    local exit_code=0
    "$check_script" || exit_code=$?

    case $exit_code in
        0)
            log_success "${check_name} passed"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            ;;
        1)
            log_error "${check_name} FAILED (CRITICAL)"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            ;;
        2)
            log_warning "${check_name} completed with warnings"
            WARNING_CHECKS=$((WARNING_CHECKS + 1))
            ;;
        *)
            log_error "${check_name} returned unexpected exit code: ${exit_code}"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            ;;
    esac

    return $exit_code
}

# Main orchestration function
run_all_security_checks() {
    log_header "IACT Security Validation Suite"
    log_info "Starting comprehensive security checks..."
    log_info "Project root: ${PROJECT_ROOT}"

    # Define all security checks
    # Format: "Display Name" "script_path"
    local -a checks=(
        "SQL Injection Check|${SCRIPT_DIR}/check_sql_injection.sh"
        "XSS Protection Check|${SCRIPT_DIR}/check_xss_protection.sh"
        "CSRF Protection Check|${SCRIPT_DIR}/check_csrf_protection.sh"
        "Django Security Check|${SCRIPT_DIR}/check_django_security.sh"
    )

    # Track critical failures
    local critical_failed=false

    # Run all checks
    for check in "${checks[@]}"; do
        IFS='|' read -r name script <<< "$check"

        local check_exit=0
        run_security_check "$name" "$script" || check_exit=$?

        # Track critical failures (exit code 1)
        if [ "$check_exit" -eq 1 ]; then
            critical_failed=true
        fi
    done

    # Print summary
    echo ""
    log_header "Security Validation Summary"
    echo "Total checks:    ${TOTAL_CHECKS}"
    echo -e "${GREEN}Passed:${NC}          ${PASSED_CHECKS}"
    echo -e "${YELLOW}Warnings:${NC}        ${WARNING_CHECKS}"
    echo -e "${RED}Failed:${NC}          ${FAILED_CHECKS}"

    # Determine final exit code
    if [ "$critical_failed" = true ]; then
        echo ""
        log_error "CRITICAL security checks FAILED"
        log_error "Fix all critical issues before proceeding"
        return 1
    elif [ "$WARNING_CHECKS" -gt 0 ]; then
        echo ""
        log_warning "Some security checks completed with warnings"
        log_warning "Manual review recommended"
        return 2
    else
        echo ""
        log_success "All security checks PASSED"
        return 0
    fi
}

# Entry point
main() {
    run_all_security_checks
}

main "$@"
