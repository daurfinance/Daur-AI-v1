#!/usr/bin/env python3
"""
Simple launcher for Daur-AI.
This is the main entry point for the application.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add the project root to Python path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

from src.agent.core import DaurAgent
from config.simple_config import DEFAULT_CONFIG

def setup_logging(debug: bool = False):
    """Setup basic logging configuration."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Daur-AI: Universal AI Agent")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--model", choices=["simple", "enhanced", "ollama"],
                      default="simple", help="AI model to use")
    parser.add_argument("--input", choices=["simple", "advanced"],
                      default="simple", help="Input controller mode")
    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    # Update config based on arguments
    config = DEFAULT_CONFIG.copy()
    config["ai"]["model"] = args.model
    config["input"]["mode"] = args.input
    config["system"]["debug"] = args.debug
    
    try:
        # Create and run agent
        agent = DaurAgent(config)
        logger.info("Starting Daur-AI agent...")
        agent.run()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()