/**
 * Componente ProtectedRoute - Protección de rutas React Router
 *
 * Fecha: 2025-11-09
 * Referencia: docs/frontend/integracion_permisos.md
 */

import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { usePermisos } from '../hooks/usePermisos';

// =============================================================================
// PROTECTED ROUTE
// =============================================================================

export interface ProtectedRouteProps {
  /**
   * Capacidad requerida para acceder a la ruta
   */
  permission: string;

  /**
   * Ruta a la que redirigir si no tiene permiso
   * @default "/access-denied"
   */
  redirectTo?: string;

  /**
   * Componente a renderizar mientras se cargan permisos
   * @default null (no muestra nada)
   */
  loading?: React.ReactNode;

  /**
   * Contenido de la ruta (página/componente)
   */
  children: React.ReactNode;

  /**
   * Callback cuando se deniega el acceso
   */
  onAccessDenied?: (permission: string, path: string) => void;
}

/**
 * Componente que protege rutas de React Router basado en permisos
 *
 * Redirige a otra ruta si el usuario no tiene el permiso requerido.
 *
 * @example Uso con React Router v6
 * ```tsx
 * import { BrowserRouter, Routes, Route } from 'react-router-dom';
 *
 * <BrowserRouter>
 *   <Routes>
 *     <Route path="/dashboard" element={
 *       <ProtectedRoute permission="sistema.vistas.dashboards.ver">
 *         <Dashboard />
 *       </ProtectedRoute>
 *     } />
 *
 *     <Route path="/admin/users" element={
 *       <ProtectedRoute
 *         permission="sistema.administracion.usuarios.ver"
 *         redirectTo="/forbidden"
 *       >
 *         <UserAdmin />
 *       </ProtectedRoute>
 *     } />
 *   </Routes>
 * </BrowserRouter>
 * ```
 */
export function ProtectedRoute({
  permission,
  redirectTo = '/access-denied',
  loading: loadingComponent = null,
  children,
  onAccessDenied,
}: ProtectedRouteProps): React.ReactElement | null {
  const { hasPermission, loading } = usePermisos();
  const location = useLocation();

  // Estado de carga
  if (loading) {
    return <>{loadingComponent}</>;
  }

  // Verificar permiso
  const granted = hasPermission(permission);

  // Callback de analytics
  React.useEffect(() => {
    if (!loading && !granted && onAccessDenied) {
      onAccessDenied(permission, location.pathname);
    }
  }, [granted, loading, permission, location.pathname, onAccessDenied]);

  // Redirigir si no tiene permiso
  if (!granted) {
    return (
      <Navigate
        to={redirectTo}
        replace
        state={{ from: location, permission, reason: 'missing_permission' }}
      />
    );
  }

  // Renderizar contenido protegido
  return <>{children}</>;
}

// =============================================================================
// PROTECTED ROUTE WITH MULTIPLE PERMISSIONS (ANY)
// =============================================================================

export interface ProtectedRouteAnyProps extends Omit<ProtectedRouteProps, 'permission'> {
  /**
   * Lista de capacidades. Si tiene ALGUNA, permite el acceso.
   */
  permissions: string[];
}

/**
 * Ruta protegida que permite acceso si tiene AL MENOS UNA de las capacidades
 *
 * @example
 * ```tsx
 * <Route path="/dashboard" element={
 *   <ProtectedRouteAny
 *     permissions={[
 *       'sistema.vistas.dashboards.ver',
 *       'sistema.vistas.metricas.ver'
 *     ]}
 *   >
 *     <Dashboard />
 *   </ProtectedRouteAny>
 * } />
 * ```
 */
export function ProtectedRouteAny({
  permissions,
  redirectTo = '/access-denied',
  loading: loadingComponent = null,
  children,
  onAccessDenied,
}: ProtectedRouteAnyProps): React.ReactElement | null {
  const { hasPermission, loading } = usePermisos();
  const location = useLocation();

  if (loading) {
    return <>{loadingComponent}</>;
  }

  const granted = permissions.some(p => hasPermission(p));

  React.useEffect(() => {
    if (!loading && !granted && onAccessDenied) {
      onAccessDenied(permissions.join(', '), location.pathname);
    }
  }, [granted, loading, permissions, location.pathname, onAccessDenied]);

  if (!granted) {
    return (
      <Navigate
        to={redirectTo}
        replace
        state={{ from: location, permissions, reason: 'missing_any_permission' }}
      />
    );
  }

  return <>{children}</>;
}

// =============================================================================
// PROTECTED ROUTE WITH MULTIPLE PERMISSIONS (ALL)
// =============================================================================

export interface ProtectedRouteAllProps extends Omit<ProtectedRouteProps, 'permission'> {
  /**
   * Lista de capacidades. Debe tener TODAS para acceder.
   */
  permissions: string[];
}

/**
 * Ruta protegida que solo permite acceso si tiene TODAS las capacidades
 *
 * @example
 * ```tsx
 * <Route path="/admin/full" element={
 *   <ProtectedRouteAll
 *     permissions={[
 *       'sistema.administracion.usuarios.ver',
 *       'sistema.administracion.usuarios.editar',
 *       'sistema.administracion.usuarios.eliminar'
 *     ]}
 *   >
 *     <FullAdminPanel />
 *   </ProtectedRouteAll>
 * } />
 * ```
 */
export function ProtectedRouteAll({
  permissions,
  redirectTo = '/access-denied',
  loading: loadingComponent = null,
  children,
  onAccessDenied,
}: ProtectedRouteAllProps): React.ReactElement | null {
  const { hasPermission, loading } = usePermisos();
  const location = useLocation();

  if (loading) {
    return <>{loadingComponent}</>;
  }

  const granted = permissions.every(p => hasPermission(p));

  React.useEffect(() => {
    if (!loading && !granted && onAccessDenied) {
      onAccessDenied(permissions.join(', '), location.pathname);
    }
  }, [granted, loading, permissions, location.pathname, onAccessDenied]);

  if (!granted) {
    return (
      <Navigate
        to={redirectTo}
        replace
        state={{ from: location, permissions, reason: 'missing_all_permissions' }}
      />
    );
  }

  return <>{children}</>;
}

// =============================================================================
// EXPORTS
// =============================================================================

export default ProtectedRoute;
