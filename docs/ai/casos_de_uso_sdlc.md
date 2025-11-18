---
title: Casos de Uso: Agentes SDLC
date: 2025-11-13
domain: ai
status: active
---

# Casos de Uso: Agentes SDLC

Guía práctica con ejemplos ejecutables para diferentes escenarios reales.

---

## Índice de Casos de Uso

1. [Evaluar si una idea es viable](#caso-1-evaluar-viabilidad)
2. [Generar arquitectura para una feature](#caso-2-generar-arquitectura)
3. [Crear estrategia de tests](#caso-3-estrategia-de-tests)
4. [Planear deployment](#caso-4-planear-deployment)
5. [Pipeline completo automático](#caso-5-pipeline-completo)
6. [Generar diagramas UML](#caso-6-generar-diagramas-uml)
7. [Comparar proveedores LLM](#caso-7-comparar-proveedores)

---

## CASO 1: Evaluar Viabilidad

**Escenario**: Tienes una idea y quieres saber si es viable antes de invertir tiempo.

**¿Cuándo usar?**
- Antes de crear un issue en GitHub
- En reuniones de planning para evaluar ideas rápidamente
- Cuando el PM pregunta "¿cuánto tiempo tomaría esto?"

### Ejemplo Simple

```python
from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent

# Sin LLM (rápido, 0.1 segundos)
agent = SDLCFeasibilityAgent(config=None)

result = agent.run({
    "issue": {
        "title": "Add dark mode toggle",
        "description": "Users can switch between light and dark themes",
        "requirements": [
            "Toggle button in settings",
            "Store preference in localStorage",
            "CSS variables for theming"
        ],
        "estimated_story_points": 2
    }
})

# Acceder a resultados
report = result["feasibility_report"]
print(f"Decision: {report.decision}")  # "go", "no-go", "review"
print(f"Confidence: {report.confidence}")  # 0.0 - 1.0
print(f"Risks: {len(report.risks)}")
```

### Ejecutar Ejemplo

```bash
# Crear script de prueba
cat > test_feasibility_case1.py << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.ai.sdlc.feasibility_agent import SDLCFeasibilityAgent

agent = SDLCFeasibilityAgent(config=None)

result = agent.run({
    "issue": {
        "title": "Add dark mode toggle",
        "description": "Users can switch between light and dark themes",
        "requirements": ["Toggle in settings", "localStorage", "CSS variables"],
        "estimated_story_points": 2
    }
})

report = result["feasibility_report"]
print(f"Decision: {report.decision}")
print(f"Confidence: {report.confidence:.0%}")
print(f"Risks: {len(report.risks)}")
print(f"Estimated days: {result['effort_analysis']['estimated_days']}")
print(f"Report: {result['report_path']}")
EOF

python3 test_feasibility_case1.py
```

### Output Esperado

```
Decision: go
Confidence: 85%
Risks: 1
Estimated days: 1.0
Report: docs/sdlc_outputs/feasibility/FEASIBILITY_REPORT_20251112_HHMMSS.md
```

---

## CASO 2: Generar Arquitectura

**Escenario**: Tienes una feature aprobada y necesitas diseñar la arquitectura.

**¿Cuándo usar?**
- Después de que feasibility sea "go"
- Antes de empezar a codear
- Para documentar decisiones arquitectónicas

### Ejemplo: API REST para Upload de Archivos

```python
from scripts.ai.sdlc.design_agent import SDLCDesignAgent

# Con heurísticas (rápido)
agent = SDLCDesignAgent(config=None)

result = agent.run({
    "feasibility_result": {
        "phase": "feasibility",
        "decision": "go",
        "confidence": 0.85
    },
    "issue": {
        "title": "File Upload API",
        "description": "REST API endpoint for uploading files with validation",
        "requirements": [
            "Accept multipart/form-data",
            "Validate file type (images only)",
            "Max 10MB per file",
            "Store in /media/uploads/",
            "Return file URL"
        ]
    }
})

# Artifacts generados
print(f"HLD: {result['artifacts'][0]}")
print(f"LLD: {result['artifacts'][1]}")
print(f"Diagrams: {result['artifacts'][2]}")
```

### Ejecutar Ejemplo

```bash
cat > test_design_case2.py << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.ai.sdlc.design_agent import SDLCDesignAgent

agent = SDLCDesignAgent(config=None)

result = agent.run({
    "feasibility_result": {
        "phase": "feasibility",
        "decision": "go",
        "confidence": 0.85
    },
    "issue": {
        "title": "File Upload API",
        "description": "REST API endpoint for uploading files",
        "requirements": [
            "Accept multipart/form-data",
            "Validate file type",
            "Max 10MB",
            "Store in /media/uploads/",
            "Return URL"
        ]
    }
})

print("Artifacts generados:")
for artifact in result['artifacts']:
    print(f"  - {artifact}")
EOF

python3 test_design_case2.py
```

### Output Esperado

```
Artifacts generados:
  - docs/sdlc_outputs/design/HLD_20251112_HHMMSS.md
  - docs/sdlc_outputs/design/LLD_20251112_HHMMSS.md
  - docs/sdlc_outputs/design/DIAGRAMS_20251112_HHMMSS.md
  - docs/sdlc_outputs/design/DESIGN_REVIEW_CHECKLIST_20251112_HHMMSS.md
```

---

## CASO 3: Estrategia de Tests

**Escenario**: Tienes código listo y necesitas planear los tests.

**¿Cuándo usar?**
- Después de implementar una feature
- Para aumentar coverage
- Para documentar casos de prueba

### Ejemplo: Tests para Autenticación

```python
from scripts.ai.sdlc.testing_agent import SDLCTestingAgent

agent = SDLCTestingAgent(config=None)

result = agent.run({
    "design_result": {
        "phase": "design",
        "decision": "go",
        "confidence": 0.9
    },
    "issue": {
        "title": "User Authentication",
        "requirements": [
            "Login with email/password",
            "Password hashing",
            "Session management"
        ],
        "estimated_story_points": 5
    }
})

# Ver test plan
test_plan = result['test_plan']
print(f"Total test cases: {len(result['test_cases'])}")
print(f"Unit tests: {result['test_pyramid']['unit_tests']}")
print(f"Integration tests: {result['test_pyramid']['integration_tests']}")
print(f"Coverage target: {result['coverage_requirements']['target_coverage']}%")
```

### Ejecutar Ejemplo

```bash
cat > test_testing_case3.py << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.ai.sdlc.testing_agent import SDLCTestingAgent

agent = SDLCTestingAgent(config=None)

result = agent.run({
    "design_result": {
        "phase": "design",
        "decision": "go",
        "confidence": 0.9
    },
    "issue": {
        "title": "User Authentication",
        "requirements": ["Login", "Password hashing", "Sessions"],
        "estimated_story_points": 5
    }
})

print(f"Test cases generados: {len(result['test_cases'])}")
print(f"Unit: {result['test_pyramid']['unit_tests']}")
print(f"Integration: {result['test_pyramid']['integration_tests']}")
print(f"E2E: {result['test_pyramid']['e2e_tests']}")
print(f"Coverage target: {result['coverage_requirements']['target_coverage']}%")
EOF

python3 test_testing_case3.py
```

### Output Esperado

```
Test cases generados: 9
Unit: 6
Integration: 2
E2E: 1
Coverage target: 85%
```

---

## CASO 4: Planear Deployment

**Escenario**: Feature está testeada y lista para deploy.

**¿Cuándo usar?**
- Antes de mergear a main
- Para planear releases
- Para documentar procedimientos de rollback

### Ejemplo: Deploy a Staging

```python
from scripts.ai.sdlc.deployment_agent import SDLCDeploymentAgent

agent = SDLCDeploymentAgent(config=None)

result = agent.run({
    "testing_result": {
        "phase": "testing",
        "decision": "go",
        "confidence": 0.88
    },
    "issue": {
        "title": "Payment Integration",
        "requirements": ["Stripe API", "Webhook handling"],
        "estimated_story_points": 8
    },
    "environment": "staging"  # o "production"
})

print(f"Deployment approach: {result['deployment_strategy']['approach']}")
print(f"Estimated downtime: {result['deployment_strategy']['downtime_minutes']} min")
print(f"Rollback time: {result['deployment_strategy']['rollback_minutes']} min")
```

### Ejecutar Ejemplo

```bash
cat > test_deployment_case4.py << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.ai.sdlc.deployment_agent import SDLCDeploymentAgent

agent = SDLCDeploymentAgent(config=None)

result = agent.run({
    "testing_result": {"phase": "testing", "decision": "go", "confidence": 0.88},
    "design_result": {"phase": "design", "decision": "go", "confidence": 0.9},
    "issue": {
        "title": "Payment Integration",
        "requirements": ["Stripe API", "Webhook handling"],
        "estimated_story_points": 8
    },
    "environment": "staging"
})

strategy = result['deployment_strategy']
print(f"Approach: {strategy['approach']}")
print(f"Downtime: {strategy['downtime_minutes']} min")
print(f"Rollback: {strategy['rollback_minutes']} min")
print(f"Artifacts: {len(result['artifacts'])}")
EOF

python3 test_deployment_case4.py
```

### Output Esperado

```
Approach: rolling
Downtime: 0 min
Rollback: 5 min
Artifacts: 5
```

---

## CASO 5: Pipeline Completo

**Escenario**: Feature nueva desde cero, automatizar todo el proceso.

**¿Cuándo usar?**
- Features grandes que requieren planning completo
- Para mantener documentación consistente
- Cuando quieres evaluación end-to-end

### Ejemplo: Feature Completa

```python
from scripts.ai.sdlc.orchestrator import SDLCOrchestratorAgent

# Sin LLM (usa heurísticas en todas las fases)
config = None

orchestrator = SDLCOrchestratorAgent(config=config)

result = orchestrator.run({
    "feature_request": {
        "title": "Two-Factor Authentication",
        "description": "Add 2FA using TOTP",
        "requirements": [
            "TOTP library integration",
            "QR code generation",
            "Backup codes"
        ],
        "estimated_story_points": 8
    }
})

# Verificar resultado
if result.get('final_decision') == 'success':
    print(f"Pipeline completado")
    print(f"Fases: {result['phases_completed']}")
    print(f"Artifacts: {len(result['all_artifacts'])}")
    print(f"Report: {result['report_path']}")
```

### Ya lo ejecuté antes - Ver resultado

```bash
cat docs/sdlc_outputs/orchestration/SDLC_PIPELINE_REPORT_20251112_033013.md
```

---

## CASO 6: Generar Diagramas UML

**Escenario**: Tienes código y necesitas visualizar la arquitectura.

**¿Cuándo usar?**
- Documentar código existente
- Onboarding de nuevos desarrolladores
- Code reviews arquitectónicos

### Ejemplo: Class Diagram desde Código

```python
from scripts.ai.agents.meta.uml_generator_agent import UMLGeneratorAgent

agent = UMLGeneratorAgent(config=None)

codigo_python = """
class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def login(self):
        pass

class Admin(User):
    def __init__(self, email, password, permissions):
        super().__init__(email, password)
        self.permissions = permissions

    def grant_permission(self, user, permission):
        pass
"""

result = agent.generate_class_diagram(code=codigo_python)

print(f"Success: {result.success}")
print(f"Diagram type: {result.diagram_type}")
print("PlantUML code:")
print(result.plantuml_code)
```

### Ejecutar Ejemplo

```bash
cat > test_uml_case6.py << 'EOF'
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.ai.agents.meta.uml_generator_agent import UMLGeneratorAgent

agent = UMLGeneratorAgent(config=None)

codigo = """
class User:
    def __init__(self, email):
        self.email = email
    def login(self):
        pass

class Admin(User):
    def grant_permission(self):
        pass
"""

result = agent.generate_class_diagram(code=codigo)

print(f"Success: {result.success}")
print(f"Method: {result.generation_method}")
print(f"Classes found: {codigo.count('class ')}")
print("\nPlantUML preview:")
print(result.plantuml_code[:200])
EOF

python3 test_uml_case6.py
```

### Output Esperado

```
Success: True
Method: heuristic
Classes found: 2

PlantUML preview:
@startuml
class User {
  +email
  +__init__(email)
  +login()
}
class Admin {
  +grant_permission()
}
User <|-- Admin
@enduml
```

---

## CASO 7: Comparar Proveedores

**Escenario**: Quieres saber qué proveedor LLM usar para tu caso.

**¿Cuándo usar?**
- Antes de configurar el proyecto
- Para optimizar costos vs calidad
- Cuando evalúas Ollama local vs APIs cloud

### Ya existe el script

```bash
python3 examples/sdlc_compare_providers.py
```

Este compara:
- Heurísticas (gratis, instantáneo)
- Ollama (gratis, requiere instalación)
- Claude (cloud, $0.003/request)
- GPT-4 (cloud, $0.005/request)

---

## Resumen de Casos de Uso

| Caso | Agente | Tiempo | Cuándo Usar |
|------|--------|--------|-------------|
| **Evaluar viabilidad** | FeasibilityAgent | <1s | Antes de empezar |
| **Diseñar arquitectura** | DesignAgent | <2s | Antes de codear |
| **Planear tests** | TestingAgent | <2s | Después de codear |
| **Planear deploy** | DeploymentAgent | <2s | Antes de mergear |
| **Pipeline completo** | Orchestrator | <5s | Features completas |
| **Generar UML** | UMLGeneratorAgent | <1s | Documentar código |
| **Comparar LLMs** | Feasibility+Compare | 5-30s | Setup inicial |

---

## Scripts de Prueba Rápida

Ejecuta todos los casos:

```bash
# Caso 1: Viabilidad
python3 test_feasibility_case1.py

# Caso 2: Diseño
python3 test_design_case2.py

# Caso 3: Testing
python3 test_testing_case3.py

# Caso 4: Deployment
python3 test_deployment_case4.py

# Caso 5: Pipeline completo (ya ejecutado)
python3 examples/sdlc_pipeline_complete.py

# Caso 6: UML
python3 test_uml_case6.py

# Caso 7: Comparar proveedores
python3 examples/sdlc_compare_providers.py
```

---

## Tips por Caso de Uso

### Para Evaluación Rápida (Casos 1, 6)
- Usa heurísticas (config=None)
- Sub-segundo de respuesta
- Suficiente para decisiones simples

### Para Análisis Profundo (Casos 2, 3, 4)
- Usa LLM si disponible
- Mejor identificación de edge cases
- Recomendaciones más contextuales

### Para Auditoría/Documentación (Caso 5)
- Usa pipeline completo
- Genera todos los artifacts
- Mantiene trazabilidad

### Para Comparar Opciones (Caso 7)
- Ejecuta con diferentes configuraciones
- Mide tiempo vs calidad
- Decide basado en necesidades

---

**Última actualización**: 2025-11-12
**Autor**: Sistema SDLC IACT
