---
name: TemplateGenerator
description: Produce plantillas Markdown estandarizadas para análisis de negocio y requisitos.
---

# Template Generator Agent

`TemplateGenerator` (`scripts/coding/ai/generators/template_generator.py`) genera plantillas reutilizables para artefactos de análisis. Acepta diferentes tipos (`master_document`, `rtm_matrix`, `completeness_checklist`, `business_rule`, `use_case`, `requirement_spec`) y personaliza placeholders según parámetros.

## Capacidades

- Valida el tipo de plantilla solicitado y expone lista de opciones soportadas.
- Inserta placeholders `[COMPLETAR]`, ejemplos y secciones obligatorias basadas en estándares ISO 29148, BABOK v3 y UML.
- Calcula métricas de salida (líneas, tamaño, cantidad de placeholders).
- Aplica guardrails para asegurar longitud mínima y ausencia de emojis.
- Permite habilitar instrucciones y ejemplos mediante flags (`include_examples`, `include_instructions`).

## Entradas y Salidas

- **Entradas**
  - `template_type`: tipo requerido.
  - `parameters`: diccionario opcional con datos como `component_name`, `domain`, etc.
- **Salidas**
  - `template_content`: texto Markdown generado.
  - Métricas (`line_count`, `placeholder_count`, `size_bytes`).
  - `parameters_used`: parámetros efectivos.

## Uso

```python
from scripts.coding.ai.generators.template_generator import TemplateGenerator

generator = TemplateGenerator({"include_examples": False})
result = generator.run({
    "template_type": "use_case",
    "parameters": {"component_name": "Portal de Pagos"}
})
print(result["template_content"].splitlines()[:10])
```

## Validaciones Relacionadas

- Ejecutar `generator.validate_input(...)` previo a la generación.
- Utilizar `generator.apply_guardrails(result)` para asegurar que la plantilla cumple estándares antes de publicarla.
