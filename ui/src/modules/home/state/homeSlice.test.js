import reducer, {
  clearAnnouncement,
  fetchAnnouncement,
  selectAnnouncement,
  selectIsLoading,
  selectError,
} from './homeSlice';

describe('homeSlice', () => {
  it('sets loading state when fetch is pending', () => {
    const initial = reducer(undefined, { type: '@@INIT' });
    const state = reducer(initial, { type: fetchAnnouncement.pending.type });

    expect(state.isLoading).toBe(true);
    expect(state.error).toBeNull();
  });

  it('stores announcement on fulfilled', () => {
    const payload = 'Nuevo comunicado';
    const state = reducer(undefined, { type: fetchAnnouncement.fulfilled.type, payload });

    expect(state.isLoading).toBe(false);
    expect(state.announcement).toBe(payload);
  });

  it('stores error on rejected', () => {
    const error = { message: 'Fallo' };
    const state = reducer(undefined, { type: fetchAnnouncement.rejected.type, error });

    expect(state.isLoading).toBe(false);
    expect(state.error).toBe('Fallo');
  });

  it('clears announcement', () => {
    const initial = {
      announcement: 'Algo',
      isLoading: false,
      error: null,
    };
    const state = reducer(initial, clearAnnouncement());

    expect(state.announcement).toBeNull();
  });

  it('selectors expose slice data', () => {
    const rootState = {
      home: {
        announcement: 'Hola',
        isLoading: true,
        error: 'Error',
      },
    };

    expect(selectAnnouncement(rootState)).toBe('Hola');
    expect(selectIsLoading(rootState)).toBe(true);
    expect(selectError(rootState)).toBe('Error');
  });
});
