const MockDataNotice = ({ isVisible, message, details }) => {
  if (!isVisible) {
    return null;
  }

  return (
    <div className="mock-notice" role="status" aria-live="polite" title={details || undefined}>
      <strong>Datos simulados.</strong> {message}
    </div>
  );
};

MockDataNotice.defaultProps = {
  message: 'Algunas funcionalidades utilizan mocks locales mientras el backend se habilita.',
  details: undefined,
};

export default MockDataNotice;
