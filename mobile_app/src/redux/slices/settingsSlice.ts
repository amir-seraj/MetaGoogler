// src/redux/slices/settingsSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { SettingsState } from '../../types/index';

const initialState: SettingsState = {
  selectedAIBackend: 'manual',
  apiKeys: {},
  theme: 'auto',
};

const settingsSlice = createSlice({
  name: 'settings',
  initialState,
  reducers: {
    setAIBackend: (
      state,
      action: PayloadAction<'gemini' | 'claude' | 'gpt4' | 'ollama' | 'manual'>
    ) => {
      state.selectedAIBackend = action.payload;
    },
    setAPIKey: (state, action: PayloadAction<{ provider: string; key: string }>) => {
      state.apiKeys[action.payload.provider] = action.payload.key;
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark' | 'auto'>) => {
      state.theme = action.payload;
    },
    setEqualizerPreset: (state, action: PayloadAction<string | undefined>) => {
      state.equalizerPreset = action.payload;
    },
  },
});

export const { setAIBackend, setAPIKey, setTheme, setEqualizerPreset } =
  settingsSlice.actions;

export default settingsSlice.reducer;
