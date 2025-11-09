/**
 * Configuración centralizada de API
 *
 * Fecha: 2025-11-09
 * Referencia: docs/frontend/integracion_permisos.md
 */

import type { PermisosClientConfig } from '../types/permisos.types';

// =============================================================================
// ENVIRONMENT VARIABLES
// =============================================================================

const getEnvVar = (key: string, defaultValue: string): string => {
  // Para React
  if (typeof process !== 'undefined' && process.env) {
    return process.env[`REACT_APP_${key}`] || defaultValue;
  }

  // Para Vite
  if (typeof import.meta !== 'undefined' && import.meta.env) {
    return (import.meta.env as any)[`VITE_${key}`] || defaultValue;
  }

  return defaultValue;
};

// =============================================================================
// API CONFIGURATION
// =============================================================================

export const API_CONFIG = {
  baseURL: getEnvVar('API_URL', 'http://localhost:8000'),

  endpoints: {
    auth: {
      login: '/api/auth/login/',
      logout: '/api/auth/logout/',
      refresh: '/api/auth/refresh/',
      me: '/api/auth/me/',
    },

    permisos: {
      // Verificación
      verificar: (userId: number) => `/api/permisos/verificar/${userId}`,
      capacidades: (userId: number) => `/api/permisos/verificar/${userId}/capacidades/`,
      tienePermiso: (userId: number, capacidad: string) =>
        `/api/permisos/verificar/${userId}/tiene-permiso/?capacidad=${encodeURIComponent(capacidad)}`,
      menu: (userId: number) => `/api/permisos/verificar/${userId}/menu/`,
      grupos: (userId: number) => `/api/permisos/verificar/${userId}/grupos/`,

      // CRUD Funciones
      funciones: '/api/permisos/funciones/',
      funcion: (id: number) => `/api/permisos/funciones/${id}/`,

      // CRUD Capacidades
      capacidades_list: '/api/permisos/capacidades/',
      capacidad: (id: number) => `/api/permisos/capacidades/${id}/`,

      // CRUD Grupos
      grupos_list: '/api/permisos/grupos/',
      grupo: (id: number) => `/api/permisos/grupos/${id}/`,

      // Permisos Excepcionales
      excepcionales: '/api/permisos/excepcionales/',
      excepcional: (id: number) => `/api/permisos/excepcionales/${id}/`,

      // Auditoría
      auditoria: '/api/permisos/auditoria/',
    },

    usuarios: {
      list: '/api/usuarios/',
      detail: (id: number) => `/api/usuarios/${id}/`,
      asignarGrupos: (id: number) => `/api/usuarios/${id}/asignar_grupos/`,
      suspender: (id: number) => `/api/usuarios/${id}/suspender/`,
      reactivar: (id: number) => `/api/usuarios/${id}/reactivar/`,
    },
  },

  cache: {
    ttl: parseInt(getEnvVar('PERMISOS_CACHE_TTL', '300000'), 10), // 5 minutos
    storageKey: 'permisos_cache',
    menuStorageKey: 'menu_cache',
  },

  auth: {
    tokenKey: getEnvVar('JWT_TOKEN_KEY', 'auth_token'),
    refreshTokenKey: 'refresh_token',
  },

  timeouts: {
    default: 10000, // 10 segundos
    upload: 30000,  // 30 segundos
  },
} as const;

// =============================================================================
// PERMISOS CLIENT CONFIGURATION
// =============================================================================

export const PERMISOS_CLIENT_CONFIG: PermisosClientConfig = {
  baseURL: API_CONFIG.baseURL,
  authTokenKey: API_CONFIG.auth.tokenKey,
  cacheTTL: API_CONFIG.cache.ttl,
  cacheStorageKey: API_CONFIG.cache.storageKey,
  enableCache: true,
  enableLogging: process.env.NODE_ENV === 'development',
};

// =============================================================================
// AXIOS DEFAULTS (if using axios)
// =============================================================================

export const AXIOS_CONFIG = {
  baseURL: API_CONFIG.baseURL,
  timeout: API_CONFIG.timeouts.default,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false, // Cambiar a true si usas cookies
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Construye URL completa con base URL
 */
export function buildURL(endpoint: string): string {
  const base = API_CONFIG.baseURL.replace(/\/$/, '');
  const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  return `${base}${path}`;
}

/**
 * Obtiene token de autenticación del storage
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(API_CONFIG.auth.tokenKey);
}

/**
 * Guarda token de autenticación en storage
 */
export function setAuthToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(API_CONFIG.auth.tokenKey, token);
}

/**
 * Elimina token de autenticación del storage
 */
export function clearAuthToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(API_CONFIG.auth.tokenKey);
  localStorage.removeItem(API_CONFIG.auth.refreshTokenKey);
}

/**
 * Construye headers HTTP con autenticación
 */
export function buildAuthHeaders(): HeadersInit {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  return headers;
}
