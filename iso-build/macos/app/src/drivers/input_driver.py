"""
Низкоуровневый драйвер ввода
Прямой доступ к устройствам ввода, обход системных защит
"""

import ctypes
import ctypes.util
import os
import struct
import time
import logging
import threading
import queue
from typing import Optional, Tuple, List, Dict, Callable
import fcntl
import select

# Linux input event структуры
class InputEvent(ctypes.Structure):
    _fields_ = [
        ("tv_sec", ctypes.c_long),
        ("tv_usec", ctypes.c_long),
        ("type", ctypes.c_uint16),
        ("code", ctypes.c_uint16),
        ("value", ctypes.c_int32),
    ]

# Константы для событий ввода
EV_SYN = 0x00
EV_KEY = 0x01
EV_REL = 0x02
EV_ABS = 0x03
EV_MSC = 0x04

# Коды клавиш
KEY_ESC = 1
KEY_ENTER = 28
KEY_SPACE = 57
KEY_LEFTCTRL = 29
KEY_LEFTALT = 56
KEY_LEFTSHIFT = 42

# Коды мыши
BTN_LEFT = 0x110
BTN_RIGHT = 0x111
BTN_MIDDLE = 0x112
REL_X = 0x00
REL_Y = 0x01
REL_WHEEL = 0x08

class InputDriver:
    """Низкоуровневый драйвер для управления вводом"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Инициализация системных библиотек
        self._init_system_libs()
        
        # Устройства ввода
        self.keyboard_devices = []
        self.mouse_devices = []
        self.input_devices = {}
        
        # Виртуальные устройства
        self.virtual_keyboard_fd = None
        self.virtual_mouse_fd = None
        
        # Мониторинг событий
        self.event_queue = queue.Queue()
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # Хуки и перехватчики
        self.key_hooks = {}
        self.mouse_hooks = {}
        
        # Инициализация
        self._initialize_driver()
    
    def _init_system_libs(self):
        """Инициализация системных библиотек"""
        try:
            self.libc = ctypes.CDLL(ctypes.util.find_library('c'))
            
            # Загружаем библиотеки для работы с устройствами
            try:
                self.libudev = ctypes.CDLL(ctypes.util.find_library('udev'))
                self.logger.info("udev библиотека загружена")
            except:
                self.logger.warning("udev библиотека недоступна")
                self.libudev = None
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации системных библиотек: {e}")
    
    def _initialize_driver(self):
        """Инициализация драйвера"""
        try:
            # Сканируем устройства ввода
            self._scan_input_devices()
            
            # Создаем виртуальные устройства
            self._create_virtual_devices()
            
            # Настраиваем перехват событий
            self._setup_event_interception()
            
            self.logger.info("Драйвер ввода инициализирован")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации драйвера ввода: {e}")
    
    def _scan_input_devices(self):
        """Сканирует доступные устройства ввода"""
        try:
            input_dir = '/dev/input'
            if not os.path.exists(input_dir):
                self.logger.error("Директория /dev/input не найдена")
                return
            
            # Сканируем все event устройства
            for device_name in os.listdir(input_dir):
                if device_name.startswith('event'):
                    device_path = os.path.join(input_dir, device_name)
                    
                    try:
                        # Пытаемся открыть устройство
                        fd = os.open(device_path, os.O_RDONLY | os.O_NONBLOCK)
                        
                        # Получаем информацию об устройстве
                        device_info = self._get_device_info(fd, device_path)
                        
                        if device_info:
                            self.input_devices[device_path] = {
                                'fd': fd,
                                'info': device_info,
                                'type': self._detect_device_type(device_info)
                            }
                            
                            # Классифицируем устройство
                            if device_info['type'] == 'keyboard':
                                self.keyboard_devices.append(device_path)
                            elif device_info['type'] == 'mouse':
                                self.mouse_devices.append(device_path)
                        else:
                            os.close(fd)
                            
                    except Exception as e:
                        self.logger.debug(f"Не удалось открыть {device_path}: {e}")
                        continue
            
            self.logger.info(f"Найдено устройств: клавиатур={len(self.keyboard_devices)}, мышей={len(self.mouse_devices)}")
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования устройств: {e}")
    
    def _get_device_info(self, fd: int, device_path: str) -> Optional[Dict]:
        """Получает информацию об устройстве"""
        try:
            # EVIOCGNAME - получить имя устройства
            EVIOCGNAME = 0x80ff4506
            name_buffer = ctypes.create_string_buffer(256)
            
            try:
                fcntl.ioctl(fd, EVIOCGNAME, name_buffer)
                device_name = name_buffer.value.decode('utf-8', errors='ignore')
            except:
                device_name = "Unknown Device"
            
            # EVIOCGID - получить ID устройства
            EVIOCGID = 0x80084502
            id_buffer = ctypes.create_string_buffer(8)
            
            try:
                fcntl.ioctl(fd, EVIOCGID, id_buffer)
                vendor, product, version, bustype = struct.unpack('HHHH', id_buffer.raw)
            except:
                vendor = product = version = bustype = 0
            
            # Определяем возможности устройства
            capabilities = self._get_device_capabilities(fd)
            
            return {
                'name': device_name,
                'path': device_path,
                'vendor': vendor,
                'product': product,
                'version': version,
                'bustype': bustype,
                'capabilities': capabilities,
                'type': self._detect_device_type_from_caps(capabilities)
            }
            
        except Exception as e:
            self.logger.debug(f"Ошибка получения информации об устройстве: {e}")
            return None
    
    def _get_device_capabilities(self, fd: int) -> Dict:
        """Получает возможности устройства"""
        try:
            capabilities = {}
            
            # EVIOCGBIT - получить битовую маску возможностей
            EVIOCGBIT = lambda ev_type: 0x80404520 + ev_type
            
            # Проверяем различные типы событий
            for ev_type in [EV_KEY, EV_REL, EV_ABS]:
                try:
                    bit_buffer = ctypes.create_string_buffer(128)  # 1024 бита
                    fcntl.ioctl(fd, EVIOCGBIT(ev_type), bit_buffer)
                    
                    # Конвертируем в список поддерживаемых кодов
                    supported_codes = []
                    for byte_idx, byte_val in enumerate(bit_buffer.raw):
                        if isinstance(byte_val, str):
                            byte_val = ord(byte_val)
                        
                        for bit_idx in range(8):
                            if byte_val & (1 << bit_idx):
                                code = byte_idx * 8 + bit_idx
                                supported_codes.append(code)
                    
                    if supported_codes:
                        capabilities[ev_type] = supported_codes
                        
                except:
                    continue
            
            return capabilities
            
        except Exception as e:
            self.logger.debug(f"Ошибка получения возможностей: {e}")
            return {}
    
    def _detect_device_type_from_caps(self, capabilities: Dict) -> str:
        """Определяет тип устройства по возможностям"""
        try:
            has_keys = EV_KEY in capabilities
            has_rel = EV_REL in capabilities
            has_abs = EV_ABS in capabilities
            
            if has_keys and capabilities.get(EV_KEY):
                key_codes = capabilities[EV_KEY]
                
                # Проверяем наличие кнопок мыши
                mouse_buttons = [BTN_LEFT, BTN_RIGHT, BTN_MIDDLE]
                has_mouse_buttons = any(btn in key_codes for btn in mouse_buttons)
                
                # Проверяем наличие клавиш клавиатуры
                keyboard_keys = [KEY_ESC, KEY_ENTER, KEY_SPACE]
                has_keyboard_keys = any(key in key_codes for key in keyboard_keys)
                
                if has_mouse_buttons and has_rel:
                    return 'mouse'
                elif has_keyboard_keys:
                    return 'keyboard'
                elif has_abs:
                    return 'touchpad'
            
            return 'unknown'
            
        except Exception as e:
            self.logger.debug(f"Ошибка определения типа устройства: {e}")
            return 'unknown'
    
    def _detect_device_type(self, device_info: Dict) -> str:
        """Определяет тип устройства"""
        return device_info.get('type', 'unknown')
    
    def _create_virtual_devices(self):
        """Создает виртуальные устройства для эмуляции ввода"""
        try:
            # Создаем виртуальную клавиатуру
            self._create_virtual_keyboard()
            
            # Создаем виртуальную мышь
            self._create_virtual_mouse()
            
        except Exception as e:
            self.logger.error(f"Ошибка создания виртуальных устройств: {e}")
    
    def _create_virtual_keyboard(self):
        """Создает виртуальную клавиатуру"""
        try:
            uinput_path = '/dev/uinput'
            if not os.path.exists(uinput_path):
                uinput_path = '/dev/input/uinput'
            
            if not os.path.exists(uinput_path):
                self.logger.warning("uinput устройство недоступно")
                return
            
            # Открываем uinput
            self.virtual_keyboard_fd = os.open(uinput_path, os.O_WRONLY | os.O_NONBLOCK)
            
            # Настраиваем возможности виртуальной клавиатуры
            UI_SET_EVBIT = 0x40045564
            UI_SET_KEYBIT = 0x40045565
            UI_DEV_CREATE = 0x5501
            
            # Включаем события клавиатуры
            fcntl.ioctl(self.virtual_keyboard_fd, UI_SET_EVBIT, EV_KEY)
            fcntl.ioctl(self.virtual_keyboard_fd, UI_SET_EVBIT, EV_SYN)
            
            # Добавляем все клавиши
            for key_code in range(1, 256):
                try:
                    fcntl.ioctl(self.virtual_keyboard_fd, UI_SET_KEYBIT, key_code)
                except:
                    continue
            
            # Создаем устройство
            device_info = struct.pack('80sHHHH', 
                b'Daur-AI Virtual Keyboard', 0, 0, 0, 0)
            os.write(self.virtual_keyboard_fd, device_info)
            fcntl.ioctl(self.virtual_keyboard_fd, UI_DEV_CREATE)
            
            self.logger.info("Виртуальная клавиатура создана")
            
        except Exception as e:
            self.logger.error(f"Ошибка создания виртуальной клавиатуры: {e}")
    
    def _create_virtual_mouse(self):
        """Создает виртуальную мышь"""
        try:
            uinput_path = '/dev/uinput'
            if not os.path.exists(uinput_path):
                uinput_path = '/dev/input/uinput'
            
            if not os.path.exists(uinput_path):
                return
            
            # Открываем uinput для мыши
            self.virtual_mouse_fd = os.open(uinput_path, os.O_WRONLY | os.O_NONBLOCK)
            
            UI_SET_EVBIT = 0x40045564
            UI_SET_KEYBIT = 0x40045565
            UI_SET_RELBIT = 0x40045566
            UI_DEV_CREATE = 0x5501
            
            # Настраиваем события мыши
            fcntl.ioctl(self.virtual_mouse_fd, UI_SET_EVBIT, EV_KEY)
            fcntl.ioctl(self.virtual_mouse_fd, UI_SET_EVBIT, EV_REL)
            fcntl.ioctl(self.virtual_mouse_fd, UI_SET_EVBIT, EV_SYN)
            
            # Добавляем кнопки мыши
            for btn in [BTN_LEFT, BTN_RIGHT, BTN_MIDDLE]:
                fcntl.ioctl(self.virtual_mouse_fd, UI_SET_KEYBIT, btn)
            
            # Добавляем оси движения
            for axis in [REL_X, REL_Y, REL_WHEEL]:
                fcntl.ioctl(self.virtual_mouse_fd, UI_SET_RELBIT, axis)
            
            # Создаем устройство
            device_info = struct.pack('80sHHHH', 
                b'Daur-AI Virtual Mouse', 0, 0, 0, 0)
            os.write(self.virtual_mouse_fd, device_info)
            fcntl.ioctl(self.virtual_mouse_fd, UI_DEV_CREATE)
            
            self.logger.info("Виртуальная мышь создана")
            
        except Exception as e:
            self.logger.error(f"Ошибка создания виртуальной мыши: {e}")
    
    def _setup_event_interception(self):
        """Настраивает перехват событий ввода"""
        try:
            # Запускаем мониторинг событий
            self.start_event_monitoring()
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки перехвата событий: {e}")
    
    def send_key_event(self, key_code: int, press: bool = True):
        """Отправляет событие клавиши"""
        try:
            if not self.virtual_keyboard_fd:
                self.logger.warning("Виртуальная клавиатура недоступна")
                return
            
            # Создаем событие
            event = InputEvent()
            event.tv_sec = int(time.time())
            event.tv_usec = int((time.time() % 1) * 1000000)
            event.type = EV_KEY
            event.code = key_code
            event.value = 1 if press else 0
            
            # Отправляем событие
            os.write(self.virtual_keyboard_fd, event)
            
            # Отправляем синхронизацию
            sync_event = InputEvent()
            sync_event.tv_sec = event.tv_sec
            sync_event.tv_usec = event.tv_usec
            sync_event.type = EV_SYN
            sync_event.code = 0
            sync_event.value = 0
            
            os.write(self.virtual_keyboard_fd, sync_event)
            
        except Exception as e:
            self.logger.error(f"Ошибка отправки события клавиши: {e}")
    
    def send_mouse_event(self, button: Optional[int] = None, x: int = 0, y: int = 0, wheel: int = 0):
        """Отправляет событие мыши"""
        try:
            if not self.virtual_mouse_fd:
                self.logger.warning("Виртуальная мышь недоступна")
                return
            
            events = []
            timestamp = time.time()
            tv_sec = int(timestamp)
            tv_usec = int((timestamp % 1) * 1000000)
            
            # Движение мыши
            if x != 0:
                event = InputEvent()
                event.tv_sec = tv_sec
                event.tv_usec = tv_usec
                event.type = EV_REL
                event.code = REL_X
                event.value = x
                events.append(event)
            
            if y != 0:
                event = InputEvent()
                event.tv_sec = tv_sec
                event.tv_usec = tv_usec
                event.type = EV_REL
                event.code = REL_Y
                event.value = y
                events.append(event)
            
            # Колесо мыши
            if wheel != 0:
                event = InputEvent()
                event.tv_sec = tv_sec
                event.tv_usec = tv_usec
                event.type = EV_REL
                event.code = REL_WHEEL
                event.value = wheel
                events.append(event)
            
            # Кнопка мыши
            if button is not None:
                event = InputEvent()
                event.tv_sec = tv_sec
                event.tv_usec = tv_usec
                event.type = EV_KEY
                event.code = button
                event.value = 1  # Нажатие
                events.append(event)
            
            # Синхронизация
            sync_event = InputEvent()
            sync_event.tv_sec = tv_sec
            sync_event.tv_usec = tv_usec
            sync_event.type = EV_SYN
            sync_event.code = 0
            sync_event.value = 0
            events.append(sync_event)
            
            # Отправляем все события
            for event in events:
                os.write(self.virtual_mouse_fd, event)
            
        except Exception as e:
            self.logger.error(f"Ошибка отправки события мыши: {e}")
    
    def start_event_monitoring(self):
        """Запускает мониторинг событий ввода"""
        try:
            if self.is_monitoring:
                return
            
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._event_monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            self.logger.info("Мониторинг событий ввода запущен")
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска мониторинга: {e}")
    
    def stop_event_monitoring(self):
        """Останавливает мониторинг событий"""
        try:
            self.is_monitoring = False
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=1.0)
            
            self.logger.info("Мониторинг событий остановлен")
            
        except Exception as e:
            self.logger.error(f"Ошибка остановки мониторинга: {e}")
    
    def _event_monitoring_loop(self):
        """Цикл мониторинга событий"""
        while self.is_monitoring:
            try:
                # Получаем список файловых дескрипторов для мониторинга
                fds = [device['fd'] for device in self.input_devices.values()]
                
                if not fds:
                    time.sleep(0.1)
                    continue
                
                # Ждем события с таймаутом
                ready_fds, _, _ = select.select(fds, [], [], 0.1)
                
                for fd in ready_fds:
                    try:
                        # Читаем события
                        data = os.read(fd, ctypes.sizeof(InputEvent))
                        if len(data) == ctypes.sizeof(InputEvent):
                            event = InputEvent.from_buffer_copy(data)
                            self._process_input_event(fd, event)
                            
                    except OSError:
                        # Устройство отключено или недоступно
                        continue
                    except Exception as e:
                        self.logger.debug(f"Ошибка чтения события: {e}")
                        continue
                
            except Exception as e:
                self.logger.error(f"Ошибка в цикле мониторинга: {e}")
                time.sleep(0.1)
    
    def _process_input_event(self, fd: int, event: InputEvent):
        """Обрабатывает событие ввода"""
        try:
            # Находим устройство по файловому дескриптору
            device_path = None
            for path, device in self.input_devices.items():
                if device['fd'] == fd:
                    device_path = path
                    break
            
            if not device_path:
                return
            
            device_info = self.input_devices[device_path]
            
            # Создаем событие для обработки
            processed_event = {
                'device': device_path,
                'device_type': device_info['type'],
                'timestamp': event.tv_sec + event.tv_usec / 1000000.0,
                'type': event.type,
                'code': event.code,
                'value': event.value
            }
            
            # Добавляем в очередь
            try:
                self.event_queue.put_nowait(processed_event)
            except queue.Full:
                # Удаляем старое событие
                try:
                    self.event_queue.get_nowait()
                    self.event_queue.put_nowait(processed_event)
                except queue.Empty:
                    pass
            
            # Вызываем хуки
            self._call_event_hooks(processed_event)
            
        except Exception as e:
            self.logger.debug(f"Ошибка обработки события: {e}")
    
    def _call_event_hooks(self, event: Dict):
        """Вызывает зарегистрированные хуки для события"""
        try:
            if event['type'] == EV_KEY:
                # Хуки клавиатуры
                for hook_id, hook_func in self.key_hooks.items():
                    try:
                        hook_func(event)
                    except Exception as e:
                        self.logger.debug(f"Ошибка в хуке клавиатуры {hook_id}: {e}")
            
            elif event['type'] in [EV_REL, EV_ABS]:
                # Хуки мыши
                for hook_id, hook_func in self.mouse_hooks.items():
                    try:
                        hook_func(event)
                    except Exception as e:
                        self.logger.debug(f"Ошибка в хуке мыши {hook_id}: {e}")
                        
        except Exception as e:
            self.logger.debug(f"Ошибка вызова хуков: {e}")
    
    def register_key_hook(self, hook_id: str, callback: Callable):
        """Регистрирует хук для событий клавиатуры"""
        self.key_hooks[hook_id] = callback
        self.logger.debug(f"Зарегистрирован хук клавиатуры: {hook_id}")
    
    def register_mouse_hook(self, hook_id: str, callback: Callable):
        """Регистрирует хук для событий мыши"""
        self.mouse_hooks[hook_id] = callback
        self.logger.debug(f"Зарегистрирован хук мыши: {hook_id}")
    
    def unregister_hook(self, hook_id: str):
        """Удаляет хук"""
        if hook_id in self.key_hooks:
            del self.key_hooks[hook_id]
        if hook_id in self.mouse_hooks:
            del self.mouse_hooks[hook_id]
        self.logger.debug(f"Хук удален: {hook_id}")
    
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
    
    def get_device_list(self) -> Dict:
        """Возвращает список устройств ввода"""
        return {
            'keyboards': self.keyboard_devices,
            'mice': self.mouse_devices,
            'all_devices': {path: device['info'] for path, device in self.input_devices.items()}
        }
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            self.stop_event_monitoring()
            
            # Закрываем виртуальные устройства
            if self.virtual_keyboard_fd:
                os.close(self.virtual_keyboard_fd)
                self.virtual_keyboard_fd = None
            
            if self.virtual_mouse_fd:
                os.close(self.virtual_mouse_fd)
                self.virtual_mouse_fd = None
            
            # Закрываем устройства ввода
            for device in self.input_devices.values():
                try:
                    os.close(device['fd'])
                except:
                    pass
            
            self.input_devices.clear()
            self.keyboard_devices.clear()
            self.mouse_devices.clear()
            
            self.logger.info("Ресурсы драйвера ввода очищены")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
    
    def __del__(self):
        """Деструктор"""
        self.cleanup()
