import permissionsMock from '@mocks/permissions.json';
import { PermissionsService } from './PermissionsService';

const formatLabel = (value) =>
  value
    .split('_')
    .map((segment) => segment.charAt(0).toUpperCase() + segment.slice(1))
    .join(' ');

describe('PermissionsService', () => {
  it('normalizes permissions from mocks with sorted menu entries', async () => {
    const result = await PermissionsService.getNormalizedPermissions();

    expect(result.source).toBe('mock');
    expect(result.data.user).toEqual(permissionsMock.user);
    expect(result.data.capabilities).toEqual(
      Array.from(new Set(permissionsMock.capacidades))
    );
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
  });

  it('filters duplicated capabilities defensively', async () => {
    const duplicated = {
      ...permissionsMock,
      capacidades: [...permissionsMock.capacidades, permissionsMock.capacidades[0]],
    };

    const result = await PermissionsService.getNormalizedPermissions({
      dataset: duplicated,
    });

    const unique = Array.from(new Set(permissionsMock.capacidades));
    expect(result.data.capabilities).toEqual(unique);
  });
});
