// src/screens/NowPlayingScreen.tsx
import React, { useEffect } from 'react';
import { View, StyleSheet } from 'react-native';
import { Text, ProgressBar } from 'react-native-paper';
import { useAppSelector, useAppDispatch } from '../redux/hooks';
import PlayerControls from '../components/PlayerControls';
import AlbumArt from '../components/AlbumArt';

export default function NowPlayingScreen() {
  const dispatch = useAppDispatch();
  const { currentTrack, isPlaying, position, duration } = useAppSelector(
    (state) => state.player
  );

  const progress = duration ? position / duration : 0;

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!currentTrack) {
    return (
      <View style={styles.container}>
        <Text variant="headlineSmall">No track playing</Text>
        <Text variant="bodyMedium" style={styles.subtitle}>
          Add songs from your library to get started
        </Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <AlbumArt
        uri={currentTrack.artwork}
        title={currentTrack.title}
        artist={currentTrack.artist}
      />

      <View style={styles.infoContainer}>
        <Text variant="headlineSmall" numberOfLines={1}>
          {currentTrack.title}
        </Text>
        <Text variant="bodyMedium" style={styles.artist} numberOfLines={1}>
          {currentTrack.artist}
        </Text>
      </View>

      <View style={styles.progressContainer}>
        <ProgressBar
          progress={progress}
          style={styles.progressBar}
          color="#6200ea"
        />
        <View style={styles.timeContainer}>
          <Text variant="bodySmall">{formatTime(position)}</Text>
          <Text variant="bodySmall">{formatTime(duration)}</Text>
        </View>
      </View>

      <PlayerControls isPlaying={isPlaying} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
    paddingVertical: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  infoContainer: {
    marginVertical: 24,
    alignItems: 'center',
    width: '100%',
  },
  artist: {
    marginTop: 8,
    opacity: 0.7,
  },
  progressContainer: {
    width: '100%',
    marginVertical: 24,
  },
  progressBar: {
    height: 4,
    marginBottom: 8,
  },
  timeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  subtitle: {
    marginTop: 8,
    opacity: 0.6,
  },
});
