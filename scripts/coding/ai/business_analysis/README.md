# Business Analysis

Generadores de documentación de análisis de negocio siguiendo ISO 29148, BABOK v3 y UML 2.5.

## Módulos

- `generator.py` - Genera análisis completo (Procesos → UC → Requisitos)
- `pipeline.py` - Orquesta generación end-to-end

## Uso

```python
from scripts.ai.business_analysis.generator import BusinessAnalysisGenerator

generator = BusinessAnalysisGenerator()
result = generator.generate(request_description)
```

Ver `scripts/ai/agents/README_BUSINESS_ANALYSIS.md` para documentación completa.
