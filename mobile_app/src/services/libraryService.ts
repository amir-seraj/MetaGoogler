// src/services/libraryService.ts
import { Song, Playlist } from '../types/index';

/**
 * Library Service - File scanning and library management
 * Handles scanning device storage for music files
 */

export class LibraryService {
  private static instance: LibraryService;

  private constructor() {}

  static getInstance(): LibraryService {
    if (!LibraryService.instance) {
      LibraryService.instance = new LibraryService();
    }
    return LibraryService.instance;
  }

  /**
   * Scan device storage for music files
   * This is a placeholder implementation - actual implementation
   * would use react-native-document-picker or similar
   */
  async scanMusicLibrary(): Promise<Song[]> {
    try {
      console.log('Scanning music library...');
      // TODO: Implement actual file scanning
      // Would use:
      // - react-native-document-picker
      // - react-native-fs
      // - MMKV for caching
      // - Metadata extraction from audio files

      // Return empty array for now
      return [];
    } catch (error) {
      console.error('Failed to scan music library:', error);
      throw error;
    }
  }

  /**
   * Get all songs from library
   */
  async getAllSongs(): Promise<Song[]> {
    try {
      // TODO: Fetch from local database
      return [];
    } catch (error) {
      console.error('Failed to get songs:', error);
      throw error;
    }
  }

  /**
   * Search songs by title, artist, or album
   */
  searchSongs(query: string, songs: Song[]): Song[] {
    const lowercaseQuery = query.toLowerCase();
    return songs.filter(
      (song) =>
        song.title.toLowerCase().includes(lowercaseQuery) ||
        song.artist.toLowerCase().includes(lowercaseQuery) ||
        song.album?.toLowerCase().includes(lowercaseQuery)
    );
  }

  /**
   * Get unique artists from songs
   */
  getArtists(songs: Song[]): { name: string; songCount: number }[] {
    const artistMap = new Map<string, number>();

    songs.forEach((song) => {
      const count = artistMap.get(song.artist) || 0;
      artistMap.set(song.artist, count + 1);
    });

    return Array.from(artistMap.entries()).map(([name, songCount]) => ({
      name,
      songCount,
    }));
  }

  /**
   * Get unique albums from songs
   */
  getAlbums(songs: Song[]): { name: string; artist: string; songCount: number }[] {
    const albumMap = new Map<string, { artist: string; count: number }>();

    songs.forEach((song) => {
      const albumName = song.album || 'Unknown Album';
      const existing = albumMap.get(albumName);
      if (existing) {
        existing.count += 1;
      } else {
        albumMap.set(albumName, {
          artist: song.artist,
          count: 1,
        });
      }
    });

    return Array.from(albumMap.entries()).map(([name, { artist, count }]) => ({
      name,
      artist,
      songCount: count,
    }));
  }

  /**
   * Get unique genres from songs
   */
  getGenres(songs: Song[]): { name: string; songCount: number }[] {
    const genreMap = new Map<string, number>();

    songs.forEach((song) => {
      const genre = song.genre || 'Unknown';
      const count = genreMap.get(genre) || 0;
      genreMap.set(genre, count + 1);
    });

    return Array.from(genreMap.entries()).map(([name, songCount]) => ({
      name,
      songCount,
    }));
  }

  /**
   * Get songs by artist
   */
  getSongsByArtist(artist: string, songs: Song[]): Song[] {
    return songs.filter((song) => song.artist === artist);
  }

  /**
   * Get songs by album
   */
  getSongsByAlbum(album: string, songs: Song[]): Song[] {
    return songs.filter((song) => song.album === album);
  }

  /**
   * Get songs by genre
   */
  getSongsByGenre(genre: string, songs: Song[]): Song[] {
    return songs.filter((song) => song.genre === genre);
  }

  /**
   * Create a new playlist
   */
  async createPlaylist(name: string, songIds: string[]): Promise<Playlist> {
    const id = Math.random().toString(36).substring(7);
    return {
      id,
      name,
      songIds,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
  }

  /**
   * Add songs to playlist
   */
  async addToPlaylist(playlistId: string, songIds: string[]): Promise<void> {
    try {
      // TODO: Update playlist in database
      console.log(`Added ${songIds.length} songs to playlist ${playlistId}`);
    } catch (error) {
      console.error('Failed to add songs to playlist:', error);
      throw error;
    }
  }

  /**
   * Remove songs from playlist
   */
  async removeFromPlaylist(playlistId: string, songIds: string[]): Promise<void> {
    try {
      // TODO: Update playlist in database
      console.log(`Removed ${songIds.length} songs from playlist ${playlistId}`);
    } catch (error) {
      console.error('Failed to remove songs from playlist:', error);
      throw error;
    }
  }

  /**
   * Delete playlist
   */
  async deletePlaylist(playlistId: string): Promise<void> {
    try {
      // TODO: Delete from database
      console.log(`Deleted playlist ${playlistId}`);
    } catch (error) {
      console.error('Failed to delete playlist:', error);
      throw error;
    }
  }
}

export const libraryService = LibraryService.getInstance();
