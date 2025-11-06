import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isLoading: true,
  config: null,
  error: null,
};

const appConfigSlice = createSlice({
  name: 'appConfig',
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setConfig: (state, action) => {
      state.config = action.payload;
      state.isLoading = false;
      state.error = null;
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

export default appConfigSlice.reducer;
