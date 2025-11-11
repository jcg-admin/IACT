import { useEffect } from 'react';
import MainLayout from '@components/MainLayout';
import HomePage from '../pages/HomePage';
import { useAppConfig } from '@hooks/useAppConfig';

function App() {
  const { isLoading, config, loadConfig, source, error } = useAppConfig();

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  if (isLoading) {
    return (
      <div className="loading-container">
        <p>Cargando configuración...</p>
      </div>
    );
  }

  const showMockBanner = (config?.featureFlags?.showMockBanner ?? true) && source === 'mock';
  const mockNotice = {
    isVisible: showMockBanner,
    message: 'Mostrando datos simulados mientras se habilita el backend.',
    details: error ?? undefined,
  };

  return (
    <MainLayout mockNotice={mockNotice}>
      <HomePage />
    </MainLayout>
  );
}

export default App;
