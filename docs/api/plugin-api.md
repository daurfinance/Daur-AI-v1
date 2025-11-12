# Plugin Development API

**Version**: 2.0  
**Last Updated**: 2025-11-12  
**Status**: Production Ready

---

## Overview

The Plugin Development API enables developers to extend Daur AI functionality through custom plugins. Plugins can add new automation capabilities, integrate with external services, process data in custom ways, and enhance the system without modifying core code.

This comprehensive guide covers plugin architecture, development workflow, best practices, and provides complete examples for creating production-ready plugins.

---

## Table of Contents

1. [Plugin Architecture](#plugin-architecture)
2. [Plugin Lifecycle](#plugin-lifecycle)
3. [Creating Plugins](#creating-plugins)
4. [Plugin API Reference](#plugin-api-reference)
5. [Configuration](#configuration)
6. [Data Storage](#data-storage)
7. [Event Handling](#event-handling)
8. [Testing Plugins](#testing-plugins)
9. [Publishing Plugins](#publishing-plugins)
10. [Examples](#examples)

---

## Plugin Architecture

### Plugin Structure

A Daur AI plugin is a Python module that implements the `PluginBase` interface. Plugins are loaded dynamically at runtime and can interact with the core system through well-defined APIs.

```
my_plugin/
├── __init__.py
├── plugin.py          # Main plugin class
├── config.json        # Plugin configuration
├── requirements.txt   # Dependencies
├── README.md          # Documentation
└── tests/
    └── test_plugin.py # Unit tests
```

### Plugin Base Class

```python
from src.system.plugin_base import PluginBase

class MyPlugin(PluginBase):
    """
    Custom plugin implementation.
    
    All plugins must inherit from PluginBase and implement
    required methods: initialize(), execute(), cleanup()
    """
    
    def __init__(self):
        super().__init__()
        self.name = "MyPlugin"
        self.version = "1.0.0"
        self.author = "Your Name"
        self.description = "Plugin description"
    
    def initialize(self) -> bool:
        """
        Initialize plugin resources.
        
        Called once when plugin is loaded.
        
        Returns:
            True if initialization successful
        """
        return True
    
    def execute(self, *args, **kwargs) -> Any:
        """
        Execute plugin functionality.
        
        Called each time plugin is invoked.
        
        Returns:
            Plugin execution result
        """
        return {"status": "success"}
    
    def cleanup(self) -> None:
        """
        Cleanup plugin resources.
        
        Called when plugin is unloaded.
        """
        pass
```

---

## Plugin Lifecycle

### Lifecycle Stages

Plugins go through several stages during their lifetime:

| Stage | Description | Method Called |
|-------|-------------|---------------|
| **Registration** | Plugin discovered and registered | `__init__()` |
| **Initialization** | Plugin resources allocated | `initialize()` |
| **Execution** | Plugin performs work | `execute()` |
| **Cleanup** | Plugin resources released | `cleanup()` |
| **Unload** | Plugin removed from system | (automatic) |

### Lifecycle Hooks

```python
class AdvancedPlugin(PluginBase):
    """Plugin with all lifecycle hooks."""
    
    def on_load(self) -> None:
        """Called immediately after plugin is loaded."""
        self.logger.info(f"{self.name} loaded")
    
    def on_enable(self) -> None:
        """Called when plugin is enabled."""
        self.logger.info(f"{self.name} enabled")
    
    def on_disable(self) -> None:
        """Called when plugin is disabled."""
        self.logger.info(f"{self.name} disabled")
    
    def on_unload(self) -> None:
        """Called before plugin is unloaded."""
        self.logger.info(f"{self.name} unloading")
```

---

## Creating Plugins

### Minimal Plugin

```python
from src.system.plugin_base import PluginBase

class HelloWorldPlugin(PluginBase):
    """Minimal plugin example."""
    
    def __init__(self):
        super().__init__()
        self.name = "HelloWorld"
        self.version = "1.0.0"
    
    def initialize(self) -> bool:
        self.logger.info("HelloWorld plugin initialized")
        return True
    
    def execute(self, name: str = "World") -> str:
        return f"Hello, {name}!"
    
    def cleanup(self) -> None:
        self.logger.info("HelloWorld plugin cleaned up")
```

### Plugin with Configuration

```python
from src.system.plugin_base import PluginBase
from pathlib import Path
import json

class ConfigurablePlugin(PluginBase):
    """Plugin with configuration support."""
    
    def __init__(self):
        super().__init__()
        self.name = "ConfigurablePlugin"
        self.version = "1.0.0"
        self.config = {}
    
    def initialize(self) -> bool:
        # Load configuration
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            with open(config_path) as f:
                self.config = json.load(f)
        
        # Validate configuration
        required_keys = ["api_key", "endpoint"]
        for key in required_keys:
            if key not in self.config:
                self.logger.error(f"Missing required config: {key}")
                return False
        
        return True
    
    def execute(self, **kwargs):
        # Use configuration
        api_key = self.config['api_key']
        endpoint = self.config['endpoint']
        
        # Perform work
        result = self.call_api(endpoint, api_key)
        return result
```

### Plugin with Dependencies

```python
# requirements.txt
requests>=2.28.0
beautifulsoup4>=4.11.0

# plugin.py
from src.system.plugin_base import PluginBase
import requests
from bs4 import BeautifulSoup

class WebScraperPlugin(PluginBase):
    """Plugin with external dependencies."""
    
    def __init__(self):
        super().__init__()
        self.name = "WebScraper"
        self.version = "1.0.0"
        self.dependencies = ["requests", "beautifulsoup4"]
    
    def initialize(self) -> bool:
        # Verify dependencies
        try:
            import requests
            import bs4
            return True
        except ImportError as e:
            self.logger.error(f"Missing dependency: {e}")
            return False
    
    def execute(self, url: str) -> dict:
        """Scrape webpage."""
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        return {
            "title": soup.title.string if soup.title else None,
            "links": [a['href'] for a in soup.find_all('a', href=True)]
        }
```

---

## Plugin API Reference

### PluginBase Methods

```python
class PluginBase:
    """Base class for all plugins."""
    
    # Required methods (must override)
    def initialize(self) -> bool:
        """Initialize plugin. Return True if successful."""
        pass
    
    def execute(self, *args, **kwargs) -> Any:
        """Execute plugin functionality."""
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass
    
    # Utility methods (available to plugins)
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        pass
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value."""
        pass
    
    def get_data_dir(self) -> Path:
        """Get plugin data directory."""
        pass
    
    def emit_event(self, event_type: str, data: Any = None) -> None:
        """Emit an event."""
        pass
    
    def subscribe_event(self, event_type: str, callback: Callable) -> str:
        """Subscribe to an event."""
        pass
    
    def call_api(self, endpoint: str, **kwargs) -> Any:
        """Call system API."""
        pass
```

### Plugin Metadata

```python
class MyPlugin(PluginBase):
    """Plugin with complete metadata."""
    
    def __init__(self):
        super().__init__()
        
        # Required metadata
        self.name = "MyPlugin"
        self.version = "1.0.0"
        
        # Optional metadata
        self.author = "Your Name"
        self.email = "you@example.com"
        self.description = "Detailed plugin description"
        self.homepage = "https://github.com/you/my-plugin"
        self.license = "MIT"
        self.tags = ["automation", "web", "data"]
        
        # Dependencies
        self.dependencies = ["requests", "pandas"]
        self.min_system_version = "2.0.0"
```

---

## Configuration

### Plugin Configuration File

```json
{
  "name": "MyPlugin",
  "version": "1.0.0",
  "enabled": true,
  "settings": {
    "api_key": "your_api_key_here",
    "endpoint": "https://api.example.com",
    "timeout": 30,
    "retry_attempts": 3
  },
  "permissions": [
    "network_access",
    "file_read",
    "file_write"
  ]
}
```

### Accessing Configuration

```python
class MyPlugin(PluginBase):
    """Plugin using configuration."""
    
    def initialize(self) -> bool:
        # Get configuration values
        self.api_key = self.get_config("settings.api_key")
        self.endpoint = self.get_config("settings.endpoint")
        self.timeout = self.get_config("settings.timeout", default=30)
        
        return True
    
    def execute(self, **kwargs):
        # Use configuration
        response = requests.get(
            self.endpoint,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=self.timeout
        )
        return response.json()
```

---

## Data Storage

### Plugin Data Directory

```python
class DataStoragePlugin(PluginBase):
    """Plugin with data storage."""
    
    def initialize(self) -> bool:
        # Get plugin data directory
        self.data_dir = self.get_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self.db_path = self.data_dir / "plugin.db"
        self.init_database()
        
        return True
    
    def save_data(self, key: str, value: Any) -> None:
        """Save data to plugin storage."""
        file_path = self.data_dir / f"{key}.json"
        with open(file_path, 'w') as f:
            json.dump(value, f)
    
    def load_data(self, key: str) -> Any:
        """Load data from plugin storage."""
        file_path = self.data_dir / f"{key}.json"
        if file_path.exists():
            with open(file_path) as f:
                return json.load(f)
        return None
```

### Database Integration

```python
import sqlite3

class DatabasePlugin(PluginBase):
    """Plugin with database."""
    
    def initialize(self) -> bool:
        db_path = self.get_data_dir() / "plugin.db"
        self.conn = sqlite3.connect(str(db_path))
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
        
        return True
    
    def execute(self, action: str, **kwargs):
        if action == "save":
            self.cursor.execute(
                "INSERT INTO records (data) VALUES (?)",
                (kwargs.get('data'),)
            )
            self.conn.commit()
            return {"status": "saved"}
        
        elif action == "list":
            self.cursor.execute("SELECT * FROM records")
            return self.cursor.fetchall()
    
    def cleanup(self) -> None:
        if hasattr(self, 'conn'):
            self.conn.close()
```

---

## Event Handling

### Emitting Events

```python
class EventEmitterPlugin(PluginBase):
    """Plugin that emits events."""
    
    def execute(self, task: str):
        # Emit event before processing
        self.emit_event("task.started", {"task": task})
        
        try:
            # Process task
            result = self.process_task(task)
            
            # Emit success event
            self.emit_event("task.completed", {
                "task": task,
                "result": result
            })
            
            return result
            
        except Exception as e:
            # Emit error event
            self.emit_event("task.failed", {
                "task": task,
                "error": str(e)
            })
            raise
```

### Subscribing to Events

```python
class EventSubscriberPlugin(PluginBase):
    """Plugin that subscribes to events."""
    
    def initialize(self) -> bool:
        # Subscribe to system events
        self.subscribe_event("system.started", self.on_system_started)
        self.subscribe_event("task.completed", self.on_task_completed)
        
        return True
    
    def on_system_started(self, data):
        """Handle system started event."""
        self.logger.info("System started, initializing plugin...")
    
    def on_task_completed(self, data):
        """Handle task completed event."""
        task = data.get('task')
        result = data.get('result')
        self.logger.info(f"Task {task} completed with result: {result}")
```

---

## Testing Plugins

### Unit Tests

```python
# tests/test_plugin.py
import unittest
from my_plugin.plugin import MyPlugin

class TestMyPlugin(unittest.TestCase):
    """Unit tests for MyPlugin."""
    
    def setUp(self):
        """Setup test fixtures."""
        self.plugin = MyPlugin()
        self.plugin.initialize()
    
    def tearDown(self):
        """Cleanup after tests."""
        self.plugin.cleanup()
    
    def test_initialization(self):
        """Test plugin initializes correctly."""
        self.assertTrue(self.plugin.initialize())
        self.assertEqual(self.plugin.name, "MyPlugin")
    
    def test_execution(self):
        """Test plugin execution."""
        result = self.plugin.execute(param="value")
        self.assertIsNotNone(result)
        self.assertEqual(result['status'], 'success')
    
    def test_configuration(self):
        """Test configuration loading."""
        config_value = self.plugin.get_config("test_key")
        self.assertIsNotNone(config_value)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```python
# tests/test_integration.py
import unittest
from src.system.plugin_manager import PluginManager
from my_plugin.plugin import MyPlugin

class TestPluginIntegration(unittest.TestCase):
    """Integration tests for plugin."""
    
    def setUp(self):
        self.plugin_manager = PluginManager()
        self.plugin_manager.load_plugin("my_plugin")
    
    def test_plugin_loaded(self):
        """Test plugin loads correctly."""
        plugins = self.plugin_manager.get_plugins()
        self.assertIn("MyPlugin", [p['name'] for p in plugins])
    
    def test_plugin_execution(self):
        """Test plugin executes through manager."""
        result = self.plugin_manager.execute_plugin("MyPlugin", param="value")
        self.assertEqual(result['status'], 'success')
```

---

## Publishing Plugins

### Plugin Package Structure

```
my-plugin/
├── setup.py
├── README.md
├── LICENSE
├── requirements.txt
├── my_plugin/
│   ├── __init__.py
│   ├── plugin.py
│   └── config.json
└── tests/
    └── test_plugin.py
```

### setup.py

```python
from setuptools import setup, find_packages

setup(
    name="daur-ai-my-plugin",
    version="1.0.0",
    author="Your Name",
    author_email="you@example.com",
    description="My custom Daur AI plugin",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/you/my-plugin",
    packages=find_packages(),
    install_requires=[
        "daur-ai>=2.0.0",
        "requests>=2.28.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">=3.8",
)
```

### Installation

```bash
# Install from PyPI
pip install daur-ai-my-plugin

# Install from source
git clone https://github.com/you/my-plugin
cd my-plugin
pip install -e .

# Install in Daur AI
daur-ai plugin install my-plugin
```

---

## Examples

### Complete Plugin Example

```python
from src.system.plugin_base import PluginBase
import requests
from pathlib import Path
import json

class WeatherPlugin(PluginBase):
    """
    Weather information plugin.
    
    Fetches weather data from OpenWeatherMap API.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Weather"
        self.version = "1.0.0"
        self.author = "Daur AI Team"
        self.description = "Get weather information for any city"
        self.api_key = None
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def initialize(self) -> bool:
        """Initialize plugin and load API key."""
        self.api_key = self.get_config("api_key")
        
        if not self.api_key:
            self.logger.error("OpenWeatherMap API key not configured")
            return False
        
        self.logger.info("Weather plugin initialized")
        return True
    
    def execute(self, city: str, units: str = "metric") -> dict:
        """
        Get weather for a city.
        
        Args:
            city: City name
            units: Temperature units (metric/imperial)
            
        Returns:
            Weather data dictionary
        """
        try:
            # Emit event
            self.emit_event("weather.request", {"city": city})
            
            # Make API request
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Format result
            result = {
                "city": data['name'],
                "country": data['sys']['country'],
                "temperature": data['main']['temp'],
                "feels_like": data['main']['feels_like'],
                "humidity": data['main']['humidity'],
                "description": data['weather'][0]['description'],
                "wind_speed": data['wind']['speed']
            }
            
            # Emit success event
            self.emit_event("weather.success", result)
            
            # Cache result
            self.cache_weather(city, result)
            
            return result
            
        except requests.RequestException as e:
            self.logger.error(f"Weather API error: {e}")
            self.emit_event("weather.error", {"city": city, "error": str(e)})
            raise
    
    def cache_weather(self, city: str, data: dict) -> None:
        """Cache weather data."""
        cache_dir = self.get_data_dir() / "cache"
        cache_dir.mkdir(exist_ok=True)
        
        cache_file = cache_dir / f"{city.lower()}.json"
        with open(cache_file, 'w') as f:
            json.dump({
                "data": data,
                "timestamp": time.time()
            }, f)
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        self.logger.info("Weather plugin cleaned up")
```

### Advanced Plugin with Multiple Features

```python
from src.system.plugin_base import PluginBase
from typing import List, Dict
import asyncio

class AdvancedPlugin(PluginBase):
    """Advanced plugin with multiple features."""
    
    def __init__(self):
        super().__init__()
        self.name = "AdvancedPlugin"
        self.version = "2.0.0"
        self.commands = {}
    
    def initialize(self) -> bool:
        """Initialize plugin with command registration."""
        # Register commands
        self.register_command("process", self.cmd_process)
        self.register_command("analyze", self.cmd_analyze)
        self.register_command("export", self.cmd_export)
        
        # Subscribe to events
        self.subscribe_event("system.started", self.on_system_start)
        
        return True
    
    def register_command(self, name: str, handler: callable) -> None:
        """Register a command handler."""
        self.commands[name] = handler
    
    def execute(self, command: str, **kwargs) -> Any:
        """Execute a command."""
        if command not in self.commands:
            raise ValueError(f"Unknown command: {command}")
        
        return self.commands[command](**kwargs)
    
    def cmd_process(self, data: List[Dict]) -> Dict:
        """Process data command."""
        results = []
        for item in data:
            processed = self.process_item(item)
            results.append(processed)
        
        return {"processed": len(results), "results": results}
    
    def cmd_analyze(self, data: List[Dict]) -> Dict:
        """Analyze data command."""
        analysis = {
            "count": len(data),
            "summary": self.generate_summary(data),
            "insights": self.extract_insights(data)
        }
        return analysis
    
    def cmd_export(self, data: List[Dict], format: str = "json") -> str:
        """Export data command."""
        output_file = self.get_data_dir() / f"export.{format}"
        
        if format == "json":
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
        elif format == "csv":
            import csv
            with open(output_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        return str(output_file)
    
    def on_system_start(self, data):
        """Handle system start event."""
        self.logger.info("System started, plugin ready")
```

---

## See Also

- [System API](./system-api.md) - System integration
- [Agent Core API](./agent-api.md) - Agent functionality
- [Security API](./security-api.md) - Plugin security

---

**Last Updated**: 2025-11-12  
**Version**: 2.0  
**Author**: Manus AI

