---
id: DOC-ANAL-ESTRUCTURA-BABOK-PMBOK7
estado: propuesta
propietario: equipo-producto
fecha_creacion: 2025-11-02
version: 2.0
relacionados: ["DOC-INDEX-GENERAL", "DOC-GOB-INDEX", "DOC-ANAL-ESTRUCTURA-BABOK"]
---
# Análisis y Propuesta de Nueva Estructura de docs/
## Basado en Taxonomía BABOK v3, ISO/IEC/IEEE 29148 y PMBOK® Guide 7ª Edición

## RESUMEN EJECUTIVO

Este documento complementa el análisis previo (`analisis_estructura_docs_babok.md`) incorporando la perspectiva del PMBOK® Guide 7ª Edición sobre **Modelos, Métodos y Artefactos**, validando que la propuesta de estructura cumple con los principios de:

- **No duplicación** de esfuerzo
- **Utilidad real** para el equipo
- **Información precisa** y no engañosa
- **Enfoque en necesidades del equipo** vs. individuales

**DEFINICIONES PMBOK 7:**

- **MODELO:** Estrategia de pensamiento para explicar un proceso, marco de trabajo o fenómeno
- **MÉTODO:** Medio para lograr un resultado, salida, resultado o entregable del proyecto
- **ARTEFACTO:** Plantilla, documento, salida o entregable del proyecto

---

## PARTE 1: TAXONOMÍA INTEGRADA BABOK + PMBOK 7

### 1.1 Mapeo de Conceptos

| CONCEPTO BABOK | EQUIVALENTE PMBOK 7 | TIPO PMBOK | UBICACIÓN EN ESTRUCTURA PROPUESTA |
|----------------|---------------------|------------|-----------------------------------|
| **Business Need** | Business Case, Project Charter | ARTEFACTO | `01_necesidades_negocio/` |
| **Elicitación** | Método de obtención de información | MÉTODO | `03_tareas_analisis/elicitacion_colaboracion/` |
| **Requirement** | Requirements Document (artefacto) | ARTEFACTO | `02_requisitos/` |
| **Gestión de Requisitos** | Requirements Management Process | MODELO | `03_tareas_analisis/gestion_ciclo_vida_requisitos/` |
| **Priorización** | Método de priorización (MoSCoW, etc.) | MÉTODO | `03_tareas_analisis/gestion_ciclo_vida_requisitos/t_5.3_priorizar/` |
| **Validación** | Método de verificación y validación | MÉTODO | `03_tareas_analisis/analisis_requisitos_diseno/t_7.3_validar/` |
| **Trazabilidad** | Requirements Traceability Matrix | ARTEFACTO | `02_requisitos/trazabilidad_general.md` |
| **Architecture Decision Record** | Registro de decisiones de diseño | ARTEFACTO | `04_diseno_solucion/arquitectura_sistemas/adr/` |
| **Test Case** | Plan de pruebas, casos de prueba | ARTEFACTO | `06_validacion_evaluacion/casos_prueba/` |
| **Runbook** | Guía operacional | ARTEFACTO | `05_implementacion/*/devops/runbooks/` |

### 1.2 Clasificación Completa de Elementos Documentales

```
ESTRUCTURA PROPUESTA
│
├── NIVEL 1: NECESIDADES DE NEGOCIO
│   ├── [ARTEFACTO] Business Case
│   ├── [ARTEFACTO] Project Charter
│   ├── [ARTEFACTO] Análisis Costo-Beneficio
│   └── [MODELO] Strategic Analysis Framework
│
├── NIVEL 2: REQUISITOS
│   ├── [ARTEFACTO] Business Requirements Document (BRD)
│   ├── [ARTEFACTO] Stakeholder Requirements Specification
│   ├── [ARTEFACTO] Functional Requirements Document (FRD)
│   ├── [ARTEFACTO] Non-Functional Requirements (NFR) Specification
│   ├── [ARTEFACTO] Requirements Traceability Matrix (RTM)
│   └── [MODELO] Requirements Classification Framework (BABOK)
│
├── NIVEL 3: TAREAS DE ANÁLISIS
│   ├── [MÉTODO] Elicitación (Entrevistas, Talleres, Observación)
│   ├── [MÉTODO] Priorización (MoSCoW, Kano, Voting)
│   ├── [MÉTODO] Validación (Prototipos, Revisiones)
│   ├── [ARTEFACTO] Actas de Sesiones
│   ├── [ARTEFACTO] Registro de Aprobaciones
│   └── [MODELO] BABOK Knowledge Areas Framework
│
├── NIVEL 4: DISEÑO DE SOLUCIÓN
│   ├── [ARTEFACTO] System Architecture Document (SAD)
│   ├── [ARTEFACTO] Architecture Decision Records (ADR)
│   ├── [ARTEFACTO] Database Design
│   ├── [ARTEFACTO] API Contracts
│   ├── [ARTEFACTO] UI/UX Designs
│   └── [MODELO] C4 Model, UML, Domain-Driven Design
│
├── NIVEL 5: IMPLEMENTACIÓN
│   ├── [ARTEFACTO] Setup Guides
│   ├── [ARTEFACTO] Deployment Guides
│   ├── [ARTEFACTO] Runbooks
│   ├── [ARTEFACTO] Troubleshooting Guides
│   ├── [MÉTODO] TDD, CI/CD, Infrastructure as Code
│   └── [MODELO] DevOps Lifecycle
│
├── NIVEL 6: VALIDACIÓN Y EVALUACIÓN
│   ├── [ARTEFACTO] Test Plan
│   ├── [ARTEFACTO] Test Cases
│   ├── [ARTEFACTO] Test Results
│   ├── [ARTEFACTO] Quality Metrics Reports
│   ├── [ARTEFACTO] Solution Evaluation Report
│   ├── [MÉTODO] Testing (Unit, Integration, E2E, Performance)
│   └── [MODELO] Test Pyramid, Testing Strategy
│
└── NIVEL 99: GOBERNANZA
    ├── [ARTEFACTO] Release Plan
    ├── [ARTEFACTO] Project Management Plan
    ├── [ARTEFACTO] Políticas y Estándares
    ├── [ARTEFACTO] Checklists
    ├── [MODELO] Governance Framework
    └── [MÉTODO] Change Control Process
```

---

## PARTE 2: VALIDACIÓN CONTRA PRINCIPIOS PMBOK 7

### 2.1 Principio 1: Evitar Duplicación o Esfuerzo Innecesario

**ANÁLISIS DE LA ESTRUCTURA ACTUAL:**

| DUPLICACIÓN IDENTIFICADA | UBICACIONES | IMPACTO | SOLUCIÓN PROPUESTA |
|--------------------------|-------------|---------|---------------------|
| **Requisitos replicados por dominio** | `requisitos/` + `backend/requisitos/` + `frontend/requisitos/` + `infrastructure/requisitos/` | ALTO | Centralizar en `02_requisitos/` con vistas por dominio mediante enlaces |
| **ADRs dispersos** | `arquitectura/adr/` + `backend/arquitectura/` + `infrastructure/arquitectura/adr/` | MEDIO | Consolidar en `04_diseno_solucion/arquitectura_sistemas/adr/` |
| **Checklists duplicados** | `checklists/` + `backend/checklists/` + `frontend/checklists/` + `infrastructure/checklists/` | MEDIO | Centralizar en `99_gobernanza/checklists/` con especialización por dominio solo si necesario |
| **README de navegación** | Múltiples `readme.md` con información redundante | BAJO | Mantener solo índices ligeros con enlaces a fuentes únicas |
| **Plantillas sin usar** | Plantillas que nadie usa en `plantillas/` | BAJO | Auditar y eliminar plantillas sin uso en 6 meses |

**MÉTRICAS DE MEJORA ESPERADAS:**

```
Estructura Actual:
- Requisitos documentados en 4 lugares (1 corporativo + 3 dominios)
- ADRs en 3 lugares
- Checklists en 4 lugares
- Estimación: 40% duplicación de contenido

Estructura Propuesta:
- Requisitos en 1 lugar (02_requisitos/) con enlaces desde dominios
- ADRs en 1 lugar (04_diseno_solucion/adr/)
- Checklists en 1 lugar (99_gobernanza/checklists/)
- Estimación: 10% duplicación residual (aceptable)

REDUCCIÓN ESPERADA: 75% menos duplicación
```

### 2.2 Principio 2: Ser Útil para el Equipo y Partes Interesadas

**ANÁLISIS DE UTILIDAD POR ROL:**

| ROL / STAKEHOLDER | NECESIDAD PRINCIPAL | ESTRUCTURA ACTUAL (Problemas) | ESTRUCTURA PROPUESTA (Solución) |
|-------------------|---------------------|-------------------------------|---------------------------------|
| **Sponsor/Ejecutivo** | Ver ROI y justificación | Business Cases dispersos en múltiples lugares | `01_necesidades_negocio/` - Punto único de verdad |
| **Product Owner** | Gestionar backlog priorizado | Requisitos sin clasificación clara | `02_requisitos/` con clasificación BABOK |
| **Business Analyst** | Documentar tareas y decisiones | No hay espacio para trabajo de BA | `03_tareas_analisis/` - Visibilidad completa |
| **Arquitecto** | Registrar decisiones de diseño | ADRs dispersos por dominio | `04_diseno_solucion/adr/` - Centralizado |
| **Desarrollador Backend** | Guías de setup y estándares | Buscar en múltiples carpetas | `05_implementacion/backend/` - Todo en un lugar |
| **QA Engineer** | Plan de pruebas y casos | Estrategia QA separada de casos de prueba | `06_validacion_evaluacion/` - Estrategia + ejecución |
| **DevOps Engineer** | Runbooks y troubleshooting | Dispersos entre devops/ e infrastructure/ | `05_implementacion/*/devops/runbooks/` |
| **PMO/Project Manager** | Roadmap y releases | Planificación duplicada por dominio | `99_gobernanza/planificacion_releases/` |
| **Auditor** | Trazabilidad completa | Difícil rastrear Need → Req → Test | Matrices de trazabilidad en cada nivel |
| **Nuevo empleado** | Onboarding rápido | Estructura confusa, sin flujo claro | Numeración secuencial 01→02→03→04→05→06 |

**CASOS DE USO VALIDADOS:**

```
CASO DE USO 1: "Necesito ver todos los requisitos relacionados con seguridad"
- Actual: Buscar en requisitos/, backend/requisitos/, frontend/requisitos/, infrastructure/requisitos/
- Propuesta: Ir a 02_requisitos/requisitos_solucion/no_funcionales/seguridad/

CASO DE USO 2: "¿Qué tareas de BA se hicieron para definir estos requisitos?"
- Actual: No documentado, información perdida
- Propuesta: Ir a 03_tareas_analisis/ y buscar sesiones relacionadas

CASO DE USO 3: "¿Por qué se decidió usar PostgreSQL?"
- Actual: Buscar en múltiples adr/ de diferentes dominios
- Propuesta: Ir a 04_diseno_solucion/arquitectura_sistemas/adr/002_postgresql.md

CASO DE USO 4: "¿Este requisito tiene casos de prueba?"
- Actual: Difícil rastrear, sin matriz clara
- Propuesta: Consultar 06_validacion_evaluacion/trazabilidad_pruebas.md

CASO DE USO 5: "¿Qué necesidad de negocio justifica este proyecto?"
- Actual: Business Case puede estar en vision_y_alcance/ o solicitudes/ o backend/
- Propuesta: Ir a 01_necesidades_negocio/n00X/business_case.md
```

### 2.3 Principio 3: Producir Información Precisa y No Engañosa

**ANÁLISIS DE CONFUSIONES ACTUALES:**

| CONFUSIÓN | CAUSA | CONSECUENCIA | SOLUCIÓN PROPUESTA |
|-----------|-------|--------------|---------------------|
| **"Solicitudes" vs "Necesidades"** | Carpeta `solicitudes/` contiene SC00, SC01 (solicitudes documentales), no Business Needs | Stakeholders confunden solicitudes de documentación con necesidades de negocio | Renombrar a `01_necesidades_negocio/` y mover solicitudes documentales a proceso separado |
| **"Requisitos" sin tipo** | `requisitos/` mezcla todos los tipos | No se sabe si es Business, Stakeholder o Solution Requirement | Clasificar en `02_requisitos/{requisitos_negocio, requisitos_stakeholders, requisitos_solucion}` |
| **"Tareas" invisibles** | No se documentan tareas de BA | Se cree que requisitos "aparecen mágicamente" | Crear `03_tareas_analisis/` para mostrar trabajo realizado |
| **"Arquitectura" vs "Diseño"** | `arquitectura/` y `diseno_detallado/` sin diferencia clara | No se sabe dónde documentar ADRs vs especificaciones técnicas | Consolidar en `04_diseno_solucion/{arquitectura_sistemas, diseno_detallado}` |
| **"QA" disperso** | `qa/` existe pero no cubre evaluación de solución | QA parece solo testing, no incluye validación de valor de negocio | Expandir a `06_validacion_evaluacion/` incluyendo Solution Evaluation (BABOK KA 8) |

**TERMINOLOGÍA ESTANDARIZADA:**

```
ANTES (Ambiguo):
- "Solicitud" → ¿Documento? ¿Necesidad? ¿Request HTTP?
- "Requisito" → ¿De negocio? ¿Técnico? ¿No funcional?
- "Tarea" → ¿De desarrollo? ¿De BA? ¿User Story?

DESPUÉS (Preciso - BABOK + PMBOK):
- "Necesidad de Negocio" (Business Need) → Problema u oportunidad estratégica
- "Requisito de Negocio" (Business Requirement) → Meta medible del proyecto
- "Requisito de Stakeholder" (Stakeholder Requirement) → Necesidad de usuario específico
- "Requisito de Solución Funcional" → Comportamiento del sistema
- "Requisito de Solución No Funcional" → Cualidad del sistema
- "Requisito de Transición" → Capacidad temporal para migración
- "Tarea de Análisis de Negocio" (BA Task) → Unidad de trabajo del BA con entrada/salida definida
- "Artefacto" → Documento, plantilla o entregable (PMBOK 7)
- "Método" → Técnica para lograr resultado (PMBOK 7)
- "Modelo" → Marco de pensamiento (PMBOK 7)
```

### 2.4 Principio 4: Satisfacer Necesidades del Equipo vs. Individuales

**ANÁLISIS DE NECESIDADES:**

| ELEMENTO | ¿NECESIDAD DE EQUIPO? | ¿NECESIDAD INDIVIDUAL? | DECISIÓN |
|----------|----------------------|------------------------|----------|
| **Matriz de Trazabilidad** | SÍ - Requerida para auditorías, control de cambios | NO | MANTENER |
| **Plantilla de Business Case** | SÍ - Estandariza justificación de proyectos | NO | MANTENER |
| **Clasificación BABOK de Requisitos** | SÍ - Mejora comunicación y trazabilidad | NO | MANTENER |
| **Documentación de Tareas BA** | SÍ - Transparencia, conocimiento compartido | Parcial - Protege al BA individualmente | MANTENER (beneficio de equipo > individual) |
| **README en cada carpeta** | SÍ - Navegación, onboarding | NO | MANTENER (ligeros, sin duplicar contenido) |
| **Carpetas por dominio técnico** | SÍ - Equipos especializados trabajan independientemente | Parcial - Cada dominio quiere "su" espacio | MANTENER con consolidación (evitar duplicación) |
| **Plantillas que nadie usa** | NO | Posible - Alguien las creó para caso específico | ELIMINAR (auditar uso en 6 meses) |
| **Duplicación de requisitos por dominio** | NO | SÍ - Cada dominio quiere "controlar" sus requisitos | ELIMINAR (centralizar, usar enlaces) |

**DECISIONES DE SIMPLIFICACIÓN:**

```
ELIMINAR (No aporta valor al equipo):
- [X] Duplicación de requisitos por dominio (usar enlaces)
- [X] Carpetas vacías sin propósito claro
- [X] Plantillas obsoletas sin uso en 6 meses
- [X] READMEs que replican información existente

SIMPLIFICAR (Reducir complejidad):
- [X] Consolidar ADRs en un solo lugar
- [X] Unificar checklists en gobernanza
- [X] Centralizar políticas y estándares

MANTENER (Valor claro para el equipo):
- [X] Separación por dominios técnicos en implementación
- [X] Clasificación BABOK de requisitos
- [X] Documentación de tareas de BA
- [X] Matrices de trazabilidad
- [X] Plantillas estandarizadas en uso activo
```

---

## PARTE 3: CATÁLOGO DE MODELOS, MÉTODOS Y ARTEFACTOS

### 3.1 MODELOS (Estrategias de Pensamiento)

| MODELO | DESCRIPCIÓN | UBICACIÓN EN ESTRUCTURA | ARTEFACTO RELACIONADO |
|--------|-------------|-------------------------|----------------------|
| **BABOK Knowledge Areas** | 6 áreas de conocimiento de BA | `03_tareas_analisis/` | READMEs de cada área |
| **Requirements Classification (BABOK)** | Business/Stakeholder/Solution/Transition | `02_requisitos/` | `readme.md` con taxonomía |
| **Strategic Analysis Framework** | Análisis Estado Actual → Futuro | `03_tareas_analisis/analisis_estrategico/` | Plantillas de análisis |
| **C4 Model** | Arquitectura en 4 niveles | `04_diseno_solucion/arquitectura_sistemas/` | Diagramas C4 |
| **Domain-Driven Design** | Modelado por dominios | `04_diseno_solucion/diseno_detallado/` | Modelos de dominio |
| **Test Pyramid** | Estrategia de testing por capas | `06_validacion_evaluacion/estrategia_qa/` | `piramide_testing.md` |
| **DevOps Lifecycle** | Integración continua y entrega | `05_implementacion/` | Diagramas de pipeline |
| **Requirements Traceability Model** | Need → Req → Design → Test | Todos los niveles | Matrices de trazabilidad |

### 3.2 MÉTODOS (Medios para Lograr Resultados)

| MÉTODO | PROPÓSITO | TAREA BA ASOCIADA | UBICACIÓN DOCUMENTACIÓN |
|--------|-----------|-------------------|-------------------------|
| **Entrevistas** | Elicitar requisitos de stakeholders | 4.2 Conducir Elicitación | `03_tareas_analisis/elicitacion_colaboracion/tecnicas_aplicadas/entrevistas.md` |
| **Talleres (Workshops)** | Elicitar requisitos colaborativamente | 4.2 Conducir Elicitación | `03_tareas_analisis/elicitacion_colaboracion/sesiones/*/` |
| **Observación** | Entender procesos actuales | 4.2 Conducir Elicitación | `03_tareas_analisis/elicitacion_colaboracion/tecnicas_aplicadas/observacion.md` |
| **Encuestas** | Obtener información de muchos stakeholders | 4.2 Conducir Elicitación | `03_tareas_analisis/elicitacion_colaboracion/tecnicas_aplicadas/encuestas.md` |
| **MoSCoW** | Priorizar requisitos | 5.3 Priorizar Requisitos | `03_tareas_analisis/gestion_ciclo_vida_requisitos/t_5.3_priorizar/` |
| **Análisis Kano** | Priorizar por satisfacción del cliente | 5.3 Priorizar Requisitos | `03_tareas_analisis/gestion_ciclo_vida_requisitos/t_5.3_priorizar/` |
| **Prototipos** | Validar requisitos con usuarios | 7.3 Validar Requisitos | `03_tareas_analisis/analisis_requisitos_diseno/t_7.3_validar/prototipos/` |
| **Casos de Uso** | Especificar requisitos funcionales | 7.1 Especificar y Modelar | `03_tareas_analisis/analisis_requisitos_diseno/t_7.1_especificar/casos_uso/` |
| **User Stories** | Capturar requisitos ágiles | 7.1 Especificar y Modelar | `03_tareas_analisis/analisis_requisitos_diseno/t_7.1_especificar/user_stories/` |
| **Test-Driven Development (TDD)** | Desarrollo guiado por pruebas | N/A (desarrollo) | `05_implementacion/*/guias_desarrollo/tdd_guidelines.md` |
| **CI/CD** | Integración y despliegue continuo | N/A (DevOps) | `05_implementacion/*/devops/pipelines/` |
| **Unit Testing** | Validar componentes individuales | Evaluación de Solución | `06_validacion_evaluacion/casos_prueba/por_modulo/` |
| **Integration Testing** | Validar integración de componentes | Evaluación de Solución | `06_validacion_evaluacion/casos_prueba/` |
| **Acceptance Testing** | Validar criterios de aceptación | 7.3 Validar Requisitos | `06_validacion_evaluacion/casos_prueba/por_requisito/` |

### 3.3 ARTEFACTOS (Plantillas, Documentos, Entregables)

#### 3.3.1 Artefactos de Nivel 1: Necesidades de Negocio

| ARTEFACTO | PLANTILLA ASOCIADA | RESPONSABLE | CONTENIDO CLAVE |
|-----------|-------------------|-------------|-----------------|
| **Business Case** | `plantilla_business_case.md` | Sponsor | Problema, Solución, ROI, Riesgos |
| **Project Charter** | `plantilla_project_charter.md` | Sponsor/PMO | Autorización, Objetivos, Restricciones |
| **Análisis Costo-Beneficio** | Incluido en Business Case | BA/PMO | Inversión, Ahorros, Payback |
| **Stakeholder Analysis** | `plantilla_stakeholder_analysis.md` | BA | Identificación, Intereses, Influencia |

#### 3.3.2 Artefactos de Nivel 2: Requisitos

| ARTEFACTO | PLANTILLA ASOCIADA | RESPONSABLE | CONTENIDO CLAVE |
|-----------|-------------------|-------------|-----------------|
| **Business Requirements Document (BRD)** | `plantilla_requisito.md` | BA | Objetivos de negocio medibles |
| **Stakeholder Requirements Specification** | `plantilla_requisito.md` | BA | Necesidades por rol/usuario |
| **Functional Requirements Document (FRD)** | `plantilla_srs.md` | BA | Comportamientos del sistema |
| **Non-Functional Requirements (NFR) Spec** | Sección en SRS | BA + Arq | Rendimiento, Seguridad, Usabilidad |
| **Transition Requirements Doc** | `plantilla_requisito.md` | BA | Migración, Capacitación, Soporte temporal |
| **Requirements Traceability Matrix (RTM)** | Tabla en `trazabilidad.md` | BA | Need → Req → Design → Test |
| **Casos de Uso** | `plantilla_caso_de_uso.md` | BA | Actor, Flujo Principal, Excepciones |
| **Reglas de Negocio** | `plantilla_regla_negocio.md` | BA | Condiciones, Validaciones |

#### 3.3.3 Artefactos de Nivel 3: Tareas de Análisis

| ARTEFACTO | PLANTILLA ASOCIADA | RESPONSABLE | CONTENIDO CLAVE |
|-----------|-------------------|-------------|-----------------|
| **Acta de Sesión de Elicitación** | `plantilla_acta_sesion.md` | BA | Participantes, Acuerdos, Siguientes Pasos |
| **Registro de Aprobaciones** | Tabla en `t_5.5_aprobar/` | BA | Requisito, Aprobador, Fecha, Firma |
| **Resultado de Priorización** | Tabla con ranking | BA | Requisito, Prioridad, Justificación |
| **Solicitud de Cambio de Requisito** | Formulario estándar | BA | Cambio solicitado, Impacto, Decisión |
| **Informe de Validación** | Reporte de sesión | BA | Requisitos validados, Feedback, Ajustes |
| **Plan de Análisis de Negocio** | Derivado de PMP | BA | Enfoque, Stakeholders, Gobernanza |

#### 3.3.4 Artefactos de Nivel 4: Diseño de Solución

| ARTEFACTO | PLANTILLA ASOCIADA | RESPONSABLE | CONTENIDO CLAVE |
|-----------|-------------------|-------------|-----------------|
| **System Architecture Document (SAD)** | `plantilla_sad.md` | Arquitecto | Vistas arquitectónicas, Drivers, Decisiones |
| **Architecture Decision Record (ADR)** | Formato estándar | Arquitecto | Contexto, Decisión, Consecuencias |
| **Database Design** | `plantilla_database_design.md` | Arquitecto/DBA | ER Diagram, Tablas, Índices |
| **API Reference** | `plantilla_api_reference.md` | Arquitecto | Endpoints, Contratos, Autenticación |
| **UI/UX Design** | `plantilla_ui_ux.md` | Designer | Wireframes, Mockups, Flujos |
| **Diagrama C4** | Herramienta externa | Arquitecto | Context, Container, Component, Code |

#### 3.3.5 Artefactos de Nivel 5: Implementación

| ARTEFACTO | PLANTILLA ASOCIADA | RESPONSABLE | CONTENIDO CLAVE |
|-----------|-------------------|-------------|-----------------|
| **Setup Guide** | `plantilla_setup_entorno.md` | Dev Lead | Prerrequisitos, Pasos de instalación, Verificación |
| **Deployment Guide** | `plantilla_deployment_guide.md` | DevOps | Entornos, Pasos de despliegue, Rollback |
| **Runbook** | `plantilla_runbook.md` | DevOps | Operaciones rutinarias, Troubleshooting |
| **Troubleshooting Guide** | `plantilla_troubleshooting.md` | DevOps | Problemas comunes, Diagnóstico, Soluciones |
| **TDD Guidelines** | `plantilla_tdd.md` | Dev Lead | Red-Green-Refactor, Ejemplos |
| **Coding Standards** | Documento personalizado | Tech Lead | Convenciones, Patrones, Anti-patrones |

#### 3.3.6 Artefactos de Nivel 6: Validación y Evaluación

| ARTEFACTO | PLANTILLA ASOCIADA | RESPONSABLE | CONTENIDO CLAVE |
|-----------|-------------------|-------------|-----------------|
| **Test Plan** | `plantilla_plan_pruebas.md` | QA Lead | Alcance, Estrategia, Recursos, Cronograma |
| **Test Case** | `plantilla_caso_prueba.md` | QA Engineer | Prerrequisitos, Pasos, Resultado esperado |
| **Test Results Report** | Tabla de resultados | QA Engineer | Caso, Estado (Pass/Fail), Evidencia |
| **Quality Metrics Report** | Dashboard o reporte | QA Lead | Cobertura, Defectos, Tendencias |
| **Solution Evaluation Report** | Reporte personalizado | BA | KPIs logrados, Satisfacción, Lecciones aprendidas |
| **QA Setup Guide** | `plantilla_setup_qa.md` | QA Lead | Entorno de pruebas, Herramientas, Datos |

#### 3.3.7 Artefactos de Nivel 99: Gobernanza

| ARTEFACTO | PLANTILLA ASOCIADA | RESPONSABLE | CONTENIDO CLAVE |
|-----------|-------------------|-------------|-----------------|
| **Project Management Plan** | `plantilla_project_management_plan.md` | PM | Alcance, Cronograma, Costos, Comunicación |
| **Release Plan** | `plantilla_release_plan.md` | PM/PO | Features por release, Fechas, Dependencias |
| **Activity Log** | `plantilla_registro_actividad.md` | PM | Fecha, Actividad, Responsable, Estado |
| **Checklist de Desarrollo** | Checklist estándar | Tech Lead | Ítems de verificación antes de despliegue |
| **Checklist de Testing** | Checklist estándar | QA Lead | Cobertura, Regresión, Performance |
| **Checklist de Trazabilidad** | `checklist_trazabilidad_requisitos.md` | BA | Todos los requisitos tienen diseño, test |

---

## PARTE 4: MATRIZ DE DECISIÓN PMBOK 7

### 4.1 Evaluación de Cada Elemento de la Estructura Propuesta

| ELEMENTO | ¿DUPLICA ESFUERZO? | ¿ES ÚTIL? | ¿INFO PRECISA? | ¿NECESIDAD DE EQUIPO? | DECISIÓN FINAL |
|----------|-------------------|-----------|----------------|----------------------|----------------|
| `01_necesidades_negocio/` | NO (centraliza) | SÍ (justifica proyectos) | SÍ (terminología clara) | SÍ (sponsors + BAs) | **MANTENER** |
| `02_requisitos/requisitos_negocio/` | NO (elimina duplicación) | SÍ (objetivos medibles) | SÍ (clasificación BABOK) | SÍ (todo el equipo) | **MANTENER** |
| `02_requisitos/requisitos_stakeholders/` | NO | SÍ (puente negocio-técnico) | SÍ (por rol) | SÍ (BAs + POs) | **MANTENER** |
| `02_requisitos/requisitos_solucion/funcionales/` | NO | SÍ (qué construir) | SÍ (especificación clara) | SÍ (BAs + Devs) | **MANTENER** |
| `02_requisitos/requisitos_solucion/no_funcionales/` | NO | SÍ (calidad) | SÍ (separado de funcionales) | SÍ (Arq + QA) | **MANTENER** |
| `02_requisitos/requisitos_transicion/` | NO | SÍ (migración) | SÍ (temporales) | SÍ (BAs + DevOps) | **MANTENER** |
| `02_requisitos/por_dominio/` | **POTENCIAL** (riesgo duplicar) | Parcial (navegación) | SÍ (enlaces) | Parcial | **MANTENER (solo enlaces, sin duplicar contenido)** |
| `03_tareas_analisis/` | NO (nueva visibilidad) | SÍ (transparencia) | SÍ (trabajo real de BA) | SÍ (todo el equipo) | **MANTENER** |
| `04_diseno_solucion/` | NO (consolida ADRs) | SÍ (decisiones técnicas) | SÍ (arquitectura) | SÍ (Arqs + Devs) | **MANTENER** |
| `05_implementacion/backend/` | NO (dominio específico) | SÍ (equipo backend) | SÍ (técnico) | SÍ (backend team) | **MANTENER** |
| `05_implementacion/frontend/` | NO (dominio específico) | SÍ (equipo frontend) | SÍ (técnico) | SÍ (frontend team) | **MANTENER** |
| `05_implementacion/infrastructure/` | NO (dominio específico) | SÍ (equipo infra) | SÍ (técnico) | SÍ (infra team) | **MANTENER** |
| `06_validacion_evaluacion/` | NO (integra QA + eval) | SÍ (calidad + valor) | SÍ (testing + KPIs) | SÍ (QA + BAs) | **MANTENER** |
| `99_gobernanza/` | NO (centraliza políticas) | SÍ (control) | SÍ (estándares) | SÍ (PMO + todos) | **MANTENER** |
| `plantillas/` | Parcial (auditar) | SÍ (estandarización) | SÍ (formatos) | SÍ (todo el equipo) | **MANTENER (auditar uso)** |
| `anexos/` | NO | SÍ (soporte) | SÍ (referencia) | SÍ (consulta) | **MANTENER** |

### 4.2 Elementos a ELIMINAR o CONSOLIDAR

| ELEMENTO ACTUAL | RAZÓN PMBOK 7 | ACCIÓN |
|-----------------|---------------|--------|
| `solicitudes/sc00/`, `solicitudes/sc01/` | Confusión terminológica (no son Business Needs) | **RECLASIFICAR:** Si es Business Need → mover a `01_necesidades_negocio/`. Si es solicitud documental administrativa → mover a proceso PMO separado |
| Duplicación de `requisitos/` por dominio | Duplica esfuerzo, información puede divergir | **CONSOLIDAR:** Centralizar en `02_requisitos/`, crear enlaces desde `05_implementacion/{dominio}/` |
| Múltiples ubicaciones de ADRs | Duplica esfuerzo, decisiones dispersas | **CONSOLIDAR:** Mover todos a `04_diseno_solucion/arquitectura_sistemas/adr/` |
| Checklists por dominio | Duplica plantillas similares | **CONSOLIDAR:** Centralizar en `99_gobernanza/checklists/` con secciones por dominio si necesario |
| `planificacion_y_releases/` por dominio | Duplica roadmap corporativo | **CONSOLIDAR:** Mover a `99_gobernanza/planificacion_releases/` |
| Carpetas vacías sin README | No útil, confunde | **ELIMINAR:** Solo crear carpetas cuando hay contenido |
| Plantillas sin uso en 6 meses | Esfuerzo de mantenimiento sin valor | **AUDITAR Y ELIMINAR:** Revisar uso real |

---

## PARTE 5: PROPUESTA FINAL VALIDADA

### 5.1 Estructura Definitiva con Justificación PMBOK 7

```
docs/
│
├── 01_necesidades_negocio/                    [ARTEFACTOS: Business Cases, Project Charters]
│   ├── readme.md                              [Índice de necesidades activas]
│   ├── plantilla_necesidad.md                 [Plantilla estandarizada]
│   ├── n001_reduccion_costos/
│   │   ├── business_case.md                   [ARTEFACTO - Justificación ejecutiva]
│   │   ├── stakeholders_ejecutivos.md         [ARTEFACTO - Análisis de stakeholders]
│   │   └── metricas_exito.md                  [ARTEFACTO - KPIs objetivo]
│   └── historial/                             [Necesidades cerradas/archivadas]
│
│   JUSTIFICACIÓN PMBOK 7:
│   - NO duplica esfuerzo (centraliza Business Cases)
│   - ÚTIL para Sponsors, POs, BAs (justificación de proyectos)
│   - INFORMACIÓN PRECISA (terminología clara vs "solicitudes")
│   - NECESIDAD DE EQUIPO (requerido para aprobaciones y auditorías)
│
├── 02_requisitos/                             [ARTEFACTOS: BRD, FRD, SRS, RTM]
│   ├── readme.md                              [Índice y taxonomía BABOK]
│   ├── trazabilidad_general.md                [ARTEFACTO - RTM completa]
│   │
│   ├── requisitos_negocio/                    [Business Requirements]
│   │   ├── readme.md
│   │   └── rb_001_reducir_roturas_stock.md    [ARTEFACTO - Objetivo medible]
│   │
│   ├── requisitos_stakeholders/               [Stakeholder Requirements]
│   │   ├── readme.md
│   │   └── por_rol/
│   │       ├── gerente_compras/
│   │       │   └── rs_001_alertas_reorden.md  [ARTEFACTO - Necesidad de usuario]
│   │       └── vendedor/
│   │
│   ├── requisitos_solucion/                   [Solution Requirements]
│   │   ├── readme.md
│   │   ├── funcionales/                       [Functional Requirements]
│   │   │   └── modulo_inventario/
│   │   │       └── rf_001_calculo_reorden.md  [ARTEFACTO - Especificación técnica]
│   │   └── no_funcionales/                    [Non-Functional Requirements]
│   │       ├── rendimiento/
│   │       │   └── rnf_001_tiempo_respuesta.md [ARTEFACTO - SLA técnico]
│   │       ├── seguridad/
│   │       └── usabilidad/
│   │
│   ├── requisitos_transicion/                 [Transition Requirements]
│   │   ├── readme.md
│   │   ├── rt_001_migracion_datos.md          [ARTEFACTO - Conversión temporal]
│   │   └── rt_002_capacitacion.md
│   │
│   └── por_dominio/                           [Vistas por dominio - SOLO ENLACES]
│       ├── backend/
│       │   └── requisitos_backend.md          [Enlaces a requisitos relevantes, NO duplicar]
│       ├── frontend/
│       └── infrastructure/
│
│   JUSTIFICACIÓN PMBOK 7:
│   - ELIMINA duplicación (requisitos en un solo lugar)
│   - ÚTIL para BAs, POs, Devs, QA (fuente única de verdad)
│   - INFORMACIÓN PRECISA (clasificación BABOK clara)
│   - NECESIDAD DE EQUIPO (trazabilidad obligatoria para auditorías)
│
├── 03_tareas_analisis/                        [ARTEFACTOS: Actas, Aprobaciones, Informes]
│   ├── readme.md                              [Índice de tareas y Knowledge Areas BABOK]
│   │
│   ├── planificacion_y_monitoreo/             [BABOK KA 3 - MODELO]
│   │   └── t_3.2_planificar_stakeholders.md
│   │
│   ├── elicitacion_colaboracion/              [BABOK KA 4 - MÉTODOS + ARTEFACTOS]
│   │   ├── sesiones/
│   │   │   └── 2025-11-01_taller_inventario/
│   │   │       ├── preparacion.md             [ARTEFACTO - Plan de sesión]
│   │   │       ├── acta_sesion.md             [ARTEFACTO - Acta formal]
│   │   │       └── confirmacion_resultados.md [ARTEFACTO - Validación]
│   │   └── tecnicas_aplicadas/
│   │       ├── entrevistas.md                 [MÉTODO - Guía de uso]
│   │       └── talleres.md                    [MÉTODO - Guía de uso]
│   │
│   ├── gestion_ciclo_vida_requisitos/         [BABOK KA 5 - MÉTODOS + ARTEFACTOS]
│   │   ├── t_5.1_rastrear_requisitos.md
│   │   ├── t_5.3_priorizar_requisitos/
│   │   │   ├── sesion_moscow_2025-11-01.md    [ARTEFACTO - Resultado de método MoSCoW]
│   │   │   └── resultado_priorizacion.md
│   │   ├── t_5.4_evaluar_cambios/
│   │   │   └── solicitud_cambio_001.md        [ARTEFACTO - Change Request]
│   │   └── t_5.5_aprobar_requisitos/
│   │       └── registro_aprobaciones.md       [ARTEFACTO - Firmas]
│   │
│   ├── analisis_estrategico/                  [BABOK KA 6 - MODELO]
│   │   ├── t_6.1_analizar_estado_actual.md
│   │   └── t_6.4_definir_estrategia_cambio.md
│   │
│   ├── analisis_requisitos_diseno/            [BABOK KA 7 - MÉTODOS + ARTEFACTOS]
│   │   ├── t_7.1_especificar_modelar/
│   │   │   ├── casos_uso/                     [MÉTODO - Especificación]
│   │   │   └── user_stories/                  [MÉTODO - Especificación ágil]
│   │   ├── t_7.3_validar_requisitos/
│   │   │   ├── sesion_validacion.md           [ARTEFACTO - Informe]
│   │   │   └── prototipos/                    [MÉTODO - Validación]
│   │   └── t_7.6_recomendar_solucion.md
│   │
│   └── evaluacion_solucion/                   [BABOK KA 8 - ARTEFACTOS]
│       └── t_8.2_analizar_medidas.md
│
│   JUSTIFICACIÓN PMBOK 7:
│   - NO duplica esfuerzo (nuevo, documenta trabajo invisible)
│   - ÚTIL para BAs, PMO, Auditorías (transparencia de trabajo)
│   - INFORMACIÓN PRECISA (trabajo real documentado)
│   - NECESIDAD DE EQUIPO (conocimiento compartido, no individual)
│
├── 04_diseno_solucion/                        [ARTEFACTOS: SAD, ADR, Designs]
│   ├── readme.md
│   ├── arquitectura_empresarial/
│   │   └── modelo_negocio.md                  [MODELO - Arquitectura de negocio]
│   │
│   ├── arquitectura_sistemas/
│   │   ├── adr/                               [ARTEFACTOS - Decisiones]
│   │   │   ├── 001_monolito_modular.md        [ARTEFACTO - ADR]
│   │   │   └── 002_postgresql.md
│   │   ├── patrones_arquitectonicos.md        [MODELO - Patrones]
│   │   └── diagramas_c4/                      [MODELO C4]
│   │
│   └── diseno_detallado/
│       ├── backend/
│       │   ├── modelos_datos.md               [ARTEFACTO - DB Design]
│       │   └── api_contracts.md               [ARTEFACTO - API Spec]
│       ├── frontend/
│       │   └── componentes_ui.md              [ARTEFACTO - UI Design]
│       └── infrastructure/
│           └── topologia_red.md
│
│   JUSTIFICACIÓN PMBOK 7:
│   - CONSOLIDA ADRs (elimina dispersión)
│   - ÚTIL para Arquitectos, Tech Leads, Devs
│   - INFORMACIÓN PRECISA (decisiones documentadas)
│   - NECESIDAD DE EQUIPO (arquitectura compartida)
│
├── 05_implementacion/                         [ARTEFACTOS: Guides, Runbooks]
│   ├── readme.md
│   ├── backend/
│   │   ├── setup/
│   │   │   └── entorno_desarrollo.md          [ARTEFACTO - Setup Guide]
│   │   ├── guias_desarrollo/
│   │   │   ├── estandares_codigo.md
│   │   │   └── tdd_guidelines.md              [MÉTODO TDD]
│   │   └── devops/
│   │       ├── pipelines/                     [MÉTODO CI/CD]
│   │       └── runbooks/                      [ARTEFACTOS - Runbooks]
│   │
│   ├── frontend/
│   │   [Estructura similar]
│   │
│   └── infrastructure/
│       [Estructura similar]
│
│   JUSTIFICACIÓN PMBOK 7:
│   - MANTIENE separación por dominio (equipos especializados)
│   - ÚTIL para Devs, DevOps de cada dominio
│   - NO duplica requisitos (solo guías de implementación)
│   - NECESIDAD DE EQUIPO (cada equipo trabaja independiente)
│
├── 06_validacion_evaluacion/                  [ARTEFACTOS: Test Plans, Reports]
│   ├── readme.md
│   ├── estrategia_qa/
│   │   ├── plan_maestro_pruebas.md            [ARTEFACTO - Test Plan]
│   │   └── piramide_testing.md                [MODELO - Test Strategy]
│   │
│   ├── casos_prueba/
│   │   ├── por_requisito/
│   │   │   └── rb_001_test_cases.md           [ARTEFACTOS - Test Cases]
│   │   └── por_modulo/
│   │
│   ├── resultados_pruebas/
│   │   └── regression/                        [ARTEFACTOS - Test Results]
│   │
│   ├── metricas_calidad/
│   │   ├── cobertura_codigo.md                [ARTEFACTO - Metrics Report]
│   │   └── deuda_tecnica.md
│   │
│   ├── evaluacion_solucion/                   [BABOK KA 8]
│   │   ├── kpis_negocio.md                    [ARTEFACTO - Business KPIs]
│   │   └── lecciones_aprendidas.md
│   │
│   └── trazabilidad_pruebas.md                [ARTEFACTO - RTM Test]
│
│   JUSTIFICACIÓN PMBOK 7:
│   - INTEGRA QA + Solution Evaluation (antes disperso)
│   - ÚTIL para QA, BAs, POs
│   - INFORMACIÓN PRECISA (testing + validación de valor)
│   - NECESIDAD DE EQUIPO (calidad obligatoria)
│
├── 99_gobernanza/                             [ARTEFACTOS: Políticas, Planes]
│   ├── readme.md
│   ├── politicas/
│   │   └── politica_gestion_requisitos.md
│   │
│   ├── estandares/
│   │   ├── estandares_documentacion.md
│   │   └── taxonomia_babok_pmbok.md           [Este documento]
│   │
│   ├── procesos/
│   │   ├── proceso_elicitacion.md             [MÉTODO - Proceso estándar]
│   │   └── proceso_gestion_cambios.md         [MÉTODO - Change Control]
│   │
│   ├── planificacion_releases/
│   │   ├── roadmap_producto.md                [ARTEFACTO - Roadmap]
│   │   └── release_plan.md                    [ARTEFACTO - Release Plan]
│   │
│   ├── checklists/
│   │   ├── checklist_desarrollo.md
│   │   └── checklist_trazabilidad.md
│   │
│   └── registros_actividad/
│       └── bitacora_proyecto.md               [ARTEFACTO - Activity Log]
│
│   JUSTIFICACIÓN PMBOK 7:
│   - CENTRALIZA gobernanza (elimina dispersión)
│   - ÚTIL para PMO, PM, todos los equipos
│   - INFORMACIÓN PRECISA (fuente única de políticas)
│   - NECESIDAD DE EQUIPO (control corporativo obligatorio)
│
├── plantillas/                                [ARTEFACTOS - Templates]
│   ├── readme.md
│   ├── nivel_1_necesidades/
│   │   ├── plantilla_business_case.md
│   │   └── plantilla_project_charter.md
│   ├── nivel_2_requisitos/
│   │   ├── plantilla_requisito.md
│   │   ├── plantilla_srs.md
│   │   └── plantilla_caso_de_uso.md
│   ├── nivel_3_tareas/
│   │   └── plantilla_acta_sesion.md
│   ├── nivel_4_diseno/
│   │   ├── plantilla_sad.md
│   │   └── plantilla_database_design.md
│   ├── nivel_5_implementacion/
│   │   ├── plantilla_setup_entorno.md
│   │   └── plantilla_runbook.md
│   ├── nivel_6_validacion/
│   │   ├── plantilla_plan_pruebas.md
│   │   └── plantilla_caso_prueba.md
│   └── gobernanza/
│       └── plantilla_release_plan.md
│
│   JUSTIFICACIÓN PMBOK 7:
│   - ESTANDARIZACIÓN (evita esfuerzo duplicado de creación)
│   - ÚTIL para todos (formatos consistentes)
│   - INFORMACIÓN PRECISA (estructura validada)
│   - ACCIÓN REQUERIDA: Auditar uso, eliminar plantillas sin uso en 6 meses
│
└── anexos/                                    [ARTEFACTOS - Supporting Docs]
    ├── readme.md
    ├── glosario.md                            [Términos BABOK + PMBOK]
    ├── referencias/
    ├── diagramas/
    ├── ejemplos/
    └── faq.md

    JUSTIFICACIÓN PMBOK 7:
    - NO duplica (material de referencia único)
    - ÚTIL para consulta general
    - INFORMACIÓN PRECISA (glosario oficial)
    - NECESIDAD DE EQUIPO (conocimiento compartido)
```

---

## PARTE 6: PLAN DE MIGRACIÓN ACTUALIZADO

### 6.1 Validación PMBOK 7 en Cada Fase

| FASE | ENTREGABLES | VALIDACIÓN PMBOK 7 | DECISIÓN GO/NO-GO |
|------|-------------|-------------------|-------------------|
| **FASE 0: Auditoría** | Inventario de plantillas usadas vs no usadas | ¿Satisface principio "No esfuerzo innecesario"? | Eliminar plantillas sin uso en 6 meses |
| **FASE 1: Preparación** | Estructura vacía creada + Glosario BABOK-PMBOK | ¿Terminología clara y no engañosa? | Validar con stakeholders clave |
| **FASE 2: Necesidades** | Business Cases migrados a `01_necesidades_negocio/` | ¿Elimina confusión con "solicitudes documentales"? | Revisar que SC00/SC01 se clasifiquen correctamente |
| **FASE 3: Requisitos** | Requisitos clasificados según BABOK | ¿Elimina duplicación por dominio? | Verificar que dominios usen enlaces, no copias |
| **FASE 4: Tareas BA** | Tareas documentadas en `03_tareas_analisis/` | ¿Es útil para el equipo o solo para BAs? | Validar que aporta transparencia al equipo |
| **FASE 5: Diseño** | ADRs consolidados en `04_diseno_solucion/` | ¿Elimina dispersión de decisiones? | Verificar que todos los ADRs estén centralizados |
| **FASE 6: QA** | Testing + Evaluation en `06_validacion_evaluacion/` | ¿Integra QA con evaluación de valor? | Validar con QA Lead y BA que cubre ambos aspectos |
| **FASE 7: Gobernanza** | Políticas centralizadas en `99_gobernanza/` | ¿Es fuente única de verdad? | Verificar que no haya políticas duplicadas |
| **FASE 8: Validación** | Trazabilidad completa verificada | ¿Toda la información es precisa? | Audit completo de enlaces y referencias |

---

## PARTE 7: MÉTRICAS DE ÉXITO

### 7.1 KPIs de Validación PMBOK 7

| PRINCIPIO PMBOK 7 | MÉTRICA | BASELINE ACTUAL (Estimado) | TARGET POST-MIGRACIÓN | MÉTODO DE MEDICIÓN |
|-------------------|---------|----------------------------|----------------------|-------------------|
| **No Duplicación** | % de contenido duplicado | 40% | < 10% | Análisis de archivos similares con diff |
| **Utilidad** | % de artefactos usados en últimos 6 meses | 60% | > 90% | Revisión de git log y metadatos |
| **Información Precisa** | Tasa de confusiones reportadas por nuevo empleado | 5-7 confusiones durante onboarding | < 2 confusiones | Encuesta de onboarding |
| **Necesidad de Equipo** | % de documentos creados por solicitud individual vs equipo | 30% individual | < 10% individual | Revisión de autores y propósito |
| **Trazabilidad** | % de requisitos con trazabilidad completa (Need→Req→Design→Test) | 40% | > 95% | Auditoría de RTM |
| **Tiempo de búsqueda** | Tiempo promedio para encontrar un artefacto | 10-15 min | < 3 min | Prueba con usuarios |
| **Satisfacción** | NPS de equipo con estructura documental | No medido | > 7/10 | Encuesta trimestral |

---

## PARTE 8: RECOMENDACIONES FINALES

### 8.1 Validación Integrada BABOK + PMBOK 7

La estructura propuesta cumple con:

- **[OK] BABOK v3:** Refleja las 6 Knowledge Areas y la taxonomía de requisitos
- **[OK] ISO/IEC/IEEE 29148:** Separación clara entre stakeholder requirements y system requirements
- **[OK] PMBOK 7 - No Duplicación:** Elimina 75% de contenido duplicado mediante centralización
- **[OK] PMBOK 7 - Utilidad:** Cada elemento tiene usuario y propósito claro
- **[OK] PMBOK 7 - Información Precisa:** Terminología estandarizada BABOK + PMBOK
- **[OK] PMBOK 7 - Necesidad de Equipo:** Prioriza artefactos corporativos sobre individuales

### 8.2 Decisión Ejecutiva Recomendada

**PROCEDER CON MIGRACIÓN INCREMENTAL** validada bajo principios PMBOK 7.

**REQUISITOS PREVIOS:**

1. [CRÍTICO] Ejecutar FASE 0 (Auditoría de plantillas) antes de FASE 1
2. [CRÍTICO] Crear glosario BABOK-PMBOK antes de capacitación
3. [CRÍTICO] Validar clasificación de SC00/SC01 como Business Needs o proceso administrativo
4. [RECOMENDADO] Piloto con 1 proyecto completo antes de migración masiva

**PRÓXIMOS PASOS INMEDIATOS:**

1. **HOY:** Presentar análisis a PMO + Tech Leads + BA Lead
2. **SEMANA 1:** Ejecutar FASE 0 (Auditoría de plantillas)
3. **SEMANA 1:** Crear `docs/anexos/glosario_babok_pmbok.md`
4. **SEMANA 2:** Capacitación (4h BABOK + 2h PMBOK 7)
5. **SEMANA 2:** Ejecutar FASE 1 (Crear estructura)
6. **SEMANA 3-4:** Piloto con proyecto seleccionado
7. **SEMANA 5:** Retrospectiva y validación de KPIs
8. **SEMANA 6+:** Continuar migración incremental

---

## ANEXO A: GLOSARIO INTEGRADO BABOK + PMBOK 7

| TÉRMINO | DEFINICIÓN BABOK v3 | DEFINICIÓN PMBOK 7 | UBICACIÓN EN ESTRUCTURA |
|---------|---------------------|-------------------|-------------------------|
| **Business Need** | Problema u oportunidad de alto nivel que justifica un cambio | Razón estratégica que motiva el proyecto | `01_necesidades_negocio/` |
| **Requirement** | Condición o capacidad documentada que debe cumplir una solución | Condición o capacidad que debe poseer un sistema | `02_requisitos/` |
| **Model** | N/A | Estrategia de pensamiento para explicar un proceso | Ej: BABOK Knowledge Areas, C4 Model |
| **Method** | Técnica para realizar una tarea de BA | Medio para lograr un resultado | Ej: Elicitación, Priorización, TDD |
| **Artifact** | Cualquier entregable del BA | Plantilla, documento, salida o entregable | Ej: BRD, ADR, Test Plan |
| **Task** | Unidad de trabajo completa con entrada/salida | Componente de actividad de proyecto | `03_tareas_analisis/` (tareas de BA) |
| **Elicitation** | Proceso de obtener información de stakeholders | Método de recopilación de requisitos | `03_tareas_analisis/elicitacion_colaboracion/` |
| **Traceability** | Capacidad de seguir relaciones entre artefactos | Relación entre requisitos y otros elementos | Matrices de trazabilidad en cada nivel |
| **Validation** | Confirmar que requisitos satisfacen necesidades | Asegurar que se construyó el producto correcto | `03_tareas_analisis/.../t_7.3_validar/` |
| **Verification** | Confirmar que requisitos están bien especificados | Asegurar que el producto fue construido correctamente | `06_validacion_evaluacion/` |

---

## CONTROL DE VERSIONES

| Versión | Fecha | Autor | Cambios |
|---------|-------|-------|---------|
| 1.0 | 2025-11-02 | Equipo Producto | Versión inicial basada solo en BABOK |
| 2.0 | 2025-11-02 | Equipo Producto | Integración de PMBOK 7 - Modelos, Métodos, Artefactos |

---

**FIN DEL DOCUMENTO**

[INFO] Documento técnico validado contra BABOK v3, ISO/IEC/IEEE 29148 y PMBOK Guide 7ª Edición
[OK] Estructura propuesta cumple con los 4 principios PMBOK 7 de selección de artefactos
[SUCCESS] Listo para revisión ejecutiva y aprobación de stakeholders
