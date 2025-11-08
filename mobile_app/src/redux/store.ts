// src/redux/store.ts
import { configureStore } from '@reduxjs/toolkit';
import playerReducer from './slices/playerSlice';
import libraryReducer from './slices/librarySlice';
import settingsReducer from './slices/settingsSlice';

export const store = configureStore({
  reducer: {
    player: playerReducer,
    library: libraryReducer,
    settings: settingsReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
