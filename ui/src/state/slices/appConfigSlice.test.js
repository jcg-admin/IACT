import reducer, {
  setLoading,
  setConfig,
  setError,
  selectAppConfig,
  selectIsLoading,
  selectError,
  selectSource,
} from './appConfigSlice';

describe('appConfigSlice', () => {
  it('handles loading state and resets error', () => {
    const initialState = {
      isLoading: false,
      config: null,
      error: 'Fallo previo',
      source: 'mock',
    };

    const state = reducer(initialState, setLoading(true));

    expect(state.isLoading).toBe(true);
    expect(state.error).toBeNull();
  });

  it('stores configuration payload with metadata', () => {
    const state = reducer(undefined, setConfig({
      config: { foo: 'bar' },
      source: 'mock',
      errorMessage: 'Fallback',
    }));

    expect(state.config).toEqual({ foo: 'bar' });
    expect(state.source).toBe('mock');
    expect(state.error).toBe('Fallback');
    expect(state.isLoading).toBe(false);
  });

  it('stores errors when setError is dispatched', () => {
    const state = reducer(undefined, setError('Error grave'));

    expect(state.error).toBe('Error grave');
    expect(state.isLoading).toBe(false);
  });

  it('selectors extract data correctly', () => {
    const state = {
      appConfig: {
        config: { foo: 'bar' },
        isLoading: false,
        error: null,
        source: 'api',
      },
    };

    expect(selectAppConfig(state)).toEqual({ foo: 'bar' });
    expect(selectIsLoading(state)).toBe(false);
    expect(selectError(state)).toBeNull();
    expect(selectSource(state)).toBe('api');
  });
});
