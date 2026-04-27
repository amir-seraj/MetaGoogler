// src/services/usePlayerBridge.ts
import { useEffect, useRef } from 'react';
import { useAppDispatch, useAppSelector } from '../redux/hooks';
import {
  pauseTrack,
  skipToNext,
  updateDuration,
  updatePosition,
} from '../redux/slices/playerSlice';
import { audioService } from './audioService';

/**
 * Bridges Redux player state to the native `expo-av` audio service.
 *
 * - When `currentTrackId` changes, loads the new track URL.
 * - When `isPlaying` changes, calls play/pause on the loaded sound.
 * - Forwards position/duration updates back to Redux.
 * - On track end, dispatches `skipToNext` (which respects repeatMode).
 */
export function usePlayerBridge() {
  const dispatch = useAppDispatch();
  const currentTrackId = useAppSelector((s) => s.player.currentTrackId);
  const isPlaying = useAppSelector((s) => s.player.isPlaying);
  const queue = useAppSelector((s) => s.player.queue);
  const loadedUrlRef = useRef<string | null>(null);

  useEffect(() => {
    const unsubscribe = audioService.subscribe((event) => {
      if (event.type === 'status') {
        dispatch(updatePosition(event.positionMillis));
        dispatch(updateDuration(event.durationMillis));
      } else if (event.type === 'finished') {
        dispatch(skipToNext());
      } else if (event.type === 'error') {
        dispatch(pauseTrack());
      }
    });
    audioService.initialize().catch(() => {});
    return () => {
      unsubscribe();
      audioService.unload().catch(() => {});
    };
  }, [dispatch]);

  useEffect(() => {
    const track = queue.find((s) => s.id === currentTrackId);
    if (!track) {
      if (loadedUrlRef.current) {
        loadedUrlRef.current = null;
        audioService.unload().catch(() => {});
      }
      return;
    }
    if (track.url === loadedUrlRef.current) return;
    loadedUrlRef.current = track.url;
    audioService.loadAndPlay(track.url).catch(() => {
      dispatch(pauseTrack());
    });
  }, [currentTrackId, queue, dispatch]);

  useEffect(() => {
    if (!loadedUrlRef.current) return;
    if (isPlaying) {
      audioService.play().catch(() => {});
    } else {
      audioService.pause().catch(() => {});
    }
  }, [isPlaying]);
}
