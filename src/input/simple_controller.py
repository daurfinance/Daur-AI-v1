"""Simple input controller implementation."""
import logging
import subprocess
import time
from typing import Dict, Any, Tuple

class SimpleInputController:
    """Basic input controller without dependencies."""
    
    def __init__(self, os_platform: str = None):
        """Initialize controller.
        
        Args:
            os_platform (str): Operating system platform
        """
        self.logger = logging.getLogger(__name__)
        self.os_platform = os_platform or "unknown"
    
    def execute(self, action: Dict[str, Any]) -> bool:
        """Execute an input action.
        
        Args:
            action (Dict): Action description with parameters
            
        Returns:
            bool: True if action was executed successfully
        """
        try:
            action_type = action.get("type", "")
            params = action.get("params", {})
            
            if action_type == "click":
                return self._handle_click(params)
            elif action_type == "type":
                return self._handle_type(params)
            elif action_type == "key":
                return self._handle_key(params)
            elif action_type == "sequence":
                return self._handle_sequence(params)
            else:
                self.logger.warning(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing action: {e}", exc_info=True)
            return False
            
    def _handle_click(self, params: Dict[str, Any]) -> bool:
        """Handle click action.
        
        Args:
            params (Dict): Click parameters including target
            
        Returns:
            bool: True if click was simulated successfully
        """
        target = params.get('target', 'unknown target')
        self.logger.info(f"Simulating click on: {target}")
        print(f"[SIMULATION] Click on: {target}")
        time.sleep(0.1)  # Simulate execution time
        return True
    
    def _handle_type(self, params: Dict[str, Any]) -> bool:
        """Handle text input action.
        
        Args:
            params (Dict): Type parameters including text and target
            
        Returns:
            bool: True if typing was simulated successfully
        """
        text = params.get('text', '')
        target = params.get('target')
        
        if target:
            self.logger.info(f"Simulating typing: {text[:50]}... in {target}")
            print(f"[SIMULATION] Typing text: {text} in {target}")
        else:
            self.logger.info(f"Simulating typing: {text[:50]}...")
            print(f"[SIMULATION] Typing text: {text}")
            
        time.sleep(len(text) * 0.01)  # Simulate typing time
        return True
    
    def _handle_key(self, params: Dict[str, Any]) -> bool:
        """Handle key press action.
        
        Args:
            params (Dict): Key parameters including key name
            
        Returns:
            bool: True if key press was simulated successfully
        """
        key = params.get('key', 'unknown key')
        self.logger.info(f"Simulating key press: {key}")
        print(f"[SIMULATION] Pressing key: {key}")
        time.sleep(0.1)
        return True
    
    def _handle_sequence(self, params: Dict[str, Any]) -> bool:
        """Handle sequence of actions.
        
        Args:
            params (Dict): Sequence parameters including list of commands
            
        Returns:
            bool: True if all actions in sequence were executed successfully
        """
        commands = params.get('commands', [])
        success = True
        
        for cmd in commands:
            if not self.execute(cmd):
                success = False
                self.logger.warning(f"Failed to execute command in sequence: {cmd}")
        
        return success
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen size.
        
        Returns:
            Tuple[int, int]: Screen dimensions (width, height)
        """
        try:
            if self.os_platform == "Linux":
                result = subprocess.run(['xrandr'], capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if '*' in line:  # Current resolution
                            parts = line.split()
                            for part in parts:
                                if 'x' in part and part.replace('x', '').replace('.', '').isdigit():
                                    width, height = part.split('x')
                                    return (int(width), int(height.split('.')[0]))
        except Exception as e:
            self.logger.debug(f"Failed to get screen size: {e}")
        
        # Return default resolution
        return (1920, 1080)
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position.
        
        Returns:
            Tuple[int, int]: Mouse coordinates (x, y)
        """
        # In simple version return dummy coordinates
        return (100, 100)
    
    def cleanup(self):
        """Clean up controller resources."""
        self.logger.info("Cleaning up simple input controller")
        
# Function to create controller based on dependency availability
def create_input_controller(os_platform: str = None):
    """Create appropriate input controller.
    
    Args:
        os_platform (str): Operating system platform
        
    Returns:
        InputController: Controller instance
    """
    try:
        # Try importing full version
        from src.input.controller import InputController
        return InputController(os_platform)
    except ImportError as e:
        # Use simple version
        logging.getLogger('daur_ai').warning(
            f"Failed to load full input controller ({e}), "
            "using simple version"
        )
        return SimpleInputController(os_platform)
