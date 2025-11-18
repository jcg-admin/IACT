import permissionsMock from '@mocks/permissions.json';
import { PermissionsService } from './PermissionsService';
import { resetMockUsageMetrics, getMockUsageMetrics } from '@services/utils/mockUsageTracker';

const formatLabel = (value) =>
  value
    .split('_')
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ');

describe('PermissionsService', () => {
  let originalEnv;

  beforeEach(() => {
    originalEnv = { ...process.env };
    resetMockUsageMetrics();
    process.env.UI_BACKEND_PERMISSIONS_SOURCE = 'mock';
  });

  afterEach(() => {
    process.env = { ...originalEnv };
  });

  it('normalizes permissions from mocks with sorted menu entries', async () => {
    const result = await PermissionsService.getNormalizedPermissions();

    expect(result.source).toBe('mock');
    expect(result.metadata).toEqual({ domain: 'permissions' });
    expect(result.data.user).toEqual(permissionsMock.user);
    expect(result.data.capabilities).toEqual(Array.from(new Set(permissionsMock.capacidades)));
    const expectedOrder = [...permissionsMock.funciones_accesibles]
      .sort((a, b) => a.orden_menu - b.orden_menu)
      .map(({ id, nombre, nombre_completo, dominio, icono, orden_menu }) => ({
        id,
        code: nombre,
        label: formatLabel(nombre),
        fullName: nombre_completo,
        domain: dominio,
        icon: icono,
        order: orden_menu,
      }));
    expect(result.data.menuEntries).toEqual(expectedOrder);
    expect(getMockUsageMetrics()).toEqual({ permissions: { api: 0, mock: 1 } });
  });

  it('filters duplicated capabilities defensively for custom dataset', async () => {
    const duplicated = {
      ...permissionsMock,
      capacidades: [...permissionsMock.capacidades, permissionsMock.capacidades[0]],
    };

    const result = await PermissionsService.getNormalizedPermissions({
      dataset: duplicated,
    });

    const unique = Array.from(new Set(permissionsMock.capacidades));
    expect(result.data.capabilities).toEqual(unique);
    expect(result.source).toBe('custom');
    expect(result.metadata).toEqual({ domain: 'permissions' });
  });

  it('handles missing arrays by defaulting to empty collections', async () => {
    const partial = {
      user: permissionsMock.user,
    };

    const result = await PermissionsService.getNormalizedPermissions({ dataset: partial });

    expect(result.data.capabilities).toEqual([]);
    expect(result.data.menuEntries).toEqual([]);
  });
});
