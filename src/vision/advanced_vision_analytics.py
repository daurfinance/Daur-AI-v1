"""
Advanced Vision Analytics for Daur-AI v2.0
Продвинутый анализ видео с обработкой в реальном времени

Поддерживает:
- Анализ видеопотока в реальном времени
- Обнаружение лиц, текста, штрих-кодов
- Callbacks для событий
- Запись результатов
- Многопоточная обработка
"""

import logging
import threading
import time
import cv2
from typing import Optional, Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoSource(Enum):
    """Источники видео"""
    WEBCAM = "webcam"
    FILE = "file"
    RTSP = "rtsp"
    HTTP = "http"


@dataclass
class DetectionEvent:
    """Событие обнаружения"""
    event_type: str  # face, text, barcode
    timestamp: datetime
    confidence: float
    data: Dict
    frame_number: int


class VideoAnalyzer:
    """Анализатор видео в реальном времени"""
    
    def __init__(self):
        """Инициализация"""
        from src.vision.real_vision_system import RealVisionSystem
        
        self.vision = RealVisionSystem()
        self.is_running = False
        self.stream_thread = None
        self.video_source = None
        self.source_type = None
        self.frame_count = 0
        self.events: List[DetectionEvent] = []
        self.callbacks: Dict[str, List[Callable]] = {
            'face': [],
            'text': [],
            'barcode': [],
            'frame': []
        }
        self.lock = threading.Lock()
        self.fps = 0
        self.last_frame_time = time.time()
        
        logger.info("Video Analyzer initialized")
    
    def register_callback(self, event_type: str, callback: Callable) -> bool:
        """Зарегистрировать callback для события"""
        if event_type not in self.callbacks:
            logger.warning(f"Unknown event type: {event_type}")
            return False
        
        with self.lock:
            self.callbacks[event_type].append(callback)
        logger.info(f"Callback registered for {event_type}")
        return True
    
    def start_stream(self, source: str, source_type: str = "webcam") -> bool:
        """
        Начать анализ видеопотока
        
        Args:
            source: Источник (0 для webcam, путь к файлу, RTSP URL)
            source_type: Тип источника (webcam, file, rtsp, http)
        
        Returns:
            True если успешно
        """
        if self.is_running:
            logger.warning("Stream already running")
            return False
        
        self.source_type = source_type
        
        # Открываем источник
        try:
            if source_type == "webcam":
                source = int(source) if isinstance(source, str) else source
            
            self.video_source = cv2.VideoCapture(source)
            
            if not self.video_source.isOpened():
                logger.error(f"Failed to open video source: {source}")
                return False
        
        except Exception as e:
            logger.error(f"Error opening video source: {e}")
            return False
        
        self.is_running = True
        self.frame_count = 0
        self.stream_thread = threading.Thread(
            target=self._stream_loop,
            daemon=True
        )
        self.stream_thread.start()
        
        logger.info(f"Stream started: {source_type} - {source}")
        return True
    
    def _stream_loop(self):
        """Основной цикл обработки видео"""
        while self.is_running:
            try:
                ret, frame = self.video_source.read()
                
                if not ret:
                    logger.warning("Failed to read frame")
                    break
                
                self.frame_count += 1
                
                # Обработка кадра
                self._process_frame(frame)
                
                # Вызываем callback для кадра
                with self.lock:
                    for callback in self.callbacks['frame']:
                        try:
                            callback(frame, self.frame_count)
                        except Exception as e:
                            logger.error(f"Error in frame callback: {e}")
                
                # Вычисляем FPS
                current_time = time.time()
                self.fps = 1.0 / (current_time - self.last_frame_time)
                self.last_frame_time = current_time
            
            except Exception as e:
                logger.error(f"Error in stream loop: {e}")
                break
        
        self.video_source.release()
        logger.info("Stream stopped")
    
    def _process_frame(self, frame):
        """Обработать кадр"""
        try:
            # Сохраняем временный файл
            temp_path = f"/tmp/frame_{self.frame_count}.jpg"
            cv2.imwrite(temp_path, frame)
            
            # Обнаружение лиц
            try:
                faces = self.vision.detect_faces(temp_path)
                if faces and faces['faces']:
                    for face in faces['faces']:
                        event = DetectionEvent(
                            event_type='face',
                            timestamp=datetime.now(),
                            confidence=face.get('confidence', 0.0),
                            data=face,
                            frame_number=self.frame_count
                        )
                        self._trigger_event(event)
            except Exception as e:
                logger.debug(f"Face detection error: {e}")
            
            # Обнаружение текста (OCR)
            try:
                ocr_result = self.vision.perform_ocr(temp_path)
                if ocr_result and ocr_result.get('text'):
                    event = DetectionEvent(
                        event_type='text',
                        timestamp=datetime.now(),
                        confidence=ocr_result.get('confidence', 0.0),
                        data={'text': ocr_result['text']},
                        frame_number=self.frame_count
                    )
                    self._trigger_event(event)
            except Exception as e:
                logger.debug(f"OCR error: {e}")
            
            # Обнаружение штрих-кодов
            try:
                barcodes = self.vision.detect_barcodes(temp_path)
                if barcodes and barcodes['barcodes']:
                    for barcode in barcodes['barcodes']:
                        event = DetectionEvent(
                            event_type='barcode',
                            timestamp=datetime.now(),
                            confidence=barcode.get('confidence', 0.0),
                            data=barcode,
                            frame_number=self.frame_count
                        )
                        self._trigger_event(event)
            except Exception as e:
                logger.debug(f"Barcode detection error: {e}")
            
            # Удаляем временный файл
            try:
                Path(temp_path).unlink()
            except Exception as e:
                pass
        
        except Exception as e:
            logger.error(f"Error processing frame: {e}")
    
    def _trigger_event(self, event: DetectionEvent):
        """Триггер события обнаружения"""
        with self.lock:
            self.events.append(event)
            
            # Вызываем callbacks
            for callback in self.callbacks[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in {event.event_type} callback: {e}")
    
    def stop_stream(self):
        """Остановить анализ"""
        self.is_running = False
        if self.stream_thread:
            self.stream_thread.join(timeout=5)
        logger.info("Stream analysis stopped")
    
    def get_statistics(self) -> Dict:
        """Получить статистику"""
        with self.lock:
            face_count = len([e for e in self.events if e.event_type == 'face'])
            text_count = len([e for e in self.events if e.event_type == 'text'])
            barcode_count = len([e for e in self.events if e.event_type == 'barcode'])
            
            return {
                'frames_processed': self.frame_count,
                'fps': self.fps,
                'faces_detected': face_count,
                'text_detected': text_count,
                'barcodes_detected': barcode_count,
                'total_events': len(self.events)
            }
    
    def get_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[DetectionEvent]:
        """Получить события"""
        with self.lock:
            if event_type:
                events = [e for e in self.events if e.event_type == event_type]
            else:
                events = self.events
            
            return events[-limit:] if events else []


class VideoRecorder:
    """Запись видео с результатами обнаружения"""
    
    def __init__(self, output_path: str):
        """Инициализация"""
        self.output_path = output_path
        self.video_writer = None
        self.is_recording = False
        
        logger.info(f"Video Recorder initialized: {output_path}")
    
    def start_recording(self, frame_width: int, frame_height: int, fps: int = 30) -> bool:
        """Начать запись"""
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            self.video_writer = cv2.VideoWriter(
                self.output_path,
                fourcc,
                fps,
                (frame_width, frame_height)
            )
            
            if not self.video_writer.isOpened():
                logger.error("Failed to open video writer")
                return False
            
            self.is_recording = True
            logger.info(f"Recording started: {self.output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error starting recording: {e}")
            return False
    
    def write_frame(self, frame) -> bool:
        """Записать кадр"""
        if not self.is_recording or not self.video_writer:
            return False
        
        try:
            self.video_writer.write(frame)
            return True
        except Exception as e:
            logger.error(f"Error writing frame: {e}")
            return False
    
    def stop_recording(self):
        """Остановить запись"""
        if self.video_writer:
            self.video_writer.release()
            self.is_recording = False
            logger.info("Recording stopped")


class FrameBuffer:
    """Буфер кадров для анализа"""
    
    def __init__(self, max_size: int = 30):
        """Инициализация"""
        self.max_size = max_size
        self.frames: List[tuple] = []  # (frame, timestamp)
        self.lock = threading.Lock()
    
    def add_frame(self, frame, timestamp: datetime = None):
        """Добавить кадр"""
        if timestamp is None:
            timestamp = datetime.now()
        
        with self.lock:
            self.frames.append((frame, timestamp))
            
            # Удаляем старые кадры
            if len(self.frames) > self.max_size:
                self.frames.pop(0)
    
    def get_frames(self, count: int = 10) -> List:
        """Получить последние кадры"""
        with self.lock:
            return [f for f, _ in self.frames[-count:]]
    
    def clear(self):
        """Очистить буфер"""
        with self.lock:
            self.frames.clear()
