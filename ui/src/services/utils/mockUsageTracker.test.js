import { recordMockUsage, getMockUsageMetrics, resetMockUsageMetrics } from './mockUsageTracker';

describe('mockUsageTracker', () => {
  beforeEach(() => {
    resetMockUsageMetrics();
  });

  it('records usage per domain and source', () => {
    recordMockUsage('calls', 'api');
    recordMockUsage('calls', 'mock');
    recordMockUsage('config', 'mock');

    expect(getMockUsageMetrics()).toEqual({
      calls: { api: 1, mock: 1 },
      config: { api: 0, mock: 1 },
    });
  });

  it('ignores unknown sources', () => {
    recordMockUsage('calls', 'other');

    expect(getMockUsageMetrics()).toEqual({});
  });

  it('resets metrics removing tracked domains', () => {
    recordMockUsage('calls', 'api');
    resetMockUsageMetrics();

    expect(getMockUsageMetrics()).toEqual({});
  });

  it('ignores events without domain information', () => {
    recordMockUsage('', 'api');

    expect(getMockUsageMetrics()).toEqual({});
  });
});
