// src/screens/SettingsScreen.tsx
import React, { useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import {
  Text,
  SegmentedButtons,
  TextInput,
  Button,
  Divider,
  RadioButton,
} from 'react-native-paper';
import { useAppSelector, useAppDispatch } from '../redux/hooks';
import { setAIBackend, setAPIKey, setTheme } from '../redux/slices/settingsSlice';

export default function SettingsScreen() {
  const dispatch = useAppDispatch();
  const settings = useAppSelector((state) => state.settings);
  const [apiKeys, setApiKeys] = useState<Record<string, string>>(settings.apiKeys);

  const handleSaveAPIKey = (provider: string, key: string) => {
    dispatch(setAPIKey({ provider, key }));
    setApiKeys((prev) => ({ ...prev, [provider]: key }));
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      {/* AI Backend Selection */}
      <View style={styles.section}>
        <Text variant="headlineMedium" style={styles.sectionTitle}>
          AI & Metadata
        </Text>
        <Text variant="bodyMedium" style={styles.description}>
          Choose which AI service to use for metadata suggestions
        </Text>

        <SegmentedButtons
          value={settings.selectedAIBackend}
          onValueChange={(value) =>
            dispatch(
              setAIBackend(
                value as 'gemini' | 'claude' | 'gpt4' | 'ollama' | 'manual'
              )
            )
          }
          buttons={[
            { value: 'manual', label: 'Manual' },
            { value: 'gemini', label: 'Gemini' },
            { value: 'claude', label: 'Claude' },
            { value: 'gpt4', label: 'GPT-4' },
            { value: 'ollama', label: 'Ollama' },
          ]}
          style={styles.segmentedButtons}
        />
      </View>

      <Divider style={styles.divider} />

      {/* API Keys */}
      <View style={styles.section}>
        <Text variant="headlineSmall">API Keys</Text>
        <Text variant="bodySmall" style={styles.description}>
          Enter API keys for your selected providers (optional)
        </Text>

        <TextInput
          label="Gemini API Key"
          placeholder="Enter your Gemini API key"
          secureTextEntry
          value={apiKeys['gemini'] || ''}
          onChangeText={(text) => setApiKeys((prev) => ({ ...prev, gemini: text }))}
          style={styles.input}
        />

        <TextInput
          label="Claude API Key"
          placeholder="Enter your Claude API key"
          secureTextEntry
          value={apiKeys['claude'] || ''}
          onChangeText={(text) => setApiKeys((prev) => ({ ...prev, claude: text }))}
          style={styles.input}
        />

        <TextInput
          label="OpenAI API Key"
          placeholder="Enter your OpenAI API key"
          secureTextEntry
          value={apiKeys['openai'] || ''}
          onChangeText={(text) => setApiKeys((prev) => ({ ...prev, openai: text }))}
          style={styles.input}
        />

        <TextInput
          label="Ollama URL"
          placeholder="http://localhost:11434"
          value={apiKeys['ollama'] || ''}
          onChangeText={(text) => setApiKeys((prev) => ({ ...prev, ollama: text }))}
          style={styles.input}
        />

        <Button
          mode="contained"
          onPress={() => {
            Object.entries(apiKeys).forEach(([provider, key]) => {
              handleSaveAPIKey(provider, key);
            });
          }}
          style={styles.button}
        >
          Save API Keys
        </Button>
      </View>

      <Divider style={styles.divider} />

      {/* Theme Settings */}
      <View style={styles.section}>
        <Text variant="headlineSmall">Appearance</Text>
        <Text variant="bodySmall" style={styles.description}>
          Choose your preferred theme
        </Text>

        <RadioButton.Group
          value={settings.theme}
          onValueChange={(value) =>
            dispatch(setTheme(value as 'light' | 'dark' | 'auto'))
          }
        >
          <View style={styles.radioItem}>
            <RadioButton value="light" />
            <Text variant="bodyMedium" style={styles.radioLabel}>
              Light
            </Text>
          </View>
          <View style={styles.radioItem}>
            <RadioButton value="dark" />
            <Text variant="bodyMedium" style={styles.radioLabel}>
              Dark
            </Text>
          </View>
          <View style={styles.radioItem}>
            <RadioButton value="auto" />
            <Text variant="bodyMedium" style={styles.radioLabel}>
              Auto (System)
            </Text>
          </View>
        </RadioButton.Group>
      </View>

      <Divider style={styles.divider} />

      {/* App Info */}
      <View style={styles.section}>
        <Text variant="headlineSmall">About</Text>
        <View style={styles.infoRow}>
          <Text variant="bodyMedium">Version</Text>
          <Text variant="bodyMedium">0.1.0</Text>
        </View>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: 16,
    paddingVertical: 16,
  },
  section: {
    marginBottom: 16,
  },
  sectionTitle: {
    marginBottom: 8,
  },
  description: {
    opacity: 0.7,
    marginBottom: 12,
  },
  segmentedButtons: {
    marginVertical: 12,
  },
  input: {
    marginBottom: 12,
  },
  button: {
    marginTop: 8,
  },
  divider: {
    marginVertical: 16,
  },
  radioItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginVertical: 8,
  },
  radioLabel: {
    marginLeft: 8,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 12,
  },
});
