import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  selectAppConfig,
  selectIsLoading,
  selectError,
  setConfig,
  setError,
  setLoading,
} from '@state/slices/appConfigSlice';

export const useAppConfig = () => {
  const dispatch = useDispatch();
  const config = useSelector(selectAppConfig);
  const isLoading = useSelector(selectIsLoading);
  const error = useSelector(selectError);

  const loadConfig = useCallback(async () => {
    try {
      dispatch(setLoading(true));
      const response = await fetch('/api/config');

      if (!response.ok) {
        throw new Error('Error cargando configuracion');
      }

      const data = await response.json();
      dispatch(setConfig(data));
    } catch (err) {
      dispatch(setError(err.message));
    }
  }, [dispatch]);

  return {
    config,
    isLoading,
    error,
    loadConfig,
  };
};
