"""
Продвинутый системный контроллер
Полное управление операционной системой и устройствами
"""

import os
import sys
import subprocess
import psutil
import time
import logging
import threading
import queue
import json
import signal
import socket
import struct
from typing import Dict, List, Optional, Tuple, Any, Callable
import ctypes
import ctypes.util
from pathlib import Path

# Импорты для работы с системой
try:
    import dbus
    DBUS_AVAILABLE = True
except ImportError:
    DBUS_AVAILABLE = False

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk
    GTK_AVAILABLE = True
except ImportError:
    GTK_AVAILABLE = False

class AdvancedSystemController:
    """Продвинутый контроллер системы с полным доступом"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Системная информация
        self.system_info = self._get_system_info()
        
        # Активные процессы и сервисы
        self.monitored_processes = {}
        self.system_services = {}
        
        # Сетевые подключения
        self.network_connections = {}
        
        # Файловая система
        self.mounted_filesystems = {}
        self.watched_directories = {}
        
        # Системные события
        self.event_queue = queue.Queue()
        self.event_handlers = {}
        
        # Мониторинг
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # D-Bus интеграция
        self.dbus_session = None
        self.dbus_system = None
        
        # Инициализация
        self._initialize_controller()
    
    def _initialize_controller(self):
        """Инициализация контроллера"""
        try:
            # Инициализация D-Bus
            self._init_dbus()
            
            # Сканирование системы
            self._scan_system_state()
            
            # Запуск мониторинга
            self.start_monitoring()
            
            self.logger.info("Продвинутый системный контроллер инициализирован")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации контроллера: {e}")
    
    def _get_system_info(self) -> Dict:
        """Получает детальную информацию о системе"""
        try:
            info = {
                'platform': sys.platform,
                'architecture': os.uname(),
                'python_version': sys.version,
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'disk_usage': {},
                'network_interfaces': {},
                'environment': dict(os.environ),
                'user_info': {
                    'uid': os.getuid(),
                    'gid': os.getgid(),
                    'username': os.getenv('USER', 'unknown'),
                    'home': os.getenv('HOME', '/'),
                    'shell': os.getenv('SHELL', '/bin/sh')
                }
            }
            
            # Информация о дисках
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    info['disk_usage'][partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    }
                except Exception as e:
                    continue
            
            # Сетевые интерфейсы
            for interface, addresses in psutil.net_if_addrs().items():
                info['network_interfaces'][interface] = []
                for addr in addresses:
                    info['network_interfaces'][interface].append({
                        'family': str(addr.family),
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast
                    })
            
            return info
            
        except Exception as e:
            self.logger.error(f"Ошибка получения системной информации: {e}")
            return {}
    
    def _init_dbus(self):
        """Инициализация D-Bus"""
        try:
            if not DBUS_AVAILABLE:
                self.logger.warning("D-Bus недоступен")
                return
            
            # Подключение к сессионной шине
            try:
                self.dbus_session = dbus.SessionBus()
                self.logger.info("D-Bus сессионная шина подключена")
            except Exception as e:
                self.logger.warning(f"Не удалось подключиться к сессионной шине D-Bus: {e}")
            
            # Подключение к системной шине
            try:
                self.dbus_system = dbus.SystemBus()
                self.logger.info("D-Bus системная шина подключена")
            except Exception as e:
                self.logger.warning(f"Не удалось подключиться к системной шине D-Bus: {e}")
                
        except Exception as e:
            self.logger.error(f"Ошибка инициализации D-Bus: {e}")
    
    def _scan_system_state(self):
        """Сканирует текущее состояние системы"""
        try:
            # Сканирование процессов
            self._scan_processes()
            
            # Сканирование сервисов
            self._scan_services()
            
            # Сканирование сетевых подключений
            self._scan_network_connections()
            
            # Сканирование файловой системы
            self._scan_filesystems()
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования системы: {e}")
    
    def _scan_processes(self):
        """Сканирует активные процессы"""
        try:
            self.monitored_processes.clear()
            
            for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_info']):
                try:
                    proc_info = proc.info
                    self.monitored_processes[proc_info['pid']] = {
                        'name': proc_info['name'],
                        'username': proc_info['username'],
                        'status': proc_info['status'],
                        'cpu_percent': proc_info['cpu_percent'],
                        'memory_rss': proc_info['memory_info'].rss if proc_info['memory_info'] else 0,
                        'cmdline': proc.cmdline() if proc.is_running() else [],
                        'create_time': proc.create_time() if proc.is_running() else 0
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.logger.info(f"Найдено процессов: {len(self.monitored_processes)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования процессов: {e}")
    
    def _scan_services(self):
        """Сканирует системные сервисы"""
        try:
            self.system_services.clear()
            
            # Попытка получить список systemd сервисов
            try:
                result = subprocess.run(
                    ['systemctl', 'list-units', '--type=service', '--no-pager', '--plain'],
                    capture_output=True, text=True, timeout=10
                )
                
                if result.returncode == 0:
                    for line in result.stdout.split('\n')[1:]:  # Пропускаем заголовок
                        parts = line.strip().split()
                        if len(parts) >= 4:
                            service_name = parts[0]
                            load_state = parts[1]
                            active_state = parts[2]
                            sub_state = parts[3]
                            
                            self.system_services[service_name] = {
                                'load_state': load_state,
                                'active_state': active_state,
                                'sub_state': sub_state,
                                'type': 'systemd'
                            }
                
                self.logger.info(f"Найдено systemd сервисов: {len(self.system_services)}")
                
            except Exception as e:
                self.logger.debug(f"Не удалось получить список systemd сервисов: {e}")
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования сервисов: {e}")
    
    def _scan_network_connections(self):
        """Сканирует сетевые подключения"""
        try:
            self.network_connections.clear()
            
            for conn in psutil.net_connections():
                conn_id = f"{conn.laddr}_{conn.raddr}_{conn.status}"
                
                self.network_connections[conn_id] = {
                    'family': conn.family,
                    'type': conn.type,
                    'laddr': conn.laddr,
                    'raddr': conn.raddr,
                    'status': conn.status,
                    'pid': conn.pid
                }
            
            self.logger.info(f"Найдено сетевых подключений: {len(self.network_connections)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования сетевых подключений: {e}")
    
    def _scan_filesystems(self):
        """Сканирует файловые системы"""
        try:
            self.mounted_filesystems.clear()
            
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    self.mounted_filesystems[partition.device] = {
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free
                    }
                except Exception as e:
                    continue
            
            self.logger.info(f"Найдено файловых систем: {len(self.mounted_filesystems)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования файловых систем: {e}")
    
    def execute_command(self, command: str, shell: bool = True, timeout: int = 30, 
                       capture_output: bool = True, env: Dict = None) -> Dict:
        """
        Выполняет системную команду с расширенными возможностями
        
        Args:
            command: Команда для выполнения
            shell: Использовать ли shell
            timeout: Таймаут выполнения
            capture_output: Захватывать ли вывод
            env: Переменные окружения
            
        Returns:
            Результат выполнения команды
        """
        try:
            start_time = time.time()
            
            # Подготовка окружения
            exec_env = os.environ.copy()
            if env:
                exec_env.update(env)
            
            # Выполнение команды
            if shell and isinstance(command, str):
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE if capture_output else None,
                    stderr=subprocess.PIPE if capture_output else None,
                    env=exec_env,
                    text=True
                )
            else:
                cmd_list = command.split() if isinstance(command, str) else command
                process = subprocess.Popen(
                    cmd_list,
                    stdout=subprocess.PIPE if capture_output else None,
                    stderr=subprocess.PIPE if capture_output else None,
                    env=exec_env,
                    text=True
                )
            
            # Ожидание завершения с таймаутом
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                
                return {
                    'success': False,
                    'returncode': -1,
                    'stdout': stdout or '',
                    'stderr': stderr or '',
                    'execution_time': time.time() - start_time,
                    'timeout': True,
                    'command': command
                }
            
            return {
                'success': process.returncode == 0,
                'returncode': process.returncode,
                'stdout': stdout or '',
                'stderr': stderr or '',
                'execution_time': time.time() - start_time,
                'timeout': False,
                'command': command
            }
            
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'execution_time': time.time() - start_time if 'start_time' in locals() else 0,
                'timeout': False,
                'command': command,
                'exception': str(e)
            }
    
    def manage_process(self, action: str, pid: int = None, name: str = None, 
                      signal_type: int = signal.SIGTERM) -> Dict:
        """
        Управляет процессами
        
        Args:
            action: Действие ('kill', 'suspend', 'resume', 'info')
            pid: ID процесса
            name: Имя процесса
            signal_type: Тип сигнала
            
        Returns:
            Результат операции
        """
        try:
            # Поиск процесса
            target_processes = []
            
            if pid:
                try:
                    proc = psutil.Process(pid)
                    target_processes.append(proc)
                except psutil.NoSuchProcess:
                    return {'success': False, 'error': f'Процесс с PID {pid} не найден'}
            
            elif name:
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if name.lower() in proc.info['name'].lower():
                            target_processes.append(proc)
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if not target_processes:
                    return {'success': False, 'error': f'Процессы с именем "{name}" не найдены'}
            
            else:
                return {'success': False, 'error': 'Не указан PID или имя процесса'}
            
            # Выполнение действия
            results = []
            
            for proc in target_processes:
                try:
                    if action == 'kill':
                        proc.send_signal(signal_type)
                        result = {'pid': proc.pid, 'action': 'killed', 'success': True}
                    
                    elif action == 'suspend':
                        proc.suspend()
                        result = {'pid': proc.pid, 'action': 'suspended', 'success': True}
                    
                    elif action == 'resume':
                        proc.resume()
                        result = {'pid': proc.pid, 'action': 'resumed', 'success': True}
                    
                    elif action == 'info':
                        info = proc.as_dict(attrs=['pid', 'name', 'username', 'status', 
                                                 'cpu_percent', 'memory_info', 'cmdline'])
                        result = {'pid': proc.pid, 'action': 'info', 'success': True, 'info': info}
                    
                    else:
                        result = {'pid': proc.pid, 'action': action, 'success': False, 
                                'error': f'Неизвестное действие: {action}'}
                    
                    results.append(result)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    results.append({'pid': proc.pid, 'action': action, 'success': False, 
                                  'error': str(e)})
            
            return {'success': True, 'results': results}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def manage_service(self, action: str, service_name: str) -> Dict:
        """
        Управляет системными сервисами
        
        Args:
            action: Действие ('start', 'stop', 'restart', 'status', 'enable', 'disable')
            service_name: Имя сервиса
            
        Returns:
            Результат операции
        """
        try:
            # Команды systemctl
            systemctl_actions = {
                'start': 'start',
                'stop': 'stop',
                'restart': 'restart',
                'status': 'status',
                'enable': 'enable',
                'disable': 'disable',
                'reload': 'reload'
            }
            
            if action not in systemctl_actions:
                return {'success': False, 'error': f'Неизвестное действие: {action}'}
            
            # Выполнение команды
            cmd = ['systemctl', systemctl_actions[action], service_name]
            
            result = self.execute_command(cmd, shell=False, timeout=30)
            
            return {
                'success': result['success'],
                'service': service_name,
                'action': action,
                'output': result['stdout'],
                'error': result['stderr'],
                'returncode': result['returncode']
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def monitor_system_resources(self) -> Dict:
        """Мониторит системные ресурсы"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Память
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Диски
            disk_io = psutil.disk_io_counters()
            
            # Сеть
            net_io = psutil.net_io_counters()
            
            # Загрузка системы
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            
            return {
                'timestamp': time.time(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'frequency': {
                        'current': cpu_freq.current if cpu_freq else 0,
                        'min': cpu_freq.min if cpu_freq else 0,
                        'max': cpu_freq.max if cpu_freq else 0
                    }
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent,
                    'swap_total': swap.total,
                    'swap_used': swap.used,
                    'swap_percent': swap.percent
                },
                'disk': {
                    'read_bytes': disk_io.read_bytes if disk_io else 0,
                    'write_bytes': disk_io.write_bytes if disk_io else 0,
                    'read_count': disk_io.read_count if disk_io else 0,
                    'write_count': disk_io.write_count if disk_io else 0
                },
                'network': {
                    'bytes_sent': net_io.bytes_sent if net_io else 0,
                    'bytes_recv': net_io.bytes_recv if net_io else 0,
                    'packets_sent': net_io.packets_sent if net_io else 0,
                    'packets_recv': net_io.packets_recv if net_io else 0
                },
                'load_average': {
                    '1min': load_avg[0],
                    '5min': load_avg[1],
                    '15min': load_avg[2]
                }
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка мониторинга ресурсов: {e}")
            return {}
    
    def manage_files(self, action: str, path: str, **kwargs) -> Dict:
        """
        Управляет файлами и директориями
        
        Args:
            action: Действие ('create', 'delete', 'copy', 'move', 'chmod', 'chown')
            path: Путь к файлу/директории
            **kwargs: Дополнительные параметры
            
        Returns:
            Результат операции
        """
        try:
            path_obj = Path(path)
            
            if action == 'create':
                if kwargs.get('directory', False):
                    path_obj.mkdir(parents=True, exist_ok=True)
                    return {'success': True, 'action': 'directory_created', 'path': str(path_obj)}
                else:
                    content = kwargs.get('content', '')
                    path_obj.write_text(content)
                    return {'success': True, 'action': 'file_created', 'path': str(path_obj)}
            
            elif action == 'delete':
                if path_obj.is_dir():
                    import shutil
                    shutil.rmtree(path_obj)
                    return {'success': True, 'action': 'directory_deleted', 'path': str(path_obj)}
                else:
                    path_obj.unlink()
                    return {'success': True, 'action': 'file_deleted', 'path': str(path_obj)}
            
            elif action == 'copy':
                dest = kwargs.get('destination')
                if not dest:
                    return {'success': False, 'error': 'Не указан путь назначения'}
                
                import shutil
                if path_obj.is_dir():
                    shutil.copytree(path_obj, dest)
                else:
                    shutil.copy2(path_obj, dest)
                
                return {'success': True, 'action': 'copied', 'source': str(path_obj), 'destination': dest}
            
            elif action == 'move':
                dest = kwargs.get('destination')
                if not dest:
                    return {'success': False, 'error': 'Не указан путь назначения'}
                
                import shutil
                shutil.move(str(path_obj), dest)
                
                return {'success': True, 'action': 'moved', 'source': str(path_obj), 'destination': dest}
            
            elif action == 'chmod':
                mode = kwargs.get('mode')
                if mode is None:
                    return {'success': False, 'error': 'Не указан режим доступа'}
                
                path_obj.chmod(mode)
                return {'success': True, 'action': 'chmod', 'path': str(path_obj), 'mode': oct(mode)}
            
            elif action == 'chown':
                uid = kwargs.get('uid')
                gid = kwargs.get('gid')
                
                if uid is None or gid is None:
                    return {'success': False, 'error': 'Не указан UID или GID'}
                
                os.chown(path_obj, uid, gid)
                return {'success': True, 'action': 'chown', 'path': str(path_obj), 'uid': uid, 'gid': gid}
            
            else:
                return {'success': False, 'error': f'Неизвестное действие: {action}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def start_monitoring(self):
        """Запускает системный мониторинг"""
        try:
            if self.is_monitoring:
                return
            
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info("Системный мониторинг запущен")
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска мониторинга: {e}")
    
    def stop_monitoring(self):
        """Останавливает системный мониторинг"""
        try:
            self.is_monitoring = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=2.0)
            
            self.logger.info("Системный мониторинг остановлен")
            
        except Exception as e:
            self.logger.error(f"Ошибка остановки мониторинга: {e}")
    
    def _monitoring_loop(self):
        """Цикл системного мониторинга"""
        while self.is_monitoring:
            try:
                # Мониторинг ресурсов
                resources = self.monitor_system_resources()
                
                # Создание события
                event = {
                    'type': 'system_resources',
                    'timestamp': time.time(),
                    'data': resources
                }
                
                # Добавление в очередь событий
                try:
                    self.event_queue.put_nowait(event)
                except queue.Full:
                    # Удаляем старое событие
                    try:
                        self.event_queue.get_nowait()
                        self.event_queue.put_nowait(event)
                    except queue.Empty:
                        pass
                
                # Вызов обработчиков событий
                self._handle_event(event)
                
                time.sleep(5)  # Мониторинг каждые 5 секунд
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(1)
    
    def _handle_event(self, event: Dict):
        """Обрабатывает системное событие"""
        try:
            event_type = event.get('type')
            
            if event_type in self.event_handlers:
                for handler in self.event_handlers[event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        self.logger.error(f"Ошибка в обработчике события: {e}")
                        
        except Exception as e:
            self.logger.error(f"Ошибка обработки события: {e}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Регистрирует обработчик событий"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        self.logger.info(f"Зарегистрирован обработчик для события: {event_type}")
    
    def get_events(self, max_events: int = 100) -> List[Dict]:
        """Получает события из очереди"""
        events = []
        for _ in range(max_events):
            try:
                event = self.event_queue.get_nowait()
                events.append(event)
            except queue.Empty:
                break
        return events
    
    def get_system_status(self) -> Dict:
        """Возвращает полный статус системы"""
        try:
            return {
                'system_info': self.system_info,
                'processes': len(self.monitored_processes),
                'services': len(self.system_services),
                'network_connections': len(self.network_connections),
                'filesystems': len(self.mounted_filesystems),
                'resources': self.monitor_system_resources(),
                'monitoring_active': self.is_monitoring,
                'dbus_available': DBUS_AVAILABLE,
                'gtk_available': GTK_AVAILABLE
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса системы: {e}")
            return {}
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            self.stop_monitoring()
            
            # Очистка D-Bus подключений
            self.dbus_session = None
            self.dbus_system = None
            
            # Очистка данных
            self.monitored_processes.clear()
            self.system_services.clear()
            self.network_connections.clear()
            self.mounted_filesystems.clear()
            
            # Очистка очереди событий
            while not self.event_queue.empty():
                try:
                    self.event_queue.get_nowait()
                except queue.Empty:
                    break
            
            self.logger.info("Ресурсы системного контроллера очищены")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
    
    def __del__(self):
        """Деструктор"""
        self.cleanup()
