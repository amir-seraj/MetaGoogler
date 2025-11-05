"""
ConfigManager: Handles loading and accessing configuration with caching.
Provides a single source of truth for all application settings.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConfigManager:
    """Manages application configuration from config.json."""
    
    _instance = None  # Singleton pattern
    _config = None
    
    def __new__(cls, config_path: Optional[Path] = None):
        """Implement singleton pattern - only one config instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize ConfigManager with configuration file."""
        if self._initialized:
            return
        
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or (Path(__file__).parent / "config.json")
        self._config = self._load_config()
        self._initialized = True
        self.logger.debug(f"ConfigManager initialized with {self.config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load and parse configuration JSON file."""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            self.logger.debug(f"Successfully loaded config from {self.config_path}")
            return config
        except FileNotFoundError:
            self.logger.error(f"Config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in config file: {self.config_path} - {e}")
            raise
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Example:
            config.get("cover_art.max_size_kb")  # Returns 500
            config.get("supported_formats")       # Returns list
            config.get("nonexistent.key", [])    # Returns default []
        
        Args:
            key_path: Dot-separated path to config key
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self._config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            self.logger.debug(f"Config key not found: {key_path}, using default")
            return default
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported audio formats."""
        return self.get("supported_formats", [])
    
    def get_max_cover_size_kb(self) -> int:
        """Get maximum cover art size in kilobytes."""
        return self.get("cover_art.max_size_kb", 500)
    
    def get_max_cover_dimensions(self) -> tuple:
        """Get maximum cover art dimensions (width, height) in pixels."""
        width = self.get("cover_art.max_width_px", 3000)
        height = self.get("cover_art.max_height_px", 3000)
        return (width, height)
    
    def get_allowed_cover_formats(self) -> List[str]:
        """Get list of allowed image formats for covers."""
        return self.get("cover_art.allowed_formats", ["jpeg", "jpg", "png"])
    
    def get_ai_model_name(self) -> str:
        """Get AI model name."""
        return self.get("ai_model.name", "phi3")
    
    def get_ai_model_path(self) -> Path:
        """Get AI model local path."""
        return Path(self.get("ai_model.model_path", "./models/phi3"))
    
    def get_logging_level(self) -> str:
        """Get logging level."""
        return self.get("logging.level", "INFO")
    
    def get_log_file(self) -> str:
        """Get log file name."""
        return self.get("logging.log_file", "fixer.log")
    
    def get_logging_format(self, target: str = "console") -> str:
        """Get logging format for console or file."""
        if target == "file":
            return self.get("logging.file_format", 
                          "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        return self.get("logging.console_format",
                       "%(asctime)s - %(levelname)s - %(message)s")
    
    def reload(self):
        """Reload configuration from file (useful for testing)."""
        self._config = self._load_config()
        self.logger.info("Configuration reloaded")
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary."""
        return self._config.copy()
    
    def dump(self) -> str:
        """Get configuration as formatted JSON string (for logging/debugging)."""
        return json.dumps(self._config, indent=2)


# Convenience function for quick access
def get_config(key_path: str, default: Any = None) -> Any:
    """Quick access to configuration without managing singleton."""
    config = ConfigManager()
    return config.get(key_path, default)
