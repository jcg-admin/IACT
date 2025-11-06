## Resumen

Este PR implementa agentes especializados para operaciones DevOps y documenta la sincronización de ramas principales del repositorio.

## Cambios principales

### 1. Agentes DevOps creados (4 agentes)

**GitOpsAgent** (.github/agents/gitops-agent.md)
- Sincronización de ramas principales (develop, docs, devcontainer, main)
- Limpieza de ramas obsoletas
- Auditoría de estructura de repositorio
- Arquitectura de 5 fases: ANALYZER, PLANNER, EXECUTOR, VALIDATOR, REPORTER

**ReleaseAgent** (.github/agents/release-agent.md)
- Versionado semántico (SemVer 2.0.0)
- Generación automática de changelogs
- Análisis de Conventional Commits
- Creación y gestión de tags Git
- Actualización de versiones en archivos del proyecto

**DependencyAgent** (.github/agents/dependency-agent.md)
- Actualización de dependencias (3 estrategias: conservadora/moderada/agresiva)
- Escaneo de vulnerabilidades (CVEs)
- Auditoría de licencias
- Validación de compatibilidad con restricciones del proyecto

**SecurityAgent** (.github/agents/security-agent.md)
- Análisis estático de código (Bandit)
- Detección de secrets (gitleaks)
- Análisis de amenazas STRIDE
- Validación de restricciones críticas del proyecto IACT

**Índice de Agentes** (.github/agents/README.md)
- Documentación completa de 5 agentes (incluye CodeTasker existente)
- Guía de uso y mejores prácticas
- Ejemplos de integración con workflows

### 2. Documentación operativa

**Runbook** (docs/devops/runbooks/merge_y_limpieza_ramas.md)
- Procedimiento de sincronización de ramas
- Troubleshooting y comandos de referencia
- Mantenimiento preventivo

**Registros de operaciones** (docs/qa/registros/)
- 2025_11_05_merge_ramas.md: Registro inicial de merge
- 2025_11_05_merge_ramas_gitops.md: Ejecución de GitOpsAgent en producción

### 3. Scripts de automatización

**scripts/cleanup_branches.sh**
- Script interactivo para limpieza de ramas
- Confirmaciones y validaciones de seguridad
- Push de ramas principales

**scripts/complete_sync.sh**
- Completar sincronización de ramas
- Reporte con colores y validación final

### 4. Actualización de documentación

**docs/desarrollo/agentes_automatizacion.md** (v1.1.0 → v1.2.0)
- Agregadas secciones 4, 5, 6 con nuevos agentes
- Integración con procesos existentes
- Sin emojis (cumple restricciones del proyecto)

## Estadísticas

- 11 archivos modificados
- 4,283 líneas agregadas
- 4 commits de features y documentación
- 0 emojis (cumple restricciones)

## Archivos creados

```
.github/agents/README.md (379 líneas)
.github/agents/dependency-agent.md (649 líneas)
.github/agents/gitops-agent.md (345 líneas)
.github/agents/release-agent.md (563 líneas)
.github/agents/security-agent.md (224 líneas)
docs/devops/runbooks/merge_y_limpieza_ramas.md (462 líneas)
docs/qa/registros/2025_11_05_merge_ramas.md (311 líneas)
docs/qa/registros/2025_11_05_merge_ramas_gitops.md (551 líneas)
scripts/cleanup_branches.sh (169 líneas)
scripts/complete_sync.sh (187 líneas)
```

## Próximos pasos

1. Review del código y documentación
2. Ejecutar scripts/complete_sync.sh para completar sincronización (requiere permisos)
3. Eliminar ramas obsoletas (feature/*, claude/* viejas)
4. Verificar estructura final del repositorio (4 ramas principales)

## Testing realizado

- GitOpsAgent ejecutado en producción con éxito
- Sincronización de 3 ramas principales completada localmente
- Scripts validados con shellcheck
- Documentación sin emojis verificada

## Integración con procesos existentes

- docs/gobernanza/procesos/procedimiento_gestion_cambios.md
- docs/gobernanza/procesos/procedimiento_release.md
- docs/gobernanza/procesos/procedimiento_analisis_seguridad.md
