---
title: Automation System Documentation - IACT Project
date: 2025-11-13
status: Active
version: 1.0
---

# IACT Automation System Documentation

**Version**: 1.0
**Date**: 2025-11-13
**Status**: Production Ready

---

## Overview

The IACT automation system is a comprehensive, hybrid Bash/Python solution for enforcing code quality, running CI/CD pipelines, validating environments, and collecting metrics.

**Key Components**:
- 6 specialized Python agents
- Bash wrapper scripts for integration
- Git hooks for automatic validation
- DevContainer lifecycle integration
- CI/CD pipeline orchestration

---

## Quick Links

### Core Documentation

- **USE_CASES.md** - Comprehensive use cases for all agents and workflows
- **INTEGRATION_GUIDE.md** - Integration patterns, configuration, and troubleshooting
- **AGENTS_ARCHITECTURE.md** (planificacion/) - System architecture and design decisions

### Architecture Decision Records (ADRs)

- **ADR-040** - SchemaValidatorAgent (YAML/JSON validation)
- **ADR-041** - DevContainerValidatorAgent (environment validation)
- **ADR-042** - MetricsCollectorAgent (metrics collection and analysis)
- **ADR-043** - CoherenceAnalyzerAgent (UI/API coherence analysis)
- **ADR-044** - ConstitutionValidatorAgent (constitution rules R1-R6)
- **ADR-045** - CIPipelineOrchestratorAgent (CI pipeline orchestration)

### Planning Documents

Located in `docs/devops/automatizacion/planificacion/`:
- **HLD_SISTEMA_AUTOMATIZACION.md** - High-level design
- **DEPLOYMENT_PLAN.md** - Deployment strategy
- **TESTING_PLAN.md** - Testing approach
- **MAINTENANCE_PLAN.md** - Maintenance procedures

---

## System Architecture

```
User/Git Hook
    |
    v
Bash Entry Point (constitucion.sh, ci-local.sh, etc.)
    |
    v
Python Agent (6 specialized agents)
    |
    v
Validation Logic / Metrics / Reports
    |
    v
JSON Output
    |
    v
Bash (parse results, handle exit codes)
    |
    v
Exit Code to Caller
```

---

## The 6 Agents

### 1. SchemaValidatorAgent
**Purpose**: Validate YAML/JSON configuration files against JSON schemas
**Location**: `scripts/coding/ai/automation/schema_validator_agent.py`
**Use Cases**: Constitution schema validation, CI config validation, DevContainer validation

### 2. DevContainerValidatorAgent
**Purpose**: Comprehensive DevContainer environment validation
**Location**: `scripts/coding/ai/automation/devcontainer_validator_agent.py`
**Use Cases**: Service health checks, version validation, dependency verification, port availability

### 3. MetricsCollectorAgent
**Purpose**: Collect and analyze automation system metrics
**Location**: `scripts/coding/ai/automation/metrics_collector_agent.py`
**Use Cases**: Violations tracking, CI metrics, coverage trends, developer compliance metrics

### 4. CoherenceAnalyzerAgent
**Purpose**: Analyze UI/API coherence and detect gaps
**Location**: `scripts/coding/ai/automation/coherence_analyzer_agent.py`
**Use Cases**: Git diff analysis, endpoint change detection, test gap detection, correlation analysis

### 5. ConstitutionValidatorAgent
**Purpose**: Validate all 6 constitution rules (R1-R6)
**Location**: `scripts/coding/ai/automation/constitution_validator_agent.py`
**Use Cases**: Pre-commit validation, pre-push validation, CI validation, manual validation

### 6. CIPipelineOrchestratorAgent
**Purpose**: Intelligent CI/CD pipeline orchestration
**Location**: `scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py`
**Use Cases**: Full pipeline execution, smart detection, stage/job filtering, parallel execution

---

## Quick Start

### Developer Daily Workflow

```bash
# 1. Make changes to code
vim src/app.py

# 2. Commit (pre-commit hook validates R2: emojis)
git add .
git commit -m "feat: add new feature"
# -> ConstitutionValidatorAgent runs automatically

# 3. Push (pre-push hook validates R1, R3, R4, R5)
git push
# -> ConstitutionValidatorAgent + CIPipelineOrchestratorAgent run automatically
```

### Manual Validation

```bash
# Validate constitution
./scripts/constitucion.sh --mode=manual

# Run CI pipeline
./scripts/ci-local.sh

# Check UI/API coherence
./scripts/check_ui_api_coherence.sh

# Validate DevContainer environment
./scripts/validate_devcontainer_env.sh

# Validate configuration schema
./scripts/validate_constitution_schema.sh .constitucion.yaml
```

### Metrics and Reporting

```bash
# Generate weekly compliance report
python3 scripts/coding/ai/automation/metrics_collector_agent.py \
    --log-file logs/constitucion_violations.log \
    --metrics-type all \
    --period 7 \
    --output reports/weekly_report.md \
    --format markdown
```

---

## Configuration Files

### .constitucion.yaml
Defines constitution principles and rules (R1-R6)

### .ci-local.yaml
Defines CI/CD pipeline stages, jobs, and dependencies

### .devcontainer/devcontainer.json
Defines DevContainer configuration and lifecycle hooks

### schemas/*.json
JSON schemas for validation (constitucion_schema.json, ci_local_schema.json)

---

## Workflows

### Pre-Commit Hook
- **Speed**: < 2 seconds
- **Rules**: R2 (emoji detection)
- **Agent**: ConstitutionValidatorAgent

### Pre-Push Hook
- **Speed**: < 30 seconds
- **Rules**: R1, R3, R4, R5
- **Agents**: ConstitutionValidatorAgent, CIPipelineOrchestratorAgent

### DevContainer Lifecycle
- **postCreateCommand**: Full environment validation
- **postStartCommand**: Quick validation (services + versions)
- **postAttachCommand**: Service health check
- **Agent**: DevContainerValidatorAgent

### CI Pipeline
- **Stages**: lint, test, build, validate
- **Execution**: Parallel with dependency resolution
- **Smart Detection**: Only run jobs for changed components
- **Agent**: CIPipelineOrchestratorAgent

---

## Testing

All agents follow TDD (Test-Driven Development) approach:

- **SchemaValidatorAgent**: 23 tests (100% pass)
- **DevContainerValidatorAgent**: 51 tests (100% pass)
- **MetricsCollectorAgent**: 25 tests (100% pass)
- **CoherenceAnalyzerAgent**: 50 tests (100% pass)
- **ConstitutionValidatorAgent**: 50+ tests (100% pass)
- **CIPipelineOrchestratorAgent**: 52 tests (100% pass)

**Total**: 250+ tests across all agents

---

## Exit Codes

Standard exit codes for all agents:

- **0**: Success (all checks passed)
- **1**: Failure (blocking errors detected)
- **2**: Warnings (non-blocking issues)
- **3**: Configuration error (cannot run)

---

## Logging

### Python Agents
```
[2025-11-13 12:00:00] agent_name - INFO - Starting validation
[2025-11-13 12:00:05] agent_name - WARNING - Deprecated config found
[2025-11-13 12:00:10] agent_name - ERROR - Validation failed
```

### Bash Scripts
```
[INFO] Starting CI pipeline
[OK] Tests passed
[WARN] Low coverage detected
[ERROR] Build failed
```

---

## Documentation Structure

```
docs/devops/automatizacion/
├── README.md                          # This file
├── USE_CASES.md                       # Comprehensive use cases (all agents)
├── INTEGRATION_GUIDE.md               # Integration patterns and troubleshooting
│
├── planificacion/
│   ├── AGENTS_ARCHITECTURE.md         # System architecture
│   ├── HLD_SISTEMA_AUTOMATIZACION.md  # High-level design
│   ├── DEPLOYMENT_PLAN.md             # Deployment strategy
│   ├── TESTING_PLAN.md                # Testing approach
│   └── MAINTENANCE_PLAN.md            # Maintenance procedures
│
└── [git_hooks, constitucion, validaciones folders]
```

---

## Support and Troubleshooting

### Common Issues

1. **Python not found**: Ensure Python 3.11+ is installed
2. **JSON parsing fails**: Verify output file exists and is valid JSON
3. **Git hook not executing**: Check permissions (`chmod +x .git/hooks/*`)
4. **DevContainer validation fails**: Verify services are running (`docker ps`)
5. **Permission denied**: Use alternative output directory

See **INTEGRATION_GUIDE.md** for detailed troubleshooting.

### Debug Mode

```bash
# Enable verbose logging
set -x  # Bash
python3 agent.py --verbose  # Python

# Check logs
tail -f ~/.automation-logs/agents.log
```

---

## Metrics and Observability

### Tracked Metrics

- Violations by rule (R1-R6)
- Violations by severity (error/warning)
- Violations trend (increasing/decreasing)
- CI pipeline success rate
- CI pipeline duration
- Code coverage trends
- Developer compliance metrics

### Reports Generated

- JSON reports (programmatic consumption)
- Markdown summaries (human-readable)
- Weekly compliance reports
- Monthly trend analysis
- Nightly build reports

---

## Key Features

### Hybrid Architecture
- Bash for entry points and Git integration
- Python for complex logic and async operations
- Best of both worlds

### Intelligent Validation
- AST parsing (Python, JavaScript/TypeScript)
- Confidence scoring (0-100%)
- Gap detection (missing tests, missing services)
- Reference validation

### Smart CI/CD
- Parallel execution (50-70% faster)
- Smart detection (skip irrelevant jobs)
- Dependency resolution
- Fail-fast logic
- Timeout handling

### Comprehensive Metrics
- Trend analysis
- Historical tracking
- Developer attribution
- Dashboard data generation

### DevContainer Integration
- Lifecycle hooks (postCreateCommand, postStartCommand)
- Service health checks
- Version validation
- Dependency verification

---

## References

### Code Locations

- **Agents**: `scripts/coding/ai/automation/*.py`
- **Bash Scripts**: `scripts/*.sh`
- **Git Hooks**: `.git/hooks/*`
- **Tests**: `tests/ai/automation/test_*_agent.py`
- **Schemas**: `schemas/*.json`
- **Configurations**: `.constitucion.yaml`, `.ci-local.yaml`

### Documentation

- **ADRs**: `docs/adr/ADR-040` through `ADR-045`
- **Planning**: `docs/devops/automatizacion/planificacion/`
- **Use Cases**: `docs/devops/automatizacion/USE_CASES.md`
- **Integration**: `docs/devops/automatizacion/INTEGRATION_GUIDE.md`

---

## Contribution

### Adding New Agent

1. Create agent in `scripts/coding/ai/automation/`
2. Write tests in `tests/ai/automation/`
3. Follow TDD approach (RED-GREEN-REFACTOR)
4. Document in ADR (`docs/adr/ADR-XXX-agent-name.md`)
5. Update USE_CASES.md with new use cases
6. Update INTEGRATION_GUIDE.md with integration patterns

### Modifying Existing Agent

1. Add tests for new functionality
2. Implement changes
3. Ensure all tests pass
4. Update documentation (ADR, USE_CASES.md)
5. Update version in agent file

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-13 | Initial documentation with all 6 agents |

---

## Contact

**Maintained By**: DevOps Team
**Project**: IACT---project
**Issue Tracker**: IACT-AUTO-001

---

**Last Updated**: 2025-11-13
**Status**: Production Ready
**Next Review**: 2025-12-13 (Monthly review)
