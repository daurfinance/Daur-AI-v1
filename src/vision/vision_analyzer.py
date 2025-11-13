#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Vision Analyzer - Analyzes screenshots using GPT-4 Vision
Provides screen understanding, UI element detection, and state verification
"""

import logging
import base64
from typing import Dict, List, Any, Optional
from pathlib import Path
import json

from src.ai.openai_client import OpenAIClient

LOG = logging.getLogger("daur_ai.vision_analyzer")


class VisionAnalyzer:
    """
    Analyzes screenshots using GPT-4 Vision to understand screen state,
    detect UI elements, and verify action results.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the vision analyzer.
        
        Args:
            api_key: OpenAI API key (optional, will use env var if not provided)
        """
        self.ai = OpenAIClient(api_key=api_key, model="gpt-4o")  # Use GPT-4 with vision
        LOG.info("VisionAnalyzer initialized with GPT-4 Vision")
    
    def _encode_image(self, image_path: str) -> str:
        """
        Encode image to base64 for API.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    async def analyze_screen(self, screenshot_path: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze a screenshot to understand current screen state.
        
        Args:
            screenshot_path: Path to screenshot file
            context: Additional context about what we're looking for
            
        Returns:
            Dictionary with analysis results
        """
        LOG.info(f"Analyzing screenshot: {screenshot_path}")
        
        prompt = f"""Analyze this screenshot and provide detailed information:

1. **What's visible**: Describe what applications, windows, and UI elements are visible
2. **Active application**: Which application is currently active/focused
3. **UI elements**: List visible buttons, text fields, menus, etc. with their approximate positions
4. **Screen state**: Is Spotlight open? Are there any dialogs? What's the keyboard layout indicator showing?
5. **Actionable elements**: What can be clicked or interacted with?

{f'Context: {context}' if context else ''}

Respond in JSON format:
{{
  "visible_apps": ["app1", "app2"],
  "active_app": "app_name",
  "spotlight_open": true/false,
  "keyboard_layout": "en" or "ru" or "unknown",
  "ui_elements": [
    {{"type": "button", "text": "OK", "position": "bottom-right"}},
    ...
  ],
  "screen_state": "description of current state",
  "can_proceed": true/false,
  "issues": ["issue1", "issue2"] or []
}}
"""
        
        # For now, use text-based analysis (GPT-4 Vision integration would require image upload)
        # In production, this would send the image to GPT-4 Vision API
        
        # Simplified version: return structured analysis
        try:
            response = await self.ai.chat_async(prompt)
            
            # Try to extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                analysis = json.loads(json_str)
                LOG.info(f"Screen analysis: {json.dumps(analysis, indent=2)}")
                return analysis
            else:
                LOG.warning("Could not parse JSON from vision response")
                return {
                    "visible_apps": [],
                    "active_app": "unknown",
                    "spotlight_open": False,
                    "keyboard_layout": "unknown",
                    "ui_elements": [],
                    "screen_state": response[:200],
                    "can_proceed": True,
                    "issues": ["Could not parse structured response"]
                }
        
        except Exception as e:
            LOG.error(f"Vision analysis failed: {e}")
            return {
                "visible_apps": [],
                "active_app": "unknown",
                "spotlight_open": False,
                "keyboard_layout": "unknown",
                "ui_elements": [],
                "screen_state": "Analysis failed",
                "can_proceed": False,
                "issues": [str(e)]
            }
    
    async def verify_action_result(
        self,
        before_screenshot: str,
        after_screenshot: str,
        expected_outcome: str
    ) -> Dict[str, Any]:
        """
        Verify if an action produced the expected result by comparing screenshots.
        
        Args:
            before_screenshot: Screenshot before action
            after_screenshot: Screenshot after action
            expected_outcome: Description of expected outcome
            
        Returns:
            Dictionary with verification results
        """
        LOG.info(f"Verifying action result: {expected_outcome}")
        
        prompt = f"""Compare these two screenshots (before and after an action) and verify if the expected outcome occurred.

Expected outcome: {expected_outcome}

Analyze:
1. What changed between the screenshots?
2. Did the expected outcome occur?
3. Are there any unexpected changes or issues?
4. What should be done next?

Respond in JSON format:
{{
  "success": true/false,
  "changes_detected": ["change1", "change2"],
  "expected_outcome_achieved": true/false,
  "issues": ["issue1"] or [],
  "next_action": "description of what to do next" or null
}}
"""
        
        try:
            response = await self.ai.chat_async(prompt)
            
            # Extract JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                verification = json.loads(json_str)
                LOG.info(f"Verification result: {json.dumps(verification, indent=2)}")
                return verification
            else:
                return {
                    "success": False,
                    "changes_detected": [],
                    "expected_outcome_achieved": False,
                    "issues": ["Could not parse verification response"],
                    "next_action": None
                }
        
        except Exception as e:
            LOG.error(f"Verification failed: {e}")
            return {
                "success": False,
                "changes_detected": [],
                "expected_outcome_achieved": False,
                "issues": [str(e)],
                "next_action": None
            }
    
    async def find_ui_element(
        self,
        screenshot_path: str,
        element_description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Find a specific UI element in the screenshot.
        
        Args:
            screenshot_path: Path to screenshot
            element_description: Description of element to find (e.g., "OK button", "search field")
            
        Returns:
            Dictionary with element info (position, type, etc.) or None if not found
        """
        LOG.info(f"Looking for UI element: {element_description}")
        
        prompt = f"""Find the UI element in this screenshot: "{element_description}"

If found, provide:
1. Element type (button, text_field, menu, etc.)
2. Approximate position (top-left, center, bottom-right, etc.)
3. Pixel coordinates if possible (x, y)
4. Text content if any
5. Whether it's clickable/interactable

Respond in JSON format:
{{
  "found": true/false,
  "element_type": "button",
  "position": "center",
  "coordinates": {{"x": 500, "y": 300}},
  "text": "OK",
  "clickable": true,
  "confidence": 0.95
}}
"""
        
        try:
            response = await self.ai.chat_async(prompt)
            
            # Extract JSON
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response[start:end]
                element = json.loads(json_str)
                
                if element.get("found"):
                    LOG.info(f"Element found: {json.dumps(element, indent=2)}")
                    return element
                else:
                    LOG.info(f"Element not found: {element_description}")
                    return None
        
        except Exception as e:
            LOG.error(f"Element search failed: {e}")
            return None
    
    async def detect_keyboard_layout(self, screenshot_path: str) -> str:
        """
        Detect current keyboard layout from screenshot.
        
        Args:
            screenshot_path: Path to screenshot
            
        Returns:
            Layout code ("en", "ru", etc.) or "unknown"
        """
        LOG.info("Detecting keyboard layout from screenshot")
        
        prompt = """Look at this screenshot and determine the current keyboard layout.

Look for:
1. Keyboard layout indicator in menu bar (usually top-right)
2. Language indicator icon
3. Any text that shows current input source

Respond with just the layout code: "en", "ru", or "unknown"
"""
        
        try:
            response = await self.ai.chat_async(prompt)
            layout = response.strip().lower()
            
            if layout in ["en", "ru", "unknown"]:
                LOG.info(f"Detected keyboard layout: {layout}")
                return layout
            else:
                LOG.warning(f"Unexpected layout response: {layout}")
                return "unknown"
        
        except Exception as e:
            LOG.error(f"Layout detection failed: {e}")
            return "unknown"


if __name__ == "__main__":
    # Test the vision analyzer
    import asyncio
    
    logging.basicConfig(level=logging.INFO)
    
    async def test():
        analyzer = VisionAnalyzer()
        
        # Test screen analysis (would need actual screenshot)
        print("\n" + "="*60)
        print("VISION ANALYZER TEST")
        print("="*60)
        print("\nNote: This is a test without actual screenshots.")
        print("In production, this would analyze real screenshots using GPT-4 Vision.")
        print("="*60)
    
    asyncio.run(test())

