import configMock from '@mocks/config.json';
import { fetchWithFallback } from '@services/utils/fetchWithFallback';

const CONFIG_ENDPOINT = '/api/config';

const shouldUseConfigMock = () => (process.env.UI_USE_CONFIG_MOCKS || '').toLowerCase() === 'true';

export class AppConfigService {
  /**
   * @param {{fetchImpl?: typeof fetch, signal?: AbortSignal}} [options]
   */
  static async getConfig(options = {}) {
    const { fetchImpl, signal } = options;
    return fetchWithFallback({
      url: CONFIG_ENDPOINT,
      fetchImpl,
      signal,
      shouldUseMock: shouldUseConfigMock,
      mockDataLoader: () => Promise.resolve(configMock),
      errorMessage: 'No fue posible obtener la configuracion de la aplicacion',
      isPayloadValid: (payload) => Boolean(payload && Object.keys(payload).length > 0),
    });
  }
}
