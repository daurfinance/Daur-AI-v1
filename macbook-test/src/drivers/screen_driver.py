"""
Низкоуровневый драйвер для захвата экрана
Прямой доступ к видеобуферу, обход системных защит
"""

import ctypes
import ctypes.util
import numpy as np
import cv2
import mmap
import os
import struct
import time
import logging
from typing import Optional, Tuple, List
import threading
import queue

# Linux-специфичные импорты
try:
    import fcntl
    import termios
    from ctypes import CDLL, c_int, c_void_p, c_char_p, c_uint32, c_uint16, POINTER, Structure
except ImportError:
    pass

class FramebufferInfo(Structure):
    """Структура информации о фреймбуфере"""
    _fields_ = [
        ("xres", c_uint32),
        ("yres", c_uint32),
        ("xres_virtual", c_uint32),
        ("yres_virtual", c_uint32),
        ("xoffset", c_uint32),
        ("yoffset", c_uint32),
        ("bits_per_pixel", c_uint32),
        ("grayscale", c_uint32),
    ]

class ScreenDriver:
    """Низкоуровневый драйвер для захвата экрана"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Инициализация системных библиотек
        self._init_system_libs()
        
        # Состояние драйвера
        self.is_initialized = False
        self.framebuffer_fd = None
        self.framebuffer_map = None
        self.screen_info = {}
        
        # Буфер для кадров
        self.frame_buffer = queue.Queue(maxsize=10)
        self.capture_thread = None
        self.is_capturing = False
        
        # Инициализация
        self._initialize_driver()
    
    def _init_system_libs(self):
        """Инициализация системных библиотек"""
        try:
            # Загружаем системные библиотеки
            self.libc = ctypes.CDLL(ctypes.util.find_library('c'))
            self.libx11 = None
            
            # Пытаемся загрузить X11 библиотеки
            try:
                self.libx11 = ctypes.CDLL(ctypes.util.find_library('X11'))
                self.logger.info("X11 библиотека загружена")
            except:
                self.logger.warning("X11 библиотека недоступна")
            
            # Загружаем OpenGL если доступен
            try:
                self.libgl = ctypes.CDLL(ctypes.util.find_library('GL'))
                self.logger.info("OpenGL библиотека загружена")
            except:
                self.logger.warning("OpenGL библиотека недоступна")
                
        except Exception as e:
            self.logger.error(f"Ошибка инициализации системных библиотек: {e}")
    
    def _initialize_driver(self):
        """Инициализация драйвера"""
        try:
            # Метод 1: Прямой доступ к фреймбуферу
            if self._init_framebuffer():
                self.logger.info("Фреймбуфер инициализирован")
                self.is_initialized = True
                return
            
            # Метод 2: X11 захват
            if self._init_x11_capture():
                self.logger.info("X11 захват инициализирован")
                self.is_initialized = True
                return
            
            # Метод 3: Системные вызовы
            if self._init_system_calls():
                self.logger.info("Системные вызовы инициализированы")
                self.is_initialized = True
                return
            
            self.logger.warning("Не удалось инициализировать низкоуровневый доступ")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации драйвера: {e}")
    
    def _init_framebuffer(self) -> bool:
        """Инициализация прямого доступа к фреймбуферу"""
        try:
            # Пытаемся открыть фреймбуфер
            framebuffer_devices = ['/dev/fb0', '/dev/fb1', '/dev/graphics/fb0']
            
            for device in framebuffer_devices:
                try:
                    if os.path.exists(device):
                        self.framebuffer_fd = os.open(device, os.O_RDONLY)
                        
                        # Получаем информацию о фреймбуфере
                        fb_info = FramebufferInfo()
                        fcntl.ioctl(self.framebuffer_fd, 0x4600, fb_info)  # FBIOGET_VSCREENINFO
                        
                        self.screen_info = {
                            'width': fb_info.xres,
                            'height': fb_info.yres,
                            'bpp': fb_info.bits_per_pixel,
                            'device': device
                        }
                        
                        # Создаем memory map
                        buffer_size = fb_info.xres * fb_info.yres * (fb_info.bits_per_pixel // 8)
                        self.framebuffer_map = mmap.mmap(
                            self.framebuffer_fd, 
                            buffer_size, 
                            mmap.MAP_SHARED, 
                            mmap.PROT_READ
                        )
                        
                        self.logger.info(f"Фреймбуфер {device} открыт: {self.screen_info}")
                        return True
                        
                except Exception as e:
                    self.logger.debug(f"Не удалось открыть {device}: {e}")
                    continue
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации фреймбуфера: {e}")
            return False
    
    def _init_x11_capture(self) -> bool:
        """Инициализация X11 захвата"""
        try:
            if not self.libx11:
                return False
            
            # Определяем функции X11
            self.libx11.XOpenDisplay.restype = c_void_p
            self.libx11.XDefaultRootWindow.restype = c_uint32
            self.libx11.XGetImage.restype = c_void_p
            
            # Открываем дисплей
            display = self.libx11.XOpenDisplay(None)
            if not display:
                return False
            
            # Получаем корневое окно
            root_window = self.libx11.XDefaultRootWindow(display)
            
            # Получаем размеры экрана
            self.libx11.XDisplayWidth.restype = c_int
            self.libx11.XDisplayHeight.restype = c_int
            
            width = self.libx11.XDisplayWidth(display, 0)
            height = self.libx11.XDisplayHeight(display, 0)
            
            self.screen_info = {
                'width': width,
                'height': height,
                'display': display,
                'root_window': root_window,
                'method': 'x11'
            }
            
            self.logger.info(f"X11 захват инициализирован: {width}x{height}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации X11: {e}")
            return False
    
    def _init_system_calls(self) -> bool:
        """Инициализация через системные вызовы"""
        try:
            # Пытаемся использовать /proc/kcore для прямого доступа к памяти
            if os.path.exists('/proc/kcore'):
                self.screen_info = {
                    'method': 'syscalls',
                    'kcore_available': True
                }
                return True
            
            # Альтернативные методы
            if os.path.exists('/dev/mem'):
                self.screen_info = {
                    'method': 'syscalls',
                    'devmem_available': True
                }
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации системных вызовов: {e}")
            return False
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Захватывает кадр экрана на низком уровне"""
        try:
            if not self.is_initialized:
                return None
            
            method = self.screen_info.get('method', 'framebuffer')
            
            if method == 'framebuffer' and self.framebuffer_map:
                return self._capture_framebuffer()
            elif method == 'x11':
                return self._capture_x11()
            elif method == 'syscalls':
                return self._capture_syscalls()
            else:
                # Fallback к стандартному методу
                return self._capture_fallback()
                
        except Exception as e:
            self.logger.error(f"Ошибка захвата кадра: {e}")
            return None
    
    def _capture_framebuffer(self) -> Optional[np.ndarray]:
        """Захват через фреймбуфер"""
        try:
            if not self.framebuffer_map:
                return None
            
            width = self.screen_info['width']
            height = self.screen_info['height']
            bpp = self.screen_info['bpp']
            
            # Читаем данные из фреймбуфера
            self.framebuffer_map.seek(0)
            buffer_data = self.framebuffer_map.read(width * height * (bpp // 8))
            
            # Конвертируем в numpy array
            if bpp == 32:
                # RGBA или BGRA
                frame = np.frombuffer(buffer_data, dtype=np.uint8)
                frame = frame.reshape((height, width, 4))
                # Конвертируем в BGR для OpenCV
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            elif bpp == 24:
                # RGB или BGR
                frame = np.frombuffer(buffer_data, dtype=np.uint8)
                frame = frame.reshape((height, width, 3))
            elif bpp == 16:
                # RGB565
                frame = np.frombuffer(buffer_data, dtype=np.uint16)
                frame = frame.reshape((height, width))
                # Конвертируем RGB565 в BGR
                frame = self._rgb565_to_bgr(frame)
            else:
                self.logger.error(f"Неподдерживаемая глубина цвета: {bpp}")
                return None
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Ошибка захвата фреймбуфера: {e}")
            return None
    
    def _capture_x11(self) -> Optional[np.ndarray]:
        """Захват через X11"""
        try:
            display = self.screen_info['display']
            root_window = self.screen_info['root_window']
            width = self.screen_info['width']
            height = self.screen_info['height']
            
            # Захватываем изображение
            image = self.libx11.XGetImage(
                display, root_window, 0, 0, width, height, 0xFFFFFF, 2  # ZPixmap
            )
            
            if not image:
                return None
            
            # Конвертируем XImage в numpy array
            # Это упрощенная версия, реальная реализация сложнее
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Здесь должна быть реализация извлечения пикселей из XImage
            # Для демонстрации возвращаем пустой кадр
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Ошибка X11 захвата: {e}")
            return None
    
    def _capture_syscalls(self) -> Optional[np.ndarray]:
        """Захват через системные вызовы"""
        try:
            # Прямое чтение видеопамяти через /dev/mem
            # ВНИМАНИЕ: Требует root прав и может быть опасно
            
            if self.screen_info.get('devmem_available'):
                # Попытка чтения /dev/mem
                # Это очень низкоуровневый доступ
                pass
            
            # Альтернативный метод через /proc
            if self.screen_info.get('kcore_available'):
                # Чтение через /proc/kcore
                pass
            
            # Для безопасности возвращаем None
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка системных вызовов: {e}")
            return None
    
    def _capture_fallback(self) -> Optional[np.ndarray]:
        """Fallback метод захвата"""
        try:
            # Используем стандартные методы как fallback
            import pyautogui
            screenshot = pyautogui.screenshot()
            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            return frame
            
        except Exception as e:
            self.logger.error(f"Ошибка fallback захвата: {e}")
            return None
    
    def _rgb565_to_bgr(self, rgb565_frame: np.ndarray) -> np.ndarray:
        """Конвертирует RGB565 в BGR"""
        try:
            height, width = rgb565_frame.shape
            bgr_frame = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Извлекаем компоненты RGB565
            r = ((rgb565_frame & 0xF800) >> 11) << 3
            g = ((rgb565_frame & 0x07E0) >> 5) << 2
            b = (rgb565_frame & 0x001F) << 3
            
            # Собираем BGR
            bgr_frame[:, :, 0] = b  # Blue
            bgr_frame[:, :, 1] = g  # Green
            bgr_frame[:, :, 2] = r  # Red
            
            return bgr_frame
            
        except Exception as e:
            self.logger.error(f"Ошибка конвертации RGB565: {e}")
            return np.array([])
    
    def start_continuous_capture(self, fps: int = 30):
        """Запускает непрерывный захват кадров"""
        try:
            if self.is_capturing:
                return
            
            self.is_capturing = True
            self.capture_thread = threading.Thread(
                target=self._capture_loop, 
                args=(fps,), 
                daemon=True
            )
            self.capture_thread.start()
            
            self.logger.info(f"Непрерывный захват запущен с {fps} FPS")
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска непрерывного захвата: {e}")
    
    def stop_continuous_capture(self):
        """Останавливает непрерывный захват"""
        try:
            self.is_capturing = False
            if self.capture_thread:
                self.capture_thread.join(timeout=1.0)
            
            # Очищаем буфер
            while not self.frame_buffer.empty():
                try:
                    self.frame_buffer.get_nowait()
                except queue.Empty:
                    break
            
            self.logger.info("Непрерывный захват остановлен")
            
        except Exception as e:
            self.logger.error(f"Ошибка остановки захвата: {e}")
    
    def _capture_loop(self, fps: int):
        """Цикл захвата кадров"""
        frame_time = 1.0 / fps
        
        while self.is_capturing:
            start_time = time.time()
            
            try:
                frame = self.capture_frame()
                if frame is not None:
                    # Добавляем кадр в буфер
                    try:
                        self.frame_buffer.put_nowait({
                            'frame': frame,
                            'timestamp': time.time()
                        })
                    except queue.Full:
                        # Удаляем старый кадр
                        try:
                            self.frame_buffer.get_nowait()
                            self.frame_buffer.put_nowait({
                                'frame': frame,
                                'timestamp': time.time()
                            })
                        except queue.Empty:
                            pass
                
                # Контролируем FPS
                elapsed = time.time() - start_time
                sleep_time = frame_time - elapsed
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
            except Exception as e:
                self.logger.error(f"Ошибка в цикле захвата: {e}")
                time.sleep(0.1)
    
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Получает последний захваченный кадр"""
        try:
            if self.frame_buffer.empty():
                return None
            
            # Получаем все кадры и возвращаем последний
            latest_frame = None
            while not self.frame_buffer.empty():
                try:
                    frame_data = self.frame_buffer.get_nowait()
                    latest_frame = frame_data['frame']
                except queue.Empty:
                    break
            
            return latest_frame
            
        except Exception as e:
            self.logger.error(f"Ошибка получения кадра: {e}")
            return None
    
    def get_screen_info(self) -> dict:
        """Возвращает информацию о экране"""
        return self.screen_info.copy()
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            self.stop_continuous_capture()
            
            if self.framebuffer_map:
                self.framebuffer_map.close()
                self.framebuffer_map = None
            
            if self.framebuffer_fd:
                os.close(self.framebuffer_fd)
                self.framebuffer_fd = None
            
            self.logger.info("Ресурсы драйвера очищены")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
    
    def __del__(self):
        """Деструктор"""
        self.cleanup()
