---
id: DOC-FRONTEND-ARQ-TODO
tipo: backlog
estado: activo
propietario: equipo-frontend
ultima_actualizacion: 2025-11-08
relacionados: ["DOC-ARQ-FRONTEND", "DOC-FRONTEND-BFF-STRATEGY"]
---

# TODO Arquitectura Frontend - Integración con Backend

Lista priorizada de trabajos arquitectónicos necesarios para que la UI absorba las brechas actuales del backend `api/callcentersite`.

## Leyenda

- **Prioridad**: `P0` crítico, `P1` alta, `P2` media, `P3` baja.
- **Estado**: `[ ]` pendiente, `[>]` en curso, `[x]` completado, `[!]` bloqueado.
- **Referencia**: archivo, módulo o documento que origina la necesidad.

## Tablero de tareas

### P0 · Continuidad operativa

- [x] **Bootstrap local de configuración** `2SP`
  - Implementar un servicio `AppConfigService` en `ui/src/services/config` que lea `/api/config` y degrade a mocks (`ui/src/mocks/config.json`).
  - Asegurar pruebas unitarias para ambos caminos (API y mock) siguiendo TDD, manteniendo cobertura ≥ 80 %.
  - Referencia: `useAppConfig` espera `/api/config` inexistente.【F:ui/src/hooks/useAppConfig.js†L18-L36】【F:docs/frontend/arquitectura/estrategia_integracion_backend.md†L31-L36】
  - Evidencia: `AppConfigService` y `useAppConfig` actualizados con fallback y pruebas.【F:ui/src/services/config/AppConfigService.js†L1-L22】【F:ui/src/hooks/useAppConfig.js†L1-L41】

- [x] **Normalizar permisos desde mocks** `3SP`
  - Crear `PermissionsService` en `ui/src/services/permissions` con adaptador a `permissions.json` mientras no exista endpoint real.
  - Generar contrato tipado para las capacidades que alimentan el menú lateral y visibilidad de componentes.
  - Referencia: mocks en `ui/src/mocks/permissions.json` y módulos backend sin datos persistentes.【F:ui/src/mocks/permissions.json†L1-L48】【F:docs/frontend/arquitectura/estrategia_integracion_backend.md†L38-L44】
  - Evidencia: menú dinámico cargado desde `PermissionsService` y pruebas de navegación.【F:ui/src/services/permissions/PermissionsService.js†L1-L55】【F:ui/src/components/MainLayout.jsx†L1-L55】

- [x] **Servicios resilientes para llamadas** `5SP`
  - Diseñar `CallsService` que combine `/api/v1/llamadas/` con `ui/src/mocks/llamadas.json` mediante feature flags.
  - Cubrir escenarios de degradación (API caída, respuesta vacía) con pruebas MSW/fetch-mock.
  - Referencia: endpoints dependen de base de datos inexistente y se trabaja con mocks locales.【F:api/callcentersite/callcentersite/apps/llamadas/views.py†L1-L120】【F:ui/src/mocks/llamadas.json†L1-L68】
  - Evidencia: `CallsService` con fallback y hook `useCallsSummary` integrados al dashboard.【F:ui/src/services/calls/CallsService.js†L1-L35】【F:ui/src/modules/home/HomeModule.jsx†L1-L40】

- [x] **Indicadores visuales de datos simulados** `3SP`
  - Añadir banner/tooltip reutilizable que advierta cuando los dashboards usan mocks.
  - Integrar con proveedor de contexto de conectividad backend.
  - Referencia: widgets actuales entregan valores cero y requieren señalización.【F:api/callcentersite/callcentersite/apps/dashboard/widgets.py†L18-L24】【F:docs/frontend/arquitectura/estrategia_integracion_backend.md†L54-L61】
  - Evidencia: banner `MockDataNotice` activado por `App` y avisos en widgets de llamadas.【F:ui/src/components/MockDataNotice.jsx†L1-L15】【F:ui/src/app/App.jsx†L1-L35】

### P1 · Fundamentos arquitectónicos

- [ ] **Crear `ui/src/services` con contrato común** `5SP`
  - Definir interfaz base (`fetchFromApi`, `fetchFromMock`, `shouldUseMock`) y factoría de servicios.
  - Documentar el patrón en ADR correspondiente.
  - Referencia: estrategia de capa adaptable propuesta.【F:docs/frontend/arquitectura/estrategia_integracion_backend.md†L64-L77】

- [ ] **Gestión centralizada de mocks** `3SP`
  - Migrar mocks a esquemas validados (Zod/TypeScript) y registrar metadatos (fecha, origen).
  - Configurar automatización para regenerar escenarios.
  - Referencia: sección de gestión de mocks.【F:docs/frontend/arquitectura/estrategia_integracion_backend.md†L79-L86】

- [ ] **Feature flags de integridad backend** `2SP`
  - Implementar toggles en build (dotenv) que permitan activar backend por dominio.
  - Registrar métricas de uso de mock vs API.
  - Referencia: plan de degradación controlada.【F:docs/frontend/arquitectura/estrategia_integracion_backend.md†L88-L108】

### P2 · Transición hacia backend real

- [ ] **Health check y monitoreo** `3SP`
  - Consumir `/health` (cuando exista) y almacenar último estado en contexto global.
  - Generar pruebas de integración que simulen backend intermitente.
  - Referencia: roadmap de fases de transición.【F:docs/frontend/arquitectura/estrategia_integracion_backend.md†L110-L118】

- [ ] **Métricas de dependencia de mocks** `3SP`
  - Registrar en analytics internas cuántos módulos operan en modo mock.
  - Alimentar reportes para priorizar endpoints backend.
  - Referencia: acciones priorizadas sobre métricas de mocks.【F:docs/frontend/arquitectura/estrategia_integracion_backend.md†L132-L135】

- [ ] **Retiro progresivo de mocks** `5SP`
  - Definir checklist para eliminar mocks por dominio una vez que existan endpoints completos.
  - Documentar cada retiro en CHANGELOG y ADR asociado.
  - Referencia: fases 2 y 3 del plan de transición.【F:docs/frontend/arquitectura/estrategia_integracion_backend.md†L112-L118】

### P3 · Documentación y seguimiento

- [ ] **Crear ADR de selección de framework y servicios** `2SP`
  - Formalizar elección de herramientas y patrón de servicios.
  - Referencia: backlog de ADRs pendientes en README de arquitectura.【F:docs/frontend/arquitectura/README.md†L36-L43】

- [ ] **Actualizar onboarding con estrategia de mocks** `1SP`
  - Incluir pasos para configurar servicios, flags y pruebas.
  - Referencia: seguimiento de estrategia y comunicación al equipo.【F:docs/frontend/arquitectura/estrategia_integracion_backend.md†L141-L145】

- [ ] **Sincronizar con ROADMAP del proyecto** `1SP`
  - Incorporar este backlog al tablero maestro (`docs/proyecto/TAREAS_ACTIVAS.md`).
  - Reportar avances en releases de frontend.
  - Referencia: necesidad de registrar avances en planeación transversal.【F:docs/proyecto/TAREAS_ACTIVAS.md†L1-L120】【F:docs/frontend/arquitectura/estrategia_integracion_backend.md†L141-L145】

## Notas de coordinación

- Ejecutar sesiones quincenales con backend para revisar brechas y validar si algún endpoint cambia de estado.
- Mantener cobertura de pruebas ≥ 80 % en cada módulo nuevo, respetando la política TDD del repositorio.
- Cada ítem completado debe reflejarse en `docs/proyecto/CHANGELOG.md` y en el índice de arquitectura frontend.
