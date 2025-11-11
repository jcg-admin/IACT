import { createResilientService } from '@services/createResilientService';
import { loadMock } from '@mocks/registry';
import { shouldUseMockForDomain } from '@services/flags/backendIntegrity';

const CONFIG_ENDPOINT = '/api/config';
const { data: configMock } = loadMock('config');

const baseService = createResilientService({
  id: 'config',
  endpoint: CONFIG_ENDPOINT,
  mockDataLoader: () => Promise.resolve(configMock),
  shouldUseMock: () => shouldUseMockForDomain('config'),
  errorMessage: 'No fue posible obtener la configuracion de la aplicacion',
  isPayloadValid: (payload) => Boolean(payload && Object.keys(payload).length > 0),
});

export class AppConfigService {
  static async getConfig(options = {}) {
    return baseService.fetch(options);
  }

  static async fetchFromApi(options = {}) {
    return baseService.fetchFromApi(options);
  }

  static async fetchFromMock() {
    return baseService.fetchFromMock();
  }

  static shouldUseMock() {
    return shouldUseMockForDomain('config');
  }
}
