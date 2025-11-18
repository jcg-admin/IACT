import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  status: 'unknown',
  isChecking: false,
  lastChecked: null,
  source: 'unknown',
  error: null,
};

const healthSlice = createSlice({
  name: 'observability',
  initialState,
  reducers: {
    setChecking: (state, action) => {
      state.isChecking = action.payload;
      if (action.payload) {
        state.error = null;
      }
    },
    setResult: (state, action) => {
      state.status = action.payload.status ?? 'unknown';
      state.lastChecked = action.payload.checkedAt ?? null;
      state.source = action.payload.source ?? 'unknown';
      state.error = action.payload.errorMessage ?? null;
      state.isChecking = false;
    },
    setError: (state, action) => {
      state.error = action.payload;
      state.isChecking = false;
    },
  },
});

export const { setChecking, setResult, setError } = healthSlice.actions;

export const selectHealthStatus = (state) => state.observability.status;
export const selectHealthSource = (state) => state.observability.source;
export const selectLastChecked = (state) => state.observability.lastChecked;
export const selectHealthError = (state) => state.observability.error;
export const selectIsCheckingHealth = (state) => state.observability.isChecking;

export default healthSlice.reducer;
