# 🚀 Daur-AI Getting Started Guide

## Installation

### Prerequisites
- Python 3.8+
- pip or conda
- Git

### Step 1: Clone Repository
```bash
git clone https://github.com/daurfinance/Daur-AI-v1.git
cd Daur-AI-v1
```

### Step 2: Install Dependencies

#### macOS/Linux:
```bash
pip install -e .
# or
pip install -r requirements.txt
```

#### Windows (PowerShell):
```powershell
pip install -e .
```

### Step 3: Verify Installation
```bash
python run_demo.py
```

You should see:
```
✓ InputController: PASSED
✓ Agent Core: PASSED
✓ Integrated Agent: PASSED
✓ Action Execution: PASSED
✓ Concurrent Operations: PASSED

Total: 5/5 tests passed
```

## Quick Examples

### Example 1: Basic Mouse & Keyboard
```python
from src.input.controller import InputController
import asyncio

async def example():
    controller = InputController(config={"safe_mode": True})
    
    # Mouse operations
    await controller.click(100, 100)
    await controller.move(200, 200)
    
    # Keyboard operations
    await controller.type("Hello!")
    await controller.hotkey("ctrl", "a")

asyncio.run(example())
```

### Example 2: Using the Agent
```python
from src.agent.core import DaurAgent

agent = DaurAgent(config={"input": {"safe_mode": True}})
agent.start()

# Submit commands
agent.submit_command({
    "type": "click",
    "x": 100,
    "y": 100
})

# Stop agent
agent.stop()
```

### Example 3: Safe Mode Testing
```python
# Safe mode simulates actions without actually running them
controller = InputController(config={"safe_mode": True})

await controller.click(100, 100)  # Logged but not executed
await controller.type("test")     # Logged but not executed
```

## Configuration

### InputController Config
```python
config = {
    "safe_mode": False,           # True = simulate, False = real
    "keyboard_delay": 0.01,       # Delay between keystrokes (seconds)
    "mouse_speed": 1.0            # Mouse movement speed multiplier
}

controller = InputController(config=config)
```

### Agent Config
```python
config = {
    "input": {
        "safe_mode": True,
        "keyboard_delay": 0.05
    },
    "ai": {
        "model": "ollama"  # or "openai"
    },
    "logging": {
        "level": "DEBUG"
    }
}

agent = DaurAgent(config=config)
```

## Troubleshooting

### Issue: "pyautogui not found"
```bash
pip install pyautogui
```

### Issue: "pyperclip not found"
```bash
pip install pyperclip
```

### Issue: Linux X11 issues
```bash
pip install python-xlib
```

### Issue: Can't click/type on macOS
Use safe_mode for testing, or ensure accessibility permissions are granted:
- System Preferences → Security & Privacy → Accessibility → Allow terminal apps

## Next Steps

1. **Run Tests**: `python -m pytest tests/ -v`
2. **Run Demo**: `python run_demo.py`
3. **Try Examples**: `python examples/quickstart.py`
4. **Read Docs**: Check `/docs` for full documentation

## Support

- 📖 Docs: `/docs`
- 🧪 Tests: `/tests`
- 📝 Examples: `/examples`
- 🐛 Issues: GitHub Issues
