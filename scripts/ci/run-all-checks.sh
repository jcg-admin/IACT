#!/bin/bash
# run-all-checks.sh
#
# Master CI/CD script - Runs all checks in proper order
# Replaces ALL GitHub Actions with shell scripts
#
# Usage:
#   ./run-all-checks.sh [--fail-fast] [--verbose] [--only infrastructure|security|testing]
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed

set -u
set -o pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_section() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Parse arguments
FAIL_FAST=false
VERBOSE=false
ONLY_SUITE=""

for arg in "$@"; do
    case $arg in
        --fail-fast) FAIL_FAST=true ;;
        --verbose) VERBOSE=true ;;
        --only)
            shift
            ONLY_SUITE="$1"
            shift
            ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

log_info "Starting CI/CD Pipeline"
log_info "Project: IACT - Sistema de Permisos"
log_info "Mode: $([ "$FAIL_FAST" = true ] && echo "Fail-fast" || echo "Run all")"

declare -a RESULTS
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
SKIPPED_CHECKS=0

run_check() {
    local check_name=$1
    local check_script=$2
    local suite=$3

    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

    log_section "$check_name"

    if [ ! -f "$check_script" ]; then
        log_error "Script not found: $check_script"
        RESULTS+=("[$suite] $check_name: SKIP (script missing)")
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
        return 1
    fi

    chmod +x "$check_script"

    local exit_code
    local output=""
    local previous_errexit=0

    if [[ $- == *e* ]]; then
        previous_errexit=1
        set +e
    fi

    if [ "$VERBOSE" = true ]; then
        "$check_script"
        exit_code=$?
    else
        output=$("$check_script" 2>&1)
        exit_code=$?
    fi

    if [ $previous_errexit -eq 1 ]; then
        set -e
    fi

    if [ "$VERBOSE" != true ] && [ $exit_code -ne 0 ] && [ -n "$output" ]; then
        echo "$output"
    fi

    if [ $exit_code -eq 0 ]; then
        log_info "$check_name: PASS"
        RESULTS+=("[$suite] $check_name: PASS")
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
        return 0
    elif [ $exit_code -eq 2 ]; then
        log_warn "$check_name: SKIP (not applicable)"
        RESULTS+=("[$suite] $check_name: SKIP")
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
        return 0
    else
        log_error "$check_name: FAIL (exit code: $exit_code)"
        RESULTS+=("[$suite] $check_name: FAIL")
        FAILED_CHECKS=$((FAILED_CHECKS + 1))

        if [ "$FAIL_FAST" = true ]; then
            log_error "Stopping due to failure (--fail-fast enabled)"
            exit 1
        fi

        return 1
    fi
}

# ===========================================
# INFRASTRUCTURE CI SUITE
# ===========================================

if [ -z "$ONLY_SUITE" ] || [ "$ONLY_SUITE" = "infrastructure" ]; then
    log_section "INFRASTRUCTURE CI SUITE"

    run_check "Health Check Scripts" "$SCRIPT_DIR/infrastructure/health-check.sh" "Infrastructure"
    run_check "Validate Scripts" "$SCRIPT_DIR/infrastructure/validate-scripts.sh" "Infrastructure"
    run_check "Validate Configuration" "$SCRIPT_DIR/infrastructure/validate-config.sh" "Infrastructure"
    run_check "Validate Docker" "$SCRIPT_DIR/infrastructure/validate-docker.sh" "Infrastructure"
fi

# ===========================================
# SECURITY SCAN SUITE
# ===========================================

if [ -z "$ONLY_SUITE" ] || [ "$ONLY_SUITE" = "security" ]; then
    log_section "SECURITY SCAN SUITE"

    run_check "CSRF Protection Check" "$SCRIPT_DIR/security/csrf-check.sh" "Security"
    run_check "Django Security Check" "$SCRIPT_DIR/security/django-security-check.sh" "Security"
    run_check "Bandit Security Scan" "$SCRIPT_DIR/security/bandit-scan.sh" "Security"
    run_check "NPM Security Audit" "$SCRIPT_DIR/security/npm-audit.sh" "Security"
fi

# ===========================================
# TEST PYRAMID VALIDATION SUITE
# ===========================================

if [ -z "$ONLY_SUITE" ] || [ "$ONLY_SUITE" = "testing" ]; then
    log_section "TEST PYRAMID VALIDATION SUITE"

    run_check "Analyze Test Pyramid" "$SCRIPT_DIR/testing/test-pyramid.sh" "Testing"
    run_check "Validate Test Execution Time" "$SCRIPT_DIR/testing/test-execution-time.sh" "Testing"
fi

# ===========================================
# PROMPTOPS GATES SUITE
# ===========================================

if [ -z "$ONLY_SUITE" ] || [ "$ONLY_SUITE" = "promptops" ]; then
    log_section "PROMPTOPS GATES SUITE"

    run_check "Route Lint Gate" "$SCRIPT_DIR/gate-route-lint.sh" "PromptOps"
    # Future gates:
    # run_check "Audit Contract Gate" "$SCRIPT_DIR/gate-audit-contract.sh" "PromptOps"
    # run_check "Permission Coverage Gate" "$SCRIPT_DIR/gate-permission-coverage.sh" "PromptOps"
fi

# ===========================================
# FINAL REPORT
# ===========================================

log_section "FINAL CI/CD REPORT"

echo ""
echo "Total Checks:   $TOTAL_CHECKS"
echo -e "${GREEN}Passed:         $PASSED_CHECKS${NC}"
echo -e "${RED}Failed:         $FAILED_CHECKS${NC}"
echo -e "${YELLOW}Skipped:        $SKIPPED_CHECKS${NC}"
echo ""

log_info "Individual Results:"
for result in "${RESULTS[@]}"; do
    if [[ $result == *"PASS"* ]]; then
        echo -e "  ${GREEN}[OK]${NC} $result"
    elif [[ $result == *"FAIL"* ]]; then
        echo -e "  ${RED}[ERROR]${NC} $result"
    else
        echo -e "  ${YELLOW}[SKIP]${NC} $result"
    fi
done

echo ""

if [ $FAILED_CHECKS -eq 0 ]; then
    log_info "All checks passed!"
    echo ""
    log_info "Ready to merge"
    exit 0
else
    log_error "$FAILED_CHECKS check(s) failed"
    echo ""
    log_error "Please fix failing checks before merging"
    exit 1
fi
