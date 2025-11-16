---
id: ADR-2025-009
estado: aceptada
propietario: architecture-team
ultima_actualizacion: 2025-11-09
relacionados:
  [
    "ADR_011_frontend_modular_monolith",
    "ADR_012_redux_toolkit_state_management",
    "ADR_013_webpack_bundler",
    "ADR_014_testing_strategy_jest_testing_library",
  ]
---

# ADR-2025-009: Postergacion de Implementacion Frontend

**Estado:** aceptada

**Fecha:** 2025-11-09

**Decisores:** Architecture Team, Product Owner, Tech Lead Backend

**Contexto tecnico:** Frontend + Product Strategy

## Contexto y Problema

El proyecto IACT tiene **4 ADRs de frontend** (ADR-011 a ADR-014) creados el 2025-11-06 que definen la arquitectura completa de un frontend React:

1. **ADR-011**: Modular Monolith (no microfrontends)
2. **ADR-012**: Redux Toolkit para state management
3. **ADR-013**: Webpack como bundler
4. **ADR-014**: Jest + Testing Library para testing

Adicionalmente, existen:

- Estructura de documentacion `docs/frontend/` preparada
- 2 requisitos funcionales: RF-010 (Pantalla login), RF-011 (Cambio password)
- Documentacion arquitectonica completa

**PROBLEMA CRITICO**: A la fecha 2025-11-09 (3 dias despues), **NO existe ninguna implementacion**:

- NO existe directorio `frontend/`
- NO hay codigo React
- NO hay package.json
- NO hay configuracion de Webpack
- NO hay tests

**Preguntas clave:**

- ¿Se requiere realmente un frontend custom o API-only es suficiente?
- ¿Hay recursos (desarrolladores frontend) disponibles?
- ¿Cual es la prioridad del frontend vs otras funcionalidades?
- ¿Que generacion de decisiones arquitectonicas sin implementacion?
- ¿Debemos implementar, postergar o cancelar el frontend?

**Restricciones actuales:**

- Backend Django + DRF esta 100% funcional y documentado
- API REST con 50+ endpoints disponibles (OpenAPI/Swagger)
- Sin equipo frontend dedicado identificado
- Focus actual: completar funcionalidades backend CORE

**Impacto:**

- **Estrategico**: Definir si IACT es API-only o full-stack
- **Recursos**: Asignacion de desarrolladores
- **Time-to-market**: Backend funcional vs esperar frontend
- **Documentacion**: Congruencia entre ADRs y codigo real

## Factores de Decision

- **Necesidad real**: ¿Usuarios requieren UI web o API es suficiente?
- **Recursos disponibles**: ¿Hay equipo frontend?
- **Prioridades**: Backend CORE vs frontend
- **Alternativas**: Herramientas third-party (Metabase, Grafana, Admin Django)
- **Time-to-market**: Valor entregable hoy vs futuro
- **Mantenibilidad**: Costo de mantener frontend custom

## Opciones Consideradas

### Opcion 1: Implementar Frontend Inmediatamente

**Descripcion:**
Comenzar implementacion siguiendo ADRs existentes (React + Redux + Webpack).

**Pros:**

- OK Arquitectura ya definida (ADRs completos)
- OK Requisitos funcionales claros
- OK Consistencia entre documentacion y codigo

**Contras:**

- NO Requiere equipo frontend (no identificado aun)
- NO Desvia recursos de backend CORE
- NO Time-to-market retrasado
- NO Alto costo de mantenimiento (2 codebases)
- NO Testing end-to-end complejo (frontend + backend)

---

### Opcion 2: Cancelar Frontend Permanentemente (API-Only)

**Descripcion:**
Declarar IACT como API-only project, eliminar ADRs y documentacion frontend.

**Pros:**

- OK Focus total en backend
- OK Menor complejidad
- OK Sin costo de mantenimiento frontend
- OK API puede consumirse por clientes externos

**Contras:**

- NO Usuarios sin UI amigable
- NO Requiere herramientas third-party para visualizacion
- NO ADRs existentes desperdiciados
- NO Dificil revertir decision en futuro

---

### Opcion 3: Postergar Frontend con Timeline Definido (Seleccionada)

**Descripcion:**
Postergar implementacion frontend hasta Q2 2026 (6 meses), enfocarse en backend CORE ahora, y usar herramientas third-party para visualizacion temporal.

**Fases:**

**Fase 1 (Actual - Q1 2026): Backend CORE**

- Completar funcionalidades backend prioritarias
- Estabilizar API REST
- Documentar exhaustivamente endpoints

**Fase 2 (Q1 2026): Evaluacion de Necesidad**

- Encuesta a usuarios finales
- Analisis de uso de API por clientes
- Decision GO/NO-GO para frontend

**Fase 3 (Q2 2026): Implementacion (si GO)**

- Contratar/asignar equipo frontend
- Implementar siguiendo ADRs existentes
- Rollout progresivo

**Herramientas Temporales**:

- Django Admin (personalizado) para CRUD basico
- Metabase para dashboards y reportes
- Postman/Swagger UI para exploracion de API
- Grafana para metricas operativas

**Pros:**

- OK Time-to-market rapido (backend disponible YA)
- OK Permite validar necesidad REAL de frontend
- OK ADRs preservados para implementacion futura
- OK Recursos enfocados en backend CORE
- OK Menor riesgo (decision reversible)
- OK Herramientas third-party cubren necesidad basica

**Contras:**

- NO UI limitada en fase inicial
- NO Experiencia usuario NO optima
- NO Requiere training en herramientas third-party
- NO Posible re-work si arquitectura cambia

---

## Decision

**Opcion elegida:** "Postergar Frontend con Timeline Definido (Q2 2026)"

**Justificacion:**

1. **Backend CORE es prioridad**: 11 apps Django funcionales, API REST completa, sistema de permisos granular
2. **Sin equipo frontend**: No hay recursos identificados para implementacion frontend custom
3. **Alternativas viables**: Django Admin + Metabase + Grafana cubren necesidades inmediatas
4. **Decision reversible**: ADRs preservados, arquitectura definida, re-activacion rapida
5. **Validacion de necesidad**: 6 meses permiten validar si frontend custom es realmente necesario
6. **Trade-offs aceptados**: UX NO optima temporalmente vs time-to-market y focus en backend

## Consecuencias

### Positivas

- OK Backend disponible INMEDIATAMENTE para consumo
- OK Recursos enfocados 100% en backend CORE
- OK Menor complejidad operativa (un solo codebase)
- OK Menor costo de infraestructura (no CI/CD frontend)
- OK ADRs preservados para future-proofing
- OK Decision basada en datos (evaluacion Q1 2026)

### Negativas

- WARNING Usuarios dependientes de herramientas third-party
- WARNING Experiencia usuario limitada en fase inicial
- WARNING Posible desmotivacion de stakeholders que esperaban UI
- WARNING Risk de re-work si arquitectura frontend cambia

### Neutrales

- INFO Django Admin requiere personalizacion
- INFO Training necesario en Metabase/Grafana
- INFO Evaluacion GO/NO-GO en Q1 2026

## Plan de Implementacion

### Fase 1: Backend CORE (Actual - Dic 2025)

**Objetivo**: Completar funcionalidades backend prioritarias

**Tareas**:

1. Finalizar migraciones pendientes (6 apps sin migrations)
2. Completar testing backend (cobertura > 90%)
3. Documentar exhaustivamente API REST (OpenAPI/Swagger)
4. Optimizar performance (query optimization, caching)
5. Hardening de seguridad (SQL injection, XSS, CSRF)

**Deliverables**:

- API REST 100% funcional
- Documentacion completa
- Coverage tests > 90%
- Security scan PASS

---

### Fase 2: Herramientas Temporales (Ene 2026)

**Objetivo**: Proveer UI basica usando herramientas third-party

**Tareas**:

1. **Django Admin Personalizado**
   - Customizar templates
   - Agregar dashboards basicos
   - Configurar permisos granulares

2. **Metabase Setup**
   - Conectar a PostgreSQL
   - Crear dashboards de DORA metrics
   - Crear reportes de analytics

3. **Grafana Setup** (opcional)
   - Metricas operativas
   - Monitoreo de performance

**Deliverables**:

- Django Admin funcional
- 10+ dashboards en Metabase
- Grafana configurado

---

### Fase 3: Evaluacion GO/NO-GO (Mar 2026)

**Objetivo**: Decidir si implementar frontend custom

**Criterios de Decision**:

1. **Usuarios solicitan UI custom**: > 70% en encuesta
2. **API NO suficiente**: Limitaciones identificadas
3. **Recursos disponibles**: Equipo frontend asignado
4. **ROI positivo**: Beneficio > costo de desarrollo + mantenimiento

**Escenarios**:

**GO (Implementar Frontend)**:

- Contratar/asignar 2-3 developers frontend
- Kickoff proyecto siguiendo ADRs existentes
- Timeline: 3-4 meses (Q2 2026)

**NO-GO (Mantener API-Only)**:

- Mejorar Django Admin
- Expandir Metabase dashboards
- Documentar API para clientes externos

---

### Fase 4: Implementacion (Abr-Jun 2026) - SI GO

**Objetivo**: Implementar frontend React siguiendo ADRs

**Sprint 1 (Abr 2026)**:

- Setup proyecto React + Webpack
- Estructura modular monolith
- Pantalla login (RF-010)

**Sprint 2 (May 2026)**:

- Dashboard modulo
- Redux Toolkit setup
- Cambio password (RF-011)

**Sprint 3 (Jun 2026)**:

- Reports modulo
- Testing (Jest + Testing Library)
- Deployment

**Deliverables**:

- Frontend React funcional
- 2 modulos implementados (dashboard, reports)
- Tests coverage > 80%
- CI/CD pipeline

---

## Validacion y Metricas

**Criterios de Exito (Fase 1 - Backend)**:

- API REST 100% documentada (OpenAPI/Swagger)
- Testing coverage > 90%
- Security scan PASS (NO vulnerabilities CRITICAL/HIGH)
- Performance: p95 response time < 200ms

**Criterios de Exito (Fase 2 - Herramientas Temporales)**:

- Django Admin funcional (CRUD para 11 models)
- Metabase dashboards (10+ reportes)
- User satisfaction > 60% (encuesta)

**Criterios GO/NO-GO (Fase 3)**:

- User survey: > 70% solicitan frontend custom
- ROI analysis: Beneficio > costo
- Team availability: 2-3 frontend devs

**Como medir**:

- User surveys (Google Forms)
- Analytics de uso de Django Admin
- Analytics de uso de Metabase
- Cost analysis (desarrollo + mantenimiento)

**Revision**:

- Fecha de evaluacion GO/NO-GO: 2026-03-31
- Responsable de seguimiento: Product Owner + Tech Lead

## Estado de ADRs Existentes

### ADR-011: Modular Monolith

**Estado actual**: SUSPENDIDO
**Accion**: Preservar documento, NO eliminar
**Razon**: Arquitectura valida si GO en Q2 2026

### ADR-012: Redux Toolkit

**Estado actual**: SUSPENDIDO
**Accion**: Preservar documento
**Razon**: State management definido para futura implementacion

### ADR-013: Webpack

**Estado actual**: SUSPENDIDO
**Accion**: Preservar documento
**Razon**: Bundler definido para futura implementacion

### ADR-014: Jest + Testing Library

**Estado actual**: SUSPENDIDO
**Accion**: Preservar documento
**Razon**: Testing strategy definida

**Nota**: Todos los ADRs de frontend mantienen estado "Aceptado" pero con implementacion suspendida. NO se eliminan para facilitar re-activacion rapida.

## Requisitos Funcionales Frontend

### RF-010: Pantalla Login

**Estado**: SUSPENDIDO
**Alternativa temporal**: Django Admin login
**Re-activacion**: Si GO en Q2 2026

### RF-011: Cambio Password

**Estado**: SUSPENDIDO
**Alternativa temporal**: Django Admin password change
**Re-activacion**: Si GO en Q2 2026

## Alternativas Descartadas

### Admin Frameworks (Django Jet, Grappelli)

**Por que se descarto:**

- Limitaciones de customizacion
- NO permite logica compleja de negocio
- UI NO moderna

### Low-Code Platforms (Retool, Appsmith)

**Por que se descarto:**

- Costo mensual alto (> $1000/mes)
- Vendor lock-in
- Limitaciones de integracion

### Vue.js o Angular en lugar de React

**Por que se descarto:**

- React ya decidido en ADR-011
- Cambio de decision requiere nuevo ADR
- React tiene mejor ecosistema para dashboards

## Referencias

### ADRs Relacionados

- [ADR-011: Frontend Modular Monolith](ADR_011_frontend_modular_monolith.md)
- [ADR-012: Redux Toolkit](ADR_012_redux_toolkit_state_management.md)
- [ADR-013: Webpack Bundler](ADR_013_webpack_bundler.md)
- [ADR-014: Testing Strategy](ADR_014_testing_strategy_jest_testing_library.md)

### Requisitos Funcionales

- [RF-010: Pantalla Login](../frontend/requisitos/funcionales/rf010_pantalla_login.md)
- [RF-011: Cambio Password](../frontend/requisitos/funcionales/rf011_cambio_password_ui.md)

### Backend API

- [OpenAPI/Swagger Documentation](http://localhost:8000/api/docs/)
- [API Schema](http://localhost:8000/api/schema/)

### Third-Party Tools

- [Metabase Documentation](https://www.metabase.com/docs/)
- [Django Admin Customization](https://docs.djangoproject.com/en/4.2/ref/contrib/admin/)
- [Grafana Documentation](https://grafana.com/docs/)

## Notas Adicionales

**Decision tomada en**: Sprint de analisis de congruencia docs-codigo (Nov 2025)
**Razon de postergacion**: Sin equipo frontend, backend CORE es prioridad
**Timeline de evaluacion**: Q1 2026 (Marzo 2026)

**Stakeholders informados**:

- Product Owner
- Tech Lead Backend
- Architecture Team
- Usuarios finales (comunicado via email)

**Comunicacion externa**:

> "El proyecto IACT priorizara completar funcionalidades backend CORE en Q4 2025 - Q1 2026. La interfaz de usuario estara disponible via Django Admin y Metabase temporalmente. La decision de implementar frontend React custom sera evaluada en Marzo 2026 basandose en feedback de usuarios y disponibilidad de recursos."

**Commitments**:

1. API REST 100% funcional para Enero 2026
2. Django Admin personalizado para Enero 2026
3. Metabase dashboards para Enero 2026
4. Evaluacion GO/NO-GO para Marzo 2026

**Lecciones aprendidas**:

1. NO crear ADRs sin plan de implementacion claro
2. Validar disponibilidad de recursos ANTES de decisiones arquitectonicas
3. ADRs requieren ownership y accountability
4. Documentacion sin codigo genera deuda tecnica (doc drift)

---

**Estado**: Implementado (postergacion activa)
**Proxima revision**: 2026-03-31 (Evaluacion GO/NO-GO)
**Impacto**: Backend-only architecture hasta Q2 2026, herramientas third-party para UI temporal
