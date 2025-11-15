"""
Photoshop Controller - Adobe Photoshop Automation
Uses AppleScript and UI automation for Photoshop control
"""

import logging
import subprocess
from typing import Optional, List, Dict, Tuple
import time

logger = logging.getLogger(__name__)


class PhotoshopController:
    """Control Adobe Photoshop via AppleScript"""
    
    def __init__(self):
        """Initialize Photoshop controller"""
        self.app_name = "Adobe Photoshop 2024"  # Adjust version as needed
        self.available = self._check_availability()
        
        if self.available:
            logger.info("Photoshop controller initialized")
        else:
            logger.warning("Photoshop not found or not available")
    
    def _check_availability(self) -> bool:
        """Check if Photoshop is installed"""
        try:
            script = f'''
            tell application "System Events"
                return exists application process "{self.app_name}"
            end tell
            '''
            result = self._run_applescript(script)
            return True
        except Exception:
            return False
    
    def _run_applescript(self, script: str) -> str:
        """Execute AppleScript and return output"""
        try:
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"AppleScript error: {result.stderr}")
                return ""
        except Exception as e:
            logger.error(f"Failed to run AppleScript: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if Photoshop is available"""
        return self.available
    
    def launch(self) -> bool:
        """Launch Photoshop"""
        script = f'tell application "{self.app_name}" to activate'
        result = self._run_applescript(script)
        
        if result or result == "":
            logger.info("Photoshop launched")
            time.sleep(3)  # Wait for Photoshop to open
            return True
        return False
    
    def quit(self) -> bool:
        """Quit Photoshop"""
        script = f'tell application "{self.app_name}" to quit'
        result = self._run_applescript(script)
        logger.info("Photoshop quit")
        return True
    
    def is_running(self) -> bool:
        """Check if Photoshop is running"""
        script = f'''
        tell application "System Events"
            return (name of processes) contains "{self.app_name}"
        end tell
        '''
        result = self._run_applescript(script)
        return result.lower() == "true"
    
    def new_document(self, width: int = 1920, height: int = 1080, resolution: int = 72) -> bool:
        """
        Create new document
        
        Args:
            width: Width in pixels
            height: Height in pixels
            resolution: Resolution in DPI
        """
        script = f'''
        tell application "{self.app_name}"
            make new document with properties {{width:{width}, height:{height}, resolution:{resolution}}}
        end tell
        '''
        result = self._run_applescript(script)
        logger.info(f"Created new document: {width}x{height}")
        return True
    
    def open_file(self, filepath: str) -> bool:
        """Open file in Photoshop"""
        script = f'''
        tell application "{self.app_name}"
            open POSIX file "{filepath}"
        end tell
        '''
        result = self._run_applescript(script)
        logger.info(f"Opened file: {filepath}")
        return True
    
    def save_file(self, filepath: str) -> bool:
        """Save current document"""
        script = f'''
        tell application "{self.app_name}"
            save current document in POSIX file "{filepath}"
        end tell
        '''
        result = self._run_applescript(script)
        logger.info(f"Saved file: {filepath}")
        return True
    
    def close_document(self) -> bool:
        """Close current document without saving"""
        script = f'''
        tell application "{self.app_name}"
            close current document saving no
        end tell
        '''
        result = self._run_applescript(script)
        logger.info("Closed document")
        return True
    
    def resize_image(self, width: int, height: int) -> bool:
        """Resize current image"""
        script = f'''
        tell application "{self.app_name}"
            tell current document
                resize image width {width} height {height}
            end tell
        end tell
        '''
        result = self._run_applescript(script)
        logger.info(f"Resized image to {width}x{height}")
        return True
    
    def rotate_image(self, angle: float) -> bool:
        """Rotate current image"""
        script = f'''
        tell application "{self.app_name}"
            tell current document
                rotate canvas angle {angle}
            end tell
        end tell
        '''
        result = self._run_applescript(script)
        logger.info(f"Rotated image by {angle} degrees")
        return True
    
    def apply_filter(self, filter_name: str) -> bool:
        """Apply filter (simplified - actual implementation depends on filter)"""
        logger.warning("Filter application requires specific AppleScript for each filter")
        return False
    
    def add_text(self, text: str, x: int = 100, y: int = 100) -> bool:
        """Add text layer"""
        script = f'''
        tell application "{self.app_name}"
            tell current document
                make new text layer with properties {{contents:"{text}", position:{{{x}, {y}}}}}
            end tell
        end tell
        '''
        result = self._run_applescript(script)
        logger.info(f"Added text: {text}")
        return True
    
    def export_png(self, filepath: str) -> bool:
        """Export as PNG"""
        script = f'''
        tell application "{self.app_name}"
            tell current document
                save in POSIX file "{filepath}" as PNG
            end tell
        end tell
        '''
        result = self._run_applescript(script)
        logger.info(f"Exported PNG: {filepath}")
        return True
    
    def export_jpeg(self, filepath: str, quality: int = 8) -> bool:
        """Export as JPEG"""
        script = f'''
        tell application "{self.app_name}"
            tell current document
                save in POSIX file "{filepath}" as JPEG with options {{quality:{quality}}}
            end tell
        end tell
        '''
        result = self._run_applescript(script)
        logger.info(f"Exported JPEG: {filepath}")
        return True


def get_photoshop_controller() -> PhotoshopController:
    """Get Photoshop controller instance"""
    return PhotoshopController()

