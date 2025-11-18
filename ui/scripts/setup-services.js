#!/usr/bin/env node
/**
 * Script to setup all missing UI services for backend endpoints
 * Creates directory structure and all service implementation files
 * 
 * Usage: node scripts/setup-services.js
 */

const fs = require('fs');
const path = require('path');

const servicesDir = path.resolve(__dirname, '../src/services');

// Service definitions with their configurations
const serviceConfigs = {
  users: {
    endpoint: '/api/v1/usuarios/',
    mockKey: 'users',
    mockFile: 'usuarios.json',
    validateFields: ['usuarios', 'grupos'],
    className: 'UsersService',
    method: 'getUsers',
  },
  dashboard: {
    endpoint: '/api/v1/dashboard/',
    mockKey: 'dashboard',
    mockFile: 'dashboard.json',
    validateFields: ['overview', 'widgets'],
    className: 'DashboardService',
    method: 'getDashboard',
  },
  configuracion: {
    endpoint: '/api/v1/configuracion/',
    mockKey: 'configuracion',
    mockFile: 'configuracion.json',
    validateFields: ['parametros'],
    className: 'ConfiguracionService',
    method: 'getConfiguracion',
  },
  configuration: {
    endpoint: '/api/v1/configuracion/',
    mockKey: 'configuration',
    mockFile: 'configuration.json',
    validateFields: ['settings'],
    className: 'ConfigurationService',
    method: 'getConfiguration',
  },
  presupuestos: {
    endpoint: '/api/v1/presupuestos/',
    mockKey: 'presupuestos',
    mockFile: 'presupuestos.json',
    validateFields: ['presupuestos'],
    className: 'PresupuestosService',
    method: 'getPresupuestos',
  },
  politicas: {
    endpoint: '/api/v1/politicas/',
    mockKey: 'politicas',
    mockFile: 'politicas.json',
    validateFields: ['politicas'],
    className: 'PoliticasService',
    method: 'getPoliticas',
  },
  excepciones: {
    endpoint: '/api/v1/excepciones/',
    mockKey: 'excepciones',
    mockFile: 'excepciones.json',
    validateFields: ['excepciones'],
    className: 'ExcepcionesService',
    method: 'getExcepciones',
  },
  reportes: {
    endpoint: '/api/v1/reportes/',
    mockKey: 'reportes',
    mockFile: 'reportes.json',
    validateFields: ['reportes'],
    className: 'ReportesService',
    method: 'getReportes',
  },
  notifications: {
    endpoint: '/api/v1/notifications/messages/',
    mockKey: 'notifications',
    mockFile: 'notifications.json',
    validateFields: ['messages'],
    className: 'NotificationsService',
    method: 'getNotifications',
  },
  etl: {
    endpoint: '/api/v1/etl/jobs/',
    mockKey: 'etl',
    mockFile: 'etl.json',
    validateFields: ['jobs'],
    className: 'ETLService',
    method: 'getJobs',
  },
  dora: {
    endpoint: '/api/dora/',
    mockKey: 'dora',
    mockFile: 'dora.json',
    validateFields: ['metrics'],
    className: 'DORAMetricsService',
    method: 'getMetrics',
  },
};

// Generate service implementation
const generateServiceImplementation = (config) => {
  const validationLogic = config.validateFields.map(field => `Array.isArray(payload.${field}) || payload.${field}`).join(' || ');
  
  return `import { createResilientService } from '@services/createResilientService';
import { loadMock } from '@mocks/registry';
import { shouldUseMockForDomain } from '@services/flags/backendIntegrity';

const ENDPOINT = '${config.endpoint}';
const { data: mock } = loadMock('${config.mockKey}');

const isPayloadValid = (payload) => {
  if (!payload) {
    return false;
  }
  return ${validationLogic};
};

const baseService = createResilientService({
  id: '${config.mockKey}',
  endpoint: ENDPOINT,
  mockDataLoader: () => Promise.resolve(mock),
  shouldUseMock: () => shouldUseMockForDomain('${config.mockKey}'),
  errorMessage: 'No fue posible obtener los datos del backend',
  isPayloadValid,
});

export class ${config.className} {
  static async ${config.method}(options = {}) {
    return baseService.fetch(options);
  }

  static async fetchFromApi(options = {}) {
    return baseService.fetchFromApi(options);
  }

  static async fetchFromMock() {
    return baseService.fetchFromMock();
  }

  static shouldUseMock() {
    return shouldUseMockForDomain('${config.mockKey}');
  }
}
`;
};

// Generate test file
const generateTestFile = (config) => {
  return `import mock from '@mocks/${config.mockFile}';
import { ${config.className} } from './${config.className}';
import { resetMockUsageMetrics, getMockUsageMetrics } from '@services/utils/mockUsageTracker';

describe('${config.className}', () => {
  let originalEnv;

  beforeEach(() => {
    originalEnv = { ...process.env };
    resetMockUsageMetrics();
  });

  afterEach(() => {
    process.env = { ...originalEnv };
  });

  it('returns mock data when the feature flag forces mock usage', async () => {
    process.env.UI_BACKEND_${config.mockKey.toUpperCase()}_SOURCE = 'mock';
    const fetchImpl = jest.fn();

    const result = await ${config.className}.${config.method}({ fetchImpl });

    expect(fetchImpl).not.toHaveBeenCalled();
    expect(result.source).toBe('mock');
    expect(result.data).toEqual(mock);
    expect(result.metadata).toEqual({ domain: '${config.mockKey}' });
    expect(getMockUsageMetrics()).toEqual({ ${config.mockKey}: { api: 0, mock: 1 } });
  });

  it('returns API data when the endpoint succeeds', async () => {
    process.env.UI_BACKEND_${config.mockKey.toUpperCase()}_SOURCE = 'api';
    const apiPayload = mock;
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(apiPayload),
    });

    const result = await ${config.className}.${config.method}({ fetchImpl });

    expect(fetchImpl).toHaveBeenCalledWith('${config.endpoint}', { signal: undefined });
    expect(result.source).toBe('api');
    expect(result.data).toEqual(apiPayload);
    expect(getMockUsageMetrics()).toEqual({ ${config.mockKey}: { api: 1, mock: 0 } });
  });

  it('falls back to mocks when API fails', async () => {
    process.env.UI_BACKEND_${config.mockKey.toUpperCase()}_SOURCE = 'api';
    const fetchImpl = jest.fn().mockResolvedValue({ ok: false, status: 503 });

    const result = await ${config.className}.${config.method}({ fetchImpl });

    expect(result.source).toBe('mock');
    expect(result.data).toEqual(mock);
  });

  it('validates payload structure', async () => {
    process.env.UI_BACKEND_${config.mockKey.toUpperCase()}_SOURCE = 'api';
    const validPayload = mock;
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(validPayload),
    });

    const result = await ${config.className}.${config.method}({ fetchImpl });

    expect(result.source).toBe('api');
  });

  it('provides fetchFromApi method', async () => {
    const apiPayload = mock;
    const fetchImpl = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(apiPayload),
    });

    const result = await ${config.className}.fetchFromApi({ fetchImpl });

    expect(result).toEqual(apiPayload);
  });

  it('provides fetchFromMock method', async () => {
    const result = await ${config.className}.fetchFromMock();

    expect(result).toEqual(mock);
  });

  it('provides shouldUseMock method', () => {
    process.env.UI_BACKEND_${config.mockKey.toUpperCase()}_SOURCE = 'mock';
    expect(${config.className}.shouldUseMock()).toBe(true);

    process.env.UI_BACKEND_${config.mockKey.toUpperCase()}_SOURCE = 'api';
    expect(${config.className}.shouldUseMock()).toBe(false);
  });
});
`;
};

// Create all services
Object.entries(serviceConfigs).forEach(([serviceName, config]) => {
  const serviceDir = path.join(servicesDir, serviceName);
  
  // Create directory
  if (!fs.existsSync(serviceDir)) {
    fs.mkdirSync(serviceDir, { recursive: true });
    console.log(`Created directory: ${serviceDir}`);
  }
  
  // Create service file
  const servicePath = path.join(serviceDir, `${config.className}.js`);
  const serviceContent = generateServiceImplementation(config);
  fs.writeFileSync(servicePath, serviceContent);
  console.log(`Created service: ${servicePath}`);
  
  // Create test file
  const testPath = path.join(serviceDir, `${config.className}.test.js`);
  const testContent = generateTestFile(config);
  fs.writeFileSync(testPath, testContent);
  console.log(`Created test: ${testPath}`);
});

console.log('\nAll services created successfully!');
console.log('\nNext steps:');
console.log('1. Update ui/src/mocks/registry.js to register new mocks');
console.log('2. Update ui/src/mocks/schemas.js to add validators');
console.log('3. Update ui/src/mocks/metadata.js to add metadata');
console.log('4. Run: npm test to verify all services work correctly');
