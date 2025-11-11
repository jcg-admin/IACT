import { createResilientService } from '@services/createResilientService';
import { loadMock } from '@mocks/registry';
import { shouldUseMockForDomain } from '@services/flags/backendIntegrity';

const CALLS_ENDPOINT = '/api/v1/llamadas/';
const { data: callsMock } = loadMock('calls');

const isCallsPayloadValid = (payload) => {
  if (!payload) {
    return false;
  }

  const hasCalls = Array.isArray(payload.llamadas) && payload.llamadas.length > 0;
  const hasCatalogs = Array.isArray(payload.estados) || Array.isArray(payload.tipos);

  return hasCalls || hasCatalogs;
};

const baseService = createResilientService({
  id: 'calls',
  endpoint: CALLS_ENDPOINT,
  mockDataLoader: () => Promise.resolve(callsMock),
  shouldUseMock: () => shouldUseMockForDomain('calls'),
  errorMessage: 'No fue posible obtener las llamadas del backend',
  isPayloadValid: isCallsPayloadValid,
});

export class CallsService {
  static async getCalls(options = {}) {
    return baseService.fetch(options);
  }

  static async fetchFromApi(options = {}) {
    return baseService.fetchFromApi(options);
  }

  static async fetchFromMock() {
    return baseService.fetchFromMock();
  }

  static shouldUseMock() {
    return shouldUseMockForDomain('calls');
  }
}
