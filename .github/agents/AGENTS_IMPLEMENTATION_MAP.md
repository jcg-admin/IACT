# Mapeo de Implementación de Agentes

Este documento mapea todos los agentes del proyecto a su implementación en código.

## Agentes Implementados (Python)

### SDLC Agents

| Agente | Implementación | Tests | Estado TDD |
|--------|---------------|-------|------------|
| SDLCPlannerAgent | `scripts/coding/ai/sdlc/planner_agent.py` | `scripts/coding/ai/tests/test_sdlc_planner_agent.py` | Parcial |
| SDLCFeasibilityAgent | `scripts/coding/ai/sdlc/feasibility_agent.py` | `scripts/coding/ai/tests/test_sdlc_feasibility_agent.py` | Parcial |
| SDLCDesignAgent | `scripts/coding/ai/sdlc/design_agent.py` | `scripts/coding/ai/tests/test_sdlc_design_agent.py` | Parcial |
| SDLCTestingAgent | `scripts/coding/ai/sdlc/testing_agent.py` | `scripts/coding/ai/tests/test_sdlc_testing_agent.py` | Completo |
| SDLCDeploymentAgent | `scripts/coding/ai/sdlc/deployment_agent.py` | `scripts/coding/ai/tests/test_sdlc_deployment_agent.py` | Parcial |
| SDLCOrchestratorAgent | `scripts/coding/ai/sdlc/orchestrator.py` | - | Pendiente |
| DORATrackedSDLCAgent | `scripts/coding/ai/sdlc/dora_integration.py` | - | Pendiente |
| SDLCAgent (Base) | `scripts/coding/ai/sdlc/base_agent.py` | - | - |

### Automation Agents

| Agente | Implementación | Tests | Estado TDD |
|--------|---------------|-------|------------|
| CoherenceAnalyzerAgent | `scripts/coding/ai/automation/coherence_analyzer_agent.py` | `scripts/coding/ai/tests/test_coherence_analyzer_agent.py` | Completo |
| PDCAAutomationAgent | `scripts/coding/ai/automation/pdca_agent.py` | `scripts/coding/ai/tests/test_pdca_agent.py` | Completo |
| ConstitutionValidatorAgent | `scripts/coding/ai/automation/constitution_validator_agent.py` | `scripts/coding/ai/tests/test_constitution_validator_agent.py` | Completo |
| DevContainerValidatorAgent | `scripts/coding/ai/automation/devcontainer_validator_agent.py` | `scripts/coding/ai/tests/test_devcontainer_validator_agent.py` | Completo |
| MetricsCollectorAgent | `scripts/coding/ai/automation/metrics_collector_agent.py` | `scripts/coding/ai/tests/test_metrics_collector_agent.py` | Completo |
| SchemaValidatorAgent | `scripts/coding/ai/automation/schema_validator_agent.py` | `scripts/coding/ai/tests/test_schema_validator_agent.py` | Completo |
| CIPipelineOrchestratorAgent | `scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py` | `scripts/coding/ai/tests/test_ci_pipeline_orchestrator_agent.py` | Completo |

### Prompting Techniques

| Técnica | Implementación | Tests | Estado TDD |
|---------|---------------|-------|------------|
| Auto-CoT | `scripts/coding/ai/agents/base/auto_cot_agent.py` | - | Pendiente |
| Chain of Verification | `scripts/coding/ai/agents/base/chain_of_verification.py` | - | Pendiente |
| Self-Consistency | `scripts/coding/ai/agents/base/self_consistency.py` | - | Pendiente |
| Tree of Thoughts | `scripts/coding/ai/agents/base/tree_of_thoughts.py` | - | Pendiente |
| Fundamental Techniques | `scripts/coding/ai/agents/base/fundamental_techniques.py` | - | Pendiente |
| Structuring Techniques | `scripts/coding/ai/agents/base/structuring_techniques.py` | - | Pendiente |
| Knowledge Techniques | `scripts/coding/ai/agents/base/knowledge_techniques.py` | - | Pendiente |
| Optimization Techniques | `scripts/coding/ai/agents/base/optimization_techniques.py` | - | Pendiente |
| Specialized Techniques | `scripts/coding/ai/agents/base/specialized_techniques.py` | - | Pendiente |
| Search Optimization | `scripts/coding/ai/agents/base/search_optimization_techniques.py` | - | Pendiente |
| Prompt Templates | `scripts/coding/ai/agents/base/prompt_templates.py` | - | Pendiente |

### Shared Components

| Componente | Implementación | Tests | Estado TDD |
|------------|---------------|-------|------------|
| Agent (Base Class) | `scripts/coding/ai/shared/agent_base.py` | - | Parcial |
| ContextSession | `scripts/coding/ai/shared/context_sessions.py` | - | Pendiente |

### Orchestration & Generation

| Componente | Implementación | Tests | Estado TDD |
|------------|---------------|-------|------------|
| CodexMCPWorkflow | `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` | - | Pendiente |
| BusinessAnalysisGenerator | `scripts/coding/ai/business_analysis/generator.py` | - | Pendiente |
| TemplateGenerator | `scripts/coding/ai/generators/template_generator.py` | - | Pendiente |
| TraceabilityMatrixGenerator | `scripts/coding/ai/generators/traceability_matrix_generator.py` | - | Pendiente |
| DocumentSplitter | `scripts/coding/ai/documentation/document_splitter.py` | - | Pendiente |
| LLMGenerator | `scripts/coding/ai/generators/llm_generator.py` | - | Pendiente |

### Documentation Sync Agents

| Agente | Implementación | Tests | Estado TDD |
|--------|----------------|-------|------------|
| CodeInspectorAgent | `scripts/coding/ai/documentation/sync_agent.py` | - | Pendiente |
| DocumentationEditorAgent | `scripts/coding/ai/documentation/sync_agent.py` | - | Pendiente |
| ConsistencyVerifierAgent | `scripts/coding/ai/documentation/sync_agent.py` | - | Pendiente |
| SyncReporterAgent | `scripts/coding/ai/documentation/sync_agent.py` | - | Pendiente |

### Quality Automation Agents

| Agente | Implementación | Tests | Estado TDD |
|--------|----------------|-------|------------|
| CompletenessValidator | `scripts/coding/ai/quality/completeness_validator.py` | - | Pendiente |
| CoverageAnalyzer | `scripts/coding/ai/quality/coverage_analyzer.py` | - | Pendiente |
| CoverageVerifier | `scripts/coding/ai/quality/coverage_validator.py` | - | Pendiente |
| SyntaxValidator | `scripts/coding/ai/quality/syntax_validator.py` | - | Pendiente |

### Shared Delivery Agents

| Agente | Implementación | Tests | Estado TDD |
|--------|----------------|-------|------------|
| TestRunner | `scripts/coding/ai/shared/test_runner.py` | - | Pendiente |
| PRCreator | `scripts/coding/ai/shared/pr_creator.py` | - | Pendiente |

### Permissions Gates

| Agente | Implementación | Tests | Estado TDD |
|--------|----------------|-------|------------|
| BasePermissionAgent | `scripts/coding/ai/agents/permissions/base.py` | - | Base |
| RouteLintAgent | `scripts/coding/ai/agents/permissions/route_linter.py` | - | Pendiente |

## Agentes Definidos (Markdown - No implementados en Python)

Estos agentes están definidos en markdown para uso con prompts, pero NO tienen implementación Python:

### DevOps Agents

| Agente | Definición | Implementación Python | Estado |
|--------|------------|----------------------|--------|
| GitOpsAgent | `.agent/agents/gitops_agent.md` | NO | Prompt-based |
| ReleaseAgent | `.agent/agents/release_agent.md` | NO | Prompt-based |
| DependencyAgent | `.agent/agents/dependency_agent.md` | NO | Prompt-based |
| SecurityAgent | `.agent/agents/security_agent.md` | NO | Prompt-based |
| CodeTasker | `.agent/agents/my_agent.md` | NO | Prompt-based |

### Domain Agents

| Agente | Definición | Implementación Python | Estado |
|--------|------------|----------------------|--------|
| ApiAgent | `.agent/agents/api_agent.md` | NO | Prompt-based |
| UiAgent | `.agent/agents/ui_agent.md` | NO | Prompt-based |
| InfrastructureAgent | `.agent/agents/infrastructure_agent.md` | NO | Prompt-based |
| DocsAgent | `.agent/agents/docs_agent.md` | NO | Prompt-based |
| ScriptsAgent | `.agent/agents/scripts_agent.md` | NO | Prompt-based |

### LLM Provider Agents

| Agente | Definición | Implementación Python | Estado |
|--------|------------|----------------------|--------|
| ClaudeAgent | `.agent/agents/claude_agent.md` | NO (usa LLMGenerator) | Prompt-based |
| ChatGPTAgent | `.agent/agents/chatgpt_agent.md` | NO (usa LLMGenerator) | Prompt-based |
| HuggingFaceAgent | `.agent/agents/huggingface_agent.md` | NO (usa LLMGenerator) | Prompt-based |

## Próximos Pasos para Implementación

### Prioridad Alta - TDD Pendiente

1. **Técnicas de Prompting Base**
   - Implementar tests para `auto_cot_agent.py`
   - Implementar tests para `self_consistency.py`
   - Implementar tests para `chain_of_verification.py`
   - Implementar tests para `tree_of_thoughts.py`

2. **Agentes de Dominio (si se requiere implementación Python)**
   - Decidir si ApiAgent/UiAgent necesitan implementación Python
   - Si SÍ: Crear `scripts/coding/ai/domain/api_agent.py` con TDD
   - Si SÍ: Crear `scripts/coding/ai/domain/ui_agent.py` con TDD

3. **Componentes Shared**
   - Implementar tests para `context_sessions.py`
   - Implementar tests para `agent_base.py` (completar)

4. **Orchestration**
   - Implementar tests para `codex_mcp_workflow.py`
   - Implementar tests para `llm_generator.py`

### Prioridad Media - Mejoras TDD

1. **SDLC Agents** - Completar TDD:
   - SDLCPlannerAgent (de Parcial a Completo)
   - SDLCFeasibilityAgent (de Parcial a Completo)
   - SDLCDesignAgent (de Parcial a Completo)
   - SDLCDeploymentAgent (de Parcial a Completo)

### Prioridad Baja - Opcionales

1. **DevOps Agents** - Implementar en Python (opcional):
   - Si se requiere automatización: Implementar GitOpsAgent.py
   - Si se requiere automatización: Implementar ReleaseAgent.py
   - Si se requiere automatización: Implementar DependencyAgent.py
   - Si se requiere automatización: Implementar SecurityAgent.py

## Comandos para Generar TDD

### Usar SDLCTestingAgent para generar tests

```bash
# Para técnicas de prompting
python scripts/coding/ai/sdlc/testing_agent.py \
  --project-root . \
  --target-module "scripts/coding/ai/agents/base/auto_cot_agent.py" \
  --output-dir "scripts/coding/ai/tests" \
  --coverage-target 80 \
  --use-technique auto-cot

# Para agentes de dominio (si se implementan)
python scripts/coding/ai/sdlc/testing_agent.py \
  --project-root . \
  --target-module "scripts/coding/ai/domain/api_agent.py" \
  --output-dir "scripts/coding/ai/tests" \
  --coverage-target 80 \
  --use-technique self-consistency
```

### Ejecutar en Paralelo

```bash
# Generar tests para múltiples agentes en paralelo
python -c "
from scripts.coding.ai.orchestrators.codex_mcp_workflow import CodexMCPWorkflowBuilder

workflow = CodexMCPWorkflowBuilder()

# Test generation para Auto-CoT
workflow.add_agent(
    name='AutoCoTTestGen',
    agent_class='SDLCTestingAgent',
    inputs={'module': 'scripts/coding/ai/agents/base/auto_cot_agent.py'},
    technique='auto-cot',
    parallel=True
)

# Test generation para Self-Consistency
workflow.add_agent(
    name='SelfConsistencyTestGen',
    agent_class='SDLCTestingAgent',
    inputs={'module': 'scripts/coding/ai/agents/base/self_consistency.py'},
    technique='self-consistency',
    parallel=True
)

# Test generation para ApiAgent (si existe)
workflow.add_agent(
    name='ApiAgentTestGen',
    agent_class='SDLCTestingAgent',
    inputs={'module': 'scripts/coding/ai/domain/api_agent.py'},
    technique='auto-cot',
    parallel=True
)

# Test generation para UiAgent (si existe)
workflow.add_agent(
    name='UiAgentTestGen',
    agent_class='SDLCTestingAgent',
    inputs={'module': 'scripts/coding/ai/domain/ui_agent.py'},
    technique='self-consistency',
    parallel=True
)

results = workflow.execute_parallel()
print(results)
"
```

## Resumen de Estado

- **Agentes con TDD Completo**: 8/20 (40%)
- **Agentes con TDD Parcial**: 5/20 (25%)
- **Agentes sin TDD**: 7/20 (35%)
- **Agentes prompt-based (no requieren TDD Python)**: 13

---

**Última actualización**: 2025-11-14
**Prioridad**: Completar TDD para técnicas de prompting y componentes shared
