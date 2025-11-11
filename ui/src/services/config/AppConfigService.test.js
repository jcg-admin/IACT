import { AppConfigService } from './AppConfigService';
import { resetMockUsageMetrics, getMockUsageMetrics } from '@services/utils/mockUsageTracker';
import { loadMock } from '@mocks/registry';

const { data: configMock } = loadMock('config');

describe('AppConfigService', () => {
  let fetchImpl;
  let originalEnv;

  beforeEach(() => {
    fetchImpl = jest.fn();
    originalEnv = { ...process.env };
    resetMockUsageMetrics();
  });

  afterEach(() => {
    process.env = { ...originalEnv };
  });

  it('returns API configuration when the endpoint responds OK', async () => {
    process.env.UI_BACKEND_CONFIG_SOURCE = 'api';
    const apiConfig = { featureFlags: { useCallsMock: false }, branding: { productName: 'API' } };
    fetchImpl.mockResolvedValue({ ok: true, json: () => Promise.resolve(apiConfig) });

    const result = await AppConfigService.getConfig({ fetchImpl });

    expect(fetchImpl).toHaveBeenCalledWith('/api/config', { signal: undefined });
    expect(result.source).toBe('api');
    expect(result.data).toEqual(apiConfig);
    expect(result.metadata).toEqual({ domain: 'config' });
    expect(getMockUsageMetrics()).toEqual({ config: { api: 1, mock: 0 } });
  });

  it('falls back to mock configuration when the endpoint fails', async () => {
    process.env.UI_BACKEND_CONFIG_SOURCE = 'api';
    fetchImpl.mockResolvedValue({ ok: false, status: 500, statusText: 'Server Error' });

    const result = await AppConfigService.getConfig({ fetchImpl });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual(configMock);
    expect(result.error).toBeInstanceOf(Error);
    expect(getMockUsageMetrics()).toEqual({ config: { api: 0, mock: 1 } });
  });

  it('falls back to mock configuration when the fetch rejects', async () => {
    process.env.UI_BACKEND_CONFIG_SOURCE = 'api';
    fetchImpl.mockRejectedValue(new Error('Network down'));

    const result = await AppConfigService.getConfig({ fetchImpl });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual(configMock);
    expect(result.error).toBeInstanceOf(Error);
    expect(result.error.message).toContain('Network down');
    expect(getMockUsageMetrics()).toEqual({ config: { api: 0, mock: 1 } });
  });

  it('uses mocks immediately when flag forces it', async () => {
    process.env.UI_BACKEND_CONFIG_SOURCE = 'mock';

    const result = await AppConfigService.getConfig({ fetchImpl });

    expect(fetchImpl).not.toHaveBeenCalled();
    expect(result.source).toBe('mock');
    expect(result.data).toEqual(configMock);
    expect(getMockUsageMetrics()).toEqual({ config: { api: 0, mock: 1 } });
  });

  it('exposes helpers to fetch from api or mocks directly', async () => {
    process.env.UI_BACKEND_CONFIG_SOURCE = 'api';
    fetchImpl.mockResolvedValue({ ok: true, json: () => Promise.resolve(configMock) });

    const apiData = await AppConfigService.fetchFromApi({ fetchImpl });
    const mockData = await AppConfigService.fetchFromMock();

    expect(apiData).toEqual(configMock);
    expect(mockData).toEqual(configMock);
    expect(AppConfigService.shouldUseMock()).toBe(false);
  });

  it('reports mock usage flag when env enforces it', () => {
    process.env.UI_BACKEND_CONFIG_SOURCE = 'mock';

    expect(AppConfigService.shouldUseMock()).toBe(true);
  });
});
