#!/usr/bin/env python3
"""
Meta-Googler: Song Metadata Management System
Main entry point for the application

Usage:
    python -m src.main              # Launch GUI
    meta-googler                    # Launch GUI (after installation)
"""

import sys
import logging
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from utils.logger_setup import setup_logging
from app_gui import MetadataEditorGUI


def main():
    """Main entry point for the application."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 70)
    logger.info("🎵 Meta-Googler: Song Metadata Management System")
    logger.info("=" * 70)
    
    try:
        # Launch GUI
        logger.info("Launching GUI...")
        app = MetadataEditorGUI()
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
