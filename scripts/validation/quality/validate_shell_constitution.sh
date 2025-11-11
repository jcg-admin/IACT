#!/bin/bash
# scripts/validation/quality/validate_shell_constitution.sh
# Validates that shell scripts comply with SHELL_SCRIPTS_CONSTITUTION.md
# Reference: SHELL_SCRIPTS_CONSTITUTION.md v1.0.0

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Source common functions
if [ -f "$PROJECT_ROOT/scripts/lib/common.sh" ]; then
    source "$PROJECT_ROOT/scripts/lib/common.sh"
fi
if [ -f "$PROJECT_ROOT/scripts/lib/exit_codes.sh" ]; then
    source "$PROJECT_ROOT/scripts/lib/exit_codes.sh"
else
    EXIT_SUCCESS=0
    EXIT_FAIL=1
    EXIT_WARNING=2
fi

# Colors fallback
log_info() { echo "[INFO] $*"; }
log_success() { echo "[SUCCESS] $*"; }
log_error() { echo "[ERROR] $*" >&2; }
log_warning() { echo "[WARNING] $*" >&2; }

# ============================================================================
# VALIDATION FUNCTIONS (one per rule)
# ============================================================================

# RULE 1: Single Responsibility Principle
# Validates that module has only ONE domain/responsibility
validate_rule_1_single_responsibility() {
    local script="$1"

    log_info "[RULE 1] Validating single responsibility..."

    # Extract function names and count different domains
    local function_domains
    function_domains=$(grep -oP '^[a-z_]+(?=\()' "$script" 2>/dev/null | \
        cut -d'_' -f1 | \
        sort -u | \
        wc -l)

    if [ "$function_domains" -gt 2 ]; then
        log_error "VIOLATION: Module has $function_domains different domains (max: 1-2)"
        log_error "Functions should belong to one conceptual domain"
        return 1
    fi

    log_success "Single responsibility OK"
    return 0
}

# RULE 2: Backward Compatibility
# Checks for breaking changes (difficult to automate fully)
validate_rule_2_backward_compatibility() {
    local script="$1"

    log_info "[RULE 2] Checking backward compatibility markers..."

    # Check for DEPRECATED markers (good practice)
    if grep -q "DEPRECATED" "$script"; then
        log_success "Deprecated functions properly marked"
    fi

    # Warning if removing public functions (needs manual review)
    log_info "Backward compatibility requires manual review of changes"
    log_info "Ensure deprecated functions have wrappers to new names"

    return 0
}

# RULE 3: Explicit Error Handling
# CRITICAL: set -e, no silent errors
validate_rule_3_explicit_error_handling() {
    local script="$1"

    log_info "[RULE 3] Validating explicit error handling..."

    local violations=0

    # Check 1: set -e must be present
    if ! grep -q 'set -e' "$script"; then
        log_error "VIOLATION: Missing 'set -e' (or 'set -euo pipefail')"
        violations=$((violations + 1))
    fi

    # Check 2: NO silent errors with || true
    if grep -P '\|\|\s*true' "$script"; then
        log_error "VIOLATION: Silent error detected with '|| true'"
        log_error "Lines:"
        grep -n '\|\|\s*true' "$script"
        violations=$((violations + 1))
    fi

    # Check 3: || should have explicit handling
    local unhandled_errors
    unhandled_errors=$(grep -P '\|\|(?!\s+(echo|log_error|log_warning|return|exit))' "$script" || true)
    if [ -n "$unhandled_errors" ]; then
        log_warning "Possible unhandled errors (review manually):"
        echo "$unhandled_errors"
    fi

    if [ $violations -eq 0 ]; then
        log_success "Explicit error handling OK"
        return 0
    else
        return 1
    fi
}

# RULE 4: Tests Without External Dependencies
# Checks if script imports/uses external services
validate_rule_4_tests_without_deps() {
    local script="$1"

    # Only validate test files
    if [[ "$script" != *test*.sh ]]; then
        log_info "[RULE 4] Skipping (not a test file)"
        return 0
    fi

    log_info "[RULE 4] Checking for external dependencies in tests..."

    local violations=0

    # Check for network calls without mocks
    if grep -E 'curl |wget |http://' "$script" | grep -qv 'mock'; then
        log_warning "Possible network dependency (ensure mocked)"
        violations=$((violations + 1))
    fi

    # Check for database connections
    if grep -E 'mysql |psql |mongo ' "$script" | grep -qv 'mock'; then
        log_warning "Possible database dependency (ensure mocked)"
        violations=$((violations + 1))
    fi

    if [ $violations -eq 0 ]; then
        log_success "No external dependencies detected"
    else
        log_warning "Review test for external dependencies"
    fi

    return 0  # Warning only, not blocking
}

# RULE 5: Clean Code Naming
# Validates function names follow Clean Code principles
validate_rule_5_clean_code_naming() {
    local script="$1"

    log_info "[RULE 5] Validating Clean Code naming..."

    local violations=0

    # Check for common abbreviations
    local bad_abbrevs
    bad_abbrevs=$(grep -oP '^(validate|check|get|set)_(dir|usr|proc|exec|val|tmp|str|int|chk)(?=_|\()' "$script" || true)
    if [ -n "$bad_abbrevs" ]; then
        log_warning "Possible abbreviations detected:"
        echo "$bad_abbrevs" | sort -u
        log_warning "Consider full names: dir->directory, usr->user, proc->process"
    fi

    # Check for very short function names (< 3 chars before first underscore)
    local short_names
    short_names=$(grep -oP '^[a-z_]{1,2}(?=\()' "$script" || true)
    if [ -n "$short_names" ]; then
        log_error "VIOLATION: Function names too short (< 3 chars):"
        echo "$short_names"
        violations=$((violations + 1))
    fi

    # Check for Hungarian notation (str_, int_, etc.)
    if grep -qE '^(str|int|bool|arr)_[a-z_]+=' "$script"; then
        log_warning "Possible Hungarian notation detected (avoid type prefixes)"
    fi

    if [ $violations -eq 0 ]; then
        log_success "Clean Code naming OK"
        return 0
    else
        return 1
    fi
}

# RULE 6: Size Limits
# Module < 200 lines, functions < 50 lines
validate_rule_6_size_limits() {
    local script="$1"

    log_info "[RULE 6] Validating size limits..."

    local violations=0

    # Check module size
    local lines
    lines=$(wc -l < "$script")

    if [ "$lines" -gt 200 ]; then
        log_error "VIOLATION: Module too large: $lines lines (max: 200)"
        violations=$((violations + 1))
    else
        log_success "Module size OK: $lines lines"
    fi

    # Check function sizes
    local large_functions
    large_functions=$(awk '
        /^[a-z_]+\(\)/ {
            fname=$1
            start=NR
        }
        /^}$/ && fname != "" {
            size=NR-start
            if (size > 50) {
                print fname " " size " lines"
            }
            fname=""
        }
    ' "$script")

    if [ -n "$large_functions" ]; then
        log_error "VIOLATION: Functions too large (max: 50 lines):"
        echo "$large_functions"
        violations=$((violations + 1))
    else
        log_success "Function sizes OK"
    fi

    if [ $violations -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# RULE 7: Inline Documentation
# All public functions must have documentation
validate_rule_7_inline_documentation() {
    local script="$1"

    log_info "[RULE 7] Checking inline documentation..."

    # Count functions
    local func_count
    func_count=$(grep -cE '^[a-z_]+\(\)' "$script" || echo 0)

    if [ "$func_count" -eq 0 ]; then
        log_info "No functions found, skipping documentation check"
        return 0
    fi

    # Count documented functions (those with Args: or Returns: before them)
    local doc_count
    doc_count=$(grep -cE '^# (Args:|Returns:|Example:)' "$script" || echo 0)

    # Calculate coverage
    local coverage=0
    if [ "$func_count" -gt 0 ]; then
        coverage=$((doc_count * 100 / func_count))
    fi

    log_info "Documentation coverage: $coverage% ($doc_count/$func_count functions)"

    if [ "$coverage" -lt 50 ]; then
        log_warning "Low documentation coverage (target: 80%)"
        return 0  # Warning only
    else
        log_success "Documentation coverage acceptable"
        return 0
    fi
}

# RULE 8: Idempotence Where Applicable
# Check for idempotence markers and patterns
validate_rule_8_idempotence() {
    local script="$1"

    log_info "[RULE 8] Checking idempotence patterns..."

    # Look for good idempotence patterns
    local idempotent_patterns=0

    # Check for "if [ ! -d" pattern (ensure_directory_exists style)
    if grep -q 'if \[ ! -d' "$script"; then
        idempotent_patterns=$((idempotent_patterns + 1))
    fi

    # Check for "if ! grep -q" pattern (ensure_line_in_file style)
    if grep -q 'if ! grep -q' "$script"; then
        idempotent_patterns=$((idempotent_patterns + 1))
    fi

    # Check for mkdir -p (idempotent directory creation)
    if grep -q 'mkdir -p' "$script"; then
        idempotent_patterns=$((idempotent_patterns + 1))
    fi

    if [ $idempotent_patterns -gt 0 ]; then
        log_success "Idempotent patterns detected: $idempotent_patterns"
    else
        log_info "No obvious idempotent patterns (may not be required)"
    fi

    return 0  # Not blocking
}

# ============================================================================
# MAIN VALIDATION
# ============================================================================

validate_script() {
    local script="$1"

    if [ ! -f "$script" ]; then
        log_error "Script not found: $script"
        return 1
    fi

    echo ""
    echo "========================================"
    echo "VALIDATING: $(basename "$script")"
    echo "========================================"
    echo ""

    local critical_failed=0
    local high_failed=0
    local warnings=0

    # CRITICAL RULES (block merge)
    validate_rule_1_single_responsibility "$script" || critical_failed=$((critical_failed + 1))
    echo ""

    validate_rule_2_backward_compatibility "$script" || critical_failed=$((critical_failed + 1))
    echo ""

    validate_rule_3_explicit_error_handling "$script" || critical_failed=$((critical_failed + 1))
    echo ""

    validate_rule_4_tests_without_deps "$script" || warnings=$((warnings + 1))
    echo ""

    # HIGH PRIORITY RULES (require justification)
    validate_rule_5_clean_code_naming "$script" || high_failed=$((high_failed + 1))
    echo ""

    validate_rule_6_size_limits "$script" || high_failed=$((high_failed + 1))
    echo ""

    # MEDIUM PRIORITY RULES (warnings)
    validate_rule_7_inline_documentation "$script" || warnings=$((warnings + 1))
    echo ""

    validate_rule_8_idempotence "$script" || warnings=$((warnings + 1))
    echo ""

    # Summary
    echo "========================================"
    echo "VALIDATION SUMMARY"
    echo "========================================"
    echo "Critical violations: $critical_failed"
    echo "High priority violations: $high_failed"
    echo "Warnings: $warnings"
    echo ""

    if [ $critical_failed -gt 0 ]; then
        log_error "FAILED: $critical_failed CRITICAL violation(s)"
        return 1
    elif [ $high_failed -gt 0 ]; then
        log_warning "PASSED with $high_failed HIGH priority violation(s)"
        log_warning "Justification required for merge"
        return 2  # Exit code 2 = warning
    else
        log_success "PASSED: Script complies with Shell Scripts Constitution"
        return 0
    fi
}

# ============================================================================
# ENTRY POINT
# ============================================================================

main() {
    if [ $# -eq 0 ]; then
        echo "Usage: $0 <shell_script.sh> [<shell_script2.sh> ...]"
        echo ""
        echo "Validates shell scripts against SHELL_SCRIPTS_CONSTITUTION.md"
        echo ""
        echo "Exit codes:"
        echo "  0 - All validations passed"
        echo "  1 - Critical violations (blocks merge)"
        echo "  2 - High priority violations (requires justification)"
        echo ""
        echo "Examples:"
        echo "  $0 utils/logger.sh"
        echo "  $0 utils/*.sh"
        exit 1
    fi

    local total_failed=0
    local total_warnings=0

    for script in "$@"; do
        validate_script "$script"
        local result=$?

        if [ $result -eq 1 ]; then
            total_failed=$((total_failed + 1))
        elif [ $result -eq 2 ]; then
            total_warnings=$((total_warnings + 1))
        fi
    done

    echo ""
    echo "========================================"
    echo "OVERALL SUMMARY"
    echo "========================================"
    echo "Scripts validated: $#"
    echo "Failed (critical): $total_failed"
    echo "Warnings (high): $total_warnings"
    echo "Passed: $(($# - total_failed - total_warnings))"
    echo ""

    if [ $total_failed -gt 0 ]; then
        log_error "VALIDATION FAILED: $total_failed script(s) with critical violations"
        return 1
    elif [ $total_warnings -gt 0 ]; then
        log_warning "VALIDATION PASSED with warnings: $total_warnings script(s)"
        return 2
    else
        log_success "ALL VALIDATIONS PASSED"
        return 0
    fi
}

main "$@"
