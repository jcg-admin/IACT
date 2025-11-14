# Agentes y Técnicas de Prompting - Proyecto IACT

Este directorio contiene la documentación consolidada de todos los agentes y técnicas de prompting utilizadas en el proyecto IACT.

## Índice

- [Agentes SDLC](#agentes-sdlc)
- [Agentes de Automatización](#agentes-de-automatización)
- [Agentes DevOps](#agentes-devops)
- [Agentes por Proveedor LLM](#agentes-por-proveedor-llm)
- [Agentes por Dominio](#agentes-por-dominio)
- [Técnicas de Prompting](#técnicas-de-prompting)
- [Mapeo de Agentes a Código](#mapeo-de-agentes-a-código)

## Resumen Ejecutivo

**Total de agentes**: 30+
**Técnicas de prompting documentadas**: 120+
**Técnicas activamente implementadas**: 20+
**Ubicaciones de código**:
- `scripts/coding/ai/sdlc/` - Agentes SDLC
- `scripts/coding/ai/automation/` - Agentes de automatización
- `scripts/coding/ai/agents/base/` - Técnicas de prompting
- `.agent/agents/` - Definiciones de agentes especializados

## Agentes SDLC

Los agentes SDLC gestionan el ciclo de vida del desarrollo de software.

**Documentación completa**: [sdlc/README.md](./sdlc/README.md)

| Agente | Propósito | Código |
|--------|-----------|--------|
| SDLCPlannerAgent | Planificación y estimación | `scripts/coding/ai/sdlc/planner_agent.py` |
| SDLCFeasibilityAgent | Análisis de viabilidad y riesgos | `scripts/coding/ai/sdlc/feasibility_agent.py` |
| SDLCDesignAgent | Generación de diseños HLD/LLD | `scripts/coding/ai/sdlc/design_agent.py` |
| SDLCTestingAgent | Generación automática de tests | `scripts/coding/ai/sdlc/testing_agent.py` |
| SDLCDeploymentAgent | Planificación de despliegues | `scripts/coding/ai/sdlc/deployment_agent.py` |

## Agentes de Automatización

Agentes que gestionan procesos CI/CD, validación y métricas.

**Documentación completa**: [automation/README.md](./automation/README.md)

| Agente | Propósito | Código |
|--------|-----------|--------|
| CoherenceAnalyzerAgent | Análisis de coherencia código/tests/docs | `scripts/coding/ai/automation/coherence_analyzer_agent.py` |
| PDCAAutomationAgent | Ciclo Plan-Do-Check-Act automatizado | `scripts/coding/ai/automation/pdca_agent.py` |
| ConstitutionValidatorAgent | Validación de principios constitucionales | `scripts/coding/ai/automation/constitution_validator_agent.py` |
| DevContainerValidatorAgent | Validación de devcontainer | `scripts/coding/ai/automation/devcontainer_validator_agent.py` |
| MetricsCollectorAgent | Recolección de métricas DORA | `scripts/coding/ai/automation/metrics_collector_agent.py` |
| SchemaValidatorAgent | Validación de esquemas JSON | `scripts/coding/ai/automation/schema_validator_agent.py` |
| CIPipelineOrchestratorAgent | Orquestación de pipelines CI | `scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py` |

## Agentes DevOps

**Documentación completa**: [devops/README.md](./devops/README.md)

| Agente | Propósito | Definición |
|--------|-----------|------------|
| GitOpsAgent | Operaciones Git y gestión de repositorio | `.agent/agents/gitops_agent.md` |
| ReleaseAgent | Gestión de releases y versionado | `.agent/agents/release_agent.md` |
| DependencyAgent | Gestión de dependencias y CVEs | `.agent/agents/dependency_agent.md` |
| SecurityAgent | Auditorías de seguridad y compliance | `.agent/agents/security_agent.md` |
| CodeTasker | Tareas de programación asíncronas | `.agent/agents/my_agent.md` |
| CodexMCPWorkflow | Orquestación multi-agente | `.agent/agents/codex_mcp_workflow.md` |

## Agentes por Proveedor LLM

Agentes especializados por proveedor de modelos de lenguaje.

**Documentación completa**: [llm-providers/README.md](./llm-providers/README.md)

| Agente | Proveedor | Modelos | Definición |
|--------|-----------|---------|------------|
| ClaudeAgent | Anthropic | Claude Sonnet/Opus/Haiku | `.agent/agents/claude_agent.md` |
| ChatGPTAgent | OpenAI | GPT-4/3.5 | `.agent/agents/chatgpt_agent.md` |
| HuggingFaceAgent | Hugging Face | Phi-3, Llama, Mistral, etc. | `.agent/agents/huggingface_agent.md` |

**Script común**: `scripts/coding/ai/generators/llm_generator.py`

## Agentes por Dominio

Agentes que conectan la estructura del repositorio por dominio.

**Documentación completa**: [domain-agents/README.md](./domain-agents/README.md)

| Agente | Directorio | Responsabilidad | Definición |
|--------|------------|-----------------|------------|
| ApiAgent | `api/` | Backend/API development | `.agent/agents/api_agent.md` |
| UiAgent | `ui/` | Frontend/UI development | `.agent/agents/ui_agent.md` |
| InfrastructureAgent | `infrastructure/` | IaC y DevOps | `.agent/agents/infrastructure_agent.md` |
| DocsAgent | `docs/` | Documentación | `.agent/agents/docs_agent.md` |
| ScriptsAgent | `scripts/` | Scripts y utilidades | `.agent/agents/scripts_agent.md` |

## Técnicas de Prompting

Implementaciones de técnicas avanzadas de ingeniería de prompts.

**Documentación completa**: [techniques/README.md](./techniques/README.md)

**Ubicación del código**: `scripts/coding/ai/agents/base/`

### Técnicas Fundamentales
- Role Prompting
- Few-Shot Prompting
- Zero-Shot Prompting

### Técnicas de Estructuración
- Prompt Chaining
- Task Decomposition

### Técnicas de Conocimiento
- ReAct (Reasoning + Acting)
- RAG (Retrieval-Augmented Generation)
- Tool-use Prompting

### Técnicas Avanzadas
- Auto-CoT (Automatic Chain-of-Thought) - `auto_cot_agent.py`
- Chain of Verification (CoVe) - `chain_of_verification.py`
- Self-Consistency - `self_consistency.py`
- Tree of Thoughts (ToT) - `tree_of_thoughts.py`

### Técnicas de Optimización
- Constitutional AI - `optimization_techniques.py`
- Delimiter-based Prompting
- Constrained Prompting

### Técnicas Especializadas
- Expert Prompting
- Meta-prompting
- Binary Search Prompting
- Greedy Information Density

## Mapeo de Agentes a Código

### Agentes con Implementación Python

| Categoría | Agente | Archivo Python | Tests |
|-----------|--------|----------------|-------|
| SDLC | SDLCPlannerAgent | `scripts/coding/ai/sdlc/planner_agent.py` | `scripts/coding/ai/tests/test_sdlc_planner_agent.py` |
| SDLC | SDLCFeasibilityAgent | `scripts/coding/ai/sdlc/feasibility_agent.py` | `scripts/coding/ai/tests/test_sdlc_feasibility_agent.py` |
| SDLC | SDLCDesignAgent | `scripts/coding/ai/sdlc/design_agent.py` | `scripts/coding/ai/tests/test_sdlc_design_agent.py` |
| SDLC | SDLCTestingAgent | `scripts/coding/ai/sdlc/testing_agent.py` | `scripts/coding/ai/tests/test_sdlc_testing_agent.py` |
| SDLC | SDLCDeploymentAgent | `scripts/coding/ai/sdlc/deployment_agent.py` | `scripts/coding/ai/tests/test_sdlc_deployment_agent.py` |
| Automation | CoherenceAnalyzerAgent | `scripts/coding/ai/automation/coherence_analyzer_agent.py` | `scripts/coding/ai/tests/test_coherence_analyzer_agent.py` |
| Automation | PDCAAutomationAgent | `scripts/coding/ai/automation/pdca_agent.py` | `scripts/coding/ai/tests/test_pdca_agent.py` |
| Automation | ConstitutionValidatorAgent | `scripts/coding/ai/automation/constitution_validator_agent.py` | `scripts/coding/ai/tests/test_constitution_validator_agent.py` |
| Automation | DevContainerValidatorAgent | `scripts/coding/ai/automation/devcontainer_validator_agent.py` | `scripts/coding/ai/tests/test_devcontainer_validator_agent.py` |
| Automation | MetricsCollectorAgent | `scripts/coding/ai/automation/metrics_collector_agent.py` | `scripts/coding/ai/tests/test_metrics_collector_agent.py` |
| Automation | SchemaValidatorAgent | `scripts/coding/ai/automation/schema_validator_agent.py` | `scripts/coding/ai/tests/test_schema_validator_agent.py` |
| Automation | CIPipelineOrchestratorAgent | `scripts/coding/ai/automation/ci_pipeline_orchestrator_agent.py` | `scripts/coding/ai/tests/test_ci_pipeline_orchestrator_agent.py` |
| Orchestration | CodexMCPWorkflow | `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` | - |
| Generation | LLMGenerator | `scripts/coding/ai/generators/llm_generator.py` | - |
| Shared | Agent (Base Class) | `scripts/coding/ai/shared/agent_base.py` | - |
| Shared | ContextSession | `scripts/coding/ai/shared/context_sessions.py` | - |

### Agentes con Definición Markdown

Estos agentes están definidos en markdown y se invocan via prompt/instrucción:

| Agente | Definición | Uso |
|--------|------------|-----|
| GitOpsAgent | `.agent/agents/gitops_agent.md` | Prompt-based |
| ReleaseAgent | `.agent/agents/release_agent.md` | Prompt-based |
| DependencyAgent | `.agent/agents/dependency_agent.md` | Prompt-based |
| SecurityAgent | `.agent/agents/security_agent.md` | Prompt-based |
| CodeTasker | `.agent/agents/my_agent.md` | Prompt-based |
| ApiAgent | `.agent/agents/api_agent.md` | Prompt-based |
| UiAgent | `.agent/agents/ui_agent.md` | Prompt-based |
| InfrastructureAgent | `.agent/agents/infrastructure_agent.md` | Prompt-based |
| DocsAgent | `.agent/agents/docs_agent.md` | Prompt-based |
| ScriptsAgent | `.agent/agents/scripts_agent.md` | Prompt-based |
| ClaudeAgent | `.agent/agents/claude_agent.md` | Prompt-based |
| ChatGPTAgent | `.agent/agents/chatgpt_agent.md` | Prompt-based |
| HuggingFaceAgent | `.agent/agents/huggingface_agent.md` | Prompt-based |

## Cómo Ejecutar Agentes

### Agentes Python (SDLC y Automatización)

```bash
# Ejemplo: SDLC Testing Agent
python scripts/coding/ai/sdlc/testing_agent.py \
  --project-root . \
  --output-dir docs/agent \
  --target-module "api/authentication" \
  --coverage-target 80

# Ejemplo: Coherence Analyzer
python scripts/coding/ai/automation/coherence_analyzer_agent.py \
  --project-root . \
  --module "scripts/coding/ai/sdlc" \
  --output-dir "docs/agent/coherence"
```

### Agentes por Prompt (DevOps, Dominio, LLM)

```
# Sintaxis general
[NombreAgente]: [Descripción de tarea]
[Parámetros opcionales]

# Ejemplo: GitOps
GitOpsAgent: Sincroniza todas las ramas principales con develop

# Ejemplo: ApiAgent
ApiAgent: Implementa endpoint POST /api/auth/login
Incluye validación, tests y documentación

# Ejemplo: con LLM específico
ClaudeAgent: Analiza el código de authentication.py y sugiere mejoras
```

## Técnicas de Prompting Aplicadas

### Auto-CoT (Automatic Chain-of-Thought)

Generación automática de razonamiento paso a paso:

```python
from scripts.coding.ai.agents.base.auto_cot_agent import AutoCoTAgent

agent = AutoCoTAgent(
    question="¿Cuáles son las implicaciones de seguridad de este código?",
    enable_clustering=True,
    num_demonstrations=5
)
result = agent.execute()
```

### Self-Consistency

Múltiples caminos de razonamiento con votación:

```python
from scripts.coding.ai.agents.base.self_consistency import SelfConsistencyAgent

agent = SelfConsistencyAgent(
    question="¿Cuál es la mejor arquitectura para este feature?",
    num_samples=5,
    temperature=0.7
)
result = agent.execute()
```

## Ejecución Paralela de Agentes

Para tareas complejas que requieren múltiples agentes:

```python
from scripts.coding/ai/orchestrators.codex_mcp_workflow import CodexMCPWorkflowBuilder

workflow = CodexMCPWorkflowBuilder()

# Agente 1: Análisis de diseño
workflow.add_agent(
    name="DesignAnalyzer",
    agent_class="SDLCDesignAgent",
    inputs={"module": "authentication"}
)

# Agente 2: Generación de tests (paralelo)
workflow.add_agent(
    name="TestGenerator",
    agent_class="SDLCTestingAgent",
    inputs={"module": "authentication"},
    parallel=True
)

# Agente 3: Análisis de coherencia (paralelo)
workflow.add_agent(
    name="CoherenceCheck",
    agent_class="CoherenceAnalyzerAgent",
    inputs={"module": "authentication"},
    parallel=True
)

# Ejecutar todo
results = workflow.execute_parallel()
```

## Test-Driven Development (TDD)

Todos los agentes SDLC y Automatización siguen TDD estricto:

```bash
# Ejecutar tests de un agente
pytest scripts/coding/ai/tests/test_sdlc_testing_agent.py -v

# Ejecutar todos los tests de agentes
pytest scripts/coding/ai/tests/ -v --cov=scripts/coding/ai

# Generar reporte de coverage
pytest scripts/coding/ai/tests/ --cov=scripts/coding/ai --cov-report=html
open htmlcov/index.html
```

## Referencias Principales

### Documentación de Agentes
- [Arquitectura de Agentes SDLC](../../scripts/coding/ai/agents/ARCHITECTURE_SDLC_AGENTS.md)
- [Guía de Agentes SDLC](../../docs/ai/SDLC_AGENTS_GUIDE.md)
- [Agentes y Técnicas Aplicadas](../../docs/ai/AGENTES_Y_TECNICAS_APLICADAS.md)

### Técnicas de Prompting
- [Catálogo de Técnicas de Prompting](../../docs/ai/prompting/PROMPT_TECHNIQUES_CATALOG.md)
- [Patrones de Sistemas Agénticos](../../docs/ai/prompting/AGENTIC_SYSTEM_PATTERNS.md)
- [Code Generation Guide](../../docs/ai_capabilities/prompting/CODE_GENERATION_GUIDE.md)
- [Phi3 Prompt Engineering Playbook](../../docs/ai_capabilities/prompting/PHI3_PROMPT_ENGINEERING_PLAYBOOK.md)

### Orquestación y Contexto
- [CODEX MCP Multi-Agent Guide](../../docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md)
- [Context Management Playbook](../../docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md)

### ExecPlans
- [ExecPlan CODEX MCP Multi-LLM](../../docs/plans/EXECPLAN_codex_mcp_multi_llm.md)
- [ExecPlan Agents Domain Alignment](../../docs/plans/EXECPLAN_agents_domain_alignment.md)

### Configuración
- [Configuración de API Keys](../../docs/ai/CONFIGURACION_API_KEYS.md)
- [Constitutional AI](../../docs/ai/constitutional_ai.md)

---

**Última actualización**: 2025-11-14
**Total de agentes**: 30+
**Técnicas de prompting**: 120+ documentadas, 20+ implementadas
**Cobertura de tests**: 80%+ en agentes SDLC y Automatización
**Metodología**: TDD (Test-Driven Development)

---

## Agentes Disponibles (Legacy - Referencia Histórica)

### 1. GitOpsAgent

**Archivo**: `gitops_agent.md`

**Propósito**: Operaciones Git y gestión de repositorio

**Capacidades**:
- Sincronización de ramas principales
- Limpieza de ramas obsoletas
- Auditoría de estructura de repositorio
- Gestión de workflows Git

**Cuándo usar**:
- Después de múltiples PRs mergeados
- Limpieza periódica de ramas
- Sincronización antes de release
- Auditoría de estructura del repositorio

**Ejemplo**:
```
GitOpsAgent: Sincroniza todas las ramas principales con develop
y genera reporte completo de cambios.
```

---

### 2. ReleaseAgent

**Archivo**: `release_agent.md`

**Propósito**: Gestión de releases y versionado semántico

**Capacidades**:
- Cálculo automático de versión según commits
- Generación de changelogs
- Creación de tags Git
- Actualización de archivos de versión
- Preparación de release notes

**Cuándo usar**:
- Crear nuevo release (major, minor, patch)
- Generar changelog
- Crear release candidate
- Hotfix urgente

**Ejemplo**:
```
ReleaseAgent: Crear nuevo release minor.
Analiza commits desde último tag, genera changelog,
actualiza versiones y crea tag.
```

---

### 3. DependencyAgent

**Archivo**: `dependency_agent.md`

**Propósito**: Gestión de dependencias y vulnerabilidades

**Capacidades**:
- Actualización de dependencias (conservadora/moderada/agresiva)
- Escaneo de vulnerabilidades (CVEs)
- Auditoría de licencias
- Limpieza de dependencias no usadas
- Gestión de lockfiles

**Cuándo usar**:
- Actualización mensual de dependencias
- Respuesta a alerta de CVE
- Auditoría de licencias antes de release
- Limpieza de dependencias obsoletas

**Ejemplo**:
```
DependencyAgent: Actualiza dependencias con estrategia conservadora.
Solo patches y minors. Genera reporte de cambios.
```

---

### 4. SecurityAgent

**Archivo**: `security_agent.md`

**Propósito**: Auditorías de seguridad y compliance

**Capacidades**:
- Escaneo de código con Bandit
- Detección de secrets con gitleaks
- Análisis de amenazas STRIDE
- Validación de restricciones del proyecto
- Auditoría de configuración de seguridad

**Cuándo usar**:
- Antes de cada release
- Auditoría mensual de seguridad
- Después de cambios en autenticación
- Respuesta a incidente de seguridad
- Validación de cumplimiento

**Ejemplo**:
```
SecurityAgent: Ejecuta auditoría completa de seguridad.
Incluye: código, dependencias, secrets, configuración.
Genera reporte priorizado por severidad.
```

---

### 5. CodeTasker (Original)

**Archivo**: `my_agent.md`

**Propósito**: Tareas de programación asíncronas

**Capacidades**:
- Escribir funciones en múltiples lenguajes
- Depurar errores
- Refactorizar módulos
- Generar documentación
- Ejecutar pruebas de código

**Cuándo usar**:
- Tareas de programación delegables
- Trabajo en segundo plano
- Refactorización de código

---

## Cómo Usar los Agentes

### Sintaxis General

```
[NombreAgente]: [Descripción de tarea]
[Parámetros opcionales]
```

### Ejemplos de Invocación

**Ejemplo 1 - Operación Simple**:
```
GitOpsAgent: Sincroniza ramas principales
```

**Ejemplo 2 - Con Parámetros**:
```
ReleaseAgent: Crear release patch
Tag: v1.3.1
Mensaje: "Hotfix crítico en autenticación"
```

**Ejemplo 3 - Operación Compleja**:
```
DependencyAgent: Actualiza dependencias con estrategia conservadora.
Solo patches y minors que resuelvan vulnerabilidades.
Excluir: Django (actualizar manualmente)
Generar reporte detallado.
```

## Buenas Prácticas

### 1. Especifica Claramente la Tarea

**Bien**:
```
SecurityAgent: Escanea vulnerabilidades en dependencias Python.
Prioriza CRITICAL y HIGH. Genera reporte con comandos de corrección.
```

**Mal**:
```
SecurityAgent: checa el código
```

### 2. Incluye Contexto Relevante

**Bien**:
```
ReleaseAgent: Crear hotfix patch para CVE-2023-xxxxx.
Prioridad: URGENTE. Solo actualizar Django a 4.2.7.
```

**Mal**:
```
ReleaseAgent: hacer release
```

### 3. Define Expectativas de Output

**Bien**:
```
GitOpsAgent: Audita estructura de ramas.
Verifica: 4 ramas principales, sin ramas obsoletas >30 días.
Genera: reporte en docs/qa/registros/
```

**Mal**:
```
GitOpsAgent: ve las ramas
```

### 4. Especifica Restricciones

**Bien**:
```
DependencyAgent: Actualiza dependencias.
NO actualizar: Django, Celery (breaking changes)
Solo: patches de paquetes en requirements/base.txt
```

**Mal**:
```
DependencyAgent: actualiza todo
```

## Integración con Workflows

Los agentes se integran con los procesos del proyecto:

### Pre-commit
```yaml
# .pre_commit_config.yaml
- repo: local
  hooks:
    - id: security-check
      name: SecurityAgent Pre-commit
      entry: SecurityAgent
      args: ["Escanea secrets en staged files"]
```

### CI/CD
```yaml
# .github/workflows/release.yml
- name: Create Release
  run: |
    ReleaseAgent: Crear release según tipo de commit.
    Push tag al remoto.
```

### Cron Jobs
```yaml
# .github/workflows/dependency-check.yml
on:
  schedule:
    - cron: '0 0 * * 1'  # Lunes
jobs:
  check:
    - name: Check Dependencies
      run: |
        DependencyAgent: Escanea vulnerabilidades.
        Crea issue si encuentra CRITICAL.
```

## Estructura de Reportes

Todos los agentes generan reportes en formato estándar:

**Ubicación**: `docs/qa/registros/YYYY_MM_DD_[agente]_[operacion].md`

**Formato**:
```markdown
---
id: QA-REG-YYYYMMDD-AGENTE
tipo: registro_actividad
categoria: devops|security|release
fecha: YYYY-MM-DD
responsable: [NombreAgente]
estado: completado|pendiente|fallido
---

# Registro: [Operación] - YYYY-MM-DD

## Información General
...

## Trabajo Realizado
...

## Resultados
...

## Próximos Pasos
...
```

## Documentación Relacionada

- **Agentes de Automatización**: `docs/desarrollo/agentes_automatizacion.md`
- **Arquitectura de Agentes**: `docs/desarrollo/arquitectura_agentes_especializados.md`
- **Runbooks DevOps**: `docs/devops/runbooks/`
- **Procedimientos**: `docs/gobernanza/procesos/`

## Desarrollo de Nuevos Agentes

Para crear un nuevo agente especializado:

1. **Definir propósito claro y específico**
   - Un agente = una responsabilidad
   - Evitar agentes monolíticos

2. **Crear archivo en `.github/agents/[nombre]-agent.md`**
   ```markdown
   ---
   name: [NombreAgente]
   description: [Descripción breve]
   ---
   # [Nombre] Agent
   ...
   ```

3. **Incluir secciones estándar**:
   - Capacidades
   - Cuándo usarlo
   - Ejemplos de uso
   - Herramientas que utiliza
   - Restricciones
   - Mejores prácticas

4. **Documentar en este README**

5. **Agregar a `docs/desarrollo/agentes_automatizacion.md`**

6. **Crear tests si el agente genera código**

## Soporte y Feedback

### Problemas con Agentes

Si un agente no funciona como esperado:

1. Verifica la sintaxis de invocación
2. Revisa el archivo de definición del agente
3. Consulta los ejemplos de uso
4. Revisa registros en `docs/qa/registros/`

### Sugerencias de Mejora

Para sugerir mejoras a agentes existentes:

1. Documentar caso de uso no cubierto
2. Proponer nueva capacidad
3. Reportar limitación encontrada
4. Crear issue en GitHub con etiqueta `agent-enhancement`

### Nuevos Agentes

Para proponer nuevos agentes:

1. Definir problema que resuelve
2. Verificar que no existe agente similar
3. Describir capacidades necesarias
4. Proponer nombre y sintaxis
5. Crear issue con etiqueta `new-agent`

## Métricas y Monitoreo

Los agentes generan métricas de uso:

- Número de ejecuciones por agente
- Tiempo promedio de ejecución
- Tasa de éxito/fallo
- Operaciones más comunes
- Reportes generados

Ver estadísticas en: `docs/qa/registros/metricas_agentes.md` (si existe)

---

**Última actualización**: 2025-11-05
**Total de agentes**: 5
**Versión de documentación**: 1.0.0
