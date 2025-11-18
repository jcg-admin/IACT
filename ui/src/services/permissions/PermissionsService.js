import { createResilientService } from '@services/createResilientService';
import { loadMock } from '@mocks/registry';
import { shouldUseMockForDomain } from '@services/flags/backendIntegrity';
import { cloneData } from '@services/utils/cloneUtils';

const PERMISSIONS_ENDPOINT = '/api/v1/permissions';
const { data: permissionsMock } = loadMock('permissions');

const baseService = createResilientService({
  id: 'permissions',
  endpoint: PERMISSIONS_ENDPOINT,
  mockDataLoader: () => Promise.resolve(permissionsMock),
  shouldUseMock: () => shouldUseMockForDomain('permissions'),
  errorMessage: 'No fue posible obtener los permisos del usuario',
  isPayloadValid: (payload) => Boolean(payload && Array.isArray(payload.funciones_accesibles)),
});

const formatLabel = (value) =>
  value
    .split('_')
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ');

const normalizePermissions = (raw) => {
  const source = cloneData(raw);

  const capabilities = Array.from(new Set(source.capacidades ?? []));
  const menuEntries = (source.funciones_accesibles ?? [])
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

  return {
    user: source.user,
    capabilities,
    menuEntries,
  };
};

export class PermissionsService {
  static async getNormalizedPermissions(options = {}) {
    const { dataset } = options;

    if (dataset) {
      return {
        data: normalizePermissions(dataset),
        source: 'custom',
        error: null,
        metadata: { domain: 'permissions' },
      };
    }

    const baseResult = await baseService.fetch(options);

    return {
      data: normalizePermissions(baseResult.data),
      source: baseResult.source,
      error: baseResult.error,
      metadata: baseResult.metadata,
    };
  }
}
