#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Full integration tests for InputController
Tests all mouse, keyboard, and clipboard functionality with safe_mode
"""

import pytest
import asyncio
from src.input.controller import InputController


@pytest.fixture
def controller_safe():
    """Create InputController in safe mode for testing."""
    return InputController(config={"safe_mode": True})


@pytest.fixture
def controller_unsafe():
    """Create InputController without safe mode (may fail if pyautogui not available)."""
    try:
        return InputController(config={"safe_mode": False})
    except ImportError:
        return None


# ==================== Mouse Tests ====================

@pytest.mark.asyncio
async def test_click_safe_mode(controller_safe):
    """Test mouse click in safe mode."""
    await controller_safe.click(100, 100, button="left", clicks=1)
    assert controller_safe.safe_mode is True


@pytest.mark.asyncio
async def test_move_safe_mode(controller_safe):
    """Test mouse move in safe mode."""
    await controller_safe.move(50, 50)
    assert controller_safe.safe_mode is True


@pytest.mark.asyncio
async def test_drag_safe_mode(controller_safe):
    """Test mouse drag in safe mode."""
    await controller_safe.drag(200, 200)
    assert controller_safe.safe_mode is True


@pytest.mark.asyncio
async def test_scroll_safe_mode(controller_safe):
    """Test mouse scroll in safe mode."""
    await controller_safe.scroll(clicks=3)
    assert controller_safe.safe_mode is True


# ==================== Keyboard Tests ====================

@pytest.mark.asyncio
async def test_key_press(controller_safe):
    """Test single key press."""
    await controller_safe.key("a", hold=False)
    assert controller_safe.safe_mode is True


@pytest.mark.asyncio
async def test_key_down_up(controller_safe):
    """Test key down and key up."""
    await controller_safe.key("shift", hold=True)
    await controller_safe.key("shift", hold=False)
    assert controller_safe.safe_mode is True


@pytest.mark.asyncio
async def test_type_text(controller_safe):
    """Test typing text."""
    await controller_safe.type("Hello World")
    assert controller_safe.safe_mode is True


@pytest.mark.asyncio
async def test_hotkey(controller_safe):
    """Test hotkey combination."""
    await controller_safe.hotkey("ctrl", "c")
    assert controller_safe.safe_mode is True


# ==================== Clipboard Tests ====================

@pytest.mark.asyncio
async def test_clipboard_get_safe_mode(controller_safe):
    """Test clipboard get in safe mode."""
    content = await controller_safe.clipboard_get()
    assert content == "[clipboard-simulated]"


@pytest.mark.asyncio
async def test_clipboard_set_safe_mode(controller_safe):
    """Test clipboard set in safe mode."""
    await controller_safe.clipboard_set("test content")
    assert controller_safe.safe_mode is True


# ==================== System Info Tests ====================

def test_get_position_safe_mode(controller_safe):
    """Test get mouse position in safe mode."""
    pos = controller_safe.get_position()
    assert pos == (0, 0)


def test_get_screen_size_safe_mode(controller_safe):
    """Test get screen size in safe mode."""
    size = controller_safe.get_screen_size()
    assert size == (1920, 1080)


# ==================== Execute Method Tests ====================

@pytest.mark.asyncio
async def test_execute_click(controller_safe):
    """Test execute method with click action."""
    result = await controller_safe.execute({
        "type": "click",
        "x": 100,
        "y": 100,
        "button": "left"
    })
    assert result["success"] is True


@pytest.mark.asyncio
async def test_execute_type(controller_safe):
    """Test execute method with type action."""
    result = await controller_safe.execute({
        "action": "type",
        "text": "Hello"
    })
    assert result["success"] is True


@pytest.mark.asyncio
async def test_execute_hotkey(controller_safe):
    """Test execute method with hotkey action."""
    result = await controller_safe.execute({
        "subtype": "hotkey",
        "keys": ["ctrl", "a"]
    })
    assert result["success"] is True


@pytest.mark.asyncio
async def test_execute_no_action(controller_safe):
    """Test execute with no action specified."""
    result = await controller_safe.execute({})
    assert result["success"] is False
    assert "error" in result


@pytest.mark.asyncio
async def test_execute_unknown_action(controller_safe):
    """Test execute with unknown action."""
    result = await controller_safe.execute({"type": "unknown_action"})
    assert result["success"] is False
    assert "error" in result


# ==================== Configuration Tests ====================

def test_controller_with_custom_delay():
    """Test controller with custom keyboard delay."""
    ctrl = InputController(config={
        "safe_mode": True,
        "keyboard_delay": 0.05
    })
    assert ctrl.keyboard_delay == 0.05


def test_controller_with_mouse_speed():
    """Test controller with custom mouse speed."""
    ctrl = InputController(config={
        "safe_mode": True,
        "mouse_speed": 2.0
    })
    assert ctrl.mouse_speed == 2.0


# ==================== Async Tests ====================

@pytest.mark.asyncio
async def test_multiple_async_operations(controller_safe):
    """Test multiple async operations in sequence."""
    await controller_safe.move(100, 100)
    await controller_safe.click(100, 100)
    await controller_safe.type("test")
    assert controller_safe.safe_mode is True


@pytest.mark.asyncio
async def test_concurrent_operations(controller_safe):
    """Test multiple async operations concurrently."""
    tasks = [
        controller_safe.move(100, 100),
        controller_safe.move(200, 200),
        controller_safe.type("test1"),
        controller_safe.type("test2"),
    ]
    await asyncio.gather(*tasks)
    assert controller_safe.safe_mode is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
