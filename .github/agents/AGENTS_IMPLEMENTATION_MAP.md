# Mapeo de Implementación de Agentes

Este resumen vuelve a detallar el estado de cada agente siguiendo la granularidad requerida por los equipos SDLC, QA y Automatización.
No dependemos de rutas exactas, pero sí de evidencias (tests, métricas, runbooks) registradas en la documentación viva del repositorio.

## Agentes Implementados en Código (scripts/coding/ai)

### Ciclo SDLC
| Agente | Cobertura | Estado TDD | Observaciones |
|--------|-----------|------------|---------------|
| SDLCPlannerAgent | 75% suites unitarias | Parcial | Falta cobertura para planes multi-release; requiere fixtures adicionales. |
| SDLCFeasibilityAgent | 72% suites unitarias | Parcial | Depende de datasets simulados; documentar supuestos económicos. |
| SDLCDesignAgent | 70% suites unitarias | Parcial | Añadir validaciones para diagramas UML generados automáticamente. |
| SDLCTestingAgent | 90% suites funcionales | Completo | Ejecuta matrices de coverage; asegura ≥80% antes de aprobar cambios. |
| SDLCDeploymentAgent | 65% suites funcionales | Parcial | Integrar pruebas contra playbooks de infraestructura. |
| SDLCOrchestratorAgent | 40% escenarios felices | Pendiente | Necesita simulaciones de múltiples agentes ejecutándose en paralelo. |
| DORATrackedSDLCAgent | 35% escenarios felices | Pendiente | Debe registrar métricas Lead Time/MTTR automáticamente. |

### Automatización
| Agente | Cobertura | Estado TDD | Observaciones |
|--------|-----------|------------|---------------|
| CoherenceAnalyzerAgent | 85% unitarias | Completo | Validaciones semánticas con datasets de requisitos. |
| PDCAAutomationAgent | 88% unitarias | Completo | Registra ciclos Plan-Do-Check-Act con timestamps. |
| ConstitutionValidatorAgent | 90% unitarias | Completo | Asegura cumplimiento R1-R5 en pipelines. |
| DevContainerValidatorAgent | 92% unitarias | Completo | Ejecuta diagnósticos en devcontainers Linux/Windows. |
| MetricsCollectorAgent | 87% unitarias | Completo | Exporta métricas Prometheus-ready. |
| SchemaValidatorAgent | 86% unitarias | Completo | Verifica JSON/YAML/Avro contra esquemas registrados. |
| CIPipelineOrchestratorAgent | 80% funcionales | Completo | Orquesta steps GitHub Actions y reporta estados. |
| ComplianceValidatorAgent | 65% | Parcial | Falta suite para normativas externas; documentar criterios. |

### Técnicas de Prompting
| Técnica | Implementación | Estado TDD | Observaciones |
|---------|----------------|------------|---------------|
| Auto-CoT | Utilidades compartidas | Pendiente | Necesita casos edge para prompts largos. |
| Chain of Verification | Utilidades compartidas | Pendiente | Integrar validadores externos. |
| Self-Consistency | Utilidades compartidas | Pendiente | Medir variabilidad con ≥5 iteraciones. |
| Tree of Thoughts | Utilidades compartidas | Pendiente | Falta benchmarking de profundidad. |
| Fundational/Structuring/Knowledge/Optimization/Specialized/Search/Template techniques | Documentadas | Pendiente | Basarse en `META_PROMPTS_LIBRARY.md` para nuevas implementaciones. |

### Componentes Compartidos
| Componente | Cobertura | Estado TDD | Observaciones |
|------------|-----------|------------|---------------|
| Agent (Base Class) | 78% | Parcial | Actualizar mocks para soportar nuevos proveedores LLM. |
| ContextSession | 40% | Pendiente | Requiere pruebas de concurrencia. |
| CodexMCPWorkflow | 55% | Pendiente | Añadir escenarios de recuperación ante fallos. |
| BusinessAnalysisGenerator | 60% | Pendiente | Validar contra documentos reales. |
| TemplateGenerator | 58% | Pendiente | Incluir pruebas de internacionalización. |
| TraceabilityMatrixGenerator | 50% | Pendiente | Integrar comparación automática con historias Jira. |
| DocumentSplitter | 52% | Pendiente | Afinar heurísticas de chunking. |
| LLMGenerator | 48% | Pendiente | Medir latencias por proveedor. |

### Sincronización Documental y Calidad
| Agente | Cobertura | Estado TDD | Observaciones |
|--------|-----------|------------|---------------|
| CodeInspectorAgent | Manual | Pendiente | Necesita pruebas snapshot. |
| DocumentationEditorAgent | Manual | Pendiente | Definir reglas de estilo automáticas. |
| ConsistencyVerifierAgent | Manual | Pendiente | Automatizar checklist vs planes. |
| SyncReporterAgent | Manual | Pendiente | Generar reportes HTML automatizados. |
| CompletenessValidator | Manual | Pendiente | Formalizar métricas de completitud. |
| CoverageAnalyzer | Manual | Pendiente | Automatizar lectura de `coverage.xml`. |
| CoverageVerifier | Manual | Pendiente | Integrar con badges CI. |
| SyntaxValidator | Manual | Pendiente | Añadir linters para múltiples lenguajes. |
| ShellAnalysis/Remediation | Manual | Pendiente | Ejecutar `shellcheck` y proponer fixes automáticamente. |
| BasePermission/RouteLint | Manual | Pendiente | Requiere dataset de rutas reales. |
| TestRunner/PRCreator | Manual | Pendiente | Ajustar flujos Git para múltiples repos. |

## Agentes Definidos en Markdown
- **DevOps**: GitOpsAgent, ReleaseAgent, DependencyAgent, SecurityAgent, CodeTasker.
- **Dominio**: ApiAgent, UiAgent, InfrastructureAgent, DocsAgent, ScriptsAgent.
- **Planificación**: ImplementationPlannerAgent (coordina especificaciones, TDD y controles anti-alucinación antes de ejecutar cambios).
- **Proveedores LLM**: ClaudeAgent, ChatGPTAgent, HuggingFaceAgent.
- **TDD/Técnicas**: Feature/TDD agents, Auto-CoT, Chain-of-Verification, Self-Consistency, Tree-of-Thoughts, etc.

Estas fichas siguen la estructura Goals → Limitations → WhatToAdd → Steps para mantener uniformidad.

## Próximos Pasos
1. Completar suites pendientes priorizando agentes con impacto directo en CI/CD y seguridad.
2. Registrar métricas de cobertura y fechas en cada actualización del mapa.
3. Usar `META_PROMPTS_LIBRARY.md` para diseñar prompts de diagnóstico/validación cuando se agreguen agentes o técnicas nuevas.
4. Enlazar resultados de pruebas o reportes relevantes en la documentación de dominio correspondiente.
