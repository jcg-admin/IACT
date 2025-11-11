import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  selectAppConfig,
  selectIsLoading,
  selectError,
  selectSource,
  setConfig,
  setError,
  setLoading,
} from '@state/slices/appConfigSlice';
import { AppConfigService } from '@services/config/AppConfigService';

export const useAppConfig = () => {
  const dispatch = useDispatch();
  const config = useSelector(selectAppConfig);
  const isLoading = useSelector(selectIsLoading);
  const error = useSelector(selectError);
  const source = useSelector(selectSource);

  const loadConfig = useCallback(async () => {
    try {
      dispatch(setLoading(true));
      const result = await AppConfigService.getConfig();
      dispatch(
        setConfig({
          config: result.data,
          source: result.source,
          errorMessage: result.error ? result.error.message : null,
        })
      );
    } catch (err) {
      dispatch(setError(err.message));
    }
  }, [dispatch]);

  return {
    config,
    isLoading,
    error,
    source,
    loadConfig,
  };
};
