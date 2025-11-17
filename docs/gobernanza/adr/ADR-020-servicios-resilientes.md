---
id: ADR-020
titulo: Capa de servicios resilientes con contratos y telemetria
autor: equipo-frontend
fecha: 2025-11-09
estado: aceptado
relacionados:
  - DOC-FRONTEND-ARQ-TODO
  - DOC-FRONTEND-BFF-STRATEGY
---

## Contexto

El frontend depende de un backend incompleto (`api/callcentersite`) que opera sin base de datos persistente. Las vistas clave (configuracion, permisos y llamadas) se alimentan de mocks locales sin contrato uniforme, lo que dificulta medir el uso de mocks y habilitar endpoints reales de forma gradual.

## Decisión

1. Definir un contrato comun para servicios resilientes mediante `createResilientService`, responsable de:
   - Validar argumentos obligatorios y normalizar el acceso a `fetch`.
   - Ejecutar `fetchWithFallback` con degradacion controlada a mocks.
   - Registrar telemetria de origen (`api` vs `mock`) con `recordMockUsage`.
   - Exponer metadatos estandar `{ domain }` junto con la respuesta.
2. Centralizar la carga de mocks en `src/mocks/registry` validando estructura con funciones de verificacion y metadatos (`src/mocks/metadata.js`).
3. Introducir flags de integridad (`UI_BACKEND_<DOMINIO>_SOURCE`) interpretados por `backendIntegrity`, con valores por defecto `mock` definidos en build (`webpack.config.cjs`).
4. Publicar un script `npm run mocks:refresh` que valida mocks y genera snapshots en `logs/mocks` para apoyar la regeneracion periodica.

## Consecuencias

- Todos los servicios nuevos deben construirse via `createResilientService` para conservar telemetria y contratos consistentes.
- Los mocks deben registrarse en `src/mocks/metadata.js` y pasar por `validate*Mock` antes de usarse.
- Las pipelines pueden activar endpoints reales configurando `UI_BACKEND_<DOMINIO>_SOURCE=api` sin cambios de codigo.
- La documentacion (`TODO.md`, `CHANGELOG.md`) se actualiza para reflejar el cierre de los items P1 relacionados.

## Consideraciones futuras

- Extender la telemetria hacia analytics persistentes usando los datos de `mockUsageTracker`.
- Migrar la validacion de mocks a un esquema compartido con el backend para evitar duplicidad de contratos.
- Incorporar alertas en CI que fallen si la telemetria detecta uso exclusivo de mocks en ambientes productivos.
