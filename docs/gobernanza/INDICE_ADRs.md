---
title: Indice Maestro de Architecture Decision Records (ADRs)
date: 2025-11-13
domain: gobernanza
tipo: indice
status: active
---

# Indice Maestro de ADRs

Este documento contiene el indice completo de todas las decisiones arquitectonicas (Architecture Decision Records) del proyecto IACT.

**Ultima actualizacion**: 2025-11-13
**Total ADRs**: 21

---

## Sistema de Numeracion

**Formato Estandar**: `ADR-YYYY-XXX-descripcion.md`

- **YYYY**: Año de la decision (2025)
- **XXX**: Numero secuencial (001-999)
- **descripcion**: Descripcion corta en kebab-case

---

## Indice por Numero

### ADR_2025_001: Vagrant mod_wsgi
**Ubicacion**: `docs/infraestructura/ADR_2025_001-vagrant-mod-wsgi.md`
**Fecha**: 2025-01-15
**Estado**: Aceptada
**Dominio**: Infraestructura
**Propietario**: @equipo-arquitectura @equipo-devops

**Resumen**: Entorno de desarrollo con Vagrant y aprovisionamiento de bases de datos.

**Contexto**: Replica infraestructura de datos en produccion (PostgreSQL + MariaDB) para entorno local.

---

### ADR_2025_002: Suite Calidad Codigo
**Ubicacion**: `docs/infraestructura/ADR_2025_002-suite-calidad-codigo.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Infraestructura
**Propietario**: @equipo-devops @equipo-qa

**Resumen**: Suite de herramientas para asegurar calidad de codigo.

---

### ADR_2025_003: DORA SDLC Integration
**Ubicacion**: `docs/ai/ADR_2025_003-dora-sdlc-integration.md`
**Fecha**: 2025-11-06
**Estado**: Aceptada
**Dominio**: AI/ML + Infrastructure
**Propietario**: @arquitecto-senior @tech-lead @devops-lead

**Resumen**: Integracion de metricas DORA con agentes SDLC.

**Contexto**: Medir impacto real de agentes IA en performance de entrega de software usando metricas DORA (Deployment Frequency, Lead Time for Changes, Change Failure Rate, Time to Restore Service).

**Relacionado**: FASES_IMPLEMENTACION_IA.md, ESTRATEGIA_IA.md, AGENTES_SDLC.md, ADR_2025_002

---

### ADR_2025_004: Centralized Log Storage
**Ubicacion**: `docs/backend/ADR_2025_004-centralized-log-storage.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Backend
**Propietario**: @equipo-backend @equipo-devops

**Resumen**: Almacenamiento centralizado de logs en Cassandra.

**Relacionado**: ADR_2025_003 (DORA metrics - Capa 1), OBSERVABILITY_LAYERS.md, RNF-002

---

### ADR_2025_005: Grupos Funcionales Sin Jerarquia
**Ubicacion**: `docs/backend/ADR_2025_005-grupos-funcionales-sin-jerarquia.md`
**Fecha**: 2025-11-07
**Estado**: Aceptada
**Dominio**: Backend
**Propietario**: @equipo-backend @equipo-ba @arquitecto-principal

**Resumen**: Sistema de permisos con grupos funcionales sin jerarquia.

**Contexto**: Escalar modelo de permisos granulares para 19 funciones, 130+ capacidades, sin roles rigidos (Admin, Supervisor, Agent).

**Relacionado**: DOC-REQ-INDICE-MAESTRO-PERMISOS, RF-001, RF-002, RF-003, RF-004

---

### ADR_2025_006: Configuracion Dinamica Sistema
**Ubicacion**: `docs/backend/ADR_2025_006-configuracion-dinamica-sistema.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Backend
**Propietario**: @equipo-backend

**Resumen**: Sistema de configuracion dinamica persistida en base de datos.

**Relacionado**: ADR_2025_005

---

### ADR_2025_007: Git Hooks Validation Strategy
**Ubicacion**: `docs/infraestructura/ADR_2025_007-git-hooks-validation-strategy.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Infraestructura
**Propietario**: @equipo-devops

**Resumen**: Estrategia de validacion con Git Hooks.

**Relacionado**: ADR_2025_002, ADR_2025_008

---

### ADR_2025_008: Workflow Validation Shell Migration
**Ubicacion**: `docs/gobernanza/ADR_2025_008-workflow-validation-shell-migration.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Gobernanza
**Propietario**: @equipo-gobernanza @equipo-devops

**Resumen**: Workflow de validacion para migracion de scripts shell.

**Relacionado**: ADR_2025_007

---

### ADR_2025_009: Frontend Postponement
**Ubicacion**: `docs/backend/ADR_2025_009-frontend-postponement.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Backend + Frontend
**Propietario**: @equipo-backend @equipo-frontend

**Resumen**: Postergacion de implementacion de frontend React.

**Relacionado**: ADR_2025_015, ADR_2025_020

---

### ADR_2025_010: ORM SQL Hybrid Permissions
**Ubicacion**: `docs/backend/ADR_2025_010-orm-sql-hybrid-permissions.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Backend
**Propietario**: @equipo-backend

**Resumen**: Estrategia hibrida ORM + SQL para sistema de permisos.

**Contexto**: Optimizacion de consultas complejas de permisos usando SQL directo cuando Django ORM es ineficiente.

**Relacionado**: ADR_2025_005, UC-PERM-001

---

### ADR_2025_011: WASI Style Virtualization
**Ubicacion**: `docs/infraestructura/ADR_2025_011-wasi_style_virtualization.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Infraestructura
**Propietario**: @equipo-devops

**Resumen**: Virtualizacion estilo WASI para entornos de desarrollo.

---

### ADR_2025_012: CPython Features vs Imagen Base
**Ubicacion**: `docs/infraestructura/ADR_2025_012-cpython-features-vs-imagen-base.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Infraestructura
**Propietario**: @equipo-devops

**Resumen**: Decision sobre features de CPython vs uso de imagen base Docker.

**Relacionado**: cpython-builder.md

---

### ADR_2025_013: Distribucion Artefactos Strategy
**Ubicacion**: `docs/infraestructura/ADR_2025_013-distribucion-artefactos-strategy.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Infraestructura
**Propietario**: @equipo-devops

**Resumen**: Estrategia de distribucion de artefactos.

---

### ADR_2025_014: Organizacion Proyecto por Dominio
**Ubicacion**: `docs/backend/ADR_2025_014-organizacion-proyecto-por-dominio.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Backend
**Propietario**: @equipo-backend @arquitecto-senior

**Resumen**: Organizacion de documentacion y codigo por dominios (ai, backend, frontend, infraestructura).

**Impacto**: Afecta estructura completa de docs/ y jerarquia de 5 niveles de requisitos.

---

### ADR_2025_015: Frontend Modular Monolith
**Ubicacion**: `docs/frontend/ADR_2025_015-frontend-modular-monolith.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Frontend
**Propietario**: @equipo-frontend @arquitecto-frontend

**Resumen**: Arquitectura de monolito modular para frontend.

**Relacionado**: ADR_2025_021

---

### ADR_2025_016: Redux Toolkit State Management
**Ubicacion**: `docs/backend/ADR_2025_016-redux-toolkit-state-management.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Backend (Frontend State)
**Propietario**: @equipo-frontend

**Resumen**: Uso de Redux Toolkit para manejo de estado en React.

**Nota**: Ubicado en docs/backend por razon historica, pero es decision de frontend.

---

### ADR_2025_017: Sistema Permisos Sin Roles Jerarquicos
**Ubicacion**: `docs/ai/ADR_2025_017-sistema-permisos-sin-roles-jerarquicos.md`
**Fecha**: 2025-11-07
**Estado**: Aceptada e Implementada
**Dominio**: General (AI + Backend)
**Propietario**: @arquitecto-senior @equipo-backend @equipo-ba

**Resumen**: Sistema de permisos granular SIN roles jerarquicos, basado en grupos funcionales y capacidades combinables.

**Filosofia Central**:
- NO mas etiquetas jerarquicas (Admin, Supervisor, Agent)
- SI grupos descriptivos ("Atencion al Cliente", "Gestion de Equipos")
- Permisos combinables (multiples grupos por usuario)

**Implementacion**: 8 tablas DB, 16 capacidades, 18 endpoints REST, 21 tests E2E

**Relacionado**:
- prioridad_01_estructura_base_datos.md
- prioridad_02_funciones_core.md
- IMPLEMENTACION_PERMISOS_GRANULAR.md
- UC-PERM-001 a UC-PERM-010

**Impacto**: CRITICA - Base del sistema de autorizacion completo

---

### ADR_2025_018: Webpack Bundler
**Ubicacion**: `docs/frontend/ADR_2025_018-webpack-bundler.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Frontend
**Propietario**: @equipo-frontend

**Resumen**: Uso de Webpack como bundler para frontend React.

---

### ADR_2025_019: Testing Strategy Jest Testing Library
**Ubicacion**: `docs/frontend/ADR_2025_019-testing-strategy-jest-testing-library.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Frontend
**Propietario**: @equipo-frontend @equipo-qa

**Resumen**: Estrategia de testing con Jest y React Testing Library.

---

### ADR_2025_020: Servicios Resilientes
**Ubicacion**: `docs/frontend/arquitectura/adr/ADR_2025_020-servicios-resilientes.md`
**Fecha**: 2025-11-09
**Estado**: Aceptado
**Dominio**: Frontend
**Propietario**: @equipo-frontend

**Resumen**: Capa de servicios resilientes con contratos y telemetria.

**Contexto**: Frontend depende de backend incompleto que opera sin DB persistente. Vistas clave usan mocks sin contrato uniforme.

**Decision**:
- Definir contrato comun con `createResilientService`
- Degradacion controlada a mocks con `fetchWithFallback`
- Telemetria de origen (API vs mock) con `recordMockUsage`
- Flags de integridad `UI_BACKEND_<DOMINIO>_SOURCE`

---

### ADR_2025_021: Arquitectura Microfrontends
**Ubicacion**: `docs/frontend/arquitectura/adr/ADR_2025_021-arquitectura-microfrontends.md`
**Fecha**: 2025-XX-XX
**Estado**: Aceptada
**Dominio**: Frontend
**Propietario**: @equipo-frontend @arquitecto-frontend

**Resumen**: Arquitectura de microfrontends para escalabilidad.

**Relacionado**: ADR_2025_015, ADR_2025_020

---

## Indice por Dominio

### AI/ML (2 ADRs)
- ADR_2025_003: DORA SDLC Integration
- ADR_2025_017: Sistema Permisos Sin Roles Jerarquicos

### Backend (8 ADRs)
- ADR_2025_004: Centralized Log Storage
- ADR_2025_005: Grupos Funcionales Sin Jerarquia
- ADR_2025_006: Configuracion Dinamica Sistema
- ADR_2025_009: Frontend Postponement
- ADR_2025_010: ORM SQL Hybrid Permissions
- ADR_2025_014: Organizacion Proyecto por Dominio
- ADR_2025_016: Redux Toolkit State Management

### Frontend (6 ADRs)
- ADR_2025_015: Frontend Modular Monolith
- ADR_2025_018: Webpack Bundler
- ADR_2025_019: Testing Strategy Jest Testing Library
- ADR_2025_020: Servicios Resilientes
- ADR_2025_021: Arquitectura Microfrontends

### Infraestructura (6 ADRs)
- ADR_2025_001: Vagrant mod_wsgi
- ADR_2025_002: Suite Calidad Codigo
- ADR_2025_007: Git Hooks Validation Strategy
- ADR_2025_011: WASI Style Virtualization
- ADR_2025_012: CPython Features vs Imagen Base
- ADR_2025_013: Distribucion Artefactos Strategy

### Gobernanza (1 ADR)
- ADR_2025_008: Workflow Validation Shell Migration

---

## Indice por Estado

### Aceptadas e Implementadas (2)
- ADR_2025_017: Sistema Permisos Sin Roles Jerarquicos

### Aceptadas (20)
- Todos los demas ADRs

---

## Indice por Criticidad

### CRITICA (3)
- ADR_2025_017: Sistema Permisos Sin Roles Jerarquicos
- ADR_2025_003: DORA SDLC Integration
- ADR_2025_005: Grupos Funcionales Sin Jerarquia

### ALTA (18)
- Todos los demas ADRs

---

## Relacionados con Sistema de Permisos

**ADRs Principales**:
- ADR_2025_017: Sistema Permisos Sin Roles Jerarquicos (filosofia)
- ADR_2025_005: Grupos Funcionales Sin Jerarquia (implementacion)
- ADR_2025_010: ORM SQL Hybrid Permissions (optimizacion)

**Documentos Relacionados**:
- prioridad_01_estructura_base_datos.md (8 tablas DB)
- prioridad_02_funciones_core.md (16 capacidades, 3 funciones)
- IMPLEMENTACION_PERMISOS_GRANULAR.md (guia implementacion)
- RESUMEN_IMPLEMENTACION_COMPLETA.md (91 tareas, 35 archivos)
- UC-PERM-001 a UC-PERM-010 (casos de uso)

---

## Como Crear un Nuevo ADR

### 1. Determinar Numero Secuencial
Siguiente numero disponible: **ADR_2025_022**

### 2. Usar Plantilla
Ubicacion: `docs/gobernanza/plantilla_adr.md`

### 3. Formato de Nombre
```
ADR-YYYY-XXX-descripcion-corta.md
```

Ejemplo:
```
ADR_2025_022-rate-limiting-api.md
```

### 4. Ubicar en Dominio Correcto
- AI/ML: `docs/ai/`
- Backend: `docs/backend/`
- Frontend: `docs/frontend/`
- Infraestructura: `docs/infraestructura/`
- Gobernanza: `docs/gobernanza/`

### 5. Actualizar Este Indice
Agregar entrada en:
- Indice por Numero
- Indice por Dominio
- Indice por Estado

### 6. Actualizar CODEOWNERS
Agregar propietarios en `.github/CODEOWNERS`

### 7. Referenciar en Documentos
Actualizar documentos relacionados con link al nuevo ADR.

---

## Referencias

- **Plantilla ADR**: docs/gobernanza/plantilla_adr.md
- **CODEOWNERS**: .github/CODEOWNERS
- **Metodologia**: docs/gobernanza/marco_integrado/04_metodologia_analisis_iact.md

---

## Estadisticas

**Total ADRs**: 21
**Por Dominio**:
- Backend: 8 (38%)
- Frontend: 6 (29%)
- Infraestructura: 6 (29%)
- AI/ML: 2 (10%)
- Gobernanza: 1 (5%)

**Por Estado**:
- Aceptadas e Implementadas: 2 (10%)
- Aceptadas: 20 (95%)

**Criticidad**:
- CRITICA: 3 (14%)
- ALTA: 18 (86%)

---

**Ultima actualizacion**: 2025-11-13
**Responsable**: @arquitecto-senior @tech-lead
**Proxima revision**: 2025-12-01
