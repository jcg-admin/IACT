# Agentes LLM por Proveedor

Agentes especializados por proveedor de modelos de lenguaje (LLM) que vinculan configuración, credenciales y scripts reutilizables.

## Ubicación

**Archivos de definición**: `.agent/agents/`
**Scripts**: `scripts/coding/ai/generators/llm_generator.py`, `scripts/coding/ai/orchestrators/codex_mcp_workflow.py`

## Agentes Disponibles

### 1. ClaudeAgent

**Archivo**: `.agent/agents/claude_agent.md`

**Proveedor**: Anthropic

**Modelos soportados**:
- `claude-sonnet-4-5-20250929` (actual)
- `claude-3-5-sonnet-20240620`
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

**Cuándo usar**:
- Tareas que requieren razonamiento profundo
- Generación de código complejo
- Análisis de documentación extensa
- Tareas que requieren seguir instrucciones detalladas

**Configuración**:
```python
# En scripts/coding/ai/generators/llm_generator.py
llm_provider = "anthropic"
model = "claude-sonnet-4-5-20250929"
```

**Variables de entorno**:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

**Documentación de configuración**:
- [CONFIGURACION_API_KEYS.md](../../../docs/ai/CONFIGURACION_API_KEYS.md)

**ExecPlans relacionados**:
- [EXECPLAN_codex_mcp_multi_llm.md](../../../docs/plans/EXECPLAN_codex_mcp_multi_llm.md)

**Guías**:
- [SDLC_AGENTS_GUIDE.md](../../../docs/ai/SDLC_AGENTS_GUIDE.md)
- [PROMPT_TECHNIQUES_CATALOG.md](../../../docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md)
- [CODEX_MCP_MULTI_AGENT_GUIDE.md](../../../docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md)
- [CONTEXT_MANAGEMENT_PLAYBOOK.md](../../../docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md)

**Scripts reutilizables**:
- `scripts/coding/ai/shared/context_sessions.py` - Context trimming/summarizing

**Ejemplo de uso**:
```python
from scripts.coding.ai.generators.llm_generator import LLMGenerator

generator = LLMGenerator(
    llm_provider="anthropic",
    model="claude-sonnet-4-5-20250929",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

response = generator.generate(
    prompt="Generate unit tests for authentication module",
    max_tokens=4096,
    temperature=0.7
)
```

---

### 2. ChatGPTAgent

**Archivo**: `.agent/agents/chatgpt_agent.md`

**Proveedor**: OpenAI

**Modelos soportados**:
- `gpt-4-turbo-preview`
- `gpt-4`
- `gpt-3.5-turbo`

**Cuándo usar**:
- Generación de código rápida
- Tareas de propósito general
- Conversaciones interactivas
- Cuando se necesita bajo costo

**Configuración**:
```python
# En scripts/coding/ai/generators/llm_generator.py
llm_provider = "openai"
model = "gpt-4-turbo-preview"
```

**Variables de entorno**:
```bash
OPENAI_API_KEY=sk-...
```

**Documentación de configuración**:
- [CONFIGURACION_API_KEYS.md](../../../docs/ai/CONFIGURACION_API_KEYS.md)

**ExecPlans relacionados**:
- [EXECPLAN_codex_mcp_multi_llm.md](../../../docs/plans/EXECPLAN_codex_mcp_multi_llm.md)

**Guías**:
- [SDLC_AGENTS_GUIDE.md](../../../docs/ai/SDLC_AGENTS_GUIDE.md)
- [PROMPT_TECHNIQUES_CATALOG.md](../../../docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md)
- [CODEX_MCP_MULTI_AGENT_GUIDE.md](../../../docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md)
- [CONTEXT_MANAGEMENT_PLAYBOOK.md](../../../docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md)

**Scripts reutilizables**:
- `scripts/coding/ai/shared/context_sessions.py` - Context trimming/summarizing

**Ejemplo de uso**:
```python
from scripts.coding.ai.generators.llm_generator import LLMGenerator

generator = LLMGenerator(
    llm_provider="openai",
    model="gpt-4-turbo-preview",
    api_key=os.getenv("OPENAI_API_KEY")
)

response = generator.generate(
    prompt="Refactor this function for better performance",
    max_tokens=2048,
    temperature=0.5
)
```

---

### 3. HuggingFaceAgent

**Archivo**: `.agent/agents/huggingface_agent.md`

**Proveedor**: Hugging Face (modelos locales y hosted)

**Modelos soportados**:
- Modelos locales (Phi-3, Llama, Mistral, etc.)
- Modelos vía Inference API
- Modelos fine-tuned propios

**Cuándo usar**:
- Modelos locales para privacidad
- Modelos fine-tuned personalizados
- Cuando se necesita control total del modelo
- Entornos sin conectividad a internet

**Configuración**:
```python
# En scripts/coding/ai/generators/llm_generator.py
llm_provider = "huggingface"
model = "microsoft/Phi-3-mini-4k-instruct"  # O modelo local
```

**Variables de entorno**:
```bash
# Para modelos hosted
HUGGINGFACEHUB_API_TOKEN=hf_...

# Para modelos locales
HF_LOCAL_MODEL_PATH=/path/to/model
HF_MODEL_ID=microsoft/Phi-3-mini-4k-instruct
```

**Documentación de configuración**:
- [CONFIGURACION_API_KEYS.md](../../../docs/ai/CONFIGURACION_API_KEYS.md)

**ExecPlans relacionados**:
- [EXECPLAN_codex_mcp_multi_llm.md](../../../docs/plans/EXECPLAN_codex_mcp_multi_llm.md)

**Guías**:
- [SDLC_AGENTS_GUIDE.md](../../../docs/ai/SDLC_AGENTS_GUIDE.md)
- [PROMPT_TECHNIQUES_CATALOG.md](../../../docs/ai_capabilities/prompting/PROMPT_TECHNIQUES_CATALOG.md)
- [PHI3_PROMPT_ENGINEERING_PLAYBOOK.md](../../../docs/ai_capabilities/prompting/PHI3_PROMPT_ENGINEERING_PLAYBOOK.md)
- [CODEX_MCP_MULTI_AGENT_GUIDE.md](../../../docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md)
- [CONTEXT_MANAGEMENT_PLAYBOOK.md](../../../docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md)

**Scripts reutilizables**:
- `scripts/coding/ai/shared/context_sessions.py` - Context trimming/summarizing

**Ejemplo de uso - Modelo local**:
```python
from scripts.coding.ai.generators.llm_generator import LLMGenerator

generator = LLMGenerator(
    llm_provider="huggingface",
    model="microsoft/Phi-3-mini-4k-instruct",
    local_model_path="/path/to/model"
)

response = generator.generate(
    prompt="Explain this Python function",
    max_tokens=1024,
    temperature=0.3
)
```

**Ejemplo de uso - Inference API**:
```python
from scripts.coding.ai.generators.llm_generator import LLMGenerator

generator = LLMGenerator(
    llm_provider="huggingface",
    model="meta-llama/Llama-2-7b-chat-hf",
    api_key=os.getenv("HUGGINGFACEHUB_API_TOKEN")
)

response = generator.generate(
    prompt="Generate SQL query for user authentication",
    max_tokens=512
)
```

---

## Comparación de Proveedores

| Característica | ClaudeAgent | ChatGPTAgent | HuggingFaceAgent |
|---------------|-------------|--------------|------------------|
| **Razonamiento** | Excelente | Muy bueno | Bueno |
| **Velocidad** | Rápido | Muy rápido | Variable |
| **Costo** | Medio | Medio | Bajo/Gratis (local) |
| **Context Window** | 200K tokens | 128K tokens | Variable (4K-32K) |
| **Privacidad** | Cloud | Cloud | Local disponible |
| **Fine-tuning** | No | Sí | Sí |
| **Offline** | No | No | Sí (local) |

## Selección de Proveedor

### Usa ClaudeAgent cuando:
- Necesitas análisis profundo de código
- Trabajas con documentación extensa
- Requieres seguir instrucciones complejas
- Necesitas razonamiento paso a paso

### Usa ChatGPTAgent cuando:
- Necesitas respuestas rápidas
- Tareas de propósito general
- Presupuesto limitado
- Necesitas función calling nativa

### Usa HuggingFaceAgent cuando:
- Necesitas privacidad total (on-premise)
- Tienes un modelo fine-tuned
- Trabajas sin conectividad
- Necesitas control total del modelo

## Multi-LLM Orchestration

Para casos que requieren múltiples proveedores:

```python
from scripts.coding.ai.orchestrators.codex_mcp_workflow import CodexMCPWorkflowBuilder

workflow = CodexMCPWorkflowBuilder()

# Fase 1: Diseño con Claude (mejor razonamiento)
workflow.add_agent(
    name="DesignAgent",
    provider="anthropic",
    model="claude-sonnet-4-5-20250929",
    phase="design"
)

# Fase 2: Generación de código con ChatGPT (más rápido)
workflow.add_agent(
    name="CodeGenAgent",
    provider="openai",
    model="gpt-4-turbo-preview",
    phase="implementation"
)

# Fase 3: Testing con modelo local (privacidad)
workflow.add_agent(
    name="TestAgent",
    provider="huggingface",
    model="microsoft/Phi-3-mini-4k-instruct",
    phase="testing",
    local=True
)

workflow.execute()
```

## Context Management

Todos los proveedores usan el mismo sistema de gestión de contexto:

```python
from scripts.coding.ai.shared.context_sessions import ContextSession

session = ContextSession(
    provider="anthropic",  # o "openai", "huggingface"
    max_tokens=8000,
    trimming_strategy="summarize"  # o "truncate", "sliding_window"
)

session.add_message("user", "Initial context...")
session.add_message("assistant", "Response...")

# Automáticamente resume o recorta cuando se excede max_tokens
session.add_message("user", "New question...")
```

## Referencias

- [Configuración de API Keys](../../../docs/ai/CONFIGURACION_API_KEYS.md)
- [ExecPlan Multi-LLM](../../../docs/plans/EXECPLAN_codex_mcp_multi_llm.md)
- [CODEX MCP Multi-Agent Guide](../../../docs/ai_capabilities/orchestration/CODEX_MCP_MULTI_AGENT_GUIDE.md)
- [Context Management Playbook](../../../docs/ai_capabilities/orchestration/CONTEXT_MANAGEMENT_PLAYBOOK.md)
- [Phi3 Prompt Engineering](../../../docs/ai_capabilities/prompting/PHI3_PROMPT_ENGINEERING_PLAYBOOK.md)

---

**Última actualización**: 2025-11-14
**Total de proveedores**: 3
**Modelos soportados**: 10+
