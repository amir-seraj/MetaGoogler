# Phase 1 Upgrade: COMPLETE ✅

## What You Now Have

### Before Phase 1
```
Song Metadata Fixer
        ↓
AIManager (Ollama only)
        ↓
Single local model (Mistral/Llama)
```

### After Phase 1
```
Song Metadata Fixer
        ↓
AIManager v2 (LiteLLM)
        ↓
13+ Models Available:
├─ Local:  Ollama (free)
├─ Cloud:  GPT-4, Claude-3, Gemini
└─ Switch: One line of code!
```

---

## What's Installed

✅ **LiteLLM** - Unified API for all LLM providers
✅ **ai_manager_v2.py** - New backward-compatible AI manager
✅ **Documentation** - Complete guide + quick reference
✅ **Mistral model** - Downloaded and ready

---

## How to Use Phase 1

### Option 1: Local Ollama (Current - Free)
```bash
# Already working!
python3 app_gui.py
```

### Option 2: Try GPT-4 (Need API key)
```bash
# 1. Get key from https://platform.openai.com/api-keys
# 2. Set environment variable
export OPENAI_API_KEY='sk-...'

# 3. Use in code or CLI
export LLM_MODEL="gpt-4"
python3 app_gui.py
```

### Option 3: Try Claude (Need API key)
```bash
# 1. Get key from https://console.anthropic.com/
# 2. Set environment variable
export ANTHROPIC_API_KEY='sk-ant-...'

# 3. Use
export LLM_MODEL="claude-3-sonnet"
python3 app_gui.py
```

### Option 4: Try Gemini (Free tier available)
```bash
# 1. Get key from https://makersuite.google.com/app/apikey
# 2. Set environment variable
export GOOGLE_API_KEY='...'

# 3. Use
export LLM_MODEL="gemini-pro"
python3 app_gui.py
```

---

## Files Created

```
Song Metadata Fixer/
├── ai_manager_v2.py                (NEW - Phase 1)
├── MCP_LITELLM_GUIDE.md           (NEW - Comprehensive guide)
├── MCP_LITELLM_QUICK_REF.md       (NEW - Quick reference)
├── app_gui.py                      (No changes needed!)
├── song_metadata_fixer_v2.py      (No changes needed!)
└── config.json                     (Add litellm_model field)
```

---

## Next: Phase 2 (Optional - Add Real Data)

To add Spotify + MusicBrainz integration:

```bash
# Install dependencies
pip install spotipy

# 1. Get Spotify API keys
# https://developer.spotify.com/dashboard
export SPOTIFY_CLIENT_ID='...'
export SPOTIFY_CLIENT_SECRET='...'

# 2. Follow Phase 2 guide in MCP_LITELLM_GUIDE.md
```

Phase 2 adds:
- Real Spotify metadata (album, release date, artist info)
- Audio features (mood, energy, danceability)
- MusicBrainz data (ISRC, comprehensive metadata)
- Enhanced AI suggestions using real data

---

## Quick Comparison: Which Model to Use?

| Model | Cost | Speed | Quality | Setup |
|-------|------|-------|---------|-------|
| **Ollama/Mistral** | Free | Fast | Good | ✅ Done |
| **GPT-4** | $0.03/1k | Medium | Excellent | Get API key |
| **Claude-3** | $0.003/1k | Medium | Excellent | Get API key |
| **Gemini** | Free tier | Fast | Good | Get API key |

**Recommendation**: Start with Ollama (working now), then try GPT-4 to see the difference!

---

## Testing Phase 1

```bash
# Test current model
python3 ai_manager_v2.py

# Test switching to another model
export LLM_MODEL="gpt-4"
python3 ai_manager_v2.py

# Test in GUI
python3 app_gui.py
# Click "Get AI Suggestions" on a file
```

---

## Troubleshooting Phase 1

**Problem**: "Model not found"
```bash
ollama pull mistral
```

**Problem**: "API key not valid"
```bash
# Check if key is set correctly
echo $OPENAI_API_KEY

# Make sure there are no extra spaces/quotes
export OPENAI_API_KEY="sk-xyz123"  # NOT "sk-xyz123" with extra quotes
```

**Problem**: "LiteLLM not found"
```bash
pip install litellm
```

---

## Next Steps

1. ✅ **Phase 1 Complete**: LiteLLM installed and tested
2. ⏳ **Phase 2 Optional**: Add MCP servers (Spotify + MusicBrainz)
3. ⏳ **Phase 3 Optional**: Integrate MCP with LLM for enhanced suggestions

Want to proceed to Phase 2? See: `MCP_LITELLM_GUIDE.md`

---

## Key Commands

```bash
# List available models
python3 -c "from ai_manager_v2 import AIManagerV2; print(AIManagerV2().list_available_models())"

# Test connection
python3 -c "from ai_manager_v2 import AIManagerV2; AIManagerV2().test_connection()"

# Switch models
export LLM_MODEL="gpt-4" && python3 app_gui.py

# Check which model is active
python3 -c "from ai_manager_v2 import AIManagerV2; print(AIManagerV2().model_name)"
```

---

## Architecture Overview

### Phase 1 (Current)
```
┌─────────────────┐
│  app_gui.py     │
└────────┬────────┘
         │ (imports)
         ▼
┌─────────────────┐
│ AIManagerV2     │
│ (LiteLLM)       │
└────────┬────────┘
         │ (completion API)
         ▼
┌─────────────────────────────┐
│  Model Provider             │
├─────────────────────────────┤
│ • Ollama (local) - ✅ Active│
│ • GPT-4 (cloud)             │
│ • Claude-3 (cloud)          │
│ • Gemini (cloud)            │
└─────────────────────────────┘
```

### Phase 2 (Optional)
```
┌─────────────────┐
│  app_gui.py     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ AIManagerV2     │◄──────────┐
│ (LiteLLM)       │           │
└────────┬────────┘           │
         │                    │
         ▼                    │
    Model with            ┌───┴────────────────┐
   Tool Use       │ MCP Servers        │
                 ├───────────────────┤
                 │ • Spotify         │
                 │ • MusicBrainz     │
                 │ • (future)        │
                 └───────────────────┘
```

---

## Success Indicators

✅ Phase 1 is complete if:
- `python3 ai_manager_v2.py` runs without errors
- Shows "✓ Connection successful"
- Generates AI suggestions
- Can list all 13+ available models

🎉 **You now have:**
- Multi-model support (local + cloud)
- Easy model switching
- Backward compatibility
- Foundation for Phase 2

---

## Questions or Issues?

Refer to:
1. **Quick answers**: See `MCP_LITELLM_QUICK_REF.md`
2. **Detailed guide**: See `MCP_LITELLM_GUIDE.md`
3. **Troubleshooting**: See Troubleshooting section in this file
4. **Code reference**: Look at `ai_manager_v2.py` docstrings

---

**Status**: Phase 1 ✅ Complete
**Next**: Phase 2 (Optional) - Add real music data via MCP
**Ready**: Yes! Everything is working and backward compatible.
