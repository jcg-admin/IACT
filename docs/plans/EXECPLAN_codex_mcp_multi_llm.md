# Integrar orquestación Codex MCP para todos los LLM soportados

Este ExecPlan es una living document. Las secciones `Progress`, `Surprises & Discoveries`, `Decision Log` y `Outcomes & Retrospective` deben mantenerse al día conforme avancemos.

Se mantiene conforme a `.agent/PLANS.md`; cualquier desviación requiere actualizar la guía central.

## Purpose / Big Picture

Brindar al proyecto una guía y componentes reutilizables para ejecutar flujos multi-agente basados en Codex MCP que funcionen con los tres proveedores LLM vigentes (Claude/Anthropic, ChatGPT/OpenAI y modelos locales Hugging Face). El resultado esperado es que un colaborador pueda generar especificaciones, ejecutar agentes y observar sus trazas sin depender de ejemplos aislados para un solo proveedor.

## Progress

- [x] (2025-11-09 12:00Z) ExecPlan creado con propósito y orientación inicial.
- [x] (2025-11-09 14:05Z) Documentación actualizada describiendo flujos Codex MCP multi-LLM y su relación con `.agent`.
- [x] (2025-11-09 14:20Z) Builder de orquestación implementado con soporte para proveedores Anthropic, OpenAI y HuggingFace.
- [x] (2025-11-09 14:22Z) Tests de unidad cubriendo generación de flujos single-agent y multi-agent para cada proveedor.
- [x] (2025-11-09 14:30Z) Secciones de documentación y catálogo de agentes enlazan el nuevo módulo.
- [x] (2025-11-09 14:40Z) Validación manual del builder y actualización del retrospect.

## Surprises & Discoveries

- Observación: Hugging Face no requiere token obligatorio para ejecutar checkpoints locales, pero el builder devuelve la clave como opcional para mantener consistencia con los proveedores remotos.
  Evidencia: Decisión codificada en `_SUPPORTED_PROVIDERS` (`required=False`).

## Decision Log

- Decision: Registrar el ExecPlan bajo `docs/plans/EXECPLAN_codex_mcp_multi_llm.md` para mantenerlo versionado junto a otras planeaciones.
  Rationale: El árbol `docs/plans/` centraliza los planes operativos referenciados desde documentos oficiales.
  Date/Author: 2025-11-09 / gpt-5-codex

## Outcomes & Retrospective

Los briefs generados cubren los tres proveedores y mantienen el gating documentado. Las pruebas unitarias confirman la presencia de políticas MCP y trazas; no se detectaron gaps adicionales. Se recomienda monitorizar posibles cambios de nombres de modelos por parte de los proveedores para mantener los defaults vigentes.

## Context and Orientation

El repositorio ya cuenta con:
- `scripts/coding/ai/generators/llm_generator.py`: agente generador de tests que abstrae proveedores Anthropics/OpenAI/HuggingFace/Ollama.
- `scripts/coding/ai/test_generation_orchestrator.py`: pipeline secuencial de agentes con arquitectura modular.
- Documentación reciente en `docs/ai_capabilities/prompting/` para uso de LLMs (DORA scripts, PHI3, etc.).
- El catálogo de agentes vive en `.agent/agents/` y la gobernanza de planes en `.agent/PLANS.md`.

Actualmente no existe una guía unificada para operar Codex MCP ni un componente reutilizable que configure flujos multi-agente según el proveedor. Los ejemplos brindados por el usuario deben adaptarse a un contexto sin dependencias externas que ejecuten redes en CI.

## Plan of Work

1. **Documentación**: Crear una guía en `docs/ai_capabilities/orchestration/` que explique cómo inicializar Codex MCP, componer agentes individuales y multi-agente, mapearlos a los tres proveedores soportados y registrar cómo habilitar trazas. Actualizar índices (`docs/ai_capabilities/prompting/README.md`, README principal) y el catálogo `.agent/agents/README.md`.
2. **Diseño del builder**: Implementar un módulo `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` con clases puramente declarativas que generen los diccionarios de configuración necesarios para single-agent y multi-agent. El builder deberá exponer metadatos para cada proveedor (p. ej., nombre del modelo por defecto, variables de entorno esperadas, banderas `approval-policy`).
3. **Interfaz con `.agent`**: Añadir una ficha de agente en `.agent/agents` que describa el nuevo orquestador y cómo interactúa con la guía documental y scripts.
4. **Pruebas**: Crear `scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py` que cubra los tres proveedores en escenarios single y multi-agent, validando que el builder aplica banderas MCP, referencias a modelos y gating de artefactos.
5. **Validaciones**: Ejecutar `pytest` sobre los tests recién creados y `docs/testing/test_documentation_alignment.py` para asegurar consistencia. Documentar hallazgos en `Surprises & Discoveries` y cerrar con `Outcomes & Retrospective`.

## Concrete Steps

1. Crear directorio `docs/ai_capabilities/orchestration/` si no existe y añadir guía `CODEX_MCP_MULTI_AGENT_GUIDE.md` basada en los lineamientos proporcionados, adaptándolos al contexto multi-proveedor.
2. Actualizar índices/documentación (`docs/ai_capabilities/prompting/README.md`, `README.md`, `.agent/agents/README.md`) para enlazar la nueva guía y el builder.
3. Escribir pruebas de TDD en `scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py` cubriendo:
    - Generación de configuración single-agent para cada proveedor.
    - Flujo multi-agent que comprueba gating y artefactos esperados.
    - Validación de errores cuando falta información crítica (por ejemplo, sin API key configurada para openai/anthropic).
4. Implementar `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` para satisfacer los tests, asegurando 100% de coverage en este módulo.
5. Ejecutar `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py` seguido de `pytest docs/testing/test_documentation_alignment.py`.
6. Actualizar secciones vivas del ExecPlan con hallazgos y retrospectiva.

## Validation and Acceptance

- Los tests unitarios creados para el builder deben pasar en los tres proveedores simulados.
- `pytest docs/testing/test_documentation_alignment.py` debe seguir pasando tras la actualización de documentación.
- La guía documental debe describir pasos reproducibles (config `.env`, inicialización MCP, construcción multi-agent) y referenciar el nuevo módulo.
- `.agent/agents/README.md` debe listar el nuevo orquestador con enlace a guía y script.

## Idempotence and Recovery

- Las modificaciones documentales son aditivas; re-ejecutar los pasos sobrescribe archivos con el mismo contenido si es necesario.
- Los tests pueden ejecutarse múltiples veces sin efectos secundarios.
- Si la generación de archivos falla, basta con repetir el paso correspondiente; no se introducen migraciones destructivas.

## Artifacts and Notes

- `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py` → 10 tests OK (proveedores openai/anthropic/huggingface).

## Interfaces and Dependencies

- Módulo nuevo: `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` expondrá funciones puras; no se realizarán llamadas de red.
- Dependencias: se mantiene compatibilidad con Python estándar y sin instalar `openai-agents`. El builder solo documenta parámetros a usar.
- Variables de entorno: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `HUGGINGFACEHUB_API_TOKEN` (opcional), `MCP_CLI_PATH` si se personaliza el comando.

