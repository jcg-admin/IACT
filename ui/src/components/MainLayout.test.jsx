import { render, screen, waitFor } from '@testing-library/react';
import MainLayout from './MainLayout';
import { PermissionsService } from '@services/permissions/PermissionsService';

jest.mock('@services/permissions/PermissionsService', () => ({
  PermissionsService: {
    getNormalizedPermissions: jest.fn(),
  },
}));

describe('MainLayout', () => {
  beforeEach(() => {
    PermissionsService.getNormalizedPermissions.mockResolvedValue({
      data: {
        user: {},
        capabilities: [],
        menuEntries: [
          { id: 1, code: 'dashboards', label: 'Dashboards', fullName: '', domain: '', icon: '', order: 10 },
          { id: 2, code: 'llamadas', label: 'Llamadas', fullName: '', domain: '', icon: '', order: 20 },
        ],
      },
      source: 'mock',
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders navigation items based on permissions service', async () => {
    render(
      <MainLayout>
        <div>Contenido</div>
      </MainLayout>
    );

    await waitFor(() => {
      expect(screen.getByText(/Dashboards/)).toBeInTheDocument();
      expect(screen.getByText(/Llamadas/)).toBeInTheDocument();
    });

    expect(PermissionsService.getNormalizedPermissions).toHaveBeenCalledTimes(1);
  });

  it('shows placeholder when service fails', async () => {
    PermissionsService.getNormalizedPermissions.mockRejectedValueOnce(
      new Error('sin permisos')
    );

    render(
      <MainLayout>
        <div>Contenido</div>
      </MainLayout>
    );

    const placeholder = await screen.findByTestId('menu-placeholder');
    expect(placeholder).toHaveTextContent(/Menu no disponible/);
  });

  it('renders children content', () => {
    render(
      <MainLayout>
        <div>Contenido principal</div>
      </MainLayout>
    );

    expect(screen.getByText(/Contenido principal/)).toBeInTheDocument();
  });
});
