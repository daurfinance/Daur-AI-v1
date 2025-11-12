from typing import Dict, Any, Optional, List, Type
import importlib.util
import logging
from pathlib import Path
import json
from abc import ABC, abstractmethod

class PluginBase(ABC):
    """Базовый класс для всех плагинов."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Инициализация плагина."""
        pass
        
    @abstractmethod
    async def execute(self, command: str, args: Dict[str, Any]) -> Any:
        """Выполнение команды плагина."""
        pass
        
    @abstractmethod
    async def cleanup(self) -> None:
        """Очистка ресурсов плагина."""
        pass
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Название плагина."""
        pass
        
    @property
    @abstractmethod
    def version(self) -> str:
        """Версия плагина."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Описание плагина."""
        pass
        
    @property
    @abstractmethod
    def commands(self) -> List[str]:
        """Список поддерживаемых команд."""
        pass

class PluginManager:
    """Менеджер плагинов для системы."""
    
    def __init__(self, plugins_dir: Path):
        self.plugins_dir = plugins_dir
        self.logger = logging.getLogger(__name__)
        self.plugins: Dict[str, PluginBase] = {}
        
    async def load_plugins(self) -> None:
        """Загружает все плагины из директории."""
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
                
            # Проверяем наличие необходимых файлов
            manifest_path = plugin_dir / "manifest.json"
            main_path = plugin_dir / "main.py"
            
            if not (manifest_path.exists() and main_path.exists()):
                self.logger.warning(f"Invalid plugin structure in {plugin_dir}")
                continue
                
            try:
                # Загружаем манифест
                with open(manifest_path, 'r') as f:
                    manifest = json.load(f)
                    
                # Загружаем модуль плагина
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{plugin_dir.name}",
                    main_path
                )
                if spec is None or spec.loader is None:
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Создаем экземпляр плагина
                plugin_class: Type[PluginBase] = getattr(module, manifest["main_class"])
                plugin = plugin_class(manifest.get("config", {}))
                
                # Инициализируем плагин
                if await plugin.initialize():
                    self.plugins[plugin.name] = plugin
                    self.logger.info(f"Loaded plugin: {plugin.name} v{plugin.version}")
                else:
                    self.logger.error(f"Failed to initialize plugin: {plugin.name}")
                    
            except Exception as e:
                self.logger.error(f"Error loading plugin from {plugin_dir}: {e}")
                
    async def execute_command(self, 
                            plugin_name: str, 
                            command: str, 
                            args: Dict[str, Any]) -> Any:
        """Выполняет команду плагина.
        
        Args:
            plugin_name: Название плагина
            command: Команда для выполнения
            args: Аргументы команды
            
        Returns:
            Результат выполнения команды
        """
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            raise ValueError(f"Plugin {plugin_name} not found")
            
        if command not in plugin.commands:
            raise ValueError(f"Command {command} not supported by plugin {plugin_name}")
            
        return await plugin.execute(command, args)
        
    def get_plugin(self, name: str) -> Optional[PluginBase]:
        """Возвращает плагин по имени."""
        return self.plugins.get(name)
        
    def list_plugins(self) -> List[Dict[str, str]]:
        """Возвращает список установленных плагинов."""
        return [
            {
                "name": plugin.name,
                "version": plugin.version,
                "description": plugin.description
            }
            for plugin in self.plugins.values()
        ]
        
    async def cleanup(self) -> None:
        """Очищает ресурсы всех плагинов."""
        for plugin in self.plugins.values():
            try:
                await plugin.cleanup()
            except Exception as e:
                self.logger.error(f"Error cleaning up plugin {plugin.name}: {e}")
                
class PluginTemplate:
    """Шаблон для создания нового плагина."""
    
    @staticmethod
    def create_plugin(path: Path, 
                     name: str,
                     description: str,
                     version: str = "1.0.0") -> None:
        """Создает структуру нового плагина.
        
        Args:
            path: Путь для создания плагина
            name: Название плагина
            description: Описание плагина
            version: Версия плагина
        """
        plugin_dir = path / name
        plugin_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем manifest.json
        manifest = {
            "name": name,
            "version": version,
            "description": description,
            "main_class": f"{name.title()}Plugin",
            "config": {}
        }
        
        with open(plugin_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)
            
        # Создаем main.py
        main_content = f'''from typing import Dict, Any, List
from plugin_system import PluginBase

class {name.title()}Plugin(PluginBase):
    """
    {description}
    """
    
    async def initialize(self) -> bool:
        """Инициализация плагина."""
        return True
        
    async def execute(self, command: str, args: Dict[str, Any]) -> Any:
        """Выполнение команды плагина."""
        if command == "example":
            return "Hello from {name}!"
        raise ValueError(f"Unknown command: {{command}}")
        
    async def cleanup(self) -> None:
        """Очистка ресурсов плагина."""
        pass
        
    @property
    def name(self) -> str:
        return "{name}"
        
    @property
    def version(self) -> str:
        return "{version}"
        
    @property
    def description(self) -> str:
        return "{description}"
        
    @property
    def commands(self) -> List[str]:
        return ["example"]
'''
        
        with open(plugin_dir / "main.py", 'w') as f:
            f.write(main_content)
            
        # Создаем README.md
        readme_content = f'''# {name}

{description}

## Installation

1. Copy this folder to your plugins directory
2. Restart the application

## Usage

Example command:
```python
result = await plugin_manager.execute_command("{name}", "example", {{}})
print(result)  # Outputs: "Hello from {name}!"
```

## Commands

- `example`: Example command that returns a greeting

## Configuration

No configuration required.

## Version History

- {version}: Initial release
'''
        
        with open(plugin_dir / "README.md", 'w') as f:
            f.write(readme_content)