---
name: CoverageVerifier
description: Comprueba que nuevos tests incrementen la cobertura mínima requerida y analiza mejoras por archivo.
---

# Coverage Verifier Agent

`CoverageVerifier` (`scripts/coding/ai/quality/coverage_validator.py`) garantiza que la cobertura aumente tras generar y ejecutar nuevos tests. Escribe temporalmente los tests validados, corre pytest con coverage y compara el porcentaje con el baseline.

## Capacidades

- Valida entradas requeridas (`current_coverage`, `test_results`, `project_path`).
- Persistente temporal de tests generados y limpieza automática al finalizar.
- Ejecuta coverage y calcula incremento global, verificando que supera `min_coverage_increase` (5% por defecto).
- Analiza mejoras por archivo usando `prioritized_targets` para medir impacto.
- Informa cantidad de archivos mejorados y si se cumple el objetivo.

## Entradas y Salidas

- **Entradas**
  - `current_coverage`: cobertura base antes de aplicar tests.
  - `test_results`: resultados generados (pasan) y opcional `validated_tests` con código.
  - `project_path`: ruta del repositorio.
  - `prioritized_targets`: lista opcional para correlacionar mejoras.
- **Salidas**
  - `new_coverage`, `coverage_increase`, `meets_requirement`.
  - `file_improvements`: detalle por archivo con diferencia de cobertura.

## Uso

```python
from scripts.coding.ai.quality.coverage_validator import CoverageVerifier

verifier = CoverageVerifier({"min_coverage_increase": 3.0})
result = verifier.run({
    "current_coverage": 78.5,
    "test_results": generated_tests,
    "validated_tests": validated,
    "project_path": Path.cwd()
})
print(result["meets_requirement"], result["coverage_increase"])
```

## Validaciones Relacionadas

- Ejecutar `verifier.validate_input(...)` para garantizar insumos completos.
- Usar después de `CoverageAnalyzer` y `SyntaxValidator` dentro de pipelines TDD automatizados.
