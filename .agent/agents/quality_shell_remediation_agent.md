---
name: Shell Remediation Agent
description: Agente especializado en correccion automatica de errores en scripts shell, refactorizacion para mejorar seguridad, portabilidad y adherencia a mejores practicas.
---

# Shell Remediation Agent

Agente experto en correccion y refactorizacion automatica de scripts shell que aplica fixes para errores detectados por ShellCheck, mejora seguridad, optimiza performance y moderniza scripts legacy.

## Capacidades

### Correccion Automatica
- Fix de quotes y escaping
- Inicializacion de variables
- Correccion de array usage
- Fix de globbing issues
- Correccion de redirects

### Refactorizacion de Seguridad
- Eliminacion de command injections
- Sanitizacion de inputs
- Secure temp file creation
- Permission hardening
- Removal of eval donde sea posible

### Modernizacion
- Conversion sh → bash
- Uso de [[ ]] en lugar de [ ]
- Arrays en lugar de strings con IFS
- printf en lugar de echo
- mapfile/readarray moderno

### Optimizacion
- Reduccion de subshells
- Eliminacion de UUOC (Useless Use Of Cat)
- Optimizacion de loops
- Caching de comandos costosos

## Cuando Usar

- Correccion de scripts con errores
- Mejora de seguridad de scripts
- Modernizacion de scripts legacy
- Estandarizacion de codigo shell
- Preparacion para produccion
- Post-analisis remediation

## Uso

### Sintaxis Basica

```bash
python scripts/coding/ai/agents/quality/shell_remediation_agent.py \
  --script-file /ruta/al/script.sh \
  --fix-all
```

### Correccion Automatica

```bash
python scripts/coding/ai/agents/quality/shell_remediation_agent.py \
  --script-file deploy.sh \
  --fix-all \
  --backup \
  --verify
```

### Correccion Selectiva

```bash
python scripts/coding/ai/agents/quality/shell_remediation_agent.py \
  --script-file backup.sh \
  --fix-security \
  --fix-quoting \
  --dry-run
```

### Modernizacion

```bash
python scripts/coding/ai/agents/quality/shell_remediation_agent.py \
  --script-file legacy.sh \
  --modernize \
  --target-shell bash \
  --output-file legacy_modern.sh
```

## Parametros

- `--script-file`: Script a remediar
- `--fix-all`: Aplicar todas las correcciones
- `--fix-security`: Solo fixes de seguridad
- `--fix-quoting`: Corregir quotes/escaping
- `--modernize`: Modernizar sintaxis
- `--target-shell`: Shell objetivo (bash, sh, zsh)
- `--backup`: Crear backup antes de modificar
- `--dry-run`: Mostrar cambios sin aplicar
- `--verify`: Verificar con shellcheck despues
- `--output-file`: Archivo de salida (default: sobrescribir)

## Salida

### Antes de Remediation

```bash
#!/bin/sh
# deploy.sh - Deployment script

DEPLOY_DIR=$1

echo "Deploying to $DEPLOY_DIR"

rm -rf $DEPLOY_DIR/*

for file in *.jar
do
  cp $file $DEPLOY_DIR/
done

eval $DEPLOY_COMMAND
```

### Despues de Remediation

```bash
#!/usr/bin/env bash
# deploy.sh - Deployment script
# Fixed by Shell Remediation Agent on 2025-11-15

set -euo pipefail

readonly DEPLOY_DIR="${1:?Usage: $0 <deploy_dir>}"

echo "Deploying to ${DEPLOY_DIR}"

# Safe deletion with verification
if [[ -d "${DEPLOY_DIR}" ]]; then
    rm -rf "${DEPLOY_DIR:?}"/*
else
    echo "Error: Deploy directory does not exist" >&2
    exit 1
fi

# Use array for file processing
shopt -s nullglob
jar_files=(*.jar)

if [[ ${#jar_files[@]} -eq 0 ]]; then
    echo "Warning: No JAR files found" >&2
else
    for file in "${jar_files[@]}"; do
        cp "${file}" "${DEPLOY_DIR}/"
    done
fi

# Avoid eval - use array
if [[ -n "${DEPLOY_COMMAND:-}" ]]; then
    # shellcheck disable=SC2206
    deploy_cmd=(${DEPLOY_COMMAND})
    "${deploy_cmd[@]}"
fi
```

### Diff de Cambios

```diff
- #!/bin/sh
+ #!/usr/bin/env bash
+ set -euo pipefail

- DEPLOY_DIR=$1
+ readonly DEPLOY_DIR="${1:?Usage: $0 <deploy_dir>}"

- echo "Deploying to $DEPLOY_DIR"
+ echo "Deploying to ${DEPLOY_DIR}"

+ # Safe deletion with verification
+ if [[ -d "${DEPLOY_DIR}" ]]; then
-     rm -rf $DEPLOY_DIR/*
+     rm -rf "${DEPLOY_DIR:?}"/*
+ else
+     echo "Error: Deploy directory does not exist" >&2
+     exit 1
+ fi

+ # Use array for file processing
+ shopt -s nullglob
+ jar_files=(*.jar)

- for file in *.jar
- do
-   cp $file $DEPLOY_DIR/
- done
+ if [[ ${#jar_files[@]} -eq 0 ]]; then
+     echo "Warning: No JAR files found" >&2
+ else
+     for file in "${jar_files[@]}"; do
+         cp "${file}" "${DEPLOY_DIR}/"
+     done
+ fi

- eval $DEPLOY_COMMAND
+ # Avoid eval - use array
+ if [[ -n "${DEPLOY_COMMAND:-}" ]]; then
+     deploy_cmd=(${DEPLOY_COMMAND})
+     "${deploy_cmd[@]}"
+ fi
```

## Transformaciones Aplicadas

### Security Fixes
1. Added parameter validation (${1:?})
2. Quoted all variable expansions
3. Added directory existence check
4. Replaced eval with array execution
5. Added error handling (set -euo pipefail)

### Modernization
6. Changed shebang to #!/usr/bin/env bash
7. Used [[ ]] instead of [ ]
8. Implemented arrays for file lists
9. Added nullglob for safe globbing
10. Used readonly for immutable variables

### Best Practices
11. Added comments for complex sections
12. Improved error messages to stderr
13. Added usage message
14. Implemented proper exit codes
15. Added shellcheck disable pragmas where needed

## Metricas de Mejora

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Security Score | 45/100 | 92/100 | +104% |
| ShellCheck Issues | 15 | 0 | -100% |
| Lines of Code | 18 | 35 | +94% (better) |
| Complexity | 8 | 6 | -25% |

## Herramientas Utilizadas

- **shellcheck**: Validacion post-remediation
- **shfmt**: Formateo de codigo
- **bashate**: Verificacion de estilo

## Mejores Practicas

1. **Siempre backup**: Crear backup antes de modificar
2. **Dry-run first**: Revisar cambios antes de aplicar
3. **Verify after**: Ejecutar shellcheck post-remediation
4. **Test scripts**: Ejecutar tests si existen
5. **Review manual**: Revisar cambios complejos
6. **Incremental**: Aplicar fixes gradualmente
7. **Document**: Agregar comentarios explicativos

## Restricciones

- Correciones automaticas pueden cambiar comportamiento
- Algunos fixes requieren contexto adicional
- No puede corregir logica de negocio incorrecta
- Modernizacion puede romper compatibilidad con sh antiguo
- Requiere revision manual para scripts criticos

## Ubicacion

Archivo: `scripts/coding/ai/agents/quality/shell_remediation_agent.py`
