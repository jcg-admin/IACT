# Regla de Negocio: Clasificacion de Tipos de Artefactos

## Metadatos
- Codigo: RN-001
- Tipo: Restriccion
- Fuente: GUIA_UBICACIONES_ARTEFACTOS.md, ADR-010
- Estado: Aprobado
- Fecha: 2025-11-16
- Owner: equipo-ba

## Descripcion

El sistema DEBE clasificar cada artefacto en uno de los tipos canonicos definidos. La clasificacion se realiza mediante analisis del nombre del archivo y patron de contenido.

### Tipos Canonicos Soportados

1. **task** - Tareas de desarrollo (TASK-NNN-descripcion.md)
2. **adr** - Architecture Decision Records (ADR-NNN-titulo.md)
3. **solicitud** - Solicitudes de cambio (REQ-NNN-descripcion.md)
4. **analisis** - Analisis documentales (ANALISIS_TEMA_YYYYMMDD.md)
5. **reporte_limpieza** - Reportes de cleanup (CLEANUP_REPORT_YYYYMMDD.md)
6. **sesion** - Sesiones de trabajo (SESSION_TEMA_YYYY_MM_DD.md)
7. **documentacion_agente** - Docs de agentes (README_AGENT_NAME.md)
8. **configuracion_agente** - Configs de agentes (agent_config.json)
9. **guia** - Guias de procedimientos (GUIA_TEMA.md)
10. **indice** - Indices de directorios (INDEX.md)
11. **script** - Scripts de automatizacion (action_object.ext)
12. **procedimiento** - Procedimientos operativos (PROC-NNN-nombre.md)
13. **diseno_detallado** - Documentos de diseño (HLD/LLD)
14. **diagrama** - Diagramas arquitectonicos (.mermaid, .puml)
15. **plan_testing** - Planes de pruebas (TEST_PLAN_*.md)
16. **registro_qa** - Registros de calidad (QA_LOG_*.md)
17. **pipeline_ci_cd** - Pipelines CI/CD (.github/workflows/*.yml)
18. **script_devops** - Scripts DevOps (deploy_*.sh, backup_*.sh)
19. **plantilla** - Plantillas de documentos (template_*.md)

### Algoritmo de Deteccion

#### Fase 1: Deteccion por Patron de Nombre

```
SI nombre empieza con "TASK-" ENTONCES tipo = "task"
SI nombre empieza con "ADR-" ENTONCES tipo = "adr"
SI nombre empieza con "REQ-" ENTONCES tipo = "solicitud"
SI nombre empieza con "ANALISIS_" ENTONCES tipo = "analisis"
SI nombre empieza con "CLEANUP_REPORT_" ENTONCES tipo = "reporte_limpieza"
SI nombre empieza con "SESSION_" ENTONCES tipo = "sesion"
SI nombre empieza con "README_" Y contiene "AGENT" ENTONCES tipo = "documentacion_agente"
SI nombre empieza con "GUIA_" ENTONCES tipo = "guia"
SI nombre == "INDEX.md" ENTONCES tipo = "indice"
SI nombre empieza con "PROC-" ENTONCES tipo = "procedimiento"
SI nombre empieza con "TEST_PLAN_" ENTONCES tipo = "plan_testing"
SI nombre empieza con "template_" ENTONCES tipo = "plantilla"
```

#### Fase 2: Deteccion por Patron de Contenido

```
SI contenido contiene "## Sub-Agentes" Y "## Arquitectura" ENTONCES tipo = "documentacion_agente"
SI contenido contiene "## Decision" Y "## Status" ENTONCES tipo = "adr"
SI contenido contiene "## Analisis de" Y "## Hallazgos" ENTONCES tipo = "analisis"
SI contenido contiene "## Casos de Prueba" Y "## Cobertura" ENTONCES tipo = "plan_testing"
```

#### Fase 3: Fallback

```
SI no se detecta tipo ENTONCES tipo = "documento_general"
```

## Impacto en Requisitos

- **RF-001**: Detectar tipo de artefacto desde nombre y contenido
- **RF-003**: Construir ubicacion canonica basada en tipo
- **RF-004**: Generar nombre estandarizado segun tipo
- **RF-005**: Generar frontmatter YAML apropiado por tipo

## Evidencia

- GUIA_UBICACIONES_ARTEFACTOS.md (seccion "Mapa de Artefactos")
- ADR-010 (Arquitectura por Dominios) - define estructura de directorios
- Auditoria nov 2025 - cataloga 19 tipos distintos de artefactos

## Observaciones

- Nuevos tipos de artefactos pueden agregarse en futuras versiones
- Si tipo no puede detectarse con confianza ≥ 0.6, se solicita clarificacion humana
- El tipo "documento_general" es un fallback, no debe usarse en produccion
