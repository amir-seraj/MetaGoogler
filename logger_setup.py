"""
Logger Setup: Configures centralized logging for the entire application.
Logs to both console and file with appropriate formatting and levels.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
from config_manager import ConfigManager


class LoggerSetup:
    """Sets up and configures application-wide logging."""
    
    _loggers = {}  # Cache for logger instances
    
    @staticmethod
    def setup(name: str = "MetaFixer", log_file: Optional[str] = None) -> logging.Logger:
        """
        Setup logger for the application or a specific module.
        
        Args:
            name: Logger name (typically module name)
            log_file: Optional override for log file path
        
        Returns:
            Configured logger instance
        """
        # Return cached logger if already set up
        if name in LoggerSetup._loggers:
            return LoggerSetup._loggers[name]
        
        try:
            config = ConfigManager()
        except Exception:
            # Fallback to defaults if config not available
            config = None
        
        # Get configuration or use defaults
        log_level = config.get_logging_level() if config else "INFO"
        log_file = log_file or (config.get_log_file() if config else "fixer.log")
        console_format = config.get_logging_format("console") if config else "%(asctime)s - %(levelname)s - %(message)s"
        file_format = config.get_logging_format("file") if config else "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        
        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level))
        logger.propagate = False
        
        # Clear existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
        console_formatter = logging.Formatter(console_format)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler with rotation
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_path,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)  # File always gets DEBUG level
            file_formatter = logging.Formatter(file_format)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not set up file logging: {e}")
        
        LoggerSetup._loggers[name] = logger
        return logger


def get_logger(name: str = "MetaFixer") -> logging.Logger:
    """
    Get or create a logger with the given name.
    
    Example:
        logger = get_logger("song_metadata_fixer")
        logger.info("Starting metadata fix")
    """
    if name not in LoggerSetup._loggers:
        LoggerSetup.setup(name)
    return LoggerSetup._loggers[name]


# Set up root logger on import
_root_logger = LoggerSetup.setup("MetaFixer")
