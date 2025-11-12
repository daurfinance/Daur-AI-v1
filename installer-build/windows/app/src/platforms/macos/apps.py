#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Обработчик приложений для macOS
Реализация управления приложениями для macOS

Версия: 1.0
Дата: 09.05.2025
"""

import os
import time
import logging
import subprocess
from typing import List, Dict, Union, Optional

# Импорт macOS-специфичных библиотек
try:
    import AppKit
    from Foundation import NSArray, NSURL
    from ScriptingBridge import SBApplication
    import psutil
    HAS_APPKIT = True
except ImportError:
    HAS_APPKIT = False
    logging.warning("pyobjc и psutil не установлены. Некоторые функции будут недоступны.")


class MacOSAppHandler:
    """Обработчик приложений для macOS с использованием AppKit и AppleScript"""
    
    def __init__(self):
        """Инициализация обработчика приложений для macOS"""
        self.logger = logging.getLogger('daur_ai.apps.macos')
        
        if not HAS_APPKIT:
            self.logger.warning("Для полной функциональности требуется pyobjc и psutil")
            self.logger.warning("Выполните: pip install pyobjc psutil")
        
        # Популярные приложения и их бандл-идентификаторы
        self.app_bundles = {
            "safari": "com.apple.Safari",
            "chrome": "com.google.Chrome",
            "firefox": "org.mozilla.firefox",
            "vscode": "com.microsoft.VSCode",
            "textedit": "com.apple.TextEdit",
            "finder": "com.apple.finder",
            "terminal": "com.apple.Terminal",
            "iterm": "com.googlecode.iterm2",
            "mail": "com.apple.Mail",
            "photos": "com.apple.Photos",
            "music": "com.apple.Music",
            "xcode": "com.apple.dt.Xcode",
            "word": "com.microsoft.Word",
            "excel": "com.microsoft.Excel",
            "slack": "com.slack.Slack",
            "teams": "com.microsoft.Teams",
            "zoom": "us.zoom.xos",
            "spotify": "com.spotify.client",
        }
    
    def _get_app_identifier(self, name: str) -> str:
        """
        Получение идентификатора приложения по имени
        
        Args:
            name (str): Имя приложения
            
        Returns:
            str: Идентификатор приложения или исходное имя, если не найден
        """
        # Проверка, является ли входное имя путем
        if os.path.exists(name) or '/' in name:
            return name
        
        # Проверка в словаре известных приложений
        if name.lower() in self.app_bundles:
            return self.app_bundles[name.lower()]
        
        # Вернуть исходное имя
        return name
    
    def _run_applescript(self, script: str) -> Union[str, bool]:
        """
        Выполнение AppleScript
        
        Args:
            script (str): Скрипт для выполнения
            
        Returns:
            str or bool: Результат выполнения скрипта или False в случае ошибки
        """
        try:
            proc = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True
            )
            
            if proc.returncode == 0:
                return proc.stdout.strip()
            else:
                self.logger.error(f"Ошибка выполнения AppleScript: {proc.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка выполнения AppleScript: {e}")
            return False
    
    def launch_app(self, name: str, arguments: List[str] = None, wait: bool = False) -> Union[bool, Dict]:
        """
        Запуск приложения
        
        Args:
            name (str): Имя приложения или путь к приложению
            arguments (list): Список аргументов командной строки
            wait (bool): Ожидать завершения приложения
            
        Returns:
            bool or dict: Результат запуска
        """
        if arguments is None:
            arguments = []
            
        try:
            # Определение идентификатора приложения
            app_id = self._get_app_identifier(name)
            
            # Если требуется ожидание, используем subprocess
            if wait:
                cmd = ["open", "-a", app_id, "--args"] + arguments
                
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
            
            # Для запуска без ожидания используем AppKit, если доступен
            if HAS_APPKIT:
                try:
                    # Различные способы запуска в зависимости от того, что мы имеем
                    if os.path.exists(app_id) and app_id.endswith('.app'):
                        # Запуск по пути к .app
                        url = NSURL.fileURLWithPath_(app_id)
                        ws = AppKit.NSWorkspace.sharedWorkspace()
                        configuration = AppKit.NSWorkspaceOpenConfiguration.new()
                        
                        if arguments:
                            configuration.setArguments_(arguments)
                            
                        ws.openApplicationAtURL_configuration_completionHandler_(
                            url, configuration, None
                        )
                    
                    elif app_id in self.app_bundles.values():
                        # Запуск по бандл-идентификатору
                        ws = AppKit.NSWorkspace.sharedWorkspace()
                        app_url = ws.URLForApplicationWithBundleIdentifier_(app_id)
                        
                        if app_url:
                            configuration = AppKit.NSWorkspaceOpenConfiguration.new()
                            
                            if arguments:
                                configuration.setArguments_(arguments)
                                
                            ws.openApplicationAtURL_configuration_completionHandler_(
                                app_url, configuration, None
                            )
                        else:
                            self.logger.warning(f"Приложение не найдено: {app_id}")
                            return False
                    
                    else:
                        # Запуск с использованием имени приложения
                        ws = AppKit.NSWorkspace.sharedWorkspace()
                        
                        if arguments:
                            # С аргументами нужно использовать AppleScript
                            args_str = " ".join([f'"{arg}"' for arg in arguments])
                            script = f'tell application "{name}" to open {args_str}'
                            return self._run_applescript(script) != False
                        else:
                            # Без аргументов можем использовать AppKit
                            success = ws.launchApplication_(name)
                            return success
                    
                    # Небольшая пауза для запуска приложения
                    time.sleep(0.5)
                    
                    # Поиск процесса (если psutil доступен)
                    if 'psutil' in globals():
                        for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                            try:
                                if name.lower() in proc.info['name'].lower():
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
                    self.logger.error(f"Ошибка при запуске через AppKit: {e}")
            
            # Fallback на open
            cmd = ["open", "-a", app_id]
            if arguments:
                cmd.extend(["--args"] + arguments)
                
            subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Небольшая пауза для запуска приложения
            time.sleep(0.5)
            
            return True
            
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
        try:
            # Проверка, является ли name числом (PID)
            try:
                pid = int(name)
                is_pid = True
            except ValueError:
                is_pid = False
                # Получение идентификатора приложения
                app_id = self._get_app_identifier(name)
            
            # Завершение по PID
            if is_pid:
                try:
                    if 'psutil' in globals():
                        proc = psutil.Process(pid)
                        if force:
                            proc.kill()
                        else:
                            proc.terminate()
                        return True
                    else:
                        # Fallback на kill
                        os.kill(pid, 9 if force else 15)  # SIGKILL или SIGTERM
                        return True
                except (psutil.NoSuchProcess, ProcessLookupError):
                    return False  # Процесс не существует
                except (psutil.AccessDenied, PermissionError):
                    self.logger.warning(f"Отказано в доступе при завершении процесса {pid}")
                    return False
            
            # Завершение по имени приложения через AppleScript
            if force:
                script = f'tell application "System Events" to set the_process to first process whose name is "{name}"\ntell the_process to quit with force'
            else:
                script = f'tell application "{name}" to quit'
                
            result = self._run_applescript(script)
            
            # Проверка результата
            if result is not False:
                return True
            
            # Fallback на поиск процесса по имени (если первые методы не сработали)
            if 'psutil' in globals():
                success = False
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if name.lower() in proc.info['name'].lower():
                            if force:
                                proc.kill()
                            else:
                                proc.terminate()
                            success = True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                return success
            
            # Если ничего не сработало
            self.logger.warning(f"Не удалось закрыть приложение {name}")
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
        try:
            # Определение идентификатора приложения
            app_id = self._get_app_identifier(name)
            
            # Активация через AppleScript (наиболее надежный способ)
            script = f'tell application "{name}" to activate'
            result = self._run_applescript(script)
            
            if result is not False:
                return True
                
            # Fallback на AppKit
            if HAS_APPKIT:
                try:
                    ws = AppKit.NSWorkspace.sharedWorkspace()
                    
                    # Проверка, запущено ли приложение
                    running_apps = ws.runningApplications()
                    for app in running_apps:
                        if name.lower() in app.localizedName().lower():
                            app.activateWithOptions_(AppKit.NSApplicationActivateIgnoringOtherApps)
                            return True
                            
                    # Если приложение не запущено, запускаем его
                    return self.launch_app(name)
                    
                except Exception as e:
                    self.logger.error(f"Ошибка при активации приложения через AppKit: {e}")
            
            # Fallback на open
            subprocess.run(["open", "-a", app_id])
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при переключении на приложение {name}: {e}")
            return False
    
    def list_running_apps(self) -> List[Dict]:
        """
        Получение списка запущенных приложений
        
        Returns:
            list: Список приложений
        """
        try:
            result = []
            
            if HAS_APPKIT:
                try:
                    # Получение списка запущенных приложений через AppKit
                    ws = AppKit.NSWorkspace.sharedWorkspace()
                    running_apps = ws.runningApplications()
                    
                    for app in running_apps:
                        if app.activationPolicy() == AppKit.NSApplicationActivationPolicyRegular:
                            # Только приложения с интерфейсом (не службы)
                            app_info = {
                                "name": str(app.localizedName()),
                                "bundle_id": str(app.bundleIdentifier()),
                                "pid": app.processIdentifier(),
                                "active": app.isActive(),
                                "source": "system"
                            }
                            
                            # Добавление информации о памяти, если доступна psutil
                            if 'psutil' in globals():
                                try:
                                    proc = psutil.Process(app_info["pid"])
                                    app_info["memory_mb"] = round(proc.memory_info().rss / (1024 * 1024), 2)
                                except (psutil.NoSuchProcess, psutil.AccessDenied):
                                    pass
                                
                            result.append(app_info)
                        
                except Exception as e:
                    self.logger.error(f"Ошибка при получении списка приложений через AppKit: {e}")
            
            # Если результат пуст или AppKit недоступен, используем psutil
            if not result and 'psutil' in globals():
                for proc in psutil.process_iter(['pid', 'name', 'username', 'memory_info', 'create_time']):
                    try:
                        proc_info = proc.info
                        
                        # Исключаем системные процессы
                        if proc_info['username'] == os.getlogin():
                            result.append({
                                "pid": proc_info['pid'],
                                "name": proc_info['name'],
                                "memory_mb": round(proc_info['memory_info'].rss / (1024 * 1024), 2),
                                "uptime": time.time() - proc_info['create_time'],
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
        try:
            # Определение идентификатора приложения
            app_id = self._get_app_identifier(name)
            
            # Проверка через AppleScript
            script = f'tell application "System Events" to (name of processes) contains "{name}"'
            result = self._run_applescript(script)
            
            if result == "true":
                script = f'tell application "System Events" to get the id of process "{name}"'
                pid = self._run_applescript(script)
                
                if pid and pid.isdigit():
                    return {
                        "running": True,
                        "pid": int(pid),
                        "name": name,
                        "source": "system"
                    }
                else:
                    return {"running": True}
                    
            elif HAS_APPKIT:
                # Проверка через AppKit
                try:
                    ws = AppKit.NSWorkspace.sharedWorkspace()
                    running_apps = ws.runningApplications()
                    
                    for app in running_apps:
                        app_name = str(app.localizedName())
                        
                        if name.lower() in app_name.lower():
                            return {
                                "running": True,
                                "pid": app.processIdentifier(),
                                "name": app_name,
                                "bundle_id": str(app.bundleIdentifier()),
                                "source": "system"
                            }
                            
                except Exception as e:
                    self.logger.error(f"Ошибка при проверке запуска через AppKit: {e}")
            
            # Проверка через psutil
            if 'psutil' in globals():
                for proc in psutil.process_iter(['pid', 'name', 'create_time']):
                    try:
                        proc_name = proc.info['name']
                        if name.lower() in proc_name.lower():
                            return {
                                "running": True,
                                "pid": proc.info['pid'],
                                "name": proc_name,
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
        pass  # Ничего не требуется для macOS
