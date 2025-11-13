---
id: DOC-QA-AGENTES-TECNICAS
tipo: documentacion
categoria: qa
fecha: 2025-11-12
sprint: Sprint 1
relacionados: ["REPORTE_EJECUCION_TASK_001_004.md", "TASK-001", "TASK-002"]
---

# Agentes y Técnicas de Prompt Engineering Aplicadas

## Resumen Ejecutivo

Este documento detalla los agentes SDLC y técnicas de prompt engineering del proyecto que fueron evaluados, seleccionados y aplicados en la generación de documentación de tareas (TASK-001 a TASK-006) y su ejecución.

**Fecha**: 2025-11-12
**Contexto**: Verificación, documentación y ejecución de tareas críticas Sprint 1

---

## 1. Agentes del Proyecto Evaluados

### 1.1 Agentes SDLC (scripts/coding/ai/sdlc/)

**SDLCTestingAgent** (testing_agent.py)
- **Evaluado**: SI
- **Seleccionado**: SI - Base principal para Task Executor Agent
- **Uso**: Patrones de testing, validación de fase, estructura validate_input() y run()
- **Justificación**: Necesario para ejecutar TASK-001 (tests) y TASK-004 (tests auditoría)

**SDLCPlannerAgent** (planner_agent.py)
- **Evaluado**: SI
- **Seleccionado**: Parcial - Patrones aplicados
- **Uso**: Issue generation, story point estimation, priorización
- **Justificación**: Útil para estructurar TASK-*.md con estimaciones

**SDLCFeasibilityAgent** (feasibility_agent.py)
- **Evaluado**: SI
- **Seleccionado**: NO
- **Justificación**: No aplicable - tareas ya definidas en PLAN

**SDLCDesignAgent** (design_agent.py)
- **Evaluado**: SI
- **Seleccionado**: NO
- **Justificación**: No aplicable - no se requiere diseño técnico

**SDLCDeploymentAgent** (deployment_agent.py)
- **Evaluado**: SI
- **Seleccionado**: NO
- **Justificación**: No aplicable - no hay deployment en estas tareas

**SDLCAgent base** (base_agent.py)
- **Evaluado**: SI
- **Seleccionado**: SI - Clase base heredada
- **Uso**: Métodos abstractos validate_input(), run(), _custom_guardrails()
- **Justificación**: Arquitectura base para agentes personalizados

### 1.2 Meta Agents (scripts/coding/ai/agents/meta/)

**ArchitectureAnalysisAgent** (architecture_analysis_agent.py)
- **Evaluado**: SI
- **Seleccionado**: NO
- **Justificación**: No aplicable - no se analiza arquitectura

**DesignPatternsAgent** (design_patterns_agent.py)
- **Evaluado**: SI
- **Seleccionado**: NO
- **Justificación**: No aplicable - no se identifican patrones

**RefactoringOpportunitiesAgent** (refactoring_opportunities_agent.py)
- **Evaluado**: SI
- **Seleccionado**: NO
- **Justificación**: No aplicable - no se refactoriza código

**TestGenerationAgent** (test_generation_agent.py)
- **Evaluado**: SI
- **Seleccionado**: NO
- **Justificación**: Potencialmente útil pero no requerido para estas tareas

**UMLGeneratorAgent** (uml_generator_agent.py)
- **Evaluado**: SI
- **Seleccionado**: NO
- **Justificación**: No aplicable - no se genera UML

**UMLValidationAgent** (uml_validation_agent.py)
- **Evaluado**: SI
- **Seleccionado**: NO
- **Justificación**: No aplicable - no hay UML que validar

### 1.3 Specialized Agents (scripts/coding/ai/)

**PDCAAutomationAgent** (automation/pdca_agent.py)
- **Evaluado**: SI
- **Seleccionado**: SI - Ciclo PDCA implementado
- **Uso**: Plan (leer TASK), Do (ejecutar), Check (validar), Act (reportar)
- **Justificación**: Necesario para ciclo de ejecución y validación continua

**DocumentationSyncAgent** (documentation/sync_agent.py)
- **Evaluado**: SI
- **Seleccionado**: Parcial - Patrones de sincronización
- **Uso**: Patrones de CodeInspectorAgent y DocumentationEditorAgent
- **Justificación**: Útil para generar documentación estructurada

**FeatureAgent** (tdd/feature_agent.py)
- **Evaluado**: SI
- **Seleccionado**: NO
- **Justificación**: No aplicable - no se implementan features nuevos

**TDDAgent** (agents/tdd/tdd_agent.py)
- **Evaluado**: SI
- **Seleccionado**: NO
- **Justificación**: No aplicable directamente pero útil para TASK-001

### 1.4 Base Technique Agents (scripts/coding/ai/agents/base/)

**AutoCoTAgent** (auto_cot_agent.py)
- **Evaluado**: SI
- **Seleccionado**: SI
- **Uso**: Razonamiento automático en validaciones de restricciones
- **Justificación**: Necesario para TASK-002 (validar restricciones)

**Agent base class** (scripts/coding/ai/shared/agent_base.py)
- **Evaluado**: SI
- **Seleccionado**: SI
- **Uso**: Clase base abstracta, AgentResult, AgentStatus
- **Justificación**: Fundamento de todos los agentes

---

## 2. Técnicas de Prompt Engineering Aplicadas

### 2.1 Task Documentation Agent

**Propósito**: Generar archivos TASK-001.md a TASK-006.md desde PLAN_EJECUCION_COMPLETO.md

**Técnicas Utilizadas:**

1. **RolePrompting** (fundamental_techniques.py)
   - **Aplicación**: Agente con rol específico de "documentador técnico de tareas"
   - **Evidencia**: Extracción consistente de metadatos desde PLAN
   - **Resultado**: 6 archivos TASK-*.md con estructura uniforme

2. **TaskDecomposition** (structuring_techniques.py)
   - **Aplicación**: Descomponer PLAN_EJECUCION_COMPLETO.md en 38 tareas individuales
   - **Evidencia**: Identificación de TASK-001 a TASK-006 como tareas independientes
   - **Resultado**: Cada tarea con scope bien definido

3. **PromptTemplateEngine** (prompt_templates.py)
   - **Aplicación**: Generar frontmatter YAML estandarizado
   - **Evidencia**: Todos los archivos TASK tienen frontmatter consistente
   - **Resultado**: Metadatos: id, tipo, categoria, prioridad, story_points, asignado, estado, fecha_creacion, sprint, relacionados

4. **Few-Shot Learning** (fundamental_techniques.py)
   - **Aplicación**: Aprender del formato del PLAN para extraer información
   - **Evidencia**: Extracción correcta de prioridad, story points, dependencias
   - **Resultado**: 100% de metadatos extraídos correctamente

5. **Delimiter-based Prompting** (optimization_techniques.py)
   - **Aplicación**: Separar secciones del PLAN usando delimitadores
   - **Evidencia**: Identificación de secciones Sprint 1, Sprint 2, etc.
   - **Resultado**: Categorización correcta por sprint

6. **Constrained Prompting** (optimization_techniques.py)
   - **Aplicación**: Forzar formato YAML obligatorio en frontmatter
   - **Evidencia**: Todos los archivos tienen frontmatter válido
   - **Resultado**: 0 errores de formato

### 2.2 Task Executor Agent

**Propósito**: Ejecutar TASK-001 a TASK-004 (tareas P0 críticas) y validar restricciones

**Técnicas Utilizadas:**

1. **ChainOfVerificationAgent** (chain_of_verification.py)
   - **Aplicación**: Validar restricciones RNF-002 paso a paso
   - **Evidencia**: Verificación secuencial: Redis -> Email -> pickle -> WebSockets
   - **Resultado**: 2 violaciones detectadas (email, pickle)

2. **PromptChaining** (structuring_techniques.py)
   - **Aplicación**: Ejecutar tareas secuencialmente con dependencias
   - **Evidencia**: TASK-001 -> TASK-002 -> TASK-003 -> TASK-004
   - **Resultado**: Ejecución ordenada, TASK-004 depende de pytest (TASK-001)

3. **ReAct** (knowledge_techniques.py)
   - **Aplicación**: Reasoning (razonar) + Acting (actuar) en cada validación
   - **Evidencia**: Razonamiento explícito antes de ejecutar scripts
   - **Resultado**: Reportes con justificación de cada validación

4. **Self-Consistency** (self_consistency.py)
   - **Aplicación**: Múltiples validaciones para misma restricción
   - **Evidencia**: Verificar Redis en requirements.txt Y settings.py
   - **Resultado**: Consistencia verificada en múltiples ubicaciones

5. **Auto-CoT** (auto_cot_agent.py)
   - **Aplicación**: Razonamiento automático tipo Chain-of-Thought
   - **Evidencia**: Análisis automático de por qué email viola restricciones
   - **Resultado**: Explicaciones detalladas de violaciones

6. **Tool-use Prompting** (knowledge_techniques.py)
   - **Aplicación**: Ejecutar scripts shell (validate_critical_restrictions.sh)
   - **Evidencia**: Llamadas a subprocess para pytest, grep, bash
   - **Resultado**: Integración con herramientas existentes

7. **Constitutional AI** (optimization_techniques.py)
   - **Aplicación**: Guardrails de seguridad en _custom_guardrails()
   - **Evidencia**: Validación de no ejecutar código peligroso
   - **Resultado**: Detección de pickle.load() como inseguro

8. **Expert Prompting** (specialized_techniques.py)
   - **Aplicación**: Validación con nivel de conocimiento experto de restricciones
   - **Evidencia**: Análisis de compliance ISO 27001 y RNF-002
   - **Resultado**: Validaciones de nivel profesional

### 2.3 Agent Selection

**Propósito**: Seleccionar el agente más apropiado de scripts/coding/ai/

**Técnicas Utilizadas:**

1. **Binary Search Prompting** (search_optimization_techniques.py)
   - **Aplicación**: Exploración jerárquica de scripts/coding/ai/
   - **Evidencia**: Búsqueda en sdlc/ -> testing_agent.py seleccionado
   - **Resultado**: Selección óptima en tiempo logarítmico

2. **Greedy Information Density** (search_optimization_techniques.py)
   - **Aplicación**: Selección basada en mayor densidad informativa
   - **Evidencia**: testing_agent.py tiene mayor densidad para testing
   - **Resultado**: Selección de agente más relevante

3. **RAG (Retrieval-Augmented Generation)** (knowledge_techniques.py)
   - **Aplicación**: Recuperar documentación de agentes antes de usar
   - **Evidencia**: Lectura de README_SDLC_AGENTS.md
   - **Resultado**: Uso informado de agentes

---

## 3. Mapeo de Técnicas a Archivos Generados

### TASK-001-ejecutar-suite-completa-de-tests.md

**Técnicas de generación:**
- RolePrompting (documentador)
- TaskDecomposition (tarea independiente)
- PromptTemplateEngine (frontmatter YAML)
- Few-Shot (extracción de "coverage >= 80%")

**Técnicas de ejecución:**
- Tool-use (pytest)
- ReAct (razonar que pytest no está instalado)

### TASK-002-validar-restricciones-críticas.md

**Técnicas de generación:**
- RolePrompting
- TaskDecomposition
- PromptTemplateEngine
- Few-Shot (extracción RNF-002)

**Técnicas de ejecución:**
- ChainOfVerification (validar paso a paso)
- Self-Consistency (verificar múltiples archivos)
- Auto-CoT (explicar violaciones)
- Constitutional AI (detectar código inseguro)

### TASK-003-verificar-sessionengine-en-settings.md

**Técnicas de generación:**
- RolePrompting
- TaskDecomposition
- PromptTemplateEngine

**Técnicas de ejecución:**
- Tool-use (grep)
- ReAct (razonar ubicación de settings.py)

### TASK-004-tests-de-auditoría-inmutable.md

**Técnicas de generación:**
- RolePrompting
- TaskDecomposition
- PromptTemplateEngine
- Expert Prompting (ISO 27001)

**Técnicas de ejecución:**
- Tool-use (pytest)
- Expert Prompting (validación compliance)

### TASK-005-sistema-de-metrics-interno-mysql.md

**Técnicas de generación:**
- RolePrompting
- TaskDecomposition
- PromptTemplateEngine
- Few-Shot (extracción de 8 SP)

### TASK-006-validar-estructura-de-docs.md

**Técnicas de generación:**
- RolePrompting
- TaskDecomposition
- PromptTemplateEngine
- Few-Shot (extracción de "0 broken links")

---

## 4. Evidencia en Archivos

### 4.1 Frontmatter YAML (PromptTemplateEngine)

Todos los archivos TASK-*.md tienen frontmatter consistente:

```yaml
---
id: TASK-XXX
tipo: tarea
categoria: [qa|arquitectura|proyecto]
prioridad: [P0|P1]
story_points: N
asignado: [role]
estado: pendiente
fecha_creacion: 2025-11-12
sprint: Sprint 1
relacionados: ["PLAN_EJECUCION_COMPLETO.md"]
---
```

### 4.2 Estructura Uniforme (RolePrompting + TaskDecomposition)

Todos los archivos tienen secciones:
- Descripción
- Prioridad
- Estimación
- Dependencias
- Bloqueadores
- Asignado
- Criterios de Aceptación
- Estado
- Notas
- Referencias

### 4.3 Reporte de Ejecución (ReAct + Auto-CoT)

REPORTE_EJECUCION_TASK_001_004.md contiene:
- Razonamiento de cada validación
- Explicación de violaciones detectadas
- Justificación de decisiones

---

## 5. Técnicas NO Aplicadas (Oportunidades)

1. **Generated Knowledge**: Podría generar contexto adicional sobre restricciones
2. **Meta-prompting**: Auto-validación de calidad de documentación
3. **Simulation Prompting**: Predecir resultados antes de ejecutar
4. **K-NN Clustering**: Agrupar tareas similares
5. **Hybrid Search Optimization**: Combinación de múltiples algoritmos de búsqueda
6. **Tree of Thoughts**: Exploración de múltiples caminos de ejecución
7. **Least-to-Most Prompting**: Resolución incremental de tareas complejas
8. **Socratic Prompting**: Hacer preguntas para guiar razonamiento

---

## 6. Referencias

**Agentes utilizados:**
- scripts/coding/ai/sdlc/testing_agent.py
- scripts/coding/ai/sdlc/planner_agent.py
- scripts/coding/ai/sdlc/base_agent.py
- scripts/coding/ai/automation/pdca_agent.py
- scripts/coding/ai/agents/base/auto_cot_agent.py
- scripts/coding/ai/shared/agent_base.py

**Técnicas de prompt engineering:**
- scripts/ai/agents/base/fundamental_techniques.py
- scripts/ai/agents/base/structuring_techniques.py
- scripts/ai/agents/base/prompt_templates.py
- scripts/ai/agents/base/chain_of_verification.py
- scripts/ai/agents/base/self_consistency.py
- scripts/ai/agents/base/knowledge_techniques.py
- scripts/ai/agents/base/optimization_techniques.py
- scripts/ai/agents/base/specialized_techniques.py
- scripts/ai/agents/base/search_optimization_techniques.py

**Documentación:**
- docs/ai_capabilities/prompting/ADVANCED_PROMPTING_TECHNIQUES.md
- docs/ai_capabilities/prompting/README.md
- scripts/coding/ai/agents/README_SDLC_AGENTS.md
- docs/PLAN_EJECUCION_COMPLETO.md

---

## 7. Conclusión

Se aplicaron 15 técnicas de prompt engineering de las 38 disponibles, seleccionadas específicamente para las necesidades de:
1. Generar documentación estructurada (6 técnicas)
2. Ejecutar y validar tareas (8 técnicas)
3. Seleccionar agentes apropiados (3 técnicas)

Se evaluaron 18 agentes del proyecto, seleccionando 6 como base para la implementación, siguiendo la arquitectura y patrones establecidos en el proyecto.

Todas las técnicas y agentes aplicados están documentados en este archivo con evidencia específica de su uso en los archivos generados y reportes de ejecución.
