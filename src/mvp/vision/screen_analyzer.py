"""
Screen Analyzer - Hybrid Vision System
Combines OCR, Accessibility API, and Local Vision models for free screen analysis
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import time

from .ocr_engine import get_ocr_engine
from .accessibility import get_accessibility_api
from ..core.ollama_client import get_ollama_client

logger = logging.getLogger(__name__)


class ScreenAnalyzer:
    """
    Hybrid screen analysis using multiple free methods:
    1. Accessibility API (90%) - Fast, accurate, free
    2. OCR (9%) - When accessibility fails
    3. Local Vision Model (0.9%) - For complex visual understanding
    4. Fallback to cloud vision (0.1%) - Only if critical and all else fails
    """
    
    def __init__(self):
        """Initialize screen analyzer with all vision methods"""
        self.ocr = get_ocr_engine()
        self.accessibility = get_accessibility_api()
        self.llm = get_ollama_client()
        
        # Statistics
        self.stats = {
            'accessibility_used': 0,
            'ocr_used': 0,
            'vision_model_used': 0,
            'total_analyses': 0
        }
        
        logger.info("Screen analyzer initialized with hybrid vision system")
    
    def analyze_screen(
        self,
        screenshot_path: str,
        task: Optional[str] = None,
        use_vision_model: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze screen using best available method
        
        Args:
            screenshot_path: Path to screenshot image
            task: Optional task description for context
            use_vision_model: Force use of vision model
            
        Returns:
            Analysis result with:
            - app_name: Active application
            - window_title: Window title
            - ui_elements: List of UI elements
            - text_content: Extracted text
            - buttons: List of detected buttons
            - method_used: Which method was used
        """
        self.stats['total_analyses'] += 1
        start_time = time.time()
        
        result = {
            'app_name': '',
            'window_title': '',
            'ui_elements': [],
            'text_content': '',
            'buttons': [],
            'method_used': '',
            'analysis_time': 0
        }
        
        # Method 1: Try Accessibility API first (fastest and most reliable)
        if self.accessibility.is_available():
            try:
                result['app_name'] = self.accessibility.get_frontmost_app()
                result['window_title'] = self.accessibility.get_window_title()
                result['ui_elements'] = self.accessibility.get_ui_elements()
                
                # If we got good data, we're done
                if result['app_name']:
                    result['method_used'] = 'accessibility_api'
                    self.stats['accessibility_used'] += 1
                    result['analysis_time'] = time.time() - start_time
                    
                    logger.info(f"Screen analyzed via Accessibility API in {result['analysis_time']:.2f}s")
                    return result
            except Exception as e:
                logger.warning(f"Accessibility API failed: {e}")
        
        # Method 2: Try OCR (slower but works when accessibility fails)
        if self.ocr.is_available():
            try:
                result['text_content'] = self.ocr.extract_text(screenshot_path)
                result['buttons'] = self.ocr.extract_buttons(screenshot_path)
                
                if result['text_content'] or result['buttons']:
                    result['method_used'] = 'ocr'
                    self.stats['ocr_used'] += 1
                    result['analysis_time'] = time.time() - start_time
                    
                    logger.info(f"Screen analyzed via OCR in {result['analysis_time']:.2f}s")
                    return result
            except Exception as e:
                logger.warning(f"OCR failed: {e}")
        
        # Method 3: Use local vision model (slowest but most capable)
        if use_vision_model:
            try:
                prompt = "Describe what you see on this screen. List all visible UI elements, buttons, text, and their approximate locations."
                
                if task:
                    prompt += f"\n\nContext: The user wants to {task}"
                
                vision_analysis = self.llm.analyze_image(
                    image_path=screenshot_path,
                    prompt=prompt
                )
                
                if vision_analysis:
                    result['text_content'] = vision_analysis
                    result['method_used'] = 'vision_model'
                    self.stats['vision_model_used'] += 1
                    result['analysis_time'] = time.time() - start_time
                    
                    logger.info(f"Screen analyzed via Vision Model in {result['analysis_time']:.2f}s")
                    return result
            except Exception as e:
                logger.warning(f"Vision model failed: {e}")
        
        # If all methods failed
        result['method_used'] = 'failed'
        result['analysis_time'] = time.time() - start_time
        logger.error("All screen analysis methods failed")
        
        return result
    
    def find_element(
        self,
        screenshot_path: str,
        element_description: str,
        element_type: str = 'button'
    ) -> Optional[Tuple[int, int]]:
        """
        Find UI element and return its coordinates
        
        Args:
            screenshot_path: Path to screenshot
            element_description: Text or description of element
            element_type: Type of element ('button', 'text_field', etc.)
            
        Returns:
            (x, y) coordinates of element center, or None if not found
        """
        # Try Accessibility API first
        if self.accessibility.is_available() and element_type == 'button':
            coords = self.accessibility.find_button(element_description)
            if coords:
                logger.info(f"Found element via Accessibility API: {coords}")
                return coords
        
        # Try OCR
        if self.ocr.is_available():
            coords = self.ocr.find_text(screenshot_path, element_description)
            if coords:
                logger.info(f"Found element via OCR: {coords}")
                return coords
        
        # Try vision model as last resort
        try:
            prompt = f"Find the {element_type} with text '{element_description}' on this screen. Return its approximate center coordinates as 'x,y' (e.g., '500,300'). Only return the coordinates, nothing else."
            
            response = self.llm.analyze_image(
                image_path=screenshot_path,
                prompt=prompt
            )
            
            # Parse coordinates from response
            if ',' in response:
                parts = response.strip().split(',')
                if len(parts) == 2:
                    try:
                        x = int(parts[0].strip())
                        y = int(parts[1].strip())
                        coords = (x, y)
                        logger.info(f"Found element via Vision Model: {coords}")
                        return coords
                    except ValueError:
                        pass
        except Exception as e:
            logger.warning(f"Vision model element search failed: {e}")
        
        logger.warning(f"Element '{element_description}' not found")
        return None
    
    def extract_text(self, screenshot_path: str) -> str:
        """
        Extract all text from screenshot
        
        Args:
            screenshot_path: Path to screenshot
            
        Returns:
            Extracted text
        """
        # OCR is best for text extraction
        if self.ocr.is_available():
            return self.ocr.extract_text(screenshot_path)
        
        # Fallback to vision model
        try:
            prompt = "Extract all visible text from this screen. Return only the text, no descriptions."
            return self.llm.analyze_image(screenshot_path, prompt)
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""
    
    def understand_screen(
        self,
        screenshot_path: str,
        question: str
    ) -> str:
        """
        Answer questions about screen content using vision model
        
        Args:
            screenshot_path: Path to screenshot
            question: Question about the screen
            
        Returns:
            Answer
        """
        try:
            return self.llm.analyze_image(screenshot_path, question)
        except Exception as e:
            logger.error(f"Screen understanding failed: {e}")
            return ""
    
    def get_current_app_info(self) -> Dict[str, str]:
        """
        Get information about currently active application
        
        Returns:
            Dict with app_name and window_title
        """
        if self.accessibility.is_available():
            return {
                'app_name': self.accessibility.get_frontmost_app(),
                'window_title': self.accessibility.get_window_title()
            }
        return {'app_name': '', 'window_title': ''}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get usage statistics
        
        Returns:
            Statistics dict
        """
        total = self.stats['total_analyses']
        if total == 0:
            return self.stats
        
        return {
            **self.stats,
            'accessibility_percentage': (self.stats['accessibility_used'] / total) * 100,
            'ocr_percentage': (self.stats['ocr_used'] / total) * 100,
            'vision_model_percentage': (self.stats['vision_model_used'] / total) * 100
        }


# Singleton instance
_screen_analyzer: Optional[ScreenAnalyzer] = None


def get_screen_analyzer() -> ScreenAnalyzer:
    """Get singleton screen analyzer instance"""
    global _screen_analyzer
    if _screen_analyzer is None:
        _screen_analyzer = ScreenAnalyzer()
    return _screen_analyzer

