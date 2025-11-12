"""Utilities for handling Playwright availability."""
import logging
from typing import Union, Tuple, Any
from importlib import import_module
from types import ModuleType

logger = logging.getLogger(__name__)

def get_playwright() -> Tuple[ModuleType, bool]:
    """Get Playwright module or fallback mock implementation.
    
    Returns:
        Tuple containing:
        - Playwright module (real or mock)
        - Boolean indicating if real Playwright is being used
    """
    try:
        # Try to import real Playwright first
        playwright = import_module("playwright.async_api")
        logger.info("Using real Playwright for browser automation")
        return playwright, True
    except ImportError:
        try:
            playwright_sync = import_module("playwright.sync_api")
            logger.info("Using real Playwright (sync) for browser automation")
            return playwright_sync, True
        except ImportError:
            # Fall back to mock implementation
            from . import playwright_mock
            logger.warning("Playwright not available, using mock implementation")
            return playwright_mock, False

# Global instance
playwright_module, is_real_playwright = get_playwright()