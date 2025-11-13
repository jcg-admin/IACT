---
title: Guía de Uso: Agentes SDLC con LLM
date: 2025-11-13
domain: ai
status: active
---

# Guía de Uso: Agentes SDLC con LLM

Esta guía explica cómo usar los agentes SDLC (Software Development Life Cycle) que han sido integrados con capacidades de LLM (Large Language Models).

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Configuración](#configuración)
3. [Agentes Disponibles](#agentes-disponibles)
4. [Uso Básico](#uso-básico)
5. [Ejemplos Avanzados](#ejemplos-avanzados)
6. [Troubleshooting](#troubleshooting)

---

## Descripción General

Los agentes SDLC automatizan cada fase del ciclo de desarrollo de software, desde la evaluación de viabilidad hasta el despliegue. Cada agente puede operar en dos modos:

- **Modo Heurístico**: Análisis basado en reglas (rápido, determinista, sin costo)
- **Modo LLM**: Análisis potenciado por IA (inteligente, contextual, requiere API/modelo local)

**Ventajas del Modo LLM:**
- Análisis más profundo y contextual
- Recomendaciones más específicas
- Identificación de riesgos sutiles
- Mejor comprensión de requisitos ambiguos

---

## Configuración

### Opción 1: Anthropic Claude (Nube)

```python
config = {
    "llm_provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022",
    "use_llm": True
}

# Configurar API key (en .env o environment)
export ANTHROPIC_API_KEY="tu-api-key"
```

**Pros:** Mejor calidad, rápido, confiable
**Cons:** Requiere API key ($), envía datos a la nube

### Opción 2: OpenAI GPT-4 (Nube)

```python
config = {
    "llm_provider": "openai",
    "model": "gpt-4-turbo-preview",
    "use_llm": True
}

# Configurar API key
export OPENAI_API_KEY="tu-api-key"
```

**Pros:** Excelente calidad, bien documentado
**Cons:** Más costoso que Claude, envía datos a la nube

### Opción 3: Ollama (Local, Open Source) - RECOMENDADO

```python
config = {
    "llm_provider": "ollama",
    "model": "qwen2.5-coder:32b",  # o "llama3.1:8b", "deepseek-coder-v2"
    "ollama_base_url": "http://localhost:11434",  # opcional
    "use_llm": True
}

# Instalar y ejecutar Ollama
curl -fsSL https://ollama.com/install.sh | sh
ollama serve

# Descargar modelo
ollama pull qwen2.5-coder:32b
```

**Pros:** Gratis, privado, sin límites de uso
**Cons:** Requiere hardware (32GB+ RAM recomendado), más lento que APIs cloud

### Opción 4: Hugging Face (Modelos Fine-Tuned)

```python
config = {
    "llm_provider": "huggingface",
    "model": "/models/TinyLlama-1.1B-qlora",  # ruta local o repo-id
    "hf_generate_kwargs": {"max_new_tokens": 512, "temperature": 0.2},
    "use_llm": True
}

# Dependencias mínimas
pip install transformers==4.41.2 accelerate==0.31.0 peft==0.11.1 bitsandbytes==0.43.1 trl==0.9.4

# Los checkpoints descritos en la guía de fine-tuning viven en docs/ai/FINE_TUNING_TINYLLAMA.md
```

**Pros:**
- Permite ejecutar modelos entrenados específicamente para nuestro dominio (TinyLlama QLoRA + DPO)
- Mantiene los datos en infraestructura propia
- Integración directa con el nuevo `llm_provider='huggingface'`

**Cons:**
- Requiere GPU con soporte CUDA o aceleradores equivalentes para tiempos razonables
- Necesita administrar los checkpoints y merges de LoRA manualmente
- Mayor complejidad operativa comparado con API SaaS

### Modo Sin LLM (Solo Heurísticas)

```python
config = {
    "use_llm": False  # o simplemente config=None
}
```

**Pros:** Rápido, no requiere configuración
**Cons:** Análisis más básico

---

## Agentes Disponibles

### Agentes por proveedor LLM

Para asegurar coherencia entre planificación, credenciales y herramientas, consulta las fichas específicas en `.agent/agents/`:

- **ClaudeAgent** (`.agent/agents/claude_agent.md`): describe el flujo completo cuando `llm_provider="anthropic"`, enlazando el catálogo `docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md`, la configuración de `ANTHROPIC_API_KEY`, el uso del `LLMGenerator`, la memoria de contexto documentada en `docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md` y las orquestaciones Codex MCP de `docs/plans/EXECPLAN_codex_mcp_multi_llm.md`.
- **ChatGPTAgent** (`.agent/agents/chatgpt_agent.md`): guía las integraciones con modelos GPT/OpenAI, combina el catálogo `PROMPT_TECHNIQUES_CATALOG.md`, el playbook de contexto multi-LLM (`CONTEXT_MANAGEMENT_PLAYBOOK.md`), `OPENAI_API_KEY` y referencia `scripts/coding/ai/orchestrators/codex_mcp_workflow.py` junto a `scripts/coding/ai/shared/context_sessions.py`.
- **HuggingFaceAgent** (`.agent/agents/huggingface_agent.md`): centraliza el trabajo con modelos locales o alojados en Hugging Face, relacionando `PROMPT_TECHNIQUES_CATALOG.md`, rutas (`HF_LOCAL_MODEL_PATH`, `HF_MODEL_ID`), el playbook `PHI3_PROMPT_ENGINEERING_PLAYBOOK.md` y la guía de contexto compartido `CONTEXT_MANAGEMENT_PLAYBOOK.md`.

Estas fichas son complementarias a esta guía y deben revisarse antes de ejecutar tareas multi-LLM.

### Agentes por dominio

Para alinear la arquitectura del repositorio con los agentes automatizados, consulta también las fichas por dominio en `.agent/agents/`:

- **ApiAgent** (`api_agent.md`): centraliza la coordinación del backend (`api/`) con los ExecPlans `EXECPLAN_agents_domain_alignment.md`, `EXECPLAN_codex_mcp_multi_llm.md`, el catálogo `PROMPT_TECHNIQUES_CATALOG.md`, el playbook `CONTEXT_MANAGEMENT_PLAYBOOK.md` y los briefs generados por `CodexMCPWorkflowBuilder`.
- **UiAgent** (`ui_agent.md`): une los entregables del Designer Agent con la implementación en `ui/`, reutilizando los playbooks de prompting (`PROMPT_TECHNIQUES_CATALOG.md`, `CODE_GENERATION_GUIDE.md`, `PHI3_PROMPT_ENGINEERING_PLAYBOOK.md`) y las sesiones de contexto descritas en `CONTEXT_MANAGEMENT_PLAYBOOK.md`.
- **InfrastructureAgent** (`infrastructure_agent.md`): orquesta cambios en `infrastructure/` en conjunto con los agentes operativos (Dependency, Release, Security), el catálogo `PROMPT_TECHNIQUES_CATALOG.md`, el playbook `CONTEXT_MANAGEMENT_PLAYBOOK.md` y los planes `SPEC_INFRA_*`.
- **DocsAgent** (`docs_agent.md`): asegura que toda modificación en `docs/` respete al ETA-AGENTE CODEX, el catálogo `PROMPT_TECHNIQUES_CATALOG.md`, la guía de contexto multi-LLM y los validadores de documentación.
- **ScriptsAgent** (`scripts_agent.md`): gobierna la evolución de `scripts/` manteniendo el enfoque TDD, el catálogo `PROMPT_TECHNIQUES_CATALOG.md`, el playbook `CONTEXT_MANAGEMENT_PLAYBOOK.md` y la sincronización con los generadores/orquestadores LLM.

Cada vez que inicies un ExecPlan nuevo, referencia tanto la ficha del proveedor LLM como la del dominio involucrado para mantener la trazabilidad completa.

### 1. SDLCFeasibilityAgent

**Propósito:** Evalúa la viabilidad técnica de una feature antes de implementarla.

**Analiza:**
- Viabilidad técnica (complejidad, dependencias, compatibilidad)
- Riesgos (técnicos, de recursos, de calendario)
- Esfuerzo estimado (story points, personas, duración)

**Decisión:** GO / NO-GO / REVIEW

**Uso:**
```python
from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent

# Con LLM
config = {"llm_provider": "ollama", "model": "qwen2.5-coder:32b", "use_llm": True}
agent = SDLCFeasibilityAgent(config=config)

result = agent.run({
    "issue": {
        "title": "Implement JWT authentication",
        "description": "Add JWT-based auth with refresh tokens...",
        "requirements": ["Secure token storage", "Token refresh", "Logout"],
        "acceptance_criteria": ["Tokens expire after 1h", "Refresh works"],
        "estimated_story_points": 5
    }
})

print(f"Decision: {result.decision}")  # "go", "no-go", "review"
print(f"Confidence: {result.confidence}")  # 0.0 - 1.0
print(f"Risks: {result.risks}")
print(f"Method: {result.phase_result['analysis_method']}")  # "llm" o "heuristic"
```

**Output Artifacts:**
- `docs/sdlc_outputs/feasibility/FEASIBILITY_REPORT_YYYYMMDD_HHMMSS.md`

---

### 2. SDLCDesignAgent

**Propósito:** Genera documentación de diseño arquitectónico.

**Genera:**
- HLD (High-Level Design): Arquitectura general, componentes, flujo de datos
- LLD (Low-Level Design): Estructura de clases, módulos, APIs
- Diagramas: Mermaid para visualización
- ADRs (Architecture Decision Records): Decisiones de diseño

**Uso:**
```python
from scripts.ai.sdlc.design_agent import SDLCDesignAgent

agent = SDLCDesignAgent(config=config)

result = agent.run({
    "feasibility_result": {
        "phase": "feasibility",
        "decision": "go",
        "confidence": 0.85
    },
    "issue": {
        "title": "Implement JWT authentication",
        "description": "Add JWT-based auth...",
        "requirements": ["Secure storage", "Refresh mechanism"]
    }
})

print(f"HLD: {result.artifacts[0]}")  # Path to HLD document
print(f"LLD: {result.artifacts[1]}")  # Path to LLD document
print(f"Diagrams: {result.artifacts[2]}")  # Path to diagrams
```

**Output Artifacts:**
- `docs/sdlc_outputs/design/HLD_YYYYMMDD_HHMMSS.md`
- `docs/sdlc_outputs/design/LLD_YYYYMMDD_HHMMSS.md`
- `docs/sdlc_outputs/design/DIAGRAMS_YYYYMMDD_HHMMSS.md`
- `docs/sdlc_outputs/design/DESIGN_REVIEW_CHECKLIST_YYYYMMDD_HHMMSS.md`

---

### 3. SDLCTestingAgent

**Propósito:** Genera estrategia y casos de prueba.

**Genera:**
- Test Strategy: Enfoque, áreas críticas, distribución de tests
- Test Cases: Unit/Integration/E2E con pasos y aserciones
- Test Pyramid: Distribución 60% unit / 30% integration / 10% e2e
- Coverage Requirements: Mínimo 80-85% según complejidad

**Uso:**
```python
from scripts.ai.sdlc.testing_agent import SDLCTestingAgent

agent = SDLCTestingAgent(config=config)

result = agent.run({
    "design_result": {
        "phase": "design",
        "decision": "go",
        "confidence": 0.9,
        "artifacts": ["docs/.../HLD.md", "docs/.../LLD.md"]
    },
    "issue": {
        "title": "Implement JWT authentication",
        "requirements": ["Secure storage", "Refresh"],
        "estimated_story_points": 5
    }
})

print(f"Test Strategy: {result.recommendations}")
print(f"Test Cases: {len(test_cases)} cases generated")
print(f"Coverage Target: {coverage_requirement}%")
```

**Output Artifacts:**
- `docs/sdlc_outputs/testing/TEST_PLAN_YYYYMMDD_HHMMSS.md`
- `docs/sdlc_outputs/testing/TEST_CASES_YYYYMMDD_HHMMSS.md`
- `docs/sdlc_outputs/testing/TEST_PYRAMID_YYYYMMDD_HHMMSS.md`
- `docs/sdlc_outputs/testing/TEST_CHECKLIST_YYYYMMDD_HHMMSS.md`

---

### 4. SDLCDeploymentAgent

**Propósito:** Genera plan de despliegue y rollback.

**Genera:**
- Deployment Plan: Estrategia (rolling/blue-green/canary), pasos, tiempos
- Rollback Plan: Triggers, procedimientos, validaciones
- Checklists: Pre/Post-deployment verification
- Monitoring Plan: Métricas, alertas, duración

**Uso:**
```python
from scripts.ai.sdlc.deployment_agent import SDLCDeploymentAgent

agent = SDLCDeploymentAgent(config=config)

result = agent.run({
    "testing_result": {
        "phase": "testing",
        "decision": "go",
        "confidence": 0.88
    },
    "design_result": {...},
    "issue": {...},
    "environment": "production"  # o "staging"
})

print(f"Deployment Strategy: {strategy['approach']}")
print(f"Estimated Downtime: {strategy['downtime_minutes']} minutes")
print(f"Rollback Time: {strategy['rollback_minutes']} minutes")
```

**Output Artifacts:**
- `docs/sdlc_outputs/deployment/DEPLOYMENT_PLAN_{env}_YYYYMMDD_HHMMSS.md`
- `docs/sdlc_outputs/deployment/ROLLBACK_PLAN_{env}_YYYYMMDD_HHMMSS.md`
- `docs/sdlc_outputs/deployment/PRE_DEPLOYMENT_CHECKLIST_YYYYMMDD_HHMMSS.md`
- `docs/sdlc_outputs/deployment/POST_DEPLOYMENT_CHECKLIST_YYYYMMDD_HHMMSS.md`
- `docs/sdlc_outputs/deployment/MONITORING_PLAN_YYYYMMDD_HHMMSS.md`

---

### 5. SDLCOrchestratorAgent

**Propósito:** Orquesta todos los agentes SDLC en un pipeline completo.

**Coordina:**
- Planning → Feasibility → Design → Testing → Deployment
- Decisiones GO/NO-GO entre fases
- Agregación de riesgos
- Síntesis de recomendaciones

**Uso:**
```python
from scripts.ai.sdlc.orchestrator import SDLCOrchestrator

orchestrator = SDLCOrchestrator(config=config)

result = orchestrator.run({
    "feature_request": {
        "title": "Implement JWT authentication",
        "description": "Add JWT-based authentication...",
        "requirements": ["Secure storage", "Token refresh", "Logout"],
        "acceptance_criteria": ["Tokens expire", "Refresh works"],
        "estimated_story_points": 5
    },
    "start_phase": "planning",  # opcional, default="planning"
    "end_phase": "deployment",  # opcional, default="deployment"
    "skip_phases": []  # opcional, ej: ["testing"]
})

print(f"Pipeline Status: {result['final_decision']}")  # "success", "stopped"
print(f"Phases Completed: {result['phases_completed']}")
print(f"Artifacts: {result['all_artifacts']}")
print(f"Final Report: {result['report_path']}")
```

**Output Artifacts:**
- `docs/sdlc_outputs/orchestration/SDLC_PIPELINE_REPORT_YYYYMMDD_HHMMSS.md`
- Todos los artifacts de las fases individuales

---

## Ejemplos Avanzados

### Pipeline Completo con Ollama

```python
from scripts.ai.sdlc.orchestrator import SDLCOrchestrator

# Configurar Ollama (local, gratis)
config = {
    "llm_provider": "ollama",
    "model": "qwen2.5-coder:32b",
    "ollama_base_url": "http://localhost:11434",
    "use_llm": True
}

orchestrator = SDLCOrchestrator(config=config)

# Feature completa
feature = {
    "title": "User Profile Management",
    "description": """
    Implement user profile management with:
    - View profile
    - Edit profile (name, email, avatar)
    - Change password
    - Delete account
    """,
    "requirements": [
        "Secure password hashing (bcrypt)",
        "Email validation",
        "Avatar upload (max 5MB)",
        "Soft delete for accounts"
    ],
    "acceptance_criteria": [
        "Users can view their profile",
        "Users can update their info",
        "Password changes require current password",
        "Account deletion is reversible within 30 days"
    ],
    "estimated_story_points": 8
}

# Ejecutar pipeline completo
result = orchestrator.run({
    "feature_request": feature,
    "start_phase": "planning",
    "end_phase": "deployment"
})

# Revisar resultados
if result['final_decision'] == 'success':
    print("Pipeline completado exitosamente")
    print(f"Reporte final: {result['report_path']}")
    print(f"Artifacts generados: {len(result['all_artifacts'])}")
    print(f"Riesgos identificados: {len(result['aggregated_risks'])}")
    print(f"Recomendaciones: {len(result['recommendations'])}")
else:
    print(f"Pipeline detenido en fase: {result['stopped_at_phase']}")
    print(f"Razón: {result['stop_reason']}")
```

### Solo Feasibility (Evaluación Rápida)

```python
from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent

# Sin LLM (rápido, heurísticas)
agent = SDLCFeasibilityAgent(config=None)

result = agent.run({
    "issue": {
        "title": "Add Redis caching",  # BLOCKER: IACT prohíbe Redis
        "description": "Use Redis for session caching",
        "requirements": ["Fast caching", "Persistence"],
        "estimated_story_points": 3
    }
})

# Decision será "no-go" por restricción IACT
print(f"Decision: {result.decision}")  # "no-go"
print(f"Blockers: {[r for r in result.risks if r['severity'] == 'critical']}")
# Output: [{"type": "blocker", "description": "Redis is not allowed in IACT"}]
```

### Comparar LLM vs Heurísticas

```python
from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent

issue = {
    "title": "Implement GraphQL API",
    "description": "Replace REST with GraphQL",
    "requirements": ["Query optimization", "Schema design"],
    "estimated_story_points": 13
}

# Con heurísticas
agent_heuristic = SDLCFeasibilityAgent(config=None)
result_h = agent_heuristic.run({"issue": issue})

# Con LLM
config = {"llm_provider": "ollama", "model": "qwen2.5-coder:32b", "use_llm": True}
agent_llm = SDLCFeasibilityAgent(config=config)
result_llm = agent_llm.run({"issue": issue})

# Comparar
print(f"Heurísticas - Risks: {len(result_h.risks)}, Confidence: {result_h.confidence}")
print(f"LLM - Risks: {len(result_llm.risks)}, Confidence: {result_llm.confidence}")
# LLM típicamente identifica más riesgos sutiles y da confianza más calibrada
```

---

## Troubleshooting

### Error: "No module named 'anthropic'"

**Solución:**
```bash
pip install anthropic
# o
uv pip install --system anthropic
```

### Error: "ANTHROPIC_API_KEY not found"

**Solución:**
```bash
# Opción 1: Variable de entorno
export ANTHROPIC_API_KEY="tu-api-key"

# Opción 2: Archivo .env
echo "ANTHROPIC_API_KEY=tu-api-key" >> .env

# Opción 3: En código (NO recomendado para producción)
import os
os.environ["ANTHROPIC_API_KEY"] = "tu-api-key"
```

### Error: "Connection refused" (Ollama)

**Solución:**
```bash
# 1. Verificar que Ollama esté instalado
ollama --version

# 2. Iniciar servidor
ollama serve

# 3. Verificar que esté corriendo
curl http://localhost:11434/api/tags

# 4. Descargar modelo si no existe
ollama pull qwen2.5-coder:32b
```

### Ollama muy lento

**Soluciones:**
1. Usar un modelo más pequeño: `llama3.1:8b` (4.7GB) en lugar de `qwen2.5-coder:32b` (19GB)
2. Agregar GPU: Ollama usa GPU automáticamente si está disponible
3. Aumentar RAM: Modelos grandes requieren 32GB+ RAM
4. Usar modo heurístico para análisis rápidos

### LLM genera resultados inconsistentes

**Soluciones:**
1. Reducir temperature en config: `"temperature": 0.1` (más determinista)
2. Usar modelo más grande: mejor coherencia
3. Usar heurísticas si necesitas resultados 100% reproducibles

### Tests fallan con "ModuleNotFoundError: requests"

**Solución:**
```bash
# Instalar requests
pip install requests
# o
uv pip install --system requests

# Ejecutar tests con python3 -m pytest
python3 -m pytest tests/ai/sdlc/
```

---

## Referencias

- **Código Fuente:** `scripts/ai/sdlc/`
- **Tests:** `tests/ai/sdlc/`
- **Arquitectura:** `scripts/ai/agents/ARCHITECTURE_SDLC_AGENTS.md`
- **Ollama Docs:** https://ollama.com/docs
- **Anthropic Docs:** https://docs.anthropic.com
- **OpenAI Docs:** https://platform.openai.com/docs

---

## Mejores Prácticas

1. **Empieza con Heurísticas:** Evalúa primero sin LLM para entender el baseline
2. **Usa Ollama para Desarrollo:** Gratis, privado, bueno para iterar
3. **Usa Claude/GPT para Producción:** Mejor calidad para análisis críticos
4. **Revisa los Artifacts:** Los documentos generados son el verdadero valor
5. **Itera el Config:** Experimenta con diferentes modelos y providers
6. **Combina Modos:** Usa LLM para diseño/feasibility, heurísticas para testing
7. **Monitorea Costos:** Si usas APIs cloud, trackea llamadas
8. **Valida Salidas:** LLMs pueden alucinar, siempre revisa manualmente

---

**Versión:** 1.0
**Última Actualización:** 2025-01-12
**Mantenedor:** Equipo IACT AI
