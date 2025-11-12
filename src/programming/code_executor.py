#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль программирования и Docker
Выполнение кода, управление контейнерами и развертывание

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import subprocess
import os
import json
import tempfile
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class ProgrammingLanguage(Enum):
    """Языки программирования"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GOLANG = "golang"
    RUST = "rust"
    CPP = "cpp"
    BASH = "bash"


class ExecutionEnvironment(Enum):
    """Окружения выполнения"""
    LOCAL = "local"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    SANDBOX = "sandbox"


@dataclass
class CodeFile:
    """Файл с кодом"""
    filename: str
    language: ProgrammingLanguage
    content: str
    filepath: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionResult:
    """Результат выполнения"""
    success: bool
    output: str = ""
    error: str = ""
    execution_time: float = 0.0
    exit_code: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DockerImage:
    """Docker образ"""
    name: str
    tag: str = "latest"
    dockerfile_path: str = ""
    base_image: str = "python:3.11"
    size: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DockerContainer:
    """Docker контейнер"""
    container_id: str
    image_name: str
    name: str = ""
    status: str = "created"
    port_mappings: Dict[int, int] = field(default_factory=dict)
    environment: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class CodeExecutor:
    """Исполнитель кода"""
    
    def __init__(self, timeout: int = 30):
        """
        Args:
            timeout: Таймаут выполнения в секундах
        """
        self.timeout = timeout
        self.logger = logging.getLogger('daur_ai.code_executor')
    
    def execute_python(self, code: str) -> ExecutionResult:
        """
        Выполнить Python код
        
        Args:
            code: Python код
            
        Returns:
            ExecutionResult: Результат выполнения
        """
        try:
            import time
            start_time = time.time()
            
            result = subprocess.run(
                ['python3', '-c', code],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                execution_time=execution_time,
                exit_code=result.returncode
            )
        
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error=f"Выполнение превысило таймаут {self.timeout}с",
                exit_code=-1
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                exit_code=-1
            )
    
    def execute_javascript(self, code: str) -> ExecutionResult:
        """
        Выполнить JavaScript код
        
        Args:
            code: JavaScript код
            
        Returns:
            ExecutionResult: Результат выполнения
        """
        try:
            import time
            start_time = time.time()
            
            result = subprocess.run(
                ['node', '-e', code],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                execution_time=execution_time,
                exit_code=result.returncode
            )
        
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error=f"Выполнение превысило таймаут {self.timeout}с",
                exit_code=-1
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                exit_code=-1
            )
    
    def execute_bash(self, script: str) -> ExecutionResult:
        """
        Выполнить Bash скрипт
        
        Args:
            script: Bash скрипт
            
        Returns:
            ExecutionResult: Результат выполнения
        """
        try:
            import time
            start_time = time.time()
            
            result = subprocess.run(
                ['bash', '-c', script],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            execution_time = time.time() - start_time
            
            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                execution_time=execution_time,
                exit_code=result.returncode
            )
        
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error=f"Выполнение превысило таймаут {self.timeout}с",
                exit_code=-1
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                exit_code=-1
            )
    
    def execute_file(self, filepath: str, language: ProgrammingLanguage) -> ExecutionResult:
        """
        Выполнить файл с кодом
        
        Args:
            filepath: Путь к файлу
            language: Язык программирования
            
        Returns:
            ExecutionResult: Результат выполнения
        """
        if not os.path.exists(filepath):
            return ExecutionResult(
                success=False,
                error=f"Файл не найден: {filepath}",
                exit_code=-1
            )
        
        try:
            with open(filepath, 'r') as f:
                code = f.read()
            
            if language == ProgrammingLanguage.PYTHON:
                return self.execute_python(code)
            elif language == ProgrammingLanguage.JAVASCRIPT:
                return self.execute_javascript(code)
            elif language == ProgrammingLanguage.BASH:
                return self.execute_bash(code)
            else:
                return ExecutionResult(
                    success=False,
                    error=f"Язык {language.value} не поддерживается",
                    exit_code=-1
                )
        
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e),
                exit_code=-1
            )


class DockerManager:
    """Менеджер Docker"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.docker_manager')
        self.images: Dict[str, DockerImage] = {}
        self.containers: Dict[str, DockerContainer] = {}
    
    def is_available(self) -> bool:
        """Проверить доступность Docker"""
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True)
            return result.returncode == 0
        except Exception as e:
            return False
    
    def build_image(self, dockerfile_path: str, image_name: str,
                   tag: str = "latest") -> bool:
        """
        Собрать Docker образ
        
        Args:
            dockerfile_path: Путь к Dockerfile
            image_name: Имя образа
            tag: Тег образа
            
        Returns:
            bool: Успешность сборки
        """
        if not self.is_available():
            self.logger.error("Docker не доступен")
            return False
        
        if not os.path.exists(dockerfile_path):
            self.logger.error(f"Dockerfile не найден: {dockerfile_path}")
            return False
        
        try:
            cmd = [
                'docker', 'build',
                '-t', f'{image_name}:{tag}',
                '-f', dockerfile_path,
                os.path.dirname(dockerfile_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                image = DockerImage(image_name, tag, dockerfile_path)
                self.images[f'{image_name}:{tag}'] = image
                self.logger.info(f"Образ собран: {image_name}:{tag}")
                return True
            else:
                self.logger.error(f"Ошибка сборки: {result.stderr}")
                return False
        
        except Exception as e:
            self.logger.error(f"Ошибка сборки образа: {e}")
            return False
    
    def run_container(self, image_name: str, container_name: str = None,
                     port_mappings: Dict[int, int] = None,
                     environment: Dict[str, str] = None) -> Optional[str]:
        """
        Запустить контейнер
        
        Args:
            image_name: Имя образа
            container_name: Имя контейнера
            port_mappings: Маппинг портов
            environment: Переменные окружения
            
        Returns:
            Optional[str]: ID контейнера или None
        """
        if not self.is_available():
            self.logger.error("Docker не доступен")
            return None
        
        try:
            cmd = ['docker', 'run', '-d']
            
            if container_name:
                cmd.extend(['--name', container_name])
            
            if port_mappings:
                for host_port, container_port in port_mappings.items():
                    cmd.extend(['-p', f'{host_port}:{container_port}'])
            
            if environment:
                for key, value in environment.items():
                    cmd.extend(['-e', f'{key}={value}'])
            
            cmd.append(image_name)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                container_id = result.stdout.strip()
                container = DockerContainer(
                    container_id=container_id,
                    image_name=image_name,
                    name=container_name or container_id,
                    port_mappings=port_mappings or {},
                    environment=environment or {}
                )
                self.containers[container_id] = container
                self.logger.info(f"Контейнер запущен: {container_id}")
                return container_id
            else:
                self.logger.error(f"Ошибка запуска: {result.stderr}")
                return None
        
        except Exception as e:
            self.logger.error(f"Ошибка запуска контейнера: {e}")
            return None
    
    def stop_container(self, container_id: str) -> bool:
        """
        Остановить контейнер
        
        Args:
            container_id: ID контейнера
            
        Returns:
            bool: Успешность операции
        """
        if not self.is_available():
            self.logger.error("Docker не доступен")
            return False
        
        try:
            cmd = ['docker', 'stop', container_id]
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                if container_id in self.containers:
                    self.containers[container_id].status = "stopped"
                self.logger.info(f"Контейнер остановлен: {container_id}")
                return True
            else:
                self.logger.error(f"Ошибка остановки: {result.stderr.decode()}")
                return False
        
        except Exception as e:
            self.logger.error(f"Ошибка остановки контейнера: {e}")
            return False
    
    def remove_container(self, container_id: str) -> bool:
        """
        Удалить контейнер
        
        Args:
            container_id: ID контейнера
            
        Returns:
            bool: Успешность операции
        """
        if not self.is_available():
            self.logger.error("Docker не доступен")
            return False
        
        try:
            cmd = ['docker', 'rm', '-f', container_id]
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                if container_id in self.containers:
                    del self.containers[container_id]
                self.logger.info(f"Контейнер удален: {container_id}")
                return True
            else:
                self.logger.error(f"Ошибка удаления: {result.stderr.decode()}")
                return False
        
        except Exception as e:
            self.logger.error(f"Ошибка удаления контейнера: {e}")
            return False
    
    def get_container_logs(self, container_id: str) -> str:
        """
        Получить логи контейнера
        
        Args:
            container_id: ID контейнера
            
        Returns:
            str: Логи контейнера
        """
        if not self.is_available():
            return ""
        
        try:
            cmd = ['docker', 'logs', container_id]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout
        
        except Exception as e:
            self.logger.error(f"Ошибка получения логов: {e}")
            return ""
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус менеджера"""
        return {
            'available': self.is_available(),
            'images': len(self.images),
            'containers': len(self.containers),
            'running_containers': sum(1 for c in self.containers.values() if c.status == 'running')
        }


class ProgrammingManager:
    """Менеджер программирования"""
    
    def __init__(self):
        """Инициализация"""
        self.code_executor = CodeExecutor()
        self.docker_manager = DockerManager()
        self.logger = logging.getLogger('daur_ai.programming_manager')
        self.code_files: Dict[str, CodeFile] = {}
    
    def create_code_file(self, filename: str, language: ProgrammingLanguage,
                        content: str) -> CodeFile:
        """
        Создать файл с кодом
        
        Args:
            filename: Имя файла
            language: Язык программирования
            content: Содержимое
            
        Returns:
            CodeFile: Объект файла
        """
        filepath = f"/tmp/{filename}"
        code_file = CodeFile(filename, language, content, filepath)
        self.code_files[filename] = code_file
        self.logger.info(f"Файл с кодом создан: {filename}")
        return code_file
    
    def execute_code(self, code: str, language: ProgrammingLanguage) -> ExecutionResult:
        """
        Выполнить код
        
        Args:
            code: Код
            language: Язык программирования
            
        Returns:
            ExecutionResult: Результат выполнения
        """
        if language == ProgrammingLanguage.PYTHON:
            return self.code_executor.execute_python(code)
        elif language == ProgrammingLanguage.JAVASCRIPT:
            return self.code_executor.execute_javascript(code)
        elif language == ProgrammingLanguage.BASH:
            return self.code_executor.execute_bash(code)
        else:
            return ExecutionResult(
                success=False,
                error=f"Язык {language.value} не поддерживается",
                exit_code=-1
            )
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус менеджера"""
        return {
            'code_files': len(self.code_files),
            'docker': self.docker_manager.get_status()
        }


# Глобальные экземпляры
_code_executor = None
_docker_manager = None
_programming_manager = None


def get_code_executor() -> CodeExecutor:
    """Получить исполнитель кода"""
    global _code_executor
    if _code_executor is None:
        _code_executor = CodeExecutor()
    return _code_executor


def get_docker_manager() -> DockerManager:
    """Получить менеджер Docker"""
    global _docker_manager
    if _docker_manager is None:
        _docker_manager = DockerManager()
    return _docker_manager


def get_programming_manager() -> ProgrammingManager:
    """Получить менеджер программирования"""
    global _programming_manager
    if _programming_manager is None:
        _programming_manager = ProgrammingManager()
    return _programming_manager

