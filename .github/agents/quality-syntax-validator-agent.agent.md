---
name: SyntaxValidator
description: Valida sintaxis, estilo y formato de tests generados antes de integrarlos al repositorio.
---

# Syntax Validator Agent

`SyntaxValidator` (`scripts/coding/ai/quality/syntax_validator.py`) asegura que el código de tests generado cumpla estándares de sintaxis, lint y formato. Ejecuta validaciones secuenciales con AST, ruff, black y opcionalmente mypy, devolviendo los archivos corregidos y métricas de éxito.

## Capacidades

- Verifica sintaxis Python compilando a AST y reporta errores precisos por línea.
- Ejecuta `ruff` para linting y `black` para formato, aplicando correcciones cuando sea necesario.
- Soporta validación opcional de tipos con `mypy` (controlado por configuración `run_mypy`).
- Registra tests validados, códigos originales y si se reformateó contenido.
- Devuelve lista de errores por etapa (syntax, ruff, mypy) para debugging.

## Entradas y Salidas

- **Entradas**
  - `generated_tests`: lista de estructuras con `test_file` y `generated_code`.
  - Configuración (`run_mypy`).
- **Salidas**
  - `validated_tests`: tests con código formateado listo para escritura.
  - `validation_errors`: lista de errores por archivo y etapa.
  - `success_rate`, `total_validated`, `total_errors`.

## Uso

```python
from scripts.coding.ai.quality.syntax_validator import SyntaxValidator

validator = SyntaxValidator({"run_mypy": True})
result = validator.run({"generated_tests": generated_tests})
print(result["success_rate"], len(result["validation_errors"]))
```

## Validaciones Relacionadas

- Ejecutar `validator.validate_input(...)` para asegurar que se reciban tests.
- Encadenar con `CoverageVerifier` para medir impacto antes de fusionar los cambios.
