# Prompting Techniques Framework

**Location:** General AI Capabilities (transversal a todo el proyecto)
**Status:** Production-ready
**Version:** 1.0

---

## Overview

Framework completo de 38 técnicas avanzadas de prompting engineering, aplicables a **cualquier componente del proyecto** (backend, frontend, features, operaciones, etc.).

Estas técnicas son **generales y transversales**, no específicas a un módulo particular.

### Scope

- **Backend:** Agentes de validación, generación de tests, análisis de código
- **Frontend:** Generación de componentes, análisis de UX, documentación
- **Features:** Análisis predictivo, auto-remediación, optimización
- **Operaciones:** Documentación automática, troubleshooting, monitoreo
- **QA:** Generación de tests, análisis de cobertura, detección de bugs

---

## Implemented Techniques (38 Total)

### Core Techniques (32)

Ver documentación completa en: [ADVANCED_PROMPTING_TECHNIQUES.md](./ADVANCED_PROMPTING_TECHNIQUES.md)

**Categorías:**
1. **Fundamental (3):** Zero-Shot, Few-Shot, Role Prompting
2. **Estructuración (4):** Chaining, Decomposition, Least-to-Most, Hierarchy
3. **Conocimiento (4):** Generated Knowledge, RAG, ReAct, Tool-use
4. **Optimización (7):** Delimiters, Constrained, Negative, Constitutional, etc.
5. **Especializadas (12):** Code Gen, Math, Analogical, Medprompt, etc.
6. **Avanzadas (5):** Auto-CoT, Chain-of-Verification, Tree of Thoughts, Self-Consistency, Templates

### Search Optimization Techniques (6)

Ver documentación completa en: [SEARCH_OPTIMIZATION_TECHNIQUES.md](./SEARCH_OPTIMIZATION_TECHNIQUES.md)

**Algoritmos de optimización de búsqueda (85-90% reducción de tokens):**
1. K-NN Clustering Prompting
2. Binary Search Prompting
3. Greedy Information Density
4. Divide-and-Conquer Search
5. Branch-and-Bound Prompting
6. **Hybrid Optimization** (Recomendado)

---

### Code Generation Guide

Material complementario centrado en estrategias de generación de código (planificación, uso de herramientas y memoria) y en patrones de prompts paso a paso está disponible en [CODE_GENERATION_GUIDE.md](./CODE_GENERATION_GUIDE.md). Resume ejemplos prácticos y recordatorios de validación para mantener alineados a los agentes orientados a código.

---

## Implementation Location

**Código:** `scripts/ai/agents/base/`

```
scripts/ai/agents/base/
├── auto_cot_agent.py                    # Auto-CoT
├── chain_of_verification.py            # Chain-of-Verification
├── prompt_templates.py                  # Templates
├── tree_of_thoughts.py                  # Tree of Thoughts
├── self_consistency.py                  # Self-Consistency
├── fundamental_techniques.py            # Zero-Shot, Few-Shot, Role
├── structuring_techniques.py            # Chaining, Decomposition, etc.
├── knowledge_techniques.py              # RAG, ReAct, Tool-use
├── optimization_techniques.py           # Delimiters, Constrained, etc.
├── specialized_techniques.py            # Code Gen, Math, Medprompt, etc.
├── search_optimization_techniques.py    # 6 algoritmos de búsqueda
└── __init__.py                          # Exports todas las técnicas
```

---

## Quick Start

### Import

```python
from scripts.ai.agents.base import (
    # Recomendado para optimización de búsquedas
    HybridSearchOptimization,
    SearchItem,
    CoverageLevel,
    Priority,

    # Verificación y validación
    ChainOfVerificationAgent,
    AutoCoTAgent,
    SelfConsistencyAgent,

    # Templates y estructuración
    PromptTemplateEngine,
    PromptChaining,

    # ... y 30+ técnicas más
)
```

### Example: Search Optimization (Cualquier Contexto)

```python
from scripts.ai.agents.base import (
    HybridSearchOptimization,
    SearchItem,
    Priority,
    CoverageLevel
)

# Ejemplo: Buscar información sobre componentes (frontend, backend, cualquiera)
components = [
    SearchItem(
        id="auth_component",
        content="Authentication component",
        priority=Priority.CRITICAL,
        keywords=["auth", "security", "login", "permissions"]
    ),
    SearchItem(
        id="ui_component",
        content="UI dashboard component",
        priority=Priority.HIGH,
        keywords=["ui", "dashboard", "visualization", "frontend"]
    ),
    # ... más componentes
]

# Optimizar búsquedas (funciona para CUALQUIER dominio)
optimizer = HybridSearchOptimization(
    k_clusters=4,
    target_coverage=CoverageLevel.BALANCED  # 85%
)

result = optimizer.optimize(components)

print(f"Queries: {len(result.queries)} (vs {len(components)} sin optimizar)")
print(f"Reducción de tokens: {result.token_reduction_percentage:.1%}")

# Ejecutar queries optimizadas
for query in result.queries:
    search_results = your_search_function(query.query_text)
    # Procesar resultados...
```

---

## Use Cases por Área

### Backend

```python
# Validación de routers de base de datos
from scripts.ai.agents.base import ChainOfVerificationAgent

verifier = ChainOfVerificationAgent()
verified = verifier.verify_response(
    question="¿El router escribe a IVR?",
    initial_response=analysis_result,
    context={"restrictions": ["IVR es READ-ONLY"]}
)
```

### Frontend

```python
# Generación de componentes React con Chain-of-Thought
from scripts.ai.agents.base import AutoCoTAgent

auto_cot = AutoCoTAgent()
demos = auto_cot.generate_demonstrations(
    questions=["Create login form", "Create dashboard", ...],
    domain="react_components"
)
```

### Features (AI)

```python
# Análisis predictivo con múltiples caminos de razonamiento
from scripts.ai.agents.base import TreeOfThoughtsAgent

tot = TreeOfThoughtsAgent()
solution, metrics = tot.solve(
    problem="Predict system failures",
    initial_thoughts=["CPU spike", "Memory leak", "Network"],
    context={"domain": "system_monitoring"}
)
```

### Operaciones

```python
# Optimizar búsqueda en documentación
from scripts.ai.agents.base import BinarySearchPrompting

binary = BinarySearchPrompting(coverage_threshold=0.80)
queries = binary.create_hierarchical_queries(
    items=documentation_topics,
    domain="deployment procedures"
)
```

### QA/Testing

```python
# Generación de tests con self-consistency
from scripts.ai.agents.base import SelfConsistencyAgent

sc = SelfConsistencyAgent(num_samples=10)
result = sc.solve_with_consistency(
    prompt="Generate test cases for authentication",
    generator_fn=llm_generator
)
```

---

## Documentation Structure

### Complete Guides

1. **[ADVANCED_PROMPTING_TECHNIQUES.md](./ADVANCED_PROMPTING_TECHNIQUES.md)**
   - Overview de las 38 técnicas
   - Ejemplos de uso
   - Patrones de integración
   - Best practices

2. **[SEARCH_OPTIMIZATION_TECHNIQUES.md](./SEARCH_OPTIMIZATION_TECHNIQUES.md)**
   - 6 algoritmos de optimización de búsqueda
   - Benchmark de performance
   - Casos de uso específicos
   - Análisis de costo-beneficio

3. **[AUTO_COT_IMPLEMENTATION.md](./AUTO_COT_IMPLEMENTATION.md)**
   - Detalles de implementación Auto-CoT
   - Integración con TDD
   - Quality metrics

### References in Other Locations

- **Backend/Permisos:** `docs/backend/permisos/promptops/` → Contiene referencias a esta ubicación general
- **Features/AI:** Pueden referenciar estas técnicas para capacidades específicas
- **Testing:** Pueden usar para generación automática de tests

---

## Why This Location?

**Razón:** Estas técnicas son **transversales y generales**, aplicables a:

- [OK] Backend (APIs, routers, validación)
- [OK] Frontend (componentes, UX, documentación)
- [OK] Features (analytics, auto-remediation)
- [OK] Operaciones (deployment, monitoring)
- [OK] QA (tests, coverage, bugs)
- [OK] Infraestructura (configuración, optimización)

**NO están limitadas** a un módulo específico como "permisos" o "backend".

Por eso están en `docs/ai_capabilities/` - son capacidades generales de AI.

---

## Contributing

Para agregar nuevas técnicas o mejorar las existentes:

1. Implementar en `scripts/ai/agents/base/`
2. Exportar en `scripts/ai/agents/base/__init__.py`
3. Documentar en este directorio (`docs/ai_capabilities/prompting/`)
4. Agregar ejemplos de uso multi-contexto (backend, frontend, etc.)

---

## Testing

```bash
# Ejecutar ejemplos de todas las técnicas
cd /home/user/IACT---project

# Core techniques
python3 scripts/ai/agents/base/auto_cot_agent.py
python3 scripts/ai/agents/base/chain_of_verification.py
python3 scripts/ai/agents/base/tree_of_thoughts.py
python3 scripts/ai/agents/base/self_consistency.py

# Search optimization
python3 scripts/ai/agents/base/search_optimization_techniques.py
```

---

**Last Updated:** 2025-11-11
**Maintainer:** AI Agents Team
**Status:** Production-ready for all project areas
