"""Fallback implementation for PyAutoGUI functionality for testing."""
import logging
from typing import Optional, Tuple, Union, List, Sequence
import time
from enum import Enum

logger = logging.getLogger(__name__)

# Mock screen size for testing
DEFAULT_SCREEN_SIZE = (1920, 1080)
CURRENT_MOUSE_POS = [0, 0]

class PyAutoGUIFallback:
    """Basic fallback implementation of PyAutoGUI for testing.
    
    This implementation tracks mouse and keyboard state and provides
    basic simulation capabilities without actually controlling the system.
    """
    
    def __init__(self):
        self.use_pyautogui = False
        try:
            import pyautogui
            self.pyautogui = pyautogui
            self.use_pyautogui = True
            logger.info("Using PyAutoGUI for input control")
        except ImportError:
            logger.warning("PyAutoGUI not available, using fallback implementation")
            self.pyautogui = None
            
        # Track input state
        self._mouse_buttons = {"left": False, "middle": False, "right": False}
        self._keyboard_state = {}
        self._last_mouse_pos = [0, 0]
        self._screen_size = DEFAULT_SCREEN_SIZE
        self._fail_safe = True
        self._pause = 0.1  # Default pause between actions
        
    def _validate_coordinates(self, x: int, y: int) -> bool:
        """Check if coordinates are within screen bounds."""
        if not (0 <= x <= self._screen_size[0] and 0 <= y <= self._screen_size[1]):
            if self._fail_safe:
                raise ValueError("Coordinates out of bounds with failsafe enabled")
            return False
        return True
        
    def moveTo(self, x: int, y: int, duration: float = 0.0) -> None:
        """Move mouse cursor to absolute coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Time to take for movement
        """
        if self.use_pyautogui:
            return self.pyautogui.moveTo(x, y, duration=duration)
            
        if self._validate_coordinates(x, y):
            if duration > 0:
                # Simulate gradual movement
                start_x, start_y = self._last_mouse_pos
                steps = int(duration * 10)  # 10 steps per second
                for i in range(1, steps + 1):
                    t = i / steps
                    curr_x = int(start_x + (x - start_x) * t)
                    curr_y = int(start_y + (y - start_y) * t)
                    self._last_mouse_pos = [curr_x, curr_y]
                    time.sleep(duration / steps)
            else:
                self._last_mouse_pos = [x, y]
                
    def click(self, x: Optional[int] = None, y: Optional[int] = None,
             button: str = "left", clicks: int = 1, interval: float = 0.0) -> None:
        """Click the mouse.
        
        Args:
            x: Optional x coordinate
            y: Optional y coordinate
            button: Mouse button to click ("left", "middle", "right")
            clicks: Number of clicks
            interval: Time between clicks
        """
        if self.use_pyautogui:
            return self.pyautogui.click(x, y, button=button, clicks=clicks, interval=interval)
            
        if x is not None and y is not None:
            self.moveTo(x, y)
            
        for i in range(clicks):
            self._mouse_buttons[button] = True
            self._mouse_buttons[button] = False
            if i < clicks - 1:
                time.sleep(interval)
                
    def dragTo(self, x: int, y: int, duration: float = 0.0,
               button: str = "left") -> None:
        """Drag mouse from current position.
        
        Args:
            x: Target x coordinate 
            y: Target y coordinate
            duration: Time for drag operation
            button: Mouse button to use
        """
        if self.use_pyautogui:
            return self.pyautogui.dragTo(x, y, duration=duration, button=button)
            
        self._mouse_buttons[button] = True
        self.moveTo(x, y, duration=duration)
        self._mouse_buttons[button] = False
        
    def scroll(self, clicks: int) -> None:
        """Scroll the mouse wheel.
        
        Args:
            clicks: Number of scroll steps (positive=up, negative=down)
        """
        if self.use_pyautogui:
            return self.pyautogui.scroll(clicks)
            
        # Just track the scroll amount
        logger.info(f"Scrolled {'up' if clicks > 0 else 'down'} {abs(clicks)} clicks")
        
    def keyDown(self, key: str) -> None:
        """Press and hold a key.
        
        Args:
            key: The key to press
        """
        if self.use_pyautogui:
            return self.pyautogui.keyDown(key)
            
        self._keyboard_state[key] = True
        
    def keyUp(self, key: str) -> None:
        """Release a key.
        
        Args:
            key: The key to release
        """
        if self.use_pyautogui:
            return self.pyautogui.keyUp(key)
            
        self._keyboard_state[key] = False
        
    def press(self, keys: Union[str, List[str]], presses: int = 1,
             interval: float = 0.0) -> None:
        """Press and release a key or keys.
        
        Args:
            keys: Key(s) to press
            presses: Times to press the key(s)
            interval: Time between presses
        """
        if self.use_pyautogui:
            return self.pyautogui.press(keys, presses=presses, interval=interval)
            
        if isinstance(keys, str):
            keys = [keys]
            
        for _ in range(presses):
            for key in keys:
                self.keyDown(key)
                self.keyUp(key)
            if presses > 1:
                time.sleep(interval)
                
    def typewrite(self, text: str, interval: float = 0.0) -> None:
        """Type text one character at a time.
        
        Args:
            text: The text to type
            interval: Time between keystrokes
        """
        if self.use_pyautogui:
            return self.pyautogui.typewrite(text, interval=interval)
            
        for char in text:
            self.press(char)
            if interval > 0:
                time.sleep(interval)
                
    def hotkey(self, *args: str) -> None:
        """Perform a keyboard hotkey combination.
        
        Args:
            *args: The keys to press in order
        """
        if self.use_pyautogui:
            return self.pyautogui.hotkey(*args)
            
        # Press all keys in sequence
        for key in args:
            self.keyDown(key)
        # Release in reverse order
        for key in reversed(args):
            self.keyUp(key)
            
    def position(self) -> Tuple[int, int]:
        """Get current mouse position.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        if self.use_pyautogui:
            return self.pyautogui.position()
        return tuple(self._last_mouse_pos)
        
    def size(self) -> Tuple[int, int]:
        """Get screen size.
        
        Returns:
            Tuple of (width, height)
        """
        if self.use_pyautogui:
            return self.pyautogui.size()
        return self._screen_size

# Global instance        
auto = PyAutoGUIFallback()