// src/AppDebug.tsx
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Provider } from 'react-redux';
import { store } from './redux/store';

export default function AppDebug() {
  return (
    <Provider store={store}>
      <View style={styles.container}>
        <Text style={styles.title}>🎵 Mobile Music Player</Text>
        <Text style={styles.subtitle}>App is loading...</Text>
        <Text style={styles.text}>If you see this, the app is working!</Text>
      </View>
    </Provider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
    padding: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 10,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    marginBottom: 20,
    textAlign: 'center',
    color: '#666',
  },
  text: {
    fontSize: 14,
    textAlign: 'center',
    color: '#999',
  },
});
