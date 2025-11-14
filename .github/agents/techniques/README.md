# Técnicas de Prompting

Implementaciones de técnicas avanzadas de ingeniería de prompts utilizadas en el proyecto IACT.

## Ubicación

**Directorio**: `scripts/coding/ai/agents/base/`

## Catálogo Completo

El proyecto soporta **120+ técnicas de prompting** documentadas en:
- [PROMPT_TECHNIQUES_CATALOG.md](../../../docs/ai/prompting/PROMPT_TECHNIQUES_CATALOG.md)

## Técnicas Implementadas

### Técnicas Fundamentales

#### 1. Role Prompting
**Archivo**: `fundamental_techniques.py` - Clase `RolePromptingAgent`

**Descripción**: Asigna un rol específico al agente para orientar sus respuestas.

**Uso**:
```python
from scripts.coding.ai.agents.base.fundamental_techniques import RolePromptingAgent

agent = RolePromptingAgent(
    role="Senior Python Developer",
    task="Review this code for best practices"
)
result = agent.execute()
```

**Aplicado en**:
- SDLCTestingAgent (rol: Test Engineer)
- SDLCDesignAgent (rol: Software Architect)
- SecurityAgent (rol: Security Auditor)

---

#### 2. Few-Shot Prompting
**Archivo**: `fundamental_techniques.py` - Clase `FewShotPromptingAgent`

**Descripción**: Proporciona ejemplos para guiar el comportamiento del agente.

**Uso**:
```python
from scripts.coding.ai.agents.base.fundamental_techniques import FewShotPromptingAgent

examples = [
    {"input": "def add(a, b):", "output": "def test_add(): assert add(2, 3) == 5"},
    {"input": "def multiply(a, b):", "output": "def test_multiply(): assert multiply(2, 3) == 6"}
]

agent = FewShotPromptingAgent(examples=examples)
```

**Aplicado en**:
- SDLCPlannerAgent (ejemplos de issues)
- SDLCTestingAgent (ejemplos de tests)

---

#### 3. Zero-Shot Prompting
**Archivo**: `fundamental_techniques.py` - Clase `ZeroShotPromptingAgent`

**Descripción**: Ejecución sin ejemplos previos, solo instrucciones claras.

**Uso**:
```python
from scripts.coding.ai.agents.base.fundamental_techniques import ZeroShotPromptingAgent

agent = ZeroShotPromptingAgent(
    instruction="Generate unit tests for the following Python function"
)
```

---

### Técnicas de Estructuración

#### 4. Prompt Chaining
**Archivo**: `structuring_techniques.py` - Clase `PromptChainingAgent`

**Descripción**: Encadena múltiples prompts donde la salida de uno es entrada del siguiente.

**Uso**:
```python
from scripts.coding.ai.agents.base.structuring_techniques import PromptChainingAgent

chain = [
    {"agent": "DesignAgent", "output_to": "TestingAgent"},
    {"agent": "TestingAgent", "output_to": "DeploymentAgent"}
]

agent = PromptChainingAgent(chain=chain)
```

**Aplicado en**:
- Pipeline SDLC completo
- CI/CD workflows

---

#### 5. Task Decomposition
**Archivo**: `structuring_techniques.py` - Clase `TaskDecompositionAgent`

**Descripción**: Divide tareas complejas en subtareas manejables.

**Uso**:
```python
from scripts.coding.ai.agents.base.structuring_techniques import TaskDecompositionAgent

agent = TaskDecompositionAgent(
    task="Implement OAuth2 authentication",
    decompose=True
)
```

**Aplicado en**:
- SDLCPlannerAgent (divide épicas en issues)
- PDCAAutomationAgent (divide mejoras en pasos)

---

### Técnicas de Conocimiento

#### 6. ReAct (Reasoning + Acting)
**Archivo**: `knowledge_techniques.py` - Clase `ReActAgent`

**Descripción**: Alterna entre razonamiento y acciones para resolver problemas.

**Uso**:
```python
from scripts.coding.ai.agents.base.knowledge_techniques import ReActAgent

agent = ReActAgent(
    problem="Debug authentication error",
    tools=["read_logs", "check_config", "test_endpoint"]
)

# Ciclo: Think -> Act -> Observe -> Think -> Act...
```

**Patrón**:
```
Thought: I need to check if the API key is configured
Action: check_config("api_key")
Observation: API key is missing
Thought: I need to set the API key
Action: set_config("api_key", "...")
Observation: API key configured successfully
```

**Aplicado en**:
- SDLCFeasibilityAgent (analiza riesgos)
- CoherenceAnalyzerAgent (detecta gaps)

---

#### 7. RAG (Retrieval-Augmented Generation)
**Archivo**: `knowledge_techniques.py` - Clase `RAGAgent`

**Descripción**: Recupera información relevante antes de generar respuesta.

**Uso**:
```python
from scripts.coding.ai.agents.base.knowledge_techniques import RAGAgent

agent = RAGAgent(
    query="How to implement authentication?",
    knowledge_base="docs/",
    retrieval_top_k=5
)
```

**Aplicado en**:
- DocsAgent (recupera documentación relevante)
- SDLCDesignAgent (recupera patrones de diseño)

---

#### 8. Tool-use Prompting
**Archivo**: `knowledge_techniques.py` - Clase `ToolUseAgent`

**Descripción**: Agente puede llamar herramientas externas.

**Uso**:
```python
from scripts.coding.ai.agents.base.knowledge_techniques import ToolUseAgent

tools = {
    "execute_tests": pytest_runner,
    "format_code": black_formatter,
    "lint_code": pylint_checker
}

agent = ToolUseAgent(tools=tools)
```

**Aplicado en**:
- CIPipelineOrchestratorAgent (ejecuta herramientas CI)
- SecurityAgent (ejecuta scanners)

---

### Técnicas Avanzadas

#### 9. Auto-CoT (Automatic Chain-of-Thought)
**Archivo**: `auto_cot_agent.py` - Clase `AutoCoTAgent`

**Descripción**: Genera automáticamente cadenas de razonamiento paso a paso.

**Uso**:
```python
from scripts.coding.ai.agents.base.auto_cot_agent import AutoCoTAgent

agent = AutoCoTAgent(
    question="What are the security implications of this code?",
    enable_clustering=True,
    num_demonstrations=5
)
```

**Características**:
- **Question Clustering**: Agrupa preguntas similares
- **Demonstration Sampling**: Selecciona ejemplos representativos
- **Zero-Shot CoT**: Genera razonamiento automáticamente

**Aplicado en**:
- SDLCFeasibilityAgent (análisis de riesgos)
- SecurityAgent (análisis de amenazas)

---

#### 10. Chain of Verification (CoVe)
**Archivo**: `chain_of_verification.py` - Clase `ChainOfVerificationAgent`

**Descripción**: Genera respuesta, luego la verifica paso a paso.

**Uso**:
```python
from scripts.coding.ai.agents.base.chain_of_verification import ChainOfVerificationAgent

agent = ChainOfVerificationAgent(
    initial_response="Generated code implementation",
    verification_questions=[
        "Does it handle edge cases?",
        "Are there security vulnerabilities?",
        "Is it well tested?"
    ]
)
```

**Patrón**:
```
1. Generate baseline response
2. Plan verification questions
3. Answer verification questions independently
4. Generate final verified response
```

**Aplicado en**:
- ConstitutionValidatorAgent (verifica principios)
- SDLCTestingAgent (verifica coverage)

---

#### 11. Self-Consistency
**Archivo**: `self_consistency.py` - Clase `SelfConsistencyAgent`

**Descripción**: Genera múltiples respuestas y selecciona la más consistente por votación.

**Uso**:
```python
from scripts.coding.ai.agents.base.self_consistency import SelfConsistencyAgent

agent = SelfConsistencyAgent(
    question="What is the best architecture for this feature?",
    num_samples=5,
    temperature=0.7
)

# Genera 5 respuestas diferentes
# Selecciona la más frecuente (majority voting)
```

**Aplicado en**:
- SDLCDesignAgent (valida diseños)
- PDCAAutomationAgent (valida decisiones)

---

#### 12. Tree of Thoughts (ToT)
**Archivo**: `tree_of_thoughts.py` - Clase `TreeOfThoughtsAgent`

**Descripción**: Explora múltiples caminos de razonamiento en forma de árbol.

**Uso**:
```python
from scripts.coding.ai.agents.base.tree_of_thoughts import TreeOfThoughtsAgent

agent = TreeOfThoughtsAgent(
    problem="Design authentication system",
    branching_factor=3,
    depth=4,
    evaluation_strategy="best_first"
)
```

**Estrategias de exploración**:
- **BFS (Breadth-First Search)**: Explora todos los nodos por nivel
- **DFS (Depth-First Search)**: Explora profundamente cada rama
- **Best-First**: Explora las ramas más prometedoras primero

**Aplicado en**:
- SDLCFeasibilityAgent (explora alternativas)
- SDLCDesignAgent (explora diseños)

---

### Técnicas de Optimización

#### 13. Constitutional AI
**Archivo**: `optimization_techniques.py` - Clase `ConstitutionalAIAgent`

**Descripción**: Aplica principios constitucionales para garantizar outputs éticos y seguros.

**Uso**:
```python
from scripts.coding.ai.agents.base.optimization_techniques import ConstitutionalAIAgent

constitution = {
    "principles": [
        "Be helpful and harmless",
        "Do not generate insecure code",
        "Respect privacy and data protection"
    ]
}

agent = ConstitutionalAIAgent(constitution=constitution)
```

**Aplicado en**:
- TODOS los agentes (via Agent.apply_guardrails())
- ConstitutionValidatorAgent

---

#### 14. Delimiter-based Prompting
**Archivo**: `optimization_techniques.py` - Clase `DelimiterPromptingAgent`

**Descripción**: Usa delimitadores para separar secciones del prompt.

**Uso**:
```python
from scripts.coding.ai.agents.base.optimization_techniques import DelimiterPromptingAgent

agent = DelimiterPromptingAgent(
    sections={
        "CONTEXT": "This is a Django application...",
        "TASK": "Generate tests for authentication...",
        "FORMAT": "Use pytest format..."
    },
    delimiter="###"
)

# Genera:
# ### CONTEXT ###
# This is a Django application...
# ### TASK ###
# Generate tests for authentication...
# ### FORMAT ###
# Use pytest format...
```

**Aplicado en**:
- Todos los agentes SDLC (estructura de prompts)

---

#### 15. Constrained Prompting
**Archivo**: `optimization_techniques.py` - Clase `ConstrainedPromptingAgent`

**Descripción**: Fuerza al output a seguir un formato específico.

**Uso**:
```python
from scripts.coding.ai.agents.base.optimization_techniques import ConstrainedPromptingAgent

agent = ConstrainedPromptingAgent(
    output_format="JSON",
    schema={
        "test_name": "string",
        "assertions": ["string"],
        "fixtures": ["string"]
    }
)
```

**Aplicado en**:
- MetricsCollectorAgent (JSON de métricas)
- SchemaValidatorAgent (validación de schemas)

---

### Técnicas Especializadas

#### 16. Expert Prompting
**Archivo**: `specialized_techniques.py` - Clase `ExpertPromptingAgent`

**Descripción**: Simula múltiples expertos en un dominio.

**Uso**:
```python
from scripts.coding.ai.agents.base.specialized_techniques import ExpertPromptingAgent

experts = [
    {"role": "Security Expert", "focus": "vulnerabilities"},
    {"role": "Performance Expert", "focus": "optimization"},
    {"role": "UX Expert", "focus": "usability"}
]

agent = ExpertPromptingAgent(experts=experts)
```

**Aplicado en**:
- SDLCDesignAgent (múltiples perspectivas)
- SecurityAgent (análisis multi-facético)

---

#### 17. Meta-prompting
**Archivo**: `specialized_techniques.py` - Clase `MetaPromptingAgent`

**Descripción**: Genera prompts para otros agentes.

**Uso**:
```python
from scripts.coding.ai.agents.base.specialized_techniques import MetaPromptingAgent

agent = MetaPromptingAgent(
    objective="Generate prompts for testing agent",
    context="Python Django application"
)

# Output: Prompts optimizados para SDLCTestingAgent
```

**Aplicado en**:
- PromptTemplateEngine (generación de templates)

---

### Técnicas de Búsqueda y Optimización

#### 18. Binary Search Prompting
**Archivo**: `search_optimization_techniques.py` - Clase `BinarySearchPromptingAgent`

**Descripción**: Búsqueda jerárquica para encontrar respuestas óptimas.

**Uso**:
```python
from scripts.coding.ai.agents.base.search_optimization_techniques import BinarySearchPromptingAgent

agent = BinarySearchPromptingAgent(
    search_space="code_complexity_range",
    low=0,
    high=100,
    target="optimal_complexity"
)
```

**Aplicado en**:
- PDCAAutomationAgent (búsqueda de umbrales óptimos)

---

#### 19. Greedy Information Density
**Archivo**: `search_optimization_techniques.py` - Clase `GreedyInformationDensityAgent`

**Descripción**: Selecciona información de mayor densidad primero.

**Uso**:
```python
from scripts.coding.ai.agents.base.search_optimization_techniques import GreedyInformationDensityAgent

agent = GreedyInformationDensityAgent(
    candidates=["doc1.md", "doc2.md", "doc3.md"],
    max_tokens=2000
)

# Selecciona documentos con mayor densidad de información
# hasta llegar al límite de tokens
```

**Aplicado en**:
- DocsAgent (selección de docs relevantes)
- RAGAgent (selección de contexto)

---

### Template Engine

#### 20. Prompt Template Engine
**Archivo**: `prompt_templates.py` - Clase `PromptTemplateEngine`

**Descripción**: Sistema de templates para generar prompts consistentes.

**Uso**:
```python
from scripts.coding.ai.agents.base.prompt_templates import PromptTemplateEngine

template = """
---
role: {{role}}
task: {{task}}
---

# Context
{{context}}

# Instructions
{{instructions}}

# Output Format
{{output_format}}
"""

engine = PromptTemplateEngine(template=template)
prompt = engine.render(
    role="Python Developer",
    task="Generate tests",
    context="Django app",
    instructions="Use pytest",
    output_format="Python file"
)
```

**Aplicado en**:
- TODOS los agentes (generación de prompts YAML frontmatter)

---

## Mapeo de Técnicas a Agentes

| Agente | Técnicas Principales |
|--------|---------------------|
| **SDLCPlannerAgent** | Few-Shot, Task Decomposition, Template Engine |
| **SDLCFeasibilityAgent** | ReAct, Auto-CoT, Tree of Thoughts |
| **SDLCDesignAgent** | Expert Prompting, RAG, Self-Consistency |
| **SDLCTestingAgent** | Few-Shot, Template Engine, Tool-use |
| **SDLCDeploymentAgent** | Chain of Verification, Constrained Prompting |
| **CoherenceAnalyzerAgent** | ReAct, Binary Search |
| **PDCAAutomationAgent** | Self-Consistency, Binary Search |
| **ConstitutionValidatorAgent** | Constitutional AI, Chain of Verification |
| **MetricsCollectorAgent** | Constrained Prompting, Greedy Information Density |
| **CIPipelineOrchestratorAgent** | Prompt Chaining, Tool-use |

## Combinación de Técnicas

Las técnicas pueden combinarse para potenciar resultados:

### Ejemplo: Testing Agent
```
Role Prompting + Few-Shot + Template Engine + Constitutional AI
↓
Genera tests de alta calidad siguiendo patterns y principios éticos
```

### Ejemplo: Design Agent
```
Expert Prompting + RAG + Tree of Thoughts + Self-Consistency
↓
Explora múltiples diseños desde perspectivas expertas y selecciona el mejor
```

### Ejemplo: Feasibility Agent
```
Auto-CoT + ReAct + Chain of Verification
↓
Analiza riesgos con razonamiento paso a paso, ejecuta acciones y verifica resultados
```

## Referencias

- [Catálogo Completo de Técnicas](../../../docs/ai/prompting/PROMPT_TECHNIQUES_CATALOG.md)
- [Patrones Agénticos](../../../docs/ai/prompting/AGENTIC_SYSTEM_PATTERNS.md)
- [Agentes y Técnicas Aplicadas](../../../docs/ai/AGENTES_Y_TECNICAS_APLICADAS.md)
- [Code Generation Guide](../../../docs/ai_capabilities/prompting/CODE_GENERATION_GUIDE.md)
- [Phi3 Prompt Engineering Playbook](../../../docs/ai_capabilities/prompting/PHI3_PROMPT_ENGINEERING_PLAYBOOK.md)

---

**Última actualización**: 2025-11-14
**Técnicas documentadas**: 120+
**Técnicas implementadas**: 20+
**Técnicas activamente aplicadas**: 17+
