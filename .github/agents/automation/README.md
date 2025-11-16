# Agentes de Automatización

Los agentes de automatización coordinan procesos de calidad, CI/CD, validación normativa y recopilación de métricas dentro del proyecto. Este resumen describe sus funciones sin depender de rutas de archivos específicas.

## Catálogo

### CoherenceAnalyzerAgent
- Analiza la coherencia entre código, pruebas y documentación.
- Detecta huecos de cobertura y produce reportes de alineación.
- Recomienda ajustes cuando encuentra divergencias.

### PDCAAutomationAgent
- Automatiza el ciclo Plan-Do-Check-Act con métricas del proyecto.
- Prioriza acciones de mejora y rastrea resultados.
- Documenta aprendizajes para futuras iteraciones.

### ConstitutionValidatorAgent
- Valida salidas de agentes respecto a principios éticos y de seguridad.
- Marca violaciones potenciales y propone mitigaciones.
- Mantiene registros de cumplimiento para auditorías.

### DevContainerValidatorAgent
- Revisa configuraciones de entornos reproducibles.
- Asegura que dependencias y herramientas esenciales estén disponibles.
- Sugiere mejoras de paridad entre entornos locales y CI.

### MetricsCollectorAgent
- Centraliza indicadores de automatización y entrega.
- Alimenta tableros de decisión con métricas relevantes.
- Configura alertas cuando los objetivos se desvían.

### SchemaValidatorAgent
- Controla versiones y compatibilidad de esquemas de datos.
- Advierte sobre cambios disruptivos y coordina su comunicación.
- Promueve planes de despliegue y rollback claros.

### CIPipelineOrchestratorAgent
- Orquesta pipelines de integración continua.
- Mantiene la secuencia de validaciones obligatorias.
- Coordina con QA y DevOps la incorporación de nuevas comprobaciones.

### BusinessRulesValidatorAgent
- Contrasta automatizaciones con reglas de negocio vigentes.
- Detecta excepciones y escenarios sin cobertura.
- Recomienda pruebas adicionales o ajustes de reglas.

## Buenas Prácticas
- Mantener planes de trabajo actualizados para cada automatización.
- Ejecutar pruebas automatizadas tras cada ajuste.
- Registrar evidencias de cumplimiento en los tableros de calidad.

Estos agentes permiten que las automatizaciones evolucionen con control, trazabilidad y métricas accionables.
