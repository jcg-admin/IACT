import { useHomeAnnouncement } from './hooks/useHomeAnnouncement';
import { useCallsSummary } from './hooks/useCallsSummary';
import AnnouncementContent from './components/AnnouncementContent';

function HomeModule() {
  const { announcement, isLoading, source: announcementSource, error: announcementError } =
    useHomeAnnouncement();
  const {
    summary: callsSummary,
    isLoading: isCallsLoading,
    source: callsSource,
    error: callsError,
  } = useCallsSummary();

  if (isLoading) {
    return <div>Cargando anuncios...</div>;
  }

  return (
    <div className="home-module">
      <h2>Dashboard Principal</h2>
      {announcement && (
        <div className="announcement-box">
          <AnnouncementContent announcement={announcement} />
          {announcementSource === 'fallback' && (
            <p className="announcement-fallback" role="status">
              Mostrando contenido educativo local por falta de comunicación con el backend.
            </p>
          )}
          {announcementError && (
            <p className="announcement-error" role="status">
              {announcementError}
            </p>
          )}
        </div>
      )}
      <div className="widgets-grid">
        <div className="widget">
          <h3>Métricas de llamadas</h3>
          {isCallsLoading ? (
            <p>Cargando llamadas...</p>
          ) : (
            <div>
              <p>{`Total de llamadas: ${callsSummary.totalCalls}`}</p>
              <p>{`En curso: ${callsSummary.activeCalls}`}</p>
              <p>{`Completadas: ${callsSummary.completedCalls}`}</p>
              {callsSource === 'mock' && (
                <p className="calls-mock-indicator">Datos simulados por ausencia de backend.</p>
              )}
              {callsError && <p className="calls-error" role="alert">{callsError}</p>}
            </div>
          )}
        </div>
        <div className="widget">
          <h3>Tiempo promedio</h3>
          <p>Duracion: ...</p>
        </div>
      </div>
    </div>
  );
}

export default HomeModule;
