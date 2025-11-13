#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Screen Capture Module
Simple screen capture functionality for intelligent agent
"""

import logging
import os
from datetime import datetime
from typing import Optional, Tuple
import asyncio

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from PIL import Image
except ImportError:
    Image = None

LOG = logging.getLogger("daur_ai.screen_capture")


class ScreenCapture:
    """
    Simple screen capture for screenshots
    """
    
    def __init__(self, save_dir: str = None):
        """
        Initialize screen capture
        
        Args:
            save_dir: Directory to save screenshots (default: current directory)
        """
        self.save_dir = save_dir or os.getcwd()
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        if pyautogui is None:
            LOG.warning("pyautogui not available - screen capture disabled")
        
        LOG.info(f"ScreenCapture initialized, save_dir: {self.save_dir}")
    
    async def capture(self, 
                     filename: str = None,
                     region: Tuple[int, int, int, int] = None) -> Optional[str]:
        """
        Capture screenshot
        
        Args:
            filename: Output filename (default: auto-generated timestamp)
            region: Region to capture (left, top, width, height)
        
        Returns:
            str: Path to saved screenshot, or None if failed
        """
        if pyautogui is None:
            LOG.error("pyautogui not available")
            return None
        
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Ensure .png extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            # Full path
            filepath = os.path.join(self.save_dir, filename)
            
            # Capture screenshot
            LOG.debug(f"Capturing screenshot: {filepath}")
            
            # Run in executor to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self._capture_sync,
                filepath,
                region
            )
            
            LOG.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            LOG.error(f"Failed to capture screenshot: {e}")
            return None
    
    def _capture_sync(self, filepath: str, region: Tuple[int, int, int, int] = None):
        """
        Synchronous capture helper
        
        Args:
            filepath: Path to save screenshot
            region: Region to capture
        """
        if region:
            # Capture specific region
            screenshot = pyautogui.screenshot(region=region)
        else:
            # Capture full screen
            screenshot = pyautogui.screenshot()
        
        # Save
        screenshot.save(filepath)
    
    def capture_sync(self, 
                    filename: str = None,
                    region: Tuple[int, int, int, int] = None) -> Optional[str]:
        """
        Synchronous version of capture
        
        Args:
            filename: Output filename
            region: Region to capture
            
        Returns:
            str: Path to saved screenshot
        """
        if pyautogui is None:
            LOG.error("pyautogui not available")
            return None
        
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Ensure .png extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            # Full path
            filepath = os.path.join(self.save_dir, filename)
            
            # Capture
            self._capture_sync(filepath, region)
            
            LOG.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            LOG.error(f"Failed to capture screenshot: {e}")
            return None
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen resolution
        
        Returns:
            Tuple[int, int]: (width, height)
        """
        if pyautogui is None:
            return (1920, 1080)  # Default
        
        try:
            size = pyautogui.size()
            return (size.width, size.height)
        except:
            return (1920, 1080)
    
    def set_save_dir(self, save_dir: str):
        """
        Set screenshot save directory
        
        Args:
            save_dir: New save directory
        """
        self.save_dir = save_dir
        
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        LOG.info(f"Save directory changed to: {self.save_dir}")


# Convenience function
async def capture_screenshot(filename: str = None) -> Optional[str]:
    """
    Quick screenshot capture
    
    Args:
        filename: Output filename
        
    Returns:
        str: Path to saved screenshot
    """
    capture = ScreenCapture()
    return await capture.capture(filename)

