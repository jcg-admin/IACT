# Mapeo de Implementación de Agentes

Este resumen agrupa los agentes definidos en el repositorio y describe su estado de implementación. No se hace referencia a archivos específicos para evitar inconsistencias cuando la estructura del proyecto cambie.

## Agentes Implementados en Código

### Ciclo SDLC

| Agente | Cobertura de Tests | Estado TDD |
|--------|--------------------|------------|
| SDLCPlannerAgent | Escenarios críticos cubiertos parcialmente | Parcial |
| SDLCFeasibilityAgent | Escenarios críticos cubiertos parcialmente | Parcial |
| SDLCDesignAgent | Escenarios críticos cubiertos parcialmente | Parcial |
| SDLCTestingAgent | Suites funcionales completas | Completo |
| SDLCDeploymentAgent | Suites funcionales parciales | Parcial |
| SDLCOrchestratorAgent | Sin suites dedicadas | Pendiente |
| DORATrackedSDLCAgent | Sin suites dedicadas | Pendiente |
| SDLCAgent (Base) | Reutilizado por agentes derivados | Base |

### Automatización

| Agente | Cobertura de Tests | Estado TDD |
|--------|--------------------|------------|
| CoherenceAnalyzerAgent | Suites unitarias completas | Completo |
| PDCAAutomationAgent | Suites unitarias completas | Completo |
| ConstitutionValidatorAgent | Suites unitarias completas | Completo |
| DevContainerValidatorAgent | Suites unitarias completas | Completo |
| MetricsCollectorAgent | Suites unitarias completas | Completo |
| SchemaValidatorAgent | Suites unitarias completas | Completo |
| CIPipelineOrchestratorAgent | Suites unitarias completas | Completo |

### Técnicas de Prompting

| Técnica | Implementación | Estado TDD |
|---------|----------------|------------|
| Auto-CoT | Utilidades base disponibles | Pendiente |
| Chain of Verification | Utilidades base disponibles | Pendiente |
| Self-Consistency | Utilidades base disponibles | Pendiente |
| Tree of Thoughts | Utilidades base disponibles | Pendiente |
| Fundamental Techniques | Utilidades base disponibles | Pendiente |
| Structuring Techniques | Utilidades base disponibles | Pendiente |
| Knowledge Techniques | Utilidades base disponibles | Pendiente |
| Optimization Techniques | Utilidades base disponibles | Pendiente |
| Specialized Techniques | Utilidades base disponibles | Pendiente |
| Search Optimization | Utilidades base disponibles | Pendiente |
| Prompt Templates | Utilidades base disponibles | Pendiente |

### Componentes Compartidos

| Componente | Cobertura de Tests | Estado TDD |
|------------|--------------------|------------|
| Agent (Base Class) | Validado en escenarios clave | Parcial |
| ContextSession | Sin suites dedicadas | Pendiente |

### Orquestación y Generación

| Componente | Cobertura de Tests | Estado TDD |
|------------|--------------------|------------|
| CodexMCPWorkflow | Utilidad de orquestación sin suites completas | Pendiente |
| BusinessAnalysisGenerator | Utilidad de negocio sin suites completas | Pendiente |
| TemplateGenerator | Utilidad de plantillas sin suites completas | Pendiente |
| TraceabilityMatrixGenerator | Utilidad de trazabilidad sin suites completas | Pendiente |
| DocumentSplitter | Utilidad documental sin suites completas | Pendiente |
| LLMGenerator | Utilidad multi-LLM sin suites completas | Pendiente |

### Sincronización de Documentación

| Agente | Cobertura de Tests | Estado TDD |
|--------|--------------------|------------|
| CodeInspectorAgent | Validación manual | Pendiente |
| DocumentationEditorAgent | Validación manual | Pendiente |
| ConsistencyVerifierAgent | Validación manual | Pendiente |
| SyncReporterAgent | Validación manual | Pendiente |

### Calidad Automatizada

| Agente | Cobertura de Tests | Estado TDD |
|--------|--------------------|------------|
| CompletenessValidator | Validación manual | Pendiente |
| CoverageAnalyzer | Validación manual | Pendiente |
| CoverageVerifier | Validación manual | Pendiente |
| SyntaxValidator | Validación manual | Pendiente |

### Entregas Compartidas

| Agente | Cobertura de Tests | Estado TDD |
|--------|--------------------|------------|
| TestRunner | Validación manual | Pendiente |
| PRCreator | Validación manual | Pendiente |

### Permisos

| Agente | Cobertura de Tests | Estado TDD |
|--------|--------------------|------------|
| BasePermissionAgent | Validación manual | Base |
| RouteLintAgent | Validación manual | Pendiente |

## Agentes Definidos en Markdown

Los siguientes agentes se exponen principalmente mediante documentación y prompts. Su implementación depende del ecosistema multi-agente y no del código fuente.

### DevOps y Operaciones
- GitOpsAgent
- ReleaseAgent
- DependencyAgent
- SecurityAgent
- CodeTasker

### Dominio y Plataforma
- ApiAgent
- UiAgent
- InfrastructureAgent
- DocsAgent
- ScriptsAgent

### Proveedores LLM
- ClaudeAgent
- ChatGPTAgent
- HuggingFaceAgent

## Próximos Pasos Sugeridos

1. Priorizar suites automáticas para los agentes SDLC con estado parcial o pendiente.
2. Completar pruebas de los componentes compartidos y las utilidades de orquestación multi-agente.
3. Definir criterios de aceptación para los agentes documentales y de calidad que aún dependen de validaciones manuales.
4. Actualizar periódicamente este mapa para reflejar avances sin necesidad de referenciar rutas específicas dentro del repositorio.
