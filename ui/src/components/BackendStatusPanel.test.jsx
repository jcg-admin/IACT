import { render, screen } from '@testing-library/react';
import BackendStatusPanel from './BackendStatusPanel';

const baseProps = {
  health: {
    status: 'ok',
    lastChecked: '2025-11-14T12:00:00Z',
    source: 'api',
    error: null,
  },
  mockSummary: {
    totalDomains: 3,
    domainsUsingMock: 1,
    metrics: {
      calls: { api: 1, mock: 0 },
      config: { api: 0, mock: 2 },
    },
  },
};

describe('BackendStatusPanel', () => {
  it('renders health status and mock dependency summary', () => {
    render(<BackendStatusPanel {...baseProps} />);

    expect(screen.getByText(/estado backend/i)).toBeInTheDocument();
    expect(screen.getByText(/ok/i)).toBeInTheDocument();
    expect(screen.getByText(/1 de 3 dominios usan mocks/i)).toBeInTheDocument();
  });

  it('shows error message when available', () => {
    render(
      <BackendStatusPanel
        {...baseProps}
        health={{ ...baseProps.health, status: 'degraded', error: 'fallo api' }}
      />
    );

    expect(screen.getByText(/fallo api/i)).toBeInTheDocument();
  });
});
