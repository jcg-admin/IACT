# Validation Scripts

This directory contains all validation scripts following Constitution Principles.

## Structure

```
validation/
├── security/         # Security validations (SQL injection, XSS, CSRF, etc.)
├── quality/          # Code quality validations (linting, formatting, naming)
├── compliance/       # IACT restrictions compliance (no Redis, no email, etc.)
└── infrastructure/   # Infrastructure validations (dependencies, migrations)
```

## Constitution Principles

All scripts in this directory MUST comply with 8 principles:

1. **Ejecutable Localmente** (CRITICAL): Run without GitHub Actions
2. **Exit Codes Estandarizados** (CRITICAL): 0=success, 1=fail, 2=warning
3. **Output Parseable** (CRITICAL): Support --output json
4. **Idempotente** (CRITICAL): Same input = same output
5. **Versionado Independiente** (HIGH): Independent semver
6. **Documentación Inline** (HIGH): --help flag with examples
7. **Testing Unitario** (MEDIUM): Unit tests required
8. **Backward Compatible** (MEDIUM): No breaking changes

## Usage

Each validator can be run standalone:

```bash
# Quality validation
./scripts/validation/quality/validate_frontmatter.py --path implementacion/

# Security validation
./scripts/validation/security/check_sql_injection.py --path api/

# Compliance validation
./scripts/validation/compliance/check_no_emojis.py --all
```

Or use orchestrators:

```bash
# All security checks
./scripts/validation/security/run_all_security_checks.sh

# All compliance checks
./scripts/validation/compliance/run_compliance_checks.sh
```

## Development

When creating a new validator:

1. Use template: `scripts/templates/validator_template.py`
2. Implement validation logic
3. Add unit tests in `scripts/testing/unit/`
4. Validate against constitution with `scripts/testing/validate_constitution_compliance.py`
5. Document in this README

## References

- Strategy: ESTRATEGIA_MIGRACION_SHELL_SCRIPTS.md
- Style Guide: docs/gobernanza/GUIA_ESTILO.md
- Contributing: CONTRIBUTING.md
