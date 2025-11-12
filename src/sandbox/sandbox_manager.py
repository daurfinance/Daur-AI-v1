# -*- coding: utf-8 -*-

"""
Daur-AI: Менеджер песочницы
Управление Docker контейнерами и ограничениями ресурсов

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import time
import resource
from typing import Optional, Dict, Any

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


class SandboxManager:
    """Менеджер песочницы для безопасного выполнения кода"""
    
    def __init__(self, use_docker: bool = True):
        """
        Инициализация менеджера песочницы
        
        Args:
            use_docker: Использовать Docker для песочницы
        """
        self.logger = logging.getLogger('daur_ai.sandbox_manager')
        self.use_docker = use_docker and DOCKER_AVAILABLE
        self.container = None
        self.client = None
        self.sandbox_id = None
        
        if self.use_docker:
            self._init_docker()
        
        self.logger.info(f"SandboxManager инициализирован (Docker: {self.use_docker})")
    
    def _init_docker(self):
        """Инициализировать Docker клиент"""
        try:
            if not DOCKER_AVAILABLE:
                self.logger.warning("Docker не доступен")
                return
            
            self.client = docker.from_env()
            self.logger.info("Docker клиент инициализирован")
        
        except Exception as e:
            self.logger.error(f"Ошибка инициализации Docker: {e}")
            self.use_docker = False
    
    def create_container(self, image: str = 'python:3.11-slim',
                        memory_limit: str = '512m',
                        cpu_limit: float = 1.0) -> bool:
        """
        Создать Docker контейнер для песочницы
        
        Args:
            image: Docker образ
            memory_limit: Лимит памяти
            cpu_limit: Лимит CPU
            
        Returns:
            bool: Успешность операции
        """
        if not self.use_docker or not self.client:
            self.logger.warning("Docker не доступен")
            return False
        
        try:
            self.sandbox_id = f'daur-ai-sandbox-{int(time.time())}'
            
            self.container = self.client.containers.run(
                image,
                detach=True,
                mem_limit=memory_limit,
                cpus=cpu_limit,
                network_mode='none',  # Отключить сеть
                read_only=True,  # Только чтение
                tmpfs={'/tmp': 'size=100m'},  # Временная файловая система
                name=self.sandbox_id,
                remove=False
            )
            
            self.logger.info(f"Контейнер создан: {self.sandbox_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка создания контейнера: {e}")
            return False
    
    def execute_command(self, command: str, timeout: int = 300) -> Dict[str, Any]:
        """
        Выполнить команду в контейнере
        
        Args:
            command: Команда для выполнения
            timeout: Таймаут выполнения
            
        Returns:
            Результат выполнения
        """
        if not self.container:
            self.logger.error("Контейнер не создан")
            return {'success': False, 'error': 'Container not created'}
        
        try:
            exit_code, output = self.container.exec_run(
                command,
                stdout=True,
                stderr=True,
                timeout=timeout
            )
            
            return {
                'success': exit_code == 0,
                'exit_code': exit_code,
                'output': output.decode('utf-8', errors='ignore')
            }
        
        except Exception as e:
            self.logger.error(f"Ошибка выполнения команды: {e}")
            return {'success': False, 'error': str(e)}
    
    def setup_os_sandbox(self) -> bool:
        """
        Настроить ограничения на уровне ОС
        
        Returns:
            bool: Успешность операции
        """
        try:
            # Ограничить использование памяти (512 MB)
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, hard))
            
            # Ограничить использование CPU (5 минут)
            soft, hard = resource.getrlimit(resource.RLIMIT_CPU)
            resource.setrlimit(resource.RLIMIT_CPU, (300, hard))
            
            # Ограничить количество открытых файлов
            soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            resource.setrlimit(resource.RLIMIT_NOFILE, (256, hard))
            
            # Ограничить размер файла (100 MB)
            soft, hard = resource.getrlimit(resource.RLIMIT_FSIZE)
            resource.setrlimit(resource.RLIMIT_FSIZE, (100 * 1024 * 1024, hard))
            
            self.logger.info("Ограничения ОС установлены")
            return True
        
        except Exception as e:
            self.logger.warning(f"Не удалось установить ограничения ОС: {e}")
            return False
    
    def get_container_stats(self) -> Dict[str, Any]:
        """Получить статистику контейнера"""
        if not self.container:
            return {}
        
        try:
            stats = self.container.stats(stream=False)
            
            memory_usage = stats['memory_stats'].get('usage', 0)
            memory_limit = stats['memory_stats'].get('limit', 0)
            
            cpu_stats = stats['cpu_stats']
            cpu_percent = 0.0
            
            if 'cpu_usage' in cpu_stats:
                cpu_delta = cpu_stats['cpu_usage'].get('total_usage', 0)
                system_delta = cpu_stats.get('system_cpu_usage', 0)
                
                if system_delta > 0:
                    cpu_percent = (cpu_delta / system_delta) * 100.0
            
            return {
                'memory_usage': memory_usage,
                'memory_limit': memory_limit,
                'memory_percent': (memory_usage / memory_limit * 100) if memory_limit > 0 else 0,
                'cpu_percent': cpu_percent,
                'container_id': self.sandbox_id
            }
        
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return {}
    
    def cleanup(self) -> bool:
        """Очистить контейнер"""
        if not self.container:
            return True
        
        try:
            self.container.stop(timeout=10)
            self.container.remove()
            self.logger.info(f"Контейнер {self.sandbox_id} удален")
            self.container = None
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка очистки контейнера: {e}")
            return False
    
    def __del__(self):
        """Деструктор"""
        self.cleanup()


def get_sandbox_manager(use_docker: bool = True) -> SandboxManager:
    """Получить экземпляр SandboxManager"""
    return SandboxManager(use_docker=use_docker)

