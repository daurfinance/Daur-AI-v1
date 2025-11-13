#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
System Profiler - Analyzes system configuration and capabilities
Collects information about OS, installed apps, keyboard layouts, screen resolution, etc.
"""

import platform
import subprocess
import os
import logging
from typing import Dict, List, Any, Optional
import json

LOG = logging.getLogger("daur_ai.system_profiler")


class SystemProfiler:
    """
    Analyzes system configuration and provides information
    needed for adaptive agent behavior.
    """
    
    def __init__(self):
        """Initialize the system profiler."""
        self.profile: Optional[Dict[str, Any]] = None
        LOG.info("SystemProfiler initialized")
    
    def get_profile(self, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get complete system profile.
        
        Args:
            force_refresh: Force re-profiling even if cached
            
        Returns:
            Dictionary with system information
        """
        if self.profile and not force_refresh:
            return self.profile
        
        LOG.info("Profiling system...")
        
        self.profile = {
            "os": self._get_os_info(),
            "screen": self._get_screen_info(),
            "keyboard": self._get_keyboard_info(),
            "applications": self._get_installed_apps(),
            "shortcuts": self._get_system_shortcuts(),
            "locale": self._get_locale_info(),
        }
        
        LOG.info(f"System profile complete: {json.dumps(self.profile, indent=2)}")
        return self.profile
    
    def _get_os_info(self) -> Dict[str, str]:
        """Get operating system information."""
        return {
            "system": platform.system(),  # Darwin, Linux, Windows
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),  # x86_64, arm64
            "processor": platform.processor(),
        }
    
    def _get_screen_info(self) -> Dict[str, Any]:
        """Get screen resolution and display information."""
        try:
            if platform.system() == "Darwin":  # macOS
                # Use system_profiler to get display info
                result = subprocess.run(
                    ["system_profiler", "SPDisplaysDataType", "-json"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    displays = data.get("SPDisplaysDataType", [{}])[0]
                    
                    # Extract resolution from first display
                    items = displays.get("spdisplays_ndrvs", [{}])
                    if items:
                        resolution = items[0].get("_spdisplays_resolution", "Unknown")
                        return {
                            "resolution": resolution,
                            "displays": len(items),
                            "info": items[0]
                        }
            
            # Fallback: try to get from environment or use default
            return {
                "resolution": "1920x1080",  # Default assumption
                "displays": 1,
                "info": "Could not detect"
            }
            
        except Exception as e:
            LOG.warning(f"Could not get screen info: {e}")
            return {
                "resolution": "1920x1080",
                "displays": 1,
                "info": "Detection failed"
            }
    
    def _get_keyboard_info(self) -> Dict[str, Any]:
        """Get keyboard layout and input source information."""
        try:
            if platform.system() == "Darwin":  # macOS
                # Get current input source
                result = subprocess.run(
                    ["defaults", "read", "com.apple.HIToolbox", "AppleSelectedInputSources"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Get keyboard shortcut for switching input
                shortcut_result = subprocess.run(
                    ["defaults", "read", "com.apple.symbolichotkeys", "AppleSymbolicHotKeys"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Parse to find layout switch shortcut
                # Common: Ctrl+Space, Cmd+Space, Fn
                layout_switch = "ctrl+space"  # Default
                
                if "Fn" in shortcut_result.stdout or "fn" in result.stdout.lower():
                    layout_switch = "fn"
                
                return {
                    "current_layout": "en",  # Will be detected dynamically
                    "available_layouts": ["en", "ru"],  # Common assumption
                    "switch_shortcut": layout_switch,
                    "raw_info": result.stdout[:200] if result.returncode == 0 else "N/A"
                }
        
        except Exception as e:
            LOG.warning(f"Could not get keyboard info: {e}")
        
        return {
            "current_layout": "en",
            "available_layouts": ["en"],
            "switch_shortcut": "ctrl+space",
            "raw_info": "Detection failed"
        }
    
    def _get_installed_apps(self) -> List[str]:
        """Get list of installed applications."""
        apps = []
        
        try:
            if platform.system() == "Darwin":  # macOS
                # List applications in /Applications
                app_dirs = ["/Applications", "/System/Applications"]
                
                for app_dir in app_dirs:
                    if os.path.exists(app_dir):
                        for item in os.listdir(app_dir):
                            if item.endswith(".app"):
                                app_name = item.replace(".app", "")
                                apps.append(app_name)
                
                # Also check user Applications
                user_apps = os.path.expanduser("~/Applications")
                if os.path.exists(user_apps):
                    for item in os.listdir(user_apps):
                        if item.endswith(".app"):
                            app_name = item.replace(".app", "")
                            apps.append(app_name)
        
        except Exception as e:
            LOG.warning(f"Could not list applications: {e}")
        
        return sorted(list(set(apps)))  # Remove duplicates and sort
    
    def _get_system_shortcuts(self) -> Dict[str, str]:
        """Get system keyboard shortcuts."""
        if platform.system() == "Darwin":  # macOS
            return {
                "spotlight": "command+space",
                "screenshot": "command+shift+3",
                "screenshot_selection": "command+shift+4",
                "force_quit": "command+option+esc",
                "switch_apps": "command+tab",
                "minimize": "command+m",
                "close_window": "command+w",
                "quit_app": "command+q",
                "new_tab": "command+t",
                "find": "command+f",
            }
        
        return {}
    
    def _get_locale_info(self) -> Dict[str, str]:
        """Get system locale and language information."""
        try:
            if platform.system() == "Darwin":  # macOS
                result = subprocess.run(
                    ["defaults", "read", "-g", "AppleLocale"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                locale = result.stdout.strip() if result.returncode == 0 else "en_US"
                
                return {
                    "locale": locale,
                    "language": locale.split("_")[0] if "_" in locale else locale,
                    "region": locale.split("_")[1] if "_" in locale else "US"
                }
        
        except Exception as e:
            LOG.warning(f"Could not get locale info: {e}")
        
        return {
            "locale": "en_US",
            "language": "en",
            "region": "US"
        }
    
    def is_app_installed(self, app_name: str) -> bool:
        """
        Check if an application is installed.
        
        Args:
            app_name: Application name (case-insensitive)
            
        Returns:
            True if installed
        """
        if not self.profile:
            self.get_profile()
        
        apps = self.profile.get("applications", [])
        app_name_lower = app_name.lower()
        
        return any(app.lower() == app_name_lower for app in apps)
    
    def get_spotlight_shortcut(self) -> str:
        """Get the keyboard shortcut for Spotlight."""
        if not self.profile:
            self.get_profile()
        
        return self.profile.get("shortcuts", {}).get("spotlight", "command+space")
    
    def get_layout_switch_shortcut(self) -> str:
        """Get the keyboard shortcut for switching input layout."""
        if not self.profile:
            self.get_profile()
        
        return self.profile.get("keyboard", {}).get("switch_shortcut", "ctrl+space")


if __name__ == "__main__":
    # Test the profiler
    logging.basicConfig(level=logging.INFO)
    
    profiler = SystemProfiler()
    profile = profiler.get_profile()
    
    print("\n" + "="*60)
    print("SYSTEM PROFILE")
    print("="*60)
    print(json.dumps(profile, indent=2))
    print("="*60)
    
    print(f"\nSafari installed: {profiler.is_app_installed('Safari')}")
    print(f"Spotlight shortcut: {profiler.get_spotlight_shortcut()}")
    print(f"Layout switch: {profiler.get_layout_switch_shortcut()}")

