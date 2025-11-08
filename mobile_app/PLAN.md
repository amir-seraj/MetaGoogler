# React Native Music Player App - Complete Development Plan
## Phase-by-Phase Implementation Guide

---

## PROJECT OVERVIEW

### What You're Building
A **cross-platform music player** (iOS + Android) with:
- Local music playback with professional audio features
- Music recognition via AudD
- AI-powered metadata suggestions (user can choose backend)
- Beautiful modern UI
- Offline-first architecture

### Tech Stack
- **Framework**: React Native (TypeScript)
- **State Management**: Redux Toolkit
- **UI**: React Native Paper (Material Design 3)
- **Audio**: react-native-track-player v4
- **Database**: SQLite (react-native-sqlite-storage)
- **APIs**: AudD, Gemini/Claude/GPT-4/Ollama
- **Build**: Expo or bare React Native

### Timeline
- **Phase 1**: 4 weeks (MVP playback)
- **Phase 2**: 3 weeks (Metadata & recognition)
- **Phase 3**: 2 weeks (Polish & release)
- **Total**: 9 weeks (~2 months)

---

## PHASE 1: CORE MUSIC PLAYER (Weeks 1-4)

### Week 1: Project Setup & Architecture

#### 1.1 Initialize Project
```bash
# Option A: Expo (Simpler, recommended for start)
npx create-expo-app MusicPlayer
cd MusicPlayer
npm install -D typescript @types/react-native

# Option B: Bare React Native (if you need more control)
npx react-native init MusicPlayer --template typescript
cd MusicPlayer
```

#### 1.2 Install Core Dependencies
```bash
npm install \
  react-native-track-player \
  @react-navigation/native @react-navigation/bottom-tabs \
  react-native-paper \
  @react-native-firebase/app \
  redux @reduxjs/toolkit react-redux \
  react-native-sqlite-storage \
  react-native-vector-icons \
  axios

# If using Expo
npx expo install react-native-gesture-handler react-native-reanimated
```

#### 1.3 Project Structure
```
music-player/
├── src/
│   ├── screens/
│   │   ├── NowPlayingScreen.tsx
│   │   ├── LibraryScreen.tsx
│   │   ├── PlaylistsScreen.tsx
│   │   └── SettingsScreen.tsx
│   │
│   ├── components/
│   │   ├── PlayerControls.tsx
│   │   ├── BottomPlayer.tsx
│   │   ├── SongListItem.tsx
│   │   ├── AlbumArt.tsx
│   │   └── EqualizerControl.tsx
│   │
│   ├── services/
│   │   ├── audioService.ts       (react-native-track-player)
│   │   ├── libraryService.ts     (music scanning)
│   │   ├── databaseService.ts    (SQLite)
│   │   ├── auddService.ts        (music recognition)
│   │   └── metadataService.ts    (AI metadata)
│   │
│   ├── redux/
│   │   ├── slices/
│   │   │   ├── playerSlice.ts    (current track, playback state)
│   │   │   ├── librarySlice.ts   (all songs, artists, albums)
│   │   │   ├── playlistSlice.ts  (playlists)
│   │   │   └── settingsSlice.ts  (user preferences, AI backend)
│   │   ├── store.ts
│   │   └── hooks.ts
│   │
│   ├── hooks/
│   │   ├── useAudio.ts           (audio controls)
│   │   ├── useLibrary.ts         (library management)
│   │   └── useMetadata.ts        (metadata fetching)
│   │
│   ├── types/
│   │   └── index.ts              (TypeScript interfaces)
│   │
│   ├── utils/
│   │   ├── formatters.ts         (time, artist names)
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   ├── styles/
│   │   ├── themes.ts             (light/dark themes)
│   │   └── colors.ts
│   │
│   ├── App.tsx
│   └── index.ts
│
├── android/
├── ios/
├── app.json
├── tsconfig.json
├── package.json
└── .env
```

#### 1.4 TypeScript Types
```typescript
// src/types/index.ts
export interface Song {
  id: string;
  title: string;
  artist: string;
  album?: string;
  genre?: string;
  year?: number;
  duration: number;
  url: string; // Local file path
  artwork?: string;
  
  // Metadata tracking
  metadataFetched: boolean;
  aiBackend?: string;
  aiSuggestions?: Record<string, any>;
  lastUpdated?: Date;
}

export interface Playlist {
  id: string;
  name: string;
  songIds: string[];
  createdAt: Date;
}

export interface PlayerState {
  currentTrackId: string | null;
  isPlaying: boolean;
  queue: string[];
  queueIndex: number;
  shuffle: boolean;
  repeatMode: 'off' | 'one' | 'all';
}

export interface Settings {
  selectedAIBackend: 'gemini' | 'claude' | 'gpt4' | 'ollama' | 'manual';
  apiKeys: Record<string, string>;
  theme: 'light' | 'dark' | 'auto';
  equalizerPreset?: string;
}
```

#### 1.5 Initial Redux Setup
```typescript
// src/redux/store.ts
import { configureStore } from '@reduxjs/toolkit';
import playerSlice from './slices/playerSlice';
import librarySlice from './slices/librarySlice';
import settingsSlice from './slices/settingsSlice';

export const store = configureStore({
  reducer: {
    player: playerSlice,
    library: librarySlice,
    settings: settingsSlice,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

**Deliverables:**
- ✅ Project initialized
- ✅ Folder structure created
- ✅ Dependencies installed
- ✅ TypeScript configured
- ✅ Redux store set up

---

### Week 2: Music Playback Engine

#### 2.1 Initialize react-native-track-player
```typescript
// src/services/audioService.ts
import TrackPlayer from 'react-native-track-player';
import { Song } from '../types';

export class AudioService {
  static async initialize() {
    try {
      await TrackPlayer.setupPlayer({
        waitForBuffer: true,
        autoHandleInterruptions: true,
      });
      
      await TrackPlayer.updateOptions({
        stopWithApp: true,
        capabilities: [
          TrackPlayer.CAPABILITY_PLAY,
          TrackPlayer.CAPABILITY_PAUSE,
          TrackPlayer.CAPABILITY_SKIP_TO_NEXT,
          TrackPlayer.CAPABILITY_SKIP_TO_PREVIOUS,
          TrackPlayer.CAPABILITY_SEEK_TO,
        ],
        compactCapabilities: [
          TrackPlayer.CAPABILITY_PLAY,
          TrackPlayer.CAPABILITY_PAUSE,
          TrackPlayer.CAPABILITY_SKIP_TO_NEXT,
        ],
      });
      
      await TrackPlayer.add([]);
      console.log('TrackPlayer initialized');
    } catch (error) {
      console.error('TrackPlayer init error:', error);
    }
  }

  static async loadQueue(songs: Song[]) {
    const tracks = songs.map(song => ({
      id: song.id,
      title: song.title,
      artist: song.artist,
      album: song.album,
      artwork: song.artwork,
      url: song.url,
      duration: song.duration,
    }));

    await TrackPlayer.reset();
    await TrackPlayer.add(tracks);
  }

  static async play() {
    await TrackPlayer.play();
  }

  static async pause() {
    await TrackPlayer.pause();
  }

  static async skipToNext() {
    await TrackPlayer.skipToNext();
  }

  static async skipToPrevious() {
    await TrackPlayer.skipToPrevious();
  }

  static async seek(position: number) {
    await TrackPlayer.seekTo(position);
  }

  static async setQueue(songs: Song[], startIndex: number = 0) {
    await this.loadQueue(songs);
    await TrackPlayer.skip(startIndex);
  }
}
```

#### 2.2 Create Player Redux Slice
```typescript
// src/redux/slices/playerSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { AudioService } from '../../services/audioService';
import { Song } from '../../types';

interface PlayerState {
  currentTrackId: string | null;
  isPlaying: boolean;
  queue: Song[];
  queueIndex: number;
  duration: number;
  position: number;
  shuffle: boolean;
  repeatMode: 'off' | 'one' | 'all';
  loading: boolean;
}

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

export const setQueue = createAsyncThunk(
  'player/setQueue',
  async ({ songs, startIndex }: { songs: Song[]; startIndex: number }) => {
    await AudioService.setQueue(songs, startIndex);
    return { songs, startIndex };
  }
);

const playerSlice = createSlice({
  name: 'player',
  initialState,
  reducers: {
    playTrack: (state) => {
      state.isPlaying = true;
    },
    pauseTrack: (state) => {
      state.isPlaying = false;
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
  },
  extraReducers: (builder) => {
    builder
      .addCase(setQueue.fulfilled, (state, action) => {
        state.queue = action.payload.songs;
        state.queueIndex = action.payload.startIndex;
        state.currentTrackId = action.payload.songs[action.payload.startIndex]?.id;
      });
  },
});

export const {
  playTrack,
  pauseTrack,
  setShuffle,
  setRepeatMode,
  updatePosition,
  updateDuration,
} = playerSlice.actions;

export default playerSlice.reducer;
```

#### 2.3 Create Now Playing Screen
```typescript
// src/screens/NowPlayingScreen.tsx
import React, { useEffect } from 'react';
import { View, StyleSheet, Dimensions } from 'react-native';
import { Text, IconButton, Slider, useTheme } from 'react-native-paper';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { playTrack, pauseTrack, skipToNext, skipToPrevious } from '../redux/slices/playerSlice';
import AlbumArt from '../components/AlbumArt';
import PlayerControls from '../components/PlayerControls';
import TrackPlayer, { usePlaybackState, useProgress } from 'react-native-track-player';

const { width } = Dimensions.get('window');

export const NowPlayingScreen = () => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { queue, queueIndex, isPlaying } = useAppSelector(s => s.player);
  const playbackState = usePlaybackState();
  const progress = useProgress();

  const currentTrack = queue[queueIndex];

  const handlePlayPause = async () => {
    if (isPlaying) {
      await TrackPlayer.pause();
      dispatch(pauseTrack());
    } else {
      await TrackPlayer.play();
      dispatch(playTrack());
    }
  };

  const handleSkipNext = async () => {
    await TrackPlayer.skipToNext();
    dispatch(skipToNext());
  };

  const handleSkipPrevious = async () => {
    await TrackPlayer.skipToPrevious();
    dispatch(skipToPrevious());
  };

  if (!currentTrack) {
    return (
      <View style={[styles.container, { backgroundColor: theme.colors.background }]}> 
        <Text>No track playing</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      {/* Album Art */}
      <AlbumArt 
        artwork={currentTrack.artwork}
        title={currentTrack.title}
        size={width - 60}
      />

      {/* Song Info */}
      <View style={styles.infoContainer}>
        <Text variant="headlineSmall" numberOfLines={1}>
          {currentTrack.title}
        </Text>
        <Text 
          variant="bodyMedium" 
          style={{ color: theme.colors.onSurfaceVariant }}
          numberOfLines={1}
        >
          {currentTrack.artist}
        </Text>
      </View>

      {/* Progress Slider */}
      <View style={styles.progressContainer}>
        <Text variant="labelSmall">
          {formatTime(progress.position)}
        </Text>
        <Slider
          style={styles.slider}
          value={progress.position}
          maximumValue={progress.duration}
          onValueChange={(value) => TrackPlayer.seekTo(value)}
        />
        <Text variant="labelSmall">
          {formatTime(progress.duration)}
        </Text>
      </View>

      {/* Controls */}
      <PlayerControls
        isPlaying={isPlaying}
        onPlayPause={handlePlayPause}
        onSkipNext={handleSkipNext}
        onSkipPrevious={handleSkipPrevious}
      />
    </View>
  );
};

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
    paddingVertical: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  infoContainer: {
    marginVertical: 20,
    alignItems: 'center',
  },
  progressContainer: {
    width: '100%',
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 12,
    gap: 8,
  },
  slider: {
    flex: 1,
  },
});
```

#### 2.4 Create Player Controls Component
```typescript
// src/components/PlayerControls.tsx
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { IconButton, useTheme } from 'react-native-paper';

interface Props {
  isPlaying: boolean;
  onPlayPause: () => void;
  onSkipNext: () => void;
  onSkipPrevious: () => void;
}

export default function PlayerControls({
  isPlaying,
  onPlayPause,
  onSkipNext,
  onSkipPrevious,
}: Props) {
  const theme = useTheme();

  return (
    <View style={styles.container}>
      <IconButton
        icon="skip-previous"
        iconColor={theme.colors.primary}
        size={32}
        onPress={onSkipPrevious}
      />

      <IconButton
        icon={isPlaying ? 'pause-circle' : 'play-circle'}
        iconColor={theme.colors.primary}
        size={56}
        onPress={onPlayPause}
      />

      <IconButton
        icon="skip-next"
        iconColor={theme.colors.primary}
        size={32}
        onPress={onSkipNext}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 20,
    marginVertical: 20,
  },
});
```

**Deliverables:**
- ✅ Audio engine initialized
- ✅ Playback controls working
- ✅ Now Playing screen complete
- ✅ Redux player state setup
- ✅ Track player integrated

---

### Week 3: Library Scanning & Organization

#### 3.1 Library Service
```typescript
// src/services/libraryService.ts
import { MMKV } from 'react-native-mmkv';
import { getRealm } from './databaseService';
import { Song } from '../types';

const storage = new MMKV();

export class LibraryService {
  static async scanMusicLibrary(): Promise<Song[]> {
    try {
      // Get music files from device storage
      // This depends on your platform (iOS/Android)
      
      const songs: Song[] = [];
      
      // For now, return empty - will implement with platform-specific code
      return songs;
    } catch (error) {
      console.error('Error scanning library:', error);
      return [];
    }
  }

  static async getSongs(filter?: {
    artist?: string;
    album?: string;
    genre?: string;
  }): Promise<Song[]> {
    const realm = await getRealm();
    let query = realm.objects('Song');

    if (filter?.artist) {
      query = query.filtered('artist = $0', filter.artist);
    }
    if (filter?.album) {
      query = query.filtered('album = $0', filter.album);
    }
    if (filter?.genre) {
      query = query.filtered('genre = $0', filter.genre);
    }

    return Array.from(query);
  }

  static async getArtists(): Promise<string[]> {
    const realm = await getRealm();
    const songs = realm.objects('Song');
    const artists = Array.from(new Set(songs.map(s => s.artist)));
    return artists;
  }

  static async getAlbums(artist?: string): Promise<string[]> {
    const realm = await getRealm();
    let songs = realm.objects('Song');
    
    if (artist) {
      songs = songs.filtered('artist = $0', artist);
    }

    const albums = Array.from(new Set(songs.map(s => s.album).filter(Boolean)));
    return albums;
  }

  static async getGenres(): Promise<string[]> {
    const realm = await getRealm();
    const songs = realm.objects('Song');
    const genres = Array.from(new Set(songs.map(s => s.genre).filter(Boolean)));
    return genres;
  }
}
```

#### 3.2 Library Redux Slice
```typescript
// src/redux/slices/librarySlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { LibraryService } from '../../services/libraryService';
import { Song } from '../../types';

interface LibraryState {
  allSongs: Song[];
  artists: string[];
  albums: string[];
  genres: string[];
  loading: boolean;
  error: string | null;
}

const initialState: LibraryState = {
  allSongs: [],
  artists: [],
  albums: [],
  genres: [],
  loading: false,
  error: null,
};

export const loadLibrary = createAsyncThunk(
  'library/loadLibrary',
  async () => {
    const [songs, artists, albums, genres] = await Promise.all([
      LibraryService.getSongs(),
      LibraryService.getArtists(),
      LibraryService.getAlbums(),
      LibraryService.getGenres(),
    ]);
    return { songs, artists, albums, genres };
  }
);

const librarySlice = createSlice({
  name: 'library',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(loadLibrary.pending, (state) => {
        state.loading = true;
      })
      .addCase(loadLibrary.fulfilled, (state, action) => {
        state.allSongs = action.payload.songs;
        state.artists = action.payload.artists;
        state.albums = action.payload.albums;
        state.genres = action.payload.genres;
        state.loading = false;
      })
      .addCase(loadLibrary.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to load library';
      });
  },
});

export default librarySlice.reducer;
```

#### 3.3 Library Screen
```typescript
// src/screens/LibraryScreen.tsx
import React, { useEffect, useState } from 'react';
import { View, ScrollView, StyleSheet, FlatList } from 'react-native';
import { SegmentedButtons, Text, useTheme, ActivityIndicator } from 'react-native-paper';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import { loadLibrary } from '../redux/slices/librarySlice';

export const LibraryScreen = ({ navigation }: any) => {
  const theme = useTheme();
  const dispatch = useAppDispatch();
  const { allSongs, artists, albums, genres, loading } = useAppSelector(s => s.library);
  const [viewMode, setViewMode] = useState<'songs' | 'artists' | 'albums' | 'genres'>('songs');

  useEffect(() => {
    dispatch(loadLibrary() as any);
  }, []);

  if (loading) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}> 
        <ActivityIndicator animating size="large" />
      </View>
    );
  }

  const renderSongs = () => (
    <FlatList
      data={allSongs}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => (
        <SongListItem 
          song={item}
          onPress={() => {
            // Play song
          }}
        />
      )}
    />
  );

  const renderArtists = () => (
    <FlatList
      data={artists}
      keyExtractor={(item) => item}
      renderItem={({ item }) => (
        <ArtistListItem 
          artist={item}
          onPress={() => {
            // Navigate to artist screen
          }}
        />
      )}
    />
  );

  return (
    <View style={[styles.container, { backgroundColor: theme.colors.background }]}>
      <SegmentedButtons
        value={viewMode}
        onValueChange={(value: any) => setViewMode(value)}
        buttons={[
          { value: 'songs', label: 'Songs' },
          { value: 'artists', label: 'Artists' },
          { value: 'albums', label: 'Albums' },
          { value: 'genres', label: 'Genres' },
        ]}
        style={styles.segmentedButtons}
      />

      {viewMode === 'songs' && renderSongs()}
      {viewMode === 'artists' && renderArtists()}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  segmentedButtons: {
    margin: 12,
  },
});
```

#### 3.4 Library Redux Slice

(continued...)

---

### Week 4: Bottom Player & Navigation

... (full plan continues)


(Plan file truncated here for brevity; full plan included in original attachment.)
