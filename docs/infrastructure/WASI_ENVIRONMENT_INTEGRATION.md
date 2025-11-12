# WASI Scripts + Environment Config Integration

## Overview

This document describes how to integrate the WASI-style virtualization scripts (bash) with the Python environment configuration system (`environment_config.py`).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Application Layer                      │
│  (Python: Django, React, SDLC Agents, Tests)            │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│           Environment Config (Python)                    │
│  scripts/ai/shared/environment_config.py                 │
│  - Auto-detects: development/staging/production          │
│  - Provides DB configs, LLM configs, cache configs       │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│         WASI Virtualization Scripts (Bash)               │
│  scripts/infrastructure/wasi/                            │
│  - lightweight_venv.sh (bash-only, like Python venv)    │
│  - virtualize.sh (Docker-based)                          │
│  - wasm_style_sandbox.sh (Linux namespaces)             │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────────────┐
│              Infrastructure Layer                        │
│  (PostgreSQL, MySQL, Redis, Services)                   │
└─────────────────────────────────────────────────────────┘
```

## Integration Patterns

### Pattern 1: Python Calls WASI Scripts

Python code can invoke WASI scripts to create isolated environments:

```python
# scripts/ai/shared/environment_config.py
from scripts.ai.shared.environment_config import EnvironmentConfig
import subprocess

config = EnvironmentConfig()

if config.is_dev:
    # Create lightweight virtual environment for PostgreSQL
    subprocess.run([
        "bash",
        "scripts/infrastructure/wasi/lightweight_venv.sh",
        "create",
        "dev-postgres",
        "postgres",
        "5432"
    ])

    # Activate the environment (set environment variables)
    activate_script = "scripts/.lightvenvs/dev-postgres/bin/activate"
    # Source the activate script to get DB credentials
    # These will be available in os.environ
```

### Pattern 2: WASI Scripts Read Environment Config

WASI scripts can read the same `.env` file used by Python:

```bash
#!/bin/bash
# scripts/infrastructure/wasi/setup_database.sh

# Source environment detection
if [ -f "$(dirname $0)/../../../.env" ]; then
    source "$(dirname $0)/../../../.env"
fi

# Use ENVIRONMENT variable to decide behavior
case "${ENVIRONMENT:-development}" in
    development)
        echo "Setting up development database with VM tunnel..."
        # Use lightweight_venv.sh for local isolated PostgreSQL
        bash scripts/infrastructure/wasi/lightweight_venv.sh create dev-db postgres 5432
        ;;
    staging)
        echo "Connecting to staging database..."
        # Use virtualize.sh for containerized staging environment
        bash scripts/infrastructure/wasi/virtualize.sh create staging-db postgres 5433
        ;;
    production)
        echo "Using production database credentials from .env..."
        # Direct connection, no virtualization needed
        ;;
esac
```

### Pattern 3: Unified Configuration via .env

Both Python and Bash read from the same `.env` file:

```bash
# .env (shared by both Python and Bash)

# Environment detection
ENVIRONMENT=development

# Development Database (VM)
DB_VM_HOST=localhost
DB_VM_PORT=5432
DB_VM_NAME=iact_dev
DB_VM_USER=iact_user
DB_VM_PASSWORD=dev_password
DB_VM_SSH_ENABLED=true

# WASI Configuration
WASI_SANDBOX_DIR=/home/user/IACT---project/scripts/.lightvenvs
WASI_USE_NAMESPACES=true
WASI_MEMORY_LIMIT=512M
```

Python reads it:
```python
from scripts.ai.shared.environment_config import EnvironmentConfig
config = EnvironmentConfig()
db_config = config.get_database_config()
# Uses DB_VM_* variables
```

Bash reads it:
```bash
source .env
echo "Environment: $ENVIRONMENT"
echo "Database: $DB_VM_HOST:$DB_VM_PORT"
```

## Use Cases

### Use Case 1: Development with VM Tunnel

**Scenario**: Developer working locally, needs PostgreSQL connection via SSH tunnel to VM.

**Solution**:
1. Set `ENVIRONMENT=development` in `.env`
2. Python `EnvironmentConfig` detects development mode
3. Returns VM database config with SSH tunnel parameters
4. WASI `lightweight_venv.sh` creates isolated environment for local testing
5. Application connects using environment variables

```python
# Python
from scripts.ai.shared.environment_config import EnvironmentConfig
config = EnvironmentConfig()

if config.is_dev:
    db_config = config.get_database_config()
    # db_config['use_vm'] == True
    # db_config['ssh_tunnel'] contains tunnel params

    # Optional: Create local isolated test DB
    import subprocess
    subprocess.run([
        "bash", "scripts/infrastructure/wasi/lightweight_venv.sh",
        "create", "test-db", "postgres", "5433"
    ])
```

### Use Case 2: Staging with Containerized Services

**Scenario**: Staging environment needs isolated services for parallel testing.

**Solution**:
1. Set `ENVIRONMENT=staging` in `.env`
2. Python `EnvironmentConfig` detects staging mode
3. Returns staging database config
4. WASI `virtualize.sh` creates Docker containers for each test run
5. Tests run in parallel without interference

```python
# Python test setup
from scripts.ai.shared.environment_config import EnvironmentConfig
import subprocess

config = EnvironmentConfig()

if config.is_staging:
    # Create isolated staging environment for this test run
    test_id = "test-123"
    subprocess.run([
        "bash", "scripts/infrastructure/wasi/virtualize.sh",
        "create", f"staging-{test_id}", "postgres", "5434"
    ])

    # Run tests with isolated database
    # ...

    # Cleanup
    subprocess.run([
        "bash", "scripts/infrastructure/wasi/virtualize.sh",
        "destroy", f"staging-{test_id}"
    ])
```

### Use Case 3: Production Direct Connection

**Scenario**: Production environment with direct database connection.

**Solution**:
1. Set `ENVIRONMENT=production` in `.env`
2. Python `EnvironmentConfig` detects production mode
3. Returns production database config (direct connection, SSL)
4. No WASI virtualization needed
5. Application connects directly

```python
# Python
from scripts.ai.shared.environment_config import EnvironmentConfig
config = EnvironmentConfig()

if config.is_prod:
    db_config = config.get_database_config()
    # db_config['use_vm'] == False
    # db_config['ssl_mode'] == 'require'
    # Direct connection to production DB
```

## Environment Variable Mapping

| Python (environment_config.py) | Bash (WASI scripts) | Purpose |
|--------------------------------|---------------------|---------|
| `config.environment` | `$ENVIRONMENT` | Environment detection |
| `config.is_dev` | `[[ $ENVIRONMENT == "development" ]]` | Development check |
| `config.get_database_config()['host']` | `$DB_VM_HOST` or `$DB_PROD_HOST` | Database host |
| `config.get_database_config()['port']` | `$DB_VM_PORT` or `$DB_PROD_PORT` | Database port |
| `config.get_llm_config()['provider']` | `$LLM_PROVIDER` | LLM provider |
| `config.get_llm_config()['model']` | `$LLM_MODEL` | LLM model name |

## Best Practices

### 1. Single Source of Truth

Use `.env` as the single source of configuration for both Python and Bash:

```bash
# .env
ENVIRONMENT=development
DB_VM_HOST=localhost
DB_VM_PORT=5432
```

### 2. Environment Detection

Always detect environment before making decisions:

**Python**:
```python
config = EnvironmentConfig()
if config.is_dev:
    # Development-specific logic
elif config.is_staging:
    # Staging-specific logic
elif config.is_prod:
    # Production-specific logic
```

**Bash**:
```bash
case "${ENVIRONMENT:-development}" in
    development) # Dev logic ;;
    staging) # Staging logic ;;
    production) # Prod logic ;;
esac
```

### 3. Fail-Safe Defaults

Always provide sensible defaults:

**Python**:
```python
env = os.getenv("ENVIRONMENT", "development")
```

**Bash**:
```bash
ENVIRONMENT="${ENVIRONMENT:-development}"
```

### 4. Validation

Validate environment configurations:

**Python**:
```python
config = EnvironmentConfig()
errors = config.validate()
if errors:
    raise ValueError(f"Invalid config: {errors}")
```

**Bash**:
```bash
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    echo "Error: Invalid ENVIRONMENT=$ENVIRONMENT"
    exit 1
fi
```

### 5. Cleanup

Always cleanup virtualized environments:

**Python**:
```python
import atexit

def cleanup_sandbox():
    subprocess.run(["bash", "scripts/infrastructure/wasi/virtualize.sh",
                    "destroy", "my-sandbox"])

atexit.register(cleanup_sandbox)
```

**Bash**:
```bash
trap cleanup EXIT

cleanup() {
    echo "Cleaning up sandbox..."
    # Cleanup logic
}
```

## Examples

### Example 1: Test Suite with Isolated Database

```python
#!/usr/bin/env python3
"""
Test suite with isolated database using WASI + environment_config
"""
import subprocess
import pytest
from scripts.ai.shared.environment_config import EnvironmentConfig

@pytest.fixture(scope="session")
def isolated_database():
    """Create isolated database for test suite."""
    config = EnvironmentConfig()

    if config.is_dev or config.is_staging:
        # Create isolated test database
        test_db_name = "pytest-isolated-db"
        subprocess.run([
            "bash",
            "scripts/infrastructure/wasi/lightweight_venv.sh",
            "create",
            test_db_name,
            "postgres",
            "5435"
        ], check=True)

        # Activate environment
        activate_path = f"scripts/.lightvenvs/{test_db_name}/bin/activate"

        yield test_db_name

        # Cleanup
        subprocess.run([
            "bash",
            "scripts/infrastructure/wasi/lightweight_venv.sh",
            "destroy",
            test_db_name
        ])
    else:
        # Production: use shared test database
        yield "production-test-db"

def test_database_connection(isolated_database):
    """Test database connection in isolated environment."""
    config = EnvironmentConfig()
    db_config = config.get_database_config()

    # Connect and test
    # ...
```

### Example 2: SDLC Agent with Auto-Environment

```python
#!/usr/bin/env python3
"""
SDLC agent that auto-configures based on environment
"""
from scripts.ai.shared.environment_config import EnvironmentConfig
from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent

def main():
    # Auto-detect environment
    config = EnvironmentConfig()

    # Get LLM config based on environment
    llm_config = config.get_llm_config()

    # Create agent with environment-appropriate config
    agent = SDLCFeasibilityAgent(config=llm_config)

    print(f"Running in {config.environment} mode")
    print(f"LLM Provider: {llm_config['provider']}")
    print(f"LLM Model: {llm_config['model']}")
    print(f"Budget: ${llm_config['monthly_budget']}")

    # Run agent
    # ...

if __name__ == "__main__":
    main()
```

## Troubleshooting

### Issue 1: Environment Not Detected

**Symptom**: Python always detects "development" even when `ENVIRONMENT=staging` in `.env`

**Solution**: Ensure `.env` file exists and `environment_config.py` loads it:
```python
# Check if .env is loaded
import os
print(f"ENVIRONMENT={os.getenv('ENVIRONMENT')}")
```

### Issue 2: WASI Script Can't Find .env

**Symptom**: Bash script doesn't read `.env` variables

**Solution**: Use absolute path to `.env`:
```bash
ENV_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)/.env"
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
fi
```

### Issue 3: Permission Denied on WASI Scripts

**Symptom**: `bash: permission denied: scripts/infrastructure/wasi/*.sh`

**Solution**: Make scripts executable:
```bash
chmod +x scripts/infrastructure/wasi/*.sh
```

## References

- [Environment Config Documentation](../ai/CONFIGURACION_AMBIENTES.md)
- [WASI Scripts README](../../scripts/infrastructure/wasi/README.md)
- [ADR-011: WASI-style Virtualization](../infraestructura/adr_2025_011_wasi_style_virtualization.md)

---

**Last Updated**: 2025-11-12
**Author**: SDLC Development Team
