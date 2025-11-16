---
title: Integration Guide - Sistema Automatizacion IACT
date: 2025-11-13
status: Active
version: 1.0
related_docs:
  - USE_CASES.md
  - AGENTS_ARCHITECTURE.md
  - ADR-040 through ADR-045
---

# Integration Guide - Sistema Automatizacion IACT

**Version**: 1.0
**Date**: 2025-11-13
**Purpose**: Complete guide for integrating automation agents with Bash scripts, Git hooks, and DevContainer lifecycle

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture Integration](#architecture-integration)
3. [Bash-Python Integration](#bash-python-integration)
4. [Git Hooks Integration](#git-hooks-integration)
5. [CI/CD Integration](#cicd-integration)
6. [DevContainer Integration](#devcontainer-integration)
7. [Configuration Files](#configuration-files)
8. [Communication Protocols](#communication-protocols)
9. [Error Handling](#error-handling)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The IACT automation system uses a hybrid Bash/Python architecture where:
- **Bash scripts** serve as entry points and orchestrate high-level workflows
- **Python agents** implement complex validation logic, AST parsing, and async operations
- **JSON** provides structured communication between layers
- **Exit codes** propagate status information

**Integration Flow**:
```
User/Git Hook
    |
    v
Bash Entry Point (constitucion.sh, ci-local.sh, etc.)
    |
    v
Python Agent (validation logic)
    |
    v
JSON Output
    |
    v
Bash (parse JSON, handle exit code)
    |
    v
Exit Code to caller
```

---

## Architecture Integration

### System Components

```
/scripts/
├── constitucion.sh                          # Bash entry point for constitution
├── ci-local.sh                              # Bash entry point for CI pipeline
├── check_ui_api_coherence.sh               # Bash entry point for coherence
├── validate_constitution_schema.sh          # Bash entry point for schema validation
├── validate_devcontainer_env.sh             # Bash entry point for environment
│
├── coding/ai/automation/
│   ├── constitution_validator_agent.py      # Python agent (R1-R6)
│   ├── ci_pipeline_orchestrator_agent.py    # Python agent (CI orchestration)
│   ├── coherence_analyzer_agent.py          # Python agent (UI/API coherence)
│   ├── schema_validator_agent.py            # Python agent (YAML/JSON validation)
│   ├── devcontainer_validator_agent.py      # Python agent (environment validation)
│   └── metrics_collector_agent.py           # Python agent (metrics collection)
│
└── .git/hooks/
    ├── pre-commit                           # Fast validation (R2)
    ├── commit-msg                           # Conventional commits
    ├── pre-push                             # Comprehensive validation (R1, R3-R5)
    └── pre-rebase                           # Branch protection
```

### Agent Dependencies

```
SchemaValidatorAgent (no dependencies)
    |
    +-- DevContainerValidatorAgent
    |
    +-- ConstitutionValidatorAgent
            |
            +-- CoherenceAnalyzerAgent
            |
            +-- CIPipelineOrchestratorAgent

MetricsCollectorAgent (no dependencies)
```

**Implementation Order** (TDD):
1. SchemaValidatorAgent
2. DevContainerValidatorAgent
3. MetricsCollectorAgent
4. CoherenceAnalyzerAgent
5. ConstitutionValidatorAgent
6. CIPipelineOrchestratorAgent

---

## Bash-Python Integration

### Pattern 1: Simple Invocation

**Bash Entry Point**:
```bash
#!/usr/bin/env bash
# scripts/validate_constitution_schema.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

python3 "$SCRIPT_DIR/coding/ai/automation/schema_validator_agent.py" \
    --file "$1" \
    --schema schemas/constitucion_schema.json \
    --output /tmp/schema_validation.json \
    --type constitucion

exit $?
```

**Python Agent**:
```python
#!/usr/bin/env python3
# scripts/coding/ai/automation/schema_validator_agent.py

import sys
import argparse
import json

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--schema", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--type", required=True)

    args = parser.parse_args()

    # Validation logic
    result = validate_schema(args.file, args.schema)

    # Write JSON output
    with open(args.output, 'w') as f:
        json.dump(result, f, indent=2)

    # Return exit code
    sys.exit(0 if result["is_valid"] else 1)

if __name__ == "__main__":
    main()
```

### Pattern 2: JSON Communication

**Bash to Python (Input)**:
```bash
# Bash prepares structured input
cat > /tmp/input.json <<EOF
{
  "mode": "pre-push",
  "changed_files": ["src/app.py", "docs/README.md"],
  "config_file": ".constitucion.yaml",
  "verbose": true
}
EOF

# Python reads JSON input
python3 agent.py --input /tmp/input.json --output /tmp/output.json
```

**Python to Bash (Output)**:
```bash
# Python writes structured output
# Output: /tmp/output.json
{
  "status": "success",
  "violations": [],
  "summary": {
    "rules_evaluated": 4,
    "rules_passed": 4
  }
}

# Bash parses JSON output
status=$(jq -r '.status' /tmp/output.json)
violations_count=$(jq '.violations | length' /tmp/output.json)

if [ "$status" == "success" ]; then
    echo "Validation passed"
else
    echo "Validation failed with $violations_count violations"
    jq '.violations' /tmp/output.json
    exit 1
fi
```

### Pattern 3: Exit Code Convention

**Standard Exit Codes**:
```
0  = Success (all checks passed)
1  = Failure (blocking errors detected)
2  = Warnings (non-blocking issues)
3  = Configuration error (cannot run)
```

**Bash Handler**:
```bash
python3 agent.py --mode pre-push
exit_code=$?

case $exit_code in
    0)
        log_success "Validation passed"
        ;;
    1)
        log_error "Validation failed (blocking)"
        jq '.violations' /tmp/report.json
        exit 1
        ;;
    2)
        log_warn "Validation has warnings (non-blocking)"
        jq '.warnings' /tmp/report.json
        ;;
    3)
        log_error "Configuration error"
        exit 3
        ;;
    *)
        log_error "Unknown exit code: $exit_code"
        exit 1
        ;;
esac
```

### Pattern 4: Argument Passing

**Bash Variable to Python**:
```bash
MODE="pre-push"
VERBOSE=true
FILES="file1.py,file2.md"

python3 agent.py \
    --mode "$MODE" \
    --changed-files "$FILES" \
    $([ "$VERBOSE" == "true" ] && echo "--verbose")
```

**Array Passing**:
```bash
# Bash array
changed_files=("file1.py" "file2.md" "file3.ts")

# Convert to comma-separated string
files_csv=$(IFS=,; echo "${changed_files[*]}")

# Pass to Python
python3 agent.py --changed-files "$files_csv"
```

**Python Parsing**:
```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--changed-files", type=str, required=False)
parser.add_argument("--verbose", action="store_true")

args = parser.parse_args()

# Parse comma-separated files
if args.changed_files:
    files = args.changed_files.split(",")
else:
    files = []
```

---

## Git Hooks Integration

### Pre-Commit Hook

**Purpose**: Fast validation before commit (< 2 seconds)
**Rules Validated**: R2 (no emojis)

**File**: `.git/hooks/pre-commit`
```bash
#!/usr/bin/env bash
set -euo pipefail

# Get staged files
changed_files=$(git diff --cached --name-only | tr '\n' ',')

# Skip if no files changed
if [ -z "$changed_files" ]; then
    exit 0
fi

echo "Running pre-commit validation (R2: emoji check)..."

# Run ConstitutionValidatorAgent in pre-commit mode
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode pre-commit \
    --changed-files "$changed_files" \
    --output /tmp/constitution_precommit.json

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "Pre-commit validation failed!"
    echo "Violations detected:"
    jq -r '.violations[] | "  - \(.file):\(.line): \(.message)"' /tmp/constitution_precommit.json
    exit 1
fi

echo "Pre-commit validation passed"
exit 0
```

**Installation**:
```bash
# Copy hook to .git/hooks/
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Or use install_hooks.sh
./scripts/install_hooks.sh
```

### Commit-Msg Hook

**Purpose**: Enforce conventional commits format
**Validation**: Commit message format

**File**: `.git/hooks/commit-msg`
```bash
#!/usr/bin/env bash
set -euo pipefail

commit_msg_file="$1"
commit_msg=$(cat "$commit_msg_file")

# Check conventional commits format
# Format: type(scope): message
# Types: feat, fix, docs, style, refactor, test, chore

if ! echo "$commit_msg" | grep -qE '^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?: .+'; then
    echo "ERROR: Commit message does not follow conventional commits format"
    echo ""
    echo "Format: type(scope): message"
    echo "Types: feat, fix, docs, style, refactor, test, chore"
    echo ""
    echo "Example: feat(auth): add user login functionality"
    echo ""
    echo "Your message:"
    echo "$commit_msg"
    exit 1
fi

exit 0
```

### Pre-Push Hook

**Purpose**: Comprehensive validation before push (< 30 seconds)
**Rules Validated**: R1, R3, R4, R5

**File**: `.git/hooks/pre-push`
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Running pre-push validation..."
echo "This may take up to 30 seconds..."

# Step 1: Constitution validation (R1, R3, R4, R5)
echo "1/2 Validating constitution rules..."
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode pre-push \
    --output /tmp/constitution_prepush.json

if [ $? -ne 0 ]; then
    echo "Constitution validation failed!"
    jq -r '.violations[] | "  - \(.rule_id): \(.message)"' /tmp/constitution_prepush.json
    exit 1
fi

# Step 2: Run CI pipeline (smart detection)
echo "2/2 Running CI pipeline..."
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --smart-detection \
    --git-diff origin/main \
    --output /tmp/ci_prepush.json

if [ $? -ne 0 ]; then
    echo "CI pipeline failed!"
    jq '.summary' /tmp/ci_prepush.json
    exit 1
fi

echo "Pre-push validation passed!"
exit 0
```

### Pre-Rebase Hook

**Purpose**: Protect main/master branch from rebase
**Validation**: Branch protection

**File**: `.git/hooks/pre-rebase`
```bash
#!/usr/bin/env bash
set -euo pipefail

# Get branch being rebased
branch="${1:-}"

# Protect main/master branches
if [ "$branch" == "main" ] || [ "$branch" == "master" ]; then
    echo "ERROR: Cannot rebase protected branch '$branch'"
    echo "This violates R1 (branch protection)"
    exit 1
fi

exit 0
```

---

## CI/CD Integration

### CI Local Configuration

**File**: `.ci-local.yaml`
```yaml
version: "1.0"

pipeline:
  name: "IACT Local CI"
  fail_fast: true
  parallel: true
  timeout: 600
  smart_detection:
    enabled: true
    strategy: git_diff
    base_branch: main

stages:
  - name: lint
    parallel: true
    depends_on: []
    jobs:
      - name: lint_ui
        working_dir: ui/
        command: "npm run lint"
        timeout: 60
        condition:
          type: files_changed
          pattern: 'ui/**/*.(js|jsx|ts|tsx)'

      - name: lint_api
        working_dir: api/callcentersite/
        command: "ruff check ."
        timeout: 60
        condition:
          type: files_changed
          pattern: 'api/**/*.py'

  - name: test
    parallel: true
    depends_on: [lint]
    jobs:
      - name: test_ui
        working_dir: ui/
        command: "npm run test"
        timeout: 180
        condition:
          type: files_changed
          pattern: 'ui/**/*.(js|jsx|ts|tsx)'

      - name: test_api
        working_dir: api/callcentersite/
        command: "pytest"
        timeout: 300
        condition:
          type: files_changed
          pattern: 'api/**/*.py'

  - name: build
    parallel: true
    depends_on: [test]
    jobs:
      - name: build_ui
        working_dir: ui/
        command: "npm run build"
        timeout: 120

      - name: build_api
        working_dir: api/callcentersite/
        command: "python manage.py collectstatic --noinput"
        timeout: 60

  - name: validate
    parallel: false
    depends_on: [build]
    jobs:
      - name: validate_constitution
        command: "python3 scripts/coding/ai/automation/constitution_validator_agent.py --mode ci-local"
        timeout: 60

      - name: validate_coherence
        command: "python3 scripts/coding/ai/automation/coherence_analyzer_agent.py --git-diff origin/main --threshold 70.0"
        timeout: 60
```

### CI Bash Wrapper

**File**: `scripts/ci-local.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="${1:-.ci-local.yaml}"
MODE="${2:-full}"

echo "IACT Local CI Pipeline"
echo "======================"
echo "Config: $CONFIG_FILE"
echo "Mode: $MODE"
echo ""

# Prepare output directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_FILE="/tmp/ci_report_${TIMESTAMP}.json"

# Execute based on mode
case "$MODE" in
    "quick")
        # Quick mode: lint only
        echo "Running QUICK mode (lint only)..."
        python3 "$SCRIPT_DIR/coding/ai/automation/ci_pipeline_orchestrator_agent.py" \
            --config "$CONFIG_FILE" \
            --stage lint \
            --output "$REPORT_FILE"
        ;;

    "smart")
        # Smart mode: only changed components
        echo "Running SMART mode (changed components only)..."
        python3 "$SCRIPT_DIR/coding/ai/automation/ci_pipeline_orchestrator_agent.py" \
            --config "$CONFIG_FILE" \
            --smart-detection \
            --git-diff origin/main \
            --output "$REPORT_FILE"
        ;;

    "full")
        # Full mode: all stages
        echo "Running FULL mode (all stages)..."
        python3 "$SCRIPT_DIR/coding/ai/automation/ci_pipeline_orchestrator_agent.py" \
            --config "$CONFIG_FILE" \
            --output "$REPORT_FILE"
        ;;

    *)
        echo "Unknown mode: $MODE"
        echo "Valid modes: quick, smart, full"
        exit 1
        ;;
esac

exit_code=$?

# Display results
echo ""
echo "Pipeline Summary:"
echo "================="
jq -r '.summary | to_entries[] | "\(.key): \(.value)"' "$REPORT_FILE"

if [ $exit_code -eq 0 ]; then
    echo ""
    echo "CI pipeline PASSED"
else
    echo ""
    echo "CI pipeline FAILED"
    echo ""
    echo "Failed jobs:"
    jq -r '.stages[].jobs[] | select(.status == "failure") | "  - \(.name): \(.exit_code)"' "$REPORT_FILE"
fi

exit $exit_code
```

---

## DevContainer Integration

### DevContainer Configuration

**File**: `.devcontainer/devcontainer.json`
```json
{
  "name": "IACT Development Container",
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspace",

  "features": {
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.12"
    },
    "ghcr.io/devcontainers/features/node:1": {
      "version": "18"
    }
  },

  "postCreateCommand": "bash scripts/validate_devcontainer_env.sh --full",
  "postStartCommand": "bash scripts/validate_devcontainer_env.sh --quick",
  "postAttachCommand": "bash scripts/validate_devcontainer_env.sh --services-only",

  "forwardPorts": [5432, 3306, 8000, 3000],

  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "dbaeumer.vscode-eslint"
      ]
    }
  }
}
```

### Lifecycle Validation Script

**File**: `scripts/validate_devcontainer_env.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:---full}"

echo "DevContainer Environment Validation"
echo "===================================="
echo "Mode: $MODE"
echo ""

DEVCONTAINER_JSON="$SCRIPT_DIR/../.devcontainer/devcontainer.json"
OUTPUT="/tmp/devcontainer_validation.json"

case "$MODE" in
    "--full")
        # Full validation (all checks)
        echo "Running FULL validation..."
        python3 "$SCRIPT_DIR/coding/ai/automation/devcontainer_validator_agent.py" \
            --devcontainer-json "$DEVCONTAINER_JSON" \
            --output "$OUTPUT" \
            --strict
        ;;

    "--quick")
        # Quick validation (services + versions)
        echo "Running QUICK validation..."
        python3 "$SCRIPT_DIR/coding/ai/automation/devcontainer_validator_agent.py" \
            --devcontainer-json "$DEVCONTAINER_JSON" \
            --output "$OUTPUT" \
            --check-services-only \
            --check-versions-only
        ;;

    "--services-only")
        # Services only (health check)
        echo "Running SERVICES validation..."
        python3 "$SCRIPT_DIR/coding/ai/automation/devcontainer_validator_agent.py" \
            --devcontainer-json "$DEVCONTAINER_JSON" \
            --output "$OUTPUT" \
            --check-services-only
        ;;

    *)
        echo "Unknown mode: $MODE"
        echo "Valid modes: --full, --quick, --services-only"
        exit 1
        ;;
esac

exit_code=$?

# Display results
if [ $exit_code -eq 0 ]; then
    echo ""
    echo "DevContainer validation PASSED"
    echo ""
    jq -r '.checks[] | "\(.status | ascii_upcase): \(.message)"' "$OUTPUT"
else
    echo ""
    echo "DevContainer validation FAILED"
    echo ""
    echo "Failed checks:"
    jq -r '.checks[] | select(.status == "fail") | "  - \(.message)"' "$OUTPUT"
fi

exit $exit_code
```

---

## Configuration Files

### Constitution Configuration

**File**: `.constitucion.yaml`
```yaml
version: "1.0"

metadata:
  project: "IACT---project"
  description: "Constitution codificada - reglas de gobernanza"
  maintained_by: "DevOps Team"

principles:
  - id: P1
    name: "Branch Protection"
    description: "Proteger branches principales de modificaciones directas"

  - id: P2
    name: "Code Quality"
    description: "Mantener alta calidad y legibilidad del codigo"

  - id: P3
    name: "Test Coverage"
    description: "Mantener cobertura de tests minima"

rules:
  - id: R1
    principle_id: P1
    name: "No Direct Push to Main/Master"
    description: "No permitir push directo a main/master"
    severity: error
    scope: ["pre-push", "ci-local"]
    enabled: true

  - id: R2
    principle_id: P2
    name: "No Emojis Anywhere"
    description: "No permitir emojis en codigo, docs, commits"
    severity: error
    scope: ["pre-commit", "pre-push", "ci-local"]
    enabled: true

  - id: R3
    principle_id: P2
    name: "UI/API Coherence"
    description: "Cambios en API deben tener correspondientes cambios en UI"
    severity: warning
    scope: ["pre-push", "ci-local"]
    enabled: true

  - id: R4
    principle_id: P2
    name: "Database Router Valid"
    description: "Configuracion database router debe ser valida"
    severity: error
    scope: ["pre-push", "ci-local"]
    enabled: true

  - id: R5
    principle_id: P3
    name: "Tests Must Pass"
    description: "Todos los tests deben pasar"
    severity: error
    scope: ["pre-push", "ci-local"]
    enabled: true

  - id: R6
    principle_id: P2
    name: "DevContainer Compatibility"
    description: "Codigo debe ser compatible con DevContainer"
    severity: warning
    scope: ["devcontainer-init", "ci-local"]
    enabled: true
```

### Schema Files

**File**: `schemas/constitucion_schema.json`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "metadata", "principles", "rules"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+$"
    },
    "metadata": {
      "type": "object",
      "required": ["project", "description"],
      "properties": {
        "project": {"type": "string"},
        "description": {"type": "string"},
        "maintained_by": {"type": "string"}
      }
    },
    "principles": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "description"],
        "properties": {
          "id": {"type": "string", "pattern": "^P\\d+$"},
          "name": {"type": "string"},
          "description": {"type": "string"}
        }
      }
    },
    "rules": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "principle_id", "name", "severity", "scope", "enabled"],
        "properties": {
          "id": {"type": "string", "pattern": "^R\\d+$"},
          "principle_id": {"type": "string"},
          "name": {"type": "string"},
          "description": {"type": "string"},
          "severity": {"type": "string", "enum": ["error", "warning"]},
          "scope": {
            "type": "array",
            "items": {
              "type": "string",
              "enum": ["pre-commit", "pre-push", "devcontainer-init", "ci-local"]
            }
          },
          "enabled": {"type": "boolean"}
        }
      }
    }
  }
}
```

---

## Communication Protocols

### JSON Output Format

**Standard Structure**:
```json
{
  "status": "success|failure|warning",
  "timestamp": "2025-11-13T12:00:00",
  "summary": {
    "total_checks": 10,
    "passed": 9,
    "failed": 1
  },
  "violations": [
    {
      "rule_id": "R2",
      "severity": "error",
      "message": "Description of violation",
      "file": "path/to/file.py",
      "line": 42,
      "column": 15
    }
  ],
  "warnings": [],
  "details": {}
}
```

### Exit Code Mapping

```bash
# Python agent returns exit code
sys.exit(0)  # Success
sys.exit(1)  # Failure (blocking)
sys.exit(2)  # Warnings (non-blocking)
sys.exit(3)  # Configuration error

# Bash handles exit code
case $? in
    0) echo "Success" ;;
    1) echo "Failure"; exit 1 ;;
    2) echo "Warnings" ;;
    3) echo "Config error"; exit 3 ;;
esac
```

### Logging Convention

**Python Agent Logging**:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

logger.info("Starting validation")
logger.warning("Deprecated configuration found")
logger.error("Validation failed")
```

**Bash Script Logging**:
```bash
# Log functions
log_info() { echo "[INFO] $*"; }
log_success() { echo "[OK] $*"; }
log_warn() { echo "[WARN] $*" >&2; }
log_error() { echo "[ERROR] $*" >&2; }

# Usage
log_info "Starting CI pipeline"
log_success "Tests passed"
log_warn "Low coverage detected"
log_error "Build failed"
```

---

## Error Handling

### Python Agent Error Handling

```python
import sys
import json
import logging

def main():
    try:
        # Validation logic
        result = run_validation()

        # Write JSON output
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)

        # Exit based on result
        sys.exit(0 if result["is_valid"] else 1)

    except FileNotFoundError as e:
        # Configuration error
        error_result = {
            "status": "error",
            "message": f"Configuration file not found: {e}"
        }
        with open(args.output, 'w') as f:
            json.dump(error_result, f, indent=2)
        sys.exit(3)

    except Exception as e:
        # Unexpected error
        logging.error(f"Unexpected error: {e}", exc_info=True)
        error_result = {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }
        with open(args.output, 'w') as f:
            json.dump(error_result, f, indent=2)
        sys.exit(3)
```

### Bash Error Handling

```bash
set -euo pipefail

# Error trap
trap 'echo "Error on line $LINENO"; exit 1' ERR

# Function with error handling
validate_file() {
    local file="$1"

    if [ ! -f "$file" ]; then
        log_error "File not found: $file"
        return 1
    fi

    python3 agent.py --file "$file" || {
        log_error "Validation failed for $file"
        return 1
    }

    return 0
}

# Usage with error handling
if ! validate_file ".constitucion.yaml"; then
    log_error "Constitution validation failed"
    exit 1
fi
```

---

## Troubleshooting

### Common Issues

#### Issue 1: Python Agent Not Found

**Symptom**:
```
bash: python3: command not found
```

**Solution**:
```bash
# Check Python installation
which python3

# If not found, install Python 3.11+
# (DevContainer should have this)

# Verify version
python3 --version  # Should be 3.11+
```

#### Issue 2: JSON Parsing Fails

**Symptom**:
```
jq: parse error: Invalid numeric literal
```

**Solution**:
```bash
# Check if JSON file exists and is valid
if [ ! -f /tmp/report.json ]; then
    echo "ERROR: Report file not generated"
    exit 1
fi

# Validate JSON
if ! jq empty /tmp/report.json 2>/dev/null; then
    echo "ERROR: Invalid JSON in report"
    cat /tmp/report.json
    exit 1
fi
```

#### Issue 3: Git Hook Not Executing

**Symptom**:
```
Commit succeeds but hook didn't run
```

**Solution**:
```bash
# Check if hook is executable
ls -la .git/hooks/pre-commit

# If not executable, fix permissions
chmod +x .git/hooks/pre-commit

# Verify hook has correct shebang
head -1 .git/hooks/pre-commit  # Should be #!/usr/bin/env bash
```

#### Issue 4: DevContainer Validation Fails

**Symptom**:
```
PostgreSQL is not available on port 5432
```

**Solution**:
```bash
# Check if services are running
docker ps

# Restart DevContainer
# VS Code: Command Palette -> Dev Containers: Rebuild Container

# Check service logs
docker logs <container_id>

# Verify port forwarding
docker port <container_id>
```

#### Issue 5: Permission Denied

**Symptom**:
```
Permission denied: /tmp/report.json
```

**Solution**:
```bash
# Check /tmp permissions
ls -ld /tmp

# Use alternative output directory
mkdir -p ~/.automation-logs
python3 agent.py --output ~/.automation-logs/report.json
```

### Debug Mode

**Enable Verbose Logging**:
```bash
# Bash
set -x  # Enable command tracing

# Python
python3 agent.py --verbose

# Environment variable
export DEBUG=1
```

**Check Logs**:
```bash
# Agent logs
tail -f ~/.automation-logs/agents.log

# Git hook logs
tail -f .git/hooks/pre-commit.log
```

---

## Summary

This integration guide provides:

1. **Complete architecture** of Bash/Python hybrid system
2. **Integration patterns** for all agent types
3. **Git hooks** setup and configuration
4. **CI/CD** pipeline integration
5. **DevContainer** lifecycle integration
6. **Configuration** file formats
7. **Communication protocols** (JSON, exit codes)
8. **Error handling** best practices
9. **Troubleshooting** common issues

For detailed use cases, see: `docs/devops/automatizacion/USE_CASES.md`
For architecture details, see: `docs/devops/automatizacion/planificacion/AGENTS_ARCHITECTURE.md`

---

**Last Updated**: 2025-11-13
**Version**: 1.0
**Maintained By**: DevOps Team
