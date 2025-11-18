import { renderHook, act } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore } from '@reduxjs/toolkit';
import healthReducer, { selectHealthStatus, selectHealthError } from '@state/slices/healthSlice';
import { useHealthStatus } from './useHealthStatus';
import { HealthService } from '@services/health/HealthService';

jest.mock('@services/health/HealthService', () => ({
  HealthService: {
    getStatus: jest.fn(),
  },
}));

const createStore = () =>
  configureStore({
    reducer: {
      observability: healthReducer,
    },
  });

const wrapperFactory = (store) => ({ children }) => <Provider store={store}>{children}</Provider>;

describe('useHealthStatus', () => {
  it('loads health status into the store', async () => {
    const store = createStore();
    HealthService.getStatus.mockResolvedValue({
      data: { status: 'ok', checkedAt: '2025-11-14T12:00:00Z' },
      source: 'api',
      error: null,
    });

    const { result } = renderHook(() => useHealthStatus(), { wrapper: wrapperFactory(store) });

    await act(async () => {
      await result.current.checkHealth();
    });

    expect(selectHealthStatus(store.getState())).toBe('ok');
    expect(result.current.source).toBe('api');
    expect(result.current.lastChecked).toBe('2025-11-14T12:00:00Z');
  });

  it('stores error when the service throws', async () => {
    const store = createStore();
    HealthService.getStatus.mockRejectedValue(new Error('backend caido'));

    const { result } = renderHook(() => useHealthStatus(), { wrapper: wrapperFactory(store) });

    await act(async () => {
      await result.current.checkHealth();
    });

    expect(selectHealthError(store.getState())).toBe('backend caido');
    expect(result.current.status).toBe('unknown');
  });
});
