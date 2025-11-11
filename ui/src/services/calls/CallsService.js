import callsMock from '@mocks/llamadas.json';
import { fetchWithFallback } from '@services/utils/fetchWithFallback';

const CALLS_ENDPOINT = '/api/v1/llamadas/';

const shouldUseCallsMock = () => (process.env.UI_USE_CALLS_MOCKS || '').toLowerCase() === 'true';

const isCallsPayloadValid = (payload) => {
  if (!payload) {
    return false;
  }

  const hasCalls = Array.isArray(payload.llamadas) && payload.llamadas.length > 0;
  const hasCatalogs = Array.isArray(payload.estados) || Array.isArray(payload.tipos);

  return hasCalls || hasCatalogs;
};

export class CallsService {
  /**
   * @param {{fetchImpl?: typeof fetch, signal?: AbortSignal}} [options]
   */
  static async getCalls(options = {}) {
    const { fetchImpl, signal } = options;
    return fetchWithFallback({
      url: CALLS_ENDPOINT,
      fetchImpl,
      signal,
      shouldUseMock: shouldUseCallsMock,
      mockDataLoader: () => Promise.resolve(callsMock),
      errorMessage: 'No fue posible obtener las llamadas del backend',
      isPayloadValid: isCallsPayloadValid,
    });
  }
}
