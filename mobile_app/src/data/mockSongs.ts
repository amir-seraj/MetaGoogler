import { Song } from '../types';

export const mockSongs: Song[] = [
  {
    id: '1',
    title: 'Midnight Dreams',
    artist: 'Luna Echo',
    album: 'Nocturne',
    duration: 245,
    url: '/music/luna-echo-midnight-dreams.mp3',
    artwork: '🎵',
    metadataFetched: true,
  },
  {
    id: '2',
    title: 'Electric Vibes',
    artist: 'Neon Pulse',
    album: 'Synthwave',
    duration: 198,
    url: '/music/neon-pulse-electric-vibes.mp3',
    artwork: '⚡',
    metadataFetched: true,
  },
  {
    id: '3',
    title: 'Ocean Waves',
    artist: 'Coastal Breeze',
    album: 'Serenity',
    duration: 312,
    url: '/music/coastal-breeze-ocean-waves.mp3',
    artwork: '🌊',
    metadataFetched: true,
  },
  {
    id: '4',
    title: 'Mountain Echo',
    artist: 'Alpine Sound',
    album: 'Heights',
    duration: 267,
    url: '/music/alpine-sound-mountain-echo.mp3',
    artwork: '⛰️',
    metadataFetched: true,
  },
  {
    id: '5',
    title: 'Urban Jungle',
    artist: 'City Lights',
    album: 'Metropolis',
    duration: 223,
    url: '/music/city-lights-urban-jungle.mp3',
    artwork: '🏙️',
    metadataFetched: true,
  },
  {
    id: '6',
    title: 'Solar Flare',
    artist: 'Cosmic Ray',
    album: 'Universe',
    duration: 289,
    url: '/music/cosmic-ray-solar-flare.mp3',
    artwork: '☀️',
    metadataFetched: true,
  },
  {
    id: '7',
    title: 'Forest Whisper',
    artist: 'Nature Sounds',
    album: 'Green Earth',
    duration: 201,
    url: '/music/nature-sounds-forest-whisper.mp3',
    artwork: '🌲',
    metadataFetched: true,
  },
  {
    id: '8',
    title: 'Midnight Storm',
    artist: 'Thunder Road',
    album: 'Weather',
    duration: 276,
    url: '/music/thunder-road-midnight-storm.mp3',
    artwork: '⛈️',
    metadataFetched: true,
  },
];

export const mockArtists = Array.from(
  new Map(mockSongs.map(song => [song.artist, song])).values()
);

export const mockAlbums = Array.from(
  new Map(mockSongs.map(song => [song.album, song])).values()
);

export const mockGenres = ['Synthwave', 'Ambient', 'Electronic', 'Lo-Fi', 'Indie'];

export const mockPlaylists = [
  {
    id: '1',
    name: 'Favorites',
    description: 'My favorite tracks',
    songs: mockSongs.slice(0, 3).map(s => s.id),
  },
  {
    id: '2',
    name: 'Chill Vibes',
    description: 'Relaxing music for focus',
    songs: mockSongs.slice(2, 5).map(s => s.id),
  },
  {
    id: '3',
    name: 'Late Night',
    description: 'Music for late night coding',
    songs: mockSongs.slice(5, 8).map(s => s.id),
  },
];
