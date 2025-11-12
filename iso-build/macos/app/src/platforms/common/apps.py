#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Стандартный обработчик приложений
Реализация платформенно-независимого управления приложениями

Версия: 1.0
Дата: 09.05.2025
"""

import os
import time
import logging
import subprocess
import platform
from typing import List, Dict, Union, Optional

# Проверка наличия psutil
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    logging.warning("psutil не установлен. Некоторые функции будут ограничены.")


class DefaultAppHandler:
    """
    Стандартный обработчик приложений
    Используется как запасной вариант или для не поддерживаемых платформ
    """
    
    def __init__(self):
        """Инициализация стандартного обработчика приложений"""
        self.logger = logging.getLogger('daur_ai.apps.default')
        self.os_platform = platform.system()
        
        # Словарь для отслеживания запущенных процессов
        self.processes = {}
        
        self.logger.info(f"Инициализирован стандартный обработчик приложений для {self.os_platform}")
    
    def launch_app(self, name: str, arguments: List[str] = None, wait: bool = False) -> Union[bool, Dict]:
        """
        Запуск приложения
        
        Args:
            name (str): Имя приложения или путь к исполняемому файлу
            arguments (list): Список аргументов командной строки
            wait (bool): Ожидать завершения приложения
            
        Returns:
            bool or dict: Результат запуска
        """
        if arguments is None:
            arguments = []
            
        try:
            cmd = [name] + arguments
            
            if wait:
                proc = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                return {
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "success": proc.returncode == 0
                }
            else:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Сохранение процесса для отслеживания
                proc_id = f"{name}_{proc.pid}"
                self.processes[proc_id] = proc
                
                return {
                    "pid": proc.pid,
                    "name": name,
                    "running": True,
                    "proc_id": proc_id
                }
                
        except Exception as e:
            self.logger.error(f"Ошибка при запуске приложения {name}: {e}")
            return False
    
    def close_app(self, name: str, force: bool = False) -> bool:
        """
        Закрытие приложения
        
        Args:
            name (str): Имя приложения, ID процесса или proc_id
            force (bool): Принудительное завершение
            
        Returns:
            bool: Результат закрытия
        """
        try:
            # Проверка, есть ли процесс в нашем словаре
            for proc_id, proc in list(self.processes.items()):
                if name in proc_id or str(proc.pid) == str(name):
                    # Завершение процесса
                    if force:
                        proc.kill()
                    else:
                        proc.terminate()
                        
                    # Ожидание завершения
                    try:
                        proc.wait(timeout=5)
                        del self.processes[proc_id]
                        return True
                    except subprocess.TimeoutExpired:
                        # Если процесс не завершился, принудительное завершение
                        proc.kill()
                        proc.wait()
                        del self.processes[proc_id]
                        return True
            
            # Проверка, является ли name числом (PID)
            try:
                pid = int(name)
                is_pid = True
            except ValueError:
                is_pid = False
            
            # Если это PID и доступен psutil
            if is_pid and HAS_PSUTIL:
                try:
                    proc = psutil.Process(pid)
                    if force:
                        proc.kill()
                    else:
                        proc.terminate()
                    return True
                except psutil.NoSuchProcess:
                    return False  # Процесс не существует
                except psutil.AccessDenied:
                    self.logger.warning(f"Отказано в доступе при завершении процесса {pid}")
                    return False
            
            # Поиск по имени, если доступен psutil
            if HAS_PSUTIL:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if name.lower() in proc.info['name'].lower():
                            if force:
                                proc.kill()
                            else:
                                proc.terminate()
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            # Если ничего не сработало, пробуем через killall (Unix-like)
            if self.os_platform != "Windows":
                try:
                    if force:
                        subprocess.run(["killall", "-9", name], check=True)
                    else:
                        subprocess.run(["killall", name], check=True)
                    return True
                except subprocess.CalledProcessError:
                    return False
                
            self.logger.warning(f"Не удалось найти и завершить процесс {name}")
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии приложения {name}: {e}")
            return False
    
    def focus_app(self, name: str) -> bool:
        """
        Переключение на приложение
        
        Args:
            name (str): Имя приложения
            
        Returns:
            bool: Результат переключения
        """
        self.logger.warning(f"Переключение на приложение не поддерживается в стандартном обработчике")
        return False
    
    def list_running_apps(self) -> List[Dict]:
        """
        Получение списка запущенных приложений
        
        Returns:
            list: Список приложений
        """
        result = []
        
        # Приложения, запущенные через наш обработчик
        for proc_id, proc in self.processes.items():
            if proc.poll() is None:  # Процесс еще работает
                app_name = proc_id.split('_')[0]
                result.append({
                    "pid": proc.pid,
                    "name": app_name,
                    "proc_id": proc_id,
                    "source": "managed"
                })
        
        # Использование psutil для получения всех процессов
        if HAS_PSUTIL:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info']):
                    try:
                        proc_info = proc.info
                        
                        # Добавляем только если это не системный процесс
                        if proc_info['username'] == os.getlogin():
                            result.append({
                                "pid": proc_info['pid'],
                                "name": proc_info['name'],
                                "memory_mb": round(proc_info['memory_info'].rss / (1024 * 1024), 2) if proc_info['memory_info'] else None,
                                "source": "system"
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except Exception as e:
                self.logger.error(f"Ошибка при получении списка приложений через psutil: {e}")
        
        return result
    
    def is_app_running(self, name: str) -> Union[bool, Dict]:
        """
        Проверка, запущено ли приложение
        
        Args:
            name (str): Имя приложения
            
        Returns:
            bool or dict: Результат проверки
        """
        try:
            # Проверка в наших процессах
            for proc_id, proc in self.processes.items():
                if name in proc_id and proc.poll() is None:
                    return {
                        "running": True,
                        "pid": proc.pid,
                        "name": name,
                        "proc_id": proc_id,
                        "source": "managed"
                    }
            
            # Проверка через psutil
            if HAS_PSUTIL:
                for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                    try:
                        if name.lower() in proc.info['name'].lower():
                            return {
                                "running": True,
                                "pid": proc.info['pid'],
                                "name": proc.info['name'],
                                "uptime": time.time() - proc.info['create_time'],
                                "source": "system"
                            }
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            
            # Проверка через pgrep (Unix-like)
            if self.os_platform != "Windows":
                try:
                    proc = subprocess.run(
                        ["pgrep", "-f", name],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    if proc.returncode == 0 and proc.stdout.strip():
                        pid = int(proc.stdout.strip().split()[0])
                        return {
                            "running": True,
                            "pid": pid,
                            "name": name,
                            "source": "system"
                        }
                except (subprocess.SubprocessError, ValueError):
                    pass
            
            return {"running": False}
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке приложения {name}: {e}")
            return {"running": False, "error": str(e)}
    
    def cleanup(self):
        """Очистка ресурсов при завершении работы"""
        # Завершение всех запущенных процессов
        for proc_id, proc in list(self.processes.items()):
            try:
                if proc.poll() is None:  # Процесс еще работает
                    self.logger.debug(f"Завершение процесса: {proc_id}")
                    proc.terminate()
                    try:
                        proc.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
                
                del self.processes[proc_id]
                
            except Exception as e:
                self.logger.error(f"Ошибка при завершении процесса {proc_id}: {e}")
