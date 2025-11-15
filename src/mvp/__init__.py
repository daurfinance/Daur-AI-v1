"""
Daur AI MVP - Autonomous AI Agent with Local LLM
"""

from .core.mvp_agent import get_mvp_agent, MVPAgent
from .core.ollama_client import get_ollama_client, OllamaClient
from .core.input_controller import get_input_controller, InputController
from .vision.screen_analyzer import get_screen_analyzer, ScreenAnalyzer
from .vision.ocr_engine import get_ocr_engine, OCREngine
from .vision.accessibility import get_accessibility_api, AccessibilityAPI

__version__ = "0.1.0"

__all__ = [
    'get_mvp_agent',
    'MVPAgent',
    'get_ollama_client',
    'OllamaClient',
    'get_input_controller',
    'InputController',
    'get_screen_analyzer',
    'ScreenAnalyzer',
    'get_ocr_engine',
    'OCREngine',
    'get_accessibility_api',
    'AccessibilityAPI',
]

