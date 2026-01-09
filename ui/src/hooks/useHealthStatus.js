import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  selectHealthStatus,
  selectHealthSource,
  selectLastChecked,
  selectHealthError,
  selectIsCheckingHealth,
  setChecking,
  setResult,
  setError,
} from '@state/slices/healthSlice';
import { HealthService } from '@services/health/HealthService';

export const useHealthStatus = () => {
  const dispatch = useDispatch();
  const status = useSelector(selectHealthStatus);
  const source = useSelector(selectHealthSource);
  const lastChecked = useSelector(selectLastChecked);
  const error = useSelector(selectHealthError);
  const isChecking = useSelector(selectIsCheckingHealth);

  const checkHealth = useCallback(async () => {
    try {
      dispatch(setChecking(true));
      const result = await HealthService.getStatus();
      dispatch(
        setResult({
          status: result?.data?.status ?? 'unknown',
          checkedAt: result?.data?.checkedAt ?? null,
          source: result?.source ?? 'unknown',
          errorMessage: result?.error ? result.error.message : null,
        })
      );
    } catch (err) {
      dispatch(setError(err.message));
    }
  }, [dispatch]);

  return {
    status,
    source,
    lastChecked,
    error,
    isChecking,
    checkHealth,
  };
};
