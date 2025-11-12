"""
Низкоуровневый драйвер камеры
Прямой доступ к видеоустройствам через V4L2
"""

import ctypes
import ctypes.util
import os
import struct
import time
import logging
import threading
import queue
import mmap
from typing import Optional, Tuple, List, Dict
import fcntl
import select
import numpy as np

# V4L2 константы и структуры
VIDIOC_QUERYCAP = 0x80685600
VIDIOC_ENUM_FMT = 0xc0405602
VIDIOC_G_FMT = 0xc0cc5604
VIDIOC_S_FMT = 0xc0cc5605
VIDIOC_REQBUFS = 0xc0145608
VIDIOC_QUERYBUF = 0xc0445609
VIDIOC_QBUF = 0xc044560f
VIDIOC_DQBUF = 0xc0445611
VIDIOC_STREAMON = 0x40045612
VIDIOC_STREAMOFF = 0x40045613

V4L2_BUF_TYPE_VIDEO_CAPTURE = 1
V4L2_MEMORY_MMAP = 1
V4L2_FIELD_NONE = 1

# Форматы пикселей
V4L2_PIX_FMT_YUYV = 0x56595559
V4L2_PIX_FMT_MJPEG = 0x47504A4D
V4L2_PIX_FMT_RGB24 = 0x33424752

class V4L2Capability(ctypes.Structure):
    _fields_ = [
        ("driver", ctypes.c_char * 16),
        ("card", ctypes.c_char * 32),
        ("bus_info", ctypes.c_char * 32),
        ("version", ctypes.c_uint32),
        ("capabilities", ctypes.c_uint32),
        ("device_caps", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32 * 3),
    ]

class V4L2PixFormat(ctypes.Structure):
    _fields_ = [
        ("width", ctypes.c_uint32),
        ("height", ctypes.c_uint32),
        ("pixelformat", ctypes.c_uint32),
        ("field", ctypes.c_uint32),
        ("bytesperline", ctypes.c_uint32),
        ("sizeimage", ctypes.c_uint32),
        ("colorspace", ctypes.c_uint32),
        ("priv", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("ycbcr_enc", ctypes.c_uint32),
        ("quantization", ctypes.c_uint32),
        ("xfer_func", ctypes.c_uint32),
    ]

class V4L2Format(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint32),
        ("fmt", V4L2PixFormat),
    ]

class V4L2RequestBuffers(ctypes.Structure):
    _fields_ = [
        ("count", ctypes.c_uint32),
        ("type", ctypes.c_uint32),
        ("memory", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32 * 2),
    ]

class V4L2Buffer(ctypes.Structure):
    _fields_ = [
        ("index", ctypes.c_uint32),
        ("type", ctypes.c_uint32),
        ("bytesused", ctypes.c_uint32),
        ("flags", ctypes.c_uint32),
        ("field", ctypes.c_uint32),
        ("timestamp", ctypes.c_uint64),
        ("timecode", ctypes.c_uint32 * 4),
        ("sequence", ctypes.c_uint32),
        ("memory", ctypes.c_uint32),
        ("m_offset", ctypes.c_uint32),
        ("length", ctypes.c_uint32),
        ("reserved2", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
    ]

class CameraDriver:
    """Низкоуровневый драйвер камеры"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Состояние драйвера
        self.camera_devices = {}
        self.active_cameras = {}
        
        # Буферы для кадров
        self.frame_buffers = {}
        self.capture_threads = {}
        self.is_capturing = {}
        
        # Инициализация
        self._scan_camera_devices()
    
    def _scan_camera_devices(self):
        """Сканирует доступные камеры"""
        try:
            video_dir = '/dev'
            camera_count = 0
            
            # Сканируем video устройства
            for i in range(10):  # Проверяем video0-video9
                device_path = f'/dev/video{i}'
                
                if os.path.exists(device_path):
                    try:
                        # Пытаемся открыть устройство
                        fd = os.open(device_path, os.O_RDWR | os.O_NONBLOCK)
                        
                        # Получаем информацию о камере
                        camera_info = self._get_camera_info(fd, device_path)
                        
                        if camera_info and camera_info.get('is_camera'):
                            self.camera_devices[device_path] = {
                                'fd': fd,
                                'info': camera_info,
                                'index': i
                            }
                            camera_count += 1
                            self.logger.info(f"Найдена камера: {device_path} - {camera_info['name']}")
                        else:
                            os.close(fd)
                            
                    except Exception as e:
                        self.logger.debug(f"Не удалось открыть {device_path}: {e}")
                        continue
            
            self.logger.info(f"Найдено камер: {camera_count}")
            
        except Exception as e:
            self.logger.error(f"Ошибка сканирования камер: {e}")
    
    def _get_camera_info(self, fd: int, device_path: str) -> Optional[Dict]:
        """Получает информацию о камере"""
        try:
            # Получаем возможности устройства
            cap = V4L2Capability()
            fcntl.ioctl(fd, VIDIOC_QUERYCAP, cap)
            
            # Проверяем, что это камера
            V4L2_CAP_VIDEO_CAPTURE = 0x00000001
            is_camera = bool(cap.capabilities & V4L2_CAP_VIDEO_CAPTURE)
            
            if not is_camera:
                return None
            
            # Получаем поддерживаемые форматы
            formats = self._get_supported_formats(fd)
            
            return {
                'name': cap.card.decode('utf-8', errors='ignore'),
                'driver': cap.driver.decode('utf-8', errors='ignore'),
                'bus_info': cap.bus_info.decode('utf-8', errors='ignore'),
                'version': cap.version,
                'capabilities': cap.capabilities,
                'device_path': device_path,
                'formats': formats,
                'is_camera': True
            }
            
        except Exception as e:
            self.logger.debug(f"Ошибка получения информации о камере: {e}")
            return None
    
    def _get_supported_formats(self, fd: int) -> List[Dict]:
        """Получает поддерживаемые форматы камеры"""
        formats = []
        
        try:
            # Структура для перечисления форматов
            class V4L2FmtDesc(ctypes.Structure):
                _fields_ = [
                    ("index", ctypes.c_uint32),
                    ("type", ctypes.c_uint32),
                    ("flags", ctypes.c_uint32),
                    ("description", ctypes.c_char * 32),
                    ("pixelformat", ctypes.c_uint32),
                    ("reserved", ctypes.c_uint32 * 4),
                ]
            
            index = 0
            while True:
                try:
                    fmt_desc = V4L2FmtDesc()
                    fmt_desc.index = index
                    fmt_desc.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
                    
                    fcntl.ioctl(fd, VIDIOC_ENUM_FMT, fmt_desc)
                    
                    # Конвертируем fourcc в строку
                    fourcc = struct.pack('<I', fmt_desc.pixelformat).decode('ascii', errors='ignore')
                    
                    formats.append({
                        'description': fmt_desc.description.decode('utf-8', errors='ignore'),
                        'pixelformat': fmt_desc.pixelformat,
                        'fourcc': fourcc,
                        'index': index
                    })
                    
                    index += 1
                    
                except OSError:
                    # Больше форматов нет
                    break
                    
        except Exception as e:
            self.logger.debug(f"Ошибка получения форматов: {e}")
        
        return formats
    
    def open_camera(self, device_path: str, width: int = 640, height: int = 480, 
                   pixelformat: int = V4L2_PIX_FMT_YUYV) -> bool:
        """Открывает камеру для захвата"""
        try:
            if device_path not in self.camera_devices:
                self.logger.error(f"Камера не найдена: {device_path}")
                return False
            
            if device_path in self.active_cameras:
                self.logger.warning(f"Камера уже открыта: {device_path}")
                return True
            
            fd = self.camera_devices[device_path]['fd']
            
            # Настраиваем формат
            if not self._set_format(fd, width, height, pixelformat):
                return False
            
            # Настраиваем буферы
            if not self._setup_buffers(fd, device_path):
                return False
            
            # Запускаем захват
            if not self._start_streaming(fd):
                return False
            
            self.active_cameras[device_path] = {
                'fd': fd,
                'width': width,
                'height': height,
                'pixelformat': pixelformat,
                'frame_queue': queue.Queue(maxsize=10)
            }
            
            # Запускаем поток захвата
            self._start_capture_thread(device_path)
            
            self.logger.info(f"Камера открыта: {device_path} ({width}x{height})")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка открытия камеры: {e}")
            return False
    
    def _set_format(self, fd: int, width: int, height: int, pixelformat: int) -> bool:
        """Устанавливает формат камеры"""
        try:
            # Получаем текущий формат
            fmt = V4L2Format()
            fmt.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
            fcntl.ioctl(fd, VIDIOC_G_FMT, fmt)
            
            # Устанавливаем новый формат
            fmt.fmt.width = width
            fmt.fmt.height = height
            fmt.fmt.pixelformat = pixelformat
            fmt.fmt.field = V4L2_FIELD_NONE
            
            fcntl.ioctl(fd, VIDIOC_S_FMT, fmt)
            
            # Проверяем установленный формат
            fcntl.ioctl(fd, VIDIOC_G_FMT, fmt)
            
            if fmt.fmt.width != width or fmt.fmt.height != height:
                self.logger.warning(f"Формат изменен: {fmt.fmt.width}x{fmt.fmt.height}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка установки формата: {e}")
            return False
    
    def _setup_buffers(self, fd: int, device_path: str, buffer_count: int = 4) -> bool:
        """Настраивает буферы для захвата"""
        try:
            # Запрашиваем буферы
            req_bufs = V4L2RequestBuffers()
            req_bufs.count = buffer_count
            req_bufs.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
            req_bufs.memory = V4L2_MEMORY_MMAP
            
            fcntl.ioctl(fd, VIDIOC_REQBUFS, req_bufs)
            
            if req_bufs.count < 2:
                self.logger.error("Недостаточно буферов")
                return False
            
            # Создаем memory-mapped буферы
            buffers = []
            for i in range(req_bufs.count):
                buf = V4L2Buffer()
                buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
                buf.memory = V4L2_MEMORY_MMAP
                buf.index = i
                
                fcntl.ioctl(fd, VIDIOC_QUERYBUF, buf)
                
                # Создаем memory map
                buffer_map = mmap.mmap(
                    fd, buf.length,
                    mmap.MAP_SHARED,
                    mmap.PROT_READ | mmap.PROT_WRITE,
                    offset=buf.m_offset
                )
                
                buffers.append({
                    'map': buffer_map,
                    'length': buf.length,
                    'index': i
                })
                
                # Ставим буфер в очередь
                fcntl.ioctl(fd, VIDIOC_QBUF, buf)
            
            self.frame_buffers[device_path] = buffers
            
            self.logger.info(f"Настроено {len(buffers)} буферов для {device_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка настройки буферов: {e}")
            return False
    
    def _start_streaming(self, fd: int) -> bool:
        """Запускает потоковый захват"""
        try:
            buf_type = ctypes.c_int(V4L2_BUF_TYPE_VIDEO_CAPTURE)
            fcntl.ioctl(fd, VIDIOC_STREAMON, buf_type)
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска потока: {e}")
            return False
    
    def _start_capture_thread(self, device_path: str):
        """Запускает поток захвата кадров"""
        try:
            self.is_capturing[device_path] = True
            
            capture_thread = threading.Thread(
                target=self._capture_loop,
                args=(device_path,),
                daemon=True
            )
            capture_thread.start()
            
            self.capture_threads[device_path] = capture_thread
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска потока захвата: {e}")
    
    def _capture_loop(self, device_path: str):
        """Цикл захвата кадров"""
        try:
            fd = self.active_cameras[device_path]['fd']
            frame_queue = self.active_cameras[device_path]['frame_queue']
            
            while self.is_capturing.get(device_path, False):
                try:
                    # Ждем готовый буфер
                    ready_fds, _, _ = select.select([fd], [], [], 1.0)
                    
                    if fd not in ready_fds:
                        continue
                    
                    # Получаем буфер
                    buf = V4L2Buffer()
                    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE
                    buf.memory = V4L2_MEMORY_MMAP
                    
                    fcntl.ioctl(fd, VIDIOC_DQBUF, buf)
                    
                    # Читаем данные из буфера
                    buffer_info = self.frame_buffers[device_path][buf.index]
                    buffer_map = buffer_info['map']
                    
                    buffer_map.seek(0)
                    frame_data = buffer_map.read(buf.bytesused)
                    
                    # Конвертируем в numpy array
                    frame = self._convert_frame(
                        frame_data, 
                        self.active_cameras[device_path]['width'],
                        self.active_cameras[device_path]['height'],
                        self.active_cameras[device_path]['pixelformat']
                    )
                    
                    if frame is not None:
                        # Добавляем кадр в очередь
                        try:
                            frame_queue.put_nowait({
                                'frame': frame,
                                'timestamp': time.time(),
                                'sequence': buf.sequence
                            })
                        except queue.Full:
                            # Удаляем старый кадр
                            try:
                                frame_queue.get_nowait()
                                frame_queue.put_nowait({
                                    'frame': frame,
                                    'timestamp': time.time(),
                                    'sequence': buf.sequence
                                })
                            except queue.Empty:
                                pass
                    
                    # Возвращаем буфер в очередь
                    fcntl.ioctl(fd, VIDIOC_QBUF, buf)
                    
                except Exception as e:
                    self.logger.debug(f"Ошибка в цикле захвата: {e}")
                    time.sleep(0.01)
                    
        except Exception as e:
            self.logger.error(f"Критическая ошибка в цикле захвата: {e}")
    
    def _convert_frame(self, frame_data: bytes, width: int, height: int, pixelformat: int) -> Optional[np.ndarray]:
        """Конвертирует данные кадра в numpy array"""
        try:
            if pixelformat == V4L2_PIX_FMT_YUYV:
                # YUYV формат
                return self._convert_yuyv_to_bgr(frame_data, width, height)
            elif pixelformat == V4L2_PIX_FMT_MJPEG:
                # MJPEG формат
                return self._convert_mjpeg_to_bgr(frame_data)
            elif pixelformat == V4L2_PIX_FMT_RGB24:
                # RGB24 формат
                frame = np.frombuffer(frame_data, dtype=np.uint8)
                frame = frame.reshape((height, width, 3))
                # Конвертируем RGB в BGR
                return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            else:
                self.logger.warning(f"Неподдерживаемый формат: {pixelformat}")
                return None
                
        except Exception as e:
            self.logger.debug(f"Ошибка конвертации кадра: {e}")
            return None
    
    def _convert_yuyv_to_bgr(self, frame_data: bytes, width: int, height: int) -> np.ndarray:
        """Конвертирует YUYV в BGR"""
        try:
            # YUYV: Y0 U0 Y1 V0 (4 байта на 2 пикселя)
            yuyv = np.frombuffer(frame_data, dtype=np.uint8)
            yuyv = yuyv.reshape((height, width // 2, 4))
            
            # Извлекаем компоненты
            y0 = yuyv[:, :, 0]
            u = yuyv[:, :, 1]
            y1 = yuyv[:, :, 2]
            v = yuyv[:, :, 3]
            
            # Создаем YUV изображение
            yuv = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Заполняем Y канал
            yuv[:, 0::2, 0] = y0  # Четные пиксели
            yuv[:, 1::2, 0] = y1  # Нечетные пиксели
            
            # Заполняем U и V каналы (интерполяция)
            yuv[:, 0::2, 1] = u
            yuv[:, 1::2, 1] = u
            yuv[:, 0::2, 2] = v
            yuv[:, 1::2, 2] = v
            
            # Конвертируем YUV в BGR
            import cv2
            bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
            
            return bgr
            
        except Exception as e:
            self.logger.debug(f"Ошибка конвертации YUYV: {e}")
            return np.array([])
    
    def _convert_mjpeg_to_bgr(self, frame_data: bytes) -> np.ndarray:
        """Конвертирует MJPEG в BGR"""
        try:
            import cv2
            
            # Декодируем JPEG
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return frame if frame is not None else np.array([])
            
        except Exception as e:
            self.logger.debug(f"Ошибка конвертации MJPEG: {e}")
            return np.array([])
    
    def capture_frame(self, device_path: str) -> Optional[np.ndarray]:
        """Захватывает кадр с камеры"""
        try:
            if device_path not in self.active_cameras:
                return None
            
            frame_queue = self.active_cameras[device_path]['frame_queue']
            
            # Получаем последний кадр
            latest_frame = None
            while not frame_queue.empty():
                try:
                    frame_data = frame_queue.get_nowait()
                    latest_frame = frame_data['frame']
                except queue.Empty:
                    break
            
            return latest_frame
            
        except Exception as e:
            self.logger.error(f"Ошибка захвата кадра: {e}")
            return None
    
    def close_camera(self, device_path: str):
        """Закрывает камеру"""
        try:
            if device_path not in self.active_cameras:
                return
            
            # Останавливаем захват
            self.is_capturing[device_path] = False
            
            # Ждем завершения потока
            if device_path in self.capture_threads:
                self.capture_threads[device_path].join(timeout=1.0)
                del self.capture_threads[device_path]
            
            # Останавливаем поток
            fd = self.active_cameras[device_path]['fd']
            try:
                buf_type = ctypes.c_int(V4L2_BUF_TYPE_VIDEO_CAPTURE)
                fcntl.ioctl(fd, VIDIOC_STREAMOFF, buf_type)
            except:
                pass
            
            # Очищаем буферы
            if device_path in self.frame_buffers:
                for buffer_info in self.frame_buffers[device_path]:
                    try:
                        buffer_info['map'].close()
                    except:
                        pass
                del self.frame_buffers[device_path]
            
            # Удаляем из активных
            del self.active_cameras[device_path]
            
            self.logger.info(f"Камера закрыта: {device_path}")
            
        except Exception as e:
            self.logger.error(f"Ошибка закрытия камеры: {e}")
    
    def get_camera_list(self) -> Dict:
        """Возвращает список доступных камер"""
        return {
            path: device['info'] 
            for path, device in self.camera_devices.items()
        }
    
    def get_active_cameras(self) -> List[str]:
        """Возвращает список активных камер"""
        return list(self.active_cameras.keys())
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            # Закрываем все активные камеры
            for device_path in list(self.active_cameras.keys()):
                self.close_camera(device_path)
            
            # Закрываем файловые дескрипторы
            for device in self.camera_devices.values():
                try:
                    os.close(device['fd'])
                except:
                    pass
            
            self.camera_devices.clear()
            
            self.logger.info("Ресурсы драйвера камеры очищены")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
    
    def __del__(self):
        """Деструктор"""
        self.cleanup()
