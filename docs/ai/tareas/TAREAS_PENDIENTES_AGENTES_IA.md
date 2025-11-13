---
title: Tareas Pendientes - Sistema de Agentes IA
fecha: 2025-11-11
owner: arquitecto-senior
status: ESPECIFICACION_COMPLETA
---

# Tareas Pendientes - Sistema de Agentes IA

## Estado Actual

### COMPLETADO

1. TDDFeatureAgent - IMPLEMENTACION COMPLETA
   - _generate_test_files() con LLMGenerator real
   - _generate_source_files() con LLMGenerator real
   - _get_test_files() con búsqueda glob
   - _get_source_files() con búsqueda glob
   - _execute_refactor_phase() con LLM + rollback safety
   - Archivo: scripts/ai/tdd/feature_agent.py
   - Commit: 6412791

2. SDLCPlannerAgent - IMPLEMENTACION COMPLETA
   - _generate_user_story() con LLMGenerator real
   - Validación de API keys implementada
   - Sistema de fallback a heurísticas
   - Parser robusto de JSON
   - Archivo: scripts/ai/sdlc/planner_agent.py
   - Commit: 6412791

---

## BLOQUE 1: Integraciones LLM Restantes (17 tareas)

### 1.1 Agentes Meta - Base (4 agentes)

**Ubicación:** scripts/ai/agents/base/

#### ChainOfVerificationAgent
**Archivo:** chain_of_verification.py
**Cambios necesarios:**
- Importar LLMGenerator: `from ...generators.llm_generator import LLMGenerator`
- Agregar en __init__: `self.llm = LLMGenerator(config=llm_config)`
- Reemplazar método `_generate()` para usar `self.llm._call_llm(prompt)`
- Implementar prompt específico para Chain-of-Verification

**Prompt sugerido:**
```
Eres un experto en verificación de hechos. Aplica la técnica Chain-of-Verification:
1. Genera respuesta base
2. Planea preguntas de verificación
3. Ejecuta verificaciones independientes
4. Genera respuesta final refinada
```

#### AutoCoTAgent
**Archivo:** auto_cot_agent.py
**Cambios necesarios:**
- Misma estructura de importación
- Reemplazar generador mock
- Implementar Auto Chain-of-Thought con ejemplos automáticos

**Prompt sugerido:**
```
Usa Auto-CoT: genera ejemplos de razonamiento automáticamente y aplica cadena de pensamiento.
```

#### SelfConsistencyAgent
**Archivo:** self_consistency.py
**Cambios necesarios:**
- Integrar LLMGenerator
- Implementar muestreo múltiple (k=5 por defecto)
- Implementar votación mayoritaria

**Implementación:**
```python
def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    k = self.config.get("num_samples", 5)
    responses = []
    for i in range(k):
        response = self.llm._call_llm(prompt)
        responses.append(response)

    # Votación mayoritaria
    final_answer = self._majority_vote(responses)
    return {"answer": final_answer, "samples": responses}
```

#### TreeOfThoughtsAgent
**Archivo:** tree_of_thoughts.py
**Cambios necesarios:**
- Integrar LLMGenerator
- Implementar búsqueda BFS o DFS
- Implementar evaluación de nodos

**Prompt sugerido:**
```
Genera N pensamientos alternativos para resolver el problema.
Para cada pensamiento, evalúa su promesa (score 1-10).
```

### 1.2 Agentes Meta - Análisis (5 agentes)

**Ubicación:** scripts/ai/agents/meta/

#### ArchitectureAnalysisAgent
**Archivo:** architecture_analysis_agent.py
**Cambios necesarios:**
- Integrar LLMGenerator
- Prompt para análisis SOLID
- Detectar violaciones arquitectónicas

**Prompt:**
```
Analiza el siguiente código Python para:
1. Violaciones de principios SOLID
2. Acoplamiento alto
3. Cohesión baja
4. Código espagueti
5. Recomendaciones de mejora
```

#### DesignPatternsAgent
**Archivo:** design_patterns_agent.py
**Cambios necesarios:**
- Integrar LLMGenerator
- Detectar patrones existentes
- Sugerir patrones apropiados

**Prompt:**
```
Analiza el código e identifica:
1. Patrones de diseño presentes (GoF, Enterprise)
2. Oportunidades para aplicar patrones
3. Patrones mal aplicados
```

#### RefactoringOpportunitiesAgent
**Archivo:** refactoring_opportunities_agent.py
**Cambios necesarios:**
- Integrar LLMGenerator
- Identificar code smells
- Sugerir refactorings

**Prompt:**
```
Identifica oportunidades de refactoring:
1. Code smells (Long Method, Large Class, etc)
2. Refactorings aplicables (Extract Method, Move Method, etc)
3. Prioridad (Alta/Media/Baja)
4. Riesgo de cada refactoring
```

#### TestGenerationAgent
**Archivo:** test_generation_agent.py
**Cambios necesarios:**
- Integrar LLMGenerator
- Generar test cases desde código
- Implementar cobertura estratégica

**Implementación:**
Ya existe LLMGenerator funcional en scripts/ai/generators/llm_generator.py
Este agente debe reutilizar esa implementación.

#### UMLValidationAgent
**Archivo:** uml_validation_agent.py
**Cambios necesarios:**
- Integrar LLMGenerator
- Validar diagramas UML
- Verificar consistencia

**Prompt:**
```
Valida el siguiente diagrama UML:
1. Sintaxis UML 2.5 correcta
2. Consistencia entre diagramas
3. Violaciones de convenciones
4. Sugerencias de mejora
```

### 1.3 test_generator.py
**Archivo:** scripts/ai/agents/tdd/test_generator.py
**Líneas:** 392, 403
**Cambios:**
- Implementar creación del agente
- Ajustar imports según ubicación
- Conectar con LLMGenerator

### 1.4 Métricas DORA (2 tareas)

#### PDCAAgent - Métricas reales
**Archivo:** scripts/ai/automation/pdca_agent.py
**Líneas:** 139-174
**Cambios:**
- Remover _get_mock_metrics()
- Implementar integración con GitHub API
- Calcular métricas DORA reales

**Implementación:**
```python
def _get_dora_metrics(self) -> Dict:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN required for DORA metrics")

    # Usar GitHub API para calcular:
    # 1. Deployment Frequency
    # 2. Lead Time for Changes
    # 3. Mean Time to Recovery
    # 4. Change Failure Rate

    return {
        'deployment_frequency': self._calc_deployment_freq(),
        'lead_time_days': self._calc_lead_time(),
        'mttr_hours': self._calc_mttr(),
        'change_failure_rate': self._calc_cfr(),
        'mock': False
    }
```

#### dora_metrics.py
**Archivo:** scripts/ai/automation/dora_metrics.py (CREAR NUEVO)
**Contenido:**
```python
"""
Módulo para cálculo de métricas DORA desde GitHub API.

Métricas DORA:
1. Deployment Frequency
2. Lead Time for Changes
3. Mean Time to Recovery (MTTR)
4. Change Failure Rate
"""

import os
from datetime import datetime, timedelta
from typing import Dict, List
import requests

class DORAMetricsCalculator:
    def __init__(self, github_token: str, repo_owner: str, repo_name: str):
        self.token = github_token
        self.owner = repo_owner
        self.repo = repo_name
        self.base_url = "https://api.github.com"

    def calculate_all_metrics(self) -> Dict:
        """Calcula todas las métricas DORA."""
        return {
            "deployment_frequency": self.deployment_frequency(),
            "lead_time_days": self.lead_time_for_changes(),
            "mttr_hours": self.mean_time_to_recovery(),
            "change_failure_rate": self.change_failure_rate(),
            "calculated_at": datetime.now().isoformat()
        }

    def deployment_frequency(self) -> float:
        """
        Deployment Frequency: deployments por día.
        Usa GitHub deployments API o tags.
        """
        # Implementar usando /repos/{owner}/{repo}/deployments
        pass

    def lead_time_for_changes(self) -> float:
        """
        Lead Time: tiempo desde commit hasta producción (días).
        """
        # Calcular desde PRs mergeados hasta deployment
        pass

    def mean_time_to_recovery(self) -> float:
        """
        MTTR: tiempo promedio de recuperación de incidentes (horas).
        """
        # Analizar issues con label 'incident'
        pass

    def change_failure_rate(self) -> float:
        """
        Change Failure Rate: % de deployments que causan fallos.
        """
        # Analizar deployments y rollbacks
        pass
```

---

## BLOQUE 2: Documentación (34 archivos)

### 2.1 Docs de Desarrollo (9 docs)

#### arquitectura_agentes_especializados.md
**Ubicación:** docs/desarrollo/arquitectura_agentes_especializados.md
**Contenido:**
```markdown
# Arquitectura de Agentes Especializados

## Visión General

Sistema de 35 agentes IA especializados que automatizan el SDLC completo.

## Categorías de Agentes

### 1. Agentes SDLC (7 agentes)
- SDLCPlannerAgent
- SDLCFeasibilityAgent
- SDLCDesignAgent
- SDLCTestingAgent
- SDLCDeploymentAgent
- SDLCMaintenanceAgent
- SDLCOrchestratorAgent

### 2. Agentes TDD (1 agente)
- TDDFeatureAgent

### 3. Agentes de Análisis de Negocio (5 agentes)
- BusinessAnalysisGenerator
- TraceabilityMatrixGenerator
- CompletenessValidator
- TemplateGenerator
- DocumentSplitter

### 4. Agentes de Calidad (6 agentes)
- CodeQualityValidator
- SyntaxValidator
- CoverageAnalyzer
- CoverageVerifier
- TestRunner
- PRCreator

### 5. Agentes Meta (9 agentes)
- ChainOfVerificationAgent
- AutoCoTAgent
- SelfConsistencyAgent
- TreeOfThoughtsAgent
- ArchitectureAnalysisAgent
- DesignPatternsAgent
- RefactoringOpportunitiesAgent
- TestGenerationAgent
- UMLValidationAgent

### 6. Agentes de Validación (3 agentes)
- RestrictionsGate
- RouteLintAgent
- DocsStructureGate

### 7. Agentes de Documentación (4 agentes)
- DocumentationEditorAgent
- CodeInspectorAgent
- ConsistencyVerifierAgent
- DocumentSplitter

### 8. Agentes de Automatización (1 agente)
- PDCAAgent

## Arquitectura de Integración LLM

### LLMGenerator
Componente central para todas las integraciones LLM:

```python
from generators.llm_generator import LLMGenerator

llm = LLMGenerator(config={
    "llm_provider": "anthropic",
    "model": "claude-3-5-sonnet-20241022"
})

response = llm._call_llm(prompt)
```

### Proveedores Soportados
- Anthropic Claude (ANTHROPIC_API_KEY)
- OpenAI GPT (OPENAI_API_KEY)

## Patrones de Implementación

### Patrón 1: Agente con LLM
```python
class MyAgent(SDLCAgent):
    def __init__(self, config):
        super().__init__(name="MyAgent", phase="custom", config=config)
        self.llm = LLMGenerator(config=config)

    def run(self, input_data):
        prompt = self._build_prompt(input_data)
        response = self.llm._call_llm(prompt)
        return self._parse_response(response)
```

### Patrón 2: Agente con Fallback
```python
def run(self, input_data):
    try:
        return self._run_with_llm(input_data)
    except Exception as e:
        logger.error(f"LLM failed: {e}")
        return self._run_with_heuristics(input_data)
```

### Patrón 3: Agente con Constitution
```python
from tdd_constitution import TDDConstitution

class MyAgent(SDLCAgent):
    def __init__(self, config):
        super().__init__(name="MyAgent", phase="custom", config=config)
        self.constitution = TDDConstitution()

    def run(self, input_data):
        result = self._execute(input_data)
        violations = self.constitution.validate(result)
        if violations:
            raise ConstitutionViolation(violations)
        return result
```

## Flujo de Ejecución

```
User Request
    |
    v
SDLCOrchestratorAgent
    |
    +-> SDLCPlannerAgent (LLM)
    |       |
    |       v
    +-> SDLCFeasibilityAgent
    |       |
    |       v (Go decision)
    +-> SDLCDesignAgent
    |       |
    |       v
    +-> TDDFeatureAgent (LLM)
    |       |
    |       v (RED-GREEN-REFACTOR)
    +-> SDLCTestingAgent
    |       |
    |       v
    +-> SDLCDeploymentAgent
            |
            v
        Production
```

## Métricas y Monitoreo

### DORA Metrics
- Deployment Frequency
- Lead Time for Changes
- Mean Time to Recovery
- Change Failure Rate

Implementación: scripts/ai/automation/dora_metrics.py

### Agent Performance
- Tiempo de ejecución por agente
- Tasa de éxito/fallo
- Uso de tokens LLM
- Costos por agente

## Seguridad

### API Keys
Almacenar en variables de entorno:
- ANTHROPIC_API_KEY
- OPENAI_API_KEY
- GITHUB_TOKEN

### Audit Trail
Todos los agentes registran en AuditLog:
```python
AuditLog.objects.create(
    user=None,
    action="agent_execution",
    resource=self.name,
    metadata={"input": input_data, "output": output_data}
)
```

### Guardrails
Validaciones automáticas en Constitution:
- No código malicioso
- No secrets en outputs
- Conformidad con estándares del proyecto

## Referencias

- Constitution: docs/gobernanza/agentes/constitution.md
- TDD Agent: docs/gobernanza/agentes/tdd-feature-agent.md
- SDLC Process: docs/gobernanza/procesos/SDLC_PROCESS.md
```

#### agentes_automatizacion.md
**Ubicación:** docs/desarrollo/agentes_automatizacion.md
**Contenido:**
```markdown
# Guía de Automatización con Agentes IA

## Introducción

Los agentes IA del proyecto IACT permiten automatizar tareas repetitivas del SDLC.

## Casos de Uso

### 1. Generación Automática de User Stories
```bash
python scripts/sdlc_cli.py plan "Implementar autenticación 2FA"
```

### 2. Implementación TDD Automática
```bash
python scripts/tdd_cli.py implement \
    --issue "ISSUE-123" \
    --module "auth" \
    --coverage 90
```

### 3. Análisis de Calidad Automático
```bash
python scripts/quality_cli.py analyze --path api/
```

### 4. Generación de Documentación
```bash
python scripts/docs_cli.py sync --project api/
```

## Integración CI/CD

### GitHub Actions
```yaml
name: AI Agents Pipeline

on: [pull_request]

jobs:
  analyze-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Quality Agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/quality_cli.py analyze \
            --path ${{ github.event.pull_request.changed_files }}
```

## Mejores Prácticas

1. Usar variables de entorno para API keys
2. Implementar rate limiting
3. Cachear respuestas LLM cuando sea posible
4. Monitorear costos de tokens
5. Validar outputs con guardrails

## Troubleshooting

Ver: docs/guias/troubleshooting/sdlc_agents_troubleshooting.md
```

#### testing.md, testing_standards.md, guia_integracion_llm.md, etc.
**Crear siguiendo estructura similar con contenido técnico relevante.**

### 2.2 Docs de Implementación

Crear estructura de directorios:
```bash
mkdir -p docs/implementacion/backend/arquitectura
mkdir -p docs/implementacion/frontend/arquitectura
mkdir -p docs/implementacion/infrastructure/arquitectura
mkdir -p docs/implementacion/backend/requisitos/negocio
mkdir -p docs/anexos/analisis_nov_2025
```

### 2.3 Docs de Gobernanza

Crear:
- docs/gobernanza/estandares_codigo.md
- docs/gobernanza/shell_scripting_guide.md

### 2.4 Otros Docs

Listar y crear según necesidad del proyecto.

---

## BLOQUE 3: Tests de Integración (20 tests)

Estructura estándar para tests de agentes:

```python
"""
Test de integración para XAgent.
"""
import pytest
from pathlib import Path
from scripts.ai.CATEGORY.agent_name import AgentClass

class TestAgentIntegration:
    @pytest.fixture
    def agent(self):
        return AgentClass(config={
            "project_root": Path("/test/project"),
            "output_dir": Path("/tmp/test_output")
        })

    def test_run_with_valid_input(self, agent):
        input_data = {
            "required_field": "value"
        }
        result = agent.run(input_data)
        assert result["status"] == "success"
        assert "output_field" in result

    def test_validate_input_missing_fields(self, agent):
        errors = agent.validate_input({})
        assert len(errors) > 0

    def test_end_to_end_workflow(self, agent):
        # Test completo del flujo
        pass
```

Crear tests para todos los agentes listados en el TODO.

---

## BLOQUE 4: Mejoras Técnicas (14 tareas)

### 4.1 Sistema de Cache
**Archivo:** scripts/ai/shared/llm_cache.py (CREAR)
```python
"""Cache para respuestas LLM."""
import hashlib
import json
from pathlib import Path

class LLMCache:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, prompt: str) -> str:
        cache_key = self._hash(prompt)
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file) as f:
                data = json.load(f)
                return data["response"]
        return None

    def set(self, prompt: str, response: str):
        cache_key = self._hash(prompt)
        cache_file = self.cache_dir / f"{cache_key}.json"
        with open(cache_file, "w") as f:
            json.dump({"prompt": prompt, "response": response}, f)

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()
```

### 4.2 Rate Limiting
**Modificar:** scripts/ai/generators/llm_generator.py
```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    def decorator(func):
        last_called = [0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            min_interval = 60.0 / calls_per_minute
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            last_called[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

class LLMGenerator:
    @rate_limit(calls_per_minute=60)
    def _call_llm(self, prompt: str) -> str:
        # existing implementation
        pass
```

### 4.3-4.14 Otras Mejoras
Documentar especificaciones técnicas para:
- Sistema de retry con backoff exponencial
- Streaming de respuestas
- Logging estructurado
- Dashboard de métricas
- Sistema de fallback
- Soporte modelos adicionales
- Validación de outputs
- Fine-tuning tracking
- A/B testing de prompts
- Profiling automático
- Benchmarks de performance

---

## BLOQUE 5: Herramientas y UX (16 tareas)

### 5.1 CLI Unificado
**Archivo:** scripts/sdlc_cli.py (CREAR)
```python
#!/usr/bin/env python3
"""
CLI unificado para agentes SDLC.
"""
import click
from pathlib import Path

@click.group()
def cli():
    """CLI para agentes SDLC."""
    pass

@cli.command()
@click.argument('feature_request')
def plan(feature_request):
    """Genera user story desde feature request."""
    from scripts.ai.sdlc.planner_agent import SDLCPlannerAgent
    agent = SDLCPlannerAgent()
    result = agent.run({"feature_request": feature_request})
    click.echo(result["issue_body"])

@cli.command()
@click.argument('issue_id')
@click.option('--module', required=True)
def implement(issue_id, module):
    """Implementa feature usando TDD."""
    from scripts.ai.tdd.feature_agent import TDDFeatureAgent
    agent = TDDFeatureAgent()
    # Implementation
    pass

if __name__ == '__main__':
    cli()
```

### 5.2-5.16 Otras Herramientas
Especificar implementaciones para:
- CLI de análisis de negocio
- Modo interactivo TDD
- Integración VS Code
- GitHub Actions
- Webhooks
- Interfaz web dashboard
- Sistema de notificaciones
- RBAC
- Modo batch
- Templates personalizables
- Sistema de plugins
- Migración de configuraciones
- Deprecation warnings
- Changelog automático
- Semantic versioning

---

## BLOQUE 6: Recursos Educativos (3 tareas)

### Video Tutoriales
Crear guiones para:
1. Introducción al Sistema de Agentes IA
2. TDDFeatureAgent - Paso a Paso
3. SDLCPlannerAgent - User Stories con IA
4. Agentes Meta - Técnicas Avanzadas
5. Integración CI/CD con Agentes

### Ejemplos de Integración
Crear repos de ejemplo:
- iact-agents-fastapi-example
- iact-agents-flask-example
- iact-agents-django-example (ya existe en IACT)

### Sistema de Feedback Loop
**Archivo:** scripts/ai/shared/feedback_loop.py (CREAR)
```python
"""
Sistema de feedback loop para aprender de correcciones humanas.
"""

class FeedbackLoop:
    def record_correction(self, agent_output, human_correction):
        """Registra corrección humana."""
        pass

    def analyze_patterns(self):
        """Analiza patrones de correcciones."""
        pass

    def suggest_prompt_improvements(self):
        """Sugiere mejoras a prompts basadas en feedback."""
        pass
```

---

## Priorización Final

### Crítico (Hacer Ya)
1. Conectar 9 agentes Meta con LLM
2. Implementar métricas DORA reales
3. Crear docs críticos (arquitectura, guía integración)
4. Tests de integración para agentes core

### Alto (Esta Semana)
1. CLI unificado
2. Sistema de cache LLM
3. Rate limiting
4. Documentación completa

### Medio (Este Mes)
1. GitHub Actions
2. Dashboard web
3. Mejoras técnicas restantes
4. Videos tutoriales

### Bajo (Backlog)
1. Integración VS Code
2. Sistema de plugins
3. Análisis de sentimiento
4. Modo determinístico

---

## Comandos de Ejecución

```bash
# Implementar agente Meta
nano scripts/ai/agents/base/chain_of_verification.py

# Crear documentación
nano docs/desarrollo/arquitectura_agentes_especializados.md

# Crear test
nano tests/ai/agents/test_tdd_feature_agent_integration.py

# Commit por bloque
git add .
git commit -m "feat(ai): BLOQUE_X - Descripción"
git push -u origin claude/analiza-de-011CV2qG9iotnq32BHnpXPzQ
```

---

## Métricas de Progreso

- Total tareas: 103
- Completadas: 2
- En progreso: 0
- Pendientes: 101

**Progreso:** 1.94%

---

**Última actualización:** 2025-11-11
**Responsable:** Claude AI Agent
**Rama:** claude/analiza-de-011CV2qG9iotnq32BHnpXPzQ
