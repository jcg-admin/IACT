import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { MICROFRONTENDS_ANNOUNCEMENT } from '../constants/announcementFallback';

export const fetchAnnouncement = createAsyncThunk(
  'home/fetchAnnouncement',
  async (_, { rejectWithValue }) => {
    try {
      const response = await fetch('/api/announcements/latest');
      if (!response.ok) {
        throw new Error('Error cargando anuncios');
      }
      const data = await response.json();
      return data;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error cargando anuncios';
      return rejectWithValue({ announcement: MICROFRONTENDS_ANNOUNCEMENT, message });
    }
  }
);

const initialState = {
  announcement: null,
  isLoading: false,
  error: null,
  announcementSource: 'unknown',
};

const homeSlice = createSlice({
  name: 'home',
  initialState,
  reducers: {
    clearAnnouncement: (state) => {
      state.announcement = null;
      state.announcementSource = 'unknown';
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAnnouncement.pending, (state) => {
        state.isLoading = true;
        state.error = null;
        state.announcementSource = 'loading';
      })
      .addCase(fetchAnnouncement.fulfilled, (state, action) => {
        state.isLoading = false;
        state.announcement = action.payload;
        state.announcementSource = action.payload?.announcementSource || 'api';
      })
      .addCase(fetchAnnouncement.rejected, (state, action) => {
        state.isLoading = false;
        const fallbackAnnouncement = action.payload?.announcement;
        if (fallbackAnnouncement) {
          state.announcement = fallbackAnnouncement;
          state.announcementSource = 'fallback';
          state.error = action.payload?.message || action.error.message;
        } else {
          state.announcement = null;
          state.announcementSource = 'unknown';
          state.error = action.error.message;
        }
      });
  },
});

export const { clearAnnouncement } = homeSlice.actions;

export const selectAnnouncement = (state) => state.home.announcement;
export const selectIsLoading = (state) => state.home.isLoading;
export const selectError = (state) => state.home.error;
export const selectAnnouncementSource = (state) => state.home.announcementSource;

export default homeSlice.reducer;
