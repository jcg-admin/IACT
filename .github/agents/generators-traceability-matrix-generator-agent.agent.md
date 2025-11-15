---
name: TraceabilityMatrixGenerator
description: Construye matrices RTM y análisis de gaps a partir de artefactos de análisis y pruebas.
---

# Traceability Matrix Generator Agent

`TraceabilityMatrixGenerator` (`scripts/coding/ai/generators/traceability_matrix_generator.py`) automatiza la creación de matrices de trazabilidad conforme a ISO/IEC/IEEE 29148:2018. Recibe artefactos generados por Business Analysis y produce matrices, análisis de brechas y métricas de cobertura.

## Capacidades

- Valida artefactos obligatorios (`use_cases`, `requirements_functional`) y la estructura de cada entrada.
- Genera múltiples matrices: principal (Necesidad→Proceso→UC→Requisito→Prueba→Implementación), Proceso-UC-Requisito, UC-Requisito-Prueba y Reglas-Impacto.
- Detecta gaps (requisitos huérfanos, UC sin requisitos, requisitos sin pruebas o implementación, reglas sin aplicación).
- Calcula índices clave: trazabilidad, cobertura de pruebas e implementación.
- Permite configurar umbrales mínimos y decidir si incluye estado de implementación.

## Entradas y Salidas

- **Entradas**
  - Artefactos estructurados (`processes`, `business_rules`, `use_cases`, `requirements_functional`, `requirements_nonfunctional`, `test_cases`, `implementations`).
  - Configuración (`min_traceability_index`, `min_coverage_index`, `include_implementation_status`).
- **Salidas**
  - Diccionario con matrices generadas, análisis de gaps, métricas globales e insights por dominio.
  - Reporte de cumplimiento contra umbrales configurados.

## Uso

```python
from scripts.coding.ai.generators.traceability_matrix_generator import TraceabilityMatrixGenerator

generator = TraceabilityMatrixGenerator({"min_traceability_index": 0.9})
result = generator.run({
    "processes": processes,
    "use_cases": use_cases,
    "requirements_functional": requirements,
    "test_cases": test_cases
})
print(result["metrics"]["traceability_index"], result["gaps"]["requirements_without_tests"])
```

## Validaciones Relacionadas

- Ejecutar `generator.validate_input(...)` para garantizar integridad de artefactos antes de la generación.
- Consumir su salida desde `BusinessAnalysisPipeline` y `CompletenessValidator` para verificar cumplimiento integral.
