# Sistema de Permisos Granular - Frontend

## Inicio Rápido

### 1. Instalación

```bash
# Las dependencias ya están en package.json
npm install
# o
yarn install
```

### 2. Configuración

Crear archivo `.env`:

```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_JWT_TOKEN_KEY=auth_token
REACT_APP_PERMISOS_CACHE_TTL=300000
```

### 3. Uso Básico

```tsx
import { PermissionGate } from './components/PermissionGate';
import { usePermisos } from './hooks/usePermisos';

function MyComponent() {
  const { hasPermission, loading } = usePermisos();

  if (loading) return <div>Cargando...</div>;

  return (
    <div>
      {/* Opción 1: Con hook */}
      {hasPermission('sistema.vistas.dashboards.ver') && (
        <Dashboard />
      )}

      {/* Opción 2: Con componente */}
      <PermissionGate permission="sistema.vistas.dashboards.ver">
        <Dashboard />
      </PermissionGate>
    </div>
  );
}
```

### 4. Protección de Rutas

```tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/dashboard" element={
          <ProtectedRoute permission="sistema.vistas.dashboards.ver">
            <Dashboard />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}
```

## Archivos Creados

```
ui/src/
├── types/
│   └── permisos.types.ts          # TypeScript types
├── config/
│   └── api.config.ts              # Configuración API
├── lib/
│   └── permisos-client.ts         # Cliente API con caché
├── hooks/
│   └── usePermisos.ts             # Hooks personalizados
└── components/
    ├── PermissionGate.tsx         # Componente de protección
    └── ProtectedRoute.tsx         # Protección de rutas
```

## Documentación Completa

Ver: `docs/frontend/integracion_permisos.md` (200+ líneas de documentación exhaustiva)

Incluye:
- Arquitectura de integración
- Configuración detallada
- API completa del cliente
- Ejemplos de uso
- Mejores prácticas
- Troubleshooting
- Guía de migración

## Endpoints API Disponibles

- `GET /api/permisos/verificar/:userId/capacidades/` - Lista de permisos
- `GET /api/permisos/verificar/:userId/tiene-permiso/?capacidad=X` - Verificar uno
- `GET /api/permisos/verificar/:userId/menu/` - Menú dinámico
- `GET /api/permisos/verificar/:userId/grupos/` - Grupos activos

## Performance

- Caché automático con TTL de 5 minutos
- Verificación con caché: < 5ms
- Verificación sin caché: < 10ms (función SQL)
- Menú dinámico: < 40ms (p95)

## Seguridad

WARNING: **IMPORTANTE**: La verificación client-side es solo para UX, NO es seguridad real.

El backend SIEMPRE verifica permisos antes de ejecutar operaciones.

## Soporte

- Documentación: `docs/frontend/integracion_permisos.md`
- Issues: Reportar en repositorio
- Owner: equipo-frontend
