#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль распознавания лиц
Детектирование, распознавание и анализ лиц

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import os
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

try:
    import cv2
    import numpy as np
except ImportError:
    cv2 = None
    np = None

try:
    import face_recognition
except ImportError:
    face_recognition = None


class FaceEmotionType(Enum):
    """Типы эмоций"""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    UNKNOWN = "unknown"


@dataclass
class FaceLocation:
    """Местоположение лица"""
    top: int
    right: int
    bottom: int
    left: int
    
    @property
    def width(self) -> int:
        return self.right - self.left
    
    @property
    def height(self) -> int:
        return self.bottom - self.top
    
    @property
    def center(self) -> Tuple[int, int]:
        return ((self.left + self.right) // 2, (self.top + self.bottom) // 2)


@dataclass
class FaceData:
    """Данные о лице"""
    location: FaceLocation
    encoding: Optional[np.ndarray] = None
    emotion: FaceEmotionType = FaceEmotionType.UNKNOWN
    confidence: float = 0.0
    name: str = "Unknown"
    age: Optional[int] = None
    gender: str = "Unknown"
    timestamp: datetime = field(default_factory=datetime.now)


class FaceRecognitionModule:
    """Модуль распознавания лиц"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.face_recognition')
        self.known_face_encodings: List[np.ndarray] = []
        self.known_face_names: List[str] = []
        self.face_history: List[FaceData] = []
        self.logger.info("Face Recognition Module инициализирован")
    
    # ==================== ДЕТЕКТИРОВАНИЕ ЛИЦ ====================
    
    def detect_faces_in_image(self, image_path: str) -> List[FaceData]:
        """
        Детектировать лица на изображении
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            List[FaceData]: Список найденных лиц
        """
        if not face_recognition or not cv2:
            self.logger.warning("face_recognition или cv2 не установлены")
            return []
        
        try:
            # Загрузить изображение
            image = face_recognition.load_image_file(image_path)
            
            # Найти лица
            face_locations = face_recognition.face_locations(image, model='hog')
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            faces = []
            for location, encoding in zip(face_locations, face_encodings):
                face_location = FaceLocation(
                    top=location[0],
                    right=location[1],
                    bottom=location[2],
                    left=location[3]
                )
                
                face_data = FaceData(
                    location=face_location,
                    encoding=encoding,
                    confidence=0.95  # Уверенность детектирования
                )
                
                faces.append(face_data)
            
            self.face_history.extend(faces)
            
            self.logger.info(f"Найдено {len(faces)} лиц на изображении: {image_path}")
            return faces
        
        except Exception as e:
            self.logger.error(f"Ошибка детектирования лиц: {e}")
            return []
    
    def detect_faces_in_video(self, video_path: str, frame_skip: int = 5) -> List[FaceData]:
        """
        Детектировать лица в видео
        
        Args:
            video_path: Путь к видео
            frame_skip: Пропускать каждый N-й кадр
            
        Returns:
            List[FaceData]: Список найденных лиц
        """
        if not face_recognition or not cv2:
            self.logger.warning("face_recognition или cv2 не установлены")
            return []
        
        try:
            cap = cv2.VideoCapture(video_path)
            faces = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame_count += 1
                
                # Пропустить кадры
                if frame_count % frame_skip != 0:
                    continue
                
                # Преобразовать в RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Найти лица
                face_locations = face_recognition.face_locations(rgb_frame, model='hog')
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                
                for location, encoding in zip(face_locations, face_encodings):
                    face_location = FaceLocation(
                        top=location[0],
                        right=location[1],
                        bottom=location[2],
                        left=location[3]
                    )
                    
                    face_data = FaceData(
                        location=face_location,
                        encoding=encoding,
                        confidence=0.95
                    )
                    
                    faces.append(face_data)
            
            cap.release()
            
            self.face_history.extend(faces)
            
            self.logger.info(f"Найдено {len(faces)} лиц в видео: {video_path}")
            return faces
        
        except Exception as e:
            self.logger.error(f"Ошибка детектирования лиц в видео: {e}")
            return []
    
    # ==================== РАСПОЗНАВАНИЕ ЛИЦ ====================
    
    def add_known_face(self, image_path: str, person_name: str) -> bool:
        """
        Добавить известное лицо
        
        Args:
            image_path: Путь к изображению
            person_name: Имя человека
            
        Returns:
            bool: Успешность операции
        """
        if not face_recognition:
            self.logger.warning("face_recognition не установлен")
            return False
        
        try:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if not face_encodings:
                self.logger.warning(f"Лица не найдены на изображении: {image_path}")
                return False
            
            # Использовать первое лицо
            self.known_face_encodings.append(face_encodings[0])
            self.known_face_names.append(person_name)
            
            self.logger.info(f"Добавлено известное лицо: {person_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка добавления известного лица: {e}")
            return False
    
    def recognize_faces(self, image_path: str, tolerance: float = 0.6) -> List[FaceData]:
        """
        Распознать лица на изображении
        
        Args:
            image_path: Путь к изображению
            tolerance: Допуск для сравнения (0.0-1.0)
            
        Returns:
            List[FaceData]: Список распознанных лиц
        """
        if not face_recognition:
            self.logger.warning("face_recognition не установлен")
            return []
        
        try:
            # Загрузить изображение
            image = face_recognition.load_image_file(image_path)
            
            # Найти лица
            face_locations = face_recognition.face_locations(image, model='hog')
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            faces = []
            
            for location, encoding in zip(face_locations, face_encodings):
                # Сравнить с известными лицами
                matches = face_recognition.compare_faces(
                    self.known_face_encodings,
                    encoding,
                    tolerance=tolerance
                )
                
                # Получить расстояния
                distances = face_recognition.face_distance(
                    self.known_face_encodings,
                    encoding
                )
                
                name = "Unknown"
                confidence = 0.0
                
                if len(distances) > 0:
                    best_match_index = np.argmin(distances)
                    
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = 1 - distances[best_match_index]
                
                face_location = FaceLocation(
                    top=location[0],
                    right=location[1],
                    bottom=location[2],
                    left=location[3]
                )
                
                face_data = FaceData(
                    location=face_location,
                    encoding=encoding,
                    name=name,
                    confidence=confidence
                )
                
                faces.append(face_data)
            
            self.face_history.extend(faces)
            
            self.logger.info(f"Распознано {len(faces)} лиц на изображении: {image_path}")
            return faces
        
        except Exception as e:
            self.logger.error(f"Ошибка распознавания лиц: {e}")
            return []
    
    # ==================== АНАЛИЗ ЛИЦ ====================
    
    def draw_face_boxes(self, image_path: str, output_path: str,
                       faces: Optional[List[FaceData]] = None) -> bool:
        """
        Нарисовать прямоугольники вокруг лиц
        
        Args:
            image_path: Путь к исходному изображению
            output_path: Путь для сохранения результата
            faces: Список лиц (если None, будут найдены автоматически)
            
        Returns:
            bool: Успешность операции
        """
        if not cv2:
            self.logger.warning("cv2 не установлен")
            return False
        
        try:
            # Загрузить изображение
            image = cv2.imread(image_path)
            
            # Найти лица если не переданы
            if faces is None:
                faces = self.detect_faces_in_image(image_path)
            
            # Нарисовать прямоугольники
            for face in faces:
                top = face.location.top
                right = face.location.right
                bottom = face.location.bottom
                left = face.location.left
                
                # Нарисовать прямоугольник
                cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
                
                # Добавить имя
                label = f"{face.name} ({face.confidence:.2f})"
                cv2.putText(image, label, (left, top - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Сохранить результат
            cv2.imwrite(output_path, image)
            
            self.logger.info(f"Результат сохранен: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка рисования прямоугольников: {e}")
            return False
    
    def get_face_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику по лицам
        
        Returns:
            Dict: Статистика
        """
        stats = {
            'total_faces': len(self.face_history),
            'known_faces': len(self.known_face_names),
            'unique_people': len(set(f.name for f in self.face_history)),
            'average_confidence': 0.0,
            'faces_by_name': {}
        }
        
        if self.face_history:
            stats['average_confidence'] = sum(f.confidence for f in self.face_history) / len(self.face_history)
            
            for face in self.face_history:
                if face.name not in stats['faces_by_name']:
                    stats['faces_by_name'][face.name] = 0
                stats['faces_by_name'][face.name] += 1
        
        return stats
    
    # ==================== ИСТОРИЯ ====================
    
    def get_face_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить историю лиц"""
        return [
            {
                'name': f.name,
                'confidence': f.confidence,
                'location': {
                    'top': f.location.top,
                    'right': f.location.right,
                    'bottom': f.location.bottom,
                    'left': f.location.left
                },
                'timestamp': f.timestamp.isoformat()
            }
            for f in self.face_history[-limit:]
        ]
    
    def clear_history(self):
        """Очистить историю"""
        self.face_history.clear()
        self.logger.info("История лиц очищена")
    
    def clear_known_faces(self):
        """Очистить известные лица"""
        self.known_face_encodings.clear()
        self.known_face_names.clear()
        self.logger.info("Известные лица очищены")


# Глобальный экземпляр
_face_recognition_module = None


def get_face_recognition_module() -> FaceRecognitionModule:
    """Получить модуль распознавания лиц"""
    global _face_recognition_module
    if _face_recognition_module is None:
        _face_recognition_module = FaceRecognitionModule()
    return _face_recognition_module

