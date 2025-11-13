#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Input Controller - Full-featured mouse/keyboard control
Supports: pyautogui, pyperclip with async wrappers and safe_mode for testing
"""

import asyncio
import logging
import platform
from typing import Any, Dict, Optional, Tuple
from threading import Lock

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    import pyperclip
except ImportError:
    pyperclip = None

LOG = logging.getLogger("daur_ai.input")


class InputController:
    """System input controller with async and safe_mode support."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize controller.
        
        Args:
            config: Optional config dict with keys:
                - safe_mode (bool): Simulate actions without actually running them
                - keyboard_delay (float): Delay between keystrokes
                - mouse_speed (float): Mouse movement speed multiplier
        """
        self.config = config or {}
        self.safe_mode = bool(self.config.get("safe_mode", False))
        self.keyboard_delay = float(self.config.get("keyboard_delay", 0.01))
        self.mouse_speed = float(self.config.get("mouse_speed", 1.0))
        self._lock = Lock()

        if pyautogui is None and not self.safe_mode:
            raise ImportError("pyautogui required (install: pip install pyautogui)")

        if pyautogui:
            pyautogui.PAUSE = self.keyboard_delay
            pyautogui.FAILSAFE = True

        if self.safe_mode:
            LOG.info("InputController in SAFE MODE - actions simulated")

    # ==================== Mouse Methods ====================

    async def click(self, x: int, y: int, button: str = "left", clicks: int = 1) -> None:
        """Click mouse button."""
        if self.safe_mode:
            LOG.debug(f"[SAFE] Click {clicks}x {button} at ({x},{y})")
            return
        await self._run_input(lambda: pyautogui.click(x, y, button=button, clicks=clicks))

    async def move(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """Move mouse to coordinates."""
        if self.safe_mode:
            LOG.debug(f"[SAFE] Move mouse to ({x},{y})")
            return
        # pyautogui requires duration to be a number, not None
        dur = duration if duration is not None else 0.0
        await self._run_input(lambda: pyautogui.moveTo(x, y, duration=dur))

    async def drag(self, x: int, y: int, button: str = "left", duration: Optional[float] = None) -> None:
        """Drag mouse to coordinates."""
        if self.safe_mode:
            LOG.debug(f"[SAFE] Drag to ({x},{y})")
            return
        # pyautogui requires duration to be a number, not None
        dur = duration if duration is not None else 0.0
        await self._run_input(lambda: pyautogui.dragTo(x, y, button=button, duration=dur))

    async def scroll(self, clicks: int = 1, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Scroll mouse wheel."""
        if self.safe_mode:
            LOG.debug(f"[SAFE] Scroll {clicks} clicks")
            return
        if x and y:
            await self.move(x, y)
        await self._run_input(lambda: pyautogui.scroll(clicks))

    # ==================== Keyboard Methods ====================

    async def key(self, key: str, hold: bool = False) -> None:
        """Press/release keyboard key."""
        if self.safe_mode:
            LOG.debug(f"[SAFE] Key {key} ({'down' if hold else 'up'})")
            return
        fn = pyautogui.keyDown if hold else pyautogui.keyUp
        await self._run_input(lambda: fn(key))

    async def type(self, text: str, interval: Optional[float] = None) -> None:
        """Type text string."""
        if self.safe_mode:
            LOG.debug(f"[SAFE] Type: {text}")
            return
        # pyautogui requires interval to be a number, not None
        intv = interval if interval is not None else self.keyboard_delay
        await self._run_input(lambda: pyautogui.write(text, interval=intv))

    async def hotkey(self, *keys: str) -> None:
        """Press key combination."""
        if self.safe_mode:
            LOG.debug(f"[SAFE] Hotkey: {'+'.join(keys)}")
            return
        # macOS: map Ctrl to Cmd for common shortcuts
        if platform.system() == "Darwin":
            if keys[0].lower() in ["ctrl", "cmd"] and len(keys) > 1 and keys[-1].lower() in "cvxazfsop":
                keys = ("cmd",) + keys[1:]
        await self._run_input(lambda: pyautogui.hotkey(*keys))

    # ==================== Clipboard Methods ====================

    async def clipboard_get(self) -> str:
        """Get clipboard contents."""
        if self.safe_mode:
            return "[clipboard-simulated]"
        if not pyperclip:
            raise RuntimeError("pyperclip not installed")
        return await self._run_input(pyperclip.paste)

    async def clipboard_set(self, text: str) -> None:
        """Set clipboard contents."""
        if self.safe_mode:
            LOG.debug(f"[SAFE] Clipboard set: {text}")
            return
        if not pyperclip:
            raise RuntimeError("pyperclip not installed")
        await self._run_input(lambda: pyperclip.copy(text))

    # ==================== System Info ====================

    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        if self.safe_mode:
            return (0, 0)
        return pyautogui.position()

    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        if self.safe_mode:
            return (1920, 1080)
        return pyautogui.size()

    # ==================== Async Execution ====================

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action from params dict.
        
        Params can have:
            - type/subtype/action: action name
            - x, y: coordinates
            - button: mouse button
            - text: text to type
            - keys: list of keys for hotkey
            - clicks: number of clicks
        """
        action = params.get("subtype") or params.get("type") or params.get("action")
        if not action:
            return {"success": False, "error": "No action specified"}

        try:
            if action == "click":
                await self.click(
                    params.get("x", 0), params.get("y", 0),
                    button=params.get("button", "left"),
                    clicks=params.get("clicks", 1)
                )
            elif action == "move":
                await self.move(params.get("x", 0), params.get("y", 0), params.get("duration"))
            elif action == "type":
                await self.type(params.get("text", ""), params.get("interval"))
            elif action == "key":
                await self.key(params.get("key", ""), params.get("hold", False))
            elif action == "hotkey":
                await self.hotkey(*params.get("keys", []))
            elif action == "scroll":
                await self.scroll(params.get("clicks", 1), params.get("x"), params.get("y"))
            elif action == "drag":
                await self.drag(params.get("x", 0), params.get("y", 0), 
                               params.get("button", "left"), params.get("duration"))
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
            
            return {"success": True}
        except Exception as e:
            LOG.exception(f"Error in execute({action})")
            return {"success": False, "error": str(e)}

    # ==================== Private Helpers ====================

    async def _run_input(self, fn):
        """Run blocking function in thread pool."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, fn)
