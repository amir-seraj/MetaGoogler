// src/screens/LibraryScreen.tsx
import React, { useState } from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Button, Text, Searchbar } from 'react-native-paper';
import { useAppSelector, useAppDispatch } from '../redux/hooks';
import SongListItem from '../components/SongListItem';
import { playTrack } from '../redux/slices/playerSlice';

type ViewMode = 'songs' | 'artists' | 'albums' | 'genres';

export default function LibraryScreen() {
  const [viewMode, setViewMode] = useState<ViewMode>('songs');
  const [searchQuery, setSearchQuery] = useState('');
  const { songs } = useAppSelector((state) => state.library);
  const dispatch = useAppDispatch();

  const filteredSongs = songs.filter(
    (song) =>
      song.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      song.artist.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getArtists = () => {
    const artists = new Map<string, number>();
    songs.forEach((song) => {
      artists.set(song.artist, (artists.get(song.artist) || 0) + 1);
    });
    return Array.from(artists.entries()).map(([name, count]) => ({
      name,
      count,
    }));
  };

  const getAlbums = () => {
    const albums = new Map<string, number>();
    songs.forEach((song) => {
      albums.set(song.album || 'Unknown', (albums.get(song.album || 'Unknown') || 0) + 1);
    });
    return Array.from(albums.entries()).map(([name, count]) => ({
      name,
      count,
    }));
  };

  const getGenres = () => {
    const genres = new Map<string, number>();
    songs.forEach((song) => {
      genres.set(song.genre || 'Unknown', (genres.get(song.genre || 'Unknown') || 0) + 1);
    });
    return Array.from(genres.entries()).map(([name, count]) => ({
      name,
      count,
    }));
  };

  const renderContent = () => {
    switch (viewMode) {
      case 'songs':
        return (
          <FlatList
            data={filteredSongs}
            keyExtractor={(item) => item.id}
            renderItem={({ item }) => (
              <SongListItem
                song={item}
                onPress={() => dispatch(playTrack(item))}
              />
            )}
            ListEmptyComponent={
              <View style={styles.emptyContainer}>
                <Text variant="bodyMedium">No songs found</Text>
              </View>
            }
          />
        );
      case 'artists':
        return (
          <FlatList
            data={getArtists().filter((a) =>
              a.name.toLowerCase().includes(searchQuery.toLowerCase())
            )}
            keyExtractor={(item) => item.name}
            renderItem={({ item }) => (
              <View style={styles.listItem}>
                <Text variant="bodyLarge">{item.name}</Text>
                <Text variant="bodySmall">{item.count} songs</Text>
              </View>
            )}
          />
        );
      case 'albums':
        return (
          <FlatList
            data={getAlbums().filter((a) =>
              a.name.toLowerCase().includes(searchQuery.toLowerCase())
            )}
            keyExtractor={(item) => item.name}
            renderItem={({ item }) => (
              <View style={styles.listItem}>
                <Text variant="bodyLarge">{item.name}</Text>
                <Text variant="bodySmall">{item.count} songs</Text>
              </View>
            )}
          />
        );
      case 'genres':
        return (
          <FlatList
            data={getGenres().filter((g) =>
              g.name.toLowerCase().includes(searchQuery.toLowerCase())
            )}
            keyExtractor={(item) => item.name}
            renderItem={({ item }) => (
              <View style={styles.listItem}>
                <Text variant="bodyLarge">{item.name}</Text>
                <Text variant="bodySmall">{item.count} songs</Text>
              </View>
            )}
          />
        );
    }
  };

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Search songs..."
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      <View style={styles.viewModeButtons}>
        {(['songs', 'artists', 'albums', 'genres'] as const).map((mode) => (
          <Button
            key={mode}
            mode={viewMode === mode ? 'contained' : 'outlined'}
            onPress={() => setViewMode(mode)}
            style={styles.modeButton}
          >
            {mode.charAt(0).toUpperCase() + mode.slice(1)}
          </Button>
        ))}
      </View>

      {renderContent()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 12,
    paddingVertical: 12,
  },
  searchbar: {
    marginBottom: 12,
  },
  viewModeButtons: {
    flexDirection: 'row',
    marginBottom: 12,
    gap: 8,
  },
  modeButton: {
    flex: 1,
  },
  listItem: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
