import { memo, useEffect, useState } from 'react';
import MockDataNotice from './MockDataNotice';
import { PermissionsService } from '@services/permissions/PermissionsService';

const MainLayout = memo(({ children, mockNotice }) => {
  const [menuEntries, setMenuEntries] = useState([]);
  const [menuError, setMenuError] = useState(null);

  useEffect(() => {
    let isActive = true;

    const loadMenu = async () => {
      try {
        const result = await PermissionsService.getNormalizedPermissions();
        if (isActive) {
          setMenuEntries(result.data.menuEntries);
          setMenuError(null);
        }
      } catch (error) {
        if (isActive) {
          setMenuEntries([]);
          setMenuError(error.message);
        }
      }
    };

    loadMenu();

    return () => {
      isActive = false;
    };
  }, []);

  const renderMenuItems = () => {
    if (menuEntries.length === 0) {
      return (
        <li className="menu-placeholder" data-testid="menu-placeholder">
          {menuError ? 'Menu no disponible' : 'Cargando menu...'}
        </li>
      );
    }

    return menuEntries.map((entry) => {
      const path = entry.code === 'dashboards' ? '/' : `/${entry.code}`;

      return (
        <li key={entry.id}>
          <a href={path}>{entry.label}</a>
        </li>
      );
    });
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>IACT - IVR Analytics</h1>
        <nav>
          <ul>
            {renderMenuItems()}
          </ul>
        </nav>
      </header>
      <MockDataNotice {...mockNotice} />
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

MainLayout.defaultProps = {
  mockNotice: { isVisible: false },
};

export default MainLayout;
