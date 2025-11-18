import healthMock from '@mocks/health.json';
import { HealthService } from './HealthService';
import { getMockUsageMetrics, resetMockUsageMetrics } from '@services/utils/mockUsageTracker';

describe('HealthService', () => {
  let originalEnv;

  beforeEach(() => {
    originalEnv = { ...process.env };
    resetMockUsageMetrics();
  });

  afterEach(() => {
    process.env = { ...originalEnv };
  });

  it('uses mock data when backend source is forced to mock', async () => {
    process.env.UI_BACKEND_HEALTH_SOURCE = 'mock';
    const fetchImpl = jest.fn();

    const result = await HealthService.getStatus({ fetchImpl });

    expect(fetchImpl).not.toHaveBeenCalled();
    expect(result.source).toBe('mock');
    expect(result.data).toEqual(healthMock);
    expect(getMockUsageMetrics()).toEqual({ health: { api: 0, mock: 1 } });
  });

  it('returns api payload when endpoint succeeds', async () => {
    process.env.UI_BACKEND_HEALTH_SOURCE = 'api';
    const apiPayload = { status: 'ok', checkedAt: '2025-11-14T10:00:00Z' };
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(apiPayload),
    });

    const result = await HealthService.getStatus({ fetchImpl });

    expect(fetchImpl).toHaveBeenCalledWith('/health/', { signal: undefined });
    expect(result.source).toBe('api');
    expect(result.data).toEqual(apiPayload);
    expect(getMockUsageMetrics()).toEqual({ health: { api: 1, mock: 0 } });
  });

  it('falls back to mock data when api fails', async () => {
    process.env.UI_BACKEND_HEALTH_SOURCE = 'api';
    const fetchImpl = jest.fn().mockResolvedValue({ ok: false, status: 503, statusText: 'Service Unavailable' });

    const result = await HealthService.getStatus({ fetchImpl });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual(healthMock);
    expect(result.error).toBeInstanceOf(Error);
    expect(getMockUsageMetrics()).toEqual({ health: { api: 0, mock: 1 } });
  });
});
