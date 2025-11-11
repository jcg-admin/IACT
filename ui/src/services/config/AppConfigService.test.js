import configMock from '@mocks/config.json';
import { AppConfigService } from './AppConfigService';

describe('AppConfigService', () => {
  const apiConfig = { featureFlags: { useCallsMock: false }, branding: { productName: 'API' } };
  let fetchImpl;

  beforeEach(() => {
    fetchImpl = jest.fn();
  });

  it('returns API configuration when the endpoint responds OK', async () => {
    fetchImpl.mockResolvedValue({ ok: true, json: () => Promise.resolve(apiConfig) });

    const result = await AppConfigService.getConfig({ fetchImpl });

    expect(fetchImpl).toHaveBeenCalledWith('/api/config', { signal: undefined });
    expect(result.source).toBe('api');
    expect(result.data).toEqual(apiConfig);
    expect(result.error).toBeNull();
  });

  it('falls back to mock configuration when the endpoint fails', async () => {
    fetchImpl.mockResolvedValue({ ok: false, status: 500, statusText: 'Server Error' });

    const result = await AppConfigService.getConfig({ fetchImpl });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual(configMock);
    expect(result.error).toBeInstanceOf(Error);
    expect(result.error.message).toContain('500');
  });

  it('falls back to mock configuration when the fetch rejects', async () => {
    fetchImpl.mockRejectedValue(new Error('Network down'));

    const result = await AppConfigService.getConfig({ fetchImpl });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual(configMock);
    expect(result.error).toBeInstanceOf(Error);
    expect(result.error.message).toContain('Network down');
  });
});
