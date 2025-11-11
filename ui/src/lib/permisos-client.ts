/**
 * Cliente API para Sistema de Permisos Granular
 *
 * Singleton pattern con caché automático y manejo de errores centralizado
 *
 * Fecha: 2025-11-09
 * Referencia: docs/frontend/integracion_permisos.md
 */

import { API_CONFIG, buildURL, buildAuthHeaders } from '../config/api.config';
import type {
  UsuarioCapacidadesResponse,
  VerificarPermisoResponse,
  MenuUsuarioResponse,
  GruposUsuarioResponse,
  PermisosCache,
  MenuCache,
  PermisosError,
  UnauthorizedError,
  ForbiddenError,
  NotFoundError,
} from '../types/permisos.types';

// =============================================================================
// PERMISOS CLIENT
// =============================================================================

export class PermisosClient {
  private static instance: PermisosClient;
  private cacheTTL: number;
  private enableCache: boolean;
  private enableLogging: boolean;

  private constructor() {
    this.cacheTTL = API_CONFIG.cache.ttl;
    this.enableCache = true;
    this.enableLogging = process.env.NODE_ENV === 'development';
  }

  /**
   * Obtiene instancia singleton del cliente
   */
  public static getInstance(): PermisosClient {
    if (!PermisosClient.instance) {
      PermisosClient.instance = new PermisosClient();
    }
    return PermisosClient.instance;
  }

  // ===========================================================================
  // CACHE MANAGEMENT
  // ===========================================================================

  private getCachedCapacidades(userId: number): string[] | null {
    if (!this.enableCache || typeof window === 'undefined') return null;

    try {
      const cached = localStorage.getItem(`${API_CONFIG.cache.storageKey}_${userId}`);
      if (!cached) return null;

      const data: PermisosCache = JSON.parse(cached);
      const now = Date.now();

      if (now - data.timestamp > this.cacheTTL) {
        this.log('Caché expirado', { userId, age: now - data.timestamp });
        localStorage.removeItem(`${API_CONFIG.cache.storageKey}_${userId}`);
        return null;
      }

      this.log('Caché hit', { userId, capacidades: data.capacidades.length });
      return data.capacidades;
    } catch (error) {
      this.log('Error leyendo caché', error);
      return null;
    }
  }

  private setCachedCapacidades(userId: number, capacidades: string[]): void {
    if (!this.enableCache || typeof window === 'undefined') return;

    try {
      const data: PermisosCache = {
        capacidades,
        timestamp: Date.now(),
        userId,
      };
      localStorage.setItem(`${API_CONFIG.cache.storageKey}_${userId}`, JSON.stringify(data));
      this.log('Caché guardado', { userId, capacidades: capacidades.length });
    } catch (error) {
      this.log('Error guardando caché', error);
    }
  }

  private getCachedMenu(userId: number): MenuUsuarioResponse['menu'] | null {
    if (!this.enableCache || typeof window === 'undefined') return null;

    try {
      const cached = localStorage.getItem(`${API_CONFIG.cache.menuStorageKey}_${userId}`);
      if (!cached) return null;

      const data: MenuCache = JSON.parse(cached);
      const now = Date.now();

      if (now - data.timestamp > this.cacheTTL) {
        localStorage.removeItem(`${API_CONFIG.cache.menuStorageKey}_${userId}`);
        return null;
      }

      this.log('Caché menu hit', { userId });
      return data.menu;
    } catch (error) {
      this.log('Error leyendo caché menu', error);
      return null;
    }
  }

  private setCachedMenu(userId: number, menu: MenuUsuarioResponse['menu']): void {
    if (!this.enableCache || typeof window === 'undefined') return;

    try {
      const data: MenuCache = {
        menu,
        timestamp: Date.now(),
        userId,
      };
      localStorage.setItem(`${API_CONFIG.cache.menuStorageKey}_${userId}`, JSON.stringify(data));
      this.log('Caché menu guardado', { userId });
    } catch (error) {
      this.log('Error guardando caché menu', error);
    }
  }

  /**
   * Limpia caché de un usuario específico
   */
  public clearCache(userId?: number): void {
    if (typeof window === 'undefined') return;

    if (userId) {
      localStorage.removeItem(`${API_CONFIG.cache.storageKey}_${userId}`);
      localStorage.removeItem(`${API_CONFIG.cache.menuStorageKey}_${userId}`);
      this.log('Caché limpiado', { userId });
    } else {
      // Limpiar todo el caché de permisos
      const keys = Object.keys(localStorage);
      keys.forEach(key => {
        if (key.startsWith(API_CONFIG.cache.storageKey) ||
            key.startsWith(API_CONFIG.cache.menuStorageKey)) {
          localStorage.removeItem(key);
        }
      });
      this.log('Todo el caché limpiado');
    }
  }

  // ===========================================================================
  // HTTP HELPERS
  // ===========================================================================

  private async fetch<T>(url: string, options?: RequestInit): Promise<T> {
    const headers = buildAuthHeaders();
    const fullURL = buildURL(url);

    this.log('Fetch', { method: options?.method || 'GET', url: fullURL });

    try {
      const response = await fetch(fullURL, {
        ...options,
        headers: {
          ...headers,
          ...options?.headers,
        },
      });

      if (!response.ok) {
        await this.handleErrorResponse(response, url);
      }

      const data = await response.json();
      this.log('Response', { status: response.status, data });
      return data;
    } catch (error) {
      if (error instanceof Error && error.name.endsWith('Error')) {
        throw error; // Re-throw custom errors
      }
      this.log('Network error', error);
      throw new Error('Error de red al comunicarse con el servidor');
    }
  }

  private async handleErrorResponse(response: Response, endpoint: string): Promise<never> {
    let errorMessage = 'Error desconocido';

    try {
      const errorData = await response.json();
      errorMessage = errorData.error || errorData.detail || JSON.stringify(errorData);
    } catch {
      errorMessage = response.statusText || `Error ${response.status}`;
    }

    this.log('Error response', { status: response.status, message: errorMessage, endpoint });

    switch (response.status) {
      case 401:
        throw new UnauthorizedError(errorMessage);
      case 403:
        throw new ForbiddenError(errorMessage);
      case 404:
        throw new NotFoundError(errorMessage);
      default:
        throw new PermisosError(errorMessage, response.status, null, endpoint);
    }
  }

  private log(message: string, data?: any): void {
    if (this.enableLogging) {
      console.log(`[PermisosClient] ${message}`, data || '');
    }
  }

  // ===========================================================================
  // PUBLIC API METHODS
  // ===========================================================================

  /**
   * Obtiene todas las capacidades de un usuario
   * Usa caché automáticamente (TTL: 5 minutos)
   */
  public async getCapacidades(userId: number): Promise<UsuarioCapacidadesResponse> {
    // Intentar desde caché
    const cached = this.getCachedCapacidades(userId);
    if (cached) {
      return {
        usuario_id: userId,
        capacidades: cached,
        total: cached.length,
      };
    }

    // Llamada a API
    const url = API_CONFIG.endpoints.permisos.capacidades(userId);
    const response = await this.fetch<UsuarioCapacidadesResponse>(url);

    // Guardar en caché
    this.setCachedCapacidades(userId, response.capacidades);

    return response;
  }

  /**
   * Verifica si un usuario tiene una capacidad específica
   * Performance: < 5ms (con caché), < 10ms (sin caché)
   */
  public async tienePermiso(userId: number, capacidad: string): Promise<boolean> {
    // Optimización: Buscar en caché primero
    const cached = this.getCachedCapacidades(userId);
    if (cached) {
      return cached.includes(capacidad);
    }

    // Llamada a API (usa función SQL ultra-rápida)
    const url = API_CONFIG.endpoints.permisos.tienePermiso(userId, capacidad);
    const response = await this.fetch<VerificarPermisoResponse>(url);

    return response.tiene_permiso;
  }

  /**
   * Obtiene menú dinámico basado en permisos del usuario
   * Performance: < 40ms (p95)
   */
  public async getMenu(userId: number): Promise<MenuUsuarioResponse> {
    // Intentar desde caché
    const cached = this.getCachedMenu(userId);
    if (cached) {
      return {
        usuario_id: userId,
        menu: cached,
      };
    }

    // Llamada a API (usa función SQL optimizada)
    const url = API_CONFIG.endpoints.permisos.menu(userId);
    const response = await this.fetch<MenuUsuarioResponse>(url);

    // Guardar en caché
    this.setCachedMenu(userId, response.menu);

    return response;
  }

  /**
   * Obtiene grupos activos de un usuario
   */
  public async getGrupos(userId: number): Promise<GruposUsuarioResponse> {
    const url = API_CONFIG.endpoints.permisos.grupos(userId);
    return await this.fetch<GruposUsuarioResponse>(url);
  }

  /**
   * Refresca capacidades del servidor (limpia caché y recarga)
   */
  public async refreshCapacidades(userId: number): Promise<UsuarioCapacidadesResponse> {
    this.clearCache(userId);
    return await this.getCapacidades(userId);
  }

  /**
   * Verifica múltiples permisos en batch
   * Optimizado para reducir llamadas a API
   */
  public async tienePermisos(userId: number, capacidades: string[]): Promise<Record<string, boolean>> {
    // Obtener todas las capacidades del usuario (usa caché)
    const response = await this.getCapacidades(userId);
    const userCapacidades = new Set(response.capacidades);

    // Verificar cada permiso contra el set
    const result: Record<string, boolean> = {};
    capacidades.forEach(cap => {
      result[cap] = userCapacidades.has(cap);
    });

    return result;
  }

  /**
   * Configura opciones del cliente
   */
  public configure(options: {
    cacheTTL?: number;
    enableCache?: boolean;
    enableLogging?: boolean;
  }): void {
    if (options.cacheTTL !== undefined) {
      this.cacheTTL = options.cacheTTL;
    }
    if (options.enableCache !== undefined) {
      this.enableCache = options.enableCache;
    }
    if (options.enableLogging !== undefined) {
      this.enableLogging = options.enableLogging;
    }
  }
}

// =============================================================================
// EXPORT DEFAULT INSTANCE
// =============================================================================

export default PermisosClient.getInstance();
