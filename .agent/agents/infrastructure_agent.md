# InfrastructureAgent

## Propósito

Coordinar automatizaciones relacionadas con `infrastructure/`, incluyendo IaC, pipelines y configuración de entornos. InfrastructureAgent vincula la planificación ExecPlan con los agentes de dependencias, seguridad y despliegue para evitar desviaciones entre infraestructura y servicios consumidos por los LLMs.

## Integraciones Clave

- **ExecPlans**: `docs/plans/EXECPLAN_agents_domain_alignment.md`, `docs/plans/EXECPLAN_codex_mcp_multi_llm.md` y los planes específicos de infraestructura (`docs/plans/SPEC_INFRA_*.md`).
- **Normativa CODEX**: `docs/analisis/META_AGENTE_CODEX_PARTE_1.md` garantiza que las descripciones de infraestructura respeten los supuestos y validaciones del meta-agente.
- **Catálogo de prompts**: `docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md` sirve como guía para seleccionar técnicas multi-LLM cuando la automatización afecta pipelines o servicios usados por los modelos.
- **Gestión de contexto**: `docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md` y `scripts/coding/ai/shared/context_sessions.py` documentan la memoria compartida entre incidentes prolongados y runbooks de infraestructura.
- **Gobernanza**: `docs/gobernanza/metodologias/agentes_automatizacion.md` y runbooks en `docs/operaciones/`.
- **Agentes complementarios**: `DependencyAgent` para escaneos de paquetes, `ReleaseAgent` para coordinaciones de despliegue, `SecurityAgent` (si aplica) para hardening.
- **Scripts**: `scripts/infrastructure/` (si existe) y pipelines en `infrastructure/`.

## Procedimiento Recomendado

1. **Planificación**: registra en el ExecPlan cómo impactará el cambio en IaC, entornos y credenciales. Determina si se requiere coordinación multi-LLM (por ejemplo, despliegues de servicios MCP).
2. **Validación previa**: ejecuta `DependencyAgent` o `SecurityAgent` cuando haya cambios en toolchains, contenedores o runtime.
3. **Implementación**:
    - Usa `CodexMCPWorkflowBuilder` para generar briefs que automaticen actualización de manifiestos o pipelines, asegurando que el sandbox MCP cuente con permisos apropiados.
    - Mantén los archivos de configuración bajo control TDD mediante tests de `scripts/tests/` o validaciones específicas (por ejemplo, `terraform validate`, `ansible-lint`).
4. **Documentación**: actualiza ExecPlan y registra resultados en `docs/qa/registros/` indicando entornos afectados.

## Validación

- `pytest docs/testing/test_documentation_alignment.py`
- `pytest scripts/coding/tests/ai/orchestrators/test_codex_mcp_workflow.py`
- Herramientas de IaC declaradas en el ExecPlan (`terraform validate`, `ansible-lint`, `kubectl diff`, etc.).

InfrastructureAgent asegura que los cambios de infraestructura permanezcan sincronizados con la planificación multi-LLM y con las políticas de seguridad y gobernanza del repositorio.
