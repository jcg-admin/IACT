# Quality Assurance & Validation

Validadores de calidad de código y completitud.

## Validators

- `code_quality_validator.py` - Valida calidad con ruff, mypy, bandit
- `completeness_validator.py` - Valida completitud de análisis
- `syntax_validator.py` - Valida sintaxis Python
- `coverage_analyzer.py` - Analiza gaps de cobertura
- `coverage_validator.py` - Verifica incremento de cobertura

## Uso

```python
from scripts.ai.quality.code_quality_validator import CodeQualityValidator

validator = CodeQualityValidator()
result = validator.validate(source_files)
```
