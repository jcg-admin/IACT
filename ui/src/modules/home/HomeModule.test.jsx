import { render, screen } from '@testing-library/react';
import HomeModule from './HomeModule';
import { useHomeAnnouncement } from './hooks/useHomeAnnouncement';
import { useCallsSummary } from './hooks/useCallsSummary';

jest.mock('./hooks/useHomeAnnouncement');
jest.mock('./hooks/useCallsSummary');

describe('HomeModule', () => {
  beforeEach(() => {
    useHomeAnnouncement.mockReturnValue({ announcement: 'Mensaje importante', isLoading: false });
    useCallsSummary.mockReturnValue({
      summary: { totalCalls: 0, activeCalls: 0, completedCalls: 0 },
      source: 'api',
      error: null,
      isLoading: true,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading state for calls summary', () => {
    render(<HomeModule />);

    expect(screen.getByText(/Cargando llamadas/)).toBeInTheDocument();
  });

  it('renders calls metrics and mock indicator', () => {
    useCallsSummary.mockReturnValue({
      summary: { totalCalls: 5, activeCalls: 2, completedCalls: 3 },
      source: 'mock',
      error: 'Fallback activado',
      isLoading: false,
    });

    render(<HomeModule />);

    expect(screen.getByText(/Total de llamadas: 5/)).toBeInTheDocument();
    expect(screen.getByText(/En curso: 2/)).toBeInTheDocument();
    expect(screen.getByText(/Completadas: 3/)).toBeInTheDocument();
    expect(screen.getByText(/datos simulados/i)).toBeInTheDocument();
    expect(screen.getByText(/Fallback activado/)).toBeInTheDocument();
  });
});
