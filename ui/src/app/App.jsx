import { useEffect } from 'react';
import MainLayout from '@components/MainLayout';
import HomePage from '../pages/HomePage';
import { useAppConfig } from '@hooks/useAppConfig';

function App() {
  const { isLoading, config, loadConfig } = useAppConfig();

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

  return (
    <MainLayout>
      <HomePage />
    </MainLayout>
  );
}

export default App;
