import { createResilientService } from './createResilientService';
import { resetMockUsageMetrics, getMockUsageMetrics } from './utils/mockUsageTracker';

describe('createResilientService', () => {
  const mockData = { ok: true, value: 42 };
  const endpoint = '/api/test';
  const errorMessage = 'Fallo la peticion';
  let fetchImpl;
  let shouldUseMock;

  beforeEach(() => {
    fetchImpl = jest.fn();
    shouldUseMock = jest.fn(() => false);
    resetMockUsageMetrics();
  });

  const buildService = (options = {}) =>
    createResilientService({
      id: 'test',
      endpoint,
      errorMessage,
      shouldUseMock,
      mockDataLoader: () => Promise.resolve(mockData),
      isPayloadValid: (payload) => Boolean(payload && payload.ok),
      ...options,
    });

  it('throws if required parameters are missing', () => {
    expect(() => createResilientService({ id: 'test' })).toThrow('requiere un endpoint');
  });

  it('requires a mockDataLoader function', () => {
    expect(() =>
      createResilientService({ id: 'test', endpoint: '/api/test' })
    ).toThrow('mockDataLoader');
  });

  it('requires an identifier for the domain', () => {
    expect(() =>
      createResilientService({ endpoint: '/api/test', mockDataLoader: () => Promise.resolve(mockData) })
    ).toThrow('identificador de dominio');
  });

  it('returns API data when request succeeds', async () => {
    const apiPayload = { ok: true, value: 99 };
    fetchImpl.mockResolvedValue({ ok: true, json: () => Promise.resolve(apiPayload) });
    const service = buildService();

    const result = await service.fetch({ fetchImpl });

    expect(fetchImpl).toHaveBeenCalledWith(endpoint, { signal: undefined });
    expect(result).toEqual({ data: apiPayload, source: 'api', error: null, metadata: { domain: 'test' } });
    expect(getMockUsageMetrics()).toEqual({ test: { api: 1, mock: 0 } });
  });

  it('falls back to mock data when API fails', async () => {
    fetchImpl.mockResolvedValue({ ok: false, status: 500, statusText: 'Server Error' });
    const service = buildService();

    const result = await service.fetch({ fetchImpl });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual(mockData);
    expect(result.error).toBeInstanceOf(Error);
    expect(getMockUsageMetrics()).toEqual({ test: { api: 0, mock: 1 } });
  });

  it('returns mock data immediately when flag enforces mock usage', async () => {
    shouldUseMock.mockReturnValue(true);
    const service = buildService();

    const result = await service.fetch({ fetchImpl });

    expect(fetchImpl).not.toHaveBeenCalled();
    expect(result.source).toBe('mock');
    expect(result.data).toEqual(mockData);
    expect(getMockUsageMetrics()).toEqual({ test: { api: 0, mock: 1 } });
  });

  it('exposes helpers to fetch directly from api or mock', async () => {
    const apiPayload = { ok: true, value: 100 };
    fetchImpl.mockResolvedValue({ ok: true, json: () => Promise.resolve(apiPayload) });
    const service = buildService();

    const apiData = await service.fetchFromApi({ fetchImpl });
    const mockDataResult = await service.fetchFromMock();

    expect(apiData).toEqual(apiPayload);
    expect(mockDataResult).toEqual(mockData);
  });

  it('propagates errors from fetchFromApi when response is not ok', async () => {
    fetchImpl.mockResolvedValue({ ok: false, status: 500, statusText: 'Server Error' });
    const service = buildService();

    await expect(service.fetchFromApi({ fetchImpl })).rejects.toEqual({ status: 500, statusText: 'Server Error' });
  });

  it('throws when fetchFromApi lacks an implementation', async () => {
    const service = buildService();

    await expect(service.fetchFromApi()).rejects.toThrow('fetchImpl');
  });

  it('throws when api payload is invalid', async () => {
    fetchImpl.mockResolvedValue({ ok: true, json: () => Promise.resolve({ ok: false }) });
    const service = buildService();

    await expect(service.fetch({ fetchImpl })).resolves.toMatchObject({ source: 'mock' });
  });
});
