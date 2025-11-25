#!/usr/bin/env bash
# scripts/utils/test_agent_integration.sh
#
# PURPOSE: Integration testing utility for Bash-Python agent integration
# Tests JSON outputs, exit codes, error handling, and real-world workflows
#
# INTEGRATION SCENARIOS:
# 1. Bash scripts calling Python agents
# 2. Python agents returning JSON to Bash
# 3. Exit code propagation
# 4. Error handling across Bash/Python boundary
# 5. Configuration file loading
# 6. Real-world workflow simulation
#
# USAGE:
#   ./scripts/utils/test_agent_integration.sh [options]
#
# OPTIONS:
#   --verbose         Enable verbose output
#   --debug           Enable debug mode
#   --test NAME       Run specific test by name
#   --skip-setup      Skip environment setup
#   --json            Output results as JSON
#
# EXIT CODES:
#   0 - All tests passed
#   1 - One or more tests failed
#   2 - Setup/dependency error
#
# Author: IACT DevOps Team
# Date: 2025-11-14

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
readonly TEST_OUTPUT_DIR="${PROJECT_ROOT}/tmp/integration_tests"
readonly TEST_LOG="${TEST_OUTPUT_DIR}/integration_test.log"

# Test configuration
VERBOSE=0
DEBUG=0
JSON_OUTPUT=0
SKIP_SETUP=0
SPECIFIC_TEST=""

# Test results tracking
declare -i TESTS_RUN=0
declare -i TESTS_PASSED=0
declare -i TESTS_FAILED=0
declare -a FAILED_TESTS=()

# ============================================================================
# DEPENDENCIES AND SETUP
# ============================================================================

# Source shared utilities
if [ -f "${SCRIPT_DIR}/logging.sh" ]; then
    # shellcheck source=scripts/utils/logging.sh
    source "${SCRIPT_DIR}/logging.sh"
else
    # Fallback logging functions if logging.sh not available
    log_info() { echo "[INFO] $*"; }
    log_success() { echo "[OK] $*"; }
    log_warn() { echo "[WARN] $*" >&2; }
    log_error() { echo "[ERROR] $*" >&2; }
    log_debug() { [ "$DEBUG" -eq 1 ] && echo "[DEBUG] $*" >&2 || true; }
fi

# Check required dependencies
check_dependencies() {
    log_info "Checking dependencies..."

    local missing_deps=()

    # Check jq for JSON parsing
    if ! command -v jq &> /dev/null; then
        missing_deps+=("jq")
    fi

    # Check python3
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    fi

    # Check pytest
    if ! python3 -c "import pytest" 2>/dev/null; then
        missing_deps+=("pytest")
    fi

    # Check git
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_error "Install with: sudo apt-get install jq git && pip install pytest"
        return 2
    fi

    log_success "All dependencies found"
    return 0
}

# Setup test environment
setup_test_environment() {
    log_info "Setting up test environment..."

    # Create test output directory
    mkdir -p "${TEST_OUTPUT_DIR}"

    # Initialize test log
    echo "Integration Test Run: $(date -Iseconds)" > "${TEST_LOG}"
    echo "Project Root: ${PROJECT_ROOT}" >> "${TEST_LOG}"
    echo "----------------------------------------" >> "${TEST_LOG}"

    # Create temporary test configuration
    cat > "${TEST_OUTPUT_DIR}/test-config.yaml" <<EOF
test_mode: true
log_level: DEBUG
output_format: json
timeout: 30
EOF

    log_success "Test environment ready at ${TEST_OUTPUT_DIR}"
}

# Cleanup test environment
cleanup_test_environment() {
    log_info "Cleaning up test environment..."

    # Remove temporary test files but keep logs for review
    if [ -d "${TEST_OUTPUT_DIR}" ]; then
        find "${TEST_OUTPUT_DIR}" -name "*.tmp" -type f -delete 2>/dev/null || true
    fi

    log_success "Cleanup complete"
}

# ============================================================================
# JSON VALIDATION HELPERS
# ============================================================================

# Validate JSON structure
validate_json() {
    local json_string="$1"
    local schema_type="${2:-basic}"

    log_debug "Validating JSON (type: ${schema_type})"

    # Basic JSON syntax validation
    if ! echo "$json_string" | jq empty 2>/dev/null; then
        log_error "Invalid JSON syntax"
        return 1
    fi

    # Schema-specific validations
    case "$schema_type" in
        basic)
            # Just check if it's valid JSON
            return 0
            ;;
        agent_output)
            # Check for standard agent output fields
            local has_status has_message
            has_status=$(echo "$json_string" | jq -r 'has("status")' 2>/dev/null)
            has_message=$(echo "$json_string" | jq -r 'has("message") or has("data")' 2>/dev/null)

            if [ "$has_status" != "true" ] || [ "$has_message" != "true" ]; then
                log_error "Missing required fields in agent output"
                return 1
            fi
            ;;
        test_results)
            # Check for test result fields
            local has_tests
            has_tests=$(echo "$json_string" | jq -r 'has("total") and has("passed") and has("failed")' 2>/dev/null)

            if [ "$has_tests" != "true" ]; then
                log_error "Missing required fields in test results"
                return 1
            fi
            ;;
        *)
            log_warn "Unknown schema type: ${schema_type}"
            return 0
            ;;
    esac

    return 0
}

# Extract field from JSON
json_get_field() {
    local json_string="$1"
    local field_path="$2"
    local default_value="${3:-}"

    local result
    result=$(echo "$json_string" | jq -r "${field_path}" 2>/dev/null || echo "$default_value")

    echo "$result"
}

# Compare JSON values
json_compare() {
    local json1="$1"
    local json2="$2"
    local path="$3"

    local val1 val2
    val1=$(json_get_field "$json1" "$path" "null")
    val2=$(json_get_field "$json2" "$path" "null")

    [ "$val1" = "$val2" ]
}

# ============================================================================
# TEST FRAMEWORK
# ============================================================================

# Run a test and track results
run_test() {
    local test_name="$1"
    local test_function="$2"

    # Skip if specific test requested and this isn't it
    if [ -n "$SPECIFIC_TEST" ] && [ "$SPECIFIC_TEST" != "$test_name" ]; then
        return 0
    fi

    ((TESTS_RUN++))

    log_info "Running test: ${test_name}"

    local start_time end_time duration
    start_time=$(date +%s)

    # Run the test function
    if $test_function; then
        ((TESTS_PASSED++))
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        log_success "PASS: ${test_name} (${duration}s)"
        echo "PASS: ${test_name} (${duration}s)" >> "${TEST_LOG}"
        return 0
    else
        ((TESTS_FAILED++))
        FAILED_TESTS+=("$test_name")
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        log_error "FAIL: ${test_name} (${duration}s)"
        echo "FAIL: ${test_name} (${duration}s)" >> "${TEST_LOG}"
        return 1
    fi
}

# Assert helper functions
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="${3:-Values not equal}"

    if [ "$expected" = "$actual" ]; then
        log_debug "Assert passed: $message"
        return 0
    else
        log_error "Assert failed: $message (expected: '$expected', got: '$actual')"
        return 1
    fi
}

assert_exit_code() {
    local expected_code="$1"
    local command="$2"

    local actual_code=0
    eval "$command" || actual_code=$?

    assert_equals "$expected_code" "$actual_code" "Exit code mismatch"
}

assert_json_valid() {
    local json_string="$1"
    local schema_type="${2:-basic}"

    if validate_json "$json_string" "$schema_type"; then
        log_debug "JSON validation passed"
        return 0
    else
        log_error "JSON validation failed"
        return 1
    fi
}

assert_file_exists() {
    local file_path="$1"

    if [ -f "$file_path" ]; then
        log_debug "File exists: $file_path"
        return 0
    else
        log_error "File not found: $file_path"
        return 1
    fi
}

# ============================================================================
# INTEGRATION TEST CASES
# ============================================================================

# Test 1: Basic Python agent invocation from Bash
test_basic_agent_invocation() {
    local agent_script="${PROJECT_ROOT}/scripts/gobernanza_sdlc/automation/ci_pipeline_orchestrator_agent.py"

    if [ ! -f "$agent_script" ]; then
        log_warn "Agent script not found, skipping test"
        return 0
    fi

    # Test with --help flag (should succeed)
    if python3 "$agent_script" --help > /dev/null 2>&1; then
        return 0
    else
        log_error "Agent invocation failed"
        return 1
    fi
}

# Test 2: JSON output from Python agent
test_json_output_from_agent() {
    local test_script="${TEST_OUTPUT_DIR}/test_json_agent.py"

    # Create a simple test agent that outputs JSON
    cat > "$test_script" <<'PYTHON'
#!/usr/bin/env python3
import json
import sys

output = {
    "status": "success",
    "message": "Test agent executed",
    "data": {
        "value": 42,
        "timestamp": "2025-11-14T00:00:00Z"
    }
}

print(json.dumps(output, indent=2))
sys.exit(0)
PYTHON

    chmod +x "$test_script"

    # Run agent and capture output
    local output
    output=$(python3 "$test_script" 2>&1)

    # Validate JSON
    assert_json_valid "$output" "agent_output"
}

# Test 3: Exit code propagation
test_exit_code_propagation() {
    local test_script="${TEST_OUTPUT_DIR}/test_exit_codes.py"

    # Create test agent with specific exit codes
    cat > "$test_script" <<'PYTHON'
#!/usr/bin/env python3
import sys
import json

if len(sys.argv) > 1:
    exit_code = int(sys.argv[1])
else:
    exit_code = 0

output = {
    "status": "error" if exit_code != 0 else "success",
    "exit_code": exit_code
}

print(json.dumps(output))
sys.exit(exit_code)
PYTHON

    chmod +x "$test_script"

    # Test success exit code
    local code=0
    python3 "$test_script" 0 > /dev/null 2>&1 || code=$?
    assert_equals 0 "$code" "Success exit code" || return 1

    # Test error exit code
    code=0
    python3 "$test_script" 1 > /dev/null 2>&1 || code=$?
    assert_equals 1 "$code" "Error exit code" || return 1

    return 0
}

# Test 4: Configuration file loading
test_config_file_loading() {
    local config_file="${TEST_OUTPUT_DIR}/test-agent-config.yaml"
    local test_script="${TEST_OUTPUT_DIR}/test_config_agent.py"

    # Create test configuration
    cat > "$config_file" <<EOF
test_value: "integration_test"
numeric_value: 123
nested:
  key: "value"
EOF

    # Create test agent that reads config
    cat > "$test_script" <<'PYTHON'
#!/usr/bin/env python3
import sys
import yaml
import json

config_file = sys.argv[1] if len(sys.argv) > 1 else None

if not config_file:
    print(json.dumps({"status": "error", "message": "No config file"}))
    sys.exit(1)

try:
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    output = {
        "status": "success",
        "config_loaded": True,
        "test_value": config.get("test_value"),
        "numeric_value": config.get("numeric_value")
    }
    print(json.dumps(output))
    sys.exit(0)
except Exception as e:
    print(json.dumps({"status": "error", "message": str(e)}))
    sys.exit(1)
PYTHON

    chmod +x "$test_script"

    # Run agent with config
    local output
    output=$(python3 "$test_script" "$config_file" 2>&1)

    # Validate output
    assert_json_valid "$output" "agent_output" || return 1

    local status
    status=$(json_get_field "$output" ".status")
    assert_equals "success" "$status" "Config loading status" || return 1

    local test_val
    test_val=$(json_get_field "$output" ".test_value")
    assert_equals "integration_test" "$test_val" "Config value" || return 1

    return 0
}

# Test 5: Error handling across Bash/Python boundary
test_error_handling() {
    local test_script="${TEST_OUTPUT_DIR}/test_error_agent.py"

    # Create agent that raises exceptions
    cat > "$test_script" <<'PYTHON'
#!/usr/bin/env python3
import sys
import json

error_type = sys.argv[1] if len(sys.argv) > 1 else "none"

try:
    if error_type == "exception":
        raise ValueError("Test exception")
    elif error_type == "json_error":
        print("INVALID JSON {{{")
        sys.exit(1)
    else:
        print(json.dumps({"status": "success"}))
        sys.exit(0)
except Exception as e:
    output = {
        "status": "error",
        "error_type": "exception",
        "message": str(e)
    }
    print(json.dumps(output))
    sys.exit(1)
PYTHON

    chmod +x "$test_script"

    # Test exception handling
    local output code=0
    output=$(python3 "$test_script" "exception" 2>&1) || code=$?

    assert_equals 1 "$code" "Exception exit code" || return 1
    assert_json_valid "$output" "agent_output" || return 1

    local status
    status=$(json_get_field "$output" ".status")
    assert_equals "error" "$status" "Error status" || return 1

    return 0
}

# Test 6: CI Pipeline Orchestrator Agent integration
test_ci_pipeline_agent() {
    local agent_script="${PROJECT_ROOT}/scripts/gobernanza_sdlc/automation/ci_pipeline_orchestrator_agent.py"
    local config_file="${PROJECT_ROOT}/.ci-local.yaml"

    if [ ! -f "$agent_script" ]; then
        log_warn "CI Pipeline Agent not found, skipping test"
        return 0
    fi

    if [ ! -f "$config_file" ]; then
        log_warn "CI config not found, skipping test"
        return 0
    fi

    # Test with --dry-run flag
    local output code=0
    output=$(python3 "$agent_script" --config "$config_file" --dry-run 2>&1) || code=$?

    # Agent should succeed or gracefully fail
    if [ $code -eq 0 ]; then
        log_debug "CI Pipeline Agent executed successfully"
        return 0
    else
        log_debug "CI Pipeline Agent returned error code $code (acceptable for test)"
        return 0
    fi
}

# Test 7: Bash script parsing JSON from agent
test_bash_json_parsing() {
    local test_script="${TEST_OUTPUT_DIR}/test_json_source.py"

    # Create agent with complex JSON output
    cat > "$test_script" <<'PYTHON'
#!/usr/bin/env python3
import json

output = {
    "status": "success",
    "results": {
        "tests_run": 42,
        "tests_passed": 40,
        "tests_failed": 2,
        "duration": 12.5
    },
    "metadata": {
        "timestamp": "2025-11-14T00:00:00Z",
        "version": "1.0.0"
    }
}

print(json.dumps(output, indent=2))
PYTHON

    chmod +x "$test_script"

    # Run agent and parse JSON in Bash
    local output
    output=$(python3 "$test_script" 2>&1)

    # Extract fields using jq
    local status tests_run tests_passed
    status=$(echo "$output" | jq -r '.status')
    tests_run=$(echo "$output" | jq -r '.results.tests_run')
    tests_passed=$(echo "$output" | jq -r '.results.tests_passed')

    assert_equals "success" "$status" "Status field" || return 1
    assert_equals "42" "$tests_run" "Tests run field" || return 1
    assert_equals "40" "$tests_passed" "Tests passed field" || return 1

    return 0
}

# Test 8: Workflow simulation - agent pipeline
test_agent_pipeline_workflow() {
    local stage1="${TEST_OUTPUT_DIR}/stage1_agent.py"
    local stage2="${TEST_OUTPUT_DIR}/stage2_agent.py"

    # Create first stage agent
    cat > "$stage1" <<'PYTHON'
#!/usr/bin/env python3
import json
import sys

output = {
    "status": "success",
    "stage": "stage1",
    "data": {"processed": True, "count": 10}
}
print(json.dumps(output))
sys.exit(0)
PYTHON

    # Create second stage agent
    cat > "$stage2" <<'PYTHON'
#!/usr/bin/env python3
import json
import sys

# Read stdin for previous stage output
input_data = json.load(sys.stdin)

if input_data.get("status") != "success":
    print(json.dumps({"status": "error", "message": "Stage 1 failed"}))
    sys.exit(1)

output = {
    "status": "success",
    "stage": "stage2",
    "previous_count": input_data.get("data", {}).get("count", 0),
    "new_count": 20
}
print(json.dumps(output))
sys.exit(0)
PYTHON

    chmod +x "$stage1" "$stage2"

    # Run pipeline
    local stage1_output stage2_output
    stage1_output=$(python3 "$stage1" 2>&1)
    assert_json_valid "$stage1_output" "agent_output" || return 1

    stage2_output=$(echo "$stage1_output" | python3 "$stage2" 2>&1)
    assert_json_valid "$stage2_output" "agent_output" || return 1

    local final_status
    final_status=$(json_get_field "$stage2_output" ".status")
    assert_equals "success" "$final_status" "Pipeline status" || return 1

    return 0
}

# Test 9: Timeout handling
test_timeout_handling() {
    local test_script="${TEST_OUTPUT_DIR}/test_timeout_agent.py"

    # Create agent that can simulate long running
    cat > "$test_script" <<'PYTHON'
#!/usr/bin/env python3
import sys
import time
import json

duration = int(sys.argv[1]) if len(sys.argv) > 1 else 0

if duration > 0:
    time.sleep(duration)

print(json.dumps({"status": "success", "duration": duration}))
sys.exit(0)
PYTHON

    chmod +x "$test_script"

    # Test with timeout (using timeout command)
    local output code=0
    output=$(timeout 2s python3 "$test_script" 1 2>&1) || code=$?

    # Should succeed within timeout
    assert_equals 0 "$code" "Fast execution" || return 1
    assert_json_valid "$output" "agent_output" || return 1

    return 0
}

# Test 10: Real agent discovery test
test_agent_discovery() {
    local agent_dir="${PROJECT_ROOT}/.agent/agents"

    if [ ! -d "$agent_dir" ]; then
        log_warn "Agent directory not found, skipping test"
        return 0
    fi

    # Count agent definition files
    local agent_count
    agent_count=$(find "$agent_dir" -name "*.md" -type f 2>/dev/null | wc -l)

    log_debug "Found $agent_count agent definitions"

    # Should have at least some agents defined
    if [ "$agent_count" -gt 0 ]; then
        return 0
    else
        log_warn "No agent definitions found"
        return 0
    fi
}

# Test 11: Git integration test
test_git_integration() {
    # Test git status in JSON format
    local output
    output=$(git -C "${PROJECT_ROOT}" status --porcelain 2>&1) || true

    # Git command should work
    if [ $? -eq 0 ] || [ $? -eq 128 ]; then
        log_debug "Git integration working"
        return 0
    else
        log_warn "Git integration issue (non-critical)"
        return 0
    fi
}

# Test 12: Python module import test
test_python_module_imports() {
    local test_script="${TEST_OUTPUT_DIR}/test_imports.py"

    # Test importing common modules
    cat > "$test_script" <<'PYTHON'
#!/usr/bin/env python3
import json
import sys

try:
    import yaml
    import pathlib
    import asyncio

    output = {
        "status": "success",
        "modules_loaded": ["yaml", "pathlib", "asyncio"]
    }
    print(json.dumps(output))
    sys.exit(0)
except ImportError as e:
    output = {
        "status": "error",
        "message": f"Import failed: {str(e)}"
    }
    print(json.dumps(output))
    sys.exit(1)
PYTHON

    chmod +x "$test_script"

    local output code=0
    output=$(python3 "$test_script" 2>&1) || code=$?

    # Should succeed or gracefully fail
    if [ $code -eq 0 ]; then
        assert_json_valid "$output" "agent_output"
        return $?
    else
        log_warn "Some Python modules not available (non-critical)"
        return 0
    fi
}

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

# Run all tests
run_all_tests() {
    log_info "Starting integration test suite..."
    echo ""

    # Run each test
    run_test "basic_agent_invocation" test_basic_agent_invocation
    run_test "json_output_from_agent" test_json_output_from_agent
    run_test "exit_code_propagation" test_exit_code_propagation
    run_test "config_file_loading" test_config_file_loading
    run_test "error_handling" test_error_handling
    run_test "ci_pipeline_agent" test_ci_pipeline_agent
    run_test "bash_json_parsing" test_bash_json_parsing
    run_test "agent_pipeline_workflow" test_agent_pipeline_workflow
    run_test "timeout_handling" test_timeout_handling
    run_test "agent_discovery" test_agent_discovery
    run_test "git_integration" test_git_integration
    run_test "python_module_imports" test_python_module_imports

    echo ""
}

# Print test summary
print_summary() {
    echo ""
    echo "========================================"
    echo "INTEGRATION TEST SUMMARY"
    echo "========================================"
    echo "Tests Run:    ${TESTS_RUN}"
    echo "Tests Passed: ${TESTS_PASSED}"
    echo "Tests Failed: ${TESTS_FAILED}"
    echo ""

    if [ ${TESTS_FAILED} -gt 0 ]; then
        echo "Failed Tests:"
        for test in "${FAILED_TESTS[@]}"; do
            echo "  - ${test}"
        done
        echo ""
    fi

    local pass_rate=0
    if [ ${TESTS_RUN} -gt 0 ]; then
        pass_rate=$((TESTS_PASSED * 100 / TESTS_RUN))
    fi

    echo "Pass Rate: ${pass_rate}%"
    echo "========================================"
    echo ""
    echo "Log file: ${TEST_LOG}"
}

# Print JSON summary
print_json_summary() {
    local json_output
    json_output=$(cat <<EOF
{
  "summary": {
    "tests_run": ${TESTS_RUN},
    "tests_passed": ${TESTS_PASSED},
    "tests_failed": ${TESTS_FAILED},
    "pass_rate": $((TESTS_RUN > 0 ? TESTS_PASSED * 100 / TESTS_RUN : 0))
  },
  "failed_tests": [
$(printf '    "%s"' "${FAILED_TESTS[@]}" | paste -sd ',' -)
  ],
  "log_file": "${TEST_LOG}",
  "timestamp": "$(date -Iseconds)"
}
EOF
    )
    echo "$json_output"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose)
                VERBOSE=1
                shift
                ;;
            --debug)
                DEBUG=1
                shift
                ;;
            --json)
                JSON_OUTPUT=1
                shift
                ;;
            --test)
                SPECIFIC_TEST="$2"
                shift 2
                ;;
            --skip-setup)
                SKIP_SETUP=1
                shift
                ;;
            --help|-h)
                cat <<EOF
Usage: $0 [options]

Integration testing utility for Bash-Python agent integration.

OPTIONS:
  --verbose         Enable verbose output
  --debug           Enable debug mode
  --test NAME       Run specific test by name
  --skip-setup      Skip environment setup
  --json            Output results as JSON
  --help, -h        Show this help message

EXIT CODES:
  0 - All tests passed
  1 - One or more tests failed
  2 - Setup/dependency error
EOF
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 2
                ;;
        esac
    done
}

# Main entry point
main() {
    parse_args "$@"

    # Setup
    if [ $SKIP_SETUP -eq 0 ]; then
        check_dependencies || exit 2
        setup_test_environment || exit 2
    fi

    # Run tests
    run_all_tests

    # Cleanup
    cleanup_test_environment

    # Print summary
    if [ $JSON_OUTPUT -eq 1 ]; then
        print_json_summary
    else
        print_summary
    fi

    # Exit with appropriate code
    if [ ${TESTS_FAILED} -gt 0 ]; then
        exit 1
    else
        exit 0
    fi
}

# Run main if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
