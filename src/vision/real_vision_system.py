"""
Real Vision System for Daur-AI v2.0
Полнофункциональный модуль компьютерного зрения

Поддерживает:
- OCR (оптическое распознавание символов) с EasyOCR и Tesseract
- Распознавание лиц (face_recognition)
- Детектирование штрих-кодов и QR кодов (pyzbar)
- Полный анализ изображений
- История анализов
- Экспорт в JSON
"""

import cv2
import numpy as np
import logging
import json
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import deque
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Попытка импортировать необходимые библиотеки
try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False
    logger.warning("EasyOCR not installed. Install with: pip install easyocr")

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False
    logger.warning("Tesseract not installed. Install with: pip install pytesseract")

try:
    import face_recognition
    HAS_FACE_RECOGNITION = True
except ImportError:
    HAS_FACE_RECOGNITION = False
    logger.warning("face_recognition not installed. Install with: pip install face_recognition")

try:
    from pyzbar import pyzbar
    HAS_PYZBAR = True
except ImportError:
    HAS_PYZBAR = False
    logger.warning("pyzbar not installed. Install with: pip install pyzbar")


class OCREngine(Enum):
    """Движки OCR"""
    EASYOCR = "easyocr"
    TESSERACT = "tesseract"
    AUTO = "auto"


@dataclass
class TextDetection:
    """Детектированный текст"""
    text: str
    confidence: float  # 0-1
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    language: Optional[str] = None


@dataclass
class FaceDetection:
    """Детектированное лицо"""
    face_id: int
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float  # 0-1
    name: Optional[str] = None
    distance: Optional[float] = None  # Расстояние до известного лица


@dataclass
class BarcodeDetection:
    """Детектированный штрих-код"""
    data: str  # Данные штрих-кода
    barcode_type: str  # Тип (QR_CODE, CODE_128 и т.д.)
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)


@dataclass
class VisionAnalysisResult:
    """Результат анализа изображения"""
    timestamp: str
    image_path: Optional[str]
    image_size: Tuple[int, int]  # (width, height)
    texts: List[TextDetection]
    faces: List[FaceDetection]
    barcodes: List[BarcodeDetection]
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'image_path': self.image_path,
            'image_size': self.image_size,
            'texts': [asdict(t) for t in self.texts],
            'faces': [asdict(f) for f in self.faces],
            'barcodes': [asdict(b) for b in self.barcodes]
        }


class RealVisionSystem:
    """Полнофункциональная система компьютерного зрения"""
    
    def __init__(self, history_size: int = 100, ocr_engine: OCREngine = OCREngine.AUTO):
        """
        Инициализация системы
        
        Args:
            history_size: Размер истории анализов
            ocr_engine: Движок OCR для использования
        """
        self.history_size = history_size
        self.analysis_history: deque = deque(maxlen=history_size)
        self.lock = threading.Lock()
        
        # Инициализация OCR
        self.ocr_engine = ocr_engine
        self.ocr_reader = None
        self._init_ocr()
        
        # Известные лица для распознавания
        self.known_face_encodings = []
        self.known_face_names = []
        
        logger.info(f"Real Vision System initialized with OCR engine: {ocr_engine.value}")
    
    def _init_ocr(self):
        """Инициализация OCR движка"""
        if self.ocr_engine == OCREngine.AUTO:
            # Используем EasyOCR если доступен, иначе Tesseract
            if HAS_EASYOCR:
                self.ocr_engine = OCREngine.EASYOCR
            elif HAS_TESSERACT:
                self.ocr_engine = OCREngine.TESSERACT
            else:
                logger.warning("No OCR engine available")
                return
        
        if self.ocr_engine == OCREngine.EASYOCR and HAS_EASYOCR:
            try:
                self.ocr_reader = easyocr.Reader(['en', 'ru'])
                logger.info("EasyOCR initialized")
            except Exception as e:
                logger.error(f"Error initializing EasyOCR: {e}")
        elif self.ocr_engine == OCREngine.TESSERACT and HAS_TESSERACT:
            logger.info("Tesseract OCR ready")
    
    def add_known_face(self, image_path: str, name: str) -> bool:
        """Добавить известное лицо для распознавания"""
        if not HAS_FACE_RECOGNITION:
            logger.error("face_recognition not installed")
            return False
        
        try:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                self.known_face_encodings.append(face_encodings[0])
                self.known_face_names.append(name)
                logger.info(f"Added known face: {name}")
                return True
            else:
                logger.warning(f"No faces found in {image_path}")
                return False
        except Exception as e:
            logger.error(f"Error adding known face: {e}")
            return False
    
    def extract_text(self, image_path: str, languages: List[str] = None) -> List[TextDetection]:
        """Извлечь текст из изображения"""
        try:
            if self.ocr_engine == OCREngine.EASYOCR and self.ocr_reader:
                return self._extract_text_easyocr(image_path, languages)
            elif self.ocr_engine == OCREngine.TESSERACT and HAS_TESSERACT:
                return self._extract_text_tesseract(image_path)
            else:
                logger.error("No OCR engine available")
                return []
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return []
    
    def _extract_text_easyocr(self, image_path: str, languages: List[str] = None) -> List[TextDetection]:
        """Извлечь текст используя EasyOCR"""
        try:
            results = self.ocr_reader.readtext(image_path)
            detections = []
            
            for (bbox, text, confidence) in results:
                # Преобразуем bbox в формат (x1, y1, x2, y2)
                bbox_array = np.array(bbox)
                x1, y1 = bbox_array.min(axis=0).astype(int)
                x2, y2 = bbox_array.max(axis=0).astype(int)
                
                detection = TextDetection(
                    text=text,
                    confidence=float(confidence),
                    bbox=(int(x1), int(y1), int(x2), int(y2)),
                    language="multi"
                )
                detections.append(detection)
            
            logger.info(f"Extracted {len(detections)} text regions from {image_path}")
            return detections
        except Exception as e:
            logger.error(f"Error in EasyOCR: {e}")
            return []
    
    def _extract_text_tesseract(self, image_path: str) -> List[TextDetection]:
        """Извлечь текст используя Tesseract"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not read image: {image_path}")
                return []
            
            # Преобразуем в grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Используем Tesseract с детальной информацией
            data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
            
            detections = []
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    detection = TextDetection(
                        text=data['text'][i],
                        confidence=int(data['conf'][i]) / 100.0,
                        bbox=(data['left'][i], data['top'][i], 
                              data['left'][i] + data['width'][i],
                              data['top'][i] + data['height'][i]),
                        language="auto"
                    )
                    detections.append(detection)
            
            logger.info(f"Extracted {len(detections)} text regions from {image_path}")
            return detections
        except Exception as e:
            logger.error(f"Error in Tesseract: {e}")
            return []
    
    def detect_faces(self, image_path: str) -> List[FaceDetection]:
        """Детектировать лица в изображении"""
        if not HAS_FACE_RECOGNITION:
            logger.error("face_recognition not installed")
            return []
        
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            detections = []
            for i, (top, right, bottom, left) in enumerate(face_locations):
                face_detection = FaceDetection(
                    face_id=i,
                    bbox=(left, top, right, bottom),
                    confidence=1.0
                )
                
                # Пытаемся распознать лицо
                if self.known_face_encodings:
                    distances = face_recognition.face_distance(
                        self.known_face_encodings,
                        face_encodings[i]
                    )
                    best_match_index = np.argmin(distances)
                    
                    if distances[best_match_index] < 0.6:  # Порог совпадения
                        face_detection.name = self.known_face_names[best_match_index]
                        face_detection.distance = float(distances[best_match_index])
                
                detections.append(face_detection)
            
            logger.info(f"Detected {len(detections)} faces in {image_path}")
            return detections
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def detect_barcodes(self, image_path: str) -> List[BarcodeDetection]:
        """Детектировать штрих-коды и QR коды"""
        if not HAS_PYZBAR:
            logger.error("pyzbar not installed")
            return []
        
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not read image: {image_path}")
                return []
            
            barcodes = pyzbar.decode(image)
            detections = []
            
            for barcode in barcodes:
                (x, y, w, h) = barcode.rect
                detection = BarcodeDetection(
                    data=barcode.data.decode('utf-8'),
                    barcode_type=barcode.type,
                    bbox=(x, y, x + w, y + h)
                )
                detections.append(detection)
            
            logger.info(f"Detected {len(detections)} barcodes in {image_path}")
            return detections
        except Exception as e:
            logger.error(f"Error detecting barcodes: {e}")
            return []
    
    def analyze_image(self, image_path: str) -> VisionAnalysisResult:
        """Полный анализ изображения"""
        try:
            # Получаем размер изображения
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not read image: {image_path}")
                return None
            
            height, width = image.shape[:2]
            
            # Выполняем все анализы параллельно
            texts = self.extract_text(image_path)
            faces = self.detect_faces(image_path)
            barcodes = self.detect_barcodes(image_path)
            
            result = VisionAnalysisResult(
                timestamp=datetime.now().isoformat(),
                image_path=image_path,
                image_size=(width, height),
                texts=texts,
                faces=faces,
                barcodes=barcodes
            )
            
            with self.lock:
                self.analysis_history.append(result)
            
            logger.info(f"Image analysis complete: {len(texts)} texts, {len(faces)} faces, {len(barcodes)} barcodes")
            return result
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return None
    
    def analyze_video(self, video_path: str, frame_interval: int = 30) -> List[VisionAnalysisResult]:
        """Анализировать видео (каждый N-й кадр)"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error(f"Could not open video: {video_path}")
                return []
            
            results = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    # Сохраняем временный файл
                    temp_path = f"/tmp/frame_{frame_count}.jpg"
                    cv2.imwrite(temp_path, frame)
                    
                    # Анализируем
                    result = self.analyze_image(temp_path)
                    if result:
                        results.append(result)
                    
                    # Удаляем временный файл
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Analyzed {len(results)} frames from video")
            return results
        except Exception as e:
            logger.error(f"Error analyzing video: {e}")
            return []
    
    def draw_detections(self, image_path: str, output_path: str) -> bool:
        """Нарисовать детектированные объекты на изображении"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not read image: {image_path}")
                return False
            
            # Получаем анализ
            result = self.analyze_image(image_path)
            if not result:
                return False
            
            # Рисуем текст
            for text_det in result.texts:
                x1, y1, x2, y2 = text_det.bbox
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(image, text_det.text, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Рисуем лица
            for face_det in result.faces:
                x1, y1, x2, y2 = face_det.bbox
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                label = face_det.name if face_det.name else "Unknown"
                cv2.putText(image, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            
            # Рисуем штрих-коды
            for barcode_det in result.barcodes:
                x1, y1, x2, y2 = barcode_det.bbox
                cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(image, barcode_det.data, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Сохраняем результат
            cv2.imwrite(output_path, image)
            logger.info(f"Detections drawn and saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error drawing detections: {e}")
            return False
    
    def save_analysis(self, filepath: str) -> bool:
        """Сохранить историю анализов в JSON"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "analyses": [a.to_dict() for a in self.analysis_history]
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Analysis saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")
            return False
    
    def get_history(self, limit: int = 100) -> List[VisionAnalysisResult]:
        """Получить историю анализов"""
        return list(self.analysis_history)[-limit:] if self.analysis_history else []
    
    def cleanup(self):
        """Очистить ресурсы"""
        logger.info("Vision System cleaned up")


# Экспорт основных классов
__all__ = [
    'RealVisionSystem',
    'OCREngine',
    'TextDetection',
    'FaceDetection',
    'BarcodeDetection',
    'VisionAnalysisResult'
]

