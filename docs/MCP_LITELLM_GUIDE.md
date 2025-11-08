# Complete Guide: Upgrading to MCP + LiteLLM

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Phase 1: LiteLLM Migration](#phase-1-litellm-migration)
3. [Phase 2: MCP Servers Setup](#phase-2-mcp-servers-setup)
4. [Phase 3: Integration](#phase-3-integration)
5. [Testing & Validation](#testing--validation)
6. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### Current Architecture
```
┌─────────────────────────────────┐
│  Song Metadata Fixer            │
│  (app_gui.py, cli)              │
└────────────────┬────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │  AIManager     │
        │  (ollama only) │
        └────────────────┘
                 │
                 ▼
        ┌────────────────┐
        │ Local LLM      │
        │ (Mistral/Llama)│
        └────────────────┘
```

### New Architecture (Phase 1: LiteLLM)
```
┌─────────────────────────────────┐
│  Song Metadata Fixer            │
│  (app_gui.py, cli)              │
└────────────────┬────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │  AIManager v2      │
        │  (LiteLLM)         │
        └────────┬───────────┘
                 │
        ┌────────┴─────────┬──────────┬─────────┐
        ▼                  ▼          ▼         ▼
    ┌────────┐         ┌──────┐  ┌──────┐  ┌──────┐
    │ Ollama │         │ GPT  │  │Claude│  │Gemini│
    │ (local)│         │  (OAI)  │ (A) │  │ (G) │
    └────────┘         └──────┘  └──────┘  └──────┘
```

### Final Architecture (Phase 2: MCP + LiteLLM)
```
┌─────────────────────────────────┐
│  Song Metadata Fixer            │
└────────────────┬────────────────┘
                 │
         ┌───────▼────────┐
         │  AIManager v2  │
         │  (LiteLLM)     │
         └───────┬────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐  ┌─────────┐  ┌──────────┐
│ Models │  │   MCP   │  │ Caching  │
└────────┘  │ Tools   │  └──────────┘
            └─────────┘
                 │
        ┌────────┴────────┐
        ▼                 ▼
    ┌─────────┐      ┌──────────┐
    │ Spotify │      │MusicBrainz
    │ MCP     │      │ MCP
    └─────────┘      └──────────┘
```

---

## Phase 1: LiteLLM Migration

### Step 1: Install LiteLLM and Dependencies

```bash
# Install LiteLLM
pip install litellm

# Install optional providers (add what you need)
pip install openai           # For GPT-4, GPT-3.5
pip install anthropic        # For Claude
pip install google-generativeai  # For Gemini
pip install cohere          # For Cohere (optional)
```

### Step 2: Create New AIManager v2

Create a new file `ai_manager_v2.py`:

```python
"""
AIManager v2: LiteLLM-based AI model management
Supports multiple LLM providers with unified interface.
Backward compatible with existing code.
"""

import json
import logging
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import re

# LiteLLM imports
from litellm import completion, list_deployed_models
import litellm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIManagerV2:
    """
    LiteLLM-based AI Manager supporting multiple model providers.
    
    Supported providers:
    - ollama (local): "ollama/mistral", "ollama/llama2"
    - openai: "gpt-4", "gpt-3.5-turbo"
    - anthropic: "claude-3-sonnet", "claude-3-opus"
    - google: "gemini-pro"
    - huggingface: "huggingface/meta-llama/Llama-2-7b"
    """
    
    def __init__(self, config_path: Optional[Path] = None, model_name: Optional[str] = None):
        """
        Initialize AIManager v2.
        
        Args:
            config_path: Path to config.json
            model_name: Override model from config (e.g., "gpt-4", "claude-3-sonnet")
        """
        self.logger = logger
        self.config = self._load_config(config_path)
        
        # Get model from parameter, environment, or config
        self.model_name = (
            model_name or 
            os.getenv('LLM_MODEL') or 
            self.config.get("ai_model", {}).get("litellm_model", "ollama/mistral")
        )
        
        self.logger.info(f"Using model: {self.model_name}")
        
        # Set up API keys from environment or config
        self._setup_api_keys()
        
        # Model configuration
        self.temperature = self.config.get("ai_model", {}).get("temperature", 0.7)
        self.max_tokens = self.config.get("ai_model", {}).get("max_tokens", 1000)
        self.timeout = self.config.get("ai_model", {}).get("timeout", 30)
    
    def _load_config(self, config_path: Optional[Path]) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if config_path is None:
            possible_paths = [
                Path(__file__).parent / "config.json",
                Path.cwd() / "config.json",
            ]
            
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break
            
            if config_path is None:
                self.logger.warning("Config file not found, using defaults")
                return {}
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.logger.debug(f"Loaded config from {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}
    
    def _setup_api_keys(self):
        """Set up API keys from environment variables or config."""
        # OpenAI
        if os.getenv('OPENAI_API_KEY'):
            litellm.openai_key = os.getenv('OPENAI_API_KEY')
        
        # Anthropic (Claude)
        if os.getenv('ANTHROPIC_API_KEY'):
            litellm.claude_key = os.getenv('ANTHROPIC_API_KEY')
        
        # Google (Gemini)
        if os.getenv('GOOGLE_API_KEY'):
            litellm.google_key = os.getenv('GOOGLE_API_KEY')
        
        # Ollama - set base URL if custom
        if os.getenv('OLLAMA_BASE_URL'):
            litellm.ollama_base_url = os.getenv('OLLAMA_BASE_URL')
        else:
            litellm.ollama_base_url = "http://localhost:11434"
        
        self.logger.debug("API keys configured")
    
    def test_connection(self) -> bool:
        """
        Test if the model is available and responding.
        
        Returns:
            True if model responds, False otherwise
        """
        try:
            self.logger.info(f"Testing connection to {self.model_name}...")
            
            response = completion(
                model=self.model_name,
                messages=[{"role": "user", "content": "Say 'ok'"}],
                temperature=0.5,
                max_tokens=10,
                timeout=self.timeout,
            )
            
            self.logger.info(f"✓ Model {self.model_name} is responsive")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to connect to {self.model_name}: {e}")
            return False
    
    def get_ai_suggestions(
        self, 
        filename: str, 
        current_metadata: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get AI metadata suggestions for a file.
        
        Args:
            filename: Audio filename (may contain metadata clues)
            current_metadata: Current metadata dict
        
        Returns:
            Dictionary with suggestions or None if failed
        """
        # Build prompt
        prompt = self._build_ai_prompt(filename, current_metadata)
        
        try:
            self.logger.debug(f"Requesting suggestions from {self.model_name}")
            
            response = completion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )
            
            response_text = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            if not response_text:
                self.logger.warning("Empty response from model")
                return None
            
            # Parse JSON
            try:
                suggestions = json.loads(response_text)
                self.logger.debug(f"Successfully parsed suggestions: {suggestions}")
                return suggestions
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse response as JSON: {e}")
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    suggestions = json.loads(json_match.group())
                    return suggestions
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {e}")
            return None
    
    def _build_ai_prompt(
        self, 
        filename: str, 
        current_meta: Dict[str, Any]
    ) -> str:
        """Build a structured prompt for metadata suggestions."""
        
        prompt = f"""You are a music metadata expert. Analyze the following information and suggest improved metadata.

Filename: {filename}

Current Metadata:
- Title: {current_meta.get('title', 'Unknown')}
- Artist: {current_meta.get('artist', 'Unknown')}
- Album: {current_meta.get('album', 'Unknown')}
- Date: {current_meta.get('date', 'Unknown')}
- Genre: {current_meta.get('genre', 'Unknown')}
- Track Number: {current_meta.get('tracknumber', '0')}

Task:
1. Extract any metadata clues from the filename
2. Suggest improvements to existing metadata
3. Return a JSON object with suggestions

Return ONLY valid JSON in this format:
{{
    "title": "suggested title",
    "artist": "suggested artist",
    "album": "suggested album",
    "genre": "suggested genre",
    "date": "YYYY-MM-DD or YYYY",
    "confidence": 0.85,
    "notes": "explanation of changes"
}}

Be accurate and conservative - only suggest changes you're confident about."""
        
        return prompt
    
    def switch_model(self, new_model: str) -> bool:
        """
        Switch to a different model.
        
        Args:
            new_model: Model identifier (e.g., "gpt-4", "claude-3-sonnet", "ollama/mistral")
        
        Returns:
            True if switch successful, False otherwise
        """
        old_model = self.model_name
        self.model_name = new_model
        
        self.logger.info(f"Switching model: {old_model} -> {new_model}")
        
        if self.test_connection():
            self.logger.info(f"✓ Successfully switched to {new_model}")
            return True
        else:
            self.model_name = old_model
            self.logger.error(f"✗ Failed to switch to {new_model}, reverted to {old_model}")
            return False
    
    def list_available_models(self) -> List[str]:
        """
        List models that could be used.
        
        Returns:
            List of model identifiers
        """
        models = [
            # Local (Ollama)
            "ollama/mistral",
            "ollama/llama2",
            "ollama/neural-chat",
            
            # OpenAI
            "gpt-4",
            "gpt-3.5-turbo",
            
            # Anthropic
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            
            # Google
            "gemini-pro",
            
            # HuggingFace
            "huggingface/meta-llama/Llama-2-7b",
        ]
        return models


# Backward compatibility: keep old interface
class AIManager(AIManagerV2):
    """Backward compatible AIManager - inherits from AIManagerV2"""
    pass


if __name__ == "__main__":
    # Test script
    ai = AIManagerV2()
    
    # Test connection
    if ai.test_connection():
        # Test suggestions
        result = ai.get_ai_suggestions(
            "The Weeknd - Blinding Lights (320).mp3",
            {
                "title": "Blinding Lights (320)",
                "artist": "The Weeknd",
                "album": "After Hours",
                "genre": "Unknown"
            }
        )
        print(json.dumps(result, indent=2))
    else:
        print("Failed to connect to model")
```

### Step 3: Update config.json

Add LiteLLM configuration:

```json
{
  "ai_model": {
    "name": "mistral",
    "litellm_model": "ollama/mistral",
    "model_path": "~/.ollama/models",
    "temperature": 0.7,
    "max_tokens": 1000,
    "timeout": 30
  },
  "supported_providers": {
    "ollama": {
      "enabled": true,
      "base_url": "http://localhost:11434"
    },
    "openai": {
      "enabled": false,
      "key_env": "OPENAI_API_KEY"
    },
    "anthropic": {
      "enabled": false,
      "key_env": "ANTHROPIC_API_KEY"
    },
    "google": {
      "enabled": false,
      "key_env": "GOOGLE_API_KEY"
    }
  }
}
```

### Step 4: Update song_metadata_fixer_v2.py

Replace the import and initialization:

```python
# OLD
from ai_manager import AIManager

# NEW
from ai_manager_v2 import AIManager  # Now uses LiteLLM
```

No other changes needed! The interface is the same.

### Step 5: Test LiteLLM Integration

Create `test_litellm.py`:

```python
#!/usr/bin/env python3
"""Test script for LiteLLM migration."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ai_manager_v2 import AIManagerV2
import json

def test_local_ollama():
    """Test with local Ollama (default)."""
    print("\n" + "="*50)
    print("TEST 1: Local Ollama (Default)")
    print("="*50)
    
    ai = AIManagerV2()
    print(f"Model: {ai.model_name}")
    
    if ai.test_connection():
        print("✓ Connection successful")
        
        result = ai.get_ai_suggestions(
            "The Weeknd - Blinding Lights (320).mp3",
            {
                "title": "Blinding Lights (320)",
                "artist": "The Weeknd",
                "album": "After Hours"
            }
        )
        
        if result:
            print("✓ Got suggestions:")
            print(json.dumps(result, indent=2))
        else:
            print("✗ Failed to get suggestions")
    else:
        print("✗ Connection failed")


def test_model_switching():
    """Test switching between models."""
    print("\n" + "="*50)
    print("TEST 2: Model Switching")
    print("="*50)
    
    ai = AIManagerV2(model_name="ollama/mistral")
    
    # Try switching to different models
    models_to_try = [
        "ollama/llama2",
        "ollama/neural-chat",
    ]
    
    for model in models_to_try:
        print(f"\nTrying to switch to: {model}")
        if ai.switch_model(model):
            print(f"  ✓ Successfully switched")
        else:
            print(f"  ✗ Model not available")


def test_list_models():
    """List available models."""
    print("\n" + "="*50)
    print("TEST 3: Available Models")
    print("="*50)
    
    ai = AIManagerV2()
    models = ai.list_available_models()
    
    print("\nAvailable models:")
    for model in models:
        print(f"  - {model}")


if __name__ == "__main__":
    test_local_ollama()
    test_model_switching()
    test_list_models()
    
    print("\n" + "="*50)
    print("All tests completed!")
    print("="*50)
```

Run the test:

```bash
python3 test_litellm.py
```

---

## Phase 2: MCP Servers Setup

### Step 1: Install MCP Framework

```bash
pip install mcp
pip install anthropic  # Required for MCP SSE transport
```

### Step 2: Create MCP Server Base

Create `mcp_servers/__init__.py`:

```python
"""MCP (Model Context Protocol) Servers for music metadata."""
```

Create `mcp_servers/spotify_server.py`:

```python
"""
MCP Server for Spotify API integration.
Allows LLM to query real Spotify data.
"""

import os
import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

try:
    import spotipy
    from spotipy.oauth2 import SpotifyClientCredentials
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False
    logger.warning("Spotipy not installed. Install with: pip install spotipy")


class SpotifyMCPServer:
    """
    MCP Server for Spotify integration.
    Provides tools for the LLM to query Spotify data.
    """
    
    def __init__(self):
        """Initialize Spotify API client."""
        self.client = None
        self.available = False
        
        if not SPOTIPY_AVAILABLE:
            logger.error("Spotipy not installed")
            return
        
        try:
            # Get credentials from environment
            client_id = os.getenv('SPOTIFY_CLIENT_ID')
            client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
            
            if not client_id or not client_secret:
                logger.error("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET not set")
                return
            
            # Authenticate
            auth = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret
            )
            self.client = spotipy.Spotify(auth_manager=auth)
            self.available = True
            logger.info("✓ Spotify MCP Server initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Spotify: {e}")
    
    def search_track(
        self, 
        query: str, 
        artist: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Search for a track on Spotify.
        
        Args:
            query: Track query string
            artist: Optional artist name
        
        Returns:
            Track data or None if not found
        """
        if not self.available:
            return None
        
        try:
            # Build search query
            search_query = query
            if artist:
                search_query = f"{query} artist:{artist}"
            
            # Search
            results = self.client.search(q=search_query, type='track', limit=1)
            
            if not results['tracks']['items']:
                logger.warning(f"No tracks found for: {search_query}")
                return None
            
            track = results['tracks']['items'][0]
            
            # Extract relevant data
            data = {
                "title": track.get('name'),
                "artist": ', '.join([a['name'] for a in track.get('artists', [])]),
                "album": track.get('album', {}).get('name'),
                "release_date": track.get('album', {}).get('release_date'),
                "duration_ms": track.get('duration_ms'),
                "explicit": track.get('explicit'),
                "isrc": track.get('external_ids', {}).get('isrc'),
                "spotify_id": track.get('id'),
                "spotify_url": track.get('external_urls', {}).get('spotify'),
                "popularity": track.get('popularity'),
            }
            
            logger.info(f"Found track: {data['artist']} - {data['title']}")
            return data
            
        except Exception as e:
            logger.error(f"Error searching Spotify: {e}")
            return None
    
    def get_audio_features(self, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audio features for a track (mood, energy, danceability, etc.).
        
        Args:
            track_id: Spotify track ID
        
        Returns:
            Audio features dict or None
        """
        if not self.available or not self.client:
            return None
        
        try:
            features = self.client.audio_features(track_id)[0]
            
            # Extract useful features
            data = {
                "energy": features.get('energy'),
                "danceability": features.get('danceability'),
                "valence": features.get('valence'),  # Mood positivity
                "acousticness": features.get('acousticness'),
                "instrumentalness": features.get('instrumentalness'),
                "liveness": features.get('liveness'),
                "speechiness": features.get('speechiness'),
                "tempo": features.get('tempo'),
                "key": features.get('key'),
                "mode": features.get('mode'),  # 0=minor, 1=major
                "time_signature": features.get('time_signature'),
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting audio features: {e}")
            return None
    
    def get_tools(self):
        """
        Get tool definitions for LLM integration.
        Returns tools that an LLM can call.
        """
        return [
            {
                "name": "search_spotify_track",
                "description": "Search for a track on Spotify and get its metadata",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Track title or query"
                        },
                        "artist": {
                            "type": "string",
                            "description": "Artist name (optional)"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_audio_features",
                "description": "Get audio features (mood, energy, tempo) for a Spotify track",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "track_id": {
                            "type": "string",
                            "description": "Spotify track ID"
                        }
                    },
                    "required": ["track_id"]
                }
            }
        ]


if __name__ == "__main__":
    # Test Spotify MCP Server
    spotify = SpotifyMCPServer()
    
    if spotify.available:
        # Test search
        result = spotify.search_track("Blinding Lights", "The Weeknd")
        if result:
            print("Track found:")
            print(json.dumps(result, indent=2))
            
            # Get audio features
            features = spotify.get_audio_features(result['spotify_id'])
            if features:
                print("\nAudio features:")
                print(json.dumps(features, indent=2))
    else:
        print("Spotify MCP Server not available")
```

### Step 3: Spotify API Setup

Get Spotify API credentials:

1. Go to https://developer.spotify.com/dashboard
2. Create a new app
3. Copy **Client ID** and **Client Secret**
4. Set environment variables:

```bash
export SPOTIFY_CLIENT_ID="your_client_id_here"
export SPOTIFY_CLIENT_SECRET="your_client_secret_here"
```

Or add to `.env`:

```bash
# .env file
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
```

### Step 4: Create MusicBrainz Server

Create `mcp_servers/musicbrainz_server.py`:

```python
"""
MCP Server for MusicBrainz API integration.
Provides access to detailed music metadata database.
"""

import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class MusicBrainzMCPServer:
    """
    MCP Server for MusicBrainz integration.
    Access to comprehensive music metadata database.
    """
    
    def __init__(self):
        """Initialize MusicBrainz client."""
        self.available = REQUESTS_AVAILABLE
        self.base_url = "https://musicbrainz.org/ws/2"
        self.headers = {
            'User-Agent': 'MetaGoogler/1.0 (music metadata fixer)'
        }
        
        if self.available:
            logger.info("✓ MusicBrainz MCP Server initialized")
        else:
            logger.error("Requests library not available")
    
    def search_recording(
        self, 
        title: str, 
        artist: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Search for a recording in MusicBrainz.
        
        Args:
            title: Recording title
            artist: Artist name (optional)
        
        Returns:
            Recording data or None
        """
        if not self.available:
            return None
        
        try:
            # Build query
            query = f'"{title}"'
            if artist:
                query += f' AND artist:"{artist}"'
            
            # Search
            params = {
                'query': query,
                'fmt': 'json',
                'limit': 1
            }
            
            response = requests.get(
                f"{self.base_url}/recording",
                params=params,
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('recordings'):
                logger.warning(f"No recordings found for: {title}")
                return None
            
            recording = data['recordings'][0]
            
            # Extract data
            result = {
                "title": recording.get('title'),
                "mb_id": recording.get('id'),
                "length_ms": recording.get('length'),
                "isrc": recording.get('isrcs', [None])[0] if recording.get('isrcs') else None,
                "score": recording.get('score'),
            }
            
            # Get release info if available
            if recording.get('releases'):
                release = recording['releases'][0]
                result.update({
                    "album": release.get('title'),
                    "release_date": release.get('date'),
                    "country": release.get('country'),
                })
            
            # Get artist info if available
            if recording.get('artist-credit'):
                artists = [a.get('artist', {}).get('name') for a in recording['artist-credit']]
                result['artists'] = artists
            
            logger.info(f"Found recording: {result['title']}")
            return result
            
        except Exception as e:
            logger.error(f"Error searching MusicBrainz: {e}")
            return None
    
    def get_tools(self):
        """Get tool definitions for LLM."""
        return [
            {
                "name": "search_musicbrainz_recording",
                "description": "Search MusicBrainz for detailed recording metadata",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Recording title"
                        },
                        "artist": {
                            "type": "string",
                            "description": "Artist name (optional)"
                        }
                    },
                    "required": ["title"]
                }
            }
        ]


if __name__ == "__main__":
    # Test MusicBrainz MCP Server
    mb = MusicBrainzMCPServer()
    
    result = mb.search_recording("Blinding Lights", "The Weeknd")
    if result:
        print("Recording found:")
        print(json.dumps(result, indent=2))
```

---

## Phase 3: Integration

### Step 1: Create Enhanced AIManager with MCP

Update `ai_manager_v2.py` to include MCP support:

```python
# Add to imports
from mcp_servers.spotify_server import SpotifyMCPServer
from mcp_servers.musicbrainz_server import MusicBrainzMCPServer


# Add to AIManagerV2 class
def __init__(self, config_path: Optional[Path] = None, model_name: Optional[str] = None):
    # ... existing code ...
    
    # Initialize MCP servers
    self.mcp_spotify = SpotifyMCPServer()
    self.mcp_musicbrainz = MusicBrainzMCPServer()
    self.logger.info("MCP servers initialized")


def get_enhanced_suggestions(
    self, 
    filename: str, 
    current_metadata: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Get AI suggestions enhanced with real data from MCP servers.
    
    1. LLM gets basic suggestions
    2. Search Spotify for real data
    3. Enhance suggestions with actual metadata
    4. Return combined result
    """
    # Step 1: Get initial suggestions from LLM
    suggestions = self.get_ai_suggestions(filename, current_metadata)
    
    if not suggestions:
        return None
    
    # Step 2: Enrich with real data
    title = suggestions.get('title', current_metadata.get('title', ''))
    artist = suggestions.get('artist', current_metadata.get('artist', ''))
    
    # Search Spotify
    spotify_data = self.mcp_spotify.search_track(title, artist)
    
    if spotify_data:
        # Get audio features for mood/energy
        features = self.mcp_spotify.get_audio_features(spotify_data.get('spotify_id'))
        
        # Enhance suggestions
        suggestions.update({
            'album': spotify_data.get('album') or suggestions.get('album'),
            'release_date': spotify_data.get('release_date'),
            'explicit': spotify_data.get('explicit'),
            'isrc': spotify_data.get('isrc'),
            'duration_ms': spotify_data.get('duration_ms'),
        })
        
        if features:
            suggestions.update({
                'energy': features.get('energy'),
                'danceability': features.get('danceability'),
                'mood': self._classify_mood(features),
            })
    
    return suggestions


def _classify_mood(self, features: Dict[str, Any]) -> str:
    """Classify mood based on audio features."""
    valence = features.get('valence', 0.5)
    energy = features.get('energy', 0.5)
    
    if valence > 0.7 and energy > 0.7:
        return "Energetic & Happy"
    elif valence < 0.3 and energy < 0.3:
        return "Sad & Calm"
    elif energy > 0.7:
        return "Energetic"
    elif valence > 0.6:
        return "Happy"
    else:
        return "Mixed"
```

### Step 2: Test Integration

Create `test_mcp_integration.py`:

```python
#!/usr/bin/env python3
"""Test MCP + LiteLLM integration."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from ai_manager_v2 import AIManagerV2
import json
import os

def test_mcp_enhanced_suggestions():
    """Test enhanced suggestions with MCP servers."""
    print("\n" + "="*60)
    print("TEST: Enhanced Suggestions with MCP")
    print("="*60)
    
    # Check Spotify credentials
    if not os.getenv('SPOTIFY_CLIENT_ID'):
        print("⚠️  SPOTIFY_CLIENT_ID not set, skipping Spotify tests")
        print("   Set: export SPOTIFY_CLIENT_ID='....'")
        print("   Set: export SPOTIFY_CLIENT_SECRET='...'")
        return
    
    ai = AIManagerV2()
    
    # Test metadata
    metadata = {
        "title": "Blinding Lights (320)",
        "artist": "The Weeknd",
        "album": "Unknown"
    }
    
    print(f"\nSearching for: {metadata['artist']} - {metadata['title']}")
    print("Getting enhanced suggestions with MCP...")
    
    result = ai.get_enhanced_suggestions(
        "Blinding Lights (320).mp3",
        metadata
    )
    
    if result:
        print("\n✓ Enhanced suggestions:")
        print(json.dumps(result, indent=2))
    else:
        print("✗ Failed to get suggestions")


def test_spotify_direct():
    """Test Spotify MCP directly."""
    print("\n" + "="*60)
    print("TEST: Spotify MCP Direct")
    print("="*60)
    
    from mcp_servers.spotify_server import SpotifyMCPServer
    
    spotify = SpotifyMCPServer()
    
    if not spotify.available:
        print("✗ Spotify not available")
        return
    
    # Search
    result = spotify.search_track("Blinding Lights", "The Weeknd")
    
    if result:
        print("\n✓ Found track:")
        print(json.dumps(result, indent=2))
        
        # Get features
        features = spotify.get_audio_features(result['spotify_id'])
        if features:
            print("\n✓ Audio features:")
            print(json.dumps(features, indent=2))
    else:
        print("✗ Track not found")


def test_musicbrainz_direct():
    """Test MusicBrainz MCP directly."""
    print("\n" + "="*60)
    print("TEST: MusicBrainz MCP Direct")
    print("="*60)
    
    from mcp_servers.musicbrainz_server import MusicBrainzMCPServer
    
    mb = MusicBrainzMCPServer()
    
    # Search
    result = mb.search_recording("Blinding Lights", "The Weeknd")
    
    if result:
        print("\n✓ Found recording:")
        print(json.dumps(result, indent=2))
    else:
        print("✗ Recording not found")


if __name__ == "__main__":
    print("MCP + LiteLLM Integration Tests")
    
    test_spotify_direct()
    test_musicbrainz_direct()
    test_mcp_enhanced_suggestions()
    
    print("\n" + "="*60)
    print("Tests completed!")
    print("="*60)
```

Run:

```bash
# Set Spotify credentials first
export SPOTIFY_CLIENT_ID='your_id'
export SPOTIFY_CLIENT_SECRET='your_secret'

python3 test_mcp_integration.py
```

---

## Testing & Validation

### Test Checklist

```bash
# 1. Test LiteLLM with Ollama
python3 test_litellm.py

# 2. Test model switching
python3 -c "
from ai_manager_v2 import AIManagerV2
ai = AIManagerV2()
print('Current model:', ai.model_name)
ai.switch_model('ollama/llama2')
print('Switched to:', ai.model_name)
"

# 3. Test Spotify MCP
export SPOTIFY_CLIENT_ID='...'
export SPOTIFY_CLIENT_SECRET='...'
python3 test_mcp_integration.py

# 4. Test MusicBrainz MCP
python3 -c "
from mcp_servers.musicbrainz_server import MusicBrainzMCPServer
mb = MusicBrainzMCPServer()
result = mb.search_recording('Blinding Lights', 'The Weeknd')
print(result)
"

# 5. Test with GUI
python3 app_gui.py
```

---

## Troubleshooting

### LiteLLM Issues

**Problem: "Model not found"**
```bash
# Check if Ollama is running
ollama serve

# In another terminal, check available models
ollama list

# If Mistral not downloaded, pull it
ollama pull mistral
```

**Problem: "API key not found"**
```bash
# Set API keys
export OPENAI_API_KEY='sk-...'
export ANTHROPIC_API_KEY='sk-ant-...'

# Verify
python3 -c "import os; print(os.getenv('OPENAI_API_KEY'))"
```

### MCP Issues

**Problem: "Spotify MCP not available"**
```bash
# Check credentials
echo $SPOTIFY_CLIENT_ID
echo $SPOTIFY_CLIENT_SECRET

# If empty, set them
export SPOTIFY_CLIENT_ID='your_id'
export SPOTIFY_CLIENT_SECRET='your_secret'

# Install spotipy
pip install spotipy
```

**Problem: "MusicBrainz timeout"**
```bash
# MusicBrainz has rate limiting
# Add delay between requests:
import time
time.sleep(1)  # Wait 1 second between requests
```

### Performance Issues

**Problem: "Requests are slow"**
```python
# Add caching:
from functools import lru_cache

@lru_cache(maxsize=128)
def get_spotify_data(title, artist):
    # Only call Spotify if not cached
    ...
```

---

## Summary

### Migration Timeline

- **Day 1**: Install LiteLLM + update AIManager (Phase 1)
- **Day 2**: Test local models + try cloud models (GPT-4, Claude)
- **Day 3-4**: Set up Spotify + MusicBrainz APIs
- **Day 5**: Integrate MCP servers with LLM (Phase 2-3)
- **Day 6-7**: Testing & optimization

### Key Files Created

- `ai_manager_v2.py` - LiteLLM integration
- `mcp_servers/spotify_server.py` - Spotify API access
- `mcp_servers/musicbrainz_server.py` - MusicBrainz API access
- `test_litellm.py` - LiteLLM tests
- `test_mcp_integration.py` - MCP tests

### Next Steps

1. ✅ Start with Phase 1 (LiteLLM)
2. ✅ Test model switching
3. ✅ Compare results: Ollama vs GPT-4 vs Claude
4. ✅ Pick best provider for quality/cost
5. ✅ Add MCP servers for real data
6. ✅ Optimize caching and performance

---

## Questions?

Each section is independent - you can:
- Use just LiteLLM (no MCP)
- Use MCP without cloud models
- Combine both for best results

Let me know which phase you want to start with!
