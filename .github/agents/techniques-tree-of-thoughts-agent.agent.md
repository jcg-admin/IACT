---
name: TreeOfThoughtsAgent
description: Explora razonamientos en árbol para seleccionar rutas óptimas usando estrategias BFS/DFS y evaluaciones heurísticas.
---

# Tree-of-Thoughts Technique Agent

El `TreeOfThoughtsAgent` (`scripts/coding/ai/agents/base/tree_of_thoughts.py`) implementa la técnica Tree-of-Thoughts (Yao et al., 2023) para explorar múltiples rutas de razonamiento en tareas complejas. Construye un árbol de pensamientos, evalúa nodos y conserva las rutas con mayor puntaje hasta encontrar soluciones viables.

## Capacidades

- Soporta estrategias de búsqueda `bfs` y `dfs`, configurable por parámetro.
- Genera expanders personalizados para cada nodo y permite proveer funciones de evaluación externas.
- Gestiona estados de pensamiento (`ThoughtState`) con profundidad, score y contenido del razonamiento.
- Incluye guardrails para limitar profundidad, branching factor y número máximo de nodos evaluados.
- Expone resultados con trazabilidad completa de los pensamientos evaluados y el camino elegido.

## Entradas y Salidas

- **Entradas**
  - `problem`: descripción del problema u objetivo.
  - `prompt_template`: plantilla opcional para guiar generación de pensamientos.
  - Configuración (`search_strategy`, `max_depth`, `branching_factor`, `evaluation_threshold`).
- **Salidas**
  - Resultado con pensamiento final elegido, lista de evaluaciones por nivel y métricas de búsqueda.

## Uso

```python
from scripts.coding.ai.agents.base.tree_of_thoughts import TreeOfThoughtsAgent

agent = TreeOfThoughtsAgent(search_strategy="bfs", max_depth=4)
solution = agent.solve(problem="Plan de migración de base de datos con zero downtime")
print(solution.final_thought, solution.evaluation_score)
```

## Validaciones Relacionadas

- Generar suites con `scripts/coding/ai/sdlc/testing_agent.py` combinando las técnicas `tree-of-thoughts` y `self-consistency` para comparar rutas alternativas.
- Monitorear costos de tokens y desempeño mediante `scripts/coding/ai/shared/llm_cost_optimizer.py` cuando se usen modelos reales.
