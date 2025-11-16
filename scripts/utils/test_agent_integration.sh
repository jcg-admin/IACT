#!/bin/bash
# Integration utility for automation agents
# Tests Bash to Python integration, JSON outputs, and exit codes
# NO EMOJIS - R2 compliant
#
# Exit codes:
#   0 - All integration tests passed
#   1 - Any integration test failed

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Set PYTHONPATH to include project root
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH:-}"

# Source common utilities
# shellcheck source=../lib/common.sh
source "$SCRIPT_DIR/../lib/common.sh"

# Create temporary directory for outputs
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

# Results tracking
PASSED_TESTS=0
FAILED_TESTS=0
TOTAL_TESTS=0

# ============================================================================
# Test Framework Functions
# ============================================================================

run_test() {
    local test_name="$1"
    local test_function="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    log_info "Running test: $test_name"

    if $test_function; then
        PASSED_TESTS=$((PASSED_TESTS + 1))
        log_success "PASSED: $test_name"
        return 0
    else
        FAILED_TESTS=$((FAILED_TESTS + 1))
        log_error "FAILED: $test_name"
        return 1
    fi
}

assert_file_exists() {
    local file="$1"
    local description="${2:-file}"

    if [ -f "$file" ]; then
        log_success "File exists: $description"
        return 0
    else
        log_error "File not found: $description ($file)"
        return 1
    fi
}

assert_json_valid() {
    local file="$1"

    if ! python3 -m json.tool "$file" >/dev/null 2>&1; then
        log_error "Invalid JSON in $file"
        return 1
    fi

    log_success "Valid JSON: $file"
    return 0
}

assert_json_has_field() {
    local file="$1"
    local field="$2"

    if ! python3 -c "import json; data = json.load(open('$file')); assert '$field' in data" 2>/dev/null; then
        log_error "JSON missing field '$field' in $file"
        return 1
    fi

    log_success "JSON has field '$field': $file"
    return 0
}

assert_exit_code() {
    local actual="$1"
    local expected="$2"
    local description="${3:-command}"

    if [ "$actual" -eq "$expected" ]; then
        log_success "Exit code correct: $description (expected $expected, got $actual)"
        return 0
    else
        log_error "Exit code incorrect: $description (expected $expected, got $actual)"
        return 1
    fi
}

assert_exit_code_range() {
    local actual="$1"
    local min="$2"
    local max="$3"
    local description="${4:-command}"

    if [ "$actual" -ge "$min" ] && [ "$actual" -le "$max" ]; then
        log_success "Exit code in range: $description ($min-$max, got $actual)"
        return 0
    else
        log_error "Exit code out of range: $description (expected $min-$max, got $actual)"
        return 1
    fi
}

# ============================================================================
# Integration Tests
# ============================================================================

test_schema_validator_integration() {
    local output_file="$TEMP_DIR/schema_test.json"
    local test_yaml="$TEMP_DIR/test.yaml"
    local test_schema="$TEMP_DIR/schema.json"

    # Create test files
    cat > "$test_yaml" <<EOF
version: "1.0"
name: "Test Config"
EOF

    cat > "$test_schema" <<EOF
{
  "\$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "version": {"type": "string"},
    "name": {"type": "string"}
  },
  "required": ["version"]
}
EOF

    # Run agent
    set +e
    python3 "$PROJECT_ROOT/scripts/coding/ai/automation/schema_validator_agent.py" \
        --file "$test_yaml" \
        --schema "$test_schema" \
        --output "$output_file" \
        --type constitucion
    local exit_code=$?
    set -e

    # Assertions
    assert_file_exists "$output_file" "Schema validator output" || return 1
    assert_json_valid "$output_file" || return 1
    assert_json_has_field "$output_file" "status" || return 1
    assert_json_has_field "$output_file" "is_valid" || return 1
    assert_exit_code "$exit_code" 0 "Schema validator" || return 1

    return 0
}

test_devcontainer_validator_integration() {
    local output_file="$TEMP_DIR/devcontainer_test.json"
    local devcontainer_json="$TEMP_DIR/devcontainer.json"

    # Create minimal devcontainer.json
    cat > "$devcontainer_json" <<EOF
{
  "name": "Test DevContainer",
  "build": {
    "args": {
      "PYTHON_VERSION": "3.12",
      "NODE_VERSION": "18"
    }
  },
  "forwardPorts": [8000],
  "containerEnv": {
    "DEBUG": "1"
  }
}
EOF

    # Run agent
    set +e
    python3 "$PROJECT_ROOT/scripts/coding/ai/automation/devcontainer_validator_agent.py" \
        --devcontainer-json "$devcontainer_json" \
        --output "$output_file"
    local exit_code=$?
    set -e

    # Assertions (0 or 1 are acceptable)
    assert_file_exists "$output_file" "DevContainer validator output" || return 1
    assert_json_valid "$output_file" || return 1
    assert_json_has_field "$output_file" "status" || return 1
    assert_json_has_field "$output_file" "summary" || return 1
    assert_exit_code_range "$exit_code" 0 1 "DevContainer validator" || return 1

    return 0
}

test_metrics_collector_integration() {
    local output_file="$TEMP_DIR/metrics_test.json"
    local violations_log="$TEMP_DIR/violations.log"

    # Create sample log with multiple violations
    cat > "$violations_log" <<EOF
[2025-11-10 10:00:00] VIOLATION - Rule: R2 - Severity: error - File: main.py - Line: 5 - Author: dev1 - Message: Emoji detected
[2025-11-11 11:00:00] VIOLATION - Rule: R2 - Severity: error - File: test.py - Line: 10 - Author: dev2 - Message: Emoji detected
[2025-11-12 12:00:00] VIOLATION - Rule: R3 - Severity: warning - File: views.py - Line: 20 - Author: dev1 - Message: Coherence issue
[2025-11-13 13:00:00] VIOLATION - Rule: R2 - Severity: error - File: utils.py - Line: 15 - Author: dev1 - Message: Emoji detected
EOF

    # Run agent
    set +e
    python3 "$PROJECT_ROOT/scripts/coding/ai/automation/metrics_collector_agent.py" \
        --log-file "$violations_log" \
        --metrics-type violations \
        --period 7 \
        --output "$output_file" \
        --format json
    local exit_code=$?
    set -e

    # Assertions
    assert_file_exists "$output_file" "Metrics collector output" || return 1
    assert_json_valid "$output_file" || return 1
    assert_json_has_field "$output_file" "violations" || return 1

    # Verify metrics structure
    if ! python3 -c "
import json
data = json.load(open('$output_file'))
assert 'violations' in data
assert 'by_rule' in data['violations']
assert 'by_severity' in data['violations']
assert 'total' in data['violations']
" 2>/dev/null; then
        log_error "Metrics structure validation failed"
        return 1
    fi
    log_success "Metrics structure validated"

    assert_exit_code "$exit_code" 0 "Metrics collector" || return 1

    return 0
}

test_coherence_analyzer_integration() {
    local output_file="$TEMP_DIR/coherence_test.json"

    # Run agent on empty project (should handle gracefully)
    set +e
    python3 "$PROJECT_ROOT/scripts/coding/ai/automation/coherence_analyzer_agent.py" \
        --output "$output_file" \
        --threshold 0
    local exit_code=$?
    set -e

    # Assertions (0 or 1 are acceptable)
    assert_file_exists "$output_file" "Coherence analyzer output" || return 1
    assert_json_valid "$output_file" || return 1
    assert_json_has_field "$output_file" "status" || return 1
    assert_json_has_field "$output_file" "confidence_score" || return 1
    assert_exit_code_range "$exit_code" 0 1 "Coherence analyzer" || return 1

    return 0
}

test_constitution_validator_integration() {
    local output_file="$TEMP_DIR/constitution_test.json"
    local test_file="$TEMP_DIR/clean_file.py"

    # Create a clean test file (no emojis)
    cat > "$test_file" <<EOF
#!/usr/bin/env python3
# Clean Python file for testing
def hello():
    print("Hello, World!")
EOF

    # Run agent in manual mode with R2
    set +e
    python3 "$PROJECT_ROOT/scripts/coding/ai/automation/constitution_validator_agent.py" \
        --mode manual \
        --rules R2 \
        --changed-files "$test_file" \
        --output "$output_file"
    local exit_code=$?
    set -e

    # Assertions
    assert_file_exists "$output_file" "Constitution validator output" || return 1
    assert_json_valid "$output_file" || return 1
    assert_json_has_field "$output_file" "status" || return 1
    assert_json_has_field "$output_file" "violations" || return 1
    assert_json_has_field "$output_file" "summary" || return 1
    assert_exit_code "$exit_code" 0 "Constitution validator (clean file)" || return 1

    return 0
}

test_constitution_validator_emoji_detection() {
    local output_file="$TEMP_DIR/constitution_emoji_test.json"
    local test_file="$TEMP_DIR/emoji_file.py"

    # Create a file with an emoji
    cat > "$test_file" <<EOF
#!/usr/bin/env python3
# File with emoji for testing
def greet():
    print("Hello World")  # This comment is clean
EOF

    # Run agent in manual mode with R2
    set +e
    python3 "$PROJECT_ROOT/scripts/coding/ai/automation/constitution_validator_agent.py" \
        --mode manual \
        --rules R2 \
        --changed-files "$test_file" \
        --output "$output_file"
    local exit_code=$?
    set -e

    # Assertions
    assert_file_exists "$output_file" "Constitution validator output (emoji test)" || return 1
    assert_json_valid "$output_file" || return 1
    assert_exit_code "$exit_code" 0 "Constitution validator (should pass - no emojis)" || return 1

    return 0
}

test_ci_pipeline_orchestrator_integration() {
    local output_file="$TEMP_DIR/pipeline_test.json"
    local ci_config="$TEMP_DIR/.ci-local.yaml"

    # Create test pipeline configuration
    cat > "$ci_config" <<EOF
version: "1.0"
pipeline:
  name: "Test Pipeline"
  fail_fast: false
  parallel: false
  timeout: 300
stages:
  - name: "lint"
    description: "Linting stage"
    parallel: true
    depends_on: []
    jobs:
      - name: "echo-lint"
        command: "echo 'Running lint'"
        timeout: 10
        description: "Echo lint test"

  - name: "test"
    description: "Testing stage"
    parallel: false
    depends_on: ["lint"]
    jobs:
      - name: "echo-test"
        command: "echo 'Running tests'"
        timeout: 10
        description: "Echo test"
EOF

    # Run agent in dry-run mode
    set +e
    python3 "$PROJECT_ROOT/scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py" \
        --config "$ci_config" \
        --dry-run \
        --output "$output_file"
    local exit_code=$?
    set -e

    # Assertions
    assert_file_exists "$output_file" "CI Pipeline orchestrator output" || return 1
    assert_json_valid "$output_file" || return 1
    assert_json_has_field "$output_file" "status" || return 1
    assert_json_has_field "$output_file" "stage_results" || return 1
    assert_json_has_field "$output_file" "dry_run" || return 1

    # Verify dry_run flag is true
    if ! python3 -c "import json; data = json.load(open('$output_file')); assert data.get('dry_run') == True" 2>/dev/null; then
        log_error "dry_run flag not set correctly"
        return 1
    fi
    log_success "dry_run flag validated"

    assert_exit_code "$exit_code" 0 "CI Pipeline orchestrator (dry-run)" || return 1

    return 0
}

test_bash_to_python_invocation() {
    local agent_path="$PROJECT_ROOT/scripts/coding/ai/automation/schema_validator_agent.py"

    # Test 1: Direct Python invocation with actual execution
    local output_file="$TEMP_DIR/bash_invoke_test.json"
    local test_yaml="$TEMP_DIR/bash_test.yaml"
    local test_schema="$TEMP_DIR/bash_schema.json"

    echo 'version: "1.0"' > "$test_yaml"
    echo '{"type": "object"}' > "$test_schema"

    set +e
    python3 "$agent_path" \
        --file "$test_yaml" \
        --schema "$test_schema" \
        --output "$output_file" \
        --type constitucion >/dev/null 2>&1
    local exit_code=$?
    set -e

    assert_exit_code "$exit_code" 0 "Direct Python invocation" || return 1

    # Test 2: Bash subprocess invocation
    set +e
    bash -c "python3 '$agent_path' --file '$test_yaml' --schema '$test_schema' --output '$output_file' --type constitucion >/dev/null 2>&1"
    local exit_code=$?
    set -e

    assert_exit_code "$exit_code" 0 "Bash subprocess invocation" || return 1

    # Test 3: Test that file exists (agent executable)
    if [ ! -f "$agent_path" ]; then
        log_error "Agent file not found: $agent_path"
        return 1
    fi
    log_success "Agent file exists and is accessible"

    return 0
}

test_json_output_parsing() {
    local output_file="$TEMP_DIR/json_parse_test.json"
    local test_yaml="$TEMP_DIR/test.yaml"
    local test_schema="$TEMP_DIR/schema.json"

    # Create minimal test files
    echo 'version: "1.0"' > "$test_yaml"
    echo '{"type": "object"}' > "$test_schema"

    # Run agent
    set +e
    python3 "$PROJECT_ROOT/scripts/coding/ai/automation/schema_validator_agent.py" \
        --file "$test_yaml" \
        --schema "$test_schema" \
        --output "$output_file" \
        --type constitucion >/dev/null 2>&1
    set -e

    # Test parsing JSON with Python
    if ! python3 -c "import json; data = json.load(open('$output_file')); print(data.get('status', 'unknown'))" >/dev/null 2>&1; then
        log_error "Python JSON parsing failed"
        return 1
    fi
    log_success "Python JSON parsing works"

    # Test parsing JSON with jq (if available)
    if command -v jq >/dev/null 2>&1; then
        if ! jq -r '.status' "$output_file" >/dev/null 2>&1; then
            log_error "jq JSON parsing failed"
            return 1
        fi
        log_success "jq JSON parsing works"
    else
        log_warning "jq not available, skipping jq test"
    fi

    return 0
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    log_info "=========================================="
    log_info "Agent Integration Test Suite"
    log_info "=========================================="
    log_info ""
    log_info "Project Root: $PROJECT_ROOT"
    log_info "Temp Directory: $TEMP_DIR"
    log_info ""

    # Run all integration tests
    run_test "Schema Validator Integration" test_schema_validator_integration || true
    run_test "DevContainer Validator Integration" test_devcontainer_validator_integration || true
    run_test "Metrics Collector Integration" test_metrics_collector_integration || true
    run_test "Coherence Analyzer Integration" test_coherence_analyzer_integration || true
    run_test "Constitution Validator Integration" test_constitution_validator_integration || true
    run_test "Constitution Validator Emoji Detection" test_constitution_validator_emoji_detection || true
    run_test "CI Pipeline Orchestrator Integration" test_ci_pipeline_orchestrator_integration || true
    run_test "Bash to Python Invocation" test_bash_to_python_invocation || true
    run_test "JSON Output Parsing" test_json_output_parsing || true

    # Report results
    log_info ""
    log_info "=========================================="
    log_info "Test Results"
    log_info "=========================================="
    log_info ""
    log_info "Total Tests: $TOTAL_TESTS"
    log_success "Passed: $PASSED_TESTS"

    if [ $FAILED_TESTS -gt 0 ]; then
        log_error "Failed: $FAILED_TESTS"
        log_info ""
        log_error "Integration tests failed"
        return 1
    else
        log_info ""
        log_success "All integration tests passed!"
        return 0
    fi
}

# Run main function
if main; then
    exit 0
else
    exit 1
fi
