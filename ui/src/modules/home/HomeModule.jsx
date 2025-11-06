import { useHomeAnnouncement } from './hooks/useHomeAnnouncement';

function HomeModule() {
  const { announcement, isLoading } = useHomeAnnouncement();

  if (isLoading) {
    return <div>Cargando anuncios...</div>;
  }

  return (
    <div className="home-module">
      <h2>Dashboard Principal</h2>
      {announcement && (
        <div className="announcement-box">
          <p>{announcement}</p>
        </div>
      )}
      <div className="widgets-grid">
        <div className="widget">
          <h3>Metricas IVR</h3>
          <p>Llamadas procesadas: ...</p>
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
