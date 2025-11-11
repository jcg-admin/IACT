/**
 * TypeScript Types para Sistema de Permisos Granular
 *
 * Fecha: 2025-11-09
 * Referencia: docs/frontend/integracion_permisos.md
 */

// =============================================================================
// ENTITIES
// =============================================================================

export interface Capacidad {
  id: number;
  codigo: string;
  nombre: string;
  descripcion?: string;
  nivel_riesgo: NivelRiesgo;
  requiere_aprobacion: boolean;
  activa: boolean;
}

export interface Funcion {
  id: number;
  nombre: string;
  nombre_completo: string;
  dominio: string;
  categoria: string;
  descripcion?: string;
  icono?: string;
  orden_menu: number;
  activa: boolean;
}

export interface GrupoPermiso {
  id: number;
  codigo: string;
  nombre: string;
  descripcion?: string;
  categoria: string;
  nivel_riesgo: NivelRiesgo;
  activo: boolean;
  capacidades_count?: number;
  usuarios_count?: number;
}

export interface PermisoExcepcional {
  id: number;
  usuario_id: number;
  capacidad_codigo: string;
  tipo: 'temporal' | 'permanente';
  fecha_inicio: string;
  fecha_expiracion?: string | null;
  motivo: string;
  activo: boolean;
  otorgado_por_email?: string;
}

// =============================================================================
// API RESPONSES
// =============================================================================

export interface UsuarioCapacidadesResponse {
  usuario_id: number;
  capacidades: string[];
  total: number;
}

export interface VerificarPermisoResponse {
  usuario_id: number;
  capacidad_codigo: string;
  tiene_permiso: boolean;
  origen?: 'grupo' | 'excepcional_concedido';
}

export interface MenuNode {
  [dominio: string]: {
    [funcion: string]: string[]; // Array de códigos de capacidades
  };
}

export interface MenuUsuarioResponse {
  usuario_id: number;
  menu: MenuNode;
}

export interface GrupoUsuarioDetalle {
  grupo_id: number;
  grupo_codigo: string;
  grupo_nombre: string;
  tipo_acceso: string;
  color_hex: string;
  vigente: boolean;
  fecha_asignacion: string;
  fecha_expiracion: string | null;
}

export interface GruposUsuarioResponse {
  usuario_id: number;
  grupos: GrupoUsuarioDetalle[];
  total: number;
}

// =============================================================================
// PAGINATION
// =============================================================================

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

// =============================================================================
// REQUEST PAYLOADS
// =============================================================================

export interface AsignarGruposRequest {
  grupos_codigos: string[];
  motivo?: string;
}

export interface OtorgarPermisoExcepcionalRequest {
  usuario_id: number;
  capacidad_codigo: string;
  tipo: 'temporal' | 'permanente';
  fecha_inicio?: string;
  fecha_expiracion?: string | null;
  motivo: string;
}

// =============================================================================
// CACHE
// =============================================================================

export interface PermisosCache {
  capacidades: string[];
  timestamp: number;
  userId: number;
}

export interface MenuCache {
  menu: MenuNode;
  timestamp: number;
  userId: number;
}

// =============================================================================
// ENUMS & CONSTANTS
// =============================================================================

export type NivelRiesgo = 'bajo' | 'medio' | 'alto' | 'critico';

export type TipoAccion =
  | 'acceso_permitido'
  | 'acceso_denegado'
  | 'asignacion_grupo'
  | 'revocacion_grupo'
  | 'permiso_excepcional';

// =============================================================================
// ERROR HANDLING
// =============================================================================

export class PermisosError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public response?: any,
    public endpoint?: string
  ) {
    super(message);
    this.name = 'PermisosError';

    // Maintains proper stack trace for where error was thrown
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, PermisosError);
    }
  }
}

export class UnauthorizedError extends PermisosError {
  constructor(message: string = 'No autorizado') {
    super(message, 401);
    this.name = 'UnauthorizedError';
  }
}

export class ForbiddenError extends PermisosError {
  constructor(message: string = 'Acceso denegado') {
    super(message, 403);
    this.name = 'ForbiddenError';
  }
}

export class NotFoundError extends PermisosError {
  constructor(message: string = 'Recurso no encontrado') {
    super(message, 404);
    this.name = 'NotFoundError';
  }
}

// =============================================================================
// UTILITY TYPES
// =============================================================================

export type AsyncState<T> = {
  data: T | null;
  loading: boolean;
  error: Error | null;
};

export type PermissionChecker = (capacidad: string) => boolean;

// =============================================================================
// CONFIGURATION
// =============================================================================

export interface PermisosClientConfig {
  baseURL: string;
  authTokenKey: string;
  cacheTTL: number;
  cacheStorageKey: string;
  enableCache: boolean;
  enableLogging: boolean;
}
