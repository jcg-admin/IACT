---
id: RT-003
tipo: regla_tecnica
relacionado: [ADR-046]
fecha: 2025-11-16
---

# RT-003: Clean Code Naming

## Constraint

El sistema DEBE generar nombres siguiendo convenciones Clean Code: sin emojis, snake_case, prefijos estandarizados.

## Formatos por Tipo

```python
FORMATOS_NOMBRE = {
    "task": "TASK-{id:03d}-{descripcion}.md",
    "adr": "ADR-{id:03d}-{titulo}.md",
    "solicitud": "REQ-{id:03d}-{descripcion}.md",
    "analisis": "ANALISIS_{tema}_{fecha:%Y%m%d}.md",
    "sesion": "SESSION_{tema}_{fecha:%Y_%m_%d}.md",
    "reporte_limpieza": "CLEANUP_REPORT_{fecha:%Y%m%d}.md",
    "documentacion_agente": "README_{agent_name}.md",
    "guia": "GUIA_{tema}.md",
    "procedimiento": "PROC-{id:03d}-{nombre}.md",
    "indice": "INDEX.md",  # Siempre este nombre
    "configuracion_agente": "{agent_name}_config.json",
    "script": "{accion}_{objeto}.{ext}",
}
```

## Normalizacion de Descripcion

```python
def normalizar_descripcion(desc: str) -> str:
    # 1. Eliminar emojis y caracteres especiales
    desc = re.sub(r'[^\w\s-]', '', desc)

    # 2. Convertir a lowercase
    desc = desc.lower()

    # 3. Reemplazar espacios/guiones por underscores
    desc = desc.replace(' ', '_').replace('-', '_')

    # 4. Eliminar underscores multiples
    desc = re.sub(r'_+', '_', desc)

    # 5. Trim underscores extremos
    desc = desc.strip('_')

    return desc
```

## Ejemplos de Transformacion

```python
transformaciones = {
    "Análisis de Docs 📊": "analisis_de_docs",
    "TASK: Fix Bug 🐛": "task_fix_bug",
    "Guía---Testing": "guia_testing",
    "Feature___Nueva": "feature_nueva",
    "___cleanup___": "cleanup",
}
```

## Validacion

Tests: `scripts/coding/tests/ai/test_placement_naming.py`

```gherkin
Given descripcion "Fix Bug 🐛 en Login"
When normalizar_descripcion(descripcion)
Then resultado == "fix_bug_en_login"
  And "🐛" not in resultado
```

## Restricciones

- Longitud maxima: 255 caracteres (limite filesystem)
- Solo caracteres: `[a-z0-9_.-]`
- NO emojis: `[\U0001F300-\U0001F9FF]`
- NO iconos: caracteres unicode decorativos

## Implementacion

Archivo: `scripts/coding/ai/agents/placement/naming.py`

```python
def construir_nombre(tipo: str, contexto: dict) -> str:
    formato = FORMATOS_NOMBRE[tipo]

    # Normalizar descripcion si existe
    if "descripcion" in contexto:
        contexto["descripcion"] = normalizar_descripcion(contexto["descripcion"])

    # Aplicar formato
    return formato.format(**contexto)
```

## Referencias

- ADR-046: Arquitectura de clasificacion
- Clean Code Principles: Nombres descriptivos sin decoracion
- Cleanup nov 2025: Elimino 47 archivos con emojis
