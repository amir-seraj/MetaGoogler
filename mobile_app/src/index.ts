// src/index.ts
/**
 * Main index file for convenient imports
 * Export all core app components, screens, services, and types
 */

// Types
export * from './types/index';

// Redux
export { useAppDispatch, useAppSelector } from './redux/hooks';
export { store } from './redux/store';
export {
  playTrack,
  pauseTrack,
  skipToNext,
  skipToPrevious,
  setShuffle,
  setRepeatMode,
  updatePosition,
  updateDuration,
  setQueue,
  setLoading as setPlayerLoading,
} from './redux/slices/playerSlice';
export {
  setSongs,
  setLoading as setLibraryLoading,
  setError,
} from './redux/slices/librarySlice';
export {
  setAIBackend,
  setAPIKey,
  setTheme,
  setEqualizerPreset,
} from './redux/slices/settingsSlice';

// Navigation
export { default as RootNavigator } from './navigation/RootNavigator';

// Screens
export { default as NowPlayingScreen } from './screens/NowPlayingScreen';
export { default as LibraryScreen } from './screens/LibraryScreen';
export { default as SettingsScreen } from './screens/SettingsScreen';
export { default as PlaylistsScreen } from './screens/PlaylistsScreen';

// Components
export { default as PlayerControls } from './components/PlayerControls';
export { default as AlbumArt } from './components/AlbumArt';
export { default as SongListItem } from './components/SongListItem';

// Services
export { audioService, AudioService } from './services/audioService';
export {
  auddService,
  AuddService,
  type AuddRecognitionResult,
} from './services/auddService';
export {
  metadataService,
  MetadataService,
  type MetadataGenerationRequest,
  type MetadataGenerationResult,
  type AIBackend,
} from './services/metadataService';
export { libraryService, LibraryService } from './services/libraryService';

// Main App
export { default as App } from './App';
