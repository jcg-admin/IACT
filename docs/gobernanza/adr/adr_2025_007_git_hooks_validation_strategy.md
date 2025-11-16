---
id: ADR-2025-007
estado: aceptada
propietario: devops-team
ultima_actualizacion: 2025-11-09
relacionados:
  [
    "ADR-002-suite-calidad-codigo",
    "ESTRATEGIA_GIT_HOOKS.md",
    "RESUMEN_MIGRACION_SHELL_SCRIPTS.md",
  ]
---

# ADR-2025-007: Estrategia de Validación Local con Git Hooks

**Estado:** aceptada

**Fecha:** 2025-11-09

**Decisores:** DevOps Team, Backend Team, Architecture Team

**Contexto técnico:** Full-stack (DevOps + Quality)

## Contexto y Problema

El proyecto IACT tiene validaciones extensivas en CI/CD (GitHub Actions) pero los desarrolladores descubrían errores solo después de push, generando ciclos largos de feedback. Necesitamos validaciones locales que detecten problemas ANTES del push para:

1. Reducir tiempo de feedback loop
2. Disminuir carga en runners de CI/CD
3. Prevenir commits que fallarán en CI
4. Enforce políticas de calidad localmente

**Preguntas clave:**

- ¿Qué validaciones ejecutar localmente vs CI/CD?
- ¿Cómo distribuir validaciones por fase de git workflow?
- ¿Cómo balance entre velocidad local y exhaustividad?
- ¿Cómo prevenir bypass de hooks sin frustrar desarrolladores?
- ¿Cómo mantener consistencia entre validaciones locales y CI/CD?

**Restricciones actuales:**

- Developers usan diferentes OS (Linux, macOS, Windows)
- Validaciones deben ser rápidas (no más de 60 segundos)
- Debe haber escape hatch para emergencias (--no-verify)
- NO requerir instalación manual de hooks (automatizado)

**Impacto:**

- **Developer Experience**: Feedback inmediato vs esperar CI/CD
- **CI/CD Load**: Reducción de jobs fallidos
- **Code Quality**: Enforcement temprano de políticas
- **Time to Fix**: Detección de errores en segundos vs minutos

## Factores de Decisión

- **Performance**: Validaciones rápidas para no interrumpir flow
- **Exhaustividad**: Cobertura suficiente sin duplicar CI/CD completo
- **Mantenibilidad**: Fácil agregar/modificar validaciones
- **Developer Experience**: No frustrante, útil, claro feedback
- **Consistency**: Mismos scripts que CI/CD (no código duplicado)
- **Bypass ability**: Escape hatch para casos edge

## Opciones Consideradas

### Opción 1: Pre-commit Framework (Python)

**Descripción:**
Usar pre-commit framework (Python package) con configuración YAML para manejar hooks.

**Pros:**

- OK Ecosistema maduro con muchos hooks pre-built
- OK Gestión automática de entornos virtuales
- OK Configuración declarativa en .pre-commit-config.yaml
- OK Cache automático de hooks

**Contras:**

- NO Dependencia de Python en environment local
- NO Complejidad adicional (gestión de venvs)
- NO Dificulta customización de hooks propios
- NO NO reutiliza scripts de validación existentes
- NO Curva de aprendizaje para configuración YAML

**Ejemplo:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
```

---

### Opción 2: Husky + lint-staged (Node.js)

**Descripción:**
Usar Husky (Git hooks manager) + lint-staged para ejecutar linters solo en staged files.

**Pros:**

- OK Popular en ecosistema JavaScript
- OK Fácil configuración en package.json
- OK Ejecuta solo en archivos modificados

**Contras:**

- NO Requiere Node.js y npm en environment
- NO Orientado principalmente a frontend
- NO NO aprovecha scripts shell existentes
- NO Complejidad de tener dos package managers (pip + npm)

---

### Opción 3: Shell Scripts en .git/hooks/ (Seleccionada)

**Descripción:**
Implementar git hooks directamente como shell scripts en scripts/git-hooks/, con symlink/copia automática a .git/hooks/ vía post-create script o instalación manual.

Estrategia de distribución:

- **pre-commit**: Validaciones rápidas (< 5 segundos)
- **commit-msg**: Validación de formato de mensaje
- **pre-push**: Validaciones exhaustivas (< 60 segundos)
- **pre-rebase**: Protección de branches

**Pros:**

- OK Sin dependencias externas (solo bash)
- OK Reutiliza scripts de validación existentes
- OK Performance óptima (shell nativo)
- OK Fácil debugging y customización
- OK Consistencia con CI/CD (mismos scripts)
- OK Funciona en cualquier OS con bash
- OK Control total sobre lógica de hooks

**Contras:**

- NO Requiere código custom para cada hook
- NO Instalación manual o automatización necesaria
- NO Mantenimiento propio del código

**Ejemplo:**

```bash
# scripts/git-hooks/pre-commit
#!/bin/bash
set -euo pipefail

FAILED=0

# Check 1: No emojis
echo "[1/5] Checking for emojis..."
if bash "$PROJECT_ROOT/scripts/workflows/check_no_emojis.sh" $STAGED_FILES; then
    log_success "No emojis found"
else
    log_error "Emojis detected"
    FAILED=$((FAILED + 1))
fi

# Check 2-5: ...

if [ $FAILED -eq 0 ]; then
    log_success "PRE-COMMIT PASSED"
    exit 0
else
    log_error "PRE-COMMIT FAILED: $FAILED validation(s) failed"
    exit 1
fi
```

---

## Decisión

**Opción elegida:** "Shell Scripts en .git/hooks/"

**Justificación:**

1. **Sin dependencias**: Solo requiere bash (disponible en todos los OS objetivo)
2. **Reutilización**: Mismos scripts que CI/CD (scripts/validation/\*)
3. **Performance**: Shell nativo es más rápido que Python/Node frameworks
4. **Simplicidad**: Lógica clara, fácil debugging, no magic
5. **Flexibilidad**: Fácil agregar/modificar validaciones específicas del proyecto
6. **Trade-offs aceptados**: Código custom vs framework - justificado por consistencia con CI/CD

## Consecuencias

### Positivas

- OK Feedback inmediato (< 5s pre-commit, < 60s pre-push)
- OK Reducción de CI/CD failures (validaciones tempranas)
- OK Consistencia total entre local y CI/CD (mismos scripts)
- OK Developer productivity (detección temprana)
- OK Sin overhead de frameworks externos

### Negativas

- WARNING Requiere mantener scripts de hooks (mitigado: código simple)
- WARNING Instalación no automática (mitigado: documentado en README)
- WARNING Developers pueden bypass con --no-verify (aceptable para emergencias)

### Neutrales

- INFO Requiere documentación de instalación de hooks
- INFO Scripts deben ser cross-platform (bash en Linux/macOS/Git Bash Windows)

## Plan de Implementación

1. **Fase 1: pre-commit hook** (Completado)
   - 5 validaciones rápidas: emojis, shell syntax, python syntax, debug statements, file sizes
   - Runtime: < 5 segundos
   - Timeframe: 1 día

2. **Fase 2: commit-msg hook** (Completado)
   - Validación Conventional Commits
   - Detección de emojis en mensajes
   - Runtime: < 1 segundo
   - Timeframe: 0.5 días

3. **Fase 3: pre-push hook** (Completado)
   - 7 validaciones comprehensivas:
     1. Tests (pytest)
     2. Linting (ruff + shellcheck)
     3. Shell constitution compliance
     4. Security checks (SQL injection, XSS, CSRF, Django)
     5. Compliance checks (RNF-002: NO Redis, NO email, MySQL sessions)
     6. Documentation quality
     7. Large files check
   - Runtime: 30-60 segundos
   - Timeframe: 2 días

4. **Fase 4: pre-rebase hook** (Completado)
   - Protección de branches publicadas
   - Runtime: < 1 segundo
   - Timeframe: 0.5 días

5. **Fase 5: Documentación y automatización** (Completado)
   - ESTRATEGIA_GIT_HOOKS.md
   - Script de instalación (opcional)
   - Timeframe: 1 día

## Validación y Métricas

**Criterios de Éxito:**

- pre-commit runtime < 5 segundos (p95): ACHIEVED
- pre-push runtime < 60 segundos (p95): ACHIEVED
- CI/CD failures reduction > 30%: TO MEASURE
- Developer adoption > 80%: TO MEASURE

**Cómo medir:**

- Timing interno en cada hook
- GitHub Actions analytics (failed jobs trend)
- Developer survey (post-implementation)

**Revisión:**

- Fecha de revisión programada: 2025-12-09
- Responsable de seguimiento: DevOps Lead

## Distribución de Validaciones

### pre-commit (< 5s)

1. NO emojis (CRITICAL)
2. Shell syntax check
3. Python syntax check
4. NO debug statements (WARNING)
5. File size limits

### commit-msg (< 1s)

1. Conventional Commits format
2. NO emojis en mensaje

### pre-push (< 60s)

1. Tests (pytest)
2. Linting (ruff + shellcheck)
3. Shell constitution (ALL scripts)
4. Security validations (CRITICAL)
5. Compliance validations (CRITICAL)
6. Documentation quality (WARNING)
7. Large files check (WARNING)

### pre-rebase (< 1s)

1. Protect published branches

## Alternativas Descartadas

### Git LFS Hooks

**Por qué se descartó:**

- NO relevante para nuestro caso de uso (no usamos LFS)
- Agrega complejidad innecesaria

### GitHub Actions como Pre-receive Hook

**Por qué se descartó:**

- Requiere push para ejecutar (NO cumple requisito de validación local)
- Latencia alta (red + queue + ejecución)

## Referencias

- [Documentación Git Hooks Strategy](../../ESTRATEGIA_GIT_HOOKS.md)
- [Resumen Migración Shell Scripts](../../RESUMEN_MIGRACION_SHELL_SCRIPTS.md)
- [ADR-002: Suite Calidad Código](ADR-002-suite-calidad-codigo.md)
- [Git Hooks Official Documentation](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)
- [Conventional Commits Specification](https://www.conventionalcommits.org/)

## Notas Adicionales

**Decisión tomada en**: Sprint de migración de shell scripts (Nov 2025)
**Implementación completada**: 2025-11-09

**Hooks implementados**:

- pre-commit: 177 líneas, 5 checks
- commit-msg: 77 líneas, 2 checks
- pre-push: 322 líneas, 7 checks
- pre-rebase: ~100 líneas, 1 check

**Scripts reutilizados desde CI/CD**:

- scripts/workflows/check_no_emojis.sh
- scripts/validation/security/\*.sh (4 scripts)
- scripts/validation/compliance/\*.sh (4 scripts)
- scripts/validation/docs/\*.sh (3 scripts)
- scripts/validation/guides/\*.sh (4 scripts)
- scripts/validation/quality/validate_shell_constitution.sh

**Bypass mechanism**:

```bash
# Para emergencias (use con precaución)
git commit --no-verify
git push --no-verify
```

---

**Estado**: Implementado y en uso
**Próxima revisión**: 2025-12-09
**Impacto medido**: Pendiente análisis post-1 mes uso
