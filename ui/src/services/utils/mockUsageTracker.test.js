import {
  recordMockUsage,
  getMockUsageMetrics,
  resetMockUsageMetrics,
  subscribeMockUsage,
} from './mockUsageTracker';

describe('mockUsageTracker subscriptions', () => {
  beforeEach(() => {
    resetMockUsageMetrics();
  });

  it('notifies subscribers when metrics change', () => {
    const events = [];
    const unsubscribe = subscribeMockUsage((data) => events.push(data));

    recordMockUsage('calls', 'mock');
    recordMockUsage('config', 'api');

    expect(events).toEqual([
      {},
      { calls: { api: 0, mock: 1 } },
      { calls: { api: 0, mock: 1 }, config: { api: 1, mock: 0 } },
    ]);

    unsubscribe();
  });
});

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
