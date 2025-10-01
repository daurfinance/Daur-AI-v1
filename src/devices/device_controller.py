"""
Интегрированный контроллер устройств
Управление всеми устройствами и системами через единый интерфейс
"""

import asyncio
import time
import logging
import json
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum
import threading

# Импорт компонентов системы
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from drivers.screen_driver import ScreenDriver
    from drivers.input_driver import InputDriver
    from drivers.camera_driver import CameraDriver
    from drivers.video_ocr_engine import VideoOCREngine
    from system.advanced_controller import AdvancedSystemController
    from browser.visual_browser_controller import VisualBrowserController
    from vision.screen_analyzer import ScreenAnalyzer
except ImportError as e:
    logging.warning(f"Некоторые драйверы недоступны: {e}")

class DeviceType(Enum):
    """Типы устройств"""
    SCREEN = "screen"
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    CAMERA = "camera"
    MICROPHONE = "microphone"
    SPEAKER = "speaker"
    BROWSER = "browser"
    SYSTEM = "system"

class DeviceStatus(Enum):
    """Статусы устройств"""
    AVAILABLE = "available"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"

@dataclass
class DeviceInfo:
    """Информация об устройстве"""
    device_type: DeviceType
    name: str
    status: DeviceStatus
    capabilities: List[str]
    last_used: float
    error_message: Optional[str] = None

class DeviceController:
    """Интегрированный контроллер устройств"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Драйверы устройств
        self.screen_driver = None
        self.input_driver = None
        self.camera_driver = None
        self.ocr_engine = None
        self.system_controller = None
        self.browser_controller = None
        self.screen_analyzer = None
        
        # Реестр устройств
        self.devices = {}
        
        # Блокировки для синхронизации
        self.device_locks = {}
        
        # Очередь команд
        self.command_queue = asyncio.Queue()
        
        # Статистика
        self.stats = {
            'commands_executed': 0,
            'devices_accessed': 0,
            'errors_occurred': 0,
            'uptime_start': time.time()
        }
        
        # Настройки
        self.max_concurrent_operations = 5
        self.device_timeout = 30.0
        self.retry_attempts = 3
        
        # Инициализация
        self._initialize()
    
    def _initialize(self):
        """Инициализация контроллера устройств"""
        try:
            # Инициализация драйверов
            self._initialize_drivers()
            
            # Регистрация устройств
            self._register_devices()
            
            # Создание блокировок
            self._create_device_locks()
            
            self.logger.info("Контроллер устройств инициализирован")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации контроллера устройств: {e}")
    
    def _initialize_drivers(self):
        """Инициализирует драйверы устройств"""
        try:
            # Экранный драйвер
            try:
                self.screen_driver = ScreenDriver()
                self.logger.info("Экранный драйвер инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать экранный драйвер: {e}")
            
            # Драйвер ввода
            try:
                self.input_driver = InputDriver()
                self.logger.info("Драйвер ввода инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать драйвер ввода: {e}")
            
            # Драйвер камеры
            try:
                self.camera_driver = CameraDriver()
                self.logger.info("Драйвер камеры инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать драйвер камеры: {e}")
            
            # OCR движок
            try:
                self.ocr_engine = VideoOCREngine()
                self.logger.info("OCR движок инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать OCR движок: {e}")
            
            # Системный контроллер
            try:
                self.system_controller = AdvancedSystemController()
                self.logger.info("Системный контроллер инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать системный контроллер: {e}")
            
            # Браузерный контроллер
            try:
                self.browser_controller = VisualBrowserController()
                self.logger.info("Браузерный контроллер инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать браузерный контроллер: {e}")
            
            # Анализатор экрана
            try:
                self.screen_analyzer = ScreenAnalyzer()
                self.logger.info("Анализатор экрана инициализирован")
            except Exception as e:
                self.logger.warning(f"Не удалось инициализировать анализатор экрана: {e}")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации драйверов: {e}")
    
    def _register_devices(self):
        """Регистрирует доступные устройства"""
        try:
            # Экран
            if self.screen_driver:
                self.devices[DeviceType.SCREEN] = DeviceInfo(
                    device_type=DeviceType.SCREEN,
                    name="Primary Screen",
                    status=DeviceStatus.AVAILABLE,
                    capabilities=["capture", "analyze", "ocr"],
                    last_used=0.0
                )
            
            # Клавиатура
            if self.input_driver:
                self.devices[DeviceType.KEYBOARD] = DeviceInfo(
                    device_type=DeviceType.KEYBOARD,
                    name="System Keyboard",
                    status=DeviceStatus.AVAILABLE,
                    capabilities=["type", "hotkeys", "shortcuts"],
                    last_used=0.0
                )
            
            # Мышь
            if self.input_driver:
                self.devices[DeviceType.MOUSE] = DeviceInfo(
                    device_type=DeviceType.MOUSE,
                    name="System Mouse",
                    status=DeviceStatus.AVAILABLE,
                    capabilities=["click", "move", "scroll", "drag"],
                    last_used=0.0
                )
            
            # Камера
            if self.camera_driver:
                self.devices[DeviceType.CAMERA] = DeviceInfo(
                    device_type=DeviceType.CAMERA,
                    name="System Camera",
                    status=DeviceStatus.AVAILABLE,
                    capabilities=["capture", "stream", "analyze"],
                    last_used=0.0
                )
            
            # Браузер
            if self.browser_controller:
                self.devices[DeviceType.BROWSER] = DeviceInfo(
                    device_type=DeviceType.BROWSER,
                    name="Web Browser",
                    status=DeviceStatus.AVAILABLE,
                    capabilities=["navigate", "interact", "scrape", "automate"],
                    last_used=0.0
                )
            
            # Система
            if self.system_controller:
                self.devices[DeviceType.SYSTEM] = DeviceInfo(
                    device_type=DeviceType.SYSTEM,
                    name="Operating System",
                    status=DeviceStatus.AVAILABLE,
                    capabilities=["execute", "monitor", "manage", "control"],
                    last_used=0.0
                )
            
            self.logger.info(f"Зарегистрировано {len(self.devices)} устройств")
            
        except Exception as e:
            self.logger.error(f"Ошибка регистрации устройств: {e}")
    
    def _create_device_locks(self):
        """Создает блокировки для устройств"""
        try:
            for device_type in self.devices:
                self.device_locks[device_type] = asyncio.Lock()
            
        except Exception as e:
            self.logger.error(f"Ошибка создания блокировок: {e}")
    
    async def execute_command(self, device_type: DeviceType, command: str, 
                            parameters: Dict = None) -> Dict:
        """
        Выполняет команду на устройстве
        
        Args:
            device_type: Тип устройства
            command: Команда для выполнения
            parameters: Параметры команды
            
        Returns:
            Результат выполнения
        """
        try:
            if device_type not in self.devices:
                return {'success': False, 'error': f'Устройство {device_type.value} недоступно'}
            
            device_info = self.devices[device_type]
            
            # Проверка статуса устройства
            if device_info.status != DeviceStatus.AVAILABLE:
                return {'success': False, 'error': f'Устройство {device_type.value} занято или недоступно'}
            
            # Получение блокировки устройства
            async with self.device_locks[device_type]:
                device_info.status = DeviceStatus.BUSY
                
                try:
                    # Выполнение команды
                    result = await self._execute_device_command(device_type, command, parameters or {})
                    
                    # Обновление статистики
                    self.stats['commands_executed'] += 1
                    device_info.last_used = time.time()
                    
                    if result.get('success', False):
                        device_info.status = DeviceStatus.AVAILABLE
                        device_info.error_message = None
                    else:
                        device_info.status = DeviceStatus.ERROR
                        device_info.error_message = result.get('error', 'Неизвестная ошибка')
                        self.stats['errors_occurred'] += 1
                    
                    return result
                    
                except Exception as e:
                    device_info.status = DeviceStatus.ERROR
                    device_info.error_message = str(e)
                    self.stats['errors_occurred'] += 1
                    
                    return {'success': False, 'error': str(e)}
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения команды {command} на {device_type.value}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_device_command(self, device_type: DeviceType, command: str, 
                                    parameters: Dict) -> Dict:
        """Выполняет команду на конкретном устройстве"""
        try:
            if device_type == DeviceType.SCREEN:
                return await self._execute_screen_command(command, parameters)
            
            elif device_type == DeviceType.KEYBOARD:
                return await self._execute_keyboard_command(command, parameters)
            
            elif device_type == DeviceType.MOUSE:
                return await self._execute_mouse_command(command, parameters)
            
            elif device_type == DeviceType.CAMERA:
                return await self._execute_camera_command(command, parameters)
            
            elif device_type == DeviceType.BROWSER:
                return await self._execute_browser_command(command, parameters)
            
            elif device_type == DeviceType.SYSTEM:
                return await self._execute_system_command(command, parameters)
            
            else:
                return {'success': False, 'error': f'Неизвестный тип устройства: {device_type.value}'}
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения команды устройства: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_screen_command(self, command: str, parameters: Dict) -> Dict:
        """Выполняет команды экрана"""
        try:
            if command == 'capture':
                if self.screen_driver:
                    screenshot = self.screen_driver.capture_screen()
                    return {'success': True, 'screenshot': screenshot, 'size': len(screenshot) if screenshot else 0}
                
            elif command == 'analyze':
                if self.screen_analyzer:
                    screenshot = self.screen_driver.capture_screen() if self.screen_driver else None
                    if screenshot:
                        analysis = self.screen_analyzer.analyze_screen(screenshot)
                        return {'success': True, 'analysis': analysis}
                
            elif command == 'ocr':
                if self.ocr_engine and self.screen_driver:
                    screenshot = self.screen_driver.capture_screen()
                    if screenshot:
                        # Конвертация в формат для OCR
                        import cv2
                        import numpy as np
                        
                        nparr = np.frombuffer(screenshot, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            text_results = self.ocr_engine.extract_text_from_frame(frame)
                            return {'success': True, 'text_results': text_results}
            
            return {'success': False, 'error': f'Неизвестная команда экрана: {command}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_keyboard_command(self, command: str, parameters: Dict) -> Dict:
        """Выполняет команды клавиатуры"""
        try:
            if command == 'type':
                text = parameters.get('text', '')
                if self.input_driver:
                    result = self.input_driver.type_text(text)
                    return {'success': result, 'text': text}
                
            elif command == 'hotkey':
                keys = parameters.get('keys', [])
                if self.input_driver:
                    result = self.input_driver.send_hotkey(keys)
                    return {'success': result, 'keys': keys}
                
            elif command == 'key_press':
                key = parameters.get('key', '')
                if self.input_driver:
                    result = self.input_driver.press_key(key)
                    return {'success': result, 'key': key}
            
            return {'success': False, 'error': f'Неизвестная команда клавиатуры: {command}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_mouse_command(self, command: str, parameters: Dict) -> Dict:
        """Выполняет команды мыши"""
        try:
            if command == 'click':
                x = parameters.get('x', 0)
                y = parameters.get('y', 0)
                button = parameters.get('button', 'left')
                
                if self.input_driver:
                    result = self.input_driver.click_at(x, y, button)
                    return {'success': result, 'position': (x, y), 'button': button}
                
            elif command == 'move':
                x = parameters.get('x', 0)
                y = parameters.get('y', 0)
                
                if self.input_driver:
                    result = self.input_driver.move_mouse(x, y)
                    return {'success': result, 'position': (x, y)}
                
            elif command == 'scroll':
                direction = parameters.get('direction', 'down')
                amount = parameters.get('amount', 3)
                
                if self.input_driver:
                    result = self.input_driver.scroll(direction, amount)
                    return {'success': result, 'direction': direction, 'amount': amount}
                
            elif command == 'drag':
                start_x = parameters.get('start_x', 0)
                start_y = parameters.get('start_y', 0)
                end_x = parameters.get('end_x', 0)
                end_y = parameters.get('end_y', 0)
                
                if self.input_driver:
                    result = self.input_driver.drag(start_x, start_y, end_x, end_y)
                    return {'success': result, 'start': (start_x, start_y), 'end': (end_x, end_y)}
            
            return {'success': False, 'error': f'Неизвестная команда мыши: {command}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_camera_command(self, command: str, parameters: Dict) -> Dict:
        """Выполняет команды камеры"""
        try:
            if command == 'capture':
                if self.camera_driver:
                    frame = self.camera_driver.capture_frame()
                    return {'success': frame is not None, 'frame_captured': frame is not None}
                
            elif command == 'start_stream':
                if self.camera_driver:
                    result = self.camera_driver.start_stream()
                    return {'success': result}
                
            elif command == 'stop_stream':
                if self.camera_driver:
                    result = self.camera_driver.stop_stream()
                    return {'success': result}
            
            return {'success': False, 'error': f'Неизвестная команда камеры: {command}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_browser_command(self, command: str, parameters: Dict) -> Dict:
        """Выполняет команды браузера"""
        try:
            if command == 'navigate':
                url = parameters.get('url', 'https://google.com')
                if self.browser_controller:
                    result = await self.browser_controller.navigate_to(url)
                    return result
                
            elif command == 'click_element':
                text = parameters.get('text', '')
                if self.browser_controller:
                    elements = await self.browser_controller.find_elements_by_text(text)
                    if elements:
                        result = await self.browser_controller.click_element(elements[0])
                        return result
                    else:
                        return {'success': False, 'error': f'Элемент с текстом "{text}" не найден'}
                
            elif command == 'type_text':
                target_text = parameters.get('target_text', '')
                input_text = parameters.get('input_text', '')
                
                if self.browser_controller:
                    elements = await self.browser_controller.find_elements_by_text(target_text)
                    if elements:
                        result = await self.browser_controller.type_text(elements[0], input_text)
                        return result
                    else:
                        return {'success': False, 'error': f'Элемент с текстом "{target_text}" не найден'}
                
            elif command == 'screenshot':
                if self.browser_controller:
                    screenshot = await self.browser_controller.take_screenshot()
                    return {'success': screenshot is not None, 'screenshot_taken': screenshot is not None}
            
            return {'success': False, 'error': f'Неизвестная команда браузера: {command}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def _execute_system_command(self, command: str, parameters: Dict) -> Dict:
        """Выполняет системные команды"""
        try:
            if command == 'execute':
                cmd = parameters.get('command', '')
                if self.system_controller:
                    result = self.system_controller.execute_command(cmd)
                    return {'success': True, 'output': result}
                
            elif command == 'monitor':
                resource = parameters.get('resource', 'cpu')
                if self.system_controller:
                    stats = self.system_controller.get_system_stats()
                    return {'success': True, 'stats': stats}
                
            elif command == 'manage_process':
                action = parameters.get('action', 'list')
                pid = parameters.get('pid', None)
                
                if self.system_controller:
                    if action == 'list':
                        processes = self.system_controller.list_processes()
                        return {'success': True, 'processes': processes}
                    elif action == 'kill' and pid:
                        result = self.system_controller.kill_process(pid)
                        return {'success': result, 'pid': pid}
            
            return {'success': False, 'error': f'Неизвестная системная команда: {command}'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def execute_complex_sequence(self, sequence: List[Dict]) -> List[Dict]:
        """
        Выполняет сложную последовательность команд
        
        Args:
            sequence: Список команд для выполнения
            
        Returns:
            Результаты выполнения
        """
        try:
            results = []
            
            for step in sequence:
                device_type_str = step.get('device_type', '')
                command = step.get('command', '')
                parameters = step.get('parameters', {})
                delay = step.get('delay', 0)
                
                # Конвертация строки в DeviceType
                try:
                    device_type = DeviceType(device_type_str)
                except ValueError:
                    results.append({
                        'success': False,
                        'error': f'Неизвестный тип устройства: {device_type_str}'
                    })
                    continue
                
                # Выполнение команды
                result = await self.execute_command(device_type, command, parameters)
                results.append(result)
                
                # Задержка между командами
                if delay > 0:
                    await asyncio.sleep(delay)
                
                # Прерывание при ошибке (если указано)
                if not result.get('success', False) and step.get('stop_on_error', False):
                    break
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения сложной последовательности: {e}")
            return [{'success': False, 'error': str(e)}]
    
    def get_device_status(self, device_type: DeviceType = None) -> Dict:
        """Возвращает статус устройств"""
        try:
            if device_type:
                if device_type in self.devices:
                    device_info = self.devices[device_type]
                    return {
                        'device_type': device_info.device_type.value,
                        'name': device_info.name,
                        'status': device_info.status.value,
                        'capabilities': device_info.capabilities,
                        'last_used': device_info.last_used,
                        'error_message': device_info.error_message
                    }
                else:
                    return {'error': f'Устройство {device_type.value} не найдено'}
            
            else:
                # Статус всех устройств
                status = {}
                for dev_type, dev_info in self.devices.items():
                    status[dev_type.value] = {
                        'name': dev_info.name,
                        'status': dev_info.status.value,
                        'capabilities': dev_info.capabilities,
                        'last_used': dev_info.last_used,
                        'error_message': dev_info.error_message
                    }
                
                return status
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статуса устройств: {e}")
            return {'error': str(e)}
    
    def get_statistics(self) -> Dict:
        """Возвращает статистику контроллера"""
        uptime = time.time() - self.stats['uptime_start']
        
        return {
            **self.stats,
            'uptime_seconds': uptime,
            'devices_registered': len(self.devices),
            'available_devices': len([d for d in self.devices.values() if d.status == DeviceStatus.AVAILABLE]),
            'busy_devices': len([d for d in self.devices.values() if d.status == DeviceStatus.BUSY]),
            'error_devices': len([d for d in self.devices.values() if d.status == DeviceStatus.ERROR]),
            'commands_per_minute': (self.stats['commands_executed'] / (uptime / 60)) if uptime > 0 else 0
        }
    
    async def health_check(self) -> Dict:
        """Проверяет здоровье всех устройств"""
        try:
            health_status = {}
            
            for device_type, device_info in self.devices.items():
                try:
                    # Простая проверка доступности
                    if device_info.status == DeviceStatus.AVAILABLE:
                        health_status[device_type.value] = {
                            'healthy': True,
                            'status': device_info.status.value,
                            'last_used': device_info.last_used
                        }
                    else:
                        health_status[device_type.value] = {
                            'healthy': False,
                            'status': device_info.status.value,
                            'error': device_info.error_message
                        }
                        
                except Exception as e:
                    health_status[device_type.value] = {
                        'healthy': False,
                        'status': 'error',
                        'error': str(e)
                    }
            
            overall_health = all(status['healthy'] for status in health_status.values())
            
            return {
                'overall_healthy': overall_health,
                'devices': health_status,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка проверки здоровья: {e}")
            return {
                'overall_healthy': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    async def cleanup(self):
        """Очистка ресурсов"""
        try:
            # Остановка всех активных операций
            for device_info in self.devices.values():
                if device_info.status == DeviceStatus.BUSY:
                    device_info.status = DeviceStatus.OFFLINE
            
            # Очистка драйверов
            if self.browser_controller:
                await self.browser_controller.cleanup()
            
            if self.camera_driver:
                self.camera_driver.cleanup()
            
            if self.ocr_engine:
                self.ocr_engine.cleanup()
            
            # Очистка очереди команд
            while not self.command_queue.empty():
                try:
                    self.command_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            self.logger.info("Ресурсы контроллера устройств очищены")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
