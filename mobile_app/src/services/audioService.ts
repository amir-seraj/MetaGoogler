// src/services/audioService.ts
import { Audio, AVPlaybackStatus, InterruptionModeAndroid, InterruptionModeIOS } from 'expo-av';

export type PlaybackEvent =
  | { type: 'status'; positionMillis: number; durationMillis: number; isPlaying: boolean; isBuffering: boolean }
  | { type: 'finished' }
  | { type: 'error'; message: string };

type Listener = (event: PlaybackEvent) => void;

/**
 * Audio Service — wraps a single `expo-av` Audio.Sound instance.
 *
 * The service is intentionally dumb: queue/shuffle/repeat live in Redux.
 * Callers load one URL at a time and react to `finished` to advance.
 */
export class AudioService {
  private static instance: AudioService;
  private sound: Audio.Sound | null = null;
  private listeners = new Set<Listener>();
  private initialized = false;
  private currentUrl: string | null = null;

  private constructor() {}

  static getInstance(): AudioService {
    if (!AudioService.instance) {
      AudioService.instance = new AudioService();
    }
    return AudioService.instance;
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;
    await Audio.setAudioModeAsync({
      playsInSilentModeIOS: true,
      staysActiveInBackground: true,
      interruptionModeIOS: InterruptionModeIOS.DoNotMix,
      interruptionModeAndroid: InterruptionModeAndroid.DoNotMix,
      shouldDuckAndroid: true,
    });
    this.initialized = true;
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private emit(event: PlaybackEvent) {
    this.listeners.forEach((l) => l(event));
  }

  private handleStatus = (status: AVPlaybackStatus) => {
    if (!status.isLoaded) {
      if ('error' in status && status.error) {
        this.emit({ type: 'error', message: status.error });
      }
      return;
    }
    this.emit({
      type: 'status',
      positionMillis: status.positionMillis ?? 0,
      durationMillis: status.durationMillis ?? 0,
      isPlaying: status.isPlaying,
      isBuffering: status.isBuffering,
    });
    if (status.didJustFinish && !status.isLooping) {
      this.emit({ type: 'finished' });
    }
  };

  /** Load a new track and start playback. Replaces any currently loaded track. */
  async loadAndPlay(url: string): Promise<void> {
    await this.initialize();
    if (this.sound) {
      await this.sound.unloadAsync().catch(() => {});
      this.sound = null;
    }
    const { sound } = await Audio.Sound.createAsync(
      { uri: url },
      { shouldPlay: true, progressUpdateIntervalMillis: 500 },
      this.handleStatus,
    );
    this.sound = sound;
    this.currentUrl = url;
  }

  async play(): Promise<void> {
    if (!this.sound) return;
    await this.sound.playAsync();
  }

  async pause(): Promise<void> {
    if (!this.sound) return;
    await this.sound.pauseAsync();
  }

  async seekTo(positionMillis: number): Promise<void> {
    if (!this.sound) return;
    await this.sound.setPositionAsync(Math.max(0, Math.floor(positionMillis)));
  }

  async unload(): Promise<void> {
    if (!this.sound) return;
    await this.sound.unloadAsync().catch(() => {});
    this.sound = null;
    this.currentUrl = null;
  }

  getCurrentUrl(): string | null {
    return this.currentUrl;
  }
}

export const audioService = AudioService.getInstance();
