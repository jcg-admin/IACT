# Plan de remediación de trazabilidad SDLC — Proyecto IACT

## 1. ¿Es necesario seguir el Plan Oficial tal cual? ¿Qué alternativas hay?
- **Recomendación**: seguir el *Plan Oficial de Implementación SDLC — Proyecto IACT* como línea base, porque ya define artefactos, rutas verticales/horizontales y gobernanza normativa. Reducirlo implicaría mantener brechas críticas (RTM corrupto, plantillas sin trazabilidad, APIs sin metadatos) y volvería a incumplir las reglas de la sección 3.3 del plan oficial.
- **Alternativa A (parcial, solo parches)**: corregir la matriz RTM existente y completar plantillas actuales sin crear el repositorio `docs/trazabilidad/` ni los nuevos artefactos (TRZ-001, RTM-IACT). **No recomendada**: no resolvería los controles de CI/CD ni la trazabilidad descendente hacia código y evidencia.
- **Alternativa B (incremental sobre el plan oficial)**: implementar el plan oficial en tres oleadas (documental → operacional → evidencia), priorizando artefactos mínimos viables. **Recomendada**: permite cerrar brechas rápido sin bloquear el desarrollo y deja un camino claro para CI/CD y auditoría.

## 2. Objetivos
1. Restablecer trazabilidad vertical obligatoria (`RNF → RF → UC → UML → API → Código → Tests → Evidencia`).
2. Restablecer trazabilidad horizontal (`UC ↔ BR`, `UC ↔ ADR`, `ADR ↔ Diseño/Código`, `RF ↔ API/Tests`).
3. Normalizar plantillas y gemas con campos de trazabilidad obligatorios.
4. Asegurar que CI/CD rechace artefactos sin referencias y valide actualizaciones de RTM.
5. Preparar auditoría mensual y por release conforme al punto 11 del plan oficial.
6. Completar la automatización de validación, reporte y rollback para que el cambio sea reversible y visible.

## 3. Alcance
Aplica a todos los dominios definidos en el Plan Oficial: Backend (Django REST), Frontend (React/Webpack), Infraestructura/DevOps, Documentación/Gobernanza, Scripts, QA/Testing, Reglas de Negocio, Casos de Uso/UML y ADRs.

## 4. Estrategia (en oleadas)
1. **Oleada 1 — Estabilización documental (Semana 1)**
   - Crear repositorio oficial `docs/trazabilidad/` con estructura del punto 9.
   - Generar `TRZ-001-estandar-sdlc.md` y `RTM.md` inicial (RTM-IACT) reemplazando la matriz corrupta de `docs/gobernanza`.
   - Actualizar plantillas v2 (`UC_v2.md`, `ADR_v2.md`, `TEST_v2.md`, `GOB_v2.md`, `BR_v2.md`) con campos de trazabilidad upward/downward.
   - Registrar política `GOB-TRZ-001` y calendario de auditoría.

2. **Oleada 2 — Integración operativa (Semanas 2-3)**
   - Modificar gemas del proyecto para incluir el bloque obligatorio de trazabilidad (punto 6).
   - Integrar validaciones en CI/CD (punto 7):
     - Verificar referencias a UC/RF/ADR en PRs.
     - Validar actualizaciones en `docs/trazabilidad/RTM.md`.
     - Ejecutar linters de plantillas UC/ADR/TEST.
   - Integrar metadatos de trazabilidad en API con `@extend_schema` (punto 8) y refrescar documentación de drf-spectacular.

3. **Oleada 3 — Evidencia y auditoría (Semanas 3-4)**
   - Completar RTM con enlaces a código, tests y evidencia ejecutada.
   - Activar auditoría mensual y por release (punto 11) y registrar hallazgos en `docs/trazabilidad/registros/`.
   - Incorporar reportes automáticos de cobertura y evidencia de pruebas.

### 4.1 Detalle técnico de CI/CD (aplica a oleadas 2 y 3)
- **Workflows** (`.github/workflows/trazabilidad.yml`):
  - Job `lint-trazabilidad` (warning semana 2 → blocking semana 3):
    - Ejecuta `scripts/trazabilidad/validar_plantillas.py --paths docs/trazabilidad/plantillas`.
    - Regex obligatoria en PR: referencias `UC-\d+`, `RF-\d+`, `ADR-\d+`, `BR-\d+` en commits y PR body.
    - Verifica que los archivos `RTM.md` y plantillas modificadas pasen `yamllint`/`markdownlint` con reglas extendidas de trazabilidad.
  - Job `rtm-drift-check` (blocking):
    - Usa `scripts/trazabilidad/validar_rtm.py --rtm docs/trazabilidad/RTM.md --codigo api backend ui scripts`.
    - Falla si hay referencias huérfanas o si la cobertura < 90%.
  - Job `api-metadata-check` (blocking):
    - Ejecuta `pytest api --maxfail=1 -q -k "extend_schema"` para asegurar metadatos.
    - Verifica que cada endpoint nuevo incluya campos `uc_refs`, `rf_refs`, `adr_refs` en el decorador `@extend_schema`.
- **Condiciones de bloqueo**: `lint-trazabilidad` en warning durante semana 2, se cambia a blocking en semana 3 mediante variable `TRZ_VALIDATION_MODE=blocking`.

## 5. Backlog detallado
- **B1. Crear repositorio de trazabilidad** (`docs/trazabilidad/` con subcarpetas `plantillas/` y `registros/`). Entregable: estructura mínima y README.
- **B2. Publicar TRZ-001** (estándar SDLC) con reglas, identificadores y ciclo de vida de artefactos.
- **B3. Publicar RTM-IACT** (Matriz oficial) con campos completos y datos heredados limpios.
- **B4. Actualizar plantillas v2** (UC, ADR, TEST, GOB, BR) con bloques de trazabilidad y ejemplos.
- **B5. Migrar matrices anteriores** desde `docs/gobernanza/trazabilidad` a `docs/trazabilidad/RTM.md` y marcar deprecated las versiones corruptas.
- **B6. Integrar trazabilidad en gemas** (bloque obligatorio en cada Gem).
- **B7. Integrar controles CI/CD** para validar referencias y RTM.
- **B8. Integrar metadatos de API** (`@extend_schema` con UC/RF/ADR) y actualizar schema.
- **B9. Activar auditorías** y registro en `registros/` (mensual y por release).

## 5.1 Cómo dividir el backlog en *n* tareas (técnica de prompt)
- **Propósito**: descomponer cualquier iniciativa de trazabilidad en *n* tareas concretas, aplicables en issues o PRs, asegurando cobertura vertical y horizontal.
- **Prompt base**: "Divide la iniciativa `<objetivo>` en `<n>` tareas, garantizando trazabilidad vertical RN→RF→UC→UML→ADR→Código→API→Tests→Evidencia y referencias horizontales (UC↔BR, UC↔ADR, RF↔API/Tests). Para cada tarea incluye: alcance, artefactos de entrada/salida, plantillas v2 a usar, matrices afectadas y validaciones de CI/CD requeridas".
- **Validación**: cada tarea debe:
  - Referenciar explícitamente artefactos origen (UC/RF/ADR/BR) y destino (código/tests/evidencia).
  - Indicar en qué matriz se reflejará el cambio (`RTM-IACT`, `M_*` correspondientes) y qué plantilla v2 aplica.
  - Incluir criterios de *Definition of Done* con prueba/linters y actualización de RTM.

### 5.2 Contenido mínimo de plantillas v2 y gemas
- **UC_v2.md**: campos `id`, `titulo`, `actores`, `precondiciones`, `flujo_basico`, `flujos_alternos`, `trazabilidad_upward (RN/RF/BR)`, `trazabilidad_downward (UML/API/Tests)`, `riesgos`, `evidencia`.
- **ADR_v2.md**: `id`, `estatus`, `contexto`, `decisión`, `alternativas`, `trazabilidad_upward (UC/UML)`, `trazabilidad_downward (Código/Tests/API)`, `fecha`, `responsable`.
- **TEST_v2.md**: `id`, `tipo`, `ambiente`, `datos_prueba`, `pasos`, `resultado_esperado`, `trazabilidad_upward (API/UC/RF)`, `trazabilidad_downward (Evidencia/Código)`, `resultado`.
- **GOB_v2.md / BR_v2.md**: incluyen `trazabilidad_upward` hacia políticas/regulaciones y `trazabilidad_downward` hacia UC/RF.
- **Gemas**: bloque obligatorio YAML/JSON `trazabilidad` con arrays `uc_refs`, `rf_refs`, `adr_refs`, `tests_refs`; validado por `scripts/trazabilidad/validar_gemas.py`.

## 6. Criterios de aceptación
- RTM-IACT sin campos vacíos y con enlaces bidireccionales a requisitos, código, tests y evidencia.
- Todas las plantillas vigentes incluyen campos `trazabilidad_upward` y `trazabilidad_downward` completos.
- CI/CD falla cuando falta referencia a UC/RF/ADR o no se actualiza RTM.
- Documentación de API incluye referencias de trazabilidad en `extend_schema`.
- Primer ciclo de auditoría registrado con hallazgos y acciones.

## 7. Riesgos y mitigaciones
- **Datos heredados incompletos**: priorizar migración con prioridad en requisitos críticos; marcar explícitamente huecos en RTM.
- **Resistencia al cambio**: proveer guía rápida en `docs/trazabilidad/TRZ-001` y checklist en PRs.
- **Sobrecarga en CI/CD**: habilitar validaciones en modo warning durante la transición (semana 2) y endurecer a blocking en semana 3.

## 8. Gobernanza y responsables
- **Owner del plan**: Equipo de Gobernanza/QA.
- **Responsables por dominio**: Tech Leads de Backend, Frontend, Infraestructura y Documentación.
- **Aprobación**: Comité de Arquitectura (ADRs) y QA para cierre de cada oleada.

## 9. Métricas de éxito
- Cobertura de trazabilidad vertical ≥ 90% en RTM.
- 0 PRs aceptados sin referencias a UC/RF/ADR tras semana 3.
- 100% de APIs nuevas con `extend_schema` incluyendo referencias.
- Auditorías mensuales sin hallazgos críticos a partir del segundo ciclo.

## 10. Integración del procedimiento PROC-IACT-TRZ (v1.1)
Esta sección incorpora el canvas normativo-operativo *PROC-IACT-TRZ-Procedimiento-Trazabilidad* dentro del plan de remediación.

### 10.1 Encabezado normativo y propósito
- **Código:** PROC-IACT-TRZ-Procedimiento-Trazabilidad — versión 1.1 (estado canvas editable, clasificación Normativo/Operativo).
- **Dominio:** SDLC / Gobernanza / Trazabilidad. **Responsable:** [EDITABLE]. **Última revisión:** [YYYY-MM-DD].
- **Propósito:** guía normativa y operativa para la GEM "IACT-SDLC-TRZ"; base para validadores automáticos, checklists y auditorías; referencia formal de cumplimiento.
- **Reglas de uso GEM:** guiar al usuario en fases 10.1→10.10; validar entradas/salidas; impedir avance si falta fase previa; detectar artefactos faltantes/huérfanos.

### 10.2 Alcance y cadena estructural
Aplica a todo el SDLC y cubre: **RN, RF, UC, UML, ADR, Código, API, Pruebas, Evidencia, Revisión final de QA**. Cadena obligatoria:

```
RN → RF → UC → UML → ADR → Código → API → Pruebas → Evidencia → Revisión Final de QA
```

### 10.3 Principios operativos obligatorios
- **Secuencialidad 10.1→10.10** sin saltos ni reordenamientos.
- **Control estricto de entradas/salidas** y bloqueo si faltan elementos.
- **Prevención de omisiones**: identificar faltantes, ubicación esperada y corrección antes de avanzar.
- **Trazabilidad bidireccional** (directa e inversa) y **prohibición de artefactos huérfanos**.
- **Consistencia en matrices**: identificadores correctos, sin duplicados, relaciones mínimas cumplidas.
- **Condiciones de cierre por fase**: salidas completas, matriz actualizada, entradas de la fase siguiente listas.

### 10.4 Procedimiento por fases (resumen aplicable al backlog)
- **Fase 10.1 — RN:** identificar RN (BR-XXX), validar unicidad y fuentes; actualizar `M_RN`.
- **Fase 10.2 — RF:** derivar RF‑XXX desde RN, establecer RN→RF, actualizar `M_RF` y `M_RN_RF`.
- **Fase 10.3 — UC:** crear UC‑XXX para RF con interacción, establecer RF→UC, actualizar `M_UC` y `M_RF_UC`.
- **Fase 10.4 — UML:** generar UML‑XXX derivados de UC, establecer UC→UML, actualizar `M_UML` y `M_UC_UML`.
- **Fase 10.5 — ADR:** registrar ADR‑XXX basados en UML, establecer UML→ADR, actualizar `M_ADR` y `M_UML_ADR`.
- **Fase 10.6 — Código:** implementar referenciando UC/UML/ADR, establecer ADR→Código, actualizar `M_CODE` y `M_ADR_CODE`.
- **Fase 10.7 — API:** documentar endpoints, establecer Código→API, actualizar `M_API` y `M_CODE_API`.
- **Fase 10.8 — Pruebas:** diseñar TC‑XXX, establecer API→Test, actualizar `M_TEST` y `M_API_TEST`.
- **Fase 10.9 — Evidencia:** registrar evidencias y Test→Evidencia, actualizar `M_EVID` y `M_TEST_EVID`.
- **Fase 10.10 — Revisión final QA:** requiere todas las matrices principales y relacionales completas; valida cierre del ciclo y autoriza liberación.

### 10.4.1 Plan de migración de datos heredados
- **Inventario inicial (día 1-2)**: exportar matrices actuales (`docs/gobernanza/trazabilidad/*`) y clasificarlas por criticidad (CRIT/MAJ/MIN).
- **Limpieza asistida (día 3-4)**: script `scripts/trazabilidad/etl_rtm.py`:
  - Normaliza IDs y detecta duplicados/huérfanos.
  - Marca huecos con etiqueta `PENDING` y `responsable`.
  - Genera reporte CSV para revisión manual.
- **Carga a RTM-IACT (día 5)**: importar CSV limpio a `docs/trazabilidad/RTM.md`.
- **Validación cruzada (día 6)**: ejecutar `validar_rtm.py` + muestreo manual 10% de entradas CRIT.
- **Cierre (día 7)**: aprobar migración, archivar matrices antiguas como deprecated.

### 10.5 Reglas de gobernanza adicionales
- **Completitud por fase**: no cerrar sin salidas obligatorias, matriz actualizada y validación formal.
- **Prohibición de iniciar sin entradas mínimas** y **control de artefactos huérfanos** (origen y destino identificables).
- **Trazabilidad continua y verificable**: matrices reflejan cambios y versiones; controles de versión del procedimiento con revisión trimestral.
- **Versionado**: mantener historial (ejemplo tabla 1.0 y 1.1) sin sobrescritura; toda modificación registrada con fecha y responsable.

### 10.6 Campos editables de operación
- Proyecto, versión de sistema, módulo o área, fecha de elaboración.
- Responsables: Trazabilidad, QA, Arquitectura, Desarrollo.
- Observaciones libres para decisiones, riesgos o acuerdos.

### 10.7 Medición y verificación de cobertura ≥90%
- **Definición**: porcentaje de filas en `RTM.md` con vínculos válidos a origen (UC/RF/ADR/BR) y destino (Código/API/Tests/Evidencia).
- **Herramienta**: `scripts/trazabilidad/coverage_rtm.py --rtm docs/trazabilidad/RTM.md --repo .`.
- **Métrica**: `cobertura_total = filas_con_origen_y_destino / filas_totales`.
- **Umbral**: warning < 90%, blocking < 85%.
- **Reporte**: genera `docs/trazabilidad/registros/rtm_coverage_<fecha>.json` + gráfico en `rtm_coverage_<fecha>.svg`.

### 10.8 Mapa ASCII de referencia

```
[RN] → [RF] → [UC] → [UML] → [ADR] → [COD] → [API] → [TEST] → [EVID] → [REV]
Origen  Reqs   Casos  Diseño  Decis.  Impl.  Interf.  Validac.  Soporte  Aprob.
```

### 10.9 Evidencia automatizada y reporting
- **Periodicidad**: semanal (pipeline) y por release.
- **Formato**: `docs/trazabilidad/registros/<fecha>-evidencia.json` con campos `id`, `tipo`, `fuente`, `uc_refs`, `rf_refs`, `adr_refs`, `resultado`, `enlace_evidencia`.
- **Integración CI/CD**: job `reporte-trazabilidad` publica artefacto HTML en `logs_data/trazabilidad/reportes/<fecha>.html`.
- **Dashboard**: script `scripts/trazabilidad/dashboard_rtm.py` genera `docs/trazabilidad/registros/dashboard/index.html` con cobertura y hallazgos.

### 10.10 Responsables, tiempos y estimaciones
- **B1–B2**: Owner Gobernanza (5d).
- **B3**: Owner QA + Gobernanza (7d).
- **B4**: Owner Arquitectura + Backend (5d).
- **B5**: Owner QA (7d, depende B3).
- **B6**: Owner Backend/Frontend (5d c/u) con soporte Arquitectura.
- **B7**: Owner DevOps (4d) — transición warning→blocking semana 3.
- **B8**: Owner Backend (3d) + QA (validación extend_schema).
- **B9**: Owner QA/Gobernanza (recurrencia mensual, 2d por ciclo).

### 10.11 Checklist de PR y UX para desarrolladores
- Plantilla `.github/PULL_REQUEST_TEMPLATE.md` debe incluir: `UC refs`, `RF refs`, `ADR refs`, `RTM actualizado (sí/no)`, `Evidencia adjunta`.
- Validación automática: workflow `trazabilidad.yml` bloquea PR si falta alguna referencia o si el RTM no cambió cuando hay nuevas funcionalidades.
- Mensajes de commit deben incluir ID de UC/RF/ADR cuando aplique.

### 10.12 Versionado y rollback
- **Habilitación progresiva**: variable `TRZ_VALIDATION_MODE` controla warning/blocking.
- **Rollback**: si el pipeline bloquea releases inesperadamente, deshabilitar job `rtm-drift-check` y revertir la versión de `RTM.md` a la última release estable (`git tag trazabilidad-vX.Y`).
- **Feature flags**: usar `feature-trz-*` para cambios de gemas o validadores; merge solo tras pasar cobertura ≥90%.

## 11. Validación de cobertura (conformidad con el plan oficial y PROC-IACT-TRZ)
Para asegurar que el plan de remediación incorpora **todo lo solicitado** en el Plan Oficial y el procedimiento PROC-IACT-TRZ v1.1, se valida lo siguiente:

- **Principios de trazabilidad vertical y horizontal (sección 3 del plan oficial)**: cubiertos en los objetivos (punto 2) y en la técnica de división en *n* tareas, que exige RN→RF→UC→UML→ADR→Código→API→Tests→Evidencia y vínculos UC↔BR/ADR, RF↔API/Tests.
- **Artefactos obligatorios y nuevas piezas del repositorio (secciones 4 y 9)**: incluidos en backlog B1–B5 (TRZ-001, RTM-IACT, plantillas v2, política GOB-TRZ-001 y estructura `docs/trazabilidad/` con `plantillas/` y `registros/`).
- **Actualización de plantillas v2 (sección 5 del plan oficial)**: contemplada en backlog B4 y en la técnica de tareas que obliga a citar plantillas UC/ADR/TEST/GOB/BR v2 y sus campos upward/downward.
- **Integraciones obligatorias (secciones 6–8 del plan oficial)**: previstas en backlog B6–B8 para gemas, CI/CD (referencias UC/RF/ADR y RTM actualizado) y metadatos de API con `@extend_schema`.
- **Procedimiento por fases 10.1–10.10 (PROC-IACT-TRZ)**: resumido en el punto 10.4, con entradas, salidas, matrices y roles, y reforzado por las reglas de gobernanza (punto 10.5).
- **Reglas de gobernanza y versionado (sección 7 y 9 del procedimiento)**: incorporadas en el punto 10.5 (completitud, entradas mínimas, control de huérfanos, actualización continua, revisión trimestral) y campos editables/versionado en el punto 10.6.
- **Auditoría y entregables (secciones 11 y 12 del plan oficial)**: integrados en oleada 3, backlog B9 y métricas de éxito (auditoría mensual/por release y RTM con ≥90% de cobertura vertical).

Esta lista debe revisarse junto con cada PR para verificar que ninguna pieza normativa quede fuera del alcance del cambio.
