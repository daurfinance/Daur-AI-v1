#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Обработчик приложений для Windows
Реализация управления приложениями для Windows

Версия: 1.0
Дата: 09.05.2025
"""

import os
import time
import logging
import subprocess
from typing import List, Dict, Union, Optional

# Импорт Windows-специфичных библиотек
try:
    import win32api
    import win32con
    import win32gui
    import win32process
    import psutil
    HAS_WIN32_API = True
except ImportError:
    HAS_WIN32_API = False
    logging.warning("win32api не установлен. Некоторые функции будут недоступны.")


class WindowsAppHandler:
    """Обработчик приложений для Windows с использованием Win32 API"""
    
    def __init__(self):
        """Инициализация обработчика приложений для Windows"""
        self.logger = logging.getLogger('daur_ai.apps.windows')
        
        if not HAS_WIN32_API:
            self.logger.warning("Для полной функциональности требуется pywin32 и psutil")
            self.logger.warning("Выполните: pip install pywin32 psutil")
        
        # Популярные приложения и их исполняемые файлы
        self.app_executables = {
            "chrome": "chrome.exe",
            "firefox": "firefox.exe",
            "edge": "msedge.exe",
            "vscode": "code.exe",
            "notepad": "notepad.exe",
            "word": "WINWORD.EXE",
            "excel": "EXCEL.EXE",
            "powershell": "powershell.exe",
            "cmd": "cmd.exe",
            "explorer": "explorer.exe",
            "outlook": "OUTLOOK.EXE",
            "teams": "Teams.exe",
            "skype": "Skype.exe",
            "python": "python.exe",
            "spotify": "Spotify.exe",
        }
    
    def _get_executable_path(self, name: str) -> str:
        """
        Получение пути к исполняемому файлу по имени приложения
        
        Args:
            name (str): Имя приложения
            
        Returns:
            str: Путь к исполняемому файлу или исходное имя, если путь не найден
        """
        # Проверка, является ли входное имя путем
        if os.path.exists(name) or '\\' in name or '/' in name:
            return name
        
        # Проверка в словаре известных приложений
        if name.lower() in self.app_executables:
            return self.app_executables[name.lower()]
        
        # Вернуть исходное имя
        return name
    
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
            
        if not HAS_WIN32_API:
            return False  # Невозможно запустить без win32api
        
        try:
            # Получение пути к исполняемому файлу
            executable = self._get_executable_path(name)
            
            # Запуск через ShellExecute для больших возможностей
            if wait:
                proc = subprocess.run(
                    [executable] + arguments,
                    shell=True,
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
                # Запуск через Win32 API для более надежной работы со встроенными приложениями
                try:
                    args = " ".join(arguments) if arguments else ""
                    win32api.ShellExecute(0, "open", executable, args, None, 1)  # SW_SHOWNORMAL = 1
                    
                    # Небольшая пауза для запуска приложения
                    time.sleep(0.5)
                    
                    # Поиск процесса по имени
                    for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                        try:
                            if proc.info['name'].lower() == os.path.basename(executable).lower():
                                return {
                                    "pid": proc.info['pid'],
                                    "name": proc.info['name'],
                                    "running": True
                                }
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    # Если процесс не найден, но ошибок не было
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Ошибка при запуске через ShellExecute: {e}")
                    
                    # Fallback на subprocess
                    proc = subprocess.Popen(
                        [executable] + arguments,
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    return {
                        "pid": proc.pid,
                        "name": os.path.basename(executable),
                        "running": True
                    }
            
        except Exception as e:
            self.logger.error(f"Ошибка при запуске приложения {name}: {e}")
            return False
    
    def close_app(self, name: str, force: bool = False) -> bool:
        """
        Закрытие приложения
        
        Args:
            name (str): Имя приложения или ID процесса
            force (bool): Принудительное завершение
            
        Returns:
            bool: Результат закрытия
        """
        if not HAS_WIN32_API:
            return False  # Невозможно закрыть без win32api и psutil
        
        try:
            # Проверка, является ли name числом (PID)
            try:
                pid = int(name)
                is_pid = True
            except ValueError:
                is_pid = False
                # Получение пути к исполняемому файлу
                executable = self._get_executable_path(name)
                executable_basename = os.path.basename(executable).lower()
            
            # Завершение по PID
            if is_pid:
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
            
            # Завершение по имени (все процессы с таким именем)
            success = False
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if proc_name == executable_basename:
                        if force:
                            proc.kill()
                        else:
                            proc.terminate()
                        success = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return success
            
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии приложения {name}: {e}")
            return False
    
    def focus_app(self, name: str) -> bool:
        """
        Переключение на приложение
        
        Args:
            name (str): Имя приложения или ID окна
            
        Returns:
            bool: Результат переключения
        """
        if not HAS_WIN32_API:
            return False  # Невозможно переключиться без win32api
        
        try:
            # Проверка, является ли name хендлом окна (число)
            try:
                hwnd = int(name)
                window_handle = hwnd
            except ValueError:
                # Получение пути к исполняемому файлу
                executable = self._get_executable_path(name)
                executable_basename = os.path.basename(executable).lower()
                
                # Найти окно по имени исполняемого файла
                window_handle = None
                
                def enum_windows_callback(hwnd, ctx):
                    if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                        try:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            try:
                                proc = psutil.Process(pid)
                                if proc.name().lower() == executable_basename:
                                    ctx.append(hwnd)
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                        except Exception:
                            pass
                    return True
                
                window_handles = []
                win32gui.EnumWindows(enum_windows_callback, window_handles)
                
                if window_handles:
                    window_handle = window_handles[0]  # Берем первое найденное окно
            
            # Переключение на окно
            if window_handle:
                # Проверка, не свернуто ли окно
                if win32gui.IsIconic(window_handle):
                    win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)
                
                # Активация окна и перевод его на передний план
                win32gui.SetForegroundWindow(window_handle)
                return True
            else:
                self.logger.warning(f"Не найдено окно для приложения {name}")
                return False
            
        except Exception as e:
            self.logger.error(f"Ошибка при переключении на приложение {name}: {e}")
            return False
    
    def list_running_apps(self) -> List[Dict]:
        """
        Получение списка запущенных приложений
        
        Returns:
            list: Список приложений
        """
        if not HAS_WIN32_API:
            return []  # Невозможно получить список без psutil
        
        try:
            result = []
            
            # Получение всех процессов
            for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info']):
                try:
                    proc_info = proc.info
                    
                    # Поиск окон для процесса (если это приложение с UI)
                    window_titles = []
                    
                    def enum_proc_windows(hwnd, ctx):
                        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                            _, win_pid = win32process.GetWindowThreadProcessId(hwnd)
                            if win_pid == ctx['pid']:
                                ctx['windows'].append(win32gui.GetWindowText(hwnd))
                        return True
                    
                    window_ctx = {'pid': proc_info['pid'], 'windows': []}
                    try:
                        win32gui.EnumWindows(enum_proc_windows, window_ctx)
                        window_titles = window_ctx['windows']
                    except Exception:
                        pass
                    
                    # Добавление в результат только процессов с окнами (исключаем фоновые службы)
                    if window_titles:
                        result.append({
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "username": proc_info['username'] if proc_info['username'] else "N/A",
                            "memory_mb": round(proc_info['memory_info'].rss / (1024 * 1024), 2),
                            "windows": window_titles,
                            "source": "system"
                        })
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка приложений: {e}")
            return []
    
    def is_app_running(self, name: str) -> Union[bool, Dict]:
        """
        Проверка, запущено ли приложение
        
        Args:
            name (str): Имя приложения
            
        Returns:
            bool or dict: Результат проверки
        """
        if not HAS_WIN32_API:
            return False  # Невозможно проверить без psutil
        
        try:
            # Получение пути к исполняемому файлу
            executable = self._get_executable_path(name)
            executable_basename = os.path.basename(executable).lower()
            
            # Поиск процесса по имени
            for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                try:
                    if proc.info['name'].lower() == executable_basename:
                        return {
                            "running": True,
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "uptime": time.time() - proc.info['create_time'],
                            "source": "system"
                        }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {"running": False}
            
        except Exception as e:
            self.logger.error(f"Ошибка при проверке приложения {name}: {e}")
            return {"running": False, "error": str(e)}
    
    def cleanup(self):
        """Очистка ресурсов при завершении работы"""
        pass  # Ничего не требуется для Windows
