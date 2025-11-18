import { useEffect } from 'react';
import MainLayout from '@components/MainLayout';
import HomePage from '../pages/HomePage';
import { useAppConfig } from '@hooks/useAppConfig';
import { useHealthStatus } from '@hooks/useHealthStatus';
import { useMockMetrics } from '@hooks/useMockMetrics';

function App() {
  const { isLoading, config, loadConfig, source, error } = useAppConfig();
  const { status: healthStatus, source: healthSource, lastChecked, error: healthError, checkHealth } =
    useHealthStatus();
  const { summary: mockSummary } = useMockMetrics();

  useEffect(() => {
    loadConfig();
    checkHealth();
  }, [loadConfig, checkHealth]);

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

  const backendStatus = {
    status: healthStatus,
    source: healthSource,
    lastChecked,
    error: healthError,
  };

  return (
    <MainLayout mockNotice={mockNotice} backendStatus={backendStatus} mockSummary={mockSummary}>
      <HomePage />
    </MainLayout>
  );
}

export default App;
