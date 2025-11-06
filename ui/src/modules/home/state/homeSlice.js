import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchAnnouncement = createAsyncThunk(
  'home/fetchAnnouncement',
  async () => {
    const response = await fetch('/api/announcements/latest');
    if (!response.ok) {
      throw new Error('Error cargando anuncios');
    }
    return response.json();
  }
);

const initialState = {
  announcement: null,
  isLoading: false,
  error: null,
};

const homeSlice = createSlice({
  name: 'home',
  initialState,
  reducers: {
    clearAnnouncement: (state) => {
      state.announcement = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAnnouncement.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAnnouncement.fulfilled, (state, action) => {
        state.isLoading = false;
        state.announcement = action.payload;
      })
      .addCase(fetchAnnouncement.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message;
      });
  },
});

export const { clearAnnouncement } = homeSlice.actions;

export const selectAnnouncement = (state) => state.home.announcement;
export const selectIsLoading = (state) => state.home.isLoading;
export const selectError = (state) => state.home.error;

export default homeSlice.reducer;
