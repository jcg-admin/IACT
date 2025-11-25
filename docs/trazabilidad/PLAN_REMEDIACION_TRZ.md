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

### 10.5 Reglas de gobernanza adicionales
- **Completitud por fase**: no cerrar sin salidas obligatorias, matriz actualizada y validación formal.
- **Prohibición de iniciar sin entradas mínimas** y **control de artefactos huérfanos** (origen y destino identificables).
- **Trazabilidad continua y verificable**: matrices reflejan cambios y versiones; controles de versión del procedimiento con revisión trimestral.
- **Versionado**: mantener historial (ejemplo tabla 1.0 y 1.1) sin sobrescritura; toda modificación registrada con fecha y responsable.

### 10.6 Campos editables de operación
- Proyecto, versión de sistema, módulo o área, fecha de elaboración.
- Responsables: Trazabilidad, QA, Arquitectura, Desarrollo.
- Observaciones libres para decisiones, riesgos o acuerdos.

### 10.7 Mapa ASCII de referencia

```
[RN] → [RF] → [UC] → [UML] → [ADR] → [COD] → [API] → [TEST] → [EVID] → [REV]
Origen  Reqs   Casos  Diseño  Decis.  Impl.  Interf.  Validac.  Soporte  Aprob.
```

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
