# Context Management Playbook

Esta guía describe cómo gestionar memoria de contexto en agentes largos utilizando las sesiones `TrimmingSession` y `SummarizingSession` incluidas en `scripts/coding/ai/shared/context_sessions.py`. El objetivo es ofrecer una estrategia uniforme para Claude (Anthropic), ChatGPT (OpenAI) y los modelos operados desde Hugging Face, asegurando coherencia, costos predecibles y trazas auditables en cualquier dominio (`api/`, `ui/`, `infrastructure/`, `docs/`, `scripts/`).

## 1. Por qué importa el contexto

- **Coherencia sostenida**: los agentes mantienen el objetivo actual sin reciclar historiales desactualizados.
- **Precisión en llamadas a herramientas**: un contexto curado reduce reintentos, tiempos de espera y errores de parámetros.
- **Latencia y costos controlados**: menos tokens por turno implican tiempos de respuesta y facturación estables.
- **Mitigación de alucinaciones**: los resúmenes sirven como “cuartos limpios” que corrigen hechos dudosos antes de seguir iterando.
- **Observabilidad**: historiales acotados facilitan diffs de sesiones, reproducen fallos y habilitan evaluaciones comparables.

## 2. Relación con los agentes del repositorio

- `ClaudeAgent`, `ChatGPTAgent` y `HuggingFaceAgent` (en `.agent/agents/`) referencian este playbook como política oficial de memoria.
- Los agentes de dominio (`ApiAgent`, `UiAgent`, `InfrastructureAgent`, `DocsAgent`, `ScriptsAgent`) delegan en estas sesiones cuando ejecutan planes desde sus ExecPlans.
- `CodexMCPWorkflowBuilder` puede envolver cualquiera de las sesiones para mantener threads extensos generados por Codex MCP.

## 3. Preparativos y dependencias

1. Configura las claves descritas en `docs/ai/CONFIGURACION_API_KEYS.md` para el proveedor que vayas a usar.
2. Instala el SDK correspondiente:
   ```bash
   pip install openai-agents openai
   ```
3. Opcional: registra claves adicionales (`ANTHROPIC_API_KEY`, `HUGGINGFACEHUB_API_TOKEN`) si alternas entre proveedores.
4. Estructura tu `.env` siguiendo `docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md` si ejecutas agentes MCP.

## 4. Sesiones con recorte (`TrimmingSession`)

`TrimmingSession` conserva únicamente los últimos *N* turnos reales del usuario (un turno = mensaje del usuario + respuestas y herramientas hasta el siguiente usuario). Se recomienda para flujos operativos donde cada paso es independiente.

```python
from scripts.coding.ai.shared.context_sessions import TrimmingSession

session = TrimmingSession("customer-support", max_turns=3)
await session.add_items([
    {"role": "user", "content": "Primer problema"},
    {"role": "assistant", "content": "Respuesta"},
])
# ...
recent_items = await session.get_items()
```

**Ventajas**
- Determinismo total: sin resúmenes ni llamadas adicionales.
- Sin latencia extra: no se invocan modelos adicionales para resumir.
- Ideal para automatizaciones de soporte, CRM o scripts internos de infraestructura.

**Limitaciones**
- Olvida de forma abrupta cualquier restricción o identificador anterior a *N* turnos.
- Historiales recientes muy extensos (por ejemplo, respuestas de herramientas pesadas) aún pueden saturar la ventana.

## 5. Sesiones con resumen (`SummarizingSession`)

`SummarizingSession` mantiene verbatim los últimos turnos y comprime el resto en un bloque sintético usuario→assistant. El resumen se realiza mediante un componente asíncrono que puedes implementar con cualquier modelo compatible.

```python
from scripts.coding.ai.shared.context_sessions import SummarizingSession

class SupportSummarizer:
    async def summarize(self, messages):
        shadow_prompt = "Summarize the conversation we had so far."
        summary_text = "\n".join(
            f"- {msg['role']}: {msg['content']}" for msg in messages
        )
        return shadow_prompt, summary_text

session = SummarizingSession(
    keep_last_n_turns=2,
    context_limit=4,
    summarizer=SupportSummarizer(),
    session_id="enterprise-case-001",
)
await session.add_items([...])
current_context = await session.get_items()
```

**Ventajas**
- Conserva decisiones, identificadores y restricciones más allá de *N* turnos.
- Experiencia fluida para el usuario: el agente “recuerda” acuerdos previos.
- Costos predecibles en sesiones prolongadas (el resumen reemplaza cientos de mensajes).

**Limitaciones**
- Riesgo de “resumen sesgado” si el modelo omite detalles críticos.
- Incremento de latencia/costos cuando se recalcula el resumen.
- Se debe auditar la salida para evitar “context poisoning”.

### 5.1 Sugerencias para prompts de resumen

- Resalta hitos (problema reportado, solución probada, estado actual).
- Integra comprobaciones de contradicciones o políticas antes de resumir.
- Incluye secciones bien delimitadas (`Product & Environment`, `Steps Tried`, `Blockers`, etc.).
- Marca datos dudosos como `UNVERIFIED` para no promover su uso automático.

## 6. Comparativa rápida

| Dimensión | TrimmingSession | SummarizingSession |
|-----------|-----------------|--------------------|
| Latencia/costo | Muy bajo | Moderado (dependiendo del resumen) |
| Memoria a largo plazo | Baja | Alta |
| Riesgo principal | Pérdida de contexto | Distorsión del contexto |
| Escenarios ideales | Automatizaciones cortas, tareas independientes | Casos analíticos, coaching, soporte premium |

## 7. Observabilidad y registros

- `SummarizingSession.get_full_history()` entrega mensajes y metadatos (`synthetic`, `kind`, `summary_for_turns`) útiles para trazas y dashboards.
- Registra las salidas de los resúmenes para auditar cambios en evaluaciones.
- Al integrar con `agents` SDK, complementa con `set_tracing_disabled(False)` para utilizar los tableros de Traces cuando estén habilitados.

## 8. Evaluaciones recomendadas

1. **Baseline vs. Delta**: ejecuta tus suites de regresión antes y después de aplicar la política de contexto.
2. **LLM-as-Judge**: evalúa resúmenes con un prompt que compare contra la conversación original.
3. **Replay de transcripciones**: reproduce threads largos y valida si el agente recuerda IDs, acuerdos o restricciones.
4. **Token Pressure Checks**: monitorea la longitud total enviada al modelo para evitar truncamientos inesperados.

## 9. Integración por dominio

- **Backend (`api/`)**: utilice sesiones para pipelines de soporte o diagnósticos de microservicios.
- **Frontend (`ui/`)**: combine resúmenes con análisis de UX para guiar mejoras graduales.
- **Infrastructure**: aplica trimming para runbooks automatizados y summarization en incidentes largos.
- **Docs**: usa resúmenes para consolidar hallazgos antes de archivarlos en `docs/analisis/`.
- **Scripts**: `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` puede recibir una sesión vía composición para mantener el estado cuando delega en múltiples agentes.

## 10. Recursos relacionados

- Implementación de referencia: `scripts/coding/ai/shared/context_sessions.py`.
- Pruebas de TDD: `scripts/coding/tests/ai/shared/test_context_sessions.py`.
- ExecPlan que gobierna esta guía: `docs/plans/EXECPLAN_context_memory_management.md`.
- Plantillas de agentes: `.agent/agents/`.
- Prueba de alineación documental: `docs/testing/test_documentation_alignment.py`.
