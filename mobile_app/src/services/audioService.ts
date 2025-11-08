// src/services/audioService.ts
import { Song } from '../types/index';

// Stub types for now - will be replaced with react-native-track-player when integrated
enum State {
  None = 0,
  Playing = 1,
  Paused = 2,
}

interface Track {
  url: string;
  title: string;
  artist?: string;
  album?: string;
  artwork?: string;
  duration?: number;
}

/**
 * Audio Service - Wrapper around audio playback
 * Handles all playback, queue management, and player state
 * Note: Native audio playback (react-native-track-player) will be integrated in Phase 2
 */

export class AudioService {
  private static instance: AudioService;

  private constructor() {}

  static getInstance(): AudioService {
    if (!AudioService.instance) {
      AudioService.instance = new AudioService();
    }
    return AudioService.instance;
  }

  /**
   * Initialize the audio player
   */
  async initialize(): Promise<void> {
    try {
      console.log('Audio player initialized (stub - Phase 2 integration)');
      // Will be implemented with react-native-track-player in Phase 2
    } catch (error) {
      console.error('Failed to initialize audio player:', error);
      throw error;
    }
  }

  /**
   * Add songs to the queue
   */
  async addToQueue(songs: Song[]): Promise<void> {
    try {
      console.log(`Added ${songs.length} songs to queue (stub)`);
      // Will be implemented with react-native-track-player in Phase 2
    } catch (error) {
      console.error('Failed to add songs to queue:', error);
      throw error;
    }
  }

  /**
   * Play a specific track
   */
  async play(index: number): Promise<void> {
    try {
      console.log(`Playing track at index ${index} (stub)`);
      // Will be implemented with react-native-track-player in Phase 2
    } catch (error) {
      console.error('Failed to play track:', error);
      throw error;
    }
  }

  /**
   * Pause playback
   */
  async pause(): Promise<void> {
    try {
      console.log('Pausing playback (stub)');
      // Will be implemented with react-native-track-player in Phase 2
    } catch (error) {
      console.error('Failed to pause:', error);
      throw error;
    }
  }

  /**
   * Resume playback
   */
  async resume(): Promise<void> {
    try {
      console.log('Resuming playback (stub)');
      // Will be implemented with react-native-track-player in Phase 2
    } catch (error) {
      console.error('Failed to resume:', error);
      throw error;
    }
  }

  /**
   * Skip to next track
   */
  async skipToNext(): Promise<void> {
    try {
      console.log('Skipping to next track (stub)');
      // Will be implemented with react-native-track-player in Phase 2
    } catch (error) {
      console.error('Failed to skip to next:', error);
      throw error;
    }
  }

  /**
   * Skip to previous track
   */
  async skipToPrevious(): Promise<void> {
    try {
      console.log('Skipping to previous track (stub)');
      // Will be implemented with react-native-track-player in Phase 2
    } catch (error) {
      console.error('Failed to skip to previous:', error);
      throw error;
    }
  }

  /**
   * Seek to position (in seconds)
   */
  async seek(position: number): Promise<void> {
    try {
      console.log(`Seeking to ${position}s (stub)`);
      // Will be implemented with react-native-track-player in Phase 2
    } catch (error) {
      console.error('Failed to seek:', error);
      throw error;
    }
  }

  /**
   * Reset the queue
   */
  async reset(): Promise<void> {
    try {
      console.log('Resetting queue (stub)');
      // Will be implemented with react-native-track-player in Phase 2
    } catch (error) {
      console.error('Failed to reset queue:', error);
      throw error;
    }
  }

  /**
   * Get current state
   */
  async getState(): Promise<State> {
    try {
      return State.Paused; // Stub implementation
    } catch (error) {
      console.error('Failed to get player state:', error);
      throw error;
    }
  }

  /**
   * Get current position (in seconds)
   */
  async getPosition(): Promise<number> {
    try {
      return 0; // Stub implementation
    } catch (error) {
      console.error('Failed to get position:', error);
      return 0;
    }
  }

  /**
   * Get current track duration (in seconds)
   */
  async getDuration(): Promise<number> {
    try {
      return 0; // Stub implementation
    } catch (error) {
      console.error('Failed to get duration:', error);
      return 0;
    }
  }
}

export const audioService = AudioService.getInstance();
