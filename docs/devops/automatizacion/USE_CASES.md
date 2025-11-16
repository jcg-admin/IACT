---
title: Use Cases - Sistema Automatizacion IACT
date: 2025-11-13
status: Active
version: 1.0
related_docs:
  - AGENTS_ARCHITECTURE.md
  - ADR-040-schema-validator-agent.md
  - ADR-041-devcontainer-validator-agent.md
  - ADR-042-metrics-collector-agent.md
  - ADR-043-coherence-analyzer-agent.md
  - ADR-044-constitution-validator-agent.md
  - ADR-045-ci-pipeline-orchestrator-agent.md
  - INTEGRATION_GUIDE.md
---

# Use Cases - Sistema Automatizacion IACT

**Version**: 1.0
**Date**: 2025-11-13
**Architecture**: Hybrid Bash/Python automation system

---

## Table of Contents

1. [Overview](#overview)
2. [Agent Use Cases](#agent-use-cases)
   - [1. SchemaValidatorAgent](#1-schemavalidatoragent)
   - [2. DevContainerValidatorAgent](#2-devcontainervalidatoragent)
   - [3. MetricsCollectorAgent](#3-metricscollectoragent)
   - [4. CoherenceAnalyzerAgent](#4-coherenceanalyzeragent)
   - [5. ConstitutionValidatorAgent](#5-constitutionvalidatoragent)
   - [6. CIPipelineOrchestratorAgent](#6-cipipelineorchestratoragent)
3. [Workflow Use Cases](#workflow-use-cases)
   - [Developer Workflows](#developer-workflows)
   - [CI/CD Workflows](#cicd-workflows)
   - [DevContainer Workflows](#devcontainer-workflows)
   - [Manual Validation Workflows](#manual-validation-workflows)
4. [Hybrid Bash/Python Patterns](#hybrid-bashpython-patterns)
5. [Common Scenarios](#common-scenarios)
6. [Integration Examples](#integration-examples)

---

## Overview

The IACT automation system consists of 6 specialized Python agents orchestrated by Bash scripts. This document provides comprehensive use cases for each agent and workflow scenario.

**System Architecture**:
```
Git Hooks (Bash Entry Points)
    |
    v
Bash Scripts (constitucion.sh, ci-local.sh, etc.)
    |
    v
Python Agents (6 specialized agents)
    |
    v
Validation Logic, Metrics, Reports
    |
    v
JSON Output -> Bash -> Exit Codes
```

**Design Principles**:
- Bash for entry points, file operations, Git integration
- Python for complex logic, AST parsing, async operations
- JSON for inter-process communication
- Exit codes for status propagation

---

## Agent Use Cases

### 1. SchemaValidatorAgent

**Location**: `scripts/coding/ai/automation/schema_validator_agent.py`
**ADR**: ADR-040
**Responsibility**: Validate YAML/JSON configuration files against JSON schemas

#### Primary Use Case: Constitution Schema Validation

**Scenario**: Developer modifies .constitucion.yaml and wants to ensure it's valid before committing.

**CLI Example**:
```bash
python3 scripts/coding/ai/automation/schema_validator_agent.py \
    --file .constitucion.yaml \
    --schema schemas/constitucion_schema.json \
    --output /tmp/validation_report.json \
    --type constitucion

# Exit codes:
# 0 = valid
# 1 = invalid (blocking)
# 3 = configuration error
```

**Output**:
```json
{
  "status": "valid",
  "is_valid": true,
  "file_path": ".constitucion.yaml",
  "file_type": "yaml",
  "errors": [],
  "warnings": [],
  "summary": {
    "syntax_valid": true,
    "schema_valid": true,
    "references_valid": true,
    "total_checks": 3,
    "errors_count": 0,
    "warnings_count": 0
  },
  "timestamp": "2025-11-13T23:39:59.025323"
}
```

#### Secondary Use Cases

**UC1.1: CI/CD Pipeline Configuration Validation**
```bash
# Validate .ci-local.yaml before pipeline execution
python3 scripts/coding/ai/automation/schema_validator_agent.py \
    --file .ci-local.yaml \
    --schema schemas/ci_local_schema.json \
    --type ci_local
```

**UC1.2: Pre-commit Hook Integration**
```bash
# In .git/hooks/pre-commit
if git diff --cached --name-only | grep -E '\.constitucion\.yaml$'; then
    python3 scripts/coding/ai/automation/schema_validator_agent.py \
        --file .constitucion.yaml \
        --schema schemas/constitucion_schema.json || exit 1
fi
```

**UC1.3: DevContainer Configuration Validation**
```bash
# Validate devcontainer.json structure
python3 scripts/coding/ai/automation/schema_validator_agent.py \
    --file .devcontainer/devcontainer.json \
    --schema schemas/devcontainer_schema.json \
    --type devcontainer
```

**UC1.4: Batch Validation (CI)**
```bash
# Validate all configuration files in CI
for config_file in .constitucion.yaml .ci-local.yaml; do
    python3 scripts/coding/ai/automation/schema_validator_agent.py \
        --file "$config_file" \
        --schema "schemas/$(basename "$config_file" .yaml)_schema.json"

    if [ $? -ne 0 ]; then
        echo "ERROR: $config_file validation failed"
        exit 1
    fi
done
```

#### Integration Examples

**Bash Wrapper Integration** (validate_constitution_schema.sh):
```bash
#!/usr/bin/env bash
# Wrapper for SchemaValidatorAgent

python3 scripts/coding/ai/automation/schema_validator_agent.py \
    --file "$1" \
    --schema schemas/constitucion_schema.json \
    --output /tmp/schema_validation.json \
    --type constitucion

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "Schema validation PASSED"
elif [ $exit_code -eq 1 ]; then
    echo "Schema validation FAILED"
    jq '.errors' /tmp/schema_validation.json
elif [ $exit_code -eq 3 ]; then
    echo "Configuration ERROR"
fi

exit $exit_code
```

**Programmatic Integration** (Python):
```python
from scripts.coding.ai.automation.schema_validator_agent import SchemaValidatorAgent

agent = SchemaValidatorAgent()
result = agent.validate_all(
    file_path=".constitucion.yaml",
    schema_path="schemas/constitucion_schema.json",
    file_type="constitucion"
)

if result["is_valid"]:
    print("Validation passed")
else:
    for error in result["errors"]:
        print(f"Error in {error['field']}: {error['message']}")
```

#### Common Scenarios

**Scenario 1: Reference Validation Failure**
```json
{
  "status": "invalid",
  "errors": [
    {
      "type": "reference",
      "message": "Rule references non-existent principle: P999",
      "field": "rules[0].principle_id",
      "location": "field: rules[0].principle_id",
      "severity": "error"
    }
  ]
}
```

**Scenario 2: Type Checking Failure**
```json
{
  "status": "invalid",
  "errors": [
    {
      "type": "schema",
      "message": "Invalid severity value. Must be 'error' or 'warning'",
      "field": "rules[2].severity",
      "severity": "error"
    }
  ]
}
```

---

### 2. DevContainerValidatorAgent

**Location**: `scripts/coding/ai/automation/devcontainer_validator_agent.py`
**ADR**: ADR-041
**Responsibility**: Comprehensive DevContainer environment validation

#### Primary Use Case: Container Startup Validation

**Scenario**: DevContainer starts and needs to validate all services are healthy before development begins.

**CLI Example**:
```bash
python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
    --devcontainer-json .devcontainer/devcontainer.json \
    --output /tmp/devcontainer_validation.json \
    --strict

# Exit codes:
# 0 = all checks passed
# 1 = validation failures
# 3 = configuration error
```

**Output**:
```json
{
  "status": "success",
  "timestamp": "2025-11-13T23:40:00",
  "summary": {
    "total_checks": 20,
    "passed": 20,
    "failed": 0
  },
  "checks": [
    {
      "status": "pass",
      "message": "PostgreSQL is available on port 5432",
      "port": 5432
    },
    {
      "status": "pass",
      "message": "MariaDB is available on port 3306",
      "port": 3306
    },
    {
      "status": "pass",
      "message": "Python version 3.12.1 matches requirement 3.12.x",
      "details": {"actual": "3.12.1", "required": "3.12.x"}
    }
  ]
}
```

#### Secondary Use Cases

**UC2.1: Service Health Check**
```bash
# Check only database services
python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
    --devcontainer-json .devcontainer/devcontainer.json \
    --check-services-only
```

**UC2.2: Version Verification**
```bash
# Verify runtime versions match requirements
python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
    --devcontainer-json .devcontainer/devcontainer.json \
    --check-versions-only
```

**UC2.3: Dependency Verification**
```bash
# Verify all required CLI tools are installed
python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
    --devcontainer-json .devcontainer/devcontainer.json \
    --check-dependencies-only
```

**UC2.4: Port Availability Check**
```bash
# Check all required ports are accessible
python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
    --devcontainer-json .devcontainer/devcontainer.json \
    --check-ports-only
```

**UC2.5: CI Environment Validation**
```bash
# Validate CI environment before running tests
python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
    --devcontainer-json .devcontainer/devcontainer.json \
    --timeout 30 \
    --output ci_env_validation.json
```

#### Integration Examples

**DevContainer Lifecycle Hook** (.devcontainer/devcontainer.json):
```json
{
  "postCreateCommand": "bash scripts/validate_devcontainer_env.sh",
  "postStartCommand": "bash scripts/validate_devcontainer_env.sh --quick"
}
```

**Bash Wrapper** (validate_devcontainer_env.sh):
```bash
#!/usr/bin/env bash

QUICK_MODE=${1:---full}

if [ "$QUICK_MODE" == "--quick" ]; then
    # Quick validation (services + versions only)
    python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
        --devcontainer-json .devcontainer/devcontainer.json \
        --check-services-only \
        --check-versions-only
else
    # Full validation
    python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
        --devcontainer-json .devcontainer/devcontainer.json \
        --output /tmp/devcontainer_validation.json
fi

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "DevContainer validation failed!"
    jq . /tmp/devcontainer_validation.json
    exit 1
fi

echo "DevContainer validation passed!"
```

**CI Integration** (.ci-local.yaml):
```yaml
jobs:
  - name: validate_environment
    stage: setup
    script: |
      python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
        --devcontainer-json .devcontainer/devcontainer.json \
        --timeout 30
    allow_failure: false
```

#### Common Scenarios

**Scenario 1: Service Down**
```json
{
  "status": "failure",
  "checks": [
    {
      "status": "fail",
      "message": "PostgreSQL is not available on port 5432",
      "port": 5432,
      "details": {"error": "Connection refused"}
    }
  ]
}
```

**Scenario 2: Version Mismatch**
```json
{
  "status": "failure",
  "checks": [
    {
      "status": "fail",
      "message": "Python version 3.11.0 does not match requirement 3.12.x",
      "details": {"actual": "3.11.0", "required": "3.12.x"}
    }
  ]
}
```

**Scenario 3: Missing Dependency**
```json
{
  "status": "failure",
  "checks": [
    {
      "status": "fail",
      "message": "Required dependency 'yq' not found",
      "dependency": "yq"
    }
  ]
}
```

---

### 3. MetricsCollectorAgent

**Location**: `scripts/coding/ai/automation/metrics_collector_agent.py`
**ADR**: ADR-042
**Responsibility**: Collect and analyze automation system metrics

#### Primary Use Case: Violations Tracking and Trend Analysis

**Scenario**: Team lead wants to understand constitution compliance trends over the last 30 days.

**CLI Example**:
```bash
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --log-file logs/constitucion_violations.log \
    --metrics-type violations \
    --period 30 \
    --output reports/violations_monthly.json \
    --format json
```

**Output**:
```json
{
  "generated_at": "2025-11-13T12:00:00",
  "period_days": 30,
  "violations": {
    "by_rule": {
      "R1_branch_protection": 2,
      "R2_no_emojis": 15,
      "R3_ui_api_coherence": 8,
      "R4_database_router": 0,
      "R5_tests_pass": 5,
      "R6_devcontainer": 3
    },
    "by_severity": {
      "error": 28,
      "warning": 5
    },
    "total": 33,
    "trend": {
      "direction": "decreasing",
      "change_percentage": -25.5,
      "previous_period": 44,
      "current_period": 33
    }
  },
  "top_violations": [
    {
      "rule": "R2_no_emojis",
      "count": 15,
      "percentage": 45.5
    }
  ]
}
```

#### Secondary Use Cases

**UC3.1: CI Pipeline Performance Analysis**
```bash
# Analyze CI pipeline metrics over last 7 days
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --metrics-type ci \
    --period 7 \
    --output reports/ci_weekly.json
```

**Output**:
```json
{
  "ci_metrics": {
    "total_runs": 45,
    "success_rate": 91.1,
    "average_duration_seconds": 185.3,
    "jobs": {
      "lint_ui": {"success_rate": 95.6, "avg_duration": 42.1},
      "test_api": {"success_rate": 88.9, "avg_duration": 120.5}
    }
  }
}
```

**UC3.2: Coverage Trend Analysis**
```bash
# Track code coverage trends
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --metrics-type coverage \
    --period 90 \
    --output reports/coverage_quarterly.json
```

**UC3.3: Developer Compliance Metrics**
```bash
# Identify developers needing constitution training
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --log-file logs/constitucion_violations.log \
    --metrics-type violations \
    --group-by author \
    --period 30
```

**Output**:
```json
{
  "developer_metrics": {
    "developer1": {
      "total_violations": 8,
      "by_rule": {"R2": 5, "R3": 3}
    },
    "developer2": {
      "total_violations": 2,
      "by_rule": {"R5": 2}
    }
  }
}
```

**UC3.4: Weekly Report Generation**
```bash
# Generate weekly compliance report in Markdown
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --log-file logs/constitucion_violations.log \
    --metrics-type all \
    --period 7 \
    --output reports/weekly_report.md \
    --format markdown
```

**UC3.5: Dashboard Data Generation**
```bash
# Generate JSON for dashboard visualization
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --metrics-type all \
    --period 30 \
    --output dashboard/metrics_data.json
```

#### Integration Examples

**Cron Job for Daily Reports**:
```bash
# /etc/cron.d/iact-metrics
0 8 * * * /usr/bin/python3 /workspace/scripts/coding/ai/automation/metrics_collector_agent.py \
    --log-file /workspace/logs/constitucion_violations.log \
    --metrics-type all \
    --period 1 \
    --output /workspace/reports/daily_$(date +\%Y-\%m-\%d).json
```

**Post-Push Hook**:
```bash
# .git/hooks/post-push (local)
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --log-file logs/constitucion_violations.log \
    --metrics-type violations \
    --period 7 \
    --output /tmp/metrics_summary.json

# Display summary
jq '.violations.trend' /tmp/metrics_summary.json
```

**CI Reporting Stage** (.ci-local.yaml):
```yaml
jobs:
  - name: metrics_report
    stage: report
    script: |
      python3 scripts/coding/ai/automation/metrics_collector_agent.py \
        --metrics-type all \
        --period 30 \
        --output reports/ci_metrics.json
    allow_failure: true
```

#### Common Scenarios

**Scenario 1: Improving Compliance**
```json
{
  "violations": {
    "trend": {
      "direction": "decreasing",
      "change_percentage": -35.2,
      "message": "Compliance improving - violations down 35%"
    }
  }
}
```

**Scenario 2: Regressing Compliance**
```json
{
  "violations": {
    "trend": {
      "direction": "increasing",
      "change_percentage": 22.8,
      "message": "Compliance regressing - violations up 23%"
    }
  }
}
```

---

### 4. CoherenceAnalyzerAgent

**Location**: `scripts/coding/ai/automation/coherence_analyzer_agent.py`
**ADR**: ADR-043
**Responsibility**: Analyze UI/API coherence and detect gaps

#### Primary Use Case: Git Diff Analysis for UI/API Changes

**Scenario**: Developer modifies API endpoints and wants to verify UI services and tests are updated.

**CLI Example**:
```bash
python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
    --git-diff HEAD~1 \
    --base-branch main \
    --output /tmp/coherence_report.json \
    --threshold 70.0
```

**Output**:
```json
{
  "status": "success",
  "timestamp": "2025-11-13T12:00:00",
  "summary": {
    "total_api_endpoints": 25,
    "total_ui_services": 20,
    "total_ui_tests": 45,
    "correlation_rate": 80.0,
    "test_coverage_rate": 90.0
  },
  "correlations": [
    {
      "api_endpoint": "UserViewSet",
      "ui_service": "UserService",
      "service_method": "getUsers",
      "test_name": "should fetch users",
      "confidence": 95.0,
      "has_api": true,
      "has_service": true,
      "has_test": true
    }
  ],
  "gaps": {
    "missing_ui_services": [
      {
        "api_endpoint": "ProductViewSet",
        "severity": "warning",
        "message": "No UI service found for API endpoint"
      }
    ],
    "missing_ui_tests": [
      {
        "service_name": "OrderService",
        "severity": "error",
        "message": "No tests found for UI service"
      }
    ]
  },
  "confidence_score": 85.5
}
```

#### Secondary Use Cases

**UC4.1: Pre-Push Validation**
```bash
# Validate coherence before pushing
python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
    --git-diff origin/main \
    --threshold 75.0

exit_code=$?
if [ $exit_code -ne 0 ]; then
    echo "ERROR: UI/API coherence below threshold"
    exit 1
fi
```

**UC4.2: Full Codebase Analysis**
```bash
# Analyze entire codebase (no git diff)
python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
    --analyze-all \
    --output reports/coherence_full.json
```

**UC4.3: Specific Endpoint Analysis**
```bash
# Analyze specific API endpoint
python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
    --endpoint UserViewSet \
    --output /tmp/user_endpoint_analysis.json
```

**UC4.4: Test Gap Detection**
```bash
# Focus on finding missing tests
python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
    --detect-gaps-only \
    --gap-type missing_tests
```

**UC4.5: CI Integration with Blocking**
```bash
# Block PR merge if coherence < 70%
python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
    --git-diff origin/main \
    --threshold 70.0 \
    --fail-on-gaps
```

#### Integration Examples

**Pre-Push Hook** (.git/hooks/pre-push):
```bash
#!/usr/bin/env bash

changed_files=$(git diff --cached --name-only)

if echo "$changed_files" | grep -qE '\.(py|ts|tsx|js)$'; then
    python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
        --git-diff HEAD \
        --threshold 65.0 || exit 1
fi
```

**Bash Wrapper** (check_ui_api_coherence.sh):
```bash
#!/usr/bin/env bash

python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
    --git-diff "${GIT_DIFF_REF:-HEAD~1}" \
    --base-branch "${BASE_BRANCH:-main}" \
    --output /tmp/coherence_report.json \
    --threshold 70.0

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "ERROR: UI/API coherence check failed"
    jq '.gaps' /tmp/coherence_report.json
    exit 1
fi

echo "UI/API coherence check passed ($(jq -r '.confidence_score' /tmp/coherence_report.json)%)"
```

**CI Pipeline** (.ci-local.yaml):
```yaml
jobs:
  - name: coherence-check
    stage: validation
    script: |
      python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
        --git-diff origin/main \
        --threshold 75.0
    allow_failure: false
    on:
      pattern: "**/*.{py,ts,tsx,js}"
```

#### Common Scenarios

**Scenario 1: New API Endpoint Without UI Service**
```json
{
  "gaps": {
    "missing_ui_services": [
      {
        "api_endpoint": "NotificationViewSet",
        "severity": "warning",
        "message": "New API endpoint has no corresponding UI service",
        "recommendation": "Create NotificationService in ui/src/services/"
      }
    ]
  }
}
```

**Scenario 2: UI Service Without Tests**
```json
{
  "gaps": {
    "missing_ui_tests": [
      {
        "service_name": "PaymentService",
        "severity": "error",
        "message": "UI service has no test coverage",
        "recommendation": "Create PaymentService.test.js in ui/src/services/__tests__/"
      }
    ]
  }
}
```

**Scenario 3: Low Confidence Correlation**
```json
{
  "correlations": [
    {
      "api_endpoint": "InvoiceViewSet",
      "ui_service": "BillingService",
      "confidence": 45.0,
      "message": "Low confidence correlation - manual verification recommended"
    }
  ]
}
```

---

### 5. ConstitutionValidatorAgent

**Location**: `scripts/coding/ai/automation/constitution_validator_agent.py`
**ADR**: ADR-044
**Responsibility**: Validate all 6 constitution rules (R1-R6)

#### Primary Use Case: Pre-Push Comprehensive Validation

**Scenario**: Developer runs pre-push hook to validate all constitution rules before pushing to remote.

**CLI Example**:
```bash
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode pre-push \
    --output /tmp/constitution_report.json
```

**Output**:
```json
{
  "status": "success",
  "violations": [],
  "summary": {
    "rules_evaluated": 4,
    "rules_passed": 4,
    "rules_failed": 0,
    "blocking": false
  },
  "rules": {
    "R1_branch_protection": {"status": "pass"},
    "R3_ui_api_coherence": {"status": "pass", "confidence": 85.5},
    "R4_database_router": {"status": "pass"},
    "R5_tests_pass": {"status": "pass", "tests_run": 245, "tests_passed": 245}
  }
}
```

#### Secondary Use Cases

**UC5.1: Pre-Commit Fast Validation (R2 only)**
```bash
# Fast emoji check (< 2 seconds)
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode pre-commit \
    --changed-files "docs/README.md,src/app.py"
```

**UC5.2: DevContainer Initialization (R6 only)**
```bash
# Validate environment on container start
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode devcontainer-init \
    --output /tmp/devcontainer_check.json
```

**UC5.3: CI Full Validation (All Rules)**
```bash
# Validate all rules in CI
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode ci-local \
    --output logs/constitution_validation.json
```

**UC5.4: Manual Selective Validation**
```bash
# Validate specific rules manually
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode manual \
    --rules "R1,R2,R5" \
    --verbose
```

**UC5.5: Dry Run Mode**
```bash
# Check what would be validated without running
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode pre-push \
    --dry-run
```

#### Integration Examples

**Pre-Commit Hook** (.git/hooks/pre-commit):
```bash
#!/usr/bin/env bash
# Fast validation (R2 only - emojis)

changed_files=$(git diff --cached --name-only | tr '\n' ',')

python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode pre-commit \
    --changed-files "$changed_files" \
    --output /tmp/constitution_report.json

exit $?
```

**Pre-Push Hook** (.git/hooks/pre-push):
```bash
#!/usr/bin/env bash
# Comprehensive validation (R1, R3, R4, R5)

python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode pre-push \
    --output /tmp/constitution_report.json

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "Constitution validation failed!"
    jq '.violations' /tmp/constitution_report.json
    exit 1
fi
```

**Bash Wrapper** (constitucion.sh):
```bash
#!/usr/bin/env bash

MODE="$1"
VERBOSE="${2:-false}"

python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode "$MODE" \
    --output "/tmp/constitution_report_$(date +%Y%m%d_%H%M%S).json" \
    $([ "$VERBOSE" == "true" ] && echo "--verbose")

exit_code=$?

status=$(jq -r '.status' "/tmp/constitution_report_*.json" | tail -1)

if [ "$exit_code" -eq 0 ]; then
    echo "All constitution rules passed"
elif [ "$exit_code" -eq 1 ]; then
    echo "Constitution validation failed (blocking)"
    exit 1
elif [ "$exit_code" -eq 2 ]; then
    echo "Constitution validation has warnings (non-blocking)"
fi

exit $exit_code
```

#### Common Scenarios

**Scenario 1: R2 Violation (Emoji Detected)**
```json
{
  "status": "failure",
  "violations": [
    {
      "rule_id": "R2",
      "severity": "error",
      "message": "Emoji detected: '✓'",
      "file": "docs/test.md",
      "line": 42
    }
  ],
  "summary": {
    "blocking": true
  }
}
```

**Scenario 2: R1 Violation (Direct Push to Main)**
```json
{
  "status": "failure",
  "violations": [
    {
      "rule_id": "R1",
      "severity": "error",
      "message": "Direct push to protected branch 'main' is not allowed",
      "file": null,
      "line": null
    }
  ]
}
```

**Scenario 3: R5 Violation (Tests Failed)**
```json
{
  "status": "failure",
  "violations": [
    {
      "rule_id": "R5",
      "severity": "error",
      "message": "Tests failed: 3 of 245 tests failed",
      "details": {
        "tests_run": 245,
        "tests_passed": 242,
        "tests_failed": 3
      }
    }
  ]
}
```

---

### 6. CIPipelineOrchestratorAgent

**Location**: `scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py`
**ADR**: ADR-045
**Responsibility**: Intelligent CI/CD pipeline orchestration

#### Primary Use Case: Full Pipeline Execution

**Scenario**: Developer runs full CI pipeline locally before pushing to ensure all checks pass.

**CLI Example**:
```bash
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --output /tmp/pipeline_report.json
```

**Output**:
```json
{
  "status": "success",
  "timestamp": "2025-11-13T14:30:00",
  "duration_seconds": 185.3,
  "summary": {
    "total_stages": 4,
    "total_jobs": 12,
    "jobs_run": 10,
    "jobs_skipped": 2,
    "jobs_passed": 10,
    "jobs_failed": 0,
    "success_rate": 100.0
  },
  "stages": [
    {
      "name": "lint",
      "status": "success",
      "duration_seconds": 42.1,
      "jobs": [
        {
          "name": "lint_ui",
          "status": "success",
          "duration_seconds": 38.5,
          "exit_code": 0
        },
        {
          "name": "lint_api",
          "status": "success",
          "duration_seconds": 40.2,
          "exit_code": 0
        }
      ]
    }
  ]
}
```

#### Secondary Use Cases

**UC6.1: Smart Detection (Only Changed Components)**
```bash
# Run only jobs relevant to changed files
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --smart-detection \
    --git-diff HEAD~1
```

**UC6.2: Specific Stage Execution**
```bash
# Run only test stage
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --stage test
```

**UC6.3: Specific Job Execution**
```bash
# Run only API tests
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --job test_api
```

**UC6.4: Dry Run (Show Execution Plan)**
```bash
# Show what would run without executing
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --dry-run
```

**Output**:
```json
{
  "dry_run": true,
  "execution_plan": {
    "stages": ["lint", "test", "build", "validate"],
    "total_jobs": 12,
    "parallel_groups": [
      ["lint_ui", "lint_api", "lint_markdown"],
      ["test_ui", "test_api"],
      ["build_ui", "build_api"]
    ]
  }
}
```

**UC6.5: Fail-Fast Disabled**
```bash
# Continue pipeline even if stage fails
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --no-fail-fast
```

**UC6.6: Parallel Execution Control**
```bash
# Limit parallel jobs to 2
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --max-parallel 2
```

#### Integration Examples

**Bash Wrapper** (ci-local.sh):
```bash
#!/usr/bin/env bash

CONFIG="${1:-.ci-local.yaml}"
MODE="${2:-full}"

case "$MODE" in
    "quick")
        # Quick validation (lint only)
        python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
            --config "$CONFIG" \
            --stage lint
        ;;
    "smart")
        # Smart detection based on git diff
        python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
            --config "$CONFIG" \
            --smart-detection \
            --git-diff origin/main
        ;;
    "full")
        # Full pipeline
        python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
            --config "$CONFIG" \
            --output /tmp/ci_report.json
        ;;
    *)
        echo "Unknown mode: $MODE"
        exit 1
        ;;
esac

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "CI pipeline failed!"
    jq '.summary' /tmp/ci_report.json
    exit 1
fi

echo "CI pipeline passed!"
jq '.summary' /tmp/ci_report.json
```

**Pre-Push Hook Integration**:
```bash
#!/usr/bin/env bash
# .git/hooks/pre-push

# Run smart CI pipeline before push
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --smart-detection \
    --git-diff origin/$(git rev-parse --abbrev-ref HEAD)

exit $?
```

**Cron Job (Nightly Full Build)**:
```bash
# /etc/cron.d/iact-nightly-build
0 2 * * * cd /workspace && python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --output /workspace/reports/nightly_$(date +\%Y-\%m-\%d).json
```

#### Common Scenarios

**Scenario 1: Parallel Execution Success**
```json
{
  "stages": [
    {
      "name": "lint",
      "execution_mode": "parallel",
      "duration_seconds": 42.1,
      "jobs": [
        {"name": "lint_ui", "status": "success", "duration": 38.5},
        {"name": "lint_api", "status": "success", "duration": 40.2},
        {"name": "lint_markdown", "status": "success", "duration": 28.3}
      ],
      "message": "All jobs ran in parallel, total time = max(38.5, 40.2, 28.3) = 40.2s"
    }
  ]
}
```

**Scenario 2: Job Skipped (Smart Detection)**
```json
{
  "jobs_skipped": [
    {
      "name": "test_ui",
      "reason": "No UI files changed in git diff",
      "condition": "files_changed: ui/**/*"
    }
  ]
}
```

**Scenario 3: Job Timeout**
```json
{
  "jobs_failed": [
    {
      "name": "build_ui",
      "status": "timeout",
      "message": "Job exceeded timeout of 300 seconds",
      "duration_seconds": 300
    }
  ]
}
```

**Scenario 4: Dependency Resolution**
```json
{
  "execution_plan": {
    "stage_order": ["lint", "test", "build", "validate"],
    "dependencies": {
      "test": ["lint"],
      "build": ["test"],
      "validate": ["build"]
    }
  }
}
```

---

## Workflow Use Cases

### Developer Workflows

#### Workflow 1: Daily Development Cycle

**Scenario**: Developer works on a feature, commits, and pushes code.

**Steps**:
1. **Edit files** (code changes)
2. **Pre-commit hook** (automatic)
   ```bash
   # R2 validation (emojis) - fast < 2s
   ConstitutionValidatorAgent --mode pre-commit
   ```
3. **Commit** (if pre-commit passes)
4. **Pre-push hook** (automatic)
   ```bash
   # R1, R3, R4, R5 validation - comprehensive
   ConstitutionValidatorAgent --mode pre-push
   ```
5. **Push** (if pre-push passes)

**Commands**:
```bash
# Developer workflow
git add .
git commit -m "feat: add user notification feature"
# -> pre-commit runs: ConstitutionValidatorAgent (R2)

git push
# -> pre-push runs: ConstitutionValidatorAgent (R1, R3, R4, R5)
```

#### Workflow 2: Local CI Before Push

**Scenario**: Developer wants to validate all checks locally before pushing.

**Steps**:
1. **Run full CI pipeline**
   ```bash
   ./ci-local.sh
   # -> CIPipelineOrchestratorAgent executes all stages
   ```
2. **Review results**
   ```bash
   jq '.summary' /tmp/ci_report.json
   ```
3. **Fix failures** (if any)
4. **Re-run CI**
5. **Push** (when all green)

**Commands**:
```bash
# Full local CI
./scripts/ci-local.sh

# Smart CI (only changed components)
./scripts/ci-local.sh --smart

# Quick CI (lint only)
./scripts/ci-local.sh --quick
```

#### Workflow 3: API Endpoint Development

**Scenario**: Developer adds new API endpoint and corresponding UI service.

**Steps**:
1. **Create API endpoint** (Django ViewSet)
2. **Create UI service** (TypeScript)
3. **Create UI tests** (Jest)
4. **Validate coherence**
   ```bash
   ./scripts/check_ui_api_coherence.sh
   # -> CoherenceAnalyzerAgent validates correlation
   ```
5. **Fix gaps** (if any missing tests/services)
6. **Commit and push**

**Commands**:
```bash
# After creating API + UI changes
python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
    --git-diff HEAD~1 \
    --threshold 75.0

# Should show high confidence correlation
# If gaps detected, fix before committing
```

#### Workflow 4: DevContainer Troubleshooting

**Scenario**: DevContainer services not responding, need to debug environment.

**Steps**:
1. **Run environment validation**
   ```bash
   ./scripts/validate_devcontainer_env.sh
   # -> DevContainerValidatorAgent checks all services
   ```
2. **Review report**
   ```bash
   jq '.checks[] | select(.status == "fail")' /tmp/devcontainer_validation.json
   ```
3. **Fix identified issues** (restart services, fix config)
4. **Re-validate**

**Commands**:
```bash
# Full validation
python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
    --devcontainer-json .devcontainer/devcontainer.json

# Service-only check
python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
    --devcontainer-json .devcontainer/devcontainer.json \
    --check-services-only
```

---

### CI/CD Workflows

#### Workflow 5: CI Pipeline Execution

**Scenario**: CI system runs full validation on PR or merge.

**Pipeline Stages**:
```yaml
stages:
  1. lint (parallel)
     - lint_ui (ESLint)
     - lint_api (Ruff)
     - lint_markdown

  2. test (parallel, depends on lint)
     - test_ui (Jest)
     - test_api (Pytest)

  3. build (parallel, depends on test)
     - build_ui (Webpack)
     - build_api (collectstatic)

  4. validate (sequential, depends on build)
     - validate_constitution
     - validate_coherence
     - validate_coverage
```

**Execution**:
```bash
# CI system runs
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --output ci_report.json \
    --fail-fast

exit_code=$?

# CI system checks exit code
if [ $exit_code -ne 0 ]; then
    # Mark build as failed
    # Post results to PR
    exit 1
fi
```

#### Workflow 6: Smart CI (Only Changed Components)

**Scenario**: PR only changes UI files, skip API-related jobs.

**Detection Logic**:
```bash
# CIPipelineOrchestratorAgent detects changes
git diff origin/main --name-only

# Files changed: ui/src/components/User.tsx, ui/src/services/UserService.ts
# Smart detection: Run only UI jobs (lint_ui, test_ui, build_ui)
# Skip: lint_api, test_api, build_api
```

**Execution**:
```bash
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --smart-detection \
    --git-diff origin/main

# Result: 50% faster (only 6 jobs run instead of 12)
```

#### Workflow 7: Nightly Full Build

**Scenario**: Run comprehensive validation every night with all checks enabled.

**Cron Configuration**:
```bash
# /etc/cron.d/iact-nightly
0 2 * * * /usr/bin/python3 /workspace/scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config /workspace/.ci-local.yaml \
    --output /workspace/reports/nightly_$(date +\%Y-\%m-\%d).json \
    --no-fail-fast

# Generate metrics report
5 2 * * * /usr/bin/python3 /workspace/scripts/coding/ai/automation/metrics_collector_agent.py \
    --metrics-type all \
    --period 1 \
    --output /workspace/reports/nightly_metrics_$(date +\%Y-\%m-\%d).json
```

---

### DevContainer Workflows

#### Workflow 8: Container Lifecycle Validation

**Scenario**: DevContainer starts and validates environment before allowing development.

**Lifecycle Hooks** (.devcontainer/devcontainer.json):
```json
{
  "postCreateCommand": "bash scripts/validate_devcontainer_env.sh --full",
  "postStartCommand": "bash scripts/validate_devcontainer_env.sh --quick",
  "postAttachCommand": "bash scripts/validate_devcontainer_env.sh --services-only"
}
```

**Execution Flow**:
```
1. Container created
   -> postCreateCommand runs
   -> DevContainerValidatorAgent validates:
      - Services (PostgreSQL, MariaDB)
      - Versions (Python 3.12.x, Node 18.x)
      - Dependencies (yq, jq, git, npm, pip)
      - Ports (5432, 3306, 8000, 3000)
      - Environment variables

2. Container started
   -> postStartCommand runs
   -> Quick validation (services + versions only)

3. User attaches to container
   -> postAttachCommand runs
   -> Service health check only
```

**Example Output**:
```bash
# postCreateCommand
DevContainer validation passed!
- PostgreSQL: OK
- MariaDB: OK
- Python 3.12.1: OK
- Node 18.19.0: OK
- All dependencies: OK
```

#### Workflow 9: Continuous Environment Monitoring

**Scenario**: Monitor DevContainer health during development session.

**Background Monitoring Script**:
```bash
#!/usr/bin/env bash
# scripts/monitor_devcontainer.sh

while true; do
    python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
        --devcontainer-json .devcontainer/devcontainer.json \
        --check-services-only \
        --output /tmp/devcontainer_health.json

    status=$(jq -r '.status' /tmp/devcontainer_health.json)

    if [ "$status" != "success" ]; then
        # Send notification
        echo "WARNING: DevContainer health check failed" | wall
        jq '.checks[] | select(.status == "fail")' /tmp/devcontainer_health.json
    fi

    sleep 300  # Check every 5 minutes
done
```

---

### Manual Validation Workflows

#### Workflow 10: Configuration File Validation

**Scenario**: Developer manually validates configuration files before committing.

**Commands**:
```bash
# Validate .constitucion.yaml
python3 scripts/coding/ai/automation/schema_validator_agent.py \
    --file .constitucion.yaml \
    --schema schemas/constitucion_schema.json \
    --type constitucion

# Validate .ci-local.yaml
python3 scripts/coding/ai/automation/schema_validator_agent.py \
    --file .ci-local.yaml \
    --schema schemas/ci_local_schema.json \
    --type ci_local

# Validate devcontainer.json
python3 scripts/coding/ai/automation/schema_validator_agent.py \
    --file .devcontainer/devcontainer.json \
    --schema schemas/devcontainer_schema.json \
    --type devcontainer
```

#### Workflow 11: Metrics and Reporting

**Scenario**: Team lead generates weekly compliance report.

**Commands**:
```bash
# Generate violations report
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --log-file logs/constitucion_violations.log \
    --metrics-type violations \
    --period 7 \
    --output reports/weekly_violations.json

# Generate CI metrics report
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --metrics-type ci \
    --period 7 \
    --output reports/weekly_ci_metrics.json

# Generate Markdown summary
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --metrics-type all \
    --period 7 \
    --output reports/weekly_summary.md \
    --format markdown

# Review reports
cat reports/weekly_summary.md
```

#### Workflow 12: Selective Constitution Validation

**Scenario**: Developer wants to test specific constitution rules manually.

**Commands**:
```bash
# Test only emoji detection (R2)
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode manual \
    --rules R2 \
    --changed-files "docs/README.md,src/app.py"

# Test only UI/API coherence (R3)
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode manual \
    --rules R3 \
    --verbose

# Test multiple rules
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode manual \
    --rules "R1,R2,R5" \
    --output /tmp/manual_validation.json
```

---

## Hybrid Bash/Python Patterns

### Pattern 1: Bash Entry Point with Python Worker

**Structure**:
```bash
#!/usr/bin/env bash
# Bash entry point (constitucion.sh)

# Parse arguments (Bash)
MODE="$1"
VERBOSE="${2:-false}"

# Invoke Python agent (worker)
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode "$MODE" \
    --output /tmp/report.json \
    $([ "$VERBOSE" == "true" ] && echo "--verbose")

# Capture exit code
exit_code=$?

# Process results (Bash)
if [ $exit_code -eq 0 ]; then
    echo "Validation passed"
else
    jq '.violations' /tmp/report.json
fi

exit $exit_code
```

**Why This Pattern**:
- Bash: CLI parsing, file operations, exit code handling
- Python: Complex validation logic, AST parsing, JSON generation

### Pattern 2: JSON-Based Communication

**Bash -> Python** (input):
```bash
# Bash prepares input
cat > /tmp/input.json <<EOF
{
  "mode": "pre-push",
  "changed_files": ["file1.py", "file2.md"],
  "config": ".constitucion.yaml"
}
EOF

# Python reads JSON input
python3 agent.py --input /tmp/input.json
```

**Python -> Bash** (output):
```bash
# Python writes JSON output
python3 agent.py --output /tmp/output.json

# Bash parses JSON output
status=$(jq -r '.status' /tmp/output.json)
violations=$(jq '.violations | length' /tmp/output.json)

echo "Status: $status, Violations: $violations"
```

### Pattern 3: Exit Code Convention

**Standard Exit Codes**:
```bash
# 0: Success (all checks passed)
# 1: Failure (blocking errors)
# 2: Warnings (non-blocking)
# 3: Configuration error (can't run)

# Python agent returns exit code
python3 agent.py --mode pre-push
exit_code=$?

# Bash handles exit code
case $exit_code in
    0)
        echo "SUCCESS"
        ;;
    1)
        echo "FAILURE (blocking)"
        exit 1
        ;;
    2)
        echo "WARNINGS (non-blocking)"
        ;;
    3)
        echo "CONFIGURATION ERROR"
        exit 3
        ;;
esac
```

### Pattern 4: Async Job Orchestration

**Bash Sequential**:
```bash
# Bash runs sequentially
./lint_ui.sh
./lint_api.sh
./test_ui.sh
./test_api.sh
# Total time: sum of all jobs
```

**Python Async**:
```python
# Python runs in parallel
import asyncio

async def main():
    tasks = [
        run_job("lint_ui"),
        run_job("lint_api"),
        run_job("test_ui"),
        run_job("test_api")
    ]
    results = await asyncio.gather(*tasks)
    # Total time: max of all jobs

asyncio.run(main())
```

### Pattern 5: Git Integration

**Bash Git Operations**:
```bash
# Bash: Git operations (fast, native)
changed_files=$(git diff --cached --name-only)
current_branch=$(git rev-parse --abbrev-ref HEAD)
base_branch="main"

# Pass to Python for analysis
python3 coherence_analyzer_agent.py \
    --git-diff "$base_branch" \
    --changed-files "$changed_files"
```

**Python Git Analysis**:
```python
# Python: Analyze git diff content
import subprocess

def get_git_diff(base_branch):
    result = subprocess.run(
        ["git", "diff", base_branch, "--name-only"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n')

# Detect changed components
changed_files = get_git_diff("main")
ui_changed = any(f.startswith("ui/") for f in changed_files)
api_changed = any(f.startswith("api/") for f in changed_files)
```

---

## Common Scenarios

### Scenario 1: First-Time DevContainer Setup

**User**: New developer joining project

**Steps**:
1. Clone repository
2. Open in DevContainer
3. Container builds and starts
4. `postCreateCommand` runs:
   ```bash
   DevContainerValidatorAgent validates environment
   ```
5. Validation passes or fails with specific errors
6. Developer fixes issues if any
7. Ready to develop

**Outcome**: Developer has validated, working environment in < 10 minutes

### Scenario 2: Breaking Constitution Rule in Pre-Commit

**User**: Developer accidentally includes emoji in code comment

**Flow**:
```bash
git add src/app.py  # Contains: print("Task complete ✓")
git commit -m "fix: resolve bug"

# Pre-commit hook runs
ConstitutionValidatorAgent --mode pre-commit
# -> Detects emoji in src/app.py line 42
# -> Exit code 1 (blocking)

# Commit rejected
# Error message: "Emoji detected: '✓' in src/app.py:42"

# Developer fixes
# Removes emoji
git add src/app.py
git commit -m "fix: resolve bug"
# -> Passes
```

### Scenario 3: CI Pipeline Failure Due to Missing UI Tests

**User**: Developer adds API endpoint but forgets UI tests

**Flow**:
```bash
# Developer commits API changes
git commit -m "feat: add notification endpoint"
git push

# Pre-push hook runs
ConstitutionValidatorAgent --mode pre-push
# -> R3 (UI/API coherence) validation

# CoherenceAnalyzerAgent detects gap
# -> API endpoint: NotificationViewSet
# -> UI service: NotificationService (exists)
# -> UI tests: MISSING

# Pre-push fails with message:
# "ERROR: UI service NotificationService has no tests"

# Developer adds tests
# Creates NotificationService.test.js
git add ui/src/services/__tests__/NotificationService.test.js
git commit --amend
git push
# -> Passes
```

### Scenario 4: Metrics Show Increasing Violations

**User**: Team lead reviewing weekly metrics

**Flow**:
```bash
# Generate weekly report
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --log-file logs/constitucion_violations.log \
    --metrics-type violations \
    --period 7 \
    --output reports/weekly_violations.json

# Review results
jq '.violations.trend' reports/weekly_violations.json
```

**Output**:
```json
{
  "direction": "increasing",
  "change_percentage": 22.8,
  "previous_period": 18,
  "current_period": 23,
  "message": "Violations increased by 23%"
}
```

**Action**: Team lead schedules constitution training session

### Scenario 5: Smart CI Skips Unnecessary Jobs

**User**: Developer changes only documentation files

**Flow**:
```bash
# Developer edits docs only
git add docs/README.md
git commit -m "docs: update setup guide"
git push

# Pre-push runs CI
CIPipelineOrchestratorAgent --smart-detection --git-diff origin/main

# Smart detection analyzes:
# - Changed files: docs/README.md
# - Pattern match: docs/**/*.md
# - Jobs to run: lint_markdown
# - Jobs to skip: lint_ui, lint_api, test_ui, test_api, build_ui, build_api

# Pipeline completes in 30s instead of 5min
```

---

## Integration Examples

### Example 1: Complete Pre-Push Workflow

**File**: `.git/hooks/pre-push`
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Running pre-push validations..."

# Step 1: Validate constitution
echo "1/3 Validating constitution rules..."
python3 scripts/coding/ai/automation/constitution_validator_agent.py \
    --mode pre-push \
    --output /tmp/constitution_report.json

if [ $? -ne 0 ]; then
    echo "Constitution validation failed!"
    jq '.violations' /tmp/constitution_report.json
    exit 1
fi

# Step 2: Run CI pipeline
echo "2/3 Running CI pipeline..."
python3 scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py \
    --config .ci-local.yaml \
    --smart-detection \
    --git-diff origin/main \
    --output /tmp/ci_report.json

if [ $? -ne 0 ]; then
    echo "CI pipeline failed!"
    jq '.summary' /tmp/ci_report.json
    exit 1
fi

# Step 3: Validate coherence
echo "3/3 Validating UI/API coherence..."
python3 scripts/coding/ai/automation/coherence_analyzer_agent.py \
    --git-diff origin/main \
    --threshold 70.0 \
    --output /tmp/coherence_report.json

if [ $? -ne 0 ]; then
    echo "Coherence validation failed!"
    jq '.gaps' /tmp/coherence_report.json
    exit 1
fi

echo "All pre-push validations passed!"
```

### Example 2: DevContainer Full Validation

**File**: `scripts/validate_devcontainer_env.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Validating DevContainer environment..."

# Full validation
python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
    --devcontainer-json .devcontainer/devcontainer.json \
    --output /tmp/devcontainer_validation.json \
    --strict

exit_code=$?

if [ $exit_code -eq 0 ]; then
    echo "DevContainer validation PASSED"
    jq -r '.checks[] | "\(.status | ascii_upcase): \(.message)"' /tmp/devcontainer_validation.json
else
    echo "DevContainer validation FAILED"
    echo "Failed checks:"
    jq -r '.checks[] | select(.status == "fail") | "  - \(.message)"' /tmp/devcontainer_validation.json
    exit 1
fi
```

### Example 3: Weekly Metrics Report

**File**: `scripts/generate_weekly_report.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail

REPORT_DIR="reports/weekly_$(date +%Y-%U)"
mkdir -p "$REPORT_DIR"

echo "Generating weekly reports..."

# Violations report
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --log-file logs/constitucion_violations.log \
    --metrics-type violations \
    --period 7 \
    --output "$REPORT_DIR/violations.json"

# CI metrics report
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --metrics-type ci \
    --period 7 \
    --output "$REPORT_DIR/ci_metrics.json"

# Coverage report
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --metrics-type coverage \
    --period 7 \
    --output "$REPORT_DIR/coverage.json"

# Generate Markdown summary
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --metrics-type all \
    --period 7 \
    --output "$REPORT_DIR/summary.md" \
    --format markdown

echo "Reports generated in $REPORT_DIR"
cat "$REPORT_DIR/summary.md"
```

---

## Summary

This document provides comprehensive use cases for the IACT automation system. Key takeaways:

1. **6 Specialized Agents**: Each agent has clear responsibilities and use cases
2. **Hybrid Architecture**: Bash for entry points, Python for complex logic
3. **Multiple Workflows**: Developer, CI/CD, DevContainer, manual validation
4. **Common Patterns**: JSON communication, exit codes, async orchestration
5. **Real-World Scenarios**: Pre-commit hooks, CI pipelines, metrics reporting

For implementation details, see:
- **Architecture**: `docs/devops/automatizacion/planificacion/AGENTS_ARCHITECTURE.md`
- **ADRs**: `docs/adr/ADR-040` through `ADR-045`
- **Integration Guide**: `docs/devops/automatizacion/INTEGRATION_GUIDE.md`

---

**Last Updated**: 2025-11-13
**Version**: 1.0
**Maintained By**: DevOps Team
