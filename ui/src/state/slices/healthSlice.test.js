import reducer, {
  setChecking,
  setResult,
  setError,
  selectHealthStatus,
  selectHealthSource,
  selectLastChecked,
  selectHealthError,
} from './healthSlice';

describe('healthSlice', () => {
  it('provides initial state', () => {
    const state = reducer(undefined, { type: '@@INIT' });

    expect(state).toEqual({
      status: 'unknown',
      isChecking: false,
      lastChecked: null,
      source: 'unknown',
      error: null,
    });
  });

  it('sets loading state', () => {
    const state = reducer(undefined, setChecking(true));

    expect(state.isChecking).toBe(true);
    expect(state.error).toBeNull();
  });

  it('stores health result and metadata', () => {
    const result = {
      status: 'ok',
      checkedAt: '2025-11-14T12:00:00Z',
      source: 'api',
      errorMessage: null,
    };

    const state = reducer(undefined, setResult(result));

    expect(state.status).toBe('ok');
    expect(state.lastChecked).toBe(result.checkedAt);
    expect(state.source).toBe('api');
    expect(state.error).toBeNull();
  });

  it('stores error state', () => {
    const state = reducer(undefined, setError('fallo backend'));

    expect(state.error).toBe('fallo backend');
    expect(state.isChecking).toBe(false);
  });

  it('exposes selectors', () => {
    const state = {
      observability: {
        status: 'degraded',
        isChecking: false,
        lastChecked: '2025-11-14T00:00:00Z',
        source: 'mock',
        error: null,
      },
    };

    expect(selectHealthStatus(state)).toBe('degraded');
    expect(selectHealthSource(state)).toBe('mock');
    expect(selectLastChecked(state)).toBe('2025-11-14T00:00:00Z');
    expect(selectHealthError(state)).toBeNull();
  });
});
