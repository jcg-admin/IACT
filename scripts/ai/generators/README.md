# Generators

Generadores de código, plantillas y matrices de trazabilidad.

## Módulos

- `llm_generator.py` - Genera código usando LLM
- `template_generator.py` - Genera plantillas personalizables
- `traceability_matrix_generator.py` - Genera matrices RTM

## Uso

```python
from scripts.ai.generators.llm_generator import LLMGenerator

generator = LLMGenerator()
code = generator.generate(prompt)
```
