// src/components/SongListItem.tsx
import React from 'react';
import { View, StyleSheet, Image, TouchableOpacity } from 'react-native';
import { Text, IconButton } from 'react-native-paper';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { Song } from '../types/index';

interface SongListItemProps {
  song: Song;
  onPress: () => void;
}

export default function SongListItem({ song, onPress }: SongListItemProps) {
  return (
    <TouchableOpacity style={styles.container} onPress={onPress}>
      {song.artwork ? (
        <Image source={{ uri: song.artwork }} style={styles.thumbnail} />
      ) : (
        <View style={styles.thumbnailPlaceholder}>
          <MaterialCommunityIcons name="music" size={24} color="#999" />
        </View>
      )}

      <View style={styles.content}>
        <Text variant="bodyLarge" numberOfLines={1} style={styles.title}>
          {song.title}
        </Text>
        <Text variant="bodySmall" numberOfLines={1} style={styles.artist}>
          {song.artist}
        </Text>
        {song.album && (
          <Text variant="labelSmall" numberOfLines={1} style={styles.album}>
            {song.album}
          </Text>
        )}
      </View>

      <Text variant="labelSmall" style={styles.duration}>
        {formatDuration(song.duration)}
      </Text>

      <IconButton icon="play" size={20} onPress={onPress} />
    </TouchableOpacity>
  );
}

function formatDuration(ms: number): string {
  const seconds = Math.floor(ms / 1000);
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  thumbnail: {
    width: 48,
    height: 48,
    borderRadius: 4,
    marginRight: 12,
  },
  thumbnailPlaceholder: {
    width: 48,
    height: 48,
    borderRadius: 4,
    marginRight: 12,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    flex: 1,
  },
  title: {
    fontWeight: '600',
  },
  artist: {
    opacity: 0.7,
    marginTop: 2,
  },
  album: {
    opacity: 0.5,
    marginTop: 2,
  },
  duration: {
    marginRight: 8,
    opacity: 0.6,
  },
});
