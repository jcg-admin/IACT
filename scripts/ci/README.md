# CI/CD Shell Scripts

**Replacement for GitHub Actions** - All CI/CD checks implemented as shell scripts.

## Purpose

This project uses **shell scripts instead of GitHub Actions** for CI/CD. All checks run locally or in any CI environment without GitHub-specific dependencies.

## Architecture

```
scripts/ci/
├── infrastructure/          # Infrastructure validation
│   ├── health-check.sh     # Health checks (DB, Python, Django)
│   ├── validate-scripts.sh # Shell script validation
│   ├── validate-config.sh  # JSON/YAML config validation
│   └── validate-docker.sh  # Docker configuration validation
├── security/                # Security scans
│   ├── csrf-check.sh       # CSRF protection verification
│   ├── django-security-check.sh  # Django security settings
│   ├── bandit-scan.sh      # Python security scan (Bandit)
│   └── npm-audit.sh        # NPM vulnerability scan
├── testing/                 # Test quality validation
│   ├── test-pyramid.sh     # Test pyramid analysis
│   └── test-execution-time.sh  # Test performance
├── gate-route-lint.sh      # PromptOps: Route Lint gate
├── run-all-gates.sh        # PromptOps gates orchestrator
├── run-tdd-cycle.sh        # TDD Agent wrapper
└── run-all-checks.sh       # Master CI/CD orchestrator
```

## Usage

### Run All Checks

```bash
# Run everything
./scripts/ci/run-all-checks.sh

# Fail fast (stop on first error)
./scripts/ci/run-all-checks.sh --fail-fast

# Verbose output
./scripts/ci/run-all-checks.sh --verbose

# Run specific suite only
./scripts/ci/run-all-checks.sh --only infrastructure
./scripts/ci/run-all-checks.sh --only security
./scripts/ci/run-all-checks.sh --only testing
./scripts/ci/run-all-checks.sh --only promptops
```

### Individual Suites

**Infrastructure CI:**
```bash
./scripts/ci/infrastructure/health-check.sh
./scripts/ci/infrastructure/validate-scripts.sh
./scripts/ci/infrastructure/validate-config.sh
./scripts/ci/infrastructure/validate-docker.sh
```

**Security Scan:**
```bash
./scripts/ci/security/csrf-check.sh
./scripts/ci/security/django-security-check.sh
./scripts/ci/security/bandit-scan.sh
./scripts/ci/security/npm-audit.sh
```

**Test Pyramid Validation:**
```bash
./scripts/ci/testing/test-pyramid.sh
./scripts/ci/testing/test-execution-time.sh
```

**PromptOps Gates:**
```bash
./scripts/ci/gate-route-lint.sh
./scripts/ci/run-all-gates.sh
```

## Exit Codes

All scripts follow standard exit code conventions:

- `0`: Check passed
- `1`: Check failed
- `2`: Check skipped (not applicable)

## Mapping: GitHub Actions → Shell Scripts

| GitHub Action | Shell Script | Status |
|---------------|--------------|--------|
| Infrastructure CI / Health Check | `infrastructure/health-check.sh` | [OK] |
| Infrastructure CI / Validate Scripts | `infrastructure/validate-scripts.sh` | [OK] |
| Infrastructure CI / Validate Config | `infrastructure/validate-config.sh` | [OK] |
| Infrastructure CI / Validate Docker | `infrastructure/validate-docker.sh` | [OK] |
| Security Scan / CSRF Check | `security/csrf-check.sh` | [OK] |
| Security Scan / Django Security | `security/django-security-check.sh` | [OK] |
| Security Scan / Bandit | `security/bandit-scan.sh` | [OK] |
| Security Scan / NPM Audit | `security/npm-audit.sh` | [OK] |
| Test Pyramid / Analyze | `testing/test-pyramid.sh` | [OK] |
| Test Pyramid / Execution Time | `testing/test-execution-time.sh` | [OK] |
| (Custom) Route Lint Gate | `gate-route-lint.sh` | [OK] |

## Integration with Pre-commit

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Run critical checks before commit

./scripts/ci/infrastructure/validate-scripts.sh || exit 1
./scripts/ci/security/csrf-check.sh || exit 1
./scripts/ci/gate-route-lint.sh || exit 1

echo "Pre-commit checks passed"
```

## Integration with CI Server

### Jenkins

```groovy
stage('CI Checks') {
    steps {
        sh './scripts/ci/run-all-checks.sh --fail-fast'
    }
}
```

### GitLab CI

```yaml
ci_checks:
  script:
    - ./scripts/ci/run-all-checks.sh --fail-fast
```

### Generic CI

```bash
#!/bin/bash
# ci-pipeline.sh

cd $PROJECT_ROOT
./scripts/ci/run-all-checks.sh --fail-fast

if [ $? -eq 0 ]; then
    echo "All checks passed - ready to deploy"
    exit 0
else
    echo "CI checks failed"
    exit 1
fi
```

## Requirements

### System Dependencies

**Required:**
- bash (4.0+)
- Python 3.8+
- pytest

**Optional:**
- Node.js + npm (for NPM audit)
- Docker + docker-compose (for Docker validation)
- bandit (auto-installed if missing)

### Python Dependencies

```bash
# Install in virtualenv
pip install pytest pytest-json-report bandit
```

## Script Details

### Infrastructure CI

**health-check.sh**
- Verifies Python version
- Tests database connectivity
- Validates Django configuration
- Checks required directories

**validate-scripts.sh**
- Finds all `.sh` files in `scripts/`
- Checks shebang exists
- Validates bash syntax (`bash -n`)
- Verifies executable permissions

**validate-config.sh**
- Validates all JSON files (syntax)
- Validates all YAML files (syntax)
- Validates Django settings imports

**validate-docker.sh**
- Checks Dockerfile has `FROM` instruction
- Validates `USER` instruction exists (security)
- Validates `docker-compose.yml` syntax

### Security Scan

**csrf-check.sh**
- Verifies `CsrfViewMiddleware` is enabled
- Scans for `@csrf_exempt` decorators
- Checks API views have session authentication

**django-security-check.sh**
- Runs `python manage.py check --deploy`
- Validates `DEBUG = False`
- Checks `SECRET_KEY` not hardcoded
- Validates SSL/HTTPS settings
- Scans for `.raw()` SQL queries

**bandit-scan.sh**
- Runs Bandit security scanner
- Excludes migrations, tests, venv
- Reports high/medium/low severity issues

**npm-audit.sh**
- Runs `npm audit` if `package.json` exists
- Auto-attempts `npm audit fix`
- Skips if NPM not used

### Test Pyramid Validation

**test-pyramid.sh**
- Counts tests by mark: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`
- Calculates percentages
- Validates pyramid ratios (70% unit, 20% integration, 10% e2e)

**test-execution-time.sh**
- Runs pytest with `--durations=10`
- Reports slowest tests
- Validates total time < 2 minutes
- Warns about slow tests (>5s)

## Best Practices

1. **Run locally before pushing:**
   ```bash
   ./scripts/ci/run-all-checks.sh --fail-fast
   ```

2. **Run specific suite when debugging:**
   ```bash
   ./scripts/ci/run-all-checks.sh --only security --verbose
   ```

3. **Integrate in pre-push hook:**
   ```bash
   # .git/hooks/pre-push
   ./scripts/ci/run-all-checks.sh || exit 1
   ```

4. **Run in CI pipeline:**
   - Always use `--fail-fast` in CI
   - Capture exit code for pipeline status
   - Archive logs for debugging

## Troubleshooting

**Issue: Script not executable**
```bash
chmod +x scripts/ci/**/*.sh
```

**Issue: Python module not found**
```bash
# Activate virtualenv first
source venv/bin/activate
./scripts/ci/run-all-checks.sh
```

**Issue: Database connection failed**
```bash
# Check .env file exists
# Verify DATABASE_URL is set
# Run migrations
python manage.py migrate
```

**Issue: Bandit not installed**
```bash
pip install bandit
# Script will auto-install if missing
```

## Future Enhancements

- [ ] Add `gate-audit-contract.sh` (validate audit log fields)
- [ ] Add `gate-permission-coverage.sh` (verify capabilities have tests)
- [ ] Add `performance/load-test.sh` (API load testing)
- [ ] Add `accessibility/a11y-check.sh` (frontend accessibility)
- [ ] Integrate with Prometheus for metrics collection

## Related Documentation

- [TDD Agent](../ai/agents/tdd/README.md)
- [PromptOps Framework](../../docs/backend/permisos/promptops/CONTRIBUTING.md)
- [Route Lint Gate](../../docs/backend/permisos/promptops/gates/route-lint.md)

---

**Generated by:** CI/CD Shell Scripts Initiative
**Date:** 2025-11-11
**Project:** IACT - Sistema de Permisos Granular
