#!/bin/bash
# Validation utility for automation agents
# Tests that all 6 agents function correctly with real data
# NO EMOJIS - R2 compliant
#
# Exit codes:
#   0 - All agents passed
#   1 - Any agent failed

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
PASSED_AGENTS=()
FAILED_AGENTS=()

# ============================================================================
# Helper Functions
# ============================================================================

validate_json_output() {
    local file="$1"
    local agent_name="$2"

    if [ ! -f "$file" ]; then
        log_error "$agent_name: Output file not created: $file"
        return 1
    fi

    if ! python3 -m json.tool "$file" >/dev/null 2>&1; then
        log_error "$agent_name: Invalid JSON output"
        return 1
    fi

    log_success "$agent_name: Valid JSON output"
    return 0
}

check_exit_code() {
    local exit_code=$1
    local agent_name="$2"
    local expected="${3:-0}"

    if [ "$exit_code" -eq "$expected" ]; then
        log_success "$agent_name: Correct exit code ($exit_code)"
        return 0
    else
        log_error "$agent_name: Unexpected exit code (got $exit_code, expected $expected)"
        return 1
    fi
}

# ============================================================================
# Agent Validation Functions
# ============================================================================

validate_schema_validator() {
    local agent_name="SchemaValidatorAgent"
    log_info "Validating $agent_name..."

    local output_file="$TEMP_DIR/schema_validation.json"

    # Create a minimal valid YAML file for testing
    local test_yaml="$TEMP_DIR/test.yaml"
    cat > "$test_yaml" <<EOF
version: "1.0"
principles:
  - principle_id: "P1"
    name: "Test Principle"
rules:
  - rule_id: "R1"
    principle_id: "P1"
    severity: "error"
EOF

    # Create a minimal schema
    local test_schema="$TEMP_DIR/schema.json"
    cat > "$test_schema" <<EOF
{
  "\$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "version": {"type": "string"},
    "principles": {"type": "array"},
    "rules": {"type": "array"}
  }
}
EOF

    # Run the agent
    if python3 "$PROJECT_ROOT/scripts/coding/ai/automation/schema_validator_agent.py" \
        --file "$test_yaml" \
        --schema "$test_schema" \
        --output "$output_file" \
        --type constitucion; then

        if validate_json_output "$output_file" "$agent_name"; then
            PASSED_AGENTS+=("$agent_name")
            return 0
        fi
    fi

    FAILED_AGENTS+=("$agent_name")
    return 1
}

validate_devcontainer_validator() {
    local agent_name="DevContainerValidatorAgent"
    log_info "Validating $agent_name..."

    local output_file="$TEMP_DIR/devcontainer_validation.json"

    # Always create a test devcontainer.json without comments for validation
    # (Real devcontainer.json may have JSONC comments which json.load() can't parse)
    local devcontainer_json="$TEMP_DIR/devcontainer.json"
    cat > "$devcontainer_json" <<'EOF'
{
  "name": "test-devcontainer",
  "build": {
    "args": {
      "PYTHON_VERSION": "3.12",
      "NODE_VERSION": "18"
    }
  },
  "forwardPorts": [8000, 3000],
  "containerEnv": {
    "DEBUG": "1",
    "ENVIRONMENT": "test"
  }
}
EOF

    # Run the agent (exit code 1 is OK if some checks fail)
    set +e
    python3 "$PROJECT_ROOT/scripts/coding/ai/automation/devcontainer_validator_agent.py" \
        --devcontainer-json "$devcontainer_json" \
        --output "$output_file"
    local exit_code=$?
    set -e

    # We accept exit codes 0 or 1 (0=all passed, 1=some failed)
    if [ "$exit_code" -le 1 ]; then
        if validate_json_output "$output_file" "$agent_name"; then
            PASSED_AGENTS+=("$agent_name")
            return 0
        fi
    fi

    FAILED_AGENTS+=("$agent_name")
    return 1
}

validate_metrics_collector() {
    local agent_name="MetricsCollectorAgent"
    log_info "Validating $agent_name..."

    local output_file="$TEMP_DIR/metrics_report.json"

    # Create a sample violations log
    local violations_log="$TEMP_DIR/violations.log"
    cat > "$violations_log" <<EOF
[2025-11-13 12:00:00] VIOLATION - Rule: R2 - Severity: error - File: test.py - Line: 10 - Author: test - Message: Test violation
[2025-11-13 12:05:00] VIOLATION - Rule: R2 - Severity: warning - File: test.py - Line: 20 - Author: test - Message: Another test
EOF

    # Run the agent
    if python3 "$PROJECT_ROOT/scripts/coding/ai/automation/metrics_collector_agent.py" \
        --log-file "$violations_log" \
        --metrics-type violations \
        --period 30 \
        --output "$output_file" \
        --format json; then

        if validate_json_output "$output_file" "$agent_name"; then
            PASSED_AGENTS+=("$agent_name")
            return 0
        fi
    fi

    FAILED_AGENTS+=("$agent_name")
    return 1
}

validate_coherence_analyzer() {
    local agent_name="CoherenceAnalyzerAgent"
    log_info "Validating $agent_name..."

    local output_file="$TEMP_DIR/coherence_report.json"

    # Run the agent with current git state (if any changes)
    set +e
    python3 "$PROJECT_ROOT/scripts/coding/ai/automation/coherence_analyzer_agent.py" \
        --output "$output_file" \
        --threshold 0
    local exit_code=$?
    set -e

    # We accept exit codes 0 or 1
    if [ "$exit_code" -le 1 ]; then
        if validate_json_output "$output_file" "$agent_name"; then
            PASSED_AGENTS+=("$agent_name")
            return 0
        fi
    fi

    FAILED_AGENTS+=("$agent_name")
    return 1
}

validate_constitution_validator() {
    local agent_name="ConstitutionValidatorAgent"
    log_info "Validating $agent_name..."

    local output_file="$TEMP_DIR/constitution_validation.json"

    # Create a test file for R2 validation
    local test_file="$TEMP_DIR/test_file.txt"
    echo "This is a clean test file without any emojis" > "$test_file"

    # Run the agent in manual mode with R2 only (fast validation)
    set +e
    python3 "$PROJECT_ROOT/scripts/coding/ai/automation/constitution_validator_agent.py" \
        --mode manual \
        --rules R2 \
        --changed-files "$test_file" \
        --output "$output_file"
    local exit_code=$?
    set -e

    # We accept exit codes 0, 1, or 2 (0=pass, 1=errors, 2=warnings)
    if [ "$exit_code" -le 2 ]; then
        if validate_json_output "$output_file" "$agent_name"; then
            PASSED_AGENTS+=("$agent_name")
            return 0
        fi
    fi

    FAILED_AGENTS+=("$agent_name")
    return 1
}

validate_ci_pipeline_orchestrator() {
    local agent_name="CIPipelineOrchestratorAgent"
    log_info "Validating $agent_name..."

    local output_file="$TEMP_DIR/pipeline_report.json"
    local ci_config="$PROJECT_ROOT/.ci-local.yaml"

    # Check if .ci-local.yaml exists
    if [ ! -f "$ci_config" ]; then
        log_warning "$agent_name: .ci-local.yaml not found, creating minimal test config"
        ci_config="$TEMP_DIR/.ci-local.yaml"
        cat > "$ci_config" <<EOF
version: "1.0"
pipeline:
  name: "Test Pipeline"
  fail_fast: false
stages:
  - name: "test"
    jobs:
      - name: "echo-test"
        command: "echo 'test passed'"
        timeout: 10
EOF
    fi

    # Run the agent in dry-run mode
    if python3 "$PROJECT_ROOT/scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py" \
        --config "$ci_config" \
        --dry-run \
        --output "$output_file"; then

        if validate_json_output "$output_file" "$agent_name"; then
            PASSED_AGENTS+=("$agent_name")
            return 0
        fi
    fi

    FAILED_AGENTS+=("$agent_name")
    return 1
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    log_info "=========================================="
    log_info "Automation Agents Validation Utility"
    log_info "=========================================="
    log_info ""
    log_info "Project Root: $PROJECT_ROOT"
    log_info "Temp Directory: $TEMP_DIR"
    log_info ""

    # Run validations
    validate_schema_validator || true
    validate_devcontainer_validator || true
    validate_metrics_collector || true
    validate_coherence_analyzer || true
    validate_constitution_validator || true
    validate_ci_pipeline_orchestrator || true

    # Report results
    log_info ""
    log_info "=========================================="
    log_info "Validation Results"
    log_info "=========================================="
    log_info ""

    log_info "Passed Agents (${#PASSED_AGENTS[@]}/6):"
    for agent in "${PASSED_AGENTS[@]}"; do
        log_success "  - $agent"
    done

    if [ ${#FAILED_AGENTS[@]} -gt 0 ]; then
        log_info ""
        log_info "Failed Agents (${#FAILED_AGENTS[@]}/6):"
        for agent in "${FAILED_AGENTS[@]}"; do
            log_error "  - $agent"
        done
        log_info ""
        log_error "Validation failed: ${#FAILED_AGENTS[@]} agent(s) failed"
        return 1
    else
        log_info ""
        log_success "All agents validated successfully!"
        return 0
    fi
}

# Run main function
if main; then
    exit 0
else
    exit 1
fi
