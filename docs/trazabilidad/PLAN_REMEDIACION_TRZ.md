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

### Objetivos — Visión más granular
- **Restablecer la cadena estructural vertical**: Asegurar que la cadena completa de trazabilidad (`RNF → ... → Evidencia`) sea funcional y medible.
- **Normalizar Plantillas V2**: Implementar las plantillas actualizadas (`UC_v2`, `ADR_v2`, `TEST_v2`, etc.) con campos de trazabilidad bidireccional (upward y downward).
- **Publicar y Consolidar RTM-IACT**: Crear la nueva Matriz de Trazabilidad de Requisitos y migrar, limpiar y consolidar todos los datos heredados.
- **Integrar Trazabilidad en el Código**: Incorporar las referencias de trazabilidad (`uc_refs`, `adr_refs`) directamente en el código fuente (Gemas/APIs) como metadatos obligatorios.
- **Implementar Gobernanza CI/CD**: Activar todos los jobs de bloqueo (`lint-trazabilidad`, `api-metadata-check`, `uml-check`, `rtm-drift-check --validar-relaciones-minimas`) para forzar el cumplimiento en tiempo real.
- **Garantizar la Consistencia de la RTM**: Asegurar la consistencia de la matriz mediante el control de Relación Mínima Requerida (ej., cada API funcional debe tener al menos una Prueba asociada) y validar estas relaciones con un job dedicado de CI/CD.
- **Certificar Cobertura**: Alcanzar y registrar una Cobertura de Trazabilidad Vertical ≥ 90%, cerrando el ciclo con la generación automática de la Evidencia de QA.

## 3. Alcance
Aplica a todos los dominios definidos en el Plan Oficial: Backend (Django REST), Frontend (React/Webpack), Infraestructura/DevOps, Documentación/Gobernanza, Scripts, QA/Testing, Reglas de Negocio, Casos de Uso/UML y ADRs.

## 4. Estrategia de implementación (fases)
La alternativa B (incremental) se mantiene como la recomendada, pero se organiza en tres fases secuenciales alineadas con las salidas obligatorias del PROC-IACT-TRZ. El detalle técnico de CI/CD antes ubicado en la sección 4.1 se mueve a la sección 6 para mayor claridad.

| ID | Nombre de la fase | Foco y objetivo |
| --- | --- | --- |
| **Fase 1** | Estabilización Documental | Cerrar brechas normativas (RN, RF, UC, UML) y publicar la RTM-IACT. Cubre las fases 10.1 a 10.4 del procedimiento. |
| **Fase 2** | Integración Operacional | Incorporar controles de trazabilidad en código, gemas, APIs y ADRs. Cubre las fases 10.5 a 10.7 del procedimiento. |
| **Fase 3** | Certificación y Evidencia | Completar la validación con Tests y Evidencia, y activar el ciclo de auditoría continua. Cubre las fases 10.8 a 10.10 del procedimiento. |

## 5. Backlog detallado de remediación (nuevas tareas)
Las tareas se reorganizan para cerrar las brechas identificadas (secuencia UML → ADR y relación mínima API → Test) y mantener la trazabilidad completa.

| Backlog ID | Tarea y artefacto de salida | Fase | Justificación (PROC-IACT-TRZ) |
| --- | --- | --- | --- |
| **B1–B4** | Tareas originales: publicación de TRZ-001, plantillas v2 y RTM-IACT. | 1 | Mantener la base normativa y la RTM oficial (fases 10.1–10.3). |
| **B4.5** | Implementación del artefacto y matriz UML. Crear `docs/trazabilidad/modelos/UML_Model.md` y script validador. | 1 | **Nuevo**: garantizar la trazabilidad UC → UML (fase 10.4) antes de los ADRs. |
| **B5** | Migración de datos heredados a `docs/trazabilidad/RTM.md` y marcado de matrices corruptas. | 1 | Completar RTM-IACT con datos limpios antes de avanzar. |
| **B6** | Integrar bloques de trazabilidad en gemas (`uc_refs`, `rf_refs`, `adr_refs`). | 2 | Alinear código y gemas con trazabilidad descendente (fase 10.6). |
| **B7.5** | Actualizar `rtm-drift-check.py` con la regla de Relación Mínima Requerida. | 2 | **Nuevo**: validar que cada `API-XXX` en RTM tenga ≥1 `TEST-YYY` asociado (punto 4.6). |
| **B8** | Integrar metadatos `@extend_schema` en APIs con referencias UC/RF/ADR. | 2 | Cumplir trazabilidad en API (fase 10.7). |
| **B9** | Activar auditorías y registros mensuales y por release. | 3 | Cerrar certificación y evidencias (fase 10.10). |

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

## 6. Controles de gobernanza en CI/CD (cambios en validación)
| Control CI/CD | Descripción y cambios implementados | Brecha mitigada |
| --- | --- | --- |
| `lint-trazabilidad` | Se mantiene. Valida formato y regex de referencias (`UC-\d+`, `ADR-\d+`, etc.) en commits y PRs. | Ausencia de referencias obligatorias. |
| `uml-check` | **Nuevo job de bloqueo (fase 1)**: ejecutado después de la creación de UC y antes de ADRs. Garantiza que exista `UML_Model.md` para los UC activos y que se genere la matriz UC → UML con referencias bidireccionales completas. | Trazabilidad UML huérfana (fase 10.4). |
| `api-metadata-check` | Se mantiene. Verifica que cada endpoint nuevo incluya campos de trazabilidad en `@extend_schema`. | Ausencia de trazabilidad en API (fase 10.7). |
| `rtm-drift-check` | **Modificado (backlog B7.5)**: falla si hay referencias huérfanas, cobertura < 90% o incumplimiento de relación mínima (cualquier `API-XXX` o `RF-YYY` en RTM sin la referencia descendente obligatoria, p. ej., sin `TEST-ZZZ`). | Consistencia y relación mínima (API → Test, RN → RF). |

## 7. Criterios de aceptación
- RTM-IACT sin campos vacíos y con enlaces bidireccionales a requisitos, código, tests y evidencia.
- Todas las plantillas vigentes incluyen campos `trazabilidad_upward` y `trazabilidad_downward` completos.
- CI/CD falla cuando falta referencia a UC/RF/ADR o no se actualiza RTM.
- Documentación de API incluye referencias de trazabilidad en `extend_schema`.
- Primer ciclo de auditoría registrado con hallazgos y acciones.

## 8. Riesgos y mitigaciones
- **Datos heredados incompletos**: priorizar migración con prioridad en requisitos críticos; marcar explícitamente huecos en RTM.
- **Resistencia al cambio**: proveer guía rápida en `docs/trazabilidad/TRZ-001` y checklist en PRs.
- **Sobrecarga en CI/CD**: habilitar validaciones en modo warning durante la transición (semana 2) y endurecer a blocking en semana 3.

## 9. Gobernanza y responsables
- **Owner del plan**: Equipo de Gobernanza/QA.
- **Responsables por dominio**: Tech Leads de Backend, Frontend, Infraestructura y Documentación.
- **Aprobación**: Comité de Arquitectura (ADRs) y QA para cierre de cada fase.

## 10. Métricas de éxito
- Cobertura de trazabilidad vertical ≥ 90% en RTM.
- 0 PRs aceptados sin referencias a UC/RF/ADR tras semana 3.
- 100% de APIs nuevas con `extend_schema` incluyendo referencias.
- Auditorías mensuales sin hallazgos críticos a partir del segundo ciclo.

## 11. Integración del procedimiento PROC-IACT-TRZ (v1.1)
Esta sección alinea el plan de remediación con el procedimiento normativo-operativo *PROC-IACT-TRZ-Procedimiento-Trazabilidad*.

### 10.0 Mapa de trazabilidad PROC-IACT-TRZ → Plan de Remediación
El procedimiento normativo define la cadena obligatoria `RN → RF → UC → UML → ADR → Código → API → Pruebas → Evidencia → Revisión Final de QA`. A continuación se presenta la alineación explícita del plan con cada fase, el artefacto generado, el backlog asociado y el control de CI/CD que valida el cumplimiento.

#### Fase 1: Estabilización Documental y Requisitos
| Fase PROC-IACT-TRZ | Artefacto de trazabilidad | Backlog específico (Plan) | Controles CI/CD y criterio de éxito |
| --- | --- | --- | --- |
| 10.1: RN | `BR_v2.md` | B1–B4: Publicar TRZ-001 y plantillas v2 (`BR_v2.md`) con trazabilidad_upward/downward; migrar matrices heredadas y marcar huecos. | `lint-trazabilidad`: asegura que `BR_v2.md` declare trazabilidad hacia políticas/regulaciones. |
| 10.2: RF | `RTM-IACT.md` (matriz oficial) | B3 y B5: Publicar RTM-IACT con campos completos y cargar datos limpios tras ETL. | Métrica de éxito: RTM-IACT sin campos vacíos y con enlaces bidireccionales. |
| 10.3: UC | `UC_v2.md` | B1–B4: Actualizar plantillas v2 (incluye `UC_v2.md` con campos upward `RN/RF/BR` y downward `UML/API/Tests`). | Regex obligatoria en PR: referencias `UC-\d+` en commits y cuerpo del PR. |
| 10.4: UML | `docs/trazabilidad/modelos/UML_Model.md` + `M_UC_UML` | B4.5: Implementar artefacto UML y matriz UC → UML antes de ADRs. | `uml-check`: bloquea si falta `UML_Model.md` o la matriz UC→UML está incompleta. |

#### Fase 2: Integración Operativa y Diseño
| Fase PROC-IACT-TRZ | Artefacto de trazabilidad | Backlog específico (Plan) | Controles CI/CD y criterio de éxito |
| --- | --- | --- | --- |
| 10.5: ADR | `ADR_v2.md` | B4: Actualizar `ADR_v2.md` con campos upward (UC/UML) y downward (Código/Tests/API). | Regex obligatoria en PR: referencias `ADR-\d+` en commits y cuerpo del PR. |
| 10.6: Código | Referencias en gemas/código | B6: Integrar bloque obligatorio de trazabilidad (`uc_refs`, `rf_refs`, `adr_refs`) en las gemas. | `rtm-drift-check`: valida contra código (`--codigo api backend ui scripts`), evitando código huérfano. |
| 10.7: API | Metadatos `@extend_schema` | B8: Integrar metadatos de API con referencias a UC/RF/ADR. | `api-metadata-check`: job de bloqueo que verifica que cada endpoint nuevo incluya `uc_refs`, `rf_refs`, `adr_refs`. |

#### Fase 3: Validación y Certificación
| Fase PROC-IACT-TRZ | Artefacto de trazabilidad | Backlog específico (Plan) | Controles CI/CD y criterio de éxito |
| --- | --- | --- | --- |
| 10.8: Pruebas | `TEST_v2.md` | B4 y B7.5: Actualizar `TEST_v2.md` con campos upward (API/UC/RF) y downward (Evidencia/Código); aplicar regla de Relación Mínima Requerida en RTM. | `rtm-drift-check`: falla si la cobertura < 90% o si algún `API-XXX` en RTM carece de `TEST-YYY`. |
| 10.10: Revisión Final QA | Auditoría/Registro | B9: Activar auditorías mensuales y por release. | Métrica de éxito: cero PRs aceptados sin referencias tras la semana 3; auditorías mensuales sin hallazgos críticos a partir del segundo ciclo. |

📐 **Cobertura de la Matriz RTM-IACT**
El principal entregable, la matriz RTM-IACT (`docs/trazabilidad/RTM.md`), es el punto central donde converge la trazabilidad. La completitud por fase (punto 10.5 del plan) exige que la matriz sea actualizada y validada en cada paso. El plan asegura el cumplimiento del criterio de trazabilidad bidireccional (punto 4.4 del PROC-IACT-TRZ) al requerir campos `trazabilidad_upward` y `trazabilidad_downward` en todas las plantillas (UC, ADR, TEST, GOB, BR), y al forzar la relación descendente hacia código, API y pruebas mediante controles de CI/CD.

### 10.1 Encabezado normativo y propósito del procedimiento
- **Código del Documento:** PROC-IACT-TRZ-Procedimiento-Trazabilidad.
- **Versión:** 1.1. **Estado:** Editable. **Clasificación:** Normativo / Operativo.
- **Proyecto:** IACT. **Dominio:** SDLC / Gobernanza / Trazabilidad.
- **Responsable:** [EDITABLE]. **Última revisión:** [YYYY-MM-DD].
- **Propósito del procedimiento:**
  - Guía normativa para aplicar trazabilidad en el SDLC de IACT.
  - Base técnica para validadores automáticos, checklists y auditorías.
  - Referencia formal para cumplimiento de gobernanza y aseguramiento de calidad.
  - Guía fase por fase (10.1 → 10.10) para validar entradas y salidas, impedir avanzar si falta una fase previa y detectar artefactos faltantes o huérfanos.

### 10.2 Alcance y estructura general
Este procedimiento aplica a todo el SDLC y cubre artefactos formales: **RN, RF, UC, UML, ADR, Código, API, Pruebas, Evidencia y Revisión Final de QA**.

Cadena estructural obligatoria:

```
RN  →  RF  →  UC  →  UML  →  ADR  →  Código  →  API  →  Pruebas  →  Evidencia  →  Revisión Final de QA
```

#### 10.2.1 Significado de los elementos
- **RN — Reglas de Negocio:** origen de la trazabilidad; políticas y condiciones.
- **RF — Requerimientos Funcionales:** derivación técnica de las RN.
- **UC — Casos de Uso:** interacciones y flujos del usuario, con pre/postcondiciones.
- **UML — Diagramas UML:** diseño visual derivado de los UC.
- **ADR — Architecture Decision Records:** decisiones arquitectónicas con contexto y consecuencias.
- **Código:** implementación alineada a UC/UML/ADR.
- **API:** interfaces públicas sustentadas por código, RF, UC y ADR.
- **Pruebas:** validaciones formales sobre RN, RF, UC, API y código.
- **Evidencia:** soportes verificables de la ejecución de pruebas.
- **Revisión Final de QA:** aprobación interna que acredita el cierre de trazabilidad.

### 10.3 Principios de operación del procedimiento
- **Secuencialidad obligatoria:** avanzar de 10.1 a 10.10 sin saltos ni reordenamientos.
- **Control estricto de entradas y salidas:** verificar salidas obligatorias y entradas mínimas antes de pasar de fase.
- **Prevención de omisiones y errores:** identificar faltantes, ubicarlos, indicar corrección y bloquear avance hasta resolver.
- **Trazabilidad bidireccional:** relaciones directas e inversas desde RN hasta Revisión Final.
- **Prohibición de artefactos huérfanos:** cada elemento debe tener origen y destino trazable.
- **Consistencia en matrices:** identificadores correctos, sin duplicados y con relaciones mínimas cumplidas.
- **Condiciones para marcar fase como completa:** salidas generadas y verificadas, matrices actualizadas y entradas válidas para la siguiente fase.

### 10.4 Procedimiento por fases (10.1–10.10)
Cada fase mantiene objetivo, entradas mínimas, actividades clave, salidas obligatorias, matrices afectadas, validaciones para avanzar y rol principal responsable.

- **5.1 Fase 10.1 — Identificación de Reglas de Negocio (RN)**
  - **Objetivo:** definir el conjunto completo y válido de Reglas de Negocio del sistema.
  - **Entradas mínimas:** información de procesos del negocio; políticas, contratos, normativas; RN existentes (si las hay).
  - **Actividades clave:** identificar y documentar cada RN; asignar un identificador único (BR-XXX); clasificar cada RN según RN-STD-IACT; registrar fuente, responsable y propósito.
  - **Salidas obligatorias:** lista oficial de RN (RN-XXX); Matriz RN (catálogo RN consolidado).
  - **Matrices afectadas:** `M_RN` (catálogo de Reglas de Negocio).
  - **Validaciones para avanzar:** no debe haber RN sin identificador único; no debe haber RN duplicadas o ambiguas; todas las RN deben tener fuente y responsable.
  - **Rol principal responsable [EDITABLE]:** Analista de Negocio / Product Owner.

- **5.2 Fase 10.2 — Derivación de Requerimientos Funcionales (RF)**
  - **Objetivo:** derivar requerimientos funcionales a partir de las RN.
  - **Entradas mínimas:** matriz `M_RN` completa.
  - **Actividades clave:** analizar cada RN; derivar uno o más RF; registrar `RF-XXX`; establecer relaciones RN → RF.
  - **Salidas obligatorias:** lista `RF-XXX`; matriz RN → RF.
  - **Matrices afectadas:** `M_RF`, `M_RN_RF`.
  - **Validaciones para avanzar:** cada RF debe referenciar al menos una RN; no debe haber RF sin RN asociada.
  - **Rol principal responsable [EDITABLE]:** Analista de Requisitos.

- **5.3 Fase 10.3 — Elaboración de Casos de Uso (UC)**
  - **Objetivo:** modelar funcionalmente el sistema mediante Casos de Uso.
  - **Entradas mínimas:** matriz RN → RF (`M_RN_RF`); lista `RF-XXX` (`M_RF`).
  - **Actividades clave:** definir `UC-XXX` por RF que implique interacción/proceso; documentar actores, flujos, pre y postcondiciones; establecer RF → UC.
  - **Salidas obligatorias:** lista `UC-XXX`; matriz RF → UC.
  - **Matrices afectadas:** `M_UC`, `M_RF_UC`.
  - **Validaciones para avanzar:** todo RF relevante debe estar cubierto por uno o más UC; no debe haber UC sin RF asociado.
  - **Rol principal responsable [EDITABLE]:** Analista Funcional.

- **5.4 Fase 10.4 — Modelado UML**
  - **Objetivo:** transformar los Casos de Uso en diseño técnico UML.
  - **Entradas mínimas:** matriz RF → UC (`M_RF_UC`); lista `UC-XXX` (`M_UC`).
  - **Actividades clave:** seleccionar tipo de diagrama para cada UC (Actividad, Secuencia, Estado, Estructural); crear diagramas `UML-XXX`; establecer UC → UML.
  - **Salidas obligatorias:** colección `UML-XXX`; matriz UC → UML.
  - **Matrices afectadas:** `M_UML`, `M_UC_UML`.
  - **Validaciones para avanzar:** cada UC debe tener al menos un diagrama UML asociado; el contenido de UML debe ser consistente con los flujos del UC.
  - **Validaciones CI/CD:** job `uml-matrix-check` bloquea el paso a la fase 10.5 si la matriz UC→UML no está publicada o está incompleta.
  - **Rol principal responsable [EDITABLE]:** Arquitecto de Software / Diseñador.

- **5.5 Fase 10.5 — Documentación de ADR**
  - **Objetivo:** registrar decisiones arquitectónicas con trazabilidad a UML.
  - **Entradas mínimas:** matriz UC → UML (`M_UC_UML`); diagramas `UML-XXX` (`M_UML`).
  - **Actividades clave:** identificar decisiones arquitectónicas en los modelos UML; documentar `ADR-XXX`; establecer UML → ADR.
  - **Salidas obligatorias:** lista `ADR-XXX`; matriz UML → ADR.
  - **Matrices afectadas:** `M_ADR`, `M_UML_ADR`.
  - **Validaciones para avanzar:** todo ADR debe referenciar al menos un UML; todo ADR debe tener contexto, decisión y consecuencias.
  - **Rol principal responsable [EDITABLE]:** Arquitecto de Software.

- **5.6 Fase 10.6 — Implementación de Código**
  - **Objetivo:** implementar el sistema conforme a UC, UML y ADR.
  - **Entradas mínimas:** matriz UML → ADR (`M_UML_ADR`); lista `ADR-XXX` (`M_ADR`); `UC-XXX` (`M_UC`).
  - **Actividades clave:** implementar código alineado a diseño; documentar referencias a ADR/UC en el código (comentarios, anotaciones); establecer ADR → Código.
  - **Salidas obligatorias:** código implementado; matriz ADR → Código.
  - **Matrices afectadas:** `M_CODE`, `M_ADR_CODE`.
  - **Validaciones para avanzar:** no debe existir código sin ADR o UC asociado; código clave debe poder rastrearse hacia arriba.
  - **Rol principal responsable [EDITABLE]:** Equipo de Desarrollo.

- **5.7 Fase 10.7 — Definición y Documentación de API**
  - **Objetivo:** documentar las APIs expuestas con trazabilidad a código y requisitos.
  - **Entradas mínimas:** matriz ADR → Código (`M_ADR_CODE`); código implementado (`M_CODE`).
  - **Actividades clave:** identificar endpoints generados por el código; documentarlos (OpenAPI u otro formato); establecer Código → API.
  - **Salidas obligatorias:** especificación de API; matriz Código → API.
  - **Matrices afectadas:** `M_API`, `M_CODE_API`.
  - **Validaciones para avanzar:** todo endpoint debe estar respaldado por código y requisitos; no debe haber API “huérfana”.
  - **Rol principal responsable [EDITABLE]:** Equipo de Desarrollo / API Owner.

- **5.8 Fase 10.8 — Diseño y Ejecución de Pruebas**
  - **Objetivo:** validar que el sistema cumple RN, RF, UC, API y Código.
  - **Entradas mínimas:** matriz Código → API (`M_CODE_API`); `RF-XXX`, `UC-XXX`, `RN-XXX`.
  - **Actividades clave:** diseñar casos de prueba (`TC-XXX`); establecer API → Test; ejecutar pruebas y registrar resultados; documentar defectos con trazabilidad inversa.
  - **Salidas obligatorias:** lista `TC-XXX`; resultados de pruebas; matriz API → Test.
  - **Matrices afectadas:** `M_TEST`, `M_API_TEST`.
  - **Validaciones para avanzar:** toda API crítica debe tener pruebas asociadas; defectos deben poder rastrearse a su origen (RN/RF/UC/API/Código).
  - **Rol principal responsable [EDITABLE]:** Equipo de QA.

- **5.9 Fase 10.9 — Registro de Evidencia**
  - **Objetivo:** respaldar todas las pruebas con evidencia verificable.
  - **Entradas mínimas:** matriz API → Test (`M_API_TEST`); resultados de pruebas (`M_TEST`).
  - **Actividades clave:** capturar evidencia (reportes, capturas, logs); registrar evidencia en repositorios oficiales; establecer Test → Evidencia.
  - **Salidas obligatorias:** evidencia catalogada; matriz Test → Evidencia.
  - **Matrices afectadas:** `M_EVID`, `M_TEST_EVID`.
  - **Validaciones para avanzar:** no debe haber test sin evidencia; evidencia debe ser accesible y verificable.
  - **Rol principal responsable [EDITABLE]:** QA / Cumplimiento.

- **5.10 Fase 10.10 — Validación Final de Trazabilidad**
  - **Objetivo:** certificar que el sistema puede liberarse con trazabilidad completa.
  - **Entradas mínimas:** todas las matrices: `M_RN`, `M_RF`, `M_UC`, `M_UML`, `M_ADR`, `M_CODE`, `M_API`, `M_TEST`, `M_EVID`; todas las matrices de relación: `M_RN_RF`, `M_RF_UC`, `M_UC_UML`, `M_UML_ADR`, `M_ADR_CODE`, `M_CODE_API`, `M_API_TEST`, `M_TEST_EVID`.
  - **Actividades clave:** verificar que ninguna matriz esté incompleta; confirmar ausencia de artefactos huérfanos; verificar trazabilidad bidireccional; registrar firmas de QA y Gobernanza.
  - **Salidas obligatorias:** certificación de Trazabilidad; acta de liberación de versión.
  - **Matrices afectadas:** `M_CERT` (registro de certificación).
  - **Validaciones para cierre:** ningún artefacto sin origen ni destino; todas las fases marcadas como completas.
  - **Rol principal responsable [EDITABLE]:** QA / Gobernanza Técnica.

### 10.5 Reglas de gobernanza del procedimiento
- **Completitud obligatoria por fase:** salidas, matriz y validación formal listas antes de cerrar.
- **Prohibición de avanzar sin entradas mínimas:** bloquear inicio de fase si faltan insumos.
- **Control de artefactos huérfanos:** todo artefacto debe tener origen y destino dentro del flujo.
- **Trazabilidad continua y verificable:** matrices actualizadas con cambios, versiones y relaciones obligatorias.
- **Control de versiones del procedimiento:** revisión al menos trimestral e incorporación de mejoras sin sobrescribir historial.

### 10.6 Campos editables del procedimiento
- **Proyecto, versión del sistema, módulo o área aplicada, fecha de elaboración** (YYYY-MM-DD).
- **Responsables:** Trazabilidad, QA, Arquitectura, Desarrollo.
- **Observaciones:** espacio libre para decisiones, acuerdos, riesgos o aclaraciones.

### 10.7 Versionado del procedimiento
|Versión|Fecha|Responsable|Descripción de cambios|
|---|---|---|---|
|1.0|[YYYY-MM-DD]|Gobernanza IACT|Versión inicial del procedimiento|
|1.1|[YYYY-MM-DD]|Gobernanza IACT|Versión ampliada, organizada por secciones independientes|

Política de actualización: registrar toda modificación, no sobrescribir historial y revisar formalmente cada tres meses.

### 10.8 Mapa ASCII del procedimiento

```
[RN]   → [RF]   → [UC]   → [UML]   → [ADR]   → [COD]   → [API]   → [TEST]   → [EVID]   → [CERT]
Origen   Reqs      Casos    Diseño    Decis.    Impl.     Interf.   Validac.   Soporte    Aprob.
```

### 10.9 Evidencia automatizada y reporting
- **Periodicidad:** semanal (pipeline) y por release.
- **Formato:** `docs/trazabilidad/registros/<fecha>-evidencia.json` con campos `id`, `tipo`, `fuente`, `uc_refs`, `rf_refs`, `adr_refs`, `resultado`, `enlace_evidencia`.
- **Integración CI/CD:** job `reporte-trazabilidad` publica artefacto HTML en `logs_data/trazabilidad/reportes/<fecha>.html`.
- **Dashboard:** `scripts/trazabilidad/dashboard_rtm.py` genera `docs/trazabilidad/registros/dashboard/index.html` con cobertura y hallazgos.

### 10.10 Plan de migración de datos heredados
- **Inventario inicial (día 1-2):** exportar matrices actuales (`docs/gobernanza/trazabilidad/*`) y clasificarlas por criticidad (CRIT/MAJ/MIN).
- **Limpieza asistida (día 3-4):** usar `scripts/trazabilidad/etl_rtm.py` para normalizar IDs, detectar duplicados/huérfanos, marcar huecos con `PENDING` y generar reporte CSV.
- **Carga a RTM-IACT (día 5):** importar CSV limpio a `docs/trazabilidad/RTM.md`.
- **Validación cruzada (día 6):** ejecutar `validar_rtm.py` y muestrear manualmente 10% de entradas CRIT.
- **Cierre (día 7):** aprobar migración y archivar matrices antiguas como deprecated.

### 10.11 Medición y verificación de cobertura ≥90%
- **Definición:** porcentaje de filas en `RTM.md` con vínculos válidos a origen (UC/RF/ADR/BR) y destino (Código/API/Tests/Evidencia).
- **Herramienta:** `scripts/trazabilidad/coverage_rtm.py --rtm docs/trazabilidad/RTM.md --repo .`.
- **Métrica:** `cobertura_total = filas_con_origen_y_destino / filas_totales`.
- **Umbral:** warning < 90%, blocking < 85%.
- **Reporte:** `docs/trazabilidad/registros/rtm_coverage_<fecha>.json` + gráfico `rtm_coverage_<fecha>.svg`.

### 10.12 Responsables, tiempos y estimaciones
- **B1–B2:** Owner Gobernanza (5d).
- **B3:** Owner QA + Gobernanza (7d).
- **B4:** Owner Arquitectura + Backend (5d).
- **B5:** Owner QA (7d, depende B3).
- **B6:** Owner Backend/Frontend (5d c/u) con soporte Arquitectura.
- **B7:** Owner DevOps (4d) — transición warning→blocking semana 3.
- **B8:** Owner Backend (3d) + QA (validación extend_schema).
- **B9:** Owner QA/Gobernanza (recurrencia mensual, 2d por ciclo).

### 10.13 Checklist de PR y UX para desarrolladores
- Plantilla `.github/PULL_REQUEST_TEMPLATE.md` con `UC refs`, `RF refs`, `ADR refs`, `RTM actualizado (sí/no)`, `Evidencia adjunta`.
- Workflow `trazabilidad.yml` bloquea PR si falta alguna referencia o si `RTM.md` no cambia cuando hay nuevas funcionalidades.
- Mensajes de commit deben incluir ID de UC/RF/ADR cuando aplique.

### 10.14 Versionado y rollback
- **Habilitación progresiva:** `TRZ_VALIDATION_MODE` controla warning/blocking.
- **Rollback:** deshabilitar `rtm-drift-check` y revertir `RTM.md` a la última release estable (`git tag trazabilidad-vX.Y`) si un bloqueo es inesperado.
- **Feature flags:** usar `feature-trz-*` para gemas o validadores; merge solo tras pasar cobertura ≥90%.


## 11. Validación de cobertura (conformidad con el plan oficial y PROC-IACT-TRZ)
Para asegurar que el plan de remediación incorpora **todo lo solicitado** en el Plan Oficial y el procedimiento PROC-IACT-TRZ v1.1, se valida lo siguiente:

- **Principios de trazabilidad vertical y horizontal (sección 3 del plan oficial)**: cubiertos en los objetivos (punto 2) y en la técnica de división en *n* tareas, que exige RN→RF→UC→UML→ADR→Código→API→Tests→Evidencia y vínculos UC↔BR/ADR, RF↔API/Tests.
- **Artefactos obligatorios y nuevas piezas del repositorio (secciones 4 y 9)**: incluidos en backlog B1–B5 (TRZ-001, RTM-IACT, plantillas v2, política GOB-TRZ-001 y estructura `docs/trazabilidad/` con `plantillas/` y `registros/`).
- **Actualización de plantillas v2 (sección 5 del plan oficial)**: contemplada en backlog B4 y en la técnica de tareas que obliga a citar plantillas UC/ADR/TEST/GOB/BR v2 y sus campos upward/downward.
- **Integraciones obligatorias (secciones 6–8 del plan oficial)**: previstas en backlog B6–B8 para gemas, CI/CD (referencias UC/RF/ADR y RTM actualizado) y metadatos de API con `@extend_schema`.
- **Procedimiento por fases 10.1–10.10 (PROC-IACT-TRZ)**: resumido en el punto 10.4, con entradas, salidas, matrices y roles, y reforzado por las reglas de gobernanza (punto 10.5).
- **Reglas de gobernanza y versionado (sección 7 y 9 del procedimiento)**: incorporadas en el punto 10.5 (completitud, entradas mínimas, control de huérfanos, actualización continua, revisión trimestral) y campos editables/versionado en el punto 10.6.
- **Auditoría y entregables (secciones 11 y 12 del plan oficial)**: integrados en fase 3, backlog B9 y métricas de éxito (auditoría mensual/por release y RTM con ≥90% de cobertura vertical).

Esta lista debe revisarse junto con cada PR para verificar que ninguna pieza normativa quede fuera del alcance del cambio.
