#!/usr/bin/env python3
"""
American Buddha Asset Namer
Main application entry point
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window_basic import AssetNamerApp
from utils.logger import setup_logger
from utils.config import Config

def main():
    """Main application entry point"""
    # Load environment variables
    load_dotenv()
    
    # Setup logging
    logger = setup_logger()
    logger.info("Starting American Buddha Asset Namer")
    
    # Load configuration
    config = Config()
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        logger.warning("No valid OpenAI API key found. AI features will be limited.")
    
    # Create and run the application
    try:
        app = AssetNamerApp(config)
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()