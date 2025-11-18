import { createResilientService } from '@services/createResilientService';
import { loadMock } from '@mocks/registry';
import { shouldUseMockForDomain } from '@services/flags/backendIntegrity';

const HEALTH_ENDPOINT = '/health/';
const { data: healthMock } = loadMock('health');

const baseService = createResilientService({
  id: 'health',
  endpoint: HEALTH_ENDPOINT,
  mockDataLoader: () => Promise.resolve(healthMock),
  shouldUseMock: () => shouldUseMockForDomain('health'),
  errorMessage: 'No fue posible obtener el estado del backend',
  isPayloadValid: (payload) => Boolean(payload && typeof payload.status === 'string'),
});

export class HealthService {
  static async getStatus(options = {}) {
    return baseService.fetch(options);
  }

  static async fetchFromApi(options = {}) {
    return baseService.fetchFromApi(options);
  }

  static async fetchFromMock() {
    return baseService.fetchFromMock();
  }

  static shouldUseMock() {
    return shouldUseMockForDomain('health');
  }
}
