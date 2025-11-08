"""
AIManager v2: LiteLLM-based AI model management
Supports multiple LLM providers with unified interface.
Backward compatible with existing code.

Usage:
    from ai_manager_v2 import AIManager
    ai = AIManager()
    suggestions = ai.get_ai_suggestions(filename, metadata)
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

# LiteLLM imports
try:
    from litellm import completion
    import litellm
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    print("ERROR: LiteLLM not installed. Install with: pip install litellm")


# Configure logging
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
        if not LITELLM_AVAILABLE:
            raise ImportError("LiteLLM not installed. Install with: pip install litellm")
        
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
        
        self.logger.debug(f"Temperature: {self.temperature}, Max tokens: {self.max_tokens}")
    
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
            
            # Extract response text
            response_text = response['choices'][0]['message']['content']
            
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
                    try:
                        suggestions = json.loads(json_match.group())
                        return suggestions
                    except:
                        pass
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

Return ONLY valid JSON in this exact format:
{{
    "title": "suggested title",
    "artist": "suggested artist",
    "album": "suggested album",
    "genre": "suggested genre",
    "date": "YYYY-MM-DD or YYYY",
    "confidence": 0.85,
    "notes": "explanation of changes"
}}

Be accurate and conservative - only suggest changes you're confident about.
Do not include any text outside the JSON object."""
        
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
            # Local (Ollama) - Free
            "ollama/mistral",
            "ollama/llama2",
            "ollama/neural-chat",
            "ollama/openchat",
            
            # OpenAI - Paid
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            
            # Anthropic - Paid
            "claude-3-opus",
            "claude-3-sonnet",
            "claude-3-haiku",
            
            # Google - Free tier available
            "gemini-pro",
            
            # HuggingFace - Various
            "huggingface/meta-llama/Llama-2-7b",
        ]
        return models
    
    def get_model_info(self, model_name: str) -> Dict[str, str]:
        """Get information about a specific model."""
        info = {
            "ollama/mistral": "Local, fast, good quality. Requires Ollama running.",
            "gpt-4": "Cloud, expensive, very high quality. Requires OpenAI API key.",
            "claude-3-sonnet": "Cloud, moderate cost, excellent quality. Requires Anthropic API key.",
            "gemini-pro": "Cloud, free tier available, good quality. Requires Google API key.",
        }
        return info.get(model_name, "Model information not available")


# Backward compatibility: keep old interface
class AIManager(AIManagerV2):
    """Backward compatible AIManager - inherits from AIManagerV2"""
    pass


if __name__ == "__main__":
    # Test script
    import sys
    
    print("="*60)
    print("AIManager v2 (LiteLLM) - Test Script")
    print("="*60)
    
    # Initialize
    try:
        ai = AIManagerV2()
    except ImportError as e:
        print(f"ERROR: {e}")
        print("\nInstall LiteLLM with:")
        print("  pip install litellm")
        sys.exit(1)
    
    # Test connection
    print(f"\nCurrent model: {ai.model_name}")
    print("Testing connection...")
    
    if ai.test_connection():
        print("✓ Connection successful\n")
        
        # Test suggestions
        metadata = {
            "title": "Blinding Lights (320)",
            "artist": "The Weeknd",
            "album": "After Hours",
            "genre": "Unknown"
        }
        
        print("Getting AI suggestions...")
        result = ai.get_ai_suggestions(
            "Blinding Lights (320).mp3",
            metadata
        )
        
        if result:
            print("✓ Suggestions received:")
            print(json.dumps(result, indent=2))
        else:
            print("✗ Failed to get suggestions")
    else:
        print("✗ Connection failed")
        print("\nTroubleshooting:")
        print("  - For Ollama: Make sure 'ollama serve' is running")
        print("  - For GPT-4: Set OPENAI_API_KEY environment variable")
        print("  - For Claude: Set ANTHROPIC_API_KEY environment variable")
    
    # List available models
    print("\n" + "="*60)
    print("Available Models:")
    print("="*60)
    for model in ai.list_available_models():
        print(f"  • {model}")
