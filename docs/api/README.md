# Daur AI API Reference

This directory contains comprehensive API documentation for all Daur AI modules and components.

## API Documentation Structure

The API documentation is organized by functional area to help developers quickly find the methods and classes they need.

### Core APIs

**Agent API** (`agent-api.md`)  
The core agent system that orchestrates all AI operations, task planning, and execution. This is the primary interface for controlling Daur AI.

**Input Control API** (`input-api.md`)  
Complete control over mouse, keyboard, and touch inputs across all supported platforms. Enables programmatic control of any application or interface.

**Vision API** (`vision-api.md`)  
Screen analysis, OCR, object detection, and visual understanding capabilities. Powers the agent's ability to "see" and understand screen content.

**Browser Automation API** (`browser-api.md`)  
Web automation using Playwright with advanced features for scraping, form filling, and complex web workflows.

**System API** (`system-api.md`)  
System integration methods for file operations, process management, and OS-level interactions.

### Specialized APIs

**Billing API** (`billing-api.md`)  
User management, subscription handling, and payment processing integration.

**Security API** (`security-api.md`)  
Authentication, authorization, encryption, and role-based access control (RBAC).

**Telegram API** (`telegram-api.md`)  
Integration with Telegram for notifications, commands, and bot interactions.

**Plugin API** (`plugin-api.md`)  
Plugin system for extending Daur AI with custom functionality.

## API Usage Patterns

All Daur AI APIs follow consistent patterns for ease of use:

### Async/Await Pattern

All I/O operations use Python's async/await pattern for optimal performance:

```python
import asyncio
from src.agent.agent_core import AgentCore

async def main():
    agent = AgentCore()
    await agent.initialize()
    result = await agent.execute_task("Open Chrome and navigate to example.com")
    print(result)

asyncio.run(main())
```

### Error Handling

All APIs use specific exception types for clear error handling:

```python
from src.exceptions import AgentException, InputControlException

try:
    await agent.execute_task(task)
except AgentException as e:
    print(f"Agent error: {e}")
except InputControlException as e:
    print(f"Input control error: {e}")
```

### Configuration

APIs accept configuration through standardized config objects:

```python
from src.config import AgentConfig

config = AgentConfig(
    model="gpt-4",
    max_tokens=4096,
    temperature=0.7
)
agent = AgentCore(config=config)
```

## Quick Reference

### Most Common Operations

**Execute a task**
```python
result = await agent.execute_task("Your task description")
```

**Control mouse/keyboard**
```python
from src.input_controller import InputController
controller = InputController()
await controller.click(x=100, y=200)
await controller.type_text("Hello World")
```

**Analyze screen**
```python
from src.vision.vision_core import VisionCore
vision = VisionCore()
text = await vision.extract_text_from_screen()
```

**Automate browser**
```python
from src.browser.browser_automation import BrowserAutomation
browser = BrowserAutomation()
await browser.navigate("https://example.com")
await browser.fill_form({"username": "user", "password": "pass"})
```

## API Stability

Daur AI follows semantic versioning for API stability:

- **Major version** (2.x.x) - Breaking API changes
- **Minor version** (x.1.x) - New features, backward compatible
- **Patch version** (x.x.1) - Bug fixes, backward compatible

Current API version: **2.0.0**

## Getting Help

- Review the detailed API documentation for each module
- Check code examples in the `examples/` directory
- See the [Developer Guide](../dev/developer_guide.md) for advanced usage
- Report API issues on [GitHub](https://github.com/daurfinance/Daur-AI-v1/issues)

---

*Last updated: 2025-11-12*

