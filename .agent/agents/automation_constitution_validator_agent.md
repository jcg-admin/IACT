---
name: ConstitutionValidatorAgent
description: Agente especializado en validacion de cumplimiento de principios de .constitucion.yaml (R1-R5), ejecutando validaciones automaticas en pre-commit, pre-push, CI local y devcontainer init.
---

# Automation: Constitution Validator Agent

El ConstitutionValidatorAgent valida el cumplimiento de los 5 principios constitucionales del proyecto (R1: Idempotencia, R2: Sin Emojis, R3: Verificacion, R4: Documentacion, R5: Trazabilidad) definidos en `.constitucion.yaml`.

## Capacidades

### Validacion R1: Idempotencia
- Scripts ejecutables multiples veces sin efectos secundarios
- Operaciones declarativas e idempotentes
- Deteccion de side effects no controlados
- Validacion de rollback capabilities

### Validacion R2: Sin Emojis
- Escaneo de codigo Python, Shell, JavaScript
- Deteccion de emojis en outputs de automation
- Validacion de logs y reportes
- Exclusion de archivos README y documentacion de usuario

### Validacion R3: Verificacion
- Presencia de tests para codigo critico
- Validacion de CI/CD pipelines
- Checks de calidad automaticos
- Coverage minimo

### Validacion R4: Documentacion
- Docstrings en funciones y clases
- Comentarios en codigo complejo
- README actualizado
- ADRs para decisiones arquitectonicas

### Validacion R5: Trazabilidad
- Logging estructurado
- Tracking de operaciones
- Audit trails
- Contexto completo en logs

### Modos de Validacion
- **pre-commit**: Validacion rapida antes de commit
- **pre-push**: Validacion completa antes de push
- **devcontainer-init**: Validacion al inicializar devcontainer
- **ci-local**: Validacion simulando CI localmente
- **manual**: Validacion manual on-demand

## Cuando usar

- **Pre-Commit Hook**: Validar antes de cada commit
- **Pre-Push Hook**: Validar antes de push a remote
- **CI Pipeline**: Gate de calidad en CI/CD
- **Devcontainer Init**: Validar ambiente al inicializar
- **Code Review**: Verificar cumplimiento en PRs
- **Onboarding**: Enseñar principios a nuevos desarrolladores

## Como usar

### Validacion Pre-Commit

```bash
python scripts/coding/ai/automation/constitution_validator_agent.py \
  --mode pre-commit \
  --staged-files-only
```

### Validacion Pre-Push

```bash
python scripts/coding/ai/automation/constitution_validator_agent.py \
  --mode pre-push \
  --validate-all
```

### Validacion CI Local

```bash
python scripts/coding/ai/automation/constitution_validator_agent.py \
  --mode ci-local \
  --fail-on-error \
  --output validation_report.json
```

### Validacion Manual

```bash
# Validar regla especifica
python scripts/coding/ai/automation/constitution_validator_agent.py \
  --mode manual \
  --rule R2 \
  --path scripts/

# Validar todas las reglas
python scripts/coding/ai/automation/constitution_validator_agent.py \
  --mode manual \
  --validate-all \
  --verbose
```

### Validacion Devcontainer Init

```bash
python scripts/coding/ai/automation/constitution_validator_agent.py \
  --mode devcontainer-init \
  --quick-check
```

### Integracion Git Hooks

```bash
# Instalar hooks
python scripts/coding/ai/automation/constitution_validator_agent.py \
  --install-hooks

# .git/hooks/pre-commit
#!/bin/bash
python scripts/coding/ai/automation/constitution_validator_agent.py \
  --mode pre-commit \
  --staged-files-only \
  --fail-on-error
```

## Output esperado

### Reporte de Validacion

```json
{
  "timestamp": "2025-11-14T12:00:00",
  "mode": "pre-push",
  "passed": false,
  "rules_evaluated": ["R1", "R2", "R3", "R4", "R5"],
  "violations": [
    {
      "rule_id": "R2",
      "severity": "error",
      "message": "Emoji detected in automation output",
      "file": "scripts/deploy.sh",
      "line": 45
    },
    {
      "rule_id": "R4",
      "severity": "warning",
      "message": "Missing docstring in function",
      "file": "api/utils.py",
      "line": 23
    }
  ],
  "summary": {
    "total_violations": 2,
    "errors": 1,
    "warnings": 1,
    "rules_passed": ["R1", "R3", "R5"],
    "rules_failed": ["R2", "R4"]
  }
}
```

### Output Consola

```
Constitution Validation Report
==============================
Mode: pre-push
Status: FAILED

Violations:
-----------
[ERROR] R2: Sin Emojis
  scripts/deploy.sh:45
  Emoji detected in automation output: echo "Deployment success! 🎉"

[WARNING] R4: Documentacion
  api/utils.py:23
  Missing docstring in function: process_data()

Summary:
--------
Total violations: 2 (1 error, 1 warning)
Rules passed: R1, R3, R5
Rules failed: R2, R4

Action required: Fix errors before pushing.
```

## Herramientas y dependencias

- **Python 3.11+**
- **AST parsing**: ast module
- **Regex**: re module
- **YAML**: PyYAML
- **File scanning**: pathlib, glob

## Buenas practicas

1. **Instalar hooks**: Configurar pre-commit y pre-push hooks
2. **Validar frecuentemente**: Correr en CI/CD siempre
3. **Fix on detection**: Corregir violaciones inmediatamente
4. **Excluir apropiadamente**: Documentacion de usuario puede tener emojis
5. **Severity levels**: Diferenciar errors vs warnings
6. **Auto-fix cuando posible**: Implementar correcciones automaticas
7. **Educacion**: Usar violaciones como teaching moments

## Restricciones

- **Solo archivos de texto**: No valida binarios
- **Lenguajes soportados**: Python, Shell, JavaScript, TypeScript
- **Regex-based**: Puede tener falsos positivos/negativos
- **Configuracion requerida**: Necesita .constitucion.yaml valido
- **Git-dependiente**: Requiere repositorio Git para pre-commit/push

## Ubicacion

Archivo Python: `scripts/coding/ai/automation/constitution_validator_agent.py`
Tests: `scripts/coding/ai/tests/test_constitution_validator_agent.py`
Config: `.constitucion.yaml`
