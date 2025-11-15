---
name: DocumentSplitter
description: Divide documentos extensos en módulos coherentes manteniendo referencias cruzadas e índice maestro.
---

# Documentation Splitter Agent

`DocumentSplitter` (`scripts/coding/ai/documentation/document_splitter.py`) automatiza la división de documentos Markdown largos en módulos navegables. Mantiene coherencia temática, genera referencias cruzadas y produce un índice maestro con métricas de balance.

## Capacidades

- Analiza la estructura de encabezados (`H1`, `H2`, `H3`) para detectar secciones y sub-secciones.
- Agrupa secciones relacionadas en módulos lógicos respetando límites mínimos/máximos de líneas.
- Genera referencias cruzadas entre módulos y las inserta automáticamente en el contenido.
- Construye un índice maestro con resumen por módulo y estadísticas de tamaño.
- Valida guardrails (mínimo 2 módulos, equilibrio de tamaños, límites máximos) antes de concluir.

## Entradas y Salidas

- **Entradas**
  - `document`: texto Markdown a modularizar.
  - Configuración opcional (`max_lines`, `min_lines`, `preserve_metadata`).
- **Salidas**
  - Diccionario con módulos resultantes, cross-references, índice maestro y métricas de tamaño.
  - Lista de errores de guardrails cuando se infringen límites.

## Uso

```python
from scripts.coding.ai.documentation.document_splitter import DocumentSplitter

splitter = DocumentSplitter({"max_lines": 800, "min_lines": 150})
result = splitter.run({
    "document": Path("docs/analisis/ANALISIS_NEGOCIO.md").read_text(),
    "component_name": "Onboarding"
})
print(result["module_count"], result["cross_references"][:3])
```

## Validaciones Relacionadas

- Ejecutar `splitter.apply_guardrails(result)` para asegurarse de que la división cumpla estándares.
- Integrar en pipelines de sincronización documental (`scripts/coding/ai/documentation/sync_agent.py`) antes de publicar cambios.
