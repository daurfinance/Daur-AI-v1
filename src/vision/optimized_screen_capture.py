import numpy as np
from typing import Optional, Tuple
import mss
from threading import Lock
from .cv2_utils import cv

class OptimizedScreenCapture:
    """Оптимизированный захват экрана с буферизацией и кэшированием."""
    
    def __init__(self):
        self._sct = mss.mss()
        self._buffer_lock = Lock()
        self._last_frame: Optional[np.ndarray] = None
        self._last_frame_region: Optional[Tuple[int, int, int, int]] = None
        self._frame_buffer = []
        self._max_buffer_size = 5
        
    def capture(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Захватывает область экрана с оптимизацией.
        
        Args:
            region: Кортеж (left, top, width, height) области захвата
            
        Returns:
            Захваченное изображение как numpy массив
        """
        # Если регион тот же, возвращаем кэшированный кадр
        if (region == self._last_frame_region and 
            self._last_frame is not None):
            return self._last_frame
            
        with self._buffer_lock:
            # Захват нового кадра
            monitor = region if region else self._sct.monitors[0]
            screenshot = self._sct.grab(monitor)
            
            # Конвертация в numpy массив
            frame = np.array(screenshot)
            
            # Конвертация из BGRA в BGR
            frame = cv.cvtColor(frame, cv.COLOR_BGRA2BGR)
            
            # Обновление буфера
            self._frame_buffer.append(frame)
            if len(self._frame_buffer) > self._max_buffer_size:
                self._frame_buffer.pop(0)
            
            # Обновление кэша
            self._last_frame = frame
            self._last_frame_region = region
            
            return frame
    
    def get_buffer_average(self) -> Optional[np.ndarray]:
        """Возвращает усредненный кадр из буфера для уменьшения шума."""
        with self._buffer_lock:
            if not self._frame_buffer:
                return None
            
            return np.mean(self._frame_buffer, axis=0).astype(np.uint8)
    
    def clear_buffer(self) -> None:
        """Очищает буфер кадров."""
        with self._buffer_lock:
            self._frame_buffer.clear()
            self._last_frame = None
            self._last_frame_region = None