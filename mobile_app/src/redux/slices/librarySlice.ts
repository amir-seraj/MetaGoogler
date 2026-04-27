// src/redux/slices/librarySlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { LibraryState, Song } from '../../types/index';

const initialState: LibraryState = {
  allSongs: [],
  artists: [],
  albums: [],
  genres: [],
  loading: false,
  error: null,
};

const librarySlice = createSlice({
  name: 'library',
  initialState,
  reducers: {
    setSongs: (state, action: PayloadAction<Song[]>) => {
      state.allSongs = action.payload;
      state.artists = Array.from(new Set(action.payload.map((s) => s.artist)));
      state.albums = Array.from(
        new Set(action.payload.map((s) => s.album).filter((a): a is string => Boolean(a))),
      );
      state.genres = Array.from(
        new Set(action.payload.map((s) => s.genre).filter((g): g is string => Boolean(g))),
      );
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const { setSongs, setLoading, setError } = librarySlice.actions;

export default librarySlice.reducer;
