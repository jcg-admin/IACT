import { getBackendSourceForDomain, shouldUseMockForDomain } from './backendIntegrity';

const ORIGINAL_ENV = { ...process.env };

describe('backendIntegrity flags', () => {
  afterEach(() => {
    process.env = { ...ORIGINAL_ENV };
  });

  it('defaults to mock when env var missing', () => {
    delete process.env.UI_BACKEND_CALLS_SOURCE;

    expect(getBackendSourceForDomain('calls')).toBe('mock');
    expect(shouldUseMockForDomain('calls')).toBe(true);
  });

  it('supports overriding to api', () => {
    process.env.UI_BACKEND_CALLS_SOURCE = 'API';

    expect(getBackendSourceForDomain('calls')).toBe('api');
    expect(shouldUseMockForDomain('calls')).toBe(false);
  });

  it('falls back to mock for invalid values', () => {
    process.env.UI_BACKEND_CALLS_SOURCE = 'sometimes';

    expect(getBackendSourceForDomain('calls')).toBe('mock');
  });

  it('handles unknown domains gracefully', () => {
    expect(getBackendSourceForDomain('unknown')).toBe('mock');
    expect(shouldUseMockForDomain('unknown')).toBe(true);
  });
});
