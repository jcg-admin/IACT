---
name: DevcontainerValidatorAgent
description: Agente especializado en validacion de configuraciones devcontainer, verificando integridad, consistencia con dependencias del proyecto y buenas practicas de desarrollo containerizado.
---

# Automation: Devcontainer Validator Agent

El DevcontainerValidatorAgent valida configuraciones de devcontainer (.devcontainer/devcontainer.json) asegurando integridad, consistencia con dependencias del proyecto y cumplimiento de buenas practicas.

## Capacidades

### Validacion de Estructura
- Schema JSON valido
- Propiedades requeridas presentes
- Configuracion de features correcta
- Extensiones VS Code apropiadas
- Settings consistentes

### Validacion de Dependencias
- Sincronizacion con requirements.txt
- Sincronizacion con package.json
- Verificacion de versiones de runtimes
- Validacion de herramientas CLI requeridas

### Validacion de Seguridad
- No secrets hardcodeados
- Permisos apropiados
- Usuario no-root cuando posible
- Network security

### Validacion de Performance
- Imagen base optimizada
- Cache layers apropiados
- Volume mounts eficientes
- Resource limits razonables

### Buenas Practicas
- Documentacion inline
- Features organizados
- Extensions relevantes
- Settings team-friendly

## Cuando usar

- **Pre-Commit**: Validar antes de commitear cambios a devcontainer
- **CI/CD**: Verificar en pipeline antes de merge
- **Onboarding**: Asegurar ambiente consistente para nuevos devs
- **Updates**: Validar al actualizar dependencias
- **Troubleshooting**: Diagnosticar problemas de ambiente

## Como usar

### Validacion Completa

```bash
python scripts/coding/ai/automation/devcontainer_validator_agent.py \
  --devcontainer-path .devcontainer/devcontainer.json \
  --validate-all
```

### Validacion Especifica

```bash
# Solo estructura
python scripts/coding/ai/automation/devcontainer_validator_agent.py \
  --validate structure

# Solo dependencias
python scripts/coding/ai/automation/devcontainer_validator_agent.py \
  --validate dependencies \
  --requirements requirements.txt \
  --package-json package.json

# Solo seguridad
python scripts/coding/ai/automation/devcontainer_validator_agent.py \
  --validate security
```

### Validacion con Autofix

```bash
python scripts/coding/ai/automation/devcontainer_validator_agent.py \
  --validate-all \
  --autofix \
  --backup
```

### Integracion CI

```bash
python scripts/coding/ai/automation/devcontainer_validator_agent.py \
  --validate-all \
  --fail-on-error \
  --output validation_report.json
```

## Output esperado

### Reporte de Validacion

```json
{
  "timestamp": "2025-11-14T12:00:00",
  "devcontainer_path": ".devcontainer/devcontainer.json",
  "passed": false,
  "validations": {
    "structure": {
      "passed": true,
      "issues": []
    },
    "dependencies": {
      "passed": false,
      "issues": [
        {
          "severity": "error",
          "message": "requirements.txt has 'django==5.0.1' but devcontainer uses '5.0.0'",
          "fix": "Update devcontainer.json to match requirements.txt"
        }
      ]
    },
    "security": {
      "passed": true,
      "issues": []
    },
    "performance": {
      "passed": true,
      "issues": []
    },
    "best_practices": {
      "passed": false,
      "issues": [
        {
          "severity": "warning",
          "message": "Missing Python extension 'ms-python.python'",
          "fix": "Add extension to customizations.vscode.extensions"
        }
      ]
    }
  },
  "summary": {
    "total_issues": 2,
    "errors": 1,
    "warnings": 1
  }
}
```

### Output Consola

```
Devcontainer Validation Report
===============================
File: .devcontainer/devcontainer.json
Status: FAILED

Issues Found:
-------------
[ERROR] Dependencies
  Django version mismatch
  - requirements.txt: django==5.0.1
  - devcontainer.json: 5.0.0
  Fix: Update devcontainer.json to match requirements.txt

[WARNING] Best Practices
  Missing recommended extension
  - Extension: ms-python.python
  Fix: Add to customizations.vscode.extensions

Summary:
--------
Total issues: 2 (1 error, 1 warning)
Validations passed: structure, security, performance
Validations failed: dependencies, best_practices
```

## Herramientas y dependencias

- **Python 3.11+**
- **JSON validation**: json, jsonschema
- **File parsing**: pathlib
- **Dependency checking**: pip, npm

## Buenas practicas

1. **Validar antes de commit**: Integrar en pre-commit hooks
2. **Sincronizar dependencias**: Mantener consistency con requirements/package.json
3. **Usar autofix**: Corregir automaticamente cuando sea seguro
4. **Backup antes de autofix**: Crear respaldo antes de modificaciones
5. **Documentar cambios**: Explicar configuraciones custom
6. **Probar localmente**: Rebuild devcontainer despues de cambios
7. **Version control**: Trackear cambios en devcontainer

## Restricciones

- **Solo devcontainer.json**: No valida Dockerfile directamente
- **Schema conocido**: Valida contra schema oficial de devcontainer
- **Dependencias Python/JS**: Solo soporta pip y npm
- **VS Code enfocado**: Optimizado para VS Code devcontainers

## Ubicacion

Archivo Python: `scripts/coding/ai/automation/devcontainer_validator_agent.py`
Tests: `scripts/coding/ai/tests/test_devcontainer_validator_agent.py`
