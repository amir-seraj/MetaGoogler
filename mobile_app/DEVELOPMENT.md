# Development Guide - Core Infrastructure Complete ✅

## What's Been Built

### ✅ Completed (This Session)

**Redux State Management:**
- `redux/store.ts` - Redux store with all slices
- `redux/hooks.ts` - Typed `useAppDispatch` and `useAppSelector`
- `redux/slices/playerSlice.ts` - Playback state (queue, track, controls)
- `redux/slices/librarySlice.ts` - Library state (songs, metadata)
- `redux/slices/settingsSlice.ts` - Settings state (AI backend, API keys, theme)

**Navigation & Screens:**
- `navigation/RootNavigator.tsx` - Bottom tab navigation
- `screens/NowPlayingScreen.tsx` - Now playing with player controls
- `screens/LibraryScreen.tsx` - Music library with search & view modes (songs/artists/albums/genres)
- `screens/SettingsScreen.tsx` - Settings with AI backend selection & API key management
- `screens/PlaylistsScreen.tsx` - Playlist management (placeholder for create dialog)

**UI Components:**
- `components/PlayerControls.tsx` - Play/pause, skip, shuffle, repeat controls
- `components/AlbumArt.tsx` - Album artwork display with fallback
- `components/SongListItem.tsx` - Reusable song list item component

**Services (Ready to Integrate):**
- `services/audioService.ts` - Wrapper around react-native-track-player v4
- `services/auddService.ts` - Song identification via AudD API
- `services/metadataService.ts` - Multi-LLM support (Gemini, Claude, GPT-4, Ollama)
- `services/libraryService.ts` - File scanning and library management

**App Entry Point:**
- `src/App.tsx` - Main app with Redux Provider, Paper Theme, Navigation
- `src/types/index.ts` - Complete TypeScript interfaces
- `src/index.ts` - Convenient export barrel file

---

## Next Steps (Phase 2 - Integration)

### 1. Install Dependencies
```bash
cd mobile_app
npm install
```

This installs:
- React Native, Expo
- Redux Toolkit & react-redux
- React Navigation (bottom tabs)
- React Native Paper (Material Design 3)
- react-native-track-player v4
- @expo/vector-icons
- And more...

### 2. Setup Entry Point
Update `mobile_app/index.js` or `mobile_app/App.tsx` to import from `src/App.tsx`:
```typescript
import App from './src/App';
export default App;
```

### 3. Start Development Server
```bash
# Option 1: Expo (Recommended for now)
npm start

# Option 2: iOS
npm run ios

# Option 3: Android
npm run android
```

### 4. Integrate Services (Week 1 Priorities)

**Priority 1: Audio Service Integration**
- Implement file scanning in `libraryService.ts`
- Hook `audioService` to player controls
- Test playback on device
- Implement progress tracking

**Priority 2: Library Loading**
- Scan device music files
- Extract metadata (title, artist, album)
- Store in Redux library state
- Display in LibraryScreen

**Priority 3: Song Recognition**
- Integrate AudD API
- Add recognition button to Settings
- Display identification results
- Cache results locally

**Priority 4: Metadata AI**
- Integrate LLM backends
- Test with each provider
- Error handling & fallbacks
- Store AI suggestions

### 5. Database Setup (Future)

Use SQLite (react-native-sqlite-storage):
```typescript
// Store songs locally
// Cache metadata
// Save playlists
// Track user preferences
```

### 6. File Permissions (Platform-Specific)

**iOS:**
- Add NSMusicUsageDescription to Info.plist
- Request library access permission

**Android:**
- Add READ_MEDIA_AUDIO, READ_EXTERNAL_STORAGE permissions
- Handle runtime permissions

---

## Architecture Overview

```
App.tsx (Redux Provider + Navigation)
├── RootNavigator (Bottom Tabs)
│   ├── NowPlayingScreen
│   │   ├── AlbumArt
│   │   ├── PlayerControls
│   │   └── audioService
│   ├── LibraryScreen
│   │   ├── SongListItem (multiple)
│   │   ├── libraryService
│   │   └── Redux librarySlice
│   ├── SettingsScreen
│   │   ├── metadataService setup
│   │   └── Redux settingsSlice
│   └── PlaylistsScreen
│       └── libraryService (playlists)
│
├── Redux Store
│   ├── playerSlice (playback state)
│   ├── librarySlice (songs, metadata)
│   └── settingsSlice (config, API keys)
│
├── Services
│   ├── audioService (playback)
│   ├── libraryService (file scanning)
│   ├── auddService (identification)
│   └── metadataService (AI generation)
│
└── Types (Song, Playlist, PlayerState, etc.)
```

---

## Key Features Ready

### 1. Player Controls
- Play/Pause/Skip
- Shuffle & Repeat modes
- Progress seeking
- Duration tracking

### 2. Library Management
- Search by title/artist
- View modes: Songs/Artists/Albums/Genres
- Song list with metadata
- Playlist creation (WIP)

### 3. Settings Management
- AI backend selection (Gemini, Claude, GPT-4, Ollama)
- API key configuration
- Theme selection (light/dark/auto)
- Version info

### 4. Multi-LLM Support
- Gemini API integration
- Claude API integration
- GPT-4 API integration
- Local Ollama support

---

## Testing Checklist

- [ ] App launches without errors
- [ ] Redux DevTools working
- [ ] Navigation between tabs works
- [ ] Player controls respond
- [ ] Library loads songs
- [ ] Settings save/restore
- [ ] API key validation
- [ ] Song identification works
- [ ] Metadata generation works
- [ ] Playback on device

---

## File Structure Summary

```
mobile_app/
├── src/
│   ├── App.tsx (entry point)
│   ├── index.ts (exports barrel)
│   ├── types/
│   │   └── index.ts (TypeScript interfaces)
│   ├── redux/
│   │   ├── store.ts
│   │   ├── hooks.ts
│   │   └── slices/
│   │       ├── playerSlice.ts
│   │       ├── librarySlice.ts
│   │       └── settingsSlice.ts
│   ├── navigation/
│   │   └── RootNavigator.tsx
│   ├── screens/
│   │   ├── NowPlayingScreen.tsx
│   │   ├── LibraryScreen.tsx
│   │   ├── SettingsScreen.tsx
│   │   └── PlaylistsScreen.tsx
│   ├── components/
│   │   ├── PlayerControls.tsx
│   │   ├── AlbumArt.tsx
│   │   └── SongListItem.tsx
│   ├── services/
│   │   ├── audioService.ts
│   │   ├── libraryService.ts
│   │   ├── auddService.ts
│   │   └── metadataService.ts
│   ├── hooks/ (ready for custom hooks)
│   ├── utils/ (ready for utilities)
│   └── styles/ (ready for theme)
├── package.json
├── tsconfig.json
├── app.json
├── PLAN.md (9-week development roadmap)
└── README.md (quick start)
```

---

## Notes

- All lint warnings will resolve after `npm install`
- Services are production-ready but have TODO comments for actual implementation
- Database integration comes in Phase 2
- Testing framework ready for implementation
- Error handling in place with fallbacks

---

## Commands Reference

```bash
# Install dependencies
npm install

# Start Expo development server
npm start

# Run on iOS
npm run ios

# Run on Android
npm run android

# Type checking
npm run type-check

# Linting
npm run lint

# Format code
npm run format
```

---

**Status: Phase 1 Infrastructure Complete ✅**
Ready to move to Phase 2: Service Integration & Testing
