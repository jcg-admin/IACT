---
name: LLMGenerator
description: Genera código de tests desde planes estructurados usando proveedores LLM configurables.
---

# LLM Test Generator Agent

`LLMGenerator` (`scripts/coding/ai/generators/llm_generator.py`) encapsula la generación de suites de tests basadas en LLM. Soporta proveedores Anthropic, OpenAI, Ollama y Hugging Face, cargando credenciales desde `.env` y produciendo código alineado con los estándares del proyecto.

## Capacidades

- Valida insumos: lista de `test_plans`, ruta del proyecto y presencia de API keys cuando son necesarias.
- Construye prompts ricos con contexto (código fuente, convenciones de testing, estrategias TDD).
- Invoca el proveedor configurado y empaqueta la respuesta en estructuras listas para persistir.
- Soporta ejecución local (Ollama) o remota (Anthropic/OpenAI/HF) con configuración flexible.
- Devuelve métricas de generación, incluyendo cantidad de archivos creados y modelo utilizado.

## Entradas y Salidas

- **Entradas**
  - `test_plans`: colección de planes con `source_file`, `test_file` y `test_cases`.
  - `project_path`: ruta base del repositorio.
  - Configuración con `llm_provider`, `model`, parámetros HF/Ollama.
- **Salidas**
  - `generated_tests`: lista con código generado y metadatos por archivo.
  - `total_generated`: conteo de archivos exitosos.
  - Datos de proveedor/modelo para trazabilidad.

## Uso

```python
from scripts.coding.ai.generators.llm_generator import LLMGenerator

generator = LLMGenerator({"llm_provider": "anthropic"})
result = generator.run({
    "test_plans": [{
        "source_file": "scripts/coding/ai/shared/agent_base.py",
        "test_file": "tests/test_agent_base.py",
        "test_cases": ["should record status transitions", "should persist results"]
    }],
    "project_path": "."
})
print(result["total_generated"], result["generated_tests"][0]["test_file"])
```

## Validaciones Relacionadas

- Ejecutar `generator.validate_input(...)` antes de correr para detectar credenciales faltantes.
- Usar en conjunto con `scripts/coding/ai/test_generation_orchestrator.py` o `SDLCTestingAgent` para pipelines TDD automatizados.
