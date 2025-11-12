import reducer, {
  clearAnnouncement,
  fetchAnnouncement,
  selectAnnouncement,
  selectIsLoading,
  selectError,
  selectAnnouncementSource,
} from './homeSlice';
import { MICROFRONTENDS_ANNOUNCEMENT } from '../constants/announcementFallback';

describe('homeSlice', () => {
  it('sets loading state when fetch is pending', () => {
    const initial = reducer(undefined, { type: '@@INIT' });
    const state = reducer(initial, { type: fetchAnnouncement.pending.type });

    expect(state.isLoading).toBe(true);
    expect(state.error).toBeNull();
  });

  it('stores announcement on fulfilled', () => {
    const payload = { title: 'Nuevo comunicado', videoPlatforms: [] };
    const state = reducer(undefined, { type: fetchAnnouncement.fulfilled.type, payload });

    expect(state.isLoading).toBe(false);
    expect(state.announcement).toBe(payload);
  });

  it('stores fallback announcement and error on rejected', () => {
    const action = {
      type: fetchAnnouncement.rejected.type,
      error: { message: 'Fallo' },
      payload: { announcement: MICROFRONTENDS_ANNOUNCEMENT, message: 'Fallo controlado' },
    };
    const state = reducer(undefined, action);

    expect(state.isLoading).toBe(false);
    expect(state.error).toBe('Fallo controlado');
    expect(state.announcement).toBe(MICROFRONTENDS_ANNOUNCEMENT);
    expect(state.announcementSource).toBe('fallback');
  });

  it('clears announcement', () => {
    const initial = {
      announcement: 'Algo',
      isLoading: false,
      error: null,
    };
    const state = reducer(initial, clearAnnouncement());

    expect(state.announcement).toBeNull();
    expect(state.announcementSource).toBe('unknown');
  });

  it('selectors expose slice data', () => {
    const rootState = {
      home: {
        announcement: 'Hola',
        isLoading: true,
        error: 'Error',
        announcementSource: 'fallback',
      },
    };

    expect(selectAnnouncement(rootState)).toBe('Hola');
    expect(selectIsLoading(rootState)).toBe(true);
    expect(selectError(rootState)).toBe('Error');
    expect(selectAnnouncementSource(rootState)).toBe('fallback');
  });
});
