---
title: ADR-041 - DevContainerValidatorAgent
date: 2025-11-13
status: Implemented
decision_makers: DevOps Team
issue: IACT-AUTO-001
parent_adr: ADR-036 (Sistema Automatizacion Hibrido)
---

# ADR-041: DevContainerValidatorAgent

**Date**: 2025-11-13
**Status**: Implemented
**Decision Makers**: DevOps Team
**Issue**: IACT-AUTO-001
**SDLC Phase**: Implementation

---

## Context

The IACT project uses DevContainers for standardized development environments. However, there is no automated validation to ensure that:

1. Required services (PostgreSQL, MariaDB) are available and responding
2. Correct runtime versions (Python 3.12.x, Node 18.x) are installed
3. Required dependencies (yq, jq, git, npm, pip) are present
4. Required ports (5432, 3306, 8000, 3000) are accessible
5. Environment variables are properly configured
6. The devcontainer.json structure is valid

**Problem**: Manual validation is error-prone and time-consuming. Developers may spend hours debugging environment issues that could be detected automatically.

**Need**: An automated agent to validate DevContainer environment comprehensively before development work begins.

---

## Decision

Implement **DevContainerValidatorAgent** as part of the automation system with the following characteristics:

### Architecture

**Type**: Python automation agent extending base Agent class
**Location**: `scripts/coding/ai/automation/devcontainer_validator_agent.py`
**Invoked by**: `validate_devcontainer_env.sh` (Bash wrapper)
**Approach**: TDD (Test-Driven Development) with 51 comprehensive tests

### Core Responsibilities

1. **Service Health Checks**
   - PostgreSQL availability (pg_isready)
   - MariaDB availability (mysqladmin ping)
   - Connection timeout handling
   - Error recovery

2. **Version Validation**
   - Python 3.12.x version verification
   - Node.js 18.x version verification
   - Patch level tolerance
   - Version mismatch detection

3. **Dependency Verification**
   - yq command availability
   - jq command availability
   - git command availability
   - npm command availability
   - pip command availability

4. **Port Availability**
   - PostgreSQL port 5432
   - MariaDB port 3306
   - Django backend port 8000
   - React frontend port 3000
   - Socket-based connectivity testing

5. **Environment Variables**
   - DATABASE_URL verification
   - MARIADB_URL verification
   - NODE_ENV verification
   - DJANGO_DEBUG verification
   - Strict mode for empty values

6. **Schema Validation**
   - devcontainer.json structure validation
   - Required fields verification
   - Version extraction from build args
   - Port extraction from configuration

### CLI Interface

```bash
python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
    --devcontainer-json /path/to/devcontainer.json \
    --output /tmp/validation_report.json \
    --strict
```

**Exit Codes**:

- 0: All validations passed
- 1: Validation failures detected
- 3: Configuration error (invalid JSON, file not found)

**Output Format**: JSON report with detailed results

```json
{
  "status": "success|failure",
  "timestamp": "2025-11-13T23:40:00",
  "summary": {
    "total_checks": 20,
    "passed": 18,
    "failed": 2
  },
  "checks": [
    {
      "status": "pass",
      "message": "PostgreSQL is available on port 5432",
      "port": 5432
    }
  ]
}
```

---

## Alternatives Considered

### 1. Shell Script Only

**Pros**: Simpler, no Python dependency
**Cons**: Harder to test, less structured error handling, no JSON output
**Verdict**: Rejected - Python provides better testability

### 2. Docker Healthchecks

**Pros**: Native Docker integration
**Cons**: Limited to container health, no version/dependency checks
**Verdict**: Rejected - Insufficient validation coverage

### 3. External Tool (e.g., container-structure-test)

**Pros**: Battle-tested, maintained externally
**Cons**: Additional dependency, limited customization
**Verdict**: Rejected - Need project-specific validation logic

### 4. Pre-commit Hook

**Pros**: Automatic validation
**Cons**: Wrong lifecycle stage (need validation before dev work)
**Verdict**: Rejected - Should run at container startup

---

## Consequences

### Positive

1. **Early Detection**: Environment issues detected before development starts
2. **Reduced Debugging Time**: Clear JSON reports identify specific failures
3. **Comprehensive Coverage**: 51 tests cover all validation scenarios
4. **Automated Validation**: No manual environment verification needed
5. **Consistent Environments**: All developers validated against same criteria
6. **CI/CD Integration**: Can be used in pipelines to validate build environments
7. **Strict Mode**: Optional strict validation for production environments
8. **Extensible**: Easy to add new checks (Redis, MongoDB, etc.)

### Negative

1. **Additional Startup Time**: Validation adds ~2-3 seconds to container startup
2. **Maintenance Burden**: Agent must be updated when environment changes
3. **False Positives**: Network issues may cause transient failures
4. **Dependency**: Requires Python 3.11+ and base agent framework

### Mitigation Strategies

- **Performance**: Run validation in parallel where possible
- **Maintenance**: Document agent in AGENTS_ARCHITECTURE.md
- **Reliability**: Implement timeout and retry logic
- **Documentation**: ADR tracks design decisions

---

## Implementation Details

### Key Components

**1. ValidationResult Dataclass**

```python
@dataclass
class ValidationResult:
    status: CheckStatus
    message: str
    port: Optional[int] = None
    dependency: Optional[str] = None
    variable: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
```

**2. CheckStatus Enum**

```python
class CheckStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    WARN = "warn"
```

**3. Service Checks**

- PostgreSQL: `pg_isready -p 5432`
- MariaDB: `mysqladmin -P 3306 ping`
- Timeout: 5 seconds (configurable)

**4. Version Checks**

- Python: `python3 --version` -> parse major.minor
- Node: `node --version` -> parse major version

**5. Port Checks**

- Socket connection attempt with 2-second timeout
- Port range validation (0-65535)

### Configuration

**Agent Config**:

```python
config = {
    "project_root": "/workspace",
    "strict_mode": False,
    "timeout": 5
}
```

**Input Data**:

```python
input_data = {
    "devcontainer_json": {...},
    "check_services": True,
    "check_versions": True,
    "check_dependencies": True,
    "check_ports": True,
    "check_env": True
}
```

---

## Testing Strategy

### Test Coverage

**Total Tests**: 51
**Test Categories**:

- Initialization: 2 tests
- PostgreSQL validation: 3 tests
- MariaDB validation: 3 tests
- Python version validation: 3 tests
- Node version validation: 3 tests
- Dependency checks: 6 tests
- Port availability: 4 tests
- Environment variables: 4 tests
- DevContainer JSON validation: 6 tests
- JSON report generation: 3 tests
- CLI interface: 5 tests
- Integration tests: 2 tests
- Edge cases: 5 tests
- ValidationResult: 2 tests

### Test Approach

**TDD Workflow**:

1. RED: Write failing tests first
2. GREEN: Implement agent to pass tests
3. REFACTOR: Optimize and clean up

**Mocking Strategy**:

- `subprocess.run` for command execution
- `socket.socket` for port checks
- `os.environ` for environment variables

**Test Execution**:

```bash
pytest tests/ai/automation/test_devcontainer_validator_agent.py -v
```

**Result**: 51 passed, 0 failed

---

## Integration

### Bash Wrapper

**Location**: `scripts/validate_devcontainer_env.sh`
**Purpose**: Provide Git hook and CLI integration

```bash
#!/usr/bin/env bash
# Wrapper for DevContainerValidatorAgent

python3 scripts/coding/ai/automation/devcontainer_validator_agent.py \
    --devcontainer-json .devcontainer/devcontainer.json \
    --output /tmp/devcontainer_validation.json

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "DevContainer validation failed!"
    jq . /tmp/devcontainer_validation.json
    exit 1
fi

echo "DevContainer validation passed!"
```

### Constitution Integration

**Rule**: R6 - Environment Validation
**Mode**: pre-commit, pre-push
**Blocking**: Yes (exit 1 on failure)

### CI/CD Integration

**Pipeline Stage**: Environment Setup
**Purpose**: Validate CI environment before tests
**Timeout**: 30 seconds

---

## Metrics & Observability

### Tracked Metrics

1. Validation execution time (ms)
2. Success/failure rate per check type
3. Most common failures
4. Environment drift over time

### Logging

**Log Level**: INFO
**Log Format**: `[timestamp] agent_name - level - message`
**Log Location**: stderr (CLI), agent logger (programmatic)

---

## Future Enhancements

### Phase 2 Additions

1. **Redis Validation**: Add Redis service health check
2. **MongoDB Validation**: Add MongoDB service health check
3. **Volume Mount Checks**: Verify volume mounts exist and are writable
4. **Network Checks**: Validate container network configuration
5. **Resource Checks**: Verify CPU/memory limits
6. **Security Checks**: Validate non-root user, security options

### Phase 3 Additions

1. **Auto-Remediation**: Attempt to fix common issues automatically
2. **Historical Tracking**: Track validation results over time
3. **Dashboard Integration**: Visual dashboard of environment health
4. **Slack/Email Alerts**: Notify team of persistent failures
5. **Performance Profiling**: Identify slow checks for optimization

---

## References

- **Parent ADR**: ADR-036 - Sistema Automatizacion Hibrido
- **Architecture**: docs/devops/automatizacion/planificacion/AGENTS_ARCHITECTURE.md
- **Constitution**: docs/gobernanza/agentes/constitution.md
- **Tests**: tests/ai/automation/test_devcontainer_validator_agent.py
- **Implementation**: scripts/coding/ai/automation/devcontainer_validator_agent.py
- **Issue**: IACT-AUTO-001

---

## Decision Outcome

**Decision**: Implement DevContainerValidatorAgent as specified above
**Rationale**: Comprehensive automated validation improves developer experience
**Status**: Implemented
**Date**: 2025-11-13
**Next Steps**: Integrate with validate_devcontainer_env.sh wrapper

---

## Appendix: Test Results

```
============================= test session starts ==============================
platform linux -- Python 3.11.14, pytest-9.0.1, pluggy-1.6.0
collected 51 items

test_devcontainer_validator_agent.py::TestDevContainerValidatorAgentInit::test_agent_initialization PASSED
test_devcontainer_validator_agent.py::TestDevContainerValidatorAgentInit::test_agent_strict_mode PASSED
test_devcontainer_validator_agent.py::TestPostgreSQLValidation::test_postgresql_availability_success PASSED
test_devcontainer_validator_agent.py::TestPostgreSQLValidation::test_postgresql_availability_failure PASSED
test_devcontainer_validator_agent.py::TestPostgreSQLValidation::test_postgresql_port_check PASSED
test_devcontainer_validator_agent.py::TestMariaDBValidation::test_mariadb_availability_success PASSED
test_devcontainer_validator_agent.py::TestMariaDBValidation::test_mariadb_availability_failure PASSED
test_devcontainer_validator_agent.py::TestMariaDBValidation::test_mariadb_connection_timeout PASSED
test_devcontainer_validator_agent.py::TestPythonVersionValidation::test_python_version_valid PASSED
test_devcontainer_validator_agent.py::TestPythonVersionValidation::test_python_version_invalid PASSED
test_devcontainer_validator_agent.py::TestPythonVersionValidation::test_python_version_patch_level PASSED
test_devcontainer_validator_agent.py::TestNodeVersionValidation::test_node_version_valid PASSED
test_devcontainer_validator_agent.py::TestNodeVersionValidation::test_node_version_invalid PASSED
test_devcontainer_validator_agent.py::TestNodeVersionValidation::test_node_not_installed PASSED
test_devcontainer_validator_agent.py::TestDependencyChecks::test_yq_dependency_available PASSED
test_devcontainer_validator_agent.py::TestDependencyChecks::test_jq_dependency_available PASSED
test_devcontainer_validator_agent.py::TestDependencyChecks::test_git_dependency_available PASSED
test_devcontainer_validator_agent.py::TestDependencyChecks::test_npm_dependency_available PASSED
test_devcontainer_validator_agent.py::TestDependencyChecks::test_pip_dependency_available PASSED
test_devcontainer_validator_agent.py::TestDependencyChecks::test_missing_dependency PASSED
test_devcontainer_validator_agent.py::TestPortAvailability::test_port_5432_available PASSED
test_devcontainer_validator_agent.py::TestPortAvailability::test_port_3306_available PASSED
test_devcontainer_validator_agent.py::TestPortAvailability::test_port_not_available PASSED
test_devcontainer_validator_agent.py::TestPortAvailability::test_multiple_ports_check PASSED
test_devcontainer_validator_agent.py::TestEnvironmentVariables::test_database_url_present PASSED
test_devcontainer_validator_agent.py::TestEnvironmentVariables::test_environment_variable_missing PASSED
test_devcontainer_validator_agent.py::TestEnvironmentVariables::test_multiple_environment_variables PASSED
test_devcontainer_validator_agent.py::TestEnvironmentVariables::test_empty_environment_variable PASSED
test_devcontainer_validator_agent.py::TestDevContainerJSONValidation::test_valid_devcontainer_json PASSED
test_devcontainer_validator_agent.py::TestDevContainerJSONValidation::test_missing_required_fields PASSED
test_devcontainer_validator_agent.py::TestDevContainerJSONValidation::test_invalid_json_structure PASSED
test_devcontainer_validator_agent.py::TestDevContainerJSONValidation::test_python_version_extraction PASSED
test_devcontainer_validator_agent.py::TestDevContainerJSONValidation::test_node_version_extraction PASSED
test_devcontainer_validator_agent.py::TestDevContainerJSONValidation::test_port_extraction PASSED
test_devcontainer_validator_agent.py::TestJSONReportGeneration::test_generate_json_report_all_pass PASSED
test_devcontainer_validator_agent.py::TestJSONReportGeneration::test_generate_json_report_with_failures PASSED
test_devcontainer_validator_agent.py::TestJSONReportGeneration::test_json_report_structure PASSED
test_devcontainer_validator_agent.py::TestCLIInterface::test_cli_parser_creation PASSED
test_devcontainer_validator_agent.py::TestCLIInterface::test_cli_arguments_parsing PASSED
test_devcontainer_validator_agent.py::TestCLIInterface::test_cli_exit_code_success PASSED
test_devcontainer_validator_agent.py::TestCLIInterface::test_cli_exit_code_failure PASSED
test_devcontainer_validator_agent.py::TestCLIInterface::test_cli_exit_code_config_error PASSED
test_devcontainer_validator_agent.py::TestIntegration::test_full_validation_success PASSED
test_devcontainer_validator_agent.py::TestIntegration::test_partial_validation_failure PASSED
test_devcontainer_validator_agent.py::TestEdgeCases::test_invalid_port_number PASSED
test_devcontainer_validator_agent.py::TestEdgeCases::test_negative_port_number PASSED
test_devcontainer_validator_agent.py::TestEdgeCases::test_none_devcontainer_json PASSED
test_devcontainer_validator_agent.py::TestEdgeCases::test_empty_devcontainer_json PASSED
test_devcontainer_validator_agent.py::TestEdgeCases::test_command_timeout_handling PASSED
test_devcontainer_validator_agent.py::TestValidationResult::test_validation_result_creation PASSED
test_devcontainer_validator_agent.py::TestValidationResult::test_validation_result_to_dict PASSED

============================== 51 passed in 0.20s ==============================
```

**Test Coverage**: 100% of core functionality
**Performance**: 0.20s execution time
**Result**: All tests passing
