# 🚀 App Startup Guide

## What Just Happened

✅ **Expo server is now running** with a clean cache  
✅ **Project is bundling** with all dependencies ready  
✅ **No native audio module** (removed to speed up bundling)

## What You Should See

In your terminal, you should see a **QR code** that looks like:

```
▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
█ ▄▄▄▄▄ █ ██▀▀▄█▄██ ▄▄▄▄▄ █
█ █   █ █  ▀█ ▀▄█▀█ █   █ █
█ █▄▄▄█ █▀  █▄▄█▄▀█ █▄▄▄█ █
█▄▄▄▄▄▄▄█▄█ ▀▄█▄▀ █▄▄▄▄▄▄▄█
█ ▄█▀ ▄▄▀██▄█▄█▄ ▄██ ▀▄▄ ▄█
█   ▀▄▄▄▀█ ▄█▀▄█▄ ▀ █▄  ▀██
...
```

Followed by metro bundler status:
```
› Metro waiting on exp://172.20.129.76:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)
```

## Options to Test

### Option 1: Expo Go App (Easiest - No Simulator Needed)
1. **Android**: Open Expo Go app → Tap QR code icon → Scan the QR code from terminal
2. **iOS**: Open Camera app → Point at QR code → Tap notification to open

### Option 2: iOS Simulator
```bash
Press 'i' in the terminal
```

### Option 3: Android Emulator
```bash
Press 'a' in the terminal
```

### Option 4: Web Browser
```bash
Press 'w' in the terminal
```

## If the App Doesn't Load

### Problem 1: Spinning forever (>2 minutes)
**Solution**: The app is still bundling. Wait another minute. First bundle is slowest.

### Problem 2: Error message appears
**Solution**: Check the terminal for the error and screenshot it

### Problem 3: Blank white screen
**Solution**: This is normal - the app might just be loading. Wait 10-15 seconds.

### Problem 4: Can't see the QR code
**Solution**: Press 'r' in the terminal to reload

## What the App Should Show When Loaded

✅ **Bottom tab navigation** with 4 tabs:
- 🎵 Now Playing (play icon)
- 📚 Library (library-music icon)  
- 📋 Playlists (playlist-music icon)
- ⚙️ Settings (cog icon)

✅ **Now Playing screen** shows:
- Album art placeholder (music box icon)
- Song title: "No track playing"
- Player controls (play, pause, skip)
- Progress bar

✅ **Library screen** shows:
- Search bar
- View mode buttons (Songs, Artists, Albums, Genres)
- Empty song list

✅ **Settings screen** shows:
- AI Backend selector (Manual, Gemini, Claude, GPT-4, Ollama)
- API Key input fields
- Theme selector (Light, Dark, Auto)
- Version info

✅ **Playlists screen** shows:
- "No playlists yet" message
- Create button (+)

## Troubleshooting

### Still Loading After 3+ Minutes?

Run this command in a NEW terminal window:
```bash
cd /home/amir/Documents/Meta/mobile_app
npm start -- --clear
```

### Want to Reset Everything?

```bash
cd /home/amir/Documents/Meta/mobile_app
rm -rf .expo node_modules/.cache
npm start -- --clear
```

### Check Logs in Terminal

Look for any red error messages in the terminal running `npm start`. Screenshot them if there are any.

## Next Steps After App Loads

1. **Test Navigation**
   - Tap each tab at the bottom
   - Verify all screens appear

2. **Test Interactions**
   - Type in search bar (Library)
   - Click buttons and see if they respond
   - Try changing the theme (Settings)

3. **Report Issues**
   - If anything doesn't work, note:
     - What tab/screen you're on
     - What you clicked
     - What happened
     - Any error messages

## Commands Available

In the terminal where Expo is running, press:
- **r** - Reload the app
- **a** - Open Android Emulator
- **i** - Open iOS Simulator
- **w** - Open web browser
- **s** - Switch to Expo Go
- **j** - Open debugger
- **m** - Toggle menu
- **?** - Show all commands

---

**Status**: ✅ App is building and ready to test!  
**Next**: Scan the QR code with Expo Go or press 'i'/'a'/'w' in the terminal
