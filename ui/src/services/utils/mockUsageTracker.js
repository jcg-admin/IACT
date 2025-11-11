const metrics = {};

const ensureDomain = (domain) => {
  if (!metrics[domain]) {
    metrics[domain] = { api: 0, mock: 0 };
  }

  return metrics[domain];
};

export const recordMockUsage = (domain, source) => {
  if (!domain) {
    return;
  }

  const normalizedSource = source === 'api' || source === 'mock' ? source : null;

  if (!normalizedSource) {
    return;
  }

  const entry = ensureDomain(domain);
  entry[normalizedSource] += 1;
};

export const getMockUsageMetrics = () => {
  return Object.keys(metrics).reduce((acc, domain) => {
    const { api = 0, mock = 0 } = metrics[domain] || {};
    acc[domain] = { api, mock };
    return acc;
  }, {});
};

export const resetMockUsageMetrics = () => {
  Object.keys(metrics).forEach((domain) => {
    delete metrics[domain];
  });
};
