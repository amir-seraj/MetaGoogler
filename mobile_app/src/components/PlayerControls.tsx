// src/components/PlayerControls.tsx
import React from 'react';
import { View, StyleSheet } from 'react-native';
import { IconButton } from 'react-native-paper';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import {
  playTrack,
  pauseTrack,
  skipToNext,
  skipToPrevious,
  setShuffle,
  setRepeatMode,
} from '../redux/slices/playerSlice';

interface PlayerControlsProps {
  isPlaying: boolean;
}

export default function PlayerControls({ isPlaying }: PlayerControlsProps) {
  const dispatch = useAppDispatch();
  const { shuffle, repeatMode, queue } = useAppSelector((state) => state.player);

  const handlePlayPause = () => {
    if (isPlaying) {
      dispatch(pauseTrack());
    } else {
      const firstTrack = queue[0];
      if (firstTrack) {
        dispatch(playTrack(firstTrack));
      }
    }
  };

  const handleRepeatMode = () => {
    const modes = ['off', 'one', 'all'] as const;
    const currentIndex = modes.indexOf(repeatMode);
    const nextMode = modes[(currentIndex + 1) % modes.length];
    dispatch(setRepeatMode(nextMode));
  };

  return (
    <View style={styles.container}>
      <IconButton
        icon={shuffle ? 'shuffle' : 'shuffle-disabled'}
        iconColor={shuffle ? '#6200ea' : '#999'}
        size={24}
        onPress={() => dispatch(setShuffle(!shuffle))}
      />

      <IconButton
        icon="skip-previous"
        iconColor="#333"
        size={28}
        onPress={() => dispatch(skipToPrevious())}
      />

      <IconButton
        icon={isPlaying ? 'pause-circle' : 'play-circle'}
        iconColor="#6200ea"
        size={48}
        onPress={handlePlayPause}
      />

      <IconButton
        icon="skip-next"
        iconColor="#333"
        size={28}
        onPress={() => dispatch(skipToNext())}
      />

      <IconButton
        icon={
          repeatMode === 'off'
            ? 'repeat-off'
            : repeatMode === 'one'
              ? 'repeat-once'
              : 'repeat'
        }
        iconColor={repeatMode === 'off' ? '#999' : '#6200ea'}
        size={24}
        onPress={handleRepeatMode}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginVertical: 16,
    gap: 8,
  },
});
