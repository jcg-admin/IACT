---
name: TestRunner
description: Ejecuta tests validados en sandbox temporal y reporta resultados detallados.
---

# Test Runner Agent

`TestRunner` (`scripts/coding/ai/shared/test_runner.py`) ejecuta los tests generados en un entorno temporal antes de escribirlos definitivamente. Permite validar funcionalidad, captura logs de pytest y entrega métricas de éxito/falla.

## Capacidades

- Valida presencia de `validated_tests` y `project_path` antes de correr.
- Escribe cada test en un archivo temporal dentro de `tmp/ai_test_runner` para evitar ensuciar el repositorio.
- Ejecuta pytest con opciones verbosas y `--tb=short` para salidas compactas.
- Calcula métricas por archivo (duración, exit code) y agrega totales (`success_rate`, `total_passed`, `total_failed`).
- Devuelve la salida de pytest por archivo para debugging.

## Entradas y Salidas

- **Entradas**
  - `validated_tests`: lista de tests con código listo para ejecutar.
  - `project_path`: ruta base del proyecto.
- **Salidas**
  - `test_results`: tests que pasan con output y métricas.
  - `execution_errors`: lista de fallos con detalle.
  - `success_rate`, `total_passed`, `total_failed`.

## Uso

```python
from scripts.coding.ai.shared.test_runner import TestRunner

runner = TestRunner()
result = runner.run({
    "validated_tests": validated,
    "project_path": Path.cwd()
})
print(result["success_rate"], result["execution_errors"])
```

## Validaciones Relacionadas

- Ejecutar `runner.validate_input(...)` para garantizar que existan tests y ruta válida.
- Integrar sus resultados con `CoverageVerifier` y `PRCreator` dentro del pipeline automatizado.
