"""
Accessibility API - macOS UI Element Detection
Uses macOS Accessibility API for fast, free, and reliable UI element detection
"""

import logging
from typing import List, Dict, Optional, Tuple
import subprocess
import json

logger = logging.getLogger(__name__)


class AccessibilityAPI:
    """
    macOS Accessibility API wrapper
    
    Uses AppleScript and system accessibility features to:
    - Get UI element hierarchy
    - Find buttons, text fields, menus
    - Get element positions and properties
    - Interact with UI elements
    """
    
    def __init__(self):
        """Initialize Accessibility API"""
        self.available = self._check_availability()
        
        if self.available:
            logger.info("Accessibility API initialized")
        else:
            logger.warning("Accessibility API not available (macOS only)")
    
    def _check_availability(self) -> bool:
        """Check if running on macOS"""
        try:
            result = subprocess.run(
                ['uname', '-s'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip() == 'Darwin'
        except Exception:
            return False
    
    def _run_applescript(self, script: str) -> str:
        """
        Execute AppleScript and return output
        
        Args:
            script: AppleScript code
            
        Returns:
            Script output
        """
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"AppleScript error: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"Failed to run AppleScript: {e}")
            return ""
    
    def get_frontmost_app(self) -> str:
        """
        Get name of frontmost (active) application
        
        Returns:
            Application name
        """
        script = '''
        tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            return frontApp
        end tell
        '''
        
        app_name = self._run_applescript(script)
        logger.debug(f"Frontmost app: {app_name}")
        return app_name
    
    def get_window_title(self, app_name: Optional[str] = None) -> str:
        """
        Get title of frontmost window
        
        Args:
            app_name: Application name (uses frontmost if None)
            
        Returns:
            Window title
        """
        if not app_name:
            app_name = self.get_frontmost_app()
        
        if not app_name:
            return ""
        
        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                try
                    set windowTitle to name of front window
                    return windowTitle
                on error
                    return ""
                end try
            end tell
        end tell
        '''
        
        title = self._run_applescript(script)
        logger.debug(f"Window title: {title}")
        return title
    
    def get_ui_elements(self, app_name: Optional[str] = None) -> List[Dict[str, any]]:
        """
        Get all UI elements in frontmost window
        
        Args:
            app_name: Application name (uses frontmost if None)
            
        Returns:
            List of UI elements with properties
        """
        if not app_name:
            app_name = self.get_frontmost_app()
        
        if not app_name:
            return []
        
        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                try
                    set windowElements to entire contents of front window
                    set elementList to {{}}
                    repeat with elem in windowElements
                        try
                            set elemClass to class of elem as string
                            set elemRole to role of elem as string
                            set elemTitle to title of elem as string
                            set elemValue to value of elem as string
                            set elemPos to position of elem
                            set elemSize to size of elem
                            
                            set end of elementList to {{elemClass, elemRole, elemTitle, elemValue, elemPos, elemSize}}
                        end try
                    end repeat
                    return elementList
                on error errMsg
                    return {{}}
                end try
            end tell
        end tell
        '''
        
        output = self._run_applescript(script)
        
        # Parse output (simplified - would need proper parsing)
        # For now, return empty list
        # TODO: Implement proper parsing of AppleScript list output
        
        logger.debug(f"Found UI elements (raw): {output[:200]}...")
        return []
    
    def find_button(self, button_text: str, app_name: Optional[str] = None) -> Optional[Tuple[int, int]]:
        """
        Find button by text and return its position
        
        Args:
            button_text: Button text to find
            app_name: Application name (uses frontmost if None)
            
        Returns:
            (x, y) coordinates of button center, or None if not found
        """
        if not app_name:
            app_name = self.get_frontmost_app()
        
        if not app_name:
            return None
        
        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                try
                    set theButton to first button whose title is "{button_text}"
                    set buttonPos to position of theButton
                    set buttonSize to size of theButton
                    
                    set x to item 1 of buttonPos
                    set y to item 2 of buttonPos
                    set w to item 1 of buttonSize
                    set h to item 2 of buttonSize
                    
                    set centerX to x + (w / 2)
                    set centerY to y + (h / 2)
                    
                    return centerX & "," & centerY
                on error
                    return ""
                end try
            end tell
        end tell
        '''
        
        output = self._run_applescript(script)
        
        if output and ',' in output:
            try:
                x, y = output.split(',')
                coords = (int(float(x)), int(float(y)))
                logger.debug(f"Found button '{button_text}' at {coords}")
                return coords
            except ValueError:
                pass
        
        logger.debug(f"Button '{button_text}' not found")
        return None
    
    def click_button(self, button_text: str, app_name: Optional[str] = None) -> bool:
        """
        Click button by text
        
        Args:
            button_text: Button text to click
            app_name: Application name (uses frontmost if None)
            
        Returns:
            True if successful
        """
        if not app_name:
            app_name = self.get_frontmost_app()
        
        if not app_name:
            return False
        
        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                try
                    click button "{button_text}" of front window
                    return "success"
                on error errMsg
                    return "error: " & errMsg
                end try
            end tell
        end tell
        '''
        
        output = self._run_applescript(script)
        success = output == "success"
        
        if success:
            logger.info(f"Clicked button '{button_text}'")
        else:
            logger.warning(f"Failed to click button '{button_text}': {output}")
        
        return success
    
    def get_menu_items(self, app_name: Optional[str] = None) -> List[str]:
        """
        Get all menu items in menu bar
        
        Args:
            app_name: Application name (uses frontmost if None)
            
        Returns:
            List of menu item names
        """
        if not app_name:
            app_name = self.get_frontmost_app()
        
        if not app_name:
            return []
        
        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                try
                    set menuNames to name of every menu bar item of menu bar 1
                    return menuNames
                on error
                    return {{}}
                end try
            end tell
        end tell
        '''
        
        output = self._run_applescript(script)
        
        # Parse comma-separated list
        if output:
            items = [item.strip() for item in output.split(',')]
            logger.debug(f"Found {len(items)} menu items")
            return items
        
        return []
    
    def click_menu_item(self, menu_path: List[str], app_name: Optional[str] = None) -> bool:
        """
        Click menu item by path
        
        Args:
            menu_path: List of menu names, e.g., ['File', 'New', 'Window']
            app_name: Application name (uses frontmost if None)
            
        Returns:
            True if successful
        """
        if not app_name:
            app_name = self.get_frontmost_app()
        
        if not app_name or not menu_path:
            return False
        
        # Build AppleScript menu path
        menu_script = f'menu bar item "{menu_path[0]}" of menu bar 1'
        
        for i, item in enumerate(menu_path[1:], 1):
            if i == len(menu_path) - 1:
                # Last item - click it
                menu_script = f'menu item "{item}" of menu "{menu_path[i-1]}" of {menu_script}'
            else:
                # Intermediate menu
                menu_script = f'menu "{item}" of {menu_script}'
        
        script = f'''
        tell application "System Events"
            tell process "{app_name}"
                try
                    click {menu_script}
                    return "success"
                on error errMsg
                    return "error: " & errMsg
                end try
            end tell
        end tell
        '''
        
        output = self._run_applescript(script)
        success = output == "success"
        
        if success:
            logger.info(f"Clicked menu item: {' > '.join(menu_path)}")
        else:
            logger.warning(f"Failed to click menu item: {output}")
        
        return success
    
    def get_text_fields(self, app_name: Optional[str] = None) -> List[Dict[str, any]]:
        """
        Get all text fields in frontmost window
        
        Args:
            app_name: Application name (uses frontmost if None)
            
        Returns:
            List of text field info
        """
        if not app_name:
            app_name = self.get_frontmost_app()
        
        if not app_name:
            return []
        
        # This is a simplified version
        # Full implementation would parse AppleScript output properly
        
        logger.debug("Getting text fields...")
        return []
    
    def is_available(self) -> bool:
        """Check if Accessibility API is available"""
        return self.available


# Singleton instance
_accessibility_api: Optional[AccessibilityAPI] = None


def get_accessibility_api() -> AccessibilityAPI:
    """Get singleton Accessibility API instance"""
    global _accessibility_api
    if _accessibility_api is None:
        _accessibility_api = AccessibilityAPI()
    return _accessibility_api

