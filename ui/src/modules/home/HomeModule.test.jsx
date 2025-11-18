import { render, screen } from '@testing-library/react';
import HomeModule from './HomeModule';
import { useHomeAnnouncement } from './hooks/useHomeAnnouncement';
import { useCallsSummary } from './hooks/useCallsSummary';

jest.mock('./hooks/useHomeAnnouncement');
jest.mock('./hooks/useCallsSummary');

describe('HomeModule', () => {
  const announcementMock = {
    title: 'Concept: Microfrontends',
    videoPlatforms: ['Youtube', 'Bilibili'],
    summary: ['A microfrontend is a microservice that exists within a browser.'],
    sections: [
      {
        heading: 'Comparison to Microservices',
        paragraphs: ['Independent builds and deployments are a shared principle.'],
      },
    ],
    tasks: ['Mantener despliegues independientes.'],
  };

  beforeEach(() => {
    useHomeAnnouncement.mockReturnValue({
      announcement: announcementMock,
      isLoading: false,
      source: 'fallback',
      error: 'Error cargando anuncios',
    });
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

  it('renders the microfrontends educational announcement with fallback notice', () => {
    render(<HomeModule />);

    expect(screen.getByRole('heading', { name: /Concept: Microfrontends/ })).toBeInTheDocument();
    expect(screen.getByText(/Tutorial video: Youtube \/ Bilibili/)).toBeInTheDocument();
    expect(screen.getByText(/Independent builds and deployments/)).toBeInTheDocument();
    expect(screen.getByText(/Mantener despliegues independientes/)).toBeInTheDocument();
    expect(screen.getByText(/Mostrando contenido educativo local/)).toBeInTheDocument();
  });
});
