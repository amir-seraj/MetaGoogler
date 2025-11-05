"""
AIManager: Encapsulates all LLM operations and model management.
Handles model checking, downloading, loading, and prompt execution.
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import urllib.request
import os


class AIManager:
    """Manages AI model lifecycle: detection, download, loading, and inference."""
    
    def __init__(self, config_path: Path = None):
        """
        Initialize AIManager with configuration.
        
        Args:
            config_path: Path to config.json file. If None, uses default location.
        """
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.model_name = self.config["ai_model"]["name"]
        self.model_path = Path(self.config["ai_model"]["model_path"])
        self.model_loaded = False
        self.model = None
    
    def _load_config(self, config_path: Optional[Path] = None) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if config_path is None:
            config_path = Path(__file__).parent / "config.json"
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            self.logger.debug(f"Loaded config from {config_path}")
            return config
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {config_path}")
            raise
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in config file: {config_path}")
            raise
    
    def model_exists(self) -> bool:
        """Check if the AI model is already downloaded locally."""
        if self.model_path.exists():
            self.logger.debug(f"Model found at {self.model_path}")
            return True
        self.logger.debug(f"Model not found at {self.model_path}")
        return False
    
    def download_model(self) -> bool:
        """
        Download the AI model if it doesn't exist.
        
        Returns:
            True if model is available (either already existed or was downloaded)
            False if download failed
        """
        if self.model_exists():
            self.logger.info("Model already available locally")
            return True
        
        self.logger.info(f"Downloading model: {self.model_name}")
        self.model_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # For Ollama-based models, we pull them instead of downloading
            result = subprocess.run(
                ["ollama", "pull", self.model_name],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully downloaded model: {self.model_name}")
                return True
            else:
                self.logger.error(f"Failed to download model. Output: {result.stderr}")
                return False
                
        except FileNotFoundError:
            self.logger.error("Ollama not found. Please install Ollama first.")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("Model download timed out")
            return False
        except Exception as e:
            self.logger.error(f"Error downloading model: {e}")
            return False
    
    def load_model(self) -> bool:
        """
        Load the AI model into memory.
        
        Returns:
            True if model loaded successfully, False otherwise
        """
        if self.model_loaded:
            self.logger.debug("Model already loaded")
            return True
        
        if not self.model_exists():
            if not self.download_model():
                self.logger.error("Failed to prepare model")
                return False
        
        try:
            # For Ollama, we don't need to explicitly load - it handles this
            # But we can verify it's available
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and self.model_name in result.stdout:
                self.model_loaded = True
                self.logger.info(f"Model {self.model_name} is available")
                return True
            else:
                self.logger.error(f"Model {self.model_name} not found in Ollama")
                return False
                
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            return False
    
    def prompt(self, prompt_text: str, json_mode: bool = True) -> Optional[Dict[str, Any]]:
        """
        Send a prompt to the model and get a response.
        
        Args:
            prompt_text: The prompt to send to the model
            json_mode: If True, attempt to parse response as JSON
        
        Returns:
            Parsed JSON response if json_mode=True and parsing succeeds
            Raw text response if json_mode=False
            None if error occurred
        """
        if not self.load_model():
            self.logger.error("Failed to load model for inference")
            return None
        
        try:
            self.logger.debug(f"Sending prompt to model: {self.model_name}")
            
            result = subprocess.run(
                ["ollama", "run", self.model_name, prompt_text],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.logger.error(f"Model inference failed: {result.stderr}")
                return None
            
            response_text = result.stdout.strip()
            
            if json_mode:
                try:
                    # Try to parse as JSON
                    response_json = json.loads(response_text)
                    self.logger.debug("Successfully parsed JSON response")
                    return response_json
                except json.JSONDecodeError:
                    self.logger.warning("Failed to parse response as JSON. Returning raw text.")
                    return {"raw_response": response_text}
            
            return {"response": response_text}
            
        except subprocess.TimeoutExpired:
            self.logger.error("Model inference timed out")
            return None
        except Exception as e:
            self.logger.error(f"Error during model inference: {e}")
            return None
    
    def fix_metadata_with_ai(self, metadata_text: str) -> Optional[Dict[str, Any]]:
        """
        Use AI to fix and enhance metadata.
        
        Args:
            metadata_text: Current metadata as text
        
        Returns:
            Fixed metadata as dictionary, or None if failed
        """
        prompt = f"""Analyze and fix the following song metadata. Return ONLY valid JSON with corrected values:

Metadata:
{metadata_text}

Return JSON with keys: artist, title, album, year, and any issues found.
Fix common issues like extra spaces, invalid years, missing values.
"""
        
        self.logger.debug("Requesting AI metadata fix")
        return self.prompt(prompt, json_mode=True)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the AI manager."""
        return {
            "model_name": self.model_name,
            "model_path": str(self.model_path),
            "model_exists": self.model_exists(),
            "model_loaded": self.model_loaded,
            "config_loaded": self.config is not None
        }
