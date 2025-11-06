import { memo } from 'react';

const MainLayout = memo(({ children }) => {
  return (
    <div className="app-container">
      <header className="app-header">
        <h1>IACT - IVR Analytics</h1>
        <nav>
          <ul>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/reports">Reportes</a></li>
            <li><a href="/alerts">Alertas</a></li>
          </ul>
        </nav>
      </header>
      <main className="app-main" role="main">
        {children}
      </main>
      <footer className="app-footer">
        <p>IACT - Sistema de metricas IVR</p>
      </footer>
    </div>
  );
});

MainLayout.displayName = 'MainLayout';

export default MainLayout;
