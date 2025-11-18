# Análisis de Estructura y Plan de Reorganización - Infraestructura

## 1. Contexto y objetivos
- Homogeneizar `docs/infraestructura/` con la estructura y convenciones usadas en `docs/gobernanza/`, incluyendo navegación (README/INDEX), plantillas QA y trazabilidad de decisiones.
- Atender el gap reportado: falta de una carpeta y plan QA visible que consolide acciones y responsables específicos para infraestructura.
- Asegurar que toda nueva automatización o runbook siga TDD (tests antes del código) y cobertura mínima del 80 %.

## 2. Situación actual
- README/INDEX de Infraestructura ya incorporan navegación básica y el dominio de DevOps, pero la carpeta `qa/` sólo contiene un placeholder y no refleja el modelo de Gobernanza.
- No existe un inventario de análisis estructurales ni plan de reorganización dedicado a infraestructura.
- Varios directorios heredados (p. ej., `checklists/`, `procedimientos/`, `plan/`) carecen de plantillas de QA consistentes con Gobernanza (estados, métricas, responsables).

## 3. Plan de acción
### 3.1 Inventario y brechas
- Levantar inventario de directorios y archivos de `docs/infraestructura/` (profundidad ≤2) y compararlo con `docs/gobernanza/` para identificar faltantes en QA, procedimientos y trazabilidad.
- Documentar hallazgos en `qa/QA-ANALISIS-ESTRUCTURA-INFRA-001/` con métricas (conteo de README/INDEX, profundidad máxima, archivos sin categoría).

### 3.2 Normalización de navegación y plantillas
- Replicar en `docs/infraestructura/README.md` y `INDEX.md` las secciones de página padre/hijas, estado de cumplimiento y acciones priorizadas siguiendo el modelo de Gobernanza.
- Crear o actualizar plantillas de QA por dominio (provisión, hardening, observabilidad, continuidad) con frontmatter consistente y checklists claros.
- Incorporar referencias a ADRs relevantes cuando haya cambios de arquitectura o plataforma.

### 3.3 Fortalecimiento de QA y trazabilidad
- Establecer en `qa/` subcarpetas específicas por análisis (p. ej., `QA-ANALISIS-*`) para registrar inspecciones, métricas y reportes, siguiendo la estructura de Gobernanza.
- Conectar `tareas_activas.md` con los nuevos planes, agregando IDs, responsables, SP y fechas objetivo para cada acción de reorganización.
- Definir validaciones automáticas post-cambio: builds de docs y suites de pruebas asociadas a scripts de infraestructura.

### 3.4 Gobernanza de cambios
- Aplicar commits convencionales para toda actualización de docs/infraestructura y scripts relacionados (`docs`, `ci`, `chore`).
- Para nuevas automatizaciones, redactar casos de prueba antes de los cambios (ciclo Red → Green → Refactor) y exigir cobertura ≥80 %.
- Registrar decisiones clave en ADRs cuando se elijan nuevas herramientas de IaC, pipelines o estándares de seguridad.

## 4. Entregables y responsables
| Entregable | Ruta | Responsable sugerido | Fecha objetivo |
|------------|------|----------------------|----------------|
| Inventario y métricas iniciales | `qa/QA-ANALISIS-ESTRUCTURA-INFRA-001/` | @arquitecto-senior | 2025-11-20 |
| README/INDEX alineados a Gobernanza (infra) | `docs/infraestructura/README.md`, `docs/infraestructura/INDEX.md` | @tech-writer | 2025-11-21 |
| Plantillas QA por dominio (provisión, hardening, observabilidad) | `docs/infraestructura/qa/` | @qa-lead | 2025-11-22 |
| Checklists operativos y runbooks | `docs/infraestructura/checklists/`, `docs/infraestructura/devops/` | @devops-lead | 2025-11-25 |
| Validaciones automáticas y cobertura | `scripts/` y pipelines asociados | @devops-lead | 2025-11-26 |

## 5. Riesgos y supuestos
- **Riesgo:** Falta de responsables asignados puede retrasar la normalización de QA. **Mitigación:** definir owners en `tareas_activas.md` y revisarlos semanalmente.
- **Riesgo:** Inconsistencias de naming entre carpetas nuevas y existentes. **Mitigación:** usar snake_case y enlaces relativos validados con builds de docs.
- **Supuesto:** Las prácticas de Gobernanza son la referencia obligatoria para navegación y plantillas.

## 6. Checklist de arranque
- [ ] Confirmar lista de directorios y archivos sin README/INDEX.
- [ ] Registrar métricas de estructura en este análisis con fecha y responsable.
- [ ] Agregar las tareas del plan a `tareas_activas.md` con prioridad y SP.
- [ ] Definir pipeline de validación de documentación (comando de build y lint).
- [ ] Programar revisión de avance semanal hasta completar los entregables.
