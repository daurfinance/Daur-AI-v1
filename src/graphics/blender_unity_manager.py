#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль работы с Blender и Unity
Управление 3D моделями, сценами и экспортом

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import subprocess
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
import xml.etree.ElementTree as ET


class BlenderVersion(Enum):
    """Версии Blender"""
    V3_0 = "3.0"
    V3_5 = "3.5"
    V4_0 = "4.0"
    V4_1 = "4.1"


class UnityVersion(Enum):
    """Версии Unity"""
    V2020 = "2020.3"
    V2021 = "2021.3"
    V2022 = "2022.3"
    V2023 = "2023.1"


class ExportFormat(Enum):
    """Форматы экспорта"""
    FBX = "fbx"
    GLTF = "gltf"
    COLLADA = "dae"
    OBJ = "obj"
    USD = "usd"
    USDZ = "usdz"


@dataclass
class BlenderScene:
    """Сцена Blender"""
    name: str
    filepath: str
    objects: List[str] = None
    materials: List[str] = None
    lights: List[str] = None
    cameras: List[str] = None
    
    def __post_init__(self):
        if self.objects is None:
            self.objects = []
        if self.materials is None:
            self.materials = []
        if self.lights is None:
            self.lights = []
        if self.cameras is None:
            self.cameras = []


@dataclass
class UnityScene:
    """Сцена Unity"""
    name: str
    filepath: str
    game_objects: List[str] = None
    prefabs: List[str] = None
    assets: List[str] = None
    
    def __post_init__(self):
        if self.game_objects is None:
            self.game_objects = []
        if self.prefabs is None:
            self.prefabs = []
        if self.assets is None:
            self.assets = []


class BlenderManager:
    """Менеджер Blender"""
    
    def __init__(self, blender_path: Optional[str] = None):
        """
        Args:
            blender_path: Путь к исполняемому файлу Blender
        """
        self.blender_path = blender_path or self._find_blender()
        self.logger = logging.getLogger('daur_ai.blender_manager')
        self.scenes: Dict[str, BlenderScene] = {}
    
    def _find_blender(self) -> Optional[str]:
        """Найти Blender в системе"""
        common_paths = [
            '/usr/bin/blender',
            '/usr/local/bin/blender',
            '/Applications/Blender.app/Contents/MacOS/Blender',
            'C:\\Program Files\\Blender Foundation\\Blender\\blender.exe'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def is_available(self) -> bool:
        """Проверить доступность Blender"""
        return self.blender_path is not None and os.path.exists(self.blender_path)
    
    def create_scene(self, name: str, filepath: str) -> BlenderScene:
        """
        Создать новую сцену
        
        Args:
            name: Имя сцены
            filepath: Путь к файлу
            
        Returns:
            BlenderScene: Объект сцены
        """
        scene = BlenderScene(name, filepath)
        self.scenes[name] = scene
        self.logger.info(f"Сцена Blender создана: {name}")
        return scene
    
    def open_scene(self, filepath: str) -> Optional[BlenderScene]:
        """
        Открыть сцену
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            BlenderScene: Объект сцены или None
        """
        if not os.path.exists(filepath):
            self.logger.error(f"Файл не найден: {filepath}")
            return None
        
        scene_name = Path(filepath).stem
        scene = BlenderScene(scene_name, filepath)
        self.scenes[scene_name] = scene
        self.logger.info(f"Сцена открыта: {filepath}")
        return scene
    
    def run_script(self, script_path: str, args: List[str] = None) -> bool:
        """
        Запустить Python скрипт в Blender
        
        Args:
            script_path: Путь к скрипту
            args: Аргументы скрипта
            
        Returns:
            bool: Успешность выполнения
        """
        if not self.is_available():
            self.logger.error("Blender не доступен")
            return False
        
        try:
            cmd = [self.blender_path, '-b', '--python', script_path]
            if args:
                cmd.extend(args)
            
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Скрипт выполнен: {script_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка выполнения скрипта: {e}")
            return False
    
    def export_scene(self, scene_name: str, output_path: str,
                    format: ExportFormat = ExportFormat.FBX) -> bool:
        """
        Экспортировать сцену
        
        Args:
            scene_name: Имя сцены
            output_path: Путь к выходному файлу
            format: Формат экспорта
            
        Returns:
            bool: Успешность операции
        """
        if scene_name not in self.scenes:
            self.logger.error(f"Сцена не найдена: {scene_name}")
            return False
        
        if not self.is_available():
            self.logger.error("Blender не доступен")
            return False
        
        try:
            # Создаем Python скрипт для экспорта
            script = f"""
import bpy
bpy.ops.object.select_all(action='SELECT')
if '{format.value}' == 'fbx':
    bpy.ops.export_scene.fbx(filepath='{output_path}')
elif '{format.value}' == 'gltf':
    bpy.ops.export_scene.gltf(filepath='{output_path}')
elif '{format.value}' == 'obj':
    bpy.ops.export_scene.obj(filepath='{output_path}')
"""
            
            script_path = '/tmp/blender_export.py'
            with open(script_path, 'w') as f:
                f.write(script)
            
            self.run_script(script_path)
            self.logger.info(f"Сцена экспортирована: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка экспорта: {e}")
            return False
    
    def render_scene(self, scene_name: str, output_path: str,
                    resolution: Tuple[int, int] = (1920, 1080),
                    samples: int = 128) -> bool:
        """
        Отрендерить сцену
        
        Args:
            scene_name: Имя сцены
            output_path: Путь к выходному файлу
            resolution: Разрешение (ширина, высота)
            samples: Количество образцов для рендеринга
            
        Returns:
            bool: Успешность операции
        """
        if scene_name not in self.scenes:
            self.logger.error(f"Сцена не найдена: {scene_name}")
            return False
        
        if not self.is_available():
            self.logger.error("Blender не доступен")
            return False
        
        try:
            script = f"""
import bpy
scene = bpy.context.scene
scene.render.resolution_x = {resolution[0]}
scene.render.resolution_y = {resolution[1]}
scene.cycles.samples = {samples}
scene.render.filepath = '{output_path}'
bpy.ops.render.render(write_still=True)
"""
            
            script_path = '/tmp/blender_render.py'
            with open(script_path, 'w') as f:
                f.write(script)
            
            self.run_script(script_path)
            self.logger.info(f"Сцена отрендерена: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка рендеринга: {e}")
            return False


class UnityManager:
    """Менеджер Unity"""
    
    def __init__(self, unity_path: Optional[str] = None, project_path: Optional[str] = None):
        """
        Args:
            unity_path: Путь к исполняемому файлу Unity
            project_path: Путь к проекту Unity
        """
        self.unity_path = unity_path or self._find_unity()
        self.project_path = project_path
        self.logger = logging.getLogger('daur_ai.unity_manager')
        self.scenes: Dict[str, UnityScene] = {}
    
    def _find_unity(self) -> Optional[str]:
        """Найти Unity в системе"""
        common_paths = [
            '/Applications/Unity/Unity.app/Contents/MacOS/Unity',
            'C:\\Program Files\\Unity\\Hub\\Editor\\2022.3.0f1\\Editor\\Unity.exe',
            '/opt/Unity/Editor/Unity'
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def is_available(self) -> bool:
        """Проверить доступность Unity"""
        return self.unity_path is not None and os.path.exists(self.unity_path)
    
    def create_scene(self, name: str, filepath: str) -> UnityScene:
        """
        Создать новую сцену
        
        Args:
            name: Имя сцены
            filepath: Путь к файлу
            
        Returns:
            UnityScene: Объект сцены
        """
        scene = UnityScene(name, filepath)
        self.scenes[name] = scene
        self.logger.info(f"Сцена Unity создана: {name}")
        return scene
    
    def open_scene(self, filepath: str) -> Optional[UnityScene]:
        """
        Открыть сцену
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            UnityScene: Объект сцены или None
        """
        if not os.path.exists(filepath):
            self.logger.error(f"Файл не найден: {filepath}")
            return None
        
        scene_name = Path(filepath).stem
        scene = UnityScene(scene_name, filepath)
        self.scenes[scene_name] = scene
        self.logger.info(f"Сцена открыта: {filepath}")
        return scene
    
    def build_project(self, target_platform: str = 'StandaloneWindows64',
                     output_path: str = None) -> bool:
        """
        Собрать проект
        
        Args:
            target_platform: Целевая платформа
            output_path: Путь к выходному файлу
            
        Returns:
            bool: Успешность операции
        """
        if not self.is_available():
            self.logger.error("Unity не доступен")
            return False
        
        if not self.project_path:
            self.logger.error("Путь к проекту не установлен")
            return False
        
        try:
            cmd = [
                self.unity_path,
                '-projectPath', self.project_path,
                '-buildTarget', target_platform,
                '-executeMethod', 'BuildScript.Build'
            ]
            
            if output_path:
                cmd.extend(['-buildOutput', output_path])
            
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Проект собран для {target_platform}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка сборки: {e}")
            return False
    
    def run_editor(self) -> bool:
        """
        Запустить редактор Unity
        
        Returns:
            bool: Успешность операции
        """
        if not self.is_available():
            self.logger.error("Unity не доступен")
            return False
        
        if not self.project_path:
            self.logger.error("Путь к проекту не установлен")
            return False
        
        try:
            cmd = [self.unity_path, '-projectPath', self.project_path]
            subprocess.Popen(cmd)
            self.logger.info("Редактор Unity запущен")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка запуска редактора: {e}")
            return False
    
    def import_asset(self, asset_path: str, destination: str = 'Assets') -> bool:
        """
        Импортировать ассет
        
        Args:
            asset_path: Путь к ассету
            destination: Путь назначения в проекте
            
        Returns:
            bool: Успешность операции
        """
        try:
            dest_path = os.path.join(self.project_path, destination)
            Path(dest_path).mkdir(parents=True, exist_ok=True)
            
            if os.path.isfile(asset_path):
                import shutil
                shutil.copy(asset_path, dest_path)
            elif os.path.isdir(asset_path):
                import shutil
                shutil.copytree(asset_path, os.path.join(dest_path, Path(asset_path).name))
            
            self.logger.info(f"Ассет импортирован: {asset_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка импорта ассета: {e}")
            return False


class GraphicsManager:
    """Менеджер 3D графики"""
    
    def __init__(self):
        """Инициализация"""
        self.blender = BlenderManager()
        self.unity = UnityManager()
        self.logger = logging.getLogger('daur_ai.graphics_manager')
    
    def get_blender_status(self) -> Dict[str, Any]:
        """Получить статус Blender"""
        return {
            'available': self.blender.is_available(),
            'path': self.blender.blender_path,
            'scenes': len(self.blender.scenes)
        }
    
    def get_unity_status(self) -> Dict[str, Any]:
        """Получить статус Unity"""
        return {
            'available': self.unity.is_available(),
            'path': self.unity.unity_path,
            'project_path': self.unity.project_path,
            'scenes': len(self.unity.scenes)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Получить общий статус"""
        return {
            'blender': self.get_blender_status(),
            'unity': self.get_unity_status()
        }


# Глобальные экземпляры
_blender_manager = None
_unity_manager = None
_graphics_manager = None


def get_blender_manager() -> BlenderManager:
    """Получить менеджер Blender"""
    global _blender_manager
    if _blender_manager is None:
        _blender_manager = BlenderManager()
    return _blender_manager


def get_unity_manager() -> UnityManager:
    """Получить менеджер Unity"""
    global _unity_manager
    if _unity_manager is None:
        _unity_manager = UnityManager()
    return _unity_manager


def get_graphics_manager() -> GraphicsManager:
    """Получить менеджер графики"""
    global _graphics_manager
    if _graphics_manager is None:
        _graphics_manager = GraphicsManager()
    return _graphics_manager

