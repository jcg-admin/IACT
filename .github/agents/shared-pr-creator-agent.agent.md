---
name: PRCreator
description: Automatiza la creación de branches y Pull Requests con los tests generados y métricas de cobertura.
---

# Pull Request Creator Agent

`PRCreator` (`scripts/coding/ai/shared/pr_creator.py`) automatiza la última milla del pipeline TDD. Toma tests validados, escribe los archivos en el repositorio, crea una rama, realiza commit y abre un Pull Request usando la CLI de GitHub (`gh`).

## Capacidades

- Valida la presencia de tests aprobados, métricas de cobertura y ruta del proyecto.
- Escribe los tests generados en disco utilizando el código validado (`validated_tests`).
- Crea ramas con nomenclatura `bot/generated-tests-<timestamp>` y realiza commits con resúmenes de cobertura.
- Construye cuerpo de PR incluyendo incremento de cobertura y archivos afectados; etiqueta con `bot-generated-tests`.
- Invoca `gh pr create` para abrir el PR y devuelve URL del resultado.

## Entradas y Salidas

- **Entradas**
  - `test_results`: lista de tests aprobados por `TestRunner`/`SyntaxValidator`.
  - `validated_tests`: código listo para escribir.
  - Métricas de cobertura (`previous_coverage`, `new_coverage`, `coverage_increase`).
  - `project_path`: ruta del repositorio.
- **Salidas**
  - `pr_created`, `pr_url`, `branch_name`, `files_added`, `total_tests_added`.

## Uso

```python
from scripts.coding.ai.shared.pr_creator import PRCreator

creator = PRCreator()
result = creator.run({
    "test_results": passed_tests,
    "validated_tests": validated,
    "previous_coverage": 82.1,
    "new_coverage": 87.4,
    "coverage_increase": 5.3,
    "project_path": Path.cwd()
})
print(result["pr_url"], result["branch_name"])
```

## Validaciones Relacionadas

- Ejecutar `creator.validate_input(...)` antes de correr para asegurar insumos completos y evitar PRs vacíos.
- Requiere tener configurado `gh` autenticado y permisos de escritura en el repositorio.
