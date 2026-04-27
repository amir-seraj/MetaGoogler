// src/redux/slices/playerSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { PlayerState, Song } from '../../types/index';
import type { RootState } from '../store';

const initialState: PlayerState = {
  currentTrackId: null,
  isPlaying: false,
  queue: [],
  queueIndex: 0,
  duration: 0,
  position: 0,
  shuffle: false,
  repeatMode: 'off',
  loading: false,
};

const playerSlice = createSlice({
  name: 'player',
  initialState,
  reducers: {
    setQueue: (state, action: PayloadAction<{ songs: Song[]; startIndex?: number }>) => {
      state.queue = action.payload.songs;
      state.queueIndex = action.payload.startIndex || 0;
      state.currentTrackId = state.queue[state.queueIndex]?.id || null;
      state.position = 0;
      state.duration = 0;
    },
    playTrack: (state, action: PayloadAction<string | undefined>) => {
      if (action.payload) {
        const idx = state.queue.findIndex((s) => s.id === action.payload);
        if (idx >= 0) {
          state.queueIndex = idx;
          state.currentTrackId = action.payload;
        }
      }
      state.isPlaying = true;
    },
    pauseTrack: (state) => {
      state.isPlaying = false;
    },
    skipToNext: (state) => {
      if (state.repeatMode === 'one') {
        state.position = 0;
        return;
      }
      if (state.queueIndex < state.queue.length - 1) {
        state.queueIndex += 1;
      } else if (state.repeatMode === 'all' && state.queue.length > 0) {
        state.queueIndex = 0;
      } else {
        state.isPlaying = false;
        return;
      }
      state.currentTrackId = state.queue[state.queueIndex]?.id || null;
      state.position = 0;
      state.isPlaying = true;
    },
    skipToPrevious: (state) => {
      if (state.position > 3000) {
        state.position = 0;
        return;
      }
      if (state.queueIndex > 0) {
        state.queueIndex -= 1;
        state.currentTrackId = state.queue[state.queueIndex]?.id || null;
        state.position = 0;
      }
    },
    setShuffle: (state, action: PayloadAction<boolean>) => {
      state.shuffle = action.payload;
    },
    setRepeatMode: (state, action: PayloadAction<'off' | 'one' | 'all'>) => {
      state.repeatMode = action.payload;
    },
    updatePosition: (state, action: PayloadAction<number>) => {
      state.position = action.payload;
    },
    updateDuration: (state, action: PayloadAction<number>) => {
      state.duration = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
});

export const selectCurrentTrack = (state: RootState): Song | null => {
  const { currentTrackId, queue } = state.player;
  if (!currentTrackId) return null;
  return queue.find((s) => s.id === currentTrackId) ?? null;
};

export const {
  setQueue,
  playTrack,
  pauseTrack,
  skipToNext,
  skipToPrevious,
  setShuffle,
  setRepeatMode,
  updatePosition,
  updateDuration,
  setLoading,
} = playerSlice.actions;

export default playerSlice.reducer;
