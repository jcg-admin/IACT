/**
 * Componente PermissionGate - Protección de UI basada en permisos
 *
 * Fecha: 2025-11-09
 * Referencia: docs/frontend/integracion_permisos.md
 */

import React from 'react';
import { usePermisos } from '../hooks/usePermisos';

// =============================================================================
// PERMISSION GATE
// =============================================================================

export interface PermissionGateProps {
  /**
   * Capacidad requerida para mostrar el contenido
   * @example "sistema.vistas.dashboards.ver"
   */
  permission: string;

  /**
   * Componente o elemento a mostrar si NO tiene permiso
   * @default null (no muestra nada)
   */
  fallback?: React.ReactNode;

  /**
   * Componente o elemento a mostrar mientras se cargan permisos
   * @default null (no muestra nada)
   */
  loading?: React.ReactNode;

  /**
   * Contenido a proteger (solo se muestra si tiene permiso)
   */
  children: React.ReactNode;

  /**
   * Callback cuando se deniega el acceso
   * Útil para analytics o logging
   */
  onAccessDenied?: (permission: string) => void;

  /**
   * Callback cuando se otorga el acceso
   * Útil para analytics o logging
   */
  onAccessGranted?: (permission: string) => void;
}

/**
 * Componente que protege contenido basado en permisos del usuario
 *
 * IMPORTANTE: Esta verificación es solo para UX, NO es seguridad real.
 * El backend SIEMPRE debe verificar permisos.
 *
 * @example Uso básico
 * ```tsx
 * <PermissionGate permission="sistema.vistas.dashboards.ver">
 *   <Dashboard />
 * </PermissionGate>
 * ```
 *
 * @example Con fallback
 * ```tsx
 * <PermissionGate
 *   permission="sistema.administracion.usuarios.ver"
 *   fallback={<AccessDenied />}
 * >
 *   <UserManagement />
 * </PermissionGate>
 * ```
 *
 * @example Con loading
 * ```tsx
 * <PermissionGate
 *   permission="sistema.vistas.dashboards.ver"
 *   loading={<Spinner />}
 *   fallback={<AccessDenied />}
 * >
 *   <Dashboard />
 * </PermissionGate>
 * ```
 */
export function PermissionGate({
  permission,
  fallback = null,
  loading: loadingComponent = null,
  children,
  onAccessDenied,
  onAccessGranted,
}: PermissionGateProps): React.ReactElement | null {
  const { hasPermission, loading } = usePermisos();

  // Estado de carga
  if (loading) {
    return <>{loadingComponent}</>;
  }

  // Verificar permiso
  const granted = hasPermission(permission);

  // Callback de analytics
  React.useEffect(() => {
    if (!loading) {
      if (granted && onAccessGranted) {
        onAccessGranted(permission);
      } else if (!granted && onAccessDenied) {
        onAccessDenied(permission);
      }
    }
  }, [granted, loading, permission, onAccessGranted, onAccessDenied]);

  // Mostrar contenido o fallback
  if (granted) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
}

// =============================================================================
// PERMISSION GATE WITH MULTIPLE PERMISSIONS (ANY)
// =============================================================================

export interface PermissionGateAnyProps extends Omit<PermissionGateProps, 'permission'> {
  /**
   * Lista de capacidades. Si tiene ALGUNA, muestra el contenido.
   */
  permissions: string[];
}

/**
 * Componente que muestra contenido si tiene AL MENOS UNA de las capacidades
 *
 * @example
 * ```tsx
 * <PermissionGateAny
 *   permissions={[
 *     'sistema.vistas.dashboards.ver',
 *     'sistema.vistas.metricas.ver'
 *   ]}
 * >
 *   <DashboardOrMetrics />
 * </PermissionGateAny>
 * ```
 */
export function PermissionGateAny({
  permissions,
  fallback = null,
  loading: loadingComponent = null,
  children,
  onAccessDenied,
  onAccessGranted,
}: PermissionGateAnyProps): React.ReactElement | null {
  const { hasPermission, loading } = usePermisos();

  if (loading) {
    return <>{loadingComponent}</>;
  }

  const granted = permissions.some(p => hasPermission(p));

  React.useEffect(() => {
    if (!loading) {
      if (granted && onAccessGranted) {
        onAccessGranted(permissions.join(', '));
      } else if (!granted && onAccessDenied) {
        onAccessDenied(permissions.join(', '));
      }
    }
  }, [granted, loading, permissions, onAccessGranted, onAccessDenied]);

  if (granted) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
}

// =============================================================================
// PERMISSION GATE WITH MULTIPLE PERMISSIONS (ALL)
// =============================================================================

export interface PermissionGateAllProps extends Omit<PermissionGateProps, 'permission'> {
  /**
   * Lista de capacidades. Debe tener TODAS para mostrar el contenido.
   */
  permissions: string[];
}

/**
 * Componente que muestra contenido solo si tiene TODAS las capacidades
 *
 * @example
 * ```tsx
 * <PermissionGateAll
 *   permissions={[
 *     'sistema.administracion.usuarios.ver',
 *     'sistema.administracion.usuarios.editar',
 *     'sistema.administracion.usuarios.eliminar'
 *   ]}
 * >
 *   <FullUserManagement />
 * </PermissionGateAll>
 * ```
 */
export function PermissionGateAll({
  permissions,
  fallback = null,
  loading: loadingComponent = null,
  children,
  onAccessDenied,
  onAccessGranted,
}: PermissionGateAllProps): React.ReactElement | null {
  const { hasPermission, loading } = usePermisos();

  if (loading) {
    return <>{loadingComponent}</>;
  }

  const granted = permissions.every(p => hasPermission(p));

  React.useEffect(() => {
    if (!loading) {
      if (granted && onAccessGranted) {
        onAccessGranted(permissions.join(', '));
      } else if (!granted && onAccessDenied) {
        onAccessDenied(permissions.join(', '));
      }
    }
  }, [granted, loading, permissions, onAccessGranted, onAccessDenied]);

  if (granted) {
    return <>{children}</>;
  }

  return <>{fallback}</>;
}

// =============================================================================
// RENDER PROP VERSION
// =============================================================================

export interface PermissionGateRenderProps {
  /**
   * Capacidad requerida
   */
  permission: string;

  /**
   * Render function que recibe el estado del permiso
   */
  children: (granted: boolean, loading: boolean) => React.ReactNode;
}

/**
 * Versión con render prop para casos avanzados
 *
 * @example
 * ```tsx
 * <PermissionGateRender permission="sistema.vistas.dashboards.ver">
 *   {(granted, loading) => {
 *     if (loading) return <Spinner />;
 *     if (granted) return <Dashboard />;
 *     return <AccessDenied />;
 *   }}
 * </PermissionGateRender>
 * ```
 */
export function PermissionGateRender({
  permission,
  children,
}: PermissionGateRenderProps): React.ReactElement | null {
  const { hasPermission, loading } = usePermisos();
  const granted = hasPermission(permission);

  return <>{children(granted, loading)}</>;
}

// =============================================================================
// EXPORTS
// =============================================================================

export default PermissionGate;
