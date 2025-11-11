import callsMock from '@mocks/llamadas.json';
import { CallsService } from './CallsService';

describe('CallsService', () => {
  let originalEnv;

  beforeEach(() => {
    originalEnv = { ...process.env };
  });

  afterEach(() => {
    process.env = { ...originalEnv };
  });

  it('returns mock data when the feature flag forces mock usage', async () => {
    process.env.UI_USE_CALLS_MOCKS = 'true';
    const fetchImpl = jest.fn();

    const result = await CallsService.getCalls({ fetchImpl });

    expect(fetchImpl).not.toHaveBeenCalled();
    expect(result.source).toBe('mock');
    expect(result.data).toEqual(callsMock);
  });

  it('returns API data when the endpoint succeeds and mocks are disabled', async () => {
    process.env.UI_USE_CALLS_MOCKS = 'false';
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ llamadas: [], estados: [], tipos: [] }),
    });

    const result = await CallsService.getCalls({ fetchImpl });

    expect(fetchImpl).toHaveBeenCalledWith('/api/v1/llamadas/', { signal: undefined });
    expect(result.source).toBe('api');
    expect(result.data).toEqual({ llamadas: [], estados: [], tipos: [] });
  });

  it('falls back to mocks when the API request fails', async () => {
    process.env.UI_USE_CALLS_MOCKS = 'false';
    const fetchImpl = jest.fn().mockResolvedValue({ ok: false, status: 503, statusText: 'Service Unavailable' });

    const result = await CallsService.getCalls({ fetchImpl });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual(callsMock);
    expect(result.error).toBeInstanceOf(Error);
    expect(result.error.message).toContain('503');
  });

  it('falls back to mocks when the API returns an empty payload', async () => {
    process.env.UI_USE_CALLS_MOCKS = 'false';
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ llamadas: [] }),
    });

    const result = await CallsService.getCalls({ fetchImpl });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual(callsMock);
    expect(result.error).toBeInstanceOf(Error);
    expect(result.error.message).toContain('payload vacio');
  });
});
