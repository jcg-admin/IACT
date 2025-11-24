---
title: Catalogo Completo de Tecnicas de Prompting Multi-LLM
date: 2025-11-13
domain: ai_capabilities
status: active
applies_to: [Claude, ChatGPT, HuggingFace, Ollama]
---

# Catalogo Completo de Tecnicas de Prompting Multi-LLM

Referencia unificada de tecnicas de prompting aplicables a Claude, ChatGPT, Hugging Face y Ollama para todos los dominios del proyecto IACT (Backend/API, Frontend/UI, Infrastructure, Docs, Scripts).

---

## Indice

1. [Tecnicas Core](#1-tecnicas-core)
2. [Tecnicas SDLC](#2-tecnicas-sdlc)
3. [Tecnicas Avanzadas](#3-tecnicas-avanzadas)
4. [Tecnicas Proyecto IACT](#4-tecnicas-proyecto-iact)
5. [Mapeo por Proveedor LLM](#5-mapeo-por-proveedor-llm)
6. [Mapeo por Dominio](#6-mapeo-por-dominio)
7. [Referencias](#7-referencias)

---

## 1. Tecnicas Core

### 1.1 Chain-of-Thought (CoT)

**Descripcion**: Prompting que guia al modelo a razonar paso a paso antes de dar respuesta final.

**Cuando usar**:
- Problemas complejos multi-paso
- Debugging
- Planificacion arquitectura
- Analisis de requisitos

**Ejemplo**:
```
Problema: Implementar autenticacion JWT en API Django

CoT Prompt:
"Analiza paso a paso como implementar autenticacion JWT:
1. Identifica dependencias necesarias (djangorestframework-simplejwt)
2. Define configuracion settings.py
3. Crea endpoints login/refresh
4. Implementa middleware autenticacion
5. Escribe tests unitarios
Explica cada paso con codigo ejemplo."
```

**Aplicable a**: Claude, ChatGPT, Llama, Qwen

---

### 1.2 Auto-CoT (Automatic Chain-of-Thought)

**Descripcion**: Extension de CoT donde el modelo AUTOMATICAMENTE descompone problema en sub-problemas sin necesidad de listar pasos manualmente.

**Cuando usar**:
- Problemas muy complejos donde no conoces todos los pasos
- Exploracion de soluciones
- Generacion de planes SDLC
- Descomposicion modular

**Ejemplo**:
```
Auto-CoT Prompt:
"Descompone automaticamente el problema de implementar sistema automatizacion
para proyecto IACT. Identifica todos los sub-problemas, dependencias y
orden de implementacion optimo."
```

**Aplicado en IACT**:
- Descomposicion LLD en 6 modulos (LLD_00_OVERVIEW.md)
- Arquitectura agentes (6 agentes identificados)
- Orden implementacion (SchemaValidator → DevContainer → Metrics → Coherence → Constitution → CIPipeline)

**Aplicable a**: Claude (excelente), ChatGPT (bueno), Llama (moderado)

---

### 1.3 Self-Consistency

**Descripcion**: Generar multiples razonamientos para mismo problema y validar consistencia entre respuestas.

**Cuando usar**:
- Decisiones arquitectura criticas
- Validacion soluciones
- Trade-off analysis
- Seleccion entre alternativas

**Ejemplo**:
```
Self-Consistency Prompt:
"Analiza desde 3 perspectivas diferentes si usar arquitectura hibrida Bash/Python:

Perspectiva 1 - Performance:
...

Perspectiva 2 - Mantenibilidad:
...

Perspectiva 3 - Integracion Git Hooks:
...

Conclusion consistente entre perspectivas?"
```

**Aplicado en IACT**:
- Analisis arquitectura hibrida Bash/Python (AGENTS_ARCHITECTURE.md section 1.1)
- 4 perspectivas convergieron en misma decision
- Validacion modularizacion LLD

**Aplicable a**: Claude (excelente), ChatGPT (excelente), GPT-4 (excelente)

---

### 1.4 Few-Shot Learning

**Descripcion**: Proveer ejemplos antes de solicitar tarea.

**Cuando usar**:
- Generacion codigo con patron especifico
- Formato output consistente
- Estilo documentacion
- Convenciones proyecto

**Ejemplo**:
```
Few-Shot Prompt:
"Genera tests siguiendo este patron:

Ejemplo 1:
def test_validate_yaml_syntax():
    agent = SchemaValidatorAgent()
    result = agent.validate_syntax('valid.yaml')
    assert result.is_valid

Ejemplo 2:
def test_validate_json_syntax():
    agent = SchemaValidatorAgent()
    result = agent.validate_syntax('valid.json')
    assert result.is_valid

Ahora genera test para validate_references():"
```

**Aplicable a**: Todos los LLMs

---

### 1.5 Zero-Shot Learning

**Descripcion**: Solicitar tarea sin ejemplos previos.

**Cuando usar**:
- Tareas genericas
- LLMs con instruccion-tuning fuerte
- Problemas bien definidos

**Ejemplo**:
```
Zero-Shot Prompt:
"Implementa funcion Python que valida sintaxis YAML usando pyyaml.
Debe retornar True si valido, False si invalido."
```

**Aplicable a**: Claude, ChatGPT, GPT-4

---

## 2. Tecnicas SDLC

### 2.1 SDLC 6-Fases Prompting

**Descripcion**: Aplicar ciclo SDLC completo (Planning, Feasibility, Design, Testing, Deployment, Maintenance) a implementacion con LLM.

**Fases**:
1. **FASE 1 - Planning**: Definir alcance, objetivos, requisitos
2. **FASE 2 - Feasibility**: Analizar viabilidad tecnica, alternativas
3. **FASE 3 - Design**: HLD (High-Level Design) + LLD (Low-Level Design)
4. **FASE 4 - Testing**: TDD RED (tests primero)
5. **FASE 5 - Deployment**: TDD GREEN (implementacion)
6. **FASE 6 - Maintenance**: TDD REFACTOR + mejora continua

**Ejemplo Completo**:
```
FASE 1 Prompt:
"Define alcance sistema automatizacion IACT:
- Objetivos
- Stakeholders
- Success criteria
- Out of scope"

FASE 2 Prompt:
"Analiza viabilidad tecnica:
- Alternativas (Bash vs Python vs hibrido)
- Trade-offs
- Riesgos
- Recomendacion"

FASE 3 Prompt:
"Diseña arquitectura:
- HLD: Componentes alto nivel
- LLD: Especificaciones detalladas
- Integracion
- Dependencias"

FASE 4 Prompt:
"Especifica tests (TDD RED):
- Unit tests
- Integration tests
- E2E tests
- Fixtures"

FASE 5 Prompt:
"Implementa para pasar tests (TDD GREEN):
- Codigo minimo
- Pasar todos tests
- Exit codes correctos"

FASE 6 Prompt:
"Refactoriza y documenta:
- Optimizaciones
- ADR
- Metricas
- Plan mantenimiento"
```

**Aplicado en IACT**:
- HLD_SISTEMA_AUTOMATIZACION.md (FASE 1-3)
- TESTING_PLAN.md (FASE 4)
- DEPLOYMENT_PLAN.md (FASE 5)
- MAINTENANCE_PLAN.md (FASE 6)
- 6 agentes Python (SchemaValidator, DevContainer, Metrics, Coherence, Constitution, CIPipeline)

**Aplicable a**: Claude (excelente seguimiento multi-fase), ChatGPT (bueno), Llama (necesita mas guidance)

---

### 2.2 TDD (Test-Driven Development) Prompting

**Descripcion**: RED (tests) → GREEN (implementacion) → REFACTOR (optimizar)

**Workflow**:
```
RED Prompt:
"Escribe tests PRIMERO para SchemaValidatorAgent:
- test_validate_yaml_syntax
- test_validate_json_syntax
- test_detect_missing_fields
- test_validate_references
Todos deben FALLAR inicialmente."

GREEN Prompt:
"Implementa SchemaValidatorAgent para pasar TODOS los tests.
Codigo minimo necesario, sin sobre-ingenieria."

REFACTOR Prompt:
"Optimiza SchemaValidatorAgent manteniendo tests verdes:
- Extract methods
- DRY principle
- Type hints
- Docstrings"
```

**Aplicado en IACT**:
- 6 agentes implementados con TDD completo
- 150+ tests totales (100% passing)
- Coverage: 75-90% por agente

**Aplicable a**: Claude, ChatGPT, GPT-4

---

### 2.3 Task Masivo Paralelo para SDLC (NUEVA TECNICA)

**Descripcion**: Lanzar MULTIPLES agentes Task en PARALELO para implementar componentes SDLC simultaneamente, maximizando eficiencia.

**Cuando usar**:
- Implementacion multiple componentes independientes
- SDLC completo de sistema complejo
- Timeboxed development (acelerar entrega)
- Componentes con dependencias claras

**Workflow**:
1. **Identificar componentes independientes** (Auto-CoT decomposition)
2. **Lanzar Task agents en PARALELO** (1 mensaje, N tool calls)
3. **Cada agente ejecuta SDLC completo** (TDD RED-GREEN-REFACTOR + ADR)
4. **Validar resultados** en paralelo
5. **Integrar componentes**

**Ejemplo Aplicado - IACT Automation Agents**:

```python
# Mensaje UNICO con 6 Task tool calls paralelos

Task 1: SchemaValidatorAgent (TDD + ADR)
Task 2: DevContainerValidatorAgent (TDD + ADR)
Task 3: MetricsCollectorAgent (TDD + ADR)
Task 4: CoherenceAnalyzerAgent (TDD + ADR)
Task 5: ConstitutionValidatorAgent (TDD + ADR)
Task 6: CIPipelineOrchestratorAgent (TDD + ADR)

# Resultado:
# - 6 agentes implementados SIMULTANEAMENTE
# - 150+ tests (100% passing)
# - 6 ADRs completos
# - 8000+ lineas codigo
# - Tiempo: ~10 minutos (vs 6+ horas secuencial)
```

**Ventajas**:
- **50-90% reduccion tiempo**: Paralelismo real
- **Consistencia**: Mismo prompt pattern para todos
- **Escalabilidad**: N componentes = mismo tiempo base
- **Validacion cruzada**: Agentes independientes validan approach

**Desventajas**:
- **Dependencias**: Componentes deben ser independientes
- **Context limits**: Cada agente tiene context propio
- **Debugging**: Mas dificil troubleshoot N agentes vs 1

**Cuando NO usar**:
- Componentes fuertemente acoplados
- Desarrollo exploratorio (no sabes que construir)
- Prototipado rapido
- Single component focus

**Mejores Practicas**:
1. **Specs claras**: Cada Task agent necesita specs COMPLETAS
2. **ADR parent**: Arquitectura padre define integracion
3. **Validacion post**: Verificar integracion componentes
4. **Dependencies first**: Implementar dependencias antes de dependientes

**Aplicable a**: Claude Code (Task tool), custom automation frameworks

**Referencias IACT**:
- AGENTS_ARCHITECTURE.md (descomposicion 6 agentes)
- Implementation (6 agentes paralelos, 100% tests passing)
- Tiempo real: ~10 min vs estimado secuencial: 6+ horas (94% reduccion)

---

## 3. Tecnicas Avanzadas

### 3.1 Retrieval-Augmented Generation (RAG)

**Descripcion**: Combinar LLM con retrieval de documentacion/codigo para context adicional.

**Cuando usar**:
- Codebase grande
- Documentacion extensa
- Necesidad context especifico
- Evitar alucinaciones

**Ejemplo**:
```
RAG Prompt:
"Usando estos archivos como context:
[CONTEXT: LLD_01_CONSTITUCION.md]
[CONTEXT: AGENTS_ARCHITECTURE.md]

Implementa ConstitutionValidatorAgent siguiendo specs exactas."
```

**Aplicable a**: Claude (excelente con large context), ChatGPT (bueno con embeddings), RAG frameworks (LangChain, LlamaIndex)

---

### 3.2 Metacognitive Prompting

**Descripcion**: Pedir al modelo que reflexione sobre su propio proceso de razonamiento.

**Ejemplo**:
```
Metacognitive Prompt:
"Antes de implementar, responde:
1. Que asumpciones estoy haciendo?
2. Que podria salir mal?
3. Como validare que funciona?
4. Que alternativas considere y por que las descarte?"
```

**Aplicado en IACT**:
- ADRs (Alternatives Considered sections)
- Self-Consistency analysis (4 perspectivas)

**Aplicable a**: Claude (excelente), GPT-4 (excelente)

---

### 3.3 Constrained Prompting

**Descripcion**: Aplicar restricciones estrictas al output.

**Ejemplo**:
```
Constrained Prompt:
"Implementa funcion Python con ESTAS restricciones:
- NO emojis (CRITICAL)
- Type hints obligatorios
- Docstrings Google style
- Max 50 lineas por funcion
- Exit codes: 0=success, 1=error, 2=warning
- JSON output format"
```

**Aplicado en IACT**:
- NO EMOJIS rule (proyecto completo)
- Exit codes estandarizados
- JSON reporting format
- Conventional Commits

**Aplicable a**: Todos los LLMs

---

## 4. Tecnicas Proyecto IACT

### 4.1 Modular SDLC Decomposition

**Descripcion**: Aplicar Auto-CoT para descomponer SDLC en modulos independientes.

**Ejemplo**:
```
Modular SDLC Prompt:
"Descompone Low-Level Design en modulos independientes:

Criterios:
- Cada modulo < 1000 lineas
- Responsabilidad unica
- Referencias cruzadas claras
- Implementacion independiente posible

Output: Estructura modulos + justificacion"
```

**Aplicado en IACT**:
- LLD_00_OVERVIEW.md: Master index
- LLD_01 a LLD_05: 5 modulos especializados
- Total: 4200+ lineas documentacion
- Beneficio: Navegabilidad, Git-friendly, PRs pequenos

---

### 4.2 Hybrid Architecture Validation

**Descripcion**: Usar Self-Consistency para validar decisiones arquitectura hibrida.

**Ejemplo**:
```
Hybrid Architecture Prompt:
"Valida arquitectura hibrida Bash/Python desde:

Perspectiva 1: Performance
Perspectiva 2: Mantenibilidad
Perspectiva 3: Integracion existente
Perspectiva 4: Team expertise

Convergencia?: [SI/NO]
Decision final: [...]"
```

**Aplicado en IACT**:
- Bash entry points + Python business logic
- 4 perspectivas convergieron → arquitectura hibrida
- AGENTS_ARCHITECTURE.md section 1.1

---

### 4.3 Constitution-Driven Development

**Descripcion**: Definir "constitucion" proyecto con reglas/principios validados automaticamente.

**Ejemplo**:
```
Constitution Prompt:
"Define constitucion proyecto IACT:

Principios (WHY):
- P1: Separacion UI/API
- P2: Dual database routing
- P3: NO emojis
- P4: Conventional commits
- P5: TDD features criticos

Reglas (WHAT):
- R1: No push directo main (ERROR)
- R2: No emojis (ERROR)
- R3: UI/API coherence (WARNING)
- R4: Database router valido (ERROR)
- R5: Tests pass (ERROR)
- R6: DevContainer compatible (WARNING)

Implementa validador automatico."
```

**Aplicado en IACT**:
- .constitucion.yaml configuration
- ConstitutionValidatorAgent (6 reglas automaticas)
- Git hooks integration
- CI/CD validation

---

## 5. Mapeo por Proveedor LLM

### 5.1 Claude (Anthropic)

**Fortalezas**:
- Chain-of-Thought (CoT)
- Auto-CoT
- Self-Consistency
- Large context (200K tokens)
- Codigo Python/Bash
- Seguimiento multi-paso

**Tecnicas recomendadas**:
- SDLC 6-Fases completo
- TDD workflow
- Task masivo paralelo
- RAG con large context

**Configuracion**:
```python
{
  "llm_provider": "anthropic",
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 8000,
  "temperature": 0.2
}
```

**Referencias**:
- `.agent/agents/claude_agent.md`
- `docs/ai/SDLC_AGENTS_GUIDE.md`

---

### 5.2 ChatGPT / GPT-4 (OpenAI)

**Fortalezas**:
- Few-Shot Learning
- Code generation
- Structured output
- Function calling

**Tecnicas recomendadas**:
- Few-Shot prompting
- Structured JSON output
- Function calling para validacion

**Configuracion**:
```python
{
  "llm_provider": "openai",
  "model": "gpt-4-turbo-preview",
  "temperature": 0.2
}
```

**Referencias**:
- `.agent/agents/chatgpt_agent.md`

---

### 5.3 Hugging Face (Local Models)

**Fortalezas**:
- Privacidad (local)
- Fine-tuning custom
- No API costs
- Modelos especializados

**Tecnicas recomendadas**:
- Few-Shot (critico para modelos pequenos)
- Prompts concisos
- Fine-tuning con ejemplos proyecto

**Modelos recomendados**:
- TinyLlama-1.1B (fine-tuned)
- Phi-3-mini
- CodeLlama-7B
- Qwen2.5-Coder

**Referencias**:
- `.agent/agents/huggingface_agent.md`
- `docs/ai/FINE_TUNING_TINYLLAMA.md`

---

### 5.4 Ollama (Local Deployment)

**Fortalezas**:
- Easy setup local
- Multiple models
- Gratis, sin limites
- Privacy

**Tecnicas recomendadas**:
- Few-Shot
- Structured prompts
- Models: qwen2.5-coder:32b, llama3.1:8b, deepseek-coder-v2

**Configuracion**:
```python
{
  "llm_provider": "ollama",
  "model": "qwen2.5-coder:32b",
  "ollama_base_url": "http://localhost:11434"
}
```

---

## 6. Mapeo por Dominio

### 6.1 Backend / API (Django)

**Tecnicas aplicables**:
- TDD workflow (pytest)
- SDLC 6-Fases
- Few-Shot con patrones Django
- RAG con Django docs

**Agentes**:
- ApiAgent (`.agent/agents/api_agent.md`)
- TestingAgent (`scripts/coding/ai/sdlc/testing_agent.py`)

**Prompt ejemplo**:
```
"Implementa ViewSet Django para modelo User:
- CRUD completo
- Permissions (IsAuthenticated)
- Serializer con validaciones
- Tests (pytest) con fixtures
- Seguir patron DRF existente"
```

---

### 6.2 Frontend / UI (React)

**Tecnicas aplicables**:
- Component-driven prompting
- Few-Shot con patrones React
- TDD con Jest

**Agentes**:
- UiAgent (`.agent/agents/ui_agent.md`)

**Prompt ejemplo**:
```
"Implementa componente React UserProfile:
- TypeScript
- Props interface
- Hooks (useState, useEffect)
- API integration (services/userService)
- Tests Jest con React Testing Library"
```

---

### 6.3 Infrastructure / DevOps

**Tecnicas aplicables**:
- SDLC 6-Fases
- Self-Consistency (arquitectura decisions)
- Constitution-Driven (reglas infra)

**Agentes**:
- InfrastructureAgent (`.agent/agents/infrastructure_agent.md`)
- DevContainerValidatorAgent

**Prompt ejemplo**:
```
"Configura GitHub Actions CI/CD:
- Lint (ESLint, Ruff)
- Tests (Jest, Pytest)
- Coverage (80% threshold)
- Deploy staging
- YAML syntax"
```

---

### 6.4 Docs / Documentation

**Tecnicas aplicables**:
- Structured documentation prompting
- ADR generation
- README generation

**Agentes**:
- DocsAgent (`.agent/agents/docs_agent.md`)

**Prompt ejemplo**:
```
"Genera ADR para decision arquitectura hibrida Bash/Python:
- Context
- Decision
- Consequences (positive/negative)
- Alternatives considered
- References"
```

---

### 6.5 Scripts / Automation

**Tecnicas aplicables**:
- TDD workflow (bats para Bash, pytest para Python)
- Task masivo paralelo
- Shell best practices

**Agentes**:
- ShellAnalysisAgent (`scripts/coding/ai/agents/quality/shell_analysis_agent.py`)
- ShellRemediationAgent

**Prompt ejemplo**:
```
"Implementa script Bash validacion Git hooks:
- set -euo pipefail
- Funciones modulares
- Logging con colores
- Exit codes (0/1/2)
- Tests con bats"
```

---

## 7. Referencias

### Documentos IACT
- `docs/plans/EXECPLAN_prompt_techniques_catalog.md` - Plan implementacion
- `docs/ai/SDLC_AGENTS_GUIDE.md` - Guia agentes SDLC
- `docs/ai/prompting/CODE_GENERATION_GUIDE.md` - Generacion codigo
- `AGENTS_ARCHITECTURE.md` - Arquitectura agentes automation
- `.agent/agents/claude_agent.md` - Claude-specific
- `.agent/agents/chatgpt_agent.md` - ChatGPT-specific
- `.agent/agents/huggingface_agent.md` - HuggingFace-specific

### Agentes por Dominio
- `.agent/agents/api_agent.md` - Backend
- `.agent/agents/ui_agent.md` - Frontend
- `.agent/agents/infrastructure_agent.md` - Infra
- `.agent/agents/docs_agent.md` - Docs
- `.agent/agents/scripts_agent.md` - Scripts

### External Resources
- [Anthropic Prompt Engineering](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [OpenAI Best Practices](https://platform.openai.com/docs/guides/prompt-engineering)
- [HuggingFace Prompting Guide](https://huggingface.co/docs/transformers/tasks/prompting)
- [Chain-of-Thought Paper](https://arxiv.org/abs/2201.11903)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-13 | Initial catalog creation |
| 1.1 | 2025-11-13 | Added Task Masivo Paralelo SDLC technique |
| 1.2 | 2025-11-13 | Added IACT-specific techniques (Constitution-Driven, Hybrid Architecture) |

---

**Mantenido por**: DevOps Team / AI Capabilities Team
**Ultima actualizacion**: 2025-11-13
**Status**: Activo
**Applies to**: Claude, ChatGPT, HuggingFace, Ollama
**Dominios**: Backend, Frontend, Infrastructure, Docs, Scripts
