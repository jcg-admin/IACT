import { fetchWithFallback } from './fetchWithFallback';

const mockDataLoader = () => Promise.resolve({ foo: 'bar' });

describe('fetchWithFallback', () => {
  it('returns mock data when shouldUseMock forces mock', async () => {
    const result = await fetchWithFallback({
      url: '/api/test',
      fetchImpl: jest.fn(),
      mockDataLoader,
      errorMessage: 'Fallo',
      shouldUseMock: () => true,
    });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual({ foo: 'bar' });
    expect(result.error).toBeNull();
  });

  it('returns API data on successful fetch', async () => {
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ foo: 'api' }),
    });

    const result = await fetchWithFallback({
      url: '/api/test',
      fetchImpl,
      mockDataLoader,
      errorMessage: 'Fallo',
      shouldUseMock: () => false,
    });

    expect(result.source).toBe('api');
    expect(result.data).toEqual({ foo: 'api' });
    expect(result.error).toBeNull();
  });

  it('falls back to mock data when response is not ok', async () => {
    const fetchImpl = jest.fn().mockResolvedValue({ ok: false, status: 500, statusText: 'Server Error' });

    const result = await fetchWithFallback({
      url: '/api/test',
      fetchImpl,
      mockDataLoader,
      errorMessage: 'Fallo',
    });

    expect(result.source).toBe('mock');
    expect(result.error).toBeInstanceOf(Error);
    expect(result.error.message).toContain('500');
  });

  it('falls back when payload validation fails', async () => {
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({}),
    });

    const result = await fetchWithFallback({
      url: '/api/test',
      fetchImpl,
      mockDataLoader,
      errorMessage: 'Fallo',
      isPayloadValid: (payload) => Object.keys(payload).length > 1,
    });

    expect(result.source).toBe('mock');
    expect(result.error).toBeInstanceOf(Error);
    expect(result.error.message).toContain('payload vacio');
  });
});
