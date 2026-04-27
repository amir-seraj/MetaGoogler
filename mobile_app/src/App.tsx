// src/App.tsx
import React from 'react';
import { Provider } from 'react-redux';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';
import { PaperProvider } from 'react-native-paper';
import { store } from './redux/store';
import RootNavigator from './navigation/RootNavigator';
import { usePlayerBridge } from './services/usePlayerBridge';

function PlayerBridge() {
  usePlayerBridge();
  return null;
}

export default function App() {
  return (
    <Provider store={store}>
      <PaperProvider>
        <SafeAreaProvider>
          <NavigationContainer>
            <PlayerBridge />
            <RootNavigator />
          </NavigationContainer>
        </SafeAreaProvider>
      </PaperProvider>
    </Provider>
  );
}
