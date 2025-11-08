// src/AppWebInteractive.tsx
import React, { useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, Pressable, FlatList } from 'react-native';
import { Provider, useDispatch, useSelector } from 'react-redux';
import { store } from './redux/store';
import { setSongs } from './redux/slices/librarySlice';
import { playTrack, pauseTrack, skipToNext, skipToPrevious, setShuffle, setRepeatMode } from './redux/slices/playerSlice';
import { mockSongs, mockPlaylists } from './data/mockSongs';
import type { RootState } from './redux/store';

function AppContent() {
  const dispatch = useDispatch();
  const [activeTab, setActiveTab] = React.useState('now-playing');
  
  // Load mock data on mount
  useEffect(() => {
    dispatch(setSongs(mockSongs));
  }, [dispatch]);

  // Redux selectors
  const playerState = useSelector((state: RootState) => state.player);
  const libraryState = useSelector((state: RootState) => state.library);

  const currentTrack = libraryState.allSongs.find(s => s.id === playerState.currentTrackId);

  const handlePlayTrack = (trackId: string) => {
    dispatch(playTrack(trackId));
  };

  const handlePause = () => {
    dispatch(pauseTrack());
  };

  const handlePlay = () => {
    if (!playerState.currentTrackId && libraryState.allSongs.length > 0) {
      dispatch(playTrack(libraryState.allSongs[0].id));
    } else {
      dispatch(playTrack(playerState.currentTrackId!));
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const renderNowPlaying = () => (
    <ScrollView style={styles.screen}>
      <Text style={styles.screenTitle}>🎵 Now Playing</Text>
      
      {currentTrack ? (
        <>
          <View style={styles.placeholder}>
            <Text style={styles.placeholderText}>{currentTrack.artwork || '♪'}</Text>
          </View>
          <Text style={styles.trackInfo}>{currentTrack.title}</Text>
          <Text style={styles.subtitle}>{currentTrack.artist}</Text>
          <Text style={styles.album}>{currentTrack.album}</Text>

          <View style={styles.progressContainer}>
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill, 
                  { width: `${(playerState.position / playerState.duration) * 100 || 0}%` }
                ]} 
              />
            </View>
            <View style={styles.timeContainer}>
              <Text style={styles.time}>{formatTime(playerState.position)}</Text>
              <Text style={styles.time}>{formatTime(playerState.duration)}</Text>
            </View>
          </View>

          <View style={styles.controls}>
            <Pressable 
              style={styles.button}
              onPress={() => dispatch(setShuffle(!playerState.shuffle))}
            >
              <Text style={playerState.shuffle ? styles.active : undefined}>{playerState.shuffle ? '🔀' : '→'}</Text>
            </Pressable>
            
            <Pressable style={styles.button} onPress={() => dispatch(skipToPrevious())}>
              <Text>⏮</Text>
            </Pressable>
            
            <Pressable 
              style={[styles.button, styles.playButton]}
              onPress={playerState.isPlaying ? handlePause : handlePlay}
            >
              <Text style={styles.playText}>{playerState.isPlaying ? '⏸' : '▶'}</Text>
            </Pressable>
            
            <Pressable style={styles.button} onPress={() => dispatch(skipToNext())}>
              <Text>⏭</Text>
            </Pressable>

            <Pressable 
              style={styles.button}
              onPress={() => {
                const modes: Array<'off' | 'one' | 'all'> = ['off', 'one', 'all'];
                const current = modes.indexOf(playerState.repeatMode);
                const next = modes[(current + 1) % modes.length];
                dispatch(setRepeatMode(next));
              }}
            >
              <Text style={playerState.repeatMode !== 'off' ? styles.active : undefined}>
                {playerState.repeatMode === 'one' ? '🔂' : playerState.repeatMode === 'all' ? '🔁' : '→'}
              </Text>
            </Pressable>
          </View>

          <View style={styles.status}>
            <Text style={styles.statusText}>
              {playerState.isPlaying ? '▶ Playing' : '⏸ Paused'}
            </Text>
          </View>
        </>
      ) : (
        <>
          <View style={styles.placeholder}>
            <Text style={styles.placeholderText}>♪</Text>
          </View>
          <Text style={styles.trackInfo}>No track playing</Text>
          <Text style={styles.subtitle}>Add songs from your library to get started</Text>
        </>
      )}
    </ScrollView>
  );

  const renderLibrary = () => (
    <View style={styles.screen}>
      <Text style={styles.screenTitle}>📚 Library</Text>
      <View style={styles.searchBox}>
        <Text>🔍 Search songs...</Text>
      </View>
      <View style={styles.tabs}>
        <Pressable style={styles.tab}><Text>Songs</Text></Pressable>
        <Pressable style={styles.tab}><Text>Artists</Text></Pressable>
        <Pressable style={styles.tab}><Text>Albums</Text></Pressable>
        <Pressable style={styles.tab}><Text>Genres</Text></Pressable>
      </View>
      
      <FlatList
        scrollEnabled={false}
        data={libraryState.allSongs}
        keyExtractor={item => item.id}
        renderItem={({ item }) => (
          <Pressable 
            style={styles.songItem}
            onPress={() => handlePlayTrack(item.id)}
          >
            <Text style={styles.songArtwork}>{item.artwork || '♪'}</Text>
            <View style={styles.songInfo}>
              <Text style={styles.songTitle}>{item.title}</Text>
              <Text style={styles.songArtist}>{item.artist}</Text>
            </View>
            <Text style={styles.songDuration}>{formatTime(item.duration)}</Text>
          </Pressable>
        )}
      />
    </View>
  );

  const renderPlaylists = () => (
    <ScrollView style={styles.screen}>
      <Text style={styles.screenTitle}>📋 Playlists</Text>
      <Text style={styles.subtitle}>Manage your playlists</Text>
      
      {mockPlaylists.map(playlist => (
        <View key={playlist.id} style={styles.playlistItem}>
          <View>
            <Text style={styles.playlistName}>{playlist.name}</Text>
            <Text style={styles.playlistDesc}>{playlist.songs.length} songs</Text>
          </View>
          <Text>→</Text>
        </View>
      ))}
      
      <Pressable style={styles.createButton}>
        <Text style={styles.createText}>+ Create Playlist</Text>
      </Pressable>
    </ScrollView>
  );

  const renderSettings = () => (
    <ScrollView style={styles.screen}>
      <Text style={styles.screenTitle}>⚙️ Settings</Text>
      
      <Text style={styles.sectionTitle}>AI & Metadata</Text>
      <View style={styles.optionGroup}>
        <Pressable style={styles.option}><Text>Manual</Text></Pressable>
        <Pressable style={styles.option}><Text>Gemini</Text></Pressable>
        <Pressable style={styles.option}><Text>Claude</Text></Pressable>
        <Pressable style={styles.option}><Text>GPT-4</Text></Pressable>
        <Pressable style={styles.option}><Text>Ollama</Text></Pressable>
      </View>
      
      <Text style={styles.sectionTitle}>Theme</Text>
      <View style={styles.optionGroup}>
        <Pressable style={styles.option}><Text>Light</Text></Pressable>
        <Pressable style={styles.option}><Text>Dark</Text></Pressable>
        <Pressable style={styles.option}><Text>Auto</Text></Pressable>
      </View>

      <Text style={styles.sectionTitle}>API Keys</Text>
      <View style={styles.inputGroup}>
        <Text style={styles.label}>AudD API Key</Text>
        <View style={styles.input}><Text style={styles.placeholder}>Enter API key...</Text></View>
      </View>
      
      <Text style={styles.version}>v1.0.0</Text>
    </ScrollView>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'now-playing':
        return renderNowPlaying();
      case 'library':
        return renderLibrary();
      case 'playlists':
        return renderPlaylists();
      case 'settings':
        return renderSettings();
      default:
        return null;
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.content}>
        {renderContent()}
      </View>
      
      <View style={styles.tabBar}>
        <Pressable 
          style={[styles.tabItem, activeTab === 'now-playing' && styles.tabItemActive]}
          onPress={() => setActiveTab('now-playing')}
        >
          <Text style={styles.tabIcon}>🎵</Text>
          <Text style={styles.tabLabel}>Now Playing</Text>
        </Pressable>
        
        <Pressable 
          style={[styles.tabItem, activeTab === 'library' && styles.tabItemActive]}
          onPress={() => setActiveTab('library')}
        >
          <Text style={styles.tabIcon}>📚</Text>
          <Text style={styles.tabLabel}>Library</Text>
        </Pressable>
        
        <Pressable 
          style={[styles.tabItem, activeTab === 'playlists' && styles.tabItemActive]}
          onPress={() => setActiveTab('playlists')}
        >
          <Text style={styles.tabIcon}>📋</Text>
          <Text style={styles.tabLabel}>Playlists</Text>
        </Pressable>
        
        <Pressable 
          style={[styles.tabItem, activeTab === 'settings' && styles.tabItemActive]}
          onPress={() => setActiveTab('settings')}
        >
          <Text style={styles.tabIcon}>⚙️</Text>
          <Text style={styles.tabLabel}>Settings</Text>
        </Pressable>
      </View>
    </View>
  );
}

export default function AppWebInteractive() {
  return (
    <Provider store={store}>
      <AppContent />
    </Provider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  content: {
    flex: 1,
    overflow: 'scroll',
  },
  screen: {
    padding: 20,
  },
  screenTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 16,
    marginBottom: 12,
  },
  placeholder: {
    width: 200,
    height: 200,
    borderRadius: 100,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'center',
    marginBottom: 20,
  },
  placeholderText: {
    fontSize: 80,
    color: '#ccc',
  },
  trackInfo: {
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
    marginBottom: 8,
  },
  album: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    marginBottom: 20,
  },
  progressContainer: {
    marginBottom: 20,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    overflow: 'hidden',
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#6200ea',
  },
  timeContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  time: {
    fontSize: 12,
    color: '#666',
  },
  controls: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
    gap: 20,
  },
  button: {
    width: 50,
    height: 50,
    borderRadius: 25,
    backgroundColor: '#f0f0f0',
    justifyContent: 'center',
    alignItems: 'center',
    fontSize: 24,
  },
  active: {
    color: '#6200ea',
    fontWeight: 'bold',
  },
  playButton: {
    width: 70,
    height: 70,
    backgroundColor: '#6200ea',
  },
  playText: {
    color: '#fff',
    fontSize: 28,
  },
  status: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    alignItems: 'center',
  },
  statusText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6200ea',
  },
  searchBox: {
    padding: 12,
    backgroundColor: '#f5f5f5',
    borderRadius: 8,
    marginBottom: 16,
  },
  tabs: {
    flexDirection: 'row',
    gap: 8,
    marginBottom: 16,
  },
  tab: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
  },
  songItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 10,
    marginBottom: 8,
    backgroundColor: '#f9f9f9',
    borderRadius: 6,
  },
  songArtwork: {
    fontSize: 32,
    marginRight: 12,
  },
  songInfo: {
    flex: 1,
  },
  songTitle: {
    fontSize: 14,
    fontWeight: '600',
  },
  songArtist: {
    fontSize: 12,
    color: '#666',
  },
  songDuration: {
    fontSize: 12,
    color: '#999',
  },
  playlistItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 12,
    marginBottom: 8,
    backgroundColor: '#f5f5f5',
    borderRadius: 6,
  },
  playlistName: {
    fontSize: 14,
    fontWeight: '600',
  },
  playlistDesc: {
    fontSize: 12,
    color: '#666',
    marginTop: 2,
  },
  createButton: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#6200ea',
    borderRadius: 8,
    marginTop: 20,
    alignItems: 'center',
  },
  createText: {
    color: '#fff',
    fontWeight: '600',
  },
  optionGroup: {
    gap: 8,
  },
  option: {
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: '#f5f5f5',
    borderRadius: 6,
  },
  inputGroup: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  input: {
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: '#f5f5f5',
    borderRadius: 6,
  },
  version: {
    fontSize: 12,
    color: '#999',
    textAlign: 'center',
    marginTop: 30,
  },
  tabBar: {
    flexDirection: 'row',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    backgroundColor: '#fff',
  },
  tabItem: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 4,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tabItemActive: {
    borderTopWidth: 3,
    borderTopColor: '#6200ea',
  },
  tabIcon: {
    fontSize: 20,
    marginBottom: 4,
  },
  tabLabel: {
    fontSize: 11,
    textAlign: 'center',
  },
});
