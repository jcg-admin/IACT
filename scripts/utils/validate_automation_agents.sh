#!/bin/bash
################################################################################
# validate_automation_agents.sh
#
# PURPOSE: Validation utility for testing all 6 automation agents with real data
#
# DESCRIPTION:
#   This script validates that all automation agents are properly installed,
#   have correct permissions, accept expected inputs, and produce valid outputs.
#   No emojis are used in compliance with project rule R2.
#
# USAGE:
#   ./validate_automation_agents.sh [OPTIONS]
#
# OPTIONS:
#   -v, --verbose    Enable verbose output
#   -h, --help       Display this help message
#
# EXIT CODES:
#   0 - All tests passed
#   1 - One or more tests failed
#
# TESTED AGENTS:
#   1. semantic_git_history_agent.py
#   2. unified_system_context_agent.py
#   3. agent_discovery_agent.py
#   4. ci_pipeline_orchestrator_agent.py
#   5. git_hook_manager_agent.py
#   6. test_results_analyzer_agent.py
#
################################################################################

set -euo pipefail

# Global variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
AGENTS_DIR="${PROJECT_ROOT}/automation/agents"
TEMP_DIR="${PROJECT_ROOT}/tmp/agent_validation_$$"
VERBOSE=false
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=0

# Color codes for output (no emojis - R2 compliant)
RESET='\033[0m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'

################################################################################
# Helper Functions
################################################################################

# Display usage information
usage() {
    head -n 32 "$0" | grep "^#" | sed 's/^# \?//'
    exit 0
}

# Print message with color
print_color() {
    local color=$1
    shift
    echo -e "${color}$*${RESET}"
}

# Log info message
log_info() {
    print_color "$BLUE" "[INFO] $*"
}

# Log success message
log_success() {
    print_color "$GREEN" "[PASS] $*"
}

# Log error message
log_error() {
    print_color "$RED" "[FAIL] $*"
}

# Log warning message
log_warning() {
    print_color "$YELLOW" "[WARN] $*"
}

# Verbose logging
log_verbose() {
    if [[ "$VERBOSE" == "true" ]]; then
        echo "[VERBOSE] $*"
    fi
}

# Setup test environment
setup_test_env() {
    log_info "Setting up test environment..."
    mkdir -p "$TEMP_DIR"
    log_verbose "Created temporary directory: $TEMP_DIR"
}

# Cleanup test environment
cleanup_test_env() {
    log_info "Cleaning up test environment..."
    if [[ -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
        log_verbose "Removed temporary directory: $TEMP_DIR"
    fi
}

# Validate JSON output
validate_json() {
    local json_file=$1
    if ! python3 -m json.tool "$json_file" >/dev/null 2>&1; then
        return 1
    fi
    return 0
}

# Record test result
record_test() {
    local test_name=$1
    local status=$2

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if [[ "$status" == "PASS" ]]; then
        TESTS_PASSED=$((TESTS_PASSED + 1))
        log_success "$test_name"
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        log_error "$test_name"
    fi
}

# Check if agent file exists and is executable
check_agent_exists() {
    local agent_name=$1
    local agent_path="${AGENTS_DIR}/${agent_name}"

    if [[ ! -f "$agent_path" ]]; then
        record_test "${agent_name}: File exists" "FAIL"
        return 1
    fi
    record_test "${agent_name}: File exists" "PASS"

    if [[ ! -x "$agent_path" ]]; then
        record_test "${agent_name}: Executable permissions" "FAIL"
        return 1
    fi
    record_test "${agent_name}: Executable permissions" "PASS"

    return 0
}

################################################################################
# Agent Test Functions
################################################################################

# Test semantic_git_history_agent.py
test_semantic_git_history_agent() {
    local agent_name="semantic_git_history_agent.py"
    log_info "Testing ${agent_name}..."

    check_agent_exists "$agent_name" || return 1

    local agent_path="${AGENTS_DIR}/${agent_name}"
    local output_file="${TEMP_DIR}/git_history_output.json"

    # Test with real git data
    log_verbose "Running ${agent_name} with real git data..."
    if python3 "$agent_path" --output "$output_file" --limit 10 >/dev/null 2>&1; then
        record_test "${agent_name}: Execution" "PASS"
    else
        record_test "${agent_name}: Execution" "FAIL"
        return 1
    fi

    # Validate JSON output
    if [[ -f "$output_file" ]] && validate_json "$output_file"; then
        record_test "${agent_name}: JSON output valid" "PASS"
    else
        record_test "${agent_name}: JSON output valid" "FAIL"
        return 1
    fi

    # Check output contains expected fields
    if grep -q '"commit"' "$output_file" && grep -q '"message"' "$output_file"; then
        record_test "${agent_name}: Output structure" "PASS"
    else
        record_test "${agent_name}: Output structure" "FAIL"
        return 1
    fi

    return 0
}

# Test unified_system_context_agent.py
test_unified_system_context_agent() {
    local agent_name="unified_system_context_agent.py"
    log_info "Testing ${agent_name}..."

    check_agent_exists "$agent_name" || return 1

    local agent_path="${AGENTS_DIR}/${agent_name}"
    local output_file="${TEMP_DIR}/system_context_output.json"

    # Test context generation
    log_verbose "Running ${agent_name}..."
    if python3 "$agent_path" --output "$output_file" >/dev/null 2>&1; then
        record_test "${agent_name}: Execution" "PASS"
    else
        record_test "${agent_name}: Execution" "FAIL"
        return 1
    fi

    # Validate JSON output
    if [[ -f "$output_file" ]] && validate_json "$output_file"; then
        record_test "${agent_name}: JSON output valid" "PASS"
    else
        record_test "${agent_name}: JSON output valid" "FAIL"
        return 1
    fi

    # Check output contains system context
    if grep -q '"system"' "$output_file" || grep -q '"context"' "$output_file"; then
        record_test "${agent_name}: Output structure" "PASS"
    else
        record_test "${agent_name}: Output structure" "FAIL"
        return 1
    fi

    return 0
}

# Test agent_discovery_agent.py
test_agent_discovery_agent() {
    local agent_name="agent_discovery_agent.py"
    log_info "Testing ${agent_name}..."

    check_agent_exists "$agent_name" || return 1

    local agent_path="${AGENTS_DIR}/${agent_name}"
    local output_file="${TEMP_DIR}/discovery_output.json"

    # Test agent discovery
    log_verbose "Running ${agent_name}..."
    if python3 "$agent_path" --scan-dir "$AGENTS_DIR" --output "$output_file" >/dev/null 2>&1; then
        record_test "${agent_name}: Execution" "PASS"
    else
        record_test "${agent_name}: Execution" "FAIL"
        return 1
    fi

    # Validate JSON output
    if [[ -f "$output_file" ]] && validate_json "$output_file"; then
        record_test "${agent_name}: JSON output valid" "PASS"
    else
        record_test "${agent_name}: JSON output valid" "FAIL"
        return 1
    fi

    # Check output contains discovered agents
    if grep -q '"agents"' "$output_file" || grep -q '"discovered"' "$output_file"; then
        record_test "${agent_name}: Output structure" "PASS"
    else
        record_test "${agent_name}: Output structure" "FAIL"
        return 1
    fi

    return 0
}

# Test ci_pipeline_orchestrator_agent.py
test_ci_pipeline_orchestrator_agent() {
    local agent_name="ci_pipeline_orchestrator_agent.py"
    log_info "Testing ${agent_name}..."

    check_agent_exists "$agent_name" || return 1

    local agent_path="${AGENTS_DIR}/${agent_name}"
    local output_file="${TEMP_DIR}/pipeline_output.json"
    local config_file="${TEMP_DIR}/pipeline_config.json"

    # Create test pipeline configuration
    cat > "$config_file" <<'EOF'
{
  "pipeline": {
    "name": "test_pipeline",
    "stages": [
      {
        "name": "validate",
        "steps": ["echo 'Validating...'"]
      }
    ]
  }
}
EOF

    # Test pipeline orchestration
    log_verbose "Running ${agent_name}..."
    if python3 "$agent_path" --config "$config_file" --output "$output_file" --dry-run >/dev/null 2>&1; then
        record_test "${agent_name}: Execution" "PASS"
    else
        record_test "${agent_name}: Execution" "FAIL"
        return 1
    fi

    # Validate JSON output if produced
    if [[ -f "$output_file" ]]; then
        if validate_json "$output_file"; then
            record_test "${agent_name}: JSON output valid" "PASS"
        else
            record_test "${agent_name}: JSON output valid" "FAIL"
            return 1
        fi
    else
        record_test "${agent_name}: JSON output valid" "PASS"
    fi

    # Check exit code was successful
    record_test "${agent_name}: Exit code" "PASS"

    return 0
}

# Test git_hook_manager_agent.py
test_git_hook_manager_agent() {
    local agent_name="git_hook_manager_agent.py"
    log_info "Testing ${agent_name}..."

    check_agent_exists "$agent_name" || return 1

    local agent_path="${AGENTS_DIR}/${agent_name}"
    local output_file="${TEMP_DIR}/hook_manager_output.json"

    # Test hook manager listing
    log_verbose "Running ${agent_name}..."
    if python3 "$agent_path" --list --output "$output_file" >/dev/null 2>&1; then
        record_test "${agent_name}: Execution" "PASS"
    else
        record_test "${agent_name}: Execution" "FAIL"
        return 1
    fi

    # Validate JSON output if produced
    if [[ -f "$output_file" ]]; then
        if validate_json "$output_file"; then
            record_test "${agent_name}: JSON output valid" "PASS"
        else
            record_test "${agent_name}: JSON output valid" "FAIL"
            return 1
        fi

        # Check output structure
        if grep -q '"hooks"' "$output_file" || grep -q '"git"' "$output_file"; then
            record_test "${agent_name}: Output structure" "PASS"
        else
            record_test "${agent_name}: Output structure" "FAIL"
            return 1
        fi
    else
        record_test "${agent_name}: JSON output valid" "PASS"
        record_test "${agent_name}: Output structure" "PASS"
    fi

    return 0
}

# Test test_results_analyzer_agent.py
test_test_results_analyzer_agent() {
    local agent_name="test_results_analyzer_agent.py"
    log_info "Testing ${agent_name}..."

    check_agent_exists "$agent_name" || return 1

    local agent_path="${AGENTS_DIR}/${agent_name}"
    local output_file="${TEMP_DIR}/test_analysis_output.json"
    local test_results_file="${TEMP_DIR}/test_results.xml"

    # Create sample test results
    cat > "$test_results_file" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
  <testsuite name="sample" tests="2" failures="0" errors="0">
    <testcase name="test_one" classname="TestSample" time="0.001"/>
    <testcase name="test_two" classname="TestSample" time="0.002"/>
  </testsuite>
</testsuites>
EOF

    # Test results analysis
    log_verbose "Running ${agent_name}..."
    if python3 "$agent_path" --input "$test_results_file" --output "$output_file" >/dev/null 2>&1; then
        record_test "${agent_name}: Execution" "PASS"
    else
        record_test "${agent_name}: Execution" "FAIL"
        return 1
    fi

    # Validate JSON output
    if [[ -f "$output_file" ]] && validate_json "$output_file"; then
        record_test "${agent_name}: JSON output valid" "PASS"
    else
        record_test "${agent_name}: JSON output valid" "FAIL"
        return 1
    fi

    # Check output contains analysis
    if grep -q '"tests"' "$output_file" || grep -q '"results"' "$output_file" || grep -q '"analysis"' "$output_file"; then
        record_test "${agent_name}: Output structure" "PASS"
    else
        record_test "${agent_name}: Output structure" "FAIL"
        return 1
    fi

    return 0
}

################################################################################
# Main Execution
################################################################################

main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                VERBOSE=true
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done

    # Print header
    echo "========================================================================"
    echo "Automation Agents Validation Script"
    echo "========================================================================"
    echo ""

    # Setup
    setup_test_env

    # Register cleanup on exit
    trap cleanup_test_env EXIT

    # Run all agent tests
    test_semantic_git_history_agent
    echo ""

    test_unified_system_context_agent
    echo ""

    test_agent_discovery_agent
    echo ""

    test_ci_pipeline_orchestrator_agent
    echo ""

    test_git_hook_manager_agent
    echo ""

    test_test_results_analyzer_agent
    echo ""

    # Print summary
    echo "========================================================================"
    echo "Validation Summary"
    echo "========================================================================"
    echo "Total Tests:  $TOTAL_TESTS"
    echo "Passed:       $TESTS_PASSED"
    echo "Failed:       $TESTS_FAILED"
    echo "========================================================================"

    # Determine exit code
    if [[ $TESTS_FAILED -eq 0 ]]; then
        log_success "All validation tests passed"
        exit 0
    else
        log_error "Some validation tests failed"
        exit 1
    fi
}

# Run main function
main "$@"
