import { useEffect, useState } from 'react';
import { CallsService } from '@services/calls/CallsService';

const INITIAL_SUMMARY = Object.freeze({
  totalCalls: 0,
  activeCalls: 0,
  completedCalls: 0,
});

const buildSummary = (payload) => {
  const calls = Array.isArray(payload?.llamadas) ? payload.llamadas : [];

  const totalCalls = calls.length;
  const activeCalls = calls.filter((call) => call?.estado && call.estado.es_final === false).length;
  const completedCalls = calls.filter((call) => call?.estado && call.estado.es_final === true).length;

  return {
    totalCalls,
    activeCalls,
    completedCalls,
  };
};

export const useCallsSummary = () => {
  const [summary, setSummary] = useState(INITIAL_SUMMARY);
  const [source, setSource] = useState('unknown');
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isActive = true;

    const loadCalls = async () => {
      try {
        const result = await CallsService.getCalls();
        if (!isActive) {
          return;
        }
        setSummary(buildSummary(result.data));
        setSource(result.source);
        setError(result.error ? result.error.message : null);
      } catch (err) {
        if (!isActive) {
          return;
        }
        setSummary(INITIAL_SUMMARY);
        setSource('error');
        setError(err.message);
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    };

    loadCalls();

    return () => {
      isActive = false;
    };
  }, []);

  return {
    summary,
    source,
    error,
    isLoading,
  };
};

export const __TESTS__ = {
  buildSummary,
};
