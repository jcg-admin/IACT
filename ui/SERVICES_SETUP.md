# UI Services Implementation Guide

## Overview

This document describes the implementation of 11 new service modules in the UI layer to integrate with all backend endpoints exposed by the IACT API.

## Architecture

### Permissions Model

The system implements a granular permissions model based on functional groups rather than hierarchical roles:

**Database Schema:**
- FUNCIONES (Functions): Resources like dashboards, users, calls
- CAPACIDADES (Capabilities): Actions like view, create, edit, delete
- GRUPOS_PERMISOS (Permission Groups): Functional descriptive groups
- USUARIOS (Users): Can belong to multiple groups simultaneously
- PERMISOS_EXCEPCIONALES (Exceptional Permissions): Temporary or permanent overrides
- AUDITORIA_PERMISOS (Audit Log): Track all permission checks

**Key Principles:**
- NO hierarchical roles like "Admin", "Supervisor", "Agent"
- YES functional groups like "Customer Service", "Team Management"
- Users can have multiple groups simultaneously
- Groups are combinable and flexible
- Clear description of what each person can do

### Service Pattern

All services follow the resilient service pattern defined in `createResilientService.js`:

```javascript
createResilientService({
  fetchFromApi: async () => { /* API call */ },
  fetchFromMock: async () => { /* mock fallback */ },
  shouldUseMock: () => flags.backendIntegrity.SOURCE === 'MOCK',
  serviceName: 'ServiceName'
})
```

## Services Implemented

### 1. UsersService
- Endpoint: `/api/v1/usuarios/`
- Operations: CRUD, suspend, reactivate, assign_groups
- Mock: `usuarios.json`

### 2. DashboardService
- Endpoint: `/api/v1/dashboard/`
- Operations: overview, export, customize, share
- Mock: `dashboard.json`

### 3. ConfiguracionService (Legacy)
- Endpoint: `/api/v1/configuracion/`
- Operations: list, detail, modify, export, import, history, audit
- Mock: `configuracion.json`

### 4. ConfigurationService (Parallel Module)
- Endpoint: `/api/v1/configuracion/`
- Operations: list, edit, export, import, restore
- Mock: `configuration.json`

### 5. PresupuestosService
- Endpoint: `/api/v1/presupuestos/`
- Operations: CRUD, approve, reject, export
- Mock: `presupuestos.json`

### 6. PoliticasService
- Endpoint: `/api/v1/politicas/`
- Operations: CRUD, publish, archive, new_version
- Mock: `politicas.json`

### 7. ExcepcionesService
- Endpoint: `/api/v1/excepciones/`
- Operations: CRUD, approve, reject, export
- Mock: `excepciones.json`

### 8. ReportesService
- Endpoint: `/api/v1/reportes/`
- Operations: list by type, advanced filters, unified export
- Mock: `reportes.json`

### 9. NotificationsService
- Endpoint: `/api/v1/notifications/messages/`
- Operations: CRUD, mark_read, unread, unread_count
- Mock: `notifications.json`

### 10. ETLService
- Endpoint: `/api/v1/etl/jobs/`, `/api/v1/etl/errors/`
- Operations: read-only queries, stats, summary, recent_failures, by_severity
- Mock: `etl.json`

### 11. DORAMetricsService
- Endpoint: `/api/dora/`
- Operations: delivery metrics
- Mock: `dora.json`

## Setup Instructions

### 1. Generate Services

Run the setup script to create all service files:

```bash
cd ui
npm run services:setup
```

This will create:
- 11 service directories under `ui/src/services/`
- 11 service implementation files
- 11 test files with 80%+ coverage

### 2. Verify Mocks

All mock files are already created in `ui/src/mocks/`. Verify they exist:

```bash
ls -la ui/src/mocks/*.json
```

### 3. Run Tests

Execute the test suite to verify all services:

```bash
cd ui
npm test
```

Expected output:
- All tests passing
- Coverage above 80% threshold
- No linting errors

### 4. Update Feature Flags

The services integrate with `backendIntegrity.js` for feature flags. Update environment variables as needed:

```bash
UI_BACKEND_USERS_SOURCE=MOCK
UI_BACKEND_DASHBOARD_SOURCE=MOCK
# ... etc
```

## Quality Standards

### TDD Compliance
- Tests written before implementation
- Coverage maintained at 80% or higher
- All edge cases covered

### Code Quality
- Follows existing patterns in `createResilientService.js`
- No duplication (DRY principle)
- Clear separation of concerns
- Proper error handling

### Commit Standards
- Conventional Commits format
- Clear, descriptive messages
- Atomic commits per service

## File Structure

```
ui/
  src/
    services/
      users/
        UsersService.js
        UsersService.test.js
      dashboard/
        DashboardService.js
        DashboardService.test.js
      ... (9 more services)
    mocks/
      usuarios.json
      dashboard.json
      ... (9 more mocks)
  scripts/
    setup-services.js
```

## Next Steps

1. Execute `npm run services:setup` to generate all service files
2. Run `npm test` to verify implementation
3. Integrate services into UI components as needed
4. Update feature flags based on backend availability
5. Document any deviations or special cases

## References

- Architecture documentation: `docs/frontend/arquitectura/`
- Backend API: `api/callcentersite/callcentersite/urls.py`
- Existing services: `ui/src/services/calls/CallsService.js`
- Test patterns: `ui/src/services/calls/CallsService.test.js`
