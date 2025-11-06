import { configureStore } from '@reduxjs/toolkit';
import appConfigReducer from './slices/appConfigSlice';
import homeReducer from '@modules/home/state/homeSlice';

export const store = configureStore({
  reducer: {
    appConfig: appConfigReducer,
    home: homeReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['appConfig/setConfig'],
        ignoredPaths: ['appConfig.config'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

export default store;
