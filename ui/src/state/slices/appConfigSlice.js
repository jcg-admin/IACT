import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isLoading: true,
  config: null,
  error: null,
  source: 'unknown',
};

const appConfigSlice = createSlice({
  name: 'appConfig',
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.isLoading = action.payload;
      if (action.payload) {
        state.error = null;
      }
    },
    setConfig: (state, action) => {
      state.config = action.payload.config;
      state.source = action.payload.source;
      state.isLoading = false;
      state.error = action.payload.errorMessage ?? null;
    },
    setError: (state, action) => {
      state.error = action.payload;
      state.isLoading = false;
    },
  },
});

export const { setLoading, setConfig, setError } = appConfigSlice.actions;

export const selectAppConfig = (state) => state.appConfig.config;
export const selectIsLoading = (state) => state.appConfig.isLoading;
export const selectError = (state) => state.appConfig.error;
export const selectSource = (state) => state.appConfig.source;

export default appConfigSlice.reducer;
