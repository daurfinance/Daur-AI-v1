# Input Control API

The Input Control API provides complete programmatic control over mouse, keyboard, and touch inputs across all supported platforms (Windows, macOS, Linux, Android, iOS).

## Overview

The `InputController` class enables Daur AI to interact with any application or interface by simulating human input. It supports precise mouse movements, keyboard input, touch gestures, and complex input sequences.

## Class: InputController

### Initialization

```python
from src.input_controller import InputController

# Basic initialization
controller = InputController()

# With platform-specific configuration
controller = InputController(platform="windows", precision_mode=True)
```

## Mouse Control

### click()

Perform a mouse click at specified coordinates.

**Signature:**
```python
async def click(
    self,
    x: int,
    y: int,
    button: str = "left",
    clicks: int = 1,
    interval: float = 0.0
) -> None
```

**Parameters:**
- `x` (int): X coordinate in pixels
- `y` (int): Y coordinate in pixels
- `button` (str): Mouse button ("left", "right", "middle")
- `clicks` (int): Number of clicks (default: 1)
- `interval` (float): Interval between clicks in seconds

**Example:**
```python
# Single left click
await controller.click(100, 200)

# Double click
await controller.click(100, 200, clicks=2, interval=0.1)

# Right click
await controller.click(100, 200, button="right")
```

---

### move()

Move mouse cursor to specified coordinates.

**Signature:**
```python
async def move(
    self,
    x: int,
    y: int,
    duration: float = 0.0,
    smooth: bool = True
) -> None
```

**Parameters:**
- `x` (int): Target X coordinate
- `y` (int): Target Y coordinate
- `duration` (float): Movement duration in seconds (0 = instant)
- `smooth` (bool): Use smooth human-like movement curve

**Example:**
```python
# Instant movement
await controller.move(500, 300)

# Smooth movement over 1 second
await controller.move(500, 300, duration=1.0, smooth=True)
```

---

### drag()

Drag from one position to another.

**Signature:**
```python
async def drag(
    self,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration: float = 0.5,
    button: str = "left"
) -> None
```

**Parameters:**
- `start_x`, `start_y` (int): Starting coordinates
- `end_x`, `end_y` (int): Ending coordinates
- `duration` (float): Drag duration in seconds
- `button` (str): Mouse button to hold

**Example:**
```python
# Drag to select text or move window
await controller.drag(100, 100, 300, 100, duration=0.5)
```

---

### scroll()

Scroll mouse wheel.

**Signature:**
```python
async def scroll(
    self,
    clicks: int,
    x: Optional[int] = None,
    y: Optional[int] = None
) -> None
```

**Parameters:**
- `clicks` (int): Number of scroll clicks (positive = up, negative = down)
- `x`, `y` (int, optional): Position to scroll at (default: current position)

**Example:**
```python
# Scroll down 5 clicks
await controller.scroll(-5)

# Scroll up at specific position
await controller.scroll(3, x=500, y=300)
```

---

### get_position()

Get current mouse cursor position.

**Signature:**
```python
def get_position(self) -> Tuple[int, int]
```

**Returns:**
- `Tuple[int, int]`: Current (x, y) coordinates

**Example:**
```python
x, y = controller.get_position()
print(f"Mouse at ({x}, {y})")
```

---

## Keyboard Control

### type_text()

Type text string with optional delays.

**Signature:**
```python
async def type_text(
    self,
    text: str,
    interval: float = 0.0,
    human_like: bool = True
) -> None
```

**Parameters:**
- `text` (str): Text to type
- `interval` (float): Delay between keystrokes in seconds
- `human_like` (bool): Add random variations to simulate human typing

**Example:**
```python
# Fast typing
await controller.type_text("Hello World")

# Slow, human-like typing
await controller.type_text("Hello World", interval=0.1, human_like=True)
```

---

### press()

Press and release a key or key combination.

**Signature:**
```python
async def press(
    self,
    *keys: str,
    interval: float = 0.0
) -> None
```

**Parameters:**
- `*keys` (str): Key(s) to press (supports modifiers)
- `interval` (float): Delay between key presses

**Example:**
```python
# Single key
await controller.press("enter")

# Key combination
await controller.press("ctrl", "c")  # Copy
await controller.press("ctrl", "v")  # Paste
await controller.press("ctrl", "shift", "n")  # Complex combo
```

---

### hold()

Hold a key down.

**Signature:**
```python
async def hold(self, key: str) -> None
```

**Parameters:**
- `key` (str): Key to hold down

**Example:**
```python
await controller.hold("shift")
await controller.click(100, 100)  # Click while holding shift
await controller.release("shift")
```

---

### release()

Release a held key.

**Signature:**
```python
async def release(self, key: str) -> None
```

**Parameters:**
- `key` (str): Key to release

---

### hotkey()

Press a hotkey combination.

**Signature:**
```python
async def hotkey(self, *keys: str) -> None
```

**Parameters:**
- `*keys` (str): Keys in the hotkey combination

**Example:**
```python
# Save file
await controller.hotkey("ctrl", "s")

# Switch application
await controller.hotkey("alt", "tab")

# Screenshot on macOS
await controller.hotkey("cmd", "shift", "4")
```

---

## Touch Control (Mobile)

### tap()

Perform a tap gesture on touch screen.

**Signature:**
```python
async def tap(
    self,
    x: int,
    y: int,
    taps: int = 1,
    duration: float = 0.1
) -> None
```

**Parameters:**
- `x`, `y` (int): Tap coordinates
- `taps` (int): Number of taps
- `duration` (float): Tap duration in seconds

**Example:**
```python
# Single tap
await controller.tap(200, 400)

# Double tap
await controller.tap(200, 400, taps=2)
```

---

### swipe()

Perform a swipe gesture.

**Signature:**
```python
async def swipe(
    self,
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration: float = 0.3
) -> None
```

**Parameters:**
- `start_x`, `start_y` (int): Starting coordinates
- `end_x`, `end_y` (int): Ending coordinates
- `duration` (float): Swipe duration in seconds

**Example:**
```python
# Swipe left
await controller.swipe(300, 500, 100, 500, duration=0.3)

# Swipe up to scroll
await controller.swipe(200, 600, 200, 200, duration=0.5)
```

---

### pinch()

Perform a pinch gesture (zoom in/out).

**Signature:**
```python
async def pinch(
    self,
    center_x: int,
    center_y: int,
    distance: int,
    direction: str = "in"
) -> None
```

**Parameters:**
- `center_x`, `center_y` (int): Center point of pinch
- `distance` (int): Pinch distance in pixels
- `direction` (str): "in" for zoom out, "out" for zoom in

**Example:**
```python
# Zoom in
await controller.pinch(400, 300, distance=200, direction="out")

# Zoom out
await controller.pinch(400, 300, distance=200, direction="in")
```

---

## Advanced Features

### record_sequence()

Record a sequence of input actions for replay.

**Signature:**
```python
async def record_sequence(self, name: str) -> None
```

**Parameters:**
- `name` (str): Name for the recorded sequence

**Example:**
```python
await controller.record_sequence("login_flow")
# Perform actions...
await controller.stop_recording()
```

---

### replay_sequence()

Replay a recorded input sequence.

**Signature:**
```python
async def replay_sequence(
    self,
    name: str,
    speed: float = 1.0
) -> None
```

**Parameters:**
- `name` (str): Name of sequence to replay
- `speed` (float): Playback speed multiplier

**Example:**
```python
await controller.replay_sequence("login_flow", speed=2.0)
```

---

### wait_for_idle()

Wait for user input to become idle.

**Signature:**
```python
async def wait_for_idle(self, timeout: float = 5.0) -> bool
```

**Parameters:**
- `timeout` (float): Maximum wait time in seconds

**Returns:**
- `bool`: True if idle detected, False if timeout

**Example:**
```python
# Wait for user to stop typing
if await controller.wait_for_idle(timeout=10.0):
    print("User input idle")
```

---

## Platform-Specific Features

### Windows

```python
# Send Windows key
await controller.press("win")

# Windows + R (Run dialog)
await controller.hotkey("win", "r")
```

### macOS

```python
# Command key
await controller.press("cmd")

# Spotlight search
await controller.hotkey("cmd", "space")
```

### Linux

```python
# Super key
await controller.press("super")
```

---

## Error Handling

```python
from src.exceptions import InputControlException

try:
    await controller.click(x, y)
except InputControlException as e:
    print(f"Input control error: {e}")
```

---

## Best Practices

**Coordinate Validation**  
Always validate coordinates are within screen bounds before clicking or moving.

**Timing**  
Add appropriate delays between actions to allow UI to respond. Use `await asyncio.sleep()` when needed.

**Human-like Behavior**  
Enable `human_like` mode for typing and `smooth` mode for mouse movements to avoid detection as automation.

**Platform Detection**  
The controller automatically detects the platform, but you can override for testing.

**Error Recovery**  
Implement retry logic for critical input operations as they can fail due to timing or UI state.

---

## Complete Example

```python
import asyncio
from src.input_controller import InputController

async def automate_login():
    controller = InputController()
    
    # Click username field
    await controller.click(300, 200)
    await asyncio.sleep(0.5)
    
    # Type username
    await controller.type_text("user@example.com", human_like=True)
    
    # Tab to password field
    await controller.press("tab")
    await asyncio.sleep(0.3)
    
    # Type password
    await controller.type_text("password123", human_like=True)
    
    # Click login button
    await controller.click(300, 350)
    
    print("Login sequence completed")

asyncio.run(automate_login())
```

---

*API Version: 2.0.0*  
*Last Updated: 2025-11-12*

