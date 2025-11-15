---
name: BusinessAnalysisGenerator
description: Orquesta la generación completa de análisis de negocio (procesos, reglas, casos de uso y requisitos trazables).
---

# Business Analysis Generator Agent

`BusinessAnalysisGenerator` reside en `scripts/coding/ai/business_analysis/generator.py` y produce documentación integral de análisis de negocio alineada con ISO/IEC/IEEE 29148, BABOK v3 y estándares internos IACT. El agente transforma un briefing funcional en un documento maestro con artefactos completos y trazables.

## Capacidades

- Valida insumos obligatorios (`component_name`, `domain`, `business_objective`, `stakeholders`) y estructura de stakeholders.
- Genera procesos de negocio, reglas clasificadas, casos de uso detallados, requisitos funcionales y no funcionales, así como procedimientos operacionales.
- Crea matrices de trazabilidad RTM y relaciona artefactos por identificadores consistentes (PROC, RN, UC, RF, RNF).
- Permite habilitar/deshabilitar procedimientos y requisitos no funcionales mediante configuración.
- Produce un resumen consolidado listo para revisión y almacenamiento en repositorio de documentación.

## Entradas y Salidas

- **Entradas**
  - Diccionario con datos del componente (objetivo, alcance, stakeholders, restricciones, etc.).
  - Flags opcionales: `include_procedures`, `include_nfr`, dominio específico.
- **Salidas**
  - Estructura con listas de procesos, reglas, casos de uso, requisitos, procedimientos y métricas de trazabilidad.
  - Documento maestro generado en Markdown con secciones jerárquicas.

## Uso

```python
from scripts.coding.ai.business_analysis.generator import BusinessAnalysisGenerator

generator = BusinessAnalysisGenerator({"include_nfr": True})
analysis = generator.run({
    "component_name": "Gestor de Campañas",
    "domain": "marketing",
    "business_objective": "Automatizar campañas omnicanal",
    "stakeholders": [{"rol": "Gerente Marketing", "interes": "Planificación"}]
})
print(analysis["summary"]["traceability_index"])
```

## Validaciones Relacionadas

- Ejecutar `scripts/coding/ai/quality/completeness_validator.py` para garantizar cobertura de artefactos generados.
- Integrar con `scripts/coding/ai/business_analysis/pipeline.py` para ensamblar pipeline completo junto a matrices de trazabilidad y validadores.
