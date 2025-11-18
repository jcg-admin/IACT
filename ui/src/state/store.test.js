import store from './store';
import { setLoading } from './slices/appConfigSlice';

describe('store', () => {
  it('initializes reducers', () => {
    const state = store.getState();

    expect(state.appConfig).toBeDefined();
    expect(state.home).toBeDefined();
    expect(state.observability).toBeDefined();
  });

  it('dispatches actions without crashing', () => {
    store.dispatch(setLoading(false));
    expect(store.getState().appConfig.isLoading).toBe(false);
  });
});
