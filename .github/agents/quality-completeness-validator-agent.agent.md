---
name: CompletenessValidator
description: Evalúa la completitud de análisis de negocio verificando artefactos, trazabilidad y estándares.
---

# Business Analysis Completeness Validator Agent

`CompletenessValidator` (`scripts/coding/ai/quality/completeness_validator.py`) verifica que un análisis de negocio cumpla estándares ISO 29148, BABOK v3 y lineamientos IACT. Analiza artefactos estructurados o documentos Markdown y produce checklist detallado con porcentaje de completitud.

## Capacidades

- Valida presencia de secciones obligatorias (contexto, procesos, reglas, UC, requisitos, matriz de trazabilidad) y opcionales.
- Evalúa trazabilidad bidireccional, nomenclatura consistente y conformidad con estándares configurables.
- Genera recomendaciones y lista priorizada de elementos faltantes.
- Produce documento Markdown con checklist completo e indicadores de calidad.
- Permite configurar umbrales mínimos (`min_completeness`) y modo estricto.

## Entradas y Salidas

- **Entradas**
  - `document` (Markdown) o artefactos estructurados (`use_cases`, `requirements`, etc.).
  - Configuración (`validate_iso_29148`, `validate_babok_v3`, `validate_uml_2_5`, `strict_mode`).
- **Salidas**
  - Checklist con categorías (`sections`, `traceability`, `standards`, `nomenclature`, `quality`).
  - `completeness` (float), `missing_items`, `recommendations` y `checklist_document`.

## Uso

```python
from scripts.coding.ai.quality.completeness_validator import CompletenessValidator

validator = CompletenessValidator({"min_completeness": 0.9})
result = validator.run({
    "document": Path("docs/analisis/ANALISIS_NEGOCIO.md").read_text(),
    "component_name": "Gestión de Campañas"
})
print(result["summary"]["completeness"], len(result["missing_items"]))
```

## Validaciones Relacionadas

- Ejecutar `validator.validate_input(...)` antes de procesar para asegurar insumos mínimos.
- Integrar el resultado con `TraceabilityMatrixGenerator` y `BusinessAnalysisPipeline` para completar revisiones automáticas.
