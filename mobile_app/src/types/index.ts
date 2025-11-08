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
  aiBackend?: 'gemini' | 'claude' | 'gpt4' | 'ollama' | 'manual';
  aiSuggestions?: Record<string, any>;
  lastUpdated?: Date;
}

export interface Playlist {
  id: string;
  name: string;
  songIds: string[];
  createdAt: Date;
  updatedAt?: Date;
}

export interface PlayerState {
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

export interface LibraryState {
  allSongs: Song[];
  artists: string[];
  albums: string[];
  genres: string[];
  loading: boolean;
  error: string | null;
}

export interface SettingsState {
  selectedAIBackend: 'gemini' | 'claude' | 'gpt4' | 'ollama' | 'manual';
  apiKeys: Record<string, string>;
  theme: 'light' | 'dark' | 'auto';
  equalizerPreset?: string;
}
