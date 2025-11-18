const BackendStatusPanel = ({ health, mockSummary }) => {
  const healthStatus = health?.status ?? 'unknown';
  const lastChecked = health?.lastChecked;
  const source = health?.source ?? 'unknown';
  const error = health?.error;

  const mockCount = mockSummary?.domainsUsingMock ?? 0;
  const totalDomains = mockSummary?.totalDomains ?? 0;

  return (
    <section className="backend-status" aria-label="Estado backend">
      <div className={`backend-status__health backend-status__health--${healthStatus}`}>
        <strong>Estado backend:</strong> {healthStatus}
        {source && <span className="backend-status__source">Fuente: {source}</span>}
        {lastChecked && <span className="backend-status__timestamp">Última verificación: {lastChecked}</span>}
      </div>
      {error && (
        <p className="backend-status__error" role="alert">
          {error}
        </p>
      )}
      <div className="backend-status__mocks">
        <strong>Dependencia de mocks:</strong> {mockCount} de {totalDomains} dominios usan mocks
      </div>
    </section>
  );
};

BackendStatusPanel.defaultProps = {
  health: {
    status: 'unknown',
    lastChecked: null,
    source: 'unknown',
    error: null,
  },
  mockSummary: {
    domainsUsingMock: 0,
    totalDomains: 0,
    metrics: {},
  },
};

export default BackendStatusPanel;
