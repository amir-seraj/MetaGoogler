# 🤖 AI-Powered Metadata Suggestions Guide

MetaDataFixer now includes an intelligent AI feature that can automatically suggest corrections for messy, unstructured music metadata using local LLM inference via **Ollama**.

---

## 🎯 What Can AI Suggestions Do?

The AI feature excels at handling **messy, unstructured data**:

### 1. **Parse Complex Filenames**
| Input | AI Output |
|-------|-----------|
| `02-the_eagles-hotel_california_(live_at_the_forum_94)-remaster.flac` | artist: "Eagles", title: "Hotel California", version: "Live, Remastered" |
| `[Official Video] Dua Lipa - Levitating (2022 Remix) HD.mp3` | artist: "Dua Lipa", title: "Levitating", version: "2022 Remix" |
| `artist_name_song_title_feat_other_artist_remix.flac` | Extracts artist, featured collaborations, remix info |

### 2. **Clean Existing Metadata**
- Remove: `[Official Video]`, `(HD)`, `(4K)`, `(Official)`, etc.
- Fix capitalization: `the beatles` → `The Beatles`
- Extract versions: Live, Remaster, Acoustic, Remix, Remix, etc.

### 3. **Suggest Music Information**
- **Genre**: Based on artist/title knowledge
- **Moods**: Emotional characteristics (e.g., melancholic, energetic, romantic)
- **Confidence**: High/Medium/Low rating for suggestions

### 4. **Maintain Human Control**
- ✅ Every suggestion has a checkbox
- ✅ You approve/reject before any changes
- ✅ AI is an advisor, not a dictator

---

## 🚀 Getting Started

### Prerequisites

1. **Install Ollama** (local LLM server)
   ```bash
   # Download from: https://ollama.ai
   # Or on Linux:
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull the AI model** (one-time setup)
   ```bash
   ollama pull phi3
   ```

3. **Install Python dependencies**
   ```bash
   pip install ollama customtkinter mutagen Pillow
   ```

### Starting the System

1. **Terminal 1: Start Ollama Server**
   ```bash
   ollama serve
   ```
   You'll see: `Listening on 127.0.0.1:11434`

2. **Terminal 2: Launch MetaDataFixer GUI**
   ```bash
   python app_gui.py
   ```

---

## 📋 Using the AI Feature

### Step 1: Load Music Folder
1. Click **"Browse Folder"** button (top left)
2. Select a folder containing music files
3. The GUI displays all found music files

### Step 2: Select a File
- Click any file in the file list
- Current metadata displays in the preview panel

### Step 3: Get AI Suggestions
1. Click the **"Get AI Suggestions"** button (orange color)
2. Status bar shows: `AI is thinking...` ⏳
3. Wait 5-30 seconds (depending on your hardware)

### Step 4: Review Suggestions
A popup window appears with:

```
┌─────────────────────────────────────────────────┐
│  Current vs. AI Suggestions                     │
├─────────────────────────────────────────────────┤
│ ☑ artist          │ the eagles    → Eagles      │
│ ☑ title           │ Hotel Cal...  → Hotel Cal.. │
│ ☑ genre           │ (empty)       → Rock        │
│ ☑ date            │ (empty)       → 1977        │
│                                                 │
│  [Apply Changes]  [Cancel]                      │
└─────────────────────────────────────────────────┘
```

### Step 5: Approve/Reject Suggestions
- **✅ Checked** = Apply this suggestion
- **☐ Unchecked** = Skip this suggestion
- Click **"Apply Changes"** to save approved changes
- Click **"Cancel"** to discard all suggestions

### Step 6: Verify Results
The activity log shows:
```
[21:32:30] ✓ Applied AI suggestions to: Song_Name.mp3
[21:32:30] Updated tags: artist, title, genre, date
```

---

## 💡 Use Cases & Examples

### Example 1: Live Performance Recording
**Input File**: `Eagles_HotelCalifornia_Live_Forum_1994_Remaster.flac`  
**Before**: artist=empty, title=empty, album=empty  
**AI Suggests**:
- artist: Eagles
- title: Hotel California
- version: Live at the Forum, 1994, Remastered
- genre: Rock

**Result**: Metadata restored from filename! ✅

---

### Example 2: Remix with Extra Info
**Input File**: `[Official Video] Dua Lipa - Levitating (2022 Remix) HD.mp3`  
**Before**: artist="Dua Lipa", title="[Official Video] Levitating (2022 Remix) HD"  
**AI Suggests**:
- artist: Dua Lipa (no change needed ✓)
- title: Levitating (remove video/quality markers)
- version: 2022 Remix
- genre: Electronic/Pop

**Result**: Cleaned metadata without losing meaning! ✅

---

### Example 3: Collaboration Track
**Input File**: `song_feat_artist1_and_artist2_remix.mp3`  
**Before**: artist="artist0", title="song", album=empty  
**AI Suggests**:
- title: Song (feat. Artist1 & Artist2) [Remix]
- artists: artist0, artist1, artist2 (collaborators)
- genre: (detected based on pattern)

**Result**: Captures full artist information! ✅

---

## ⚙️ Configuration

Edit `config.json` to customize AI behavior:

```json
{
  "AI": {
    "model_name": "phi3",
    "confidence_threshold": "medium",
    "auto_apply_high_confidence": false
  }
}
```

### Settings
- **model_name**: LLM to use (phi3, mistral, neural-chat)
- **confidence_threshold**: Only apply suggestions at this confidence level
- **auto_apply_high_confidence**: Automatically apply high-confidence suggestions (without user review)

---

## 🔍 Understanding Confidence Levels

The AI provides a **confidence score** for each suggestion:

| Level | Meaning | Example |
|-------|---------|---------|
| 🟢 **High** | Very confident in this suggestion | Common songs, clear patterns |
| 🟡 **Medium** | Reasonable confidence, but might be wrong | Obscure artists, ambiguous names |
| 🔴 **Low** | Low confidence, manual review recommended | Very messy, conflicting info |

**Best Practice**: Always review suggestions, especially for **Medium/Low** confidence results.

---

## 🚨 Troubleshooting

### "Get AI Suggestions button is grayed out"
**Problem**: Ollama server not running or not reachable  
**Solution**:
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Test connection
ollama list
```

### "AI suggestions don't look right"
**Reasons**:
- AI model needs more context (try renaming file more descriptively)
- Unusual metadata format (AI works best with standard naming)
- Model needs updating

**Solution**: Update model:
```bash
ollama pull phi3
```

### "Application freezes when clicking 'Get AI Suggestions'"
**Problem**: GUI blocking during AI inference (shouldn't happen with v2.5)  
**Solution**: 
- Update to latest version
- Check system logs: `tail -50 metafixer.log`

### "Metadata not being written to file"
**Reasons**:
- File is read-only
- File format not supported (check supported formats in config.json)
- ID3 tag version issue

**Solution**: Check GUI logs for detailed error message

---

## 📊 Performance Tips

### Optimize Inference Speed
1. **Use GPU**: Ollama automatically uses NVIDIA CUDA if available
   ```
   GPU Memory: ~4GB for phi3
   Inference Speed: ~6-10 seconds per file
   ```

2. **Use Faster Models** (if inference is slow):
   ```bash
   ollama pull neural-chat   # Smaller, faster
   ollama pull mistral       # Faster reasoning
   ```

3. **Batch Processing** (coming in Phase 3):
   - Process multiple files sequentially
   - Progress tracking
   - Cancel at any time

---

## 🎓 Advanced: Custom AI Models

You can use different LLMs:

```bash
# Smaller models (faster, less accurate)
ollama pull neural-chat  # 4.1GB, fast
ollama pull orca-mini    # 3.3GB, very fast

# Larger models (slower, more accurate)
ollama pull mistral      # 4.4GB
ollama pull llama2        # 3.8GB

# Specialized models
ollama pull nous-hermes   # Better reasoning
ollama pull solar         # Better instructions
```

Then update `config.json`:
```json
{
  "AI": {
    "model_name": "mistral"
  }
}
```

---

## 📈 Feature Roadmap (Future Phases)

- **Phase 3**: Batch processing (analyze 10+ files at once)
- **Phase 3.5**: REST API for remote AI access
- **Phase 4**: Database to cache previous suggestions
- **Phase 4.5**: Fine-tuned models for better accuracy
- **Phase 5**: Multi-model voting (ensemble for better results)
- **Phase 6**: Docker deployment

---

## 🤝 Feedback & Issues

Found a bug or have a suggestion?
- Check logs: `metafixer.log`
- Report: GitHub Issues
- Include: Log file, file being processed, OS/hardware info

---

## 📚 Related Documentation

- **Quick Start**: `QUICK_START.md`
- **Configuration**: `config.json`
- **Architecture**: `README.md`
- **Testing**: `test_ai_feature.py`

---

**Happy metadata fixing! 🎵**
