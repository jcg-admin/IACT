/**
 * Custom Hooks para Sistema de Permisos Granular
 *
 * Fecha: 2025-11-09
 * Referencia: docs/frontend/integracion_permisos.md
 */

import { useState, useEffect, useCallback, useContext, createContext } from 'react';
import { PermisosClient } from '../lib/permisos-client';
import type {
  MenuNode,
  GrupoUsuarioDetalle,
  PermissionChecker,
} from '../types/permisos.types';

// =============================================================================
// AUTH CONTEXT (Placeholder - Adaptar según tu implementación)
// =============================================================================

interface AuthContextValue {
  user: { id: number; email: string } | null;
  isAuthenticated: boolean;
}

// Crear tu propio AuthContext o importar el existente
const AuthContext = createContext<AuthContextValue>({
  user: null,
  isAuthenticated: false,
});

export const useAuth = () => useContext(AuthContext);

// =============================================================================
// HOOK: usePermisos
// =============================================================================

interface UsePermisosReturn {
  /**
   * Verifica si el usuario tiene una capacidad específica
   */
  hasPermission: PermissionChecker;

  /**
   * Lista completa de capacidades del usuario
   */
  capacidades: string[];

  /**
   * Estado de carga
   */
  loading: boolean;

  /**
   * Error si ocurrió alguno
   */
  error: Error | null;

  /**
   * Refresca permisos desde el servidor
   */
  refreshPermissions: () => Promise<void>;

  /**
   * Verifica múltiples permisos en batch
   */
  hasPermissions: (capacidades: string[]) => Record<string, boolean>;
}

/**
 * Hook principal para gestión de permisos
 *
 * @example
 * ```tsx
 * const { hasPermission, capacidades, loading } = usePermisos();
 *
 * if (loading) return <Spinner />;
 *
 * if (hasPermission('sistema.vistas.dashboards.ver')) {
 *   return <Dashboard />;
 * }
 * ```
 */
export function usePermisos(): UsePermisosReturn {
  const { user, isAuthenticated } = useAuth();
  const [capacidades, setCapacidades] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadPermissions = useCallback(async () => {
    if (!isAuthenticated || !user?.id) {
      setCapacidades([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const client = PermisosClient.getInstance();
      const response = await client.getCapacidades(user.id);

      setCapacidades(response.capacidades);
    } catch (err) {
      console.error('[usePermisos] Error cargando permisos:', err);
      setError(err as Error);
      setCapacidades([]);
    } finally {
      setLoading(false);
    }
  }, [user?.id, isAuthenticated]);

  useEffect(() => {
    loadPermissions();
  }, [loadPermissions]);

  const hasPermission = useCallback<PermissionChecker>(
    (capacidad: string) => {
      return capacidades.includes(capacidad);
    },
    [capacidades]
  );

  const hasPermissions = useCallback(
    (caps: string[]) => {
      const result: Record<string, boolean> = {};
      caps.forEach(cap => {
        result[cap] = capacidades.includes(cap);
      });
      return result;
    },
    [capacidades]
  );

  const refreshPermissions = useCallback(async () => {
    if (!user?.id) return;

    try {
      const client = PermisosClient.getInstance();
      const response = await client.refreshCapacidades(user.id);
      setCapacidades(response.capacidades);
      setError(null);
    } catch (err) {
      console.error('[usePermisos] Error refrescando permisos:', err);
      setError(err as Error);
    }
  }, [user?.id]);

  return {
    hasPermission,
    capacidades,
    loading,
    error,
    refreshPermissions,
    hasPermissions,
  };
}

// =============================================================================
// HOOK: useMenu
// =============================================================================

interface UseMenuReturn {
  /**
   * Menú jerárquico generado dinámicamente
   */
  menu: MenuNode;

  /**
   * Estado de carga
   */
  loading: boolean;

  /**
   * Error si ocurrió alguno
   */
  error: Error | null;

  /**
   * Refresca menú desde el servidor
   */
  refreshMenu: () => Promise<void>;
}

/**
 * Hook para generar menú dinámico basado en permisos
 *
 * @example
 * ```tsx
 * const { menu, loading } = useMenu();
 *
 * return (
 *   <nav>
 *     {Object.entries(menu).map(([dominio, funciones]) => (
 *       <MenuItem key={dominio} title={dominio}>
 *         {Object.keys(funciones).map(funcion => (
 *           <SubMenuItem key={funcion}>{funcion}</SubMenuItem>
 *         ))}
 *       </MenuItem>
 *     ))}
 *   </nav>
 * );
 * ```
 */
export function useMenu(): UseMenuReturn {
  const { user, isAuthenticated } = useAuth();
  const [menu, setMenu] = useState<MenuNode>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadMenu = useCallback(async () => {
    if (!isAuthenticated || !user?.id) {
      setMenu({});
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const client = PermisosClient.getInstance();
      const response = await client.getMenu(user.id);

      setMenu(response.menu);
    } catch (err) {
      console.error('[useMenu] Error cargando menú:', err);
      setError(err as Error);
      setMenu({});
    } finally {
      setLoading(false);
    }
  }, [user?.id, isAuthenticated]);

  useEffect(() => {
    loadMenu();
  }, [loadMenu]);

  const refreshMenu = useCallback(async () => {
    if (!user?.id) return;

    try {
      const client = PermisosClient.getInstance();
      client.clearCache(user.id);
      const response = await client.getMenu(user.id);
      setMenu(response.menu);
      setError(null);
    } catch (err) {
      console.error('[useMenu] Error refrescando menú:', err);
      setError(err as Error);
    }
  }, [user?.id]);

  return {
    menu,
    loading,
    error,
    refreshMenu,
  };
}

// =============================================================================
// HOOK: useCapacidades
// =============================================================================

interface UseCapacidadesReturn {
  /**
   * Lista completa de capacidades
   */
  capacidades: string[];

  /**
   * Estado de carga
   */
  loading: boolean;

  /**
   * Error si ocurrió alguno
   */
  error: Error | null;

  /**
   * Total de capacidades
   */
  total: number;

  /**
   * Refresca capacidades desde el servidor
   */
  refresh: () => Promise<void>;
}

/**
 * Hook para obtener lista completa de capacidades del usuario
 *
 * @example
 * ```tsx
 * const { capacidades, total, loading } = useCapacidades();
 *
 * return (
 *   <div>
 *     <h3>Mis Permisos ({total})</h3>
 *     <ul>
 *       {capacidades.map(cap => (
 *         <li key={cap}>{cap}</li>
 *       ))}
 *     </ul>
 *   </div>
 * );
 * ```
 */
export function useCapacidades(): UseCapacidadesReturn {
  const { user, isAuthenticated } = useAuth();
  const [capacidades, setCapacidades] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadCapacidades = useCallback(async () => {
    if (!isAuthenticated || !user?.id) {
      setCapacidades([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const client = PermisosClient.getInstance();
      const response = await client.getCapacidades(user.id);

      setCapacidades(response.capacidades);
    } catch (err) {
      console.error('[useCapacidades] Error cargando capacidades:', err);
      setError(err as Error);
      setCapacidades([]);
    } finally {
      setLoading(false);
    }
  }, [user?.id, isAuthenticated]);

  useEffect(() => {
    loadCapacidades();
  }, [loadCapacidades]);

  const refresh = useCallback(async () => {
    if (!user?.id) return;

    try {
      const client = PermisosClient.getInstance();
      const response = await client.refreshCapacidades(user.id);
      setCapacidades(response.capacidades);
      setError(null);
    } catch (err) {
      console.error('[useCapacidades] Error refrescando capacidades:', err);
      setError(err as Error);
    }
  }, [user?.id]);

  return {
    capacidades,
    loading,
    error,
    total: capacidades.length,
    refresh,
  };
}

// =============================================================================
// HOOK: useGrupos
// =============================================================================

interface UseGruposReturn {
  /**
   * Lista de grupos activos del usuario
   */
  grupos: GrupoUsuarioDetalle[];

  /**
   * Estado de carga
   */
  loading: boolean;

  /**
   * Error si ocurrió alguno
   */
  error: Error | null;

  /**
   * Total de grupos
   */
  total: number;

  /**
   * Refresca grupos desde el servidor
   */
  refresh: () => Promise<void>;
}

/**
 * Hook para obtener grupos activos del usuario
 *
 * @example
 * ```tsx
 * const { grupos, loading } = useGrupos();
 *
 * return (
 *   <div>
 *     <h3>Mis Grupos</h3>
 *     {grupos.map(grupo => (
 *       <Badge key={grupo.grupo_id} color={grupo.color_hex}>
 *         {grupo.grupo_nombre}
 *       </Badge>
 *     ))}
 *   </div>
 * );
 * ```
 */
export function useGrupos(): UseGruposReturn {
  const { user, isAuthenticated } = useAuth();
  const [grupos, setGrupos] = useState<GrupoUsuarioDetalle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const loadGrupos = useCallback(async () => {
    if (!isAuthenticated || !user?.id) {
      setGrupos([]);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const client = PermisosClient.getInstance();
      const response = await client.getGrupos(user.id);

      setGrupos(response.grupos);
    } catch (err) {
      console.error('[useGrupos] Error cargando grupos:', err);
      setError(err as Error);
      setGrupos([]);
    } finally {
      setLoading(false);
    }
  }, [user?.id, isAuthenticated]);

  useEffect(() => {
    loadGrupos();
  }, [loadGrupos]);

  const refresh = useCallback(async () => {
    await loadGrupos();
  }, [loadGrupos]);

  return {
    grupos,
    loading,
    error,
    total: grupos.length,
    refresh,
  };
}
