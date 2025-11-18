"""
Agentes SDLC - Directorio Legacy

Este directorio contiene documentación histórica de los agentes SDLC.

**NOTA**: Los agentes han sido reorganizados en dominios separados:

- **SDLC Agents**: `scripts/ai/sdlc/`
- **TDD System**: `scripts/ai/tdd/`
- **Quality Validators**: `scripts/ai/quality/`
- **Business Analysis**: `scripts/ai/business_analysis/`
- **Documentation**: `scripts/ai/documentation/`
- **Generators**: `scripts/ai/generators/`
- **Automation**: `scripts/ai/automation/`
- **Shared Components**: `scripts/ai/shared/`

Para imports, usar las nuevas ubicaciones:

```python
# Antes:
from scripts.coding.ai.agents.sdlc_planner import SDLCPlannerAgent

# Ahora:
from scripts.coding.ai.sdlc.planner_agent import PlannerAgent
```

Ver documentación completa en los READMEs de este directorio.
"""

# Importaciones legacy para compatibilidad temporal (deprecated)
import warnings

def __getattr__(name):
    """Provide backward compatibility with deprecation warnings."""
    warnings.warn(
        f"Importing from scripts.coding.ai.agents is deprecated. "
        f"Please update imports to use domain-specific modules "
        f"(scripts.ai.sdlc, scripts.ai.tdd, scripts.ai.quality, etc.)",
        DeprecationWarning,
        stacklevel=2
    )
    raise AttributeError(f"Module 'scripts.ai.agents' has no attribute '{name}'")
