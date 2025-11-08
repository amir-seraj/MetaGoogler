// src/AppWeb.tsx
import React from 'react';
import { View, Text, ScrollView, StyleSheet, Pressable } from 'react-native';
import { Provider } from 'react-redux';
import { store } from './redux/store';

export default function AppWeb() {
  const [activeTab, setActiveTab] = React.useState('now-playing');

  const renderContent = () => {
    switch (activeTab) {
      case 'now-playing':
        return (
          <View style={styles.screen}>
            <Text style={styles.screenTitle}>🎵 Now Playing</Text>
            <View style={styles.placeholder}>
              <Text style={styles.placeholderText}>♪</Text>
            </View>
            <Text style={styles.trackInfo}>No track playing</Text>
            <Text style={styles.subtitle}>Add songs from your library to get started</Text>
            <View style={styles.controls}>
              <Pressable style={styles.button}><Text>⏮</Text></Pressable>
              <Pressable style={[styles.button, styles.playButton]}><Text style={styles.playText}>▶</Text></Pressable>
              <Pressable style={styles.button}><Text>⏭</Text></Pressable>
            </View>
          </View>
        );
      case 'library':
        return (
          <View style={styles.screen}>
            <Text style={styles.screenTitle}>📚 Library</Text>
            <Text style={styles.subtitle}>Search and browse your music</Text>
            <View style={styles.searchBox}>
              <Text>🔍 Search songs...</Text>
            </View>
            <View style={styles.tabs}>
              <Pressable style={styles.tab}><Text>Songs</Text></Pressable>
              <Pressable style={styles.tab}><Text>Artists</Text></Pressable>
              <Pressable style={styles.tab}><Text>Albums</Text></Pressable>
              <Pressable style={styles.tab}><Text>Genres</Text></Pressable>
            </View>
            <Text style={styles.emptyText}>No songs found</Text>
          </View>
        );
      case 'playlists':
        return (
          <View style={styles.screen}>
            <Text style={styles.screenTitle}>📋 Playlists</Text>
            <Text style={styles.subtitle}>Manage your playlists</Text>
            <Text style={styles.emptyText}>No playlists yet</Text>
            <Pressable style={styles.createButton}>
              <Text style={styles.createText}>+ Create Playlist</Text>
            </Pressable>
          </View>
        );
      case 'settings':
        return (
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
          </ScrollView>
        );
      default:
        return null;
    }
  };

  return (
    <Provider store={store}>
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
  controls: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 30,
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
  playButton: {
    width: 70,
    height: 70,
    backgroundColor: '#6200ea',
  },
  playText: {
    color: '#fff',
    fontSize: 28,
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
  emptyText: {
    textAlign: 'center',
    color: '#999',
    marginTop: 20,
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
