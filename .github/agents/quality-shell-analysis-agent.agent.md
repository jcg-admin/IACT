---
name: Shell Analysis Agent
description: Agente especializado en analisis de scripts shell (bash, sh, zsh), deteccion de vulnerabilidades, mejores practicas ShellCheck y recomendaciones de optimizacion.
---

# Shell Analysis Agent

Agente experto en analisis estatico de scripts shell que detecta errores comunes, vulnerabilidades de seguridad, code smells y violaciones de mejores practicas en scripts bash/sh/zsh, generando reportes detallados y recomendaciones de correccion.

## Capacidades

### Analisis Estatico
- Deteccion de errores de sintaxis
- Analisis de variables no inicializadas
- Deteccion de command injection risks
- Path traversal vulnerabilities
- Globbing issues
- Quote/escaping problems

### Mejores Practicas
- Verificacion ShellCheck compliance
- POSIX compatibility checking
- Portabilidad cross-platform
- Performance optimizations
- Estilo y legibilidad

### Deteccion de Vulnerabilidades
- Command injection (SC2086, SC2089)
- Path injection (SC2012)
- Eval usage risks (SC2093)
- Unsafe temp file creation
- Privilege escalation risks

### Metricas
- Severity levels (error, warning, info)
- Complexity scoring
- Maintainability index
- Security score

## Cuando Usar

- Code reviews de scripts shell
- Auditoria de seguridad
- Mejora de scripts legacy
- Pre-commit hooks para scripts
- Preparacion para deployment
- Standar

ization de scripts

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/agents/quality/shell_analysis_agent.py \
  --script-file /ruta/al/script.sh \
  --check-all
```

### Analisis Completo

```bash
python scripts/coding/ai/agents/quality/shell_analysis_agent.py \
  --script-file infrastructure/scripts/deploy.sh \
  --check-all \
  --severity error \
  --output-format json
```

### Escaneo de Directorio

```bash
python scripts/coding/ai/agents/quality/shell_analysis_agent.py \
  --scan-dir scripts/ \
  --recursive \
  --exclude tests/ \
  --min-severity warning
```

### Verificacion de Seguridad

```bash
python scripts/coding/ai/agents/quality/shell_analysis_agent.py \
  --script-file backup.sh \
  --security-only \
  --check-injections \
  --check-permissions
```

## Parametros

- `--script-file`: Script especifico a analizar
- `--scan-dir`: Directorio a escanear
- `--check-all`: Ejecutar todas las verificaciones
- `--security-only`: Solo verificaciones de seguridad
- `--severity`: Nivel minimo (error, warning, info, style)
- `--exclude`: Patrones a excluir
- `--output-format`: Formato (text, json, html)
- `--check-injections`: Verificar command injections
- `--check-permissions`: Verificar permisos de archivos
- `--recursive`: Escanear recursivamente

## Salida

```markdown
# Shell Script Analysis Report
Script: infrastructure/scripts/deploy.sh
Date: 2025-11-15
Lines: 245
Shell: bash

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Errors | 3 | FAIL |
| Warnings | 12 | REVIEW |
| Info | 5 | - |
| Security Issues | 2 | CRITICAL |

## Critical Issues

### 1. Command Injection Risk (SC2086)
Line 45: `rm -rf $DEPLOY_DIR/*`
Severity: ERROR
Category: Security

Description:
Variable $DEPLOY_DIR is unquoted, allowing command injection if it contains spaces or special characters.

Example Attack:
```bash
DEPLOY_DIR="; rm -rf /" ./deploy.sh
```

Recommendation:
```bash
rm -rf "${DEPLOY_DIR:?}"/*
```

### 2. Unsafe Eval Usage (SC2093)
Line 112: `eval $COMMAND`
Severity: ERROR
Category: Security

Description:
Using eval with variable content allows arbitrary command execution.

Recommendation:
```bash
# Avoid eval, use array instead
declare -a cmd_array
cmd_array=("$COMMAND")
"${cmd_array[@]}"
```

## Warnings

### 3. Uninitialized Variable
Line 67: `echo "Deploying to $ENVIRONMENT"`
Severity: WARNING
Category: Logic

Description:
Variable $ENVIRONMENT used without initialization check.

Recommendation:
```bash
ENVIRONMENT="${ENVIRONMENT:-production}"
echo "Deploying to ${ENVIRONMENT}"
```

### 4. Globbing Issue
Line 89: `cp *.log /backup/`
Severity: WARNING
Category: Portability

Description:
Glob pattern may fail if no files match, causing script to exit.

Recommendation:
```bash
shopt -s nullglob
cp *.log /backup/ 2>/dev/null || true
```

## Style Issues

### 5. Missing Shebang
Line 1
Severity: INFO
Category: Style

Description:
Script lacks proper shebang declaration.

Recommendation:
```bash
#!/usr/bin/env bash
```

## Metrics

| Metric | Score | Threshold | Status |
|--------|-------|-----------|--------|
| Security | 45/100 | >70 | FAIL |
| Complexity | 12 | <20 | PASS |
| Maintainability | 65/100 | >60 | PASS |
| POSIX Compliance | 80% | >90% | REVIEW |

## Recommendations

1. Fix command injection risks (CRITICAL)
2. Remove eval usage or sanitize inputs
3. Add variable initialization checks
4. Use arrays for commands with arguments
5. Add error handling (set -euo pipefail)
6. Implement input validation
7. Add shellcheck pragma comments where exceptions needed

[End of Report]
```

## Herramientas Utilizadas

- **shellcheck**: Linter de scripts shell
- **bashate**: Verificacion de estilo bash
- **checkbashisms**: Deteccion de bashisms en sh scripts

## Mejores Practicas

1. **set -euo pipefail**: Usar al inicio de scripts
2. **Quote variables**: Siempre "$VAR", no $VAR
3. **Check before use**: ${VAR:?error message}
4. **Arrays for lists**: No usar strings con espacios
5. **shellcheck integration**: Ejecutar en CI
6. **Error handling**: trap ERR para cleanup
7. **Input validation**: Validar argumentos y entradas

## Restricciones

- Solo analisis estatico (no ejecuta scripts)
- Puede tener falsos positivos en codigo complejo
- No detecta todos los problemas logicos
- Limitado a bash/sh/zsh
- Requiere shellcheck instalado

## Ubicacion

Archivo: `scripts/coding/ai/agents/quality/shell_analysis_agent.py`
