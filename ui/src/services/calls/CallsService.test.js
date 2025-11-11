import callsMock from '@mocks/llamadas.json';
import { CallsService } from './CallsService';
import { resetMockUsageMetrics, getMockUsageMetrics } from '@services/utils/mockUsageTracker';

describe('CallsService', () => {
  let originalEnv;

  beforeEach(() => {
    originalEnv = { ...process.env };
    resetMockUsageMetrics();
  });

  afterEach(() => {
    process.env = { ...originalEnv };
  });

  it('returns mock data when the feature flag forces mock usage', async () => {
    process.env.UI_BACKEND_CALLS_SOURCE = 'mock';
    const fetchImpl = jest.fn();

    const result = await CallsService.getCalls({ fetchImpl });

    expect(fetchImpl).not.toHaveBeenCalled();
    expect(result.source).toBe('mock');
    expect(result.data).toEqual(callsMock);
    expect(result.metadata).toEqual({ domain: 'calls' });
    expect(getMockUsageMetrics()).toEqual({ calls: { api: 0, mock: 1 } });
  });

  it('returns API data when the endpoint succeeds and mocks are disabled', async () => {
    process.env.UI_BACKEND_CALLS_SOURCE = 'api';
    const apiPayload = { llamadas: [], estados: [], tipos: [] };
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(apiPayload),
    });

    const result = await CallsService.getCalls({ fetchImpl });

    expect(fetchImpl).toHaveBeenCalledWith('/api/v1/llamadas/', { signal: undefined });
    expect(result.source).toBe('api');
    expect(result.data).toEqual(apiPayload);
    expect(result.metadata).toEqual({ domain: 'calls' });
    expect(getMockUsageMetrics()).toEqual({ calls: { api: 1, mock: 0 } });
  });

  it('falls back to mocks when the API request fails', async () => {
    process.env.UI_BACKEND_CALLS_SOURCE = 'api';
    const fetchImpl = jest.fn().mockResolvedValue({ ok: false, status: 503, statusText: 'Service Unavailable' });

    const result = await CallsService.getCalls({ fetchImpl });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual(callsMock);
    expect(result.error).toBeInstanceOf(Error);
    expect(getMockUsageMetrics()).toEqual({ calls: { api: 0, mock: 1 } });
  });

  it('falls back to mocks when the API returns an empty payload', async () => {
    process.env.UI_BACKEND_CALLS_SOURCE = 'api';
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ llamadas: [] }),
    });

    const result = await CallsService.getCalls({ fetchImpl });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual(callsMock);
    expect(result.error).toBeInstanceOf(Error);
    expect(result.error.message).toContain('payload vacio');
    expect(getMockUsageMetrics()).toEqual({ calls: { api: 0, mock: 1 } });
  });

  it('exposes helper methods for direct fetch and flag state', async () => {
    process.env.UI_BACKEND_CALLS_SOURCE = 'api';
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ llamadas: callsMock.llamadas, estados: [], tipos: [] }),
    });

    const apiData = await CallsService.fetchFromApi({ fetchImpl });
    const mockData = await CallsService.fetchFromMock();

    expect(apiData.llamadas).toHaveLength(callsMock.llamadas.length);
    expect(mockData).toEqual(callsMock);
    expect(CallsService.shouldUseMock()).toBe(false);
  });

  it('reports mock toggle state when env forces mocks', () => {
    process.env.UI_BACKEND_CALLS_SOURCE = 'mock';

    expect(CallsService.shouldUseMock()).toBe(true);
  });
});
