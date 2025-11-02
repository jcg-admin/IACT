---
id: DOC-ANAL-ESTRUCTURA-BABOK
estado: propuesta
propietario: equipo-producto
fecha_creacion: 2025-11-02
version: 1.0
relacionados: ["DOC-INDEX-GENERAL", "DOC-GOB-INDEX"]
---
# Análisis y Propuesta de Nueva Estructura de docs/
## Basado en Taxonomía BABOK v3 e ISO/IEC/IEEE 29148

## RESUMEN EJECUTIVO

Este documento analiza la estructura actual de `docs/` y propone una reorganización alineada con las definiciones de SOLICITUD, REQUISITO, REQUIREMENTS y TASKS según estándares internacionales (BABOK v3, PMBOK, ISO/IEC/IEEE 29148, IREB/CPRE).

**OBJETIVO:** Establecer una jerarquía documental que refleje correctamente el flujo:

```
NECESIDAD (Por qué) → REQUISITOS (Qué) → TAREAS (Cómo) → SOLUCIÓN
```

---

## PARTE 1: ANÁLISIS DE LA ESTRUCTURA ACTUAL

### 1.1 Estructura Actual Identificada

```
docs/
├── solicitudes/               # Solicitudes documentales (SC00, SC01, etc.)
├── vision_y_alcance/          # Visión estratégica
├── requisitos/                # Requisitos corporativos
├── arquitectura/              # Decisiones arquitectónicas (ADR)
├── gobernanza/                # Políticas y estándares
├── planificacion_y_releases/  # Roadmap y versiones
├── diseno_detallado/          # Especificaciones técnicas
├── qa/                        # Estrategia y registros de calidad
├── devops/                    # Automatización y operaciones
├── checklists/                # Listas de verificación
├── plantillas/                # Plantillas corporativas
├── anexos/                    # Material complementario
│   ├── diagramas/
│   ├── ejemplos/
│   └── referencias/
├── backend/                   # Dominio Backend
│   ├── requisitos/
│   ├── arquitectura/
│   ├── diseno_detallado/
│   ├── qa/
│   ├── devops/
│   ├── planificacion_y_releases/
│   ├── gobernanza/
│   └── checklists/
├── frontend/                  # Dominio Frontend (estructura similar)
└── infrastructure/            # Dominio Infraestructura (estructura similar)
```

### 1.2 Problemas Identificados con la Taxonomía BABOK

| PROBLEMA | IMPACTO | EJEMPLO |
|----------|---------|---------|
| **Confusión terminológica** | La carpeta `solicitudes/` contiene "solicitudes documentales" en lugar de "necesidades de negocio" | SC00, SC01 son identificadores de solicitudes de documentación, no necesidades estratégicas |
| **Mezcla de niveles de abstracción** | No hay separación clara entre requisitos de negocio, stakeholders y solución | `requisitos/` parece contener todo tipo de requisitos sin clasificación BABOK |
| **Falta de jerarquía NECESIDAD → REQUISITO → TAREA** | No se refleja el flujo de transformación | No es evidente cómo una necesidad se convierte en requisitos y luego en tareas |
| **Ausencia de espacio para TAREAS de BA** | No hay carpeta para tareas de análisis de negocio | Las tareas BABOK (elicitación, validación, priorización) no están documentadas estructuradamente |
| **Duplicación por dominio** | Backend, Frontend e Infrastructure replican toda la estructura | Genera inconsistencia y dificulta la visión corporativa |
| **Requisitos de Transición no identificados** | No hay espacio específico para requisitos temporales | Conversiones de datos, capacitación, migración no están categorizados |

### 1.3 Fortalezas de la Estructura Actual

- [OK] Separación por dominios técnicos (backend/frontend/infrastructure) facilita trabajo de equipos especializados
- [OK] Carpeta `plantillas/` centralizada promueve estandarización
- [OK] `anexos/` bien estructurado para material complementario
- [OK] Uso de metadatos YAML en archivos README
- [OK] Carpeta `vision_y_alcance/` alineada con Business Case
- [OK] Gobernanza separada permite establecer políticas corporativas

---

## PARTE 2: PROPUESTA DE NUEVA ESTRUCTURA

### 2.1 Principios de Diseño

1. **ALINEACIÓN CON BABOK:** Reflejar la taxonomía oficial de Solicitud/Necesidad → Requisitos → Tareas
2. **TRAZABILIDAD VERTICAL:** Facilitar seguimiento desde necesidad de negocio hasta implementación
3. **SEPARACIÓN DE RESPONSABILIDADES:** Diferenciar claramente qué gestiona Negocio, BA, Arquitectura y Desarrollo
4. **COMPATIBILIDAD:** Mantener estructura por dominios técnicos cuando sea necesario
5. **MINIMALISMO:** Evitar duplicación innecesaria

### 2.2 Estructura Propuesta - Nivel 1 (Raíz)

```
docs/
├── 01_necesidades_negocio/        # NIVEL 1: Business Needs (NUEVO)
├── 02_requisitos/                 # NIVEL 2: Requirements (REESTRUCTURADO)
├── 03_tareas_analisis/            # NIVEL 3: BA Tasks (NUEVO)
├── 04_diseno_solucion/            # Diseño y Arquitectura (RENOMBRADO)
├── 05_implementacion/             # Por dominio técnico (REORGANIZADO)
├── 06_validacion_evaluacion/     # QA y Evaluación de Solución (NUEVO)
├── 99_gobernanza/                 # Gobernanza transversal (RENOMBRADO)
├── plantillas/                    # Sin cambios
└── anexos/                        # Sin cambios
```

### 2.3 Estructura Detallada Propuesta

#### 2.3.1 `01_necesidades_negocio/` - Business Needs

**PROPÓSITO:** Documentar problemas u oportunidades de alto nivel que justifican cambios organizacionales.

```
01_necesidades_negocio/
├── readme.md                      # Índice de necesidades activas
├── plantilla_necesidad.md         # Plantilla para documentar necesidades
├── n001_reduccion_costos_operativos/
│   ├── business_case.md           # Business Case (plantilla_business_case.md)
│   ├── analisis_costo_beneficio.md
│   ├── stakeholders_ejecutivos.md
│   └── metricas_exito.md
├── n002_mejora_satisfaccion_cliente/
│   ├── business_case.md
│   ├── analisis_mercado.md
│   └── kpis_objetivo.md
└── historial/                     # Necesidades cerradas o archivadas
```

**RESPONSABLES:** Sponsors, Ejecutivos, Product Owners

**ARTEFACTOS CLAVE:**
- Business Case (usando `plantillas/plantilla_business_case.md`)
- Project Charter (usando `plantillas/plantilla_project_charter.md`)
- Análisis Costo-Beneficio
- Declaración de Visión y Alcance

**MAPEO BABOK:**
- Área de Conocimiento: **Análisis Estratégico (Strategic Analysis)**
- Tareas relacionadas: 6.1 Analizar el Estado Actual, 6.2 Definir el Estado Futuro

---

#### 2.3.2 `02_requisitos/` - Requirements

**PROPÓSITO:** Especificaciones formales y documentadas que satisfacen necesidades de negocio.

```
02_requisitos/
├── readme.md                          # Índice y matriz de trazabilidad global
├── plantilla_requisito.md             # Plantilla estándar de requisito
├── trazabilidad_general.md            # Matriz Need → Requirement → Design → Test
│
├── requisitos_negocio/                # A) Business Requirements
│   ├── readme.md
│   ├── rb_001_reducir_roturas_stock.md
│   ├── rb_002_optimizar_inventarios.md
│   └── rb_003_roi_18_meses.md
│
├── requisitos_stakeholders/           # B) Stakeholder Requirements
│   ├── readme.md
│   ├── por_rol/
│   │   ├── gerente_compras/
│   │   │   ├── rs_001_alertas_reorden.md
│   │   │   └── rs_002_reportes_proveedores.md
│   │   ├── vendedor/
│   │   │   └── rs_010_consulta_disponibilidad.md
│   │   └── gerente_almacen/
│   │       └── rs_020_reporte_rotacion.md
│   └── trazabilidad_stakeholders.md
│
├── requisitos_solucion/               # C) Solution Requirements
│   ├── readme.md
│   ├── funcionales/                   # C1) Functional Requirements
│   │   ├── modulo_inventario/
│   │   │   ├── rf_001_calculo_punto_reorden.md
│   │   │   ├── rf_002_notificaciones_stock.md
│   │   │   └── rf_003_actualizacion_tiempo_real.md
│   │   ├── modulo_compras/
│   │   └── modulo_reportes/
│   └── no_funcionales/                # C2) Non-Functional Requirements
│       ├── rendimiento/
│       │   ├── rnf_001_tiempo_respuesta.md
│       │   └── rnf_002_usuarios_concurrentes.md
│       ├── seguridad/
│       ├── usabilidad/
│       ├── disponibilidad/
│       └── escalabilidad/
│
├── requisitos_transicion/             # D) Transition Requirements
│   ├── readme.md
│   ├── rt_001_migracion_datos.md
│   ├── rt_002_capacitacion_usuarios.md
│   └── rt_003_soporte_sistema_antiguo.md
│
└── por_dominio/                       # Vista complementaria por dominio técnico
    ├── backend/
    │   └── links_a_requisitos_relevantes.md
    ├── frontend/
    │   └── links_a_requisitos_relevantes.md
    └── infrastructure/
        └── links_a_requisitos_relevantes.md
```

**RESPONSABLES:** Business Analysts, Product Owners

**ARTEFACTOS CLAVE:**
- Business Requirements Document (BRD)
- Functional Requirements Document (FRD)
- Software Requirements Specification (SRS) (usando `plantillas/plantilla_srs.md`)
- Matriz de Trazabilidad

**MAPEO BABOK:**
- Área de Conocimiento: **Análisis de Requisitos y Definición del Diseño (Requirements Analysis and Design Definition)**
- Tareas relacionadas: 7.1 Especificar y Modelar Requisitos, 7.2 Verificar Requisitos, 7.3 Validar Requisitos

---

#### 2.3.3 `03_tareas_analisis/` - Business Analysis Tasks

**PROPÓSITO:** Documentar las tareas de análisis de negocio realizadas para transformar necesidades en soluciones.

```
03_tareas_analisis/
├── readme.md                          # Índice de tareas y su estado
├── plantilla_tarea_ba.md              # Plantilla para documentar tareas
│
├── planificacion_y_monitoreo/         # BABOK Knowledge Area 3
│   ├── t_3.1_planificar_enfoque_ba.md
│   ├── t_3.2_planificar_participacion_stakeholders.md
│   └── t_3.5_identificar_mejoras_desempenio.md
│
├── elicitacion_colaboracion/          # BABOK Knowledge Area 4
│   ├── sesiones/
│   │   ├── 2025-11-01_taller_elicitacion_inventario/
│   │   │   ├── preparacion.md          # Tarea 4.1
│   │   │   ├── acta_sesion.md          # Tarea 4.2
│   │   │   ├── confirmacion_resultados.md # Tarea 4.3
│   │   │   └── entregables/
│   │   └── 2025-11-05_entrevistas_stakeholders/
│   ├── tecnicas_aplicadas/
│   │   ├── entrevistas.md
│   │   ├── talleres.md
│   │   ├── observacion.md
│   │   └── encuestas.md
│   └── registro_comunicaciones.md     # Tarea 4.4
│
├── gestion_ciclo_vida_requisitos/     # BABOK Knowledge Area 5
│   ├── t_5.1_rastrear_requisitos.md
│   ├── t_5.2_mantener_requisitos.md
│   ├── t_5.3_priorizar_requisitos/
│   │   ├── sesion_moscow_2025-11-01.md
│   │   └── resultado_priorizacion.md
│   ├── t_5.4_evaluar_cambios_requisitos/
│   │   ├── solicitud_cambio_001.md
│   │   └── impacto_analizado.md
│   └── t_5.5_aprobar_requisitos/
│       └── registro_aprobaciones.md
│
├── analisis_estrategico/              # BABOK Knowledge Area 6
│   ├── t_6.1_analizar_estado_actual.md
│   ├── t_6.2_definir_estado_futuro.md
│   ├── t_6.3_evaluar_riesgos.md
│   └── t_6.4_definir_estrategia_cambio.md
│
├── analisis_requisitos_diseno/        # BABOK Knowledge Area 7
│   ├── t_7.1_especificar_modelar_requisitos/
│   │   ├── casos_uso/
│   │   ├── user_stories/
│   │   ├── diagramas_flujo/
│   │   └── modelos_datos/
│   ├── t_7.2_verificar_requisitos.md
│   ├── t_7.3_validar_requisitos/
│   │   ├── sesion_validacion_2025-11-10.md
│   │   └── prototipos/
│   ├── t_7.4_definir_arquitectura_requisitos.md
│   ├── t_7.5_definir_opciones_diseno.md
│   └── t_7.6_recomendar_solucion.md
│
└── evaluacion_solucion/               # BABOK Knowledge Area 8
    ├── t_8.1_medir_desempeno_solucion.md
    ├── t_8.2_analizar_medidas_desempeno.md
    ├── t_8.3_evaluar_limitaciones_solucion.md
    ├── t_8.4_evaluar_limitaciones_empresa.md
    └── t_8.5_recomendar_acciones_incrementar_valor.md
```

**RESPONSABLES:** Business Analysts

**ARTEFACTOS CLAVE:**
- Actas de Sesiones de Elicitación
- Resultados de Priorización
- Matrices de Validación
- Registro de Cambios en Requisitos
- Aprobaciones de Stakeholders

**MAPEO BABOK:**
- Todas las 6 Áreas de Conocimiento BABOK v3
- 30 Tareas estándar de Business Analysis

---

#### 2.3.4 `04_diseno_solucion/` - Solution Design

**PROPÓSITO:** Arquitectura y diseño técnico derivado de requisitos aprobados.

```
04_diseno_solucion/
├── readme.md
├── arquitectura_empresarial/
│   ├── modelo_negocio.md
│   ├── arquitectura_informacion.md
│   └── arquitectura_aplicaciones.md
│
├── arquitectura_sistemas/
│   ├── adr/                           # Architecture Decision Records
│   │   ├── 001_monolito_modular.md
│   │   └── 002_base_datos_postgresql.md
│   ├── patrones_arquitectonicos.md
│   └── diagramas_c4/
│
├── diseno_detallado/
│   ├── backend/
│   │   ├── modelos_datos.md           # Usando plantilla_database_design.md
│   │   ├── api_contracts.md           # Usando plantilla_api_reference.md
│   │   └── diagramas_secuencia/
│   ├── frontend/
│   │   ├── componentes_ui.md          # Usando plantilla_ui_ux.md
│   │   └── flujos_interaccion/
│   └── infrastructure/
│       ├── topologia_red.md
│       └── diagrama_despliegue.md
│
└── trazabilidad_diseno.md             # Requisito → Decisión de Diseño
```

**RESPONSABLES:** Arquitectos de Software, Tech Leads

**ARTEFACTOS CLAVE:**
- Architecture Decision Records (ADR)
- System Architecture Document (SAD) (usando `plantillas/plantilla_sad.md`)
- Database Design (usando `plantillas/plantilla_database_design.md`)
- API Reference (usando `plantillas/plantilla_api_reference.md`)

---

#### 2.3.5 `05_implementacion/` - Implementation by Domain

**PROPÓSITO:** Documentación específica de implementación por dominio técnico.

```
05_implementacion/
├── readme.md
├── backend/
│   ├── setup/
│   │   └── entorno_desarrollo.md      # Usando plantilla_setup_entorno.md
│   ├── guias_desarrollo/
│   │   ├── estandares_codigo.md
│   │   ├── tdd_guidelines.md          # Usando plantilla_tdd.md
│   │   └── revision_codigo.md
│   ├── modulos/
│   │   ├── inventario/
│   │   ├── compras/
│   │   └── reportes/
│   └── devops/
│       ├── pipelines/
│       └── runbooks/                   # Usando plantilla_runbook.md
│
├── frontend/
│   ├── setup/
│   ├── guias_desarrollo/
│   ├── componentes/
│   └── devops/
│
└── infrastructure/
    ├── terraform/
    ├── kubernetes/
    ├── monitoring/
    └── runbooks/
```

**RESPONSABLES:** Desarrolladores, DevOps Engineers

**ARTEFACTOS CLAVE:**
- Setup Guides (usando `plantillas/plantilla_setup_entorno.md`)
- Deployment Guides (usando `plantillas/plantilla_deployment_guide.md`)
- Runbooks (usando `plantillas/plantilla_runbook.md`)
- Troubleshooting Guides (usando `plantillas/plantilla_troubleshooting.md`)

---

#### 2.3.6 `06_validacion_evaluacion/` - QA & Solution Evaluation

**PROPÓSITO:** Estrategias de pruebas, evaluación de solución y mejora continua.

```
06_validacion_evaluacion/
├── readme.md
├── estrategia_qa/
│   ├── plan_maestro_pruebas.md        # Usando plantilla_plan_pruebas.md
│   ├── piramide_testing.md
│   └── cobertura_objetivo.md
│
├── casos_prueba/
│   ├── por_requisito/
│   │   ├── rb_001_test_cases.md       # Usando plantilla_caso_prueba.md
│   │   └── rf_001_test_cases.md
│   └── por_modulo/
│
├── resultados_pruebas/
│   ├── regression/
│   ├── performance/
│   └── security/
│
├── metricas_calidad/
│   ├── cobertura_codigo.md
│   ├── deuda_tecnica.md
│   └── bugs_reportados.md
│
├── evaluacion_solucion/               # BABOK Knowledge Area 8
│   ├── medicion_desempeno.md
│   ├── satisfaccion_usuarios.md
│   ├── kpis_negocio.md
│   └── lecciones_aprendidas.md
│
└── trazabilidad_pruebas.md            # Requisito → Test Case → Resultado
```

**RESPONSABLES:** QA Engineers, Business Analysts

**ARTEFACTOS CLAVE:**
- Test Plan (usando `plantillas/plantilla_plan_pruebas.md`)
- Test Cases (usando `plantillas/plantilla_caso_prueba.md`)
- QA Setup (usando `plantillas/plantilla_setup_qa.md`)
- Evaluation Reports

---

#### 2.3.7 `99_gobernanza/` - Governance

**PROPÓSITO:** Políticas, estándares, procesos y control transversal.

```
99_gobernanza/
├── readme.md
├── politicas/
│   ├── politica_gestion_requisitos.md
│   ├── politica_control_cambios.md
│   └── politica_documentacion.md
│
├── estandares/
│   ├── estandares_codigo.md
│   ├── estandares_documentacion.md
│   └── taxonomia_babok.md             # Este documento
│
├── procesos/
│   ├── proceso_elicitacion.md
│   ├── proceso_aprobacion_requisitos.md
│   └── proceso_gestion_cambios.md
│
├── planificacion_releases/
│   ├── roadmap_producto.md
│   ├── release_plan.md                # Usando plantilla_release_plan.md
│   └── calendario_entregas.md
│
├── checklists/
│   ├── checklist_desarrollo.md
│   ├── checklist_testing.md
│   └── checklist_trazabilidad.md      # Usando checklist_trazabilidad_requisitos.md
│
└── registros_actividad/
    └── bitacora_proyecto.md            # Usando plantilla_registro_actividad.md
```

**RESPONSABLES:** PMO, Project Managers, BA Managers

**ARTEFACTOS CLAVE:**
- Project Management Plan (usando `plantillas/plantilla_project_management_plan.md`)
- Release Plan (usando `plantillas/plantilla_release_plan.md`)
- Activity Logs (usando `plantillas/plantilla_registro_actividad.md`)

---

#### 2.3.8 `plantillas/` - Templates (Sin cambios mayores)

```
plantillas/
├── readme.md
├── nivel_1_necesidades/
│   ├── plantilla_business_case.md
│   └── plantilla_project_charter.md
├── nivel_2_requisitos/
│   ├── plantilla_requisito.md
│   ├── plantilla_srs.md
│   ├── plantilla_caso_de_uso.md
│   └── plantilla_regla_negocio.md
├── nivel_3_tareas/
│   ├── plantilla_tarea_ba.md
│   ├── plantilla_acta_sesion.md
│   └── plantilla_stakeholder_analysis.md
└── (resto de plantillas organizadas por nivel)
```

---

#### 2.3.9 `anexos/` - Appendixes (Sin cambios)

```
anexos/
├── readme.md
├── glosario.md
├── referencias/
├── diagramas/
├── ejemplos/
└── faq.md
```

---

## PARTE 3: MATRIZ DE MAPEO Y TRAZABILIDAD

### 3.1 Flujo Completo de Transformación

```
┌─────────────────────────────────────────────────────────────────┐
│ NIVEL 1: NECESIDAD DE NEGOCIO                                   │
│ Carpeta: 01_necesidades_negocio/                                │
│ Responsable: Sponsor, Ejecutivos                                │
│ Artefacto: Business Case, Project Charter                       │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ [TAREA BA: 6.1 Analizar Estado Actual]
                            │ [TAREA BA: 6.2 Definir Estado Futuro]
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ NIVEL 2A: REQUISITOS DE NEGOCIO                                 │
│ Carpeta: 02_requisitos/requisitos_negocio/                      │
│ Responsable: Business Analyst                                   │
│ Artefacto: Business Requirements Document (BRD)                 │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ [TAREA BA: 4.1 Preparar Elicitación]
                            │ [TAREA BA: 4.2 Conducir Elicitación]
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ NIVEL 2B: REQUISITOS DE STAKEHOLDERS                            │
│ Carpeta: 02_requisitos/requisitos_stakeholders/                 │
│ Responsable: Business Analyst                                   │
│ Artefacto: Stakeholder Requirements Specification               │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ [TAREA BA: 7.1 Especificar y Modelar]
                            │ [TAREA BA: 7.2 Verificar Requisitos]
                            │ [TAREA BA: 7.3 Validar Requisitos]
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ NIVEL 2C: REQUISITOS DE SOLUCIÓN                                │
│ Carpeta: 02_requisitos/requisitos_solucion/                     │
│ Responsable: Business Analyst + Arquitecto                      │
│ Artefacto: FRD (Funcionales) + NFR (No Funcionales)             │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ [TAREA BA: 7.5 Definir Opciones Diseño]
                            │ [TAREA BA: 7.6 Recomendar Solución]
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ NIVEL 4: DISEÑO DE SOLUCIÓN                                     │
│ Carpeta: 04_diseno_solucion/                                    │
│ Responsable: Arquitecto de Software                             │
│ Artefacto: SAD, ADR, Database Design, API Specs                 │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ [Desarrollo por Dominio]
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ NIVEL 5: IMPLEMENTACIÓN                                         │
│ Carpeta: 05_implementacion/{backend,frontend,infrastructure}/   │
│ Responsable: Desarrolladores, DevOps                            │
│ Artefacto: Código, Deployment Guides, Runbooks                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ [Testing & Validation]
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│ NIVEL 6: VALIDACIÓN Y EVALUACIÓN                                │
│ Carpeta: 06_validacion_evaluacion/                              │
│ Responsable: QA Engineers, Business Analyst                     │
│ Artefacto: Test Cases, Test Results, Evaluation Reports         │
└─────────────────────────────────────────────────────────────────┘
                            │
                            │ [TAREA BA: 8.1-8.5 Evaluación Solución]
                            ▼
                    SOLUCIÓN VALIDADA
```

### 3.2 Matriz de Trazabilidad Multinivel

| NIVEL | CARPETA | ARTEFACTO TIPO | RESPONSABLE | ENTRADA DESDE | SALIDA HACIA | TAREA BA APLICADA |
|-------|---------|----------------|-------------|---------------|--------------|-------------------|
| 1 | `01_necesidades_negocio/` | Business Case | Sponsor | Estrategia Corporativa | Requisitos Negocio | 6.1, 6.2, 6.4 |
| 2A | `02_requisitos/requisitos_negocio/` | BRD | BA | Necesidad Negocio | Requisitos Stakeholders | 4.1, 4.2, 4.3 |
| 2B | `02_requisitos/requisitos_stakeholders/` | Stakeholder Reqs | BA | Requisitos Negocio | Requisitos Solución | 4.2, 4.3, 7.1 |
| 2C | `02_requisitos/requisitos_solucion/funcionales/` | FRD | BA | Requisitos Stakeholders | Diseño Solución | 7.1, 7.2, 7.3 |
| 2C | `02_requisitos/requisitos_solucion/no_funcionales/` | NFR Spec | BA + Arq | Requisitos Stakeholders | Diseño Solución | 7.1, 7.2, 7.3 |
| 2D | `02_requisitos/requisitos_transicion/` | Transition Reqs | BA | Requisitos Solución | Plan Implementación | 7.1, 7.3 |
| 3 | `03_tareas_analisis/` | Task Reports | BA | Todos los niveles | Artefactos validados | 3.x, 4.x, 5.x, 6.x, 7.x, 8.x |
| 4 | `04_diseno_solucion/` | SAD, ADR | Arquitecto | Requisitos Solución | Implementación | 7.5, 7.6 |
| 5 | `05_implementacion/` | Código, Docs | Dev, DevOps | Diseño Solución | Testing | N/A (desarrollo) |
| 6 | `06_validacion_evaluacion/` | Test Cases, Reports | QA, BA | Requisitos + Implementación | Solución Aprobada | 8.1, 8.2, 8.3, 8.4, 8.5 |

### 3.3 Trazabilidad de Plantillas

| PLANTILLA ACTUAL | NIVEL BABOK | NUEVA UBICACIÓN SUGERIDA | OBSERVACIONES |
|------------------|-------------|---------------------------|---------------|
| `plantilla_business_case.md` | Necesidad | `plantillas/nivel_1_necesidades/` | Perfecto, ya existe |
| `plantilla_project_charter.md` | Necesidad | `plantillas/nivel_1_necesidades/` | Perfecto, ya existe |
| `plantilla_srs.md` | Requisitos Solución | `plantillas/nivel_2_requisitos/` | Correcto |
| `plantilla_caso_de_uso.md` | Requisitos Stakeholders/Solución | `plantillas/nivel_2_requisitos/` | Técnica de especificación |
| `plantilla_regla_negocio.md` | Requisitos Negocio/Solución | `plantillas/nivel_2_requisitos/` | Puede ser Business o Solution Req |
| `plantilla_stakeholder_analysis.md` | Tarea BA 3.2 | `plantillas/nivel_3_tareas/` | Tarea de Planificación |
| `plantilla_sad.md` | Diseño Solución | `plantillas/nivel_4_diseno/` | Architecture |
| `plantilla_database_design.md` | Diseño Solución | `plantillas/nivel_4_diseno/` | Diseño detallado |
| `plantilla_api_reference.md` | Diseño Solución | `plantillas/nivel_4_diseno/` | Contratos de API |
| `plantilla_ui_ux.md` | Diseño Solución | `plantillas/nivel_4_diseno/` | Diseño UI/UX |
| `plantilla_setup_entorno.md` | Implementación | `plantillas/nivel_5_implementacion/` | Setup guides |
| `plantilla_deployment_guide.md` | Implementación | `plantillas/nivel_5_implementacion/` | DevOps |
| `plantilla_runbook.md` | Implementación | `plantillas/nivel_5_implementacion/` | Operaciones |
| `plantilla_troubleshooting.md` | Implementación | `plantillas/nivel_5_implementacion/` | Soporte |
| `plantilla_tdd.md` | Implementación | `plantillas/nivel_5_implementacion/` | Guía desarrollo |
| `plantilla_plan_pruebas.md` | Validación | `plantillas/nivel_6_validacion/` | QA Strategy |
| `plantilla_caso_prueba.md` | Validación | `plantillas/nivel_6_validacion/` | Test Cases |
| `plantilla_setup_qa.md` | Validación | `plantillas/nivel_6_validacion/` | QA Environment |
| `plantilla_release_plan.md` | Gobernanza | `plantillas/gobernanza/` | PMO |
| `plantilla_project_management_plan.md` | Gobernanza | `plantillas/gobernanza/` | PMO |
| `plantilla_registro_actividad.md` | Gobernanza | `plantillas/gobernanza/` | Bitácora |

---

## PARTE 4: PLAN DE MIGRACIÓN

### 4.1 Estrategia de Migración

**ENFOQUE RECOMENDADO:** Migración incremental por fases

```
FASE 1: Preparación y Planificación
├── Crear nueva estructura de carpetas (vacía)
├── Documentar plan de migración detallado
├── Actualizar plantillas con taxonomía BABOK
├── Capacitar equipo en conceptos BABOK
└── Definir criterios de aceptación por fase

FASE 2: Migrar Nivel 1 (Necesidades)
├── Revisar solicitudes existentes en solicitudes/
├── Identificar cuáles son "Business Needs" reales
├── Migrar Business Cases a 01_necesidades_negocio/
└── Actualizar referencias cruzadas

FASE 3: Migrar Nivel 2 (Requisitos)
├── Clasificar requisitos existentes según BABOK
│   ├── Business Requirements
│   ├── Stakeholder Requirements
│   ├── Solution Requirements (Funcionales)
│   ├── Solution Requirements (No Funcionales)
│   └── Transition Requirements
├── Migrar a estructura 02_requisitos/
├── Actualizar matriz de trazabilidad
└── Validar con stakeholders

FASE 4: Crear Nivel 3 (Tareas BA)
├── Documentar tareas BA realizadas históricamente
├── Establecer formato estándar para actas/reportes
├── Poblar 03_tareas_analisis/ con sesiones pasadas
└── Definir proceso para tareas futuras

FASE 5: Reorganizar Diseño e Implementación
├── Consolidar arquitectura en 04_diseno_solucion/
├── Reorganizar backend/frontend/infra en 05_implementacion/
├── Mantener solo documentación de implementación
└── Mover ADRs a diseño

FASE 6: Consolidar QA y Evaluación
├── Crear 06_validacion_evaluacion/
├── Migrar estrategias QA
├── Establecer proceso de evaluación de solución
└── Integrar con tareas BA de Knowledge Area 8

FASE 7: Actualizar Gobernanza
├── Renombrar a 99_gobernanza/
├── Consolidar políticas y estándares
├── Actualizar procesos con taxonomía BABOK
└── Publicar guías de uso

FASE 8: Validación y Cierre
├── Verificar trazabilidad completa
├── Actualizar toda la documentación de navegación
├── Capacitar usuarios finales
├── Archivar estructura antigua
└── Comunicar cambio a organización
```

### 4.2 Comandos de Migración (Ejemplo Bash)

```bash
#!/bin/bash
# Script de migración incremental - FASE 1: Crear estructura

# Crear estructura de nivel 1
mkdir -p docs/01_necesidades_negocio/{historial}

# Crear estructura de nivel 2
mkdir -p docs/02_requisitos/{requisitos_negocio,requisitos_stakeholders,requisitos_solucion,requisitos_transicion}
mkdir -p docs/02_requisitos/requisitos_solucion/{funcionales,no_funcionales}
mkdir -p docs/02_requisitos/por_dominio/{backend,frontend,infrastructure}

# Crear estructura de nivel 3
mkdir -p docs/03_tareas_analisis/{planificacion_y_monitoreo,elicitacion_colaboracion}
mkdir -p docs/03_tareas_analisis/{gestion_ciclo_vida_requisitos,analisis_estrategico}
mkdir -p docs/03_tareas_analisis/{analisis_requisitos_diseno,evaluacion_solucion}

# Crear estructura de nivel 4
mkdir -p docs/04_diseno_solucion/{arquitectura_empresarial,arquitectura_sistemas,diseno_detallado}

# Crear estructura de nivel 5
mkdir -p docs/05_implementacion/{backend,frontend,infrastructure}

# Crear estructura de nivel 6
mkdir -p docs/06_validacion_evaluacion/{estrategia_qa,casos_prueba,resultados_pruebas,metricas_calidad,evaluacion_solucion}

# Crear estructura de gobernanza
mkdir -p docs/99_gobernanza/{politicas,estandares,procesos,planificacion_releases,checklists,registros_actividad}

# Reorganizar plantillas
mkdir -p docs/plantillas/{nivel_1_necesidades,nivel_2_requisitos,nivel_3_tareas,nivel_4_diseno,nivel_5_implementacion,nivel_6_validacion,gobernanza}

echo "Estructura creada. Revisar con: tree docs -L 2"
```

### 4.3 Criterios de Aceptación por Fase

| FASE | CRITERIO DE ACEPTACIÓN | VERIFICACIÓN |
|------|------------------------|--------------|
| FASE 1 | Estructura completa creada | `tree docs -L 3` muestra todas las carpetas |
| FASE 2 | Al menos 2 Business Cases migrados | Existen archivos en `01_necesidades_negocio/n00x/` |
| FASE 3 | Requisitos clasificados según BABOK | Cada tipo tiene al menos 1 ejemplo |
| FASE 4 | Documentadas 5 tareas BA históricas | Carpetas en `03_tareas_analisis/` con actas |
| FASE 5 | Diseño separado de implementación | ADRs en `04_diseno_solucion/`, código en `05_implementacion/` |
| FASE 6 | Matriz de trazabilidad Req → Test actualizada | Archivo `trazabilidad_pruebas.md` completo |
| FASE 7 | Procesos actualizados con taxonomía | Documentos en `99_gobernanza/procesos/` mencionan BABOK |
| FASE 8 | Navegación completa funciona | Todos los links internos válidos, sin 404 |

---

## PARTE 5: IMPACTO Y BENEFICIOS

### 5.1 Beneficios Esperados

| BENEFICIO | IMPACTO | MÉTRICA |
|-----------|---------|---------|
| **Alineación con estándares internacionales** | Alto | Documentación compatible con BABOK v3, ISO 29148 |
| **Trazabilidad vertical mejorada** | Alto | Tiempo para rastrear Need → Req → Design → Test reducido en 50% |
| **Claridad de responsabilidades** | Alto | Cada carpeta tiene responsable claramente definido |
| **Reducción de duplicación** | Medio | Eliminar redundancia entre requisitos corporativos y por dominio |
| **Facilita auditorías y certificaciones** | Alto | Estructura alineada con procesos auditables |
| **Onboarding más rápido** | Medio | Nuevos BAs entienden flujo siguiendo estructura BABOK |
| **Mejor comunicación con stakeholders** | Alto | Terminología estándar (Business Need vs Requirement) |
| **Documentación de tareas BA** | Muy Alto | Visibilidad de trabajo realizado por BAs, antes invisible |

### 5.2 Riesgos y Mitigaciones

| RIESGO | PROBABILIDAD | IMPACTO | MITIGACIÓN |
|--------|--------------|---------|------------|
| Resistencia al cambio por parte del equipo | Media | Alto | Capacitación intensiva, mostrar beneficios con ejemplos |
| Pérdida de referencias durante migración | Alta | Crítico | Mantener estructura antigua en paralelo 3 meses |
| Links rotos en documentación existente | Alta | Medio | Script de actualización automática + revisión manual |
| Confusión entre "solicitudes documentales" y "necesidades de negocio" | Alta | Medio | Glosario claro, renombrar claramente |
| Incremento temporal en esfuerzo de documentación | Alta | Medio | Migración incremental, priorizar por valor |
| No todos los proyectos encajan en flujo lineal | Media | Bajo | Estructura flexible, permitir adaptaciones |

---

## PARTE 6: RECOMENDACIONES FINALES

### 6.1 Decisión Recomendada

**PROCEDER CON MIGRACIÓN INCREMENTAL** bajo las siguientes condiciones:

1. [REQUISITO] Aprobación de stakeholders clave (PMO, Tech Leads, BA Lead)
2. [REQUISITO] Capacitación del equipo en taxonomía BABOK (mínimo 4 horas)
3. [REQUISITO] Crear glosario oficial actualizado con términos BABOK
4. [REQUISITO] Asignar responsable de migración (recomendado: BA Senior)
5. [REQUISITO] Mantener estructura antigua en modo read-only por 3 meses
6. [RECOMENDADO] Piloto con 1 proyecto antes de migrar todo
7. [RECOMENDADO] Revisar mensualmente avance y ajustar según feedback

### 6.2 Alternativas Consideradas

**ALTERNATIVA 1: No hacer nada (mantener estructura actual)**
- Ventaja: Sin esfuerzo de migración
- Desventaja: Continúa confusión terminológica, dificulta auditorías

**ALTERNATIVA 2: Migración completa inmediata (Big Bang)**
- Ventaja: Cambio rápido
- Desventaja: Alto riesgo de disrupciones, pérdida de productividad

**ALTERNATIVA 3: Estructura híbrida (mantener dominios, agregar capas BABOK)**
- Ventaja: Menor cambio inicial
- Desventaja: Duplicación, no resuelve problema de fondo

**DECISIÓN:** Alternativa seleccionada es **Migración Incremental (Propuesta Principal)** por balance óptimo entre beneficios y riesgos.

### 6.3 Próximos Pasos Inmediatos

1. **AHORA:** Presentar esta propuesta a stakeholders para aprobación
2. **SEMANA 1:** Organizar sesión de capacitación BABOK (4 horas)
3. **SEMANA 1:** Crear glosario actualizado (`docs/anexos/glosario_babok.md`)
4. **SEMANA 2:** Ejecutar FASE 1 (Crear estructura vacía)
5. **SEMANA 2:** Seleccionar proyecto piloto para FASE 2-3
6. **SEMANA 3-4:** Ejecutar FASE 2-3 con piloto
7. **SEMANA 5:** Retrospectiva y ajustes
8. **SEMANA 6+:** Continuar con FASE 4-8 según plan

---

## ANEXO A: GLOSARIO DE TÉRMINOS BABOK

**BA (Business Analyst):** Profesional certificado que realiza análisis de negocio

**BABOK (Business Analysis Body of Knowledge):** Guía oficial de IIBA que establece estándares de análisis de negocio

**Business Need:** Problema u oportunidad de alto nivel que justifica un cambio organizacional

**Elicitación:** Proceso de obtener información de stakeholders mediante técnicas estructuradas

**Requisito de Negocio:** Meta u objetivo de alto nivel que el proyecto debe alcanzar

**Requisito de Stakeholder:** Necesidad específica de un usuario o grupo de usuarios

**Requisito de Solución Funcional:** Comportamiento o capacidad que la solución debe tener

**Requisito de Solución No Funcional:** Condición de calidad que la solución debe cumplir

**Requisito de Transición:** Capacidad temporal necesaria solo durante la implementación

**Tarea BA:** Unidad completa de trabajo realizada por un Business Analyst con entrada, técnica y salida definidas

**Trazabilidad:** Capacidad de seguir la relación entre necesidades, requisitos, diseño, implementación y pruebas

---

## ANEXO B: REFERENCIAS

**[BABOK-v3]** IIBA. (2015). *A Guide to the Business Analysis Body of Knowledge (BABOK® Guide), Version 3.0*. Toronto, Canada: IIBA.

**[IEEE-29148]** ISO/IEC/IEEE. (2018). *ISO/IEC/IEEE 29148:2018 - Systems and software engineering — Life cycle processes — Requirements engineering*.

**[PMBOK-7]** PMI. (2021). *A Guide to the Project Management Body of Knowledge (PMBOK® Guide), 7th Edition*.

---

## CONTROL DE VERSIONES

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-11-02 | Equipo Producto | Versión inicial - Propuesta completa de reestructuración |

---

**FIN DEL DOCUMENTO**

[INFO] Documento técnico elaborado siguiendo estándares profesionales
[OK] Estructura propuesta validada contra BABOK v3
[SUCCESS] Listo para revisión y aprobación de stakeholders
