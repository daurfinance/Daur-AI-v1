"""
BlueStacks Controller - Android Emulator Control
Uses ADB (Android Debug Bridge) for BlueStacks automation
"""

import logging
import subprocess
from typing import Optional, List, Dict, Tuple
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class BlueStacksController:
    """Control BlueStacks emulator via ADB"""
    
    def __init__(self, adb_path: str = "adb", device_id: Optional[str] = None):
        """
        Initialize BlueStacks controller
        
        Args:
            adb_path: Path to adb executable
            device_id: Specific device ID (auto-detect if None)
        """
        self.adb_path = adb_path
        self.device_id = device_id
        self.available = self._check_adb()
        
        if self.available:
            logger.info("BlueStacks controller initialized")
        else:
            logger.warning("ADB not found. Install Android SDK Platform Tools")
    
    def _check_adb(self) -> bool:
        """Check if ADB is available"""
        try:
            result = subprocess.run(
                [self.adb_path, 'version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def _run_adb(self, *args, timeout: int = 30) -> str:
        """
        Run ADB command
        
        Args:
            *args: ADB command arguments
            timeout: Command timeout
            
        Returns:
            Command output
        """
        cmd = [self.adb_path]
        
        if self.device_id:
            cmd.extend(['-s', self.device_id])
        
        cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"ADB command failed: {result.stderr}")
                return ""
        
        except Exception as e:
            logger.error(f"ADB error: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if ADB is available"""
        return self.available
    
    def list_devices(self) -> List[str]:
        """List connected devices"""
        output = self._run_adb('devices')
        
        devices = []
        for line in output.split('\n')[1:]:  # Skip header
            if line.strip():
                device_id = line.split()[0]
                devices.append(device_id)
        
        logger.info(f"Found {len(devices)} devices: {devices}")
        return devices
    
    def connect_bluestacks(self, port: int = 5555) -> bool:
        """
        Connect to BlueStacks emulator
        
        Args:
            port: BlueStacks ADB port (default 5555)
        """
        address = f"127.0.0.1:{port}"
        output = self._run_adb('connect', address)
        
        if 'connected' in output.lower():
            self.device_id = address
            logger.info(f"Connected to BlueStacks: {address}")
            return True
        
        logger.error(f"Failed to connect to BlueStacks: {output}")
        return False
    
    def disconnect(self) -> bool:
        """Disconnect from device"""
        output = self._run_adb('disconnect')
        logger.info("Disconnected from device")
        return True
    
    def tap(self, x: int, y: int) -> bool:
        """
        Tap screen at coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        output = self._run_adb('shell', 'input', 'tap', str(x), str(y))
        logger.debug(f"Tapped at ({x}, {y})")
        return True
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """
        Swipe from one point to another
        
        Args:
            x1: Start X
            y1: Start Y
            x2: End X
            y2: End Y
            duration: Swipe duration in ms
        """
        output = self._run_adb(
            'shell', 'input', 'swipe',
            str(x1), str(y1), str(x2), str(y2), str(duration)
        )
        logger.debug(f"Swiped from ({x1}, {y1}) to ({x2}, {y2})")
        return True
    
    def type_text(self, text: str) -> bool:
        """
        Type text (spaces must be escaped as %s)
        
        Args:
            text: Text to type
        """
        # Escape spaces
        text = text.replace(' ', '%s')
        output = self._run_adb('shell', 'input', 'text', text)
        logger.debug(f"Typed text: {text}")
        return True
    
    def press_key(self, keycode: str) -> bool:
        """
        Press key
        
        Args:
            keycode: Android keycode (e.g., 'KEYCODE_HOME', 'KEYCODE_BACK')
        """
        output = self._run_adb('shell', 'input', 'keyevent', keycode)
        logger.debug(f"Pressed key: {keycode}")
        return True
    
    def press_home(self) -> bool:
        """Press home button"""
        return self.press_key('KEYCODE_HOME')
    
    def press_back(self) -> bool:
        """Press back button"""
        return self.press_key('KEYCODE_BACK')
    
    def launch_app(self, package_name: str) -> bool:
        """
        Launch app by package name
        
        Args:
            package_name: App package name (e.g., 'com.whatsapp')
        """
        output = self._run_adb(
            'shell', 'monkey', '-p', package_name, '-c',
            'android.intent.category.LAUNCHER', '1'
        )
        logger.info(f"Launched app: {package_name}")
        return True
    
    def stop_app(self, package_name: str) -> bool:
        """Stop app"""
        output = self._run_adb('shell', 'am', 'force-stop', package_name)
        logger.info(f"Stopped app: {package_name}")
        return True
    
    def install_apk(self, apk_path: str) -> bool:
        """
        Install APK
        
        Args:
            apk_path: Path to APK file
        """
        output = self._run_adb('install', apk_path, timeout=120)
        
        if 'Success' in output:
            logger.info(f"Installed APK: {apk_path}")
            return True
        
        logger.error(f"APK installation failed: {output}")
        return False
    
    def uninstall_app(self, package_name: str) -> bool:
        """Uninstall app"""
        output = self._run_adb('uninstall', package_name)
        
        if 'Success' in output:
            logger.info(f"Uninstalled app: {package_name}")
            return True
        
        return False
    
    def take_screenshot(self, output_path: str) -> bool:
        """
        Take screenshot
        
        Args:
            output_path: Path to save screenshot
        """
        # Take screenshot on device
        device_path = '/sdcard/screenshot.png'
        self._run_adb('shell', 'screencap', '-p', device_path)
        
        # Pull to local
        output = self._run_adb('pull', device_path, output_path)
        
        if Path(output_path).exists():
            logger.info(f"Screenshot saved: {output_path}")
            return True
        
        return False
    
    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen resolution
        
        Returns:
            (width, height) tuple
        """
        output = self._run_adb('shell', 'wm', 'size')
        
        # Parse output: "Physical size: 1080x1920"
        if 'Physical size:' in output:
            size_str = output.split('Physical size:')[1].strip()
            width, height = size_str.split('x')
            return (int(width), int(height))
        
        return (1080, 1920)  # Default
    
    def list_packages(self) -> List[str]:
        """List installed packages"""
        output = self._run_adb('shell', 'pm', 'list', 'packages')
        
        packages = []
        for line in output.split('\n'):
            if line.startswith('package:'):
                package = line.replace('package:', '').strip()
                packages.append(package)
        
        return packages
    
    def get_current_activity(self) -> str:
        """Get current foreground activity"""
        output = self._run_adb('shell', 'dumpsys', 'window', 'windows')
        
        # Parse current focus
        for line in output.split('\n'):
            if 'mCurrentFocus' in line:
                return line.strip()
        
        return ""
    
    # Social Media Helpers
    
    def open_whatsapp(self) -> bool:
        """Open WhatsApp"""
        return self.launch_app('com.whatsapp')
    
    def open_instagram(self) -> bool:
        """Open Instagram"""
        return self.launch_app('com.instagram.android')
    
    def open_facebook(self) -> bool:
        """Open Facebook"""
        return self.launch_app('com.facebook.katana')
    
    def open_telegram(self) -> bool:
        """Open Telegram"""
        return self.launch_app('org.telegram.messenger')


def get_bluestacks_controller() -> BlueStacksController:
    """Get BlueStacks controller instance"""
    return BlueStacksController()

