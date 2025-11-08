# Quick Reference: MCP + LiteLLM Migration

## At a Glance

| Aspect | Current | Phase 1 | Phase 2 |
|--------|---------|---------|---------|
| **Models** | Ollama only | Ollama + Cloud | All + MCP Tools |
| **Setup Time** | - | 30 min | 2-3 hours |
| **API Keys** | None | Optional | Required (Spotify) |
| **Accuracy** | Good | Better (if cloud) | Best (real data) |
| **Cost** | Electricity | $0-20/month | $0-30/month |

---

## Phase 1: Quick Start (30 minutes)

### Step 1: Install
```bash
pip install litellm
```

### Step 2: Copy ai_manager_v2.py
From the detailed guide, use the `ai_manager_v2.py` code.

### Step 3: Update config.json
Add this section:
```json
{
  "ai_model": {
    "litellm_model": "ollama/mistral"
  }
}
```

### Step 4: Test
```python
from ai_manager_v2 import AIManagerV2
ai = AIManagerV2()
ai.test_connection()
```

### Step 5: Switch Models (Optional)
```bash
# Try GPT-4 (requires OPENAI_API_KEY)
export OPENAI_API_KEY='sk-...'
export LLM_MODEL="gpt-4"

# Or Claude (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY='sk-ant-...'
export LLM_MODEL="claude-3-sonnet"
```

---

## Phase 2: MCP Servers (2-3 hours)

### Spotify Setup
```bash
# 1. Get credentials from https://developer.spotify.com/dashboard
# 2. Set environment variables
export SPOTIFY_CLIENT_ID='...'
export SPOTIFY_CLIENT_SECRET='...'

# 3. Install spotipy
pip install spotipy

# 4. Test
python3 -c "
from mcp_servers.spotify_server import SpotifyMCPServer
s = SpotifyMCPServer()
result = s.search_track('Blinding Lights', 'The Weeknd')
print(result)
"
```

### MusicBrainz Setup
```bash
# No API key needed!
python3 -c "
from mcp_servers.musicbrainz_server import MusicBrainzMCPServer
m = MusicBrainzMCPServer()
result = m.search_recording('Blinding Lights', 'The Weeknd')
print(result)
"
```

---

## Model Examples

### Local (Free, Instant)
```python
ai = AIManagerV2(model_name="ollama/mistral")
```

### OpenAI (Fast, Accurate)
```bash
export OPENAI_API_KEY='sk-...'
ai = AIManagerV2(model_name="gpt-4")
```

### Claude (Accurate, Thoughtful)
```bash
export ANTHROPIC_API_KEY='sk-ant-...'
ai = AIManagerV2(model_name="claude-3-sonnet")
```

### Google Gemini (Fast, Free Tier)
```bash
export GOOGLE_API_KEY='...'
ai = AIManagerV2(model_name="gemini-pro")
```

---

## Model Comparison

| Model | Speed | Cost | Quality | Best For |
|-------|-------|------|---------|----------|
| Ollama/Mistral | Fast | Free | Good | Local, testing |
| GPT-4 | Medium | $0.03/1k tokens | Excellent | Production |
| Claude 3 | Medium | $0.003/1k tokens | Excellent | Analysis |
| Gemini | Very Fast | Free tier | Good | Quick tasks |

---

## Command Reference

```bash
# Test connection
python3 -c "from ai_manager_v2 import AIManagerV2; AIManagerV2().test_connection()"

# List available models
python3 -c "from ai_manager_v2 import AIManagerV2; print(AIManagerV2().list_available_models())"

# Switch models
export LLM_MODEL="gpt-4"
python3 app_gui.py

# Get AI suggestions
python3 -c "
from ai_manager_v2 import AIManagerV2
ai = AIManagerV2()
result = ai.get_ai_suggestions('Song.mp3', {'artist': 'Unknown'})
print(result)
"

# Test Spotify MCP
python3 test_mcp_integration.py

# Test MusicBrainz MCP
python3 -c "
from mcp_servers.musicbrainz_server import MusicBrainzMCPServer
m = MusicBrainzMCPServer()
print(m.search_recording('Blinding Lights', 'The Weeknd'))
"
```

---

## Environment Variables Cheat Sheet

```bash
# Ollama (local)
export OLLAMA_BASE_URL="http://localhost:11434"

# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GOOGLE_API_KEY="..."

# Spotify
export SPOTIFY_CLIENT_ID="..."
export SPOTIFY_CLIENT_SECRET="..."

# Override model globally
export LLM_MODEL="gpt-4"
```

Save to `.env` file and load with:
```bash
source .env
```

---

## Troubleshooting Quick Links

- Ollama not running? → `ollama serve`
- Model not found? → `ollama pull mistral`
- API key error? → Check `export OPENAI_API_KEY='...'`
- Spotify not working? → Check credentials with `echo $SPOTIFY_CLIENT_ID`
- MusicBrainz timeout? → Add `time.sleep(1)` between requests

---

## Next Steps

1. **Start Phase 1**: Copy `ai_manager_v2.py` and test with local Ollama
2. **Try cloud models**: Get API key, test GPT-4 vs Claude
3. **Pick best model**: Compare quality/cost for your use case
4. **Add Phase 2**: Set up Spotify MCP for real metadata
5. **Optimize**: Add caching, batch processing

---

## File Structure After Migration

```
Song Metadata Fixer/
├── app_gui.py                    (no changes needed)
├── song_metadata_fixer_v2.py     (no changes needed)
├── ai_manager_v2.py              (NEW - replaces ai_manager.py)
├── config.json                   (update with litellm_model)
├── mcp_servers/                  (NEW)
│   ├── __init__.py
│   ├── spotify_server.py         (NEW)
│   └── musicbrainz_server.py     (NEW)
├── .env                          (NEW - add API keys here)
└── test_*.py                     (NEW - test files)
```
