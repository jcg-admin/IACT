import permissionsMock from '@mocks/permissions.json';
import { cloneData } from '@services/utils/cloneUtils';

/**
 * @typedef {Object} MenuEntry
 * @property {number} id
 * @property {string} code
 * @property {string} fullName
 * @property {string} domain
 * @property {string} icon
 * @property {number} order
 */

/**
 * @typedef {Object} NormalizedPermissions
 * @property {{ id: number, username: string, email: string, grupos: Array<Object> }} user
 * @property {string[]} capabilities
 * @property {MenuEntry[]} menuEntries
 */

const formatLabel = (value) =>
  value
    .split('_')
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ');

export class PermissionsService {
  /**
   * @param {{ dataset?: typeof permissionsMock }} [options]
   * @returns {Promise<{ data: NormalizedPermissions, source: 'mock' | 'custom', error: null }>}
   */
  static async getNormalizedPermissions(options = {}) {
    const { dataset } = options;
    const source = dataset ? 'custom' : 'mock';
    const raw = cloneData(dataset ?? permissionsMock);

    const capabilities = Array.from(new Set(raw.capacidades ?? []));
    const menuEntries = (raw.funciones_accesibles ?? [])
      .map(({ id, nombre, nombre_completo, dominio, icono, orden_menu }) => ({
        id,
        code: nombre,
        label: formatLabel(nombre),
        fullName: nombre_completo,
        domain: dominio,
        icon: icono,
        order: orden_menu,
      }))
      .sort((a, b) => a.order - b.order);

    const normalized = {
      user: raw.user,
      capabilities,
      menuEntries,
    };

    return { data: normalized, source, error: null };
  }
}
