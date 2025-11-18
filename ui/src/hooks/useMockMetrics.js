import { useEffect, useState } from 'react';
import { getMockUsageMetrics, subscribeMockUsage } from '@services/utils/mockUsageTracker';

const buildSummary = (metrics) => {
  const entries = Object.values(metrics || {});
  const totalDomains = Object.keys(metrics || {}).length;
  const domainsUsingMock = entries.filter((entry) => entry.mock > 0).length;

  return { totalDomains, domainsUsingMock };
};

export const useMockMetrics = () => {
  const [metrics, setMetrics] = useState(getMockUsageMetrics());

  useEffect(() => {
    const unsubscribe = subscribeMockUsage(setMetrics);
    return unsubscribe;
  }, []);

  return { metrics, summary: buildSummary(metrics) };
};
