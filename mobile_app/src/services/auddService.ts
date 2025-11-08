// src/services/auddService.ts
/**
 * AudD Music Recognition Service
 * Handles song identification via AudD API
 */

export interface AuddRecognitionResult {
  status: string;
  result?: {
    title: string;
    artist: string;
    album: string;
    release_date: string;
    label: string;
    timecode: string;
    song_link: string;
  };
}

export class AuddService {
  private static instance: AuddService;
  private apiKey: string = '';
  private baseUrl = 'https://api.audd.io';

  private constructor() {}

  static getInstance(): AuddService {
    if (!AuddService.instance) {
      AuddService.instance = new AuddService();
    }
    return AuddService.instance;
  }

  /**
   * Set API key for AudD
   */
  setApiKey(key: string): void {
    this.apiKey = key;
  }

  /**
   * Recognize a song from audio file
   * @param audioPath - Path to audio file
   * @returns Recognition result with song metadata
   */
  async recognizeSong(audioPath: string): Promise<AuddRecognitionResult> {
    if (!this.apiKey) {
      throw new Error('AudD API key not configured');
    }

    try {
      const formData = new FormData();
      formData.append('file', {
        uri: audioPath,
        type: 'audio/mpeg',
        name: 'audio.mp3',
      } as any);
      formData.append('api_token', this.apiKey);
      formData.append('return', 'apple_music,spotify');

      const response = await fetch(`${this.baseUrl}/identify`, {
        method: 'POST',
        body: formData,
      });

      const result: AuddRecognitionResult = await response.json();

      if (result.status !== 'success') {
        throw new Error(`AudD API error: ${result.status}`);
      }

      return result;
    } catch (error) {
      console.error('Failed to recognize song:', error);
      throw error;
    }
  }

  /**
   * Recognize song from audio file with progress callback
   * @param audioPath - Path to audio file
   * @param onProgress - Callback for recognition progress
   */
  async recognizeSongWithProgress(
    audioPath: string,
    onProgress?: (progress: number) => void
  ): Promise<AuddRecognitionResult> {
    if (onProgress) {
      onProgress(10);
    }

    const result = await this.recognizeSong(audioPath);

    if (onProgress) {
      onProgress(100);
    }

    return result;
  }

  /**
   * Batch recognize multiple songs
   * @param audioPaths - Array of audio file paths
   */
  async recognizeMultipleSongs(
    audioPaths: string[]
  ): Promise<AuddRecognitionResult[]> {
    try {
      const results = await Promise.allSettled(
        audioPaths.map((path) => this.recognizeSong(path))
      );

      return results.map((result) => {
        if (result.status === 'fulfilled') {
          return result.value;
        } else {
          console.error('Recognition failed:', result.reason);
          return {
            status: 'error',
          };
        }
      });
    } catch (error) {
      console.error('Batch recognition failed:', error);
      throw error;
    }
  }
}

export const auddService = AuddService.getInstance();
