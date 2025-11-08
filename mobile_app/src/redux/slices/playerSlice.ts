// src/redux/slices/playerSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { PlayerState, Song } from '../../types/index';

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
    },
    playTrack: (state) => {
      state.isPlaying = true;
    },
    pauseTrack: (state) => {
      state.isPlaying = false;
    },
    skipToNext: (state) => {
      if (state.queueIndex < state.queue.length - 1) {
        state.queueIndex += 1;
        state.currentTrackId = state.queue[state.queueIndex]?.id || null;
      }
    },
    skipToPrevious: (state) => {
      if (state.queueIndex > 0) {
        state.queueIndex -= 1;
        state.currentTrackId = state.queue[state.queueIndex]?.id || null;
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
