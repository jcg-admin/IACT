---
title: Prevención de Emojis en Documentación de Tareas
date: 2025-11-13
domain: general
status: active
---

# Prevención de Emojis en Documentación de Tareas

## Problema Identificado

Durante la generación masiva de archivos TASK-*.md (commits 084f820 y anteriores), se introdujeron emojis y caracteres especiales en 20 archivos, violando la política estricta del proyecto de NO emojis/NO iconos documentada en:
- docs/ANALISIS_POLITICA_NO_EMOJIS.md
- docs/gobernanza/GUIA_ESTILO.md

## Archivos Afectados (20)

### Categorías con emojis detectados:
- QA (2): TASK-032, TASK-037
- Arquitectura (5): TASK-010, TASK-011, TASK-017, TASK-028, TASK-035
- Operaciones (2): TASK-036, TASK-038
- Gobernanza (3): TASK-012, TASK-016, TASK-024
- Features (2): TASK-033, TASK-034
- Observabilidad (2): TASK-020, TASK-021
- Seguridad (1): TASK-023
- AI Capabilities (2): TASK-025, TASK-026
- Analytics (1): TASK-027

### Emojis/iconos detectados:
- ✅ (checkmark) - usado para compliance
- ▼ (triangulo abajo) - usado para jerarquías
- Otros caracteres Unicode de formato

## Solución Aplicada

### 1. Script de Limpieza Automatizado

Creado script `/tmp/remove_all_special.py` que reemplaza:
- ✅ -> [OK]
- ❌ -> [NO]
- ▼ -> =>
- Otros emojis -> texto equivalente

### 2. Corrección Masiva

Ejecutado en 20 archivos con 100% de éxito:
```bash
python3 /tmp/remove_all_special.py <archivo>
```

### 3. Validación

```bash
git diff --name-only HEAD~8 | grep "TASK-.*\.md" | xargs python3 scripts/workflows/check_no_emojis.py
# Resultado: OK - No se encontraron emojis en 36 archivos verificados
```

## Medidas Preventivas

### Para Agentes de Documentación

Cuando generes archivos TASK-*.md, aplica estas reglas:

1. **NO usar emojis/iconos NUNCA**
   - NO: ✅ ❌ ✓ ✗ ⚠️ 🚀 📝 🔍 🎯
   - SI: [OK] [NO] [x] [ ] ADVERTENCIA: (texto simple)

2. **NO usar caracteres Unicode especiales**
   - NO: ▼ ► ◆ ● ○ ■ □ ▲ △ ▽ ◇ ◎
   - SI: => - ^ v (ASCII básico)

3. **Alternativas recomendadas:**
   - Estado OK: [OK] o "Cumple"
   - Estado NO: [NO] o "No cumple"
   - Checkboxes: [x] completado, [ ] pendiente
   - Advertencias: "ADVERTENCIA:" o "Nota:"
   - Jerarquías: => o - (guión)
   - Bullets: - o * (ASCII)

### Técnicas de Prompt Engineering Aplicables

**Constitutional AI (scripts/ai/agents/base/constitutional_ai.py)**
Agregar guardrail explícito:
```
NUNCA uses emojis, iconos o caracteres Unicode especiales.
Solo usa caracteres ASCII básicos: A-Z, a-z, 0-9, -, _, ., /, [], ()
Reemplaza cualquier emoji con texto equivalente: ✅ -> [OK]
```

**Self-Consistency (scripts/ai/agents/base/self_consistency.py)**
Validar múltiples veces:
- Genera el contenido
- Valida con check_no_emojis.py
- Si falla, regenera sin emojis
- Repite hasta pasar validación

**Tool-use Prompting (scripts/ai/agents/base/tool_use_prompting.py)**
Usar herramienta de validación:
```python
# Después de generar archivo
result = subprocess.run(['python3', 'scripts/workflows/check_no_emojis.py', filepath])
if result.returncode != 0:
    # Regenerar sin emojis
    content = remove_emojis(content)
```

### Pre-commit Hook Recomendado

Agregar a `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Validar NO emojis antes de commit
git diff --cached --name-only | grep "\.md$" | while read file; do
    python3 scripts/workflows/check_no_emojis.py "$file" || exit 1
done
```

### CI/CD Validation

Agregar paso en GitHub Actions:
```yaml
- name: Validate NO emojis policy
  run: |
    find docs -name "*.md" | xargs python3 scripts/workflows/check_no_emojis.py
```

## Lecciones Aprendidas

1. **Agentes deben tener guardrails explícitos** sobre restricciones del proyecto
2. **Validación automatizada** debe ejecutarse inmediatamente después de generación
3. **Self-consistency** es crítica para cumplir políticas estrictas
4. **Constitutional AI** debe incluir reglas de formato de documentación
5. **Tool-use** debe invocar check_no_emojis.py antes de finalizar

## Referencias

- docs/ANALISIS_POLITICA_NO_EMOJIS.md (política completa)
- docs/gobernanza/GUIA_ESTILO.md (guía de estilo)
- scripts/workflows/check_no_emojis.py (validador)
- scripts/ai/agents/base/constitutional_ai.py (técnica aplicable)
- scripts/ai/agents/base/self_consistency.py (técnica aplicable)
- scripts/ai/agents/base/tool_use_prompting.py (técnica aplicable)

## Aplicación Inmediata

Para CUALQUIER generación futura de archivos TASK-*.md:

1. Incluir guardrail Constitutional AI: "NO emojis NUNCA"
2. Validar con check_no_emojis.py después de generar
3. Usar Self-Consistency si validación falla
4. Documentar técnicas aplicadas en sección del archivo

## Resolución

**Commit de corrección:** [hash del próximo commit]
**Archivos corregidos:** 20
**Validación final:** PASS (0 emojis en 36 archivos TASK)
**Estado:** RESUELTO
