// src/services/audioService.ts
import TrackPlayer, {
  Event,
  State,
  Track,
  useTrackPlayerEvents,
} from 'react-native-track-player';
import { Song } from '../types/index';

/**
 * Audio Service - Wrapper around react-native-track-player
 * Handles all playback, queue management, and player state
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
      await TrackPlayer.setupPlayer();
      console.log('Audio player initialized');
    } catch (error) {
      console.error('Failed to initialize audio player:', error);
      throw error;
    }
  }

  /**
   * Add songs to the queue
   */
  async addToQueue(songs: Song[]): Promise<void> {
    const tracks: Track[] = songs.map((song) => ({
      url: song.url,
      title: song.title,
      artist: song.artist,
      album: song.album,
      artwork: song.artwork,
      duration: song.duration / 1000, // Convert ms to seconds
    }));

    try {
      await TrackPlayer.add(tracks);
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
      await TrackPlayer.skip(index);
      await TrackPlayer.play();
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
      await TrackPlayer.pause();
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
      await TrackPlayer.play();
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
      await TrackPlayer.skipToNext();
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
      await TrackPlayer.skipToPrevious();
    } catch (error) {
      console.error('Failed to skip to previous:', error);
      throw error;
    }
  }

  /**
   * Seek to position
   */
  async seek(position: number): Promise<void> {
    try {
      await TrackPlayer.seekTo(position);
    } catch (error) {
      console.error('Failed to seek:', error);
      throw error;
    }
  }

  /**
   * Set shuffle mode
   */
  async setShuffle(enabled: boolean): Promise<void> {
    try {
      // react-native-track-player v4+ has built-in shuffle support
      // This would be implemented based on the actual player API
      console.log('Shuffle:', enabled ? 'on' : 'off');
    } catch (error) {
      console.error('Failed to set shuffle:', error);
      throw error;
    }
  }

  /**
   * Clear the queue
   */
  async clearQueue(): Promise<void> {
    try {
      await TrackPlayer.reset();
    } catch (error) {
      console.error('Failed to clear queue:', error);
      throw error;
    }
  }

  /**
   * Get current state
   */
  async getState(): Promise<State> {
    try {
      return await TrackPlayer.getState();
    } catch (error) {
      console.error('Failed to get player state:', error);
      throw error;
    }
  }

  /**
   * Get current position
   */
  async getPosition(): Promise<number> {
    try {
      return await TrackPlayer.getPosition();
    } catch (error) {
      console.error('Failed to get position:', error);
      return 0;
    }
  }

  /**
   * Get current track duration
   */
  async getDuration(): Promise<number> {
    try {
      return await TrackPlayer.getDuration();
    } catch (error) {
      console.error('Failed to get duration:', error);
      return 0;
    }
  }
}

export const audioService = AudioService.getInstance();
