"""
Input Controller - Mouse and Keyboard Control
Cross-platform input control using pyautogui
"""

import logging
import time
from typing import Tuple, Optional, List
import subprocess

logger = logging.getLogger(__name__)


class InputController:
    """Control mouse and keyboard"""
    
    def __init__(self):
        """Initialize input controller"""
        try:
            import pyautogui
            self.pyautogui = pyautogui
            
            # Safety settings
            self.pyautogui.PAUSE = 0.1  # Pause between actions
            self.pyautogui.FAILSAFE = True  # Move mouse to corner to abort
            
            # Get screen size
            self.screen_width, self.screen_height = self.pyautogui.size()
            
            logger.info(f"Input controller initialized. Screen: {self.screen_width}x{self.screen_height}")
            self.available = True
            
        except ImportError:
            logger.error("pyautogui not installed. Input control will not work.")
            self.available = False
    
    def is_available(self) -> bool:
        """Check if input control is available"""
        return self.available
    
    # Mouse Control
    
    def move_mouse(self, x: int, y: int, duration: float = 0.2) -> bool:
        """
        Move mouse to coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Movement duration in seconds
            
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            self.pyautogui.moveTo(x, y, duration=duration)
            logger.debug(f"Moved mouse to ({x}, {y})")
            return True
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")
            return False
    
    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        button: str = 'left',
        clicks: int = 1,
        interval: float = 0.1
    ) -> bool:
        """
        Click mouse at coordinates
        
        Args:
            x: X coordinate (current position if None)
            y: Y coordinate (current position if None)
            button: 'left', 'right', or 'middle'
            clicks: Number of clicks
            interval: Interval between clicks
            
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            if x is not None and y is not None:
                self.pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
                logger.debug(f"Clicked {button} button at ({x}, {y}) {clicks} time(s)")
            else:
                self.pyautogui.click(clicks=clicks, interval=interval, button=button)
                logger.debug(f"Clicked {button} button {clicks} time(s)")
            
            return True
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            return False
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Double click at coordinates"""
        return self.click(x, y, clicks=2)
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """Right click at coordinates"""
        return self.click(x, y, button='right')
    
    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5
    ) -> bool:
        """
        Drag from start to end coordinates
        
        Args:
            start_x: Start X coordinate
            start_y: Start Y coordinate
            end_x: End X coordinate
            end_y: End Y coordinate
            duration: Drag duration
            
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            self.pyautogui.moveTo(start_x, start_y)
            self.pyautogui.dragTo(end_x, end_y, duration=duration)
            logger.debug(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
        except Exception as e:
            logger.error(f"Failed to drag: {e}")
            return False
    
    def scroll(self, clicks: int, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        Scroll mouse wheel
        
        Args:
            clicks: Number of scroll clicks (positive = up, negative = down)
            x: X coordinate to scroll at
            y: Y coordinate to scroll at
            
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            if x is not None and y is not None:
                self.pyautogui.moveTo(x, y)
            
            self.pyautogui.scroll(clicks)
            logger.debug(f"Scrolled {clicks} clicks")
            return True
        except Exception as e:
            logger.error(f"Failed to scroll: {e}")
            return False
    
    # Keyboard Control
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type text
        
        Args:
            text: Text to type
            interval: Interval between keystrokes
            
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            self.pyautogui.write(text, interval=interval)
            logger.debug(f"Typed text: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return False
    
    def press_key(self, key: str, presses: int = 1, interval: float = 0.1) -> bool:
        """
        Press key
        
        Args:
            key: Key name (e.g., 'enter', 'esc', 'tab')
            presses: Number of times to press
            interval: Interval between presses
            
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            self.pyautogui.press(key, presses=presses, interval=interval)
            logger.debug(f"Pressed key '{key}' {presses} time(s)")
            return True
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            return False
    
    def hotkey(self, *keys: str) -> bool:
        """
        Press key combination
        
        Args:
            *keys: Keys to press together (e.g., 'ctrl', 'c')
            
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            self.pyautogui.hotkey(*keys)
            logger.debug(f"Pressed hotkey: {'+'.join(keys)}")
            return True
        except Exception as e:
            logger.error(f"Failed to press hotkey: {e}")
            return False
    
    def key_down(self, key: str) -> bool:
        """Hold key down"""
        if not self.available:
            return False
        
        try:
            self.pyautogui.keyDown(key)
            return True
        except Exception as e:
            logger.error(f"Failed to key down: {e}")
            return False
    
    def key_up(self, key: str) -> bool:
        """Release key"""
        if not self.available:
            return False
        
        try:
            self.pyautogui.keyUp(key)
            return True
        except Exception as e:
            logger.error(f"Failed to key up: {e}")
            return False
    
    # macOS Specific
    
    def cmd_key(self, key: str) -> bool:
        """Press Cmd+Key (macOS)"""
        return self.hotkey('command', key)
    
    def open_spotlight(self) -> bool:
        """Open Spotlight search (macOS)"""
        return self.hotkey('command', 'space')
    
    def switch_app(self) -> bool:
        """Open app switcher (macOS)"""
        return self.hotkey('command', 'tab')
    
    # Screenshot
    
    def take_screenshot(self, filepath: str) -> bool:
        """
        Take screenshot and save to file
        
        Args:
            filepath: Path to save screenshot
            
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            screenshot = self.pyautogui.screenshot()
            screenshot.save(filepath)
            logger.debug(f"Screenshot saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position"""
        if not self.available:
            return (0, 0)
        
        return self.pyautogui.position()
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size"""
        return (self.screen_width, self.screen_height)
    
    # Utility
    
    def wait(self, seconds: float):
        """Wait for specified seconds"""
        time.sleep(seconds)
        logger.debug(f"Waited {seconds} seconds")


# Singleton instance
_input_controller: Optional[InputController] = None


def get_input_controller() -> InputController:
    """Get singleton input controller instance"""
    global _input_controller
    if _input_controller is None:
        _input_controller = InputController()
    return _input_controller

