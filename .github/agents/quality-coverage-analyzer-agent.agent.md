---
name: CoverageAnalyzer
description: Ejecuta pytest con coverage y prioriza archivos con baja cobertura para acciones TDD.
---

# Coverage Analyzer Agent

`CoverageAnalyzer` (`scripts/coding/ai/quality/coverage_analyzer.py`) analiza cobertura de código ejecutando pytest con reportes JSON. Identifica archivos con cobertura inferior al umbral, prioriza targets y calcula brecha frente al objetivo mínimo.

## Capacidades

- Valida rutas del proyecto antes de ejecutar.
- Lanza pytest con `--cov` y `--cov-report=json` para obtener métricas detalladas.
- Detecta archivos/funciones con baja cobertura y calcula líneas faltantes.
- Prioriza objetivos según porcentaje actual y tamaño del archivo.
- Calcula métricas globales (`current_coverage`, `coverage_gap`, `files_below_threshold`).

## Entradas y Salidas

- **Entradas**
  - `project_path`: ruta del repositorio a analizar.
  - Configuración (`min_coverage`, `threshold_low`).
- **Salidas**
  - `current_coverage`, `coverage_gap`, lista de `low_coverage_files` con detalles y `prioritized_targets`.
  - Ruta del reporte JSON (`coverage_report_path`).

## Uso

```python
from scripts.coding.ai.quality.coverage_analyzer import CoverageAnalyzer

analyzer = CoverageAnalyzer({"min_coverage": 90})
report = analyzer.run({"project_path": Path.cwd()})
print(report["current_coverage"], report["low_coverage_files"][:2])
```

## Validaciones Relacionadas

- Ejecutar `analyzer.validate_input(...)` para asegurar que la ruta exista y sea accesible.
- Reutilizar los resultados en `CoverageVerifier` o pipelines de mejora continua PDCA.
