---
id: UC-SYS-004
tipo: caso_uso_sistema
relacionado: [ADR-052, RT-009, RT-010, RF-007, RF-008]
prioridad: alta
estado: propuesto
fecha: 2025-11-16
---

# UC-SYS-004: Metacognitive Agent Operations

## Descripción

Sistema ejecuta operaciones metacognitivas (Planning, Evaluation, Reflection) para permitir que agentes "piensen sobre su pensamiento" y mejoren sus estrategias basándose en experiencias pasadas.

## Actores

- **Sistema**: Metacognitive Agent (no humano)
- **Sistemas Externos**:
  - Memory Manager (episodic memory)
  - LLM Provider (GPT-4, Claude)
  - Quality Validator
  - Cost Tracker

## Precondiciones

- Agente tiene tarea asignada
- Memory Manager está disponible
- LLM Provider está disponible
- Cost budget no está excedido

## Flujo Principal

### 1. Planning Layer

```
1.1. Sistema recibe task del usuario
1.2. Sistema busca experiencia previa en episodic memory
     - Retrieve similar past tasks (semantic search)
     - Latency target: < 100ms (RT-009)
1.3. Sistema analiza contexto actual
     - User preferences, constraints, available tools
1.4. Sistema crea plan con:
     - Desired Result: ¿Cómo se verá el mundo al terminar?
     - Steps: Descomposición de la tarea
     - Success Criteria: Criterios medibles de éxito
1.5. SI experiencia previa existe:
     - Sistema ajusta plan basado en learnings previos
     - Aplica strategy adjustments de reflections pasadas
1.6. Sistema cachea plan (para future reuse)
     - Latency target: < 2s total (RT-009)
```

### 2. Execution Layer

```
2.1. Sistema ejecuta steps del plan secuencialmente
2.2. Para cada step:
     - Ejecuta acción
     - Registra resultado
     - Actualiza runtime state
2.3. Sistema recolecta evidencia de ejecución
```

### 3. Evaluation Layer

```
3.1. Sistema evalúa resultado final contra success criteria
     - Check cada criterio del plan
     - Latency target: < 500ms (RT-009)
3.2. Sistema calcula:
     - Success: ¿Se cumplieron todos los criterios?
     - Criteria Met: Lista de criterios cumplidos/fallidos
     - Errors: Errores detectados durante ejecución
     - Relevancy Score: ¿Qué tan relevante fue el resultado?
3.3. SI success == True:
     - Sistema marca task como completado
     - Almacena resultado en episodic memory
     - [Fin - Success Path]
3.4. SI success == False:
     - Sistema procede a Reflection Layer
```

### 4. Reflection Layer (TRUE METACOGNITION)

```
4.1. Sistema inicia reflection sobre fallo
     - Input: Plan original + Evaluation result
     - Latency target: < 3s (RT-009)

4.2. Sistema analiza ROOT CAUSE (no solo síntomas)
     - ¿POR QUÉ falló? (no solo QUÉ falló)
     - ¿Qué asumió mal?
     - ¿Qué estrategia usó que no funcionó?

4.3. Sistema identifica patterns
     - Busca en episodic memory: ¿Ha pasado esto antes?
     - Valida patterns estadísticamente (>= 3 occurrences) (RT-010)
     - Ejemplo: "Siempre que priorizo 'cheapest', usuario rechaza calidad <7"

4.4. Sistema decide strategy adjustments
     - Ajustes concretos y ejecutables (RT-010 actionability >= 0.8)
     - Ejemplo: "Cambiar de 'cheapest' a 'highest_quality'"
     - Ejemplo: "Agregar constraint: quality >= 7"

4.5. Sistema formula learning
     - ¿Qué se aprendió?
     - ¿Cómo aplicarlo en el futuro?

4.6. Sistema valida quality de reflection (RT-010)
     - Quality score >= 0.8 requerido
     - Depth score >= 0.7 (root cause analysis)
     - Actionability >= 0.8 (concrete adjustments)

4.7. SI quality_score < 0.5:
     - [Alternate: Quality Rejection Loop]
4.8. SI quality_score >= 0.5:
     - Sistema almacena reflection en episodic memory
     - Memory type: EPISODIC
     - TTL: 90 días
     - Metadata: {plan_id, evaluation, patterns, adjustments}

4.9. Sistema aplica strategy adjustments inmediatamente
     - Actualiza agent configuration
     - Ejemplo: agent.config["hotel_search"]["priority"] = "quality"

4.10. Sistema retorna a Planning Layer (retry task con nueva estrategia)
      - [Loop: Volver a paso 1.1 con estrategia ajustada]
```

## Flujos Alternativos

### Alternate 1: Plan Cache Hit

```
1A.1. Durante Planning Layer, sistema busca en plan cache
1A.2. SI existe plan similar (similarity >= 0.85):
      - Sistema reutiliza cached plan (con ajustes mínimos)
      - Latency reducida: < 500ms (vs 2s)
      - Cost reducido: $0 (no LLM call)
      - [Resume: Execution Layer 2.1]
```

### Alternate 2: Quality Rejection Loop

```
4A.1. Reflection generada tiene quality_score < 0.5
4A.2. Sistema identifica violations:
      - Insufficient depth (no root cause)
      - Not actionable (vague adjustments)
      - Invalid patterns (< 3 occurrences)
4A.3. Sistema re-genera reflection con enhanced prompt
      - Attempt 2: Prompt incluye quality guidance
      - Attempt 3: Prompt más específico
4A.4. MAX_ITERATIONS = 3 (RT-010)
4A.5. SI quality mejora a >= 0.5:
      - [Resume: Paso 4.8 - Store reflection]
4A.6. SI después de 3 attempts, quality < 0.5:
      - Sistema rechaza reflection
      - Log warning
      - NO almacena en memory (low quality)
      - [Resume: Execution termina sin learning]
```

### Alternate 3: Cost Budget Exceeded

```
3A.1. Durante Planning o Reflection Layer
3A.2. Sistema verifica cost budget (RT-009)
3A.3. SI daily_cost + estimated_cost > daily_budget:
      - Sistema lanza MetacognitionCostExceeded
      - [Alternate: Degradation Strategy]
```

### Alternate 4: Degradation Strategy

```
4D.1. Sistema detecta repeated latency violations o cost exceeded
4D.2. Sistema ajusta degradation level:
      - Level 0 (full): Planning + Evaluation + Reflection
      - Level 1 (reduced): Planning + Evaluation (skip Reflection)
      - Level 2 (minimal): Planning only
      - Level 3 (disabled): No metacognition
4D.3. Sistema opera con degraded mode
4D.4. Sistema monitorea conditions
4D.5. SI conditions mejoran (latency normal, budget OK):
      - Sistema restaura a level superior
      - [Resume: Normal operations]
```

### Alternate 5: Timeout During Reflection

```
5A.1. Reflection Layer excede hard timeout (10s)
5A.2. Sistema aborta reflection generation
5A.3. Sistema lanza MetacognitionTimeoutError
5A.4. Sistema log error + metrics
5A.5. NO almacena partial reflection (incomplete)
5A.6. [End: Task fails, no learning stored]
```

### Alternate 6: Corrective RAG

```
6A.1. Durante Execution Layer, tool retorna resultado
6A.2. Sistema evalúa relevance de resultado (Evaluation Layer)
6A.3. SI relevance_score < threshold (0.5):
      - Sistema identifica: "Resultado no relevante"
      - [Corrective RAG Loop Start]
6A.4. Sistema analiza WHY resultado no es relevante
      - Query mal formada?
      - Knowledge base incompleta?
6A.5. Sistema refina query o knowledge
      - Reformulate query con más contexto
      - O: Fetch additional knowledge sources
6A.6. Sistema retry retrieval con query refinada
6A.7. Sistema re-evalúa relevance
6A.8. SI relevance_score >= threshold:
      - [Resume: Execution continúa]
6A.9. SI después de 3 iterations, relevance < threshold:
      - Sistema procede a Reflection Layer (analizar por qué RAG falla)
      - [Resume: Paso 4.1]
```

### Alternate 7: LLM Re-ranking

```
7A.1. Tool retorna múltiples resultados (ej: search results)
7A.2. Sistema evalúa initial ranking
7A.3. SI ranking parece suboptimal:
      - Sistema usa LLM para re-ranking
      - LLM analiza relevance de cada resultado al task
      - Latency target: < 800ms (RT-009)
7A.4. Sistema reordena results por LLM scores
7A.5. Sistema retorna top-K re-ranked results
      - [Resume: Execution continúa con mejores results]
```

## Postcondiciones

### Éxito

- Plan creado y ejecutado
- Evaluation completada
- SI fallo: Reflection almacenada en episodic memory
- Strategy adjustments aplicados
- Future tasks se benefician de learnings

### Fallo

- Timeout durante metacognition
- Cost budget excedido
- Quality validation falló después de MAX_ITERATIONS
- NO learning almacenado (degradation a non-metacognitive mode)

## Requisitos No Funcionales

- **Performance**: Cumplir latency targets (RT-009)
  - Planning: < 2s
  - Evaluation: < 500ms
  - Reflection: < 3s
- **Quality**: Reflections con quality_score >= 0.8 (RT-010)
- **Cost**: Respetar cost budgets (RT-009)
  - < $0.02 per reflection
  - < $5 daily per user
- **Storage**: Episodic memories dentro de quota (RT-006)
  - Max 5,000 episodic memories per user
- **Reliability**: Success rate > 95% para reflection generation

## Flujo Completo - Ejemplo Real

### Escenario: Travel Agent - Hotel Booking

```
1. PLANNING LAYER
   - User task: "Book hotel in Paris"
   - Sistema retrieve past experience: "User rejected Hotel A (cheap, quality=6)"
   - Sistema identify pattern from memory: "User prefers quality > price"
   - Sistema crea plan:
     * Desired Result: Hotel booked, quality >= 7, near Eiffel Tower
     * Steps: [Search hotels, Filter quality>=7, Sort by reviews, Select top]
     * Success Criteria: [Quality >= 7, User confirms, Within budget]
   - Sistema ajusta strategy basado en past reflection:
     * Apply: "Priority = quality (not price)"

2. EXECUTION LAYER
   - Sistema ejecuta search_hotels(location="Paris")
   - Sistema filter results: quality >= 7
   - Sistema sort by reviews (descending)
   - Sistema select top result: Hotel B (quality=8, price=$150)
   - Sistema presenta a user: "Hotel B recommended"

3. EVALUATION LAYER
   - Sistema check success criteria:
     * Quality >= 7? ✓ (quality=8)
     * User confirms? ✓ (user says "yes")
     * Within budget? ✓ ($150 < $200)
   - Success = True
   - Sistema almacena resultado en episodic memory:
     * "Task: Book hotel Paris - SUCCESS"
     * "Strategy: quality-first worked (user confirmed)"
     * "Result: Hotel B (quality=8)"
   - [End - Success]

4. REFLECTION LAYER (solo si fallo)
   - Not executed (success en este caso)
```

### Escenario: Travel Agent - Hotel Booking (Failure)

```
1. PLANNING LAYER (mismo que arriba, pero SIN past learnings)
   - Sistema crea plan sin learnings:
     * Strategy: "Priority = price (cheapest)"

2. EXECUTION LAYER
   - Sistema ejecuta search_hotels(location="Paris")
   - Sistema sort by price (ascending)
   - Sistema select cheapest: Hotel C (quality=5, price=$80)
   - Sistema presenta: "Hotel C recommended (best price!)"

3. EVALUATION LAYER
   - User feedback: "No, quality too low"
   - Sistema check success criteria:
     * Quality >= 7? ✗ (quality=5)
     * User confirms? ✗ (user rejected)
   - Success = False
   - Sistema procede a REFLECTION

4. REFLECTION LAYER
   4.1. Analyze ROOT CAUSE:
        Analysis = """
        I prioritized cheapest price, which led to selecting quality=5 hotel.
        User feedback indicates quality is more important than price.
        My 'budget-first' strategy is flawed for this user.
        """
        Depth score = 0.8 (identifies strategy flaw) ✓

   4.2. Identify PATTERNS:
        - Search episodic memory: "hotel rejection" queries
        - Found 3 past rejections: all quality < 7
        Pattern = "Whenever I prioritize 'cheapest', user rejects quality <7"
        Pattern validity = 3/3 = 1.0 (100% confidence) ✓

   4.3. Decide STRATEGY ADJUSTMENTS:
        Adjustments = [
          "Change priority from 'price' to 'quality'",
          "Add constraint: quality >= 7 in search",
          "Sort by quality*reviews, not price"
        ]
        Actionability score = 1.0 (all concrete, executable) ✓

   4.4. Formulate LEARNING:
        Learning = """
        For this user, quality > price.
        Future hotel searches: quality >= 7, then optimize price.
        This prevents repeated low-quality selections.
        """

   4.5. Validate QUALITY:
        - Completeness: 4/4 fields ✓
        - Depth: 0.8 ✓
        - Actionability: 1.0 ✓
        - Quality Score: 0.9 ✓

   4.6. Store REFLECTION in episodic memory:
        Memory {
          type: EPISODIC,
          content: "Hotel booking failed - learned: quality > price",
          metadata: {
            plan_id: "plan_123",
            evaluation: {...},
            patterns: ["cheapest → rejected"],
            adjustments: ["priority=quality", "constraint: quality>=7"]
          },
          ttl: 90 days
        }

   4.7. Apply ADJUSTMENTS immediately:
        agent.config["hotel_search"]["priority"] = "quality"
        agent.config["hotel_search"]["min_quality"] = 7

   4.8. RETRY task con nueva estrategia:
        [Loop back to Planning Layer con adjusted strategy]

5. PLANNING LAYER (Retry)
   - Sistema retrieve reflection: "quality > price"
   - Sistema crea plan con adjusted strategy:
     * Priority = quality (not price)
     * Constraint: quality >= 7

6. EXECUTION LAYER (Retry)
   - Sistema ejecuta con new strategy
   - Sistema filter quality >= 7
   - Sistema sort by quality
   - Sistema select: Hotel B (quality=8, price=$150)

7. EVALUATION LAYER (Retry)
   - User: "Yes, perfect!"
   - Success = True ✓
   - [End - Success after learning]
```

## Métricas

```python
METACOGNITION_METRICS = {
    "planning_latency_p95_ms": 2000,
    "evaluation_latency_p95_ms": 500,
    "reflection_latency_p95_ms": 3000,

    "reflection_quality_score_avg": 0.8,
    "reflection_acceptance_rate": 0.95,

    "plan_cache_hit_rate": 0.4,
    "pattern_validity_avg": 0.75,

    "cost_per_reflection_usd": 0.02,
    "daily_cost_per_user_usd": 5.0,

    "success_after_reflection_rate": 0.85,  # Tasks succeed after applying learnings
    "metacognition_improvement_rate": 0.70,  # % of reflections that improve future performance
}
```

## Diagramas

### Secuencia Completa

```
User          Agent         PlanningLayer    ExecutionLayer   EvaluationLayer   ReflectionLayer   Memory
 |              |                 |                 |                 |                  |             |
 |--task------->|                 |                 |                 |                  |             |
 |              |--retrieve-------|---------------->|---------------->|----------------->|------------>|
 |              |<-experience-----|                 |                 |                  |<------------|
 |              |--create_plan--->|                 |                 |                  |             |
 |              |<--plan----------|                 |                 |                  |             |
 |              |--execute--------|---------------->|                 |                  |             |
 |              |<--result--------|<----------------|                 |                  |             |
 |              |--evaluate-------|---------------->|---------------->|                  |             |
 |              |<--evaluation----|                 |<----------------|                  |             |
 |              |                 |                 |                 |                  |             |
 |              | IF success == False:              |                 |                  |             |
 |              |--reflect--------|---------------->|---------------->|----------------->|             |
 |              |                 |                 |                 |<-----------------|             |
 |              |                 |                 |                 |--validate------->|             |
 |              |                 |                 |                 |<--quality--------|             |
 |              |                 |                 |                 |--store-----------|------------>|
 |              |                 |                 |                 |                  |<------------|
 |              |<--reflection----|<----------------|<----------------|<-----------------|             |
 |              |--apply_adjust-->|                 |                 |                  |             |
 |              |--retry--------->|                 |                 |                  |             |
 |              |                 |                 |                 |                  |             |
```

## Referencias

- ADR-052: Metacognition Architecture for AI Agents
- RT-009: Metacognition Performance Constraints
- RT-010: Reflection Quality Standards
- ADR-048: AI Agent Memory Architecture (episodic memory storage)

---

**Caso de Uso**: Sistema ejecuta ciclo metacognitivo completo (Plan → Execute → Evaluate → Reflect) para self-improvement.
**Objetivo**: Agentes aprenden de experiencias y mejoran estrategias automáticamente.
