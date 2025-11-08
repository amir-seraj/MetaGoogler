// src/screens/PlaylistsScreen.tsx
import React from 'react';
import { View, StyleSheet, FlatList } from 'react-native';
import { Text, FAB } from 'react-native-paper';

export default function PlaylistsScreen() {
  const [playlists, setPlaylists] = React.useState<Array<{ id: string; name: string; songCount: number }>>([]);

  return (
    <View style={styles.container}>
      {playlists.length === 0 ? (
        <View style={styles.emptyContainer}>
          <Text variant="headlineSmall">No playlists yet</Text>
          <Text variant="bodyMedium" style={styles.emptyText}>
            Create a playlist to organize your favorite songs
          </Text>
        </View>
      ) : (
        <FlatList
          data={playlists}
          keyExtractor={(item) => item.id}
          renderItem={({ item }) => (
            <View style={styles.playlistItem}>
              <Text variant="bodyLarge">{item.name}</Text>
              <Text variant="bodySmall">{item.songCount} songs</Text>
            </View>
          )}
        />
      )}

      <FAB
        icon="plus"
        label="New Playlist"
        onPress={() => {
          // TODO: Show dialog to create playlist
        }}
        style={styles.fab}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 16,
  },
  emptyText: {
    marginTop: 8,
    opacity: 0.6,
    textAlign: 'center',
  },
  playlistItem: {
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  fab: {
    position: 'absolute',
    margin: 16,
    right: 0,
    bottom: 0,
  },
});
