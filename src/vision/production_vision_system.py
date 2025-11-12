"""
Production-Grade Vision System for Daur-AI v2.0
Полнофункциональная система компьютерного зрения с реальным OCR
"""

import cv2
import numpy as np
import pytesseract
import easyocr
from PIL import Image
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import threading
import time
import json

# Попытка импорта face_recognition
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logging.warning("face_recognition library not available")

# Попытка импорта pyzbar для штрих-кодов
try:
    from pyzbar import pyzbar
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    logging.warning("pyzbar library not available")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Результат OCR"""
    text: str
    confidence: float
    bounding_boxes: List[Tuple[int, int, int, int]]
    language: str
    processing_time: float
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return asdict(self)


@dataclass
class FaceDetection:
    """Результат детектирования лица"""
    face_id: int
    location: Tuple[int, int, int, int]  # top, right, bottom, left
    confidence: float
    encoding: Optional[np.ndarray] = None
    name: Optional[str] = None
    
    def to_dict(self):
        return {
            'face_id': self.face_id,
            'location': self.location,
            'confidence': self.confidence,
            'name': self.name
        }


@dataclass
class BarcodeDetection:
    """Результат детектирования штрих-кода"""
    type: str
    data: str
    location: Tuple[int, int, int, int]
    confidence: float
    
    def to_dict(self):
        return asdict(self)


class ProductionOCREngine:
    """Полнофункциональный OCR движок"""
    
    def __init__(self, languages: List[str] = None):
        self.languages = languages or ['en', 'ru']
        self.reader = None
        self.tesseract_available = self._check_tesseract()
        self.initialize_easyocr()
    
    def _check_tesseract(self) -> bool:
        """Проверить доступность Tesseract"""
        try:
            pytesseract.get_tesseract_version()
            logger.info("Tesseract OCR is available")
            return True
        except Exception as e:
            logger.warning(f"Tesseract OCR not available: {e}")
            return False
    
    def initialize_easyocr(self):
        """Инициализировать EasyOCR"""
        try:
            self.reader = easyocr.Reader(self.languages, gpu=self._check_gpu())
            logger.info(f"EasyOCR initialized with languages: {self.languages}")
        except Exception as e:
            logger.error(f"Error initializing EasyOCR: {e}")
            self.reader = None
    
    def _check_gpu(self) -> bool:
        """Проверить доступность GPU"""
        try:
            import torch
            return torch.cuda.is_available()
        except Exception as e:
            return False
    
    def extract_text_from_image(self, image_path: str) -> Optional[OCRResult]:
        """Извлечь текст из изображения"""
        try:
            start_time = time.time()
            
            # Читаем изображение
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not read image: {image_path}")
                return None
            
            # Пытаемся использовать EasyOCR
            if self.reader:
                results = self.reader.readtext(image)
                
                text_parts = []
                bounding_boxes = []
                confidence_scores = []
                
                for (bbox, text, conf) in results:
                    text_parts.append(text)
                    confidence_scores.append(conf)
                    
                    # Преобразуем координаты
                    pts = np.array(bbox, dtype=np.int32)
                    x_min, y_min = pts.min(axis=0)
                    x_max, y_max = pts.max(axis=0)
                    bounding_boxes.append((x_min, y_min, x_max, y_max))
                
                full_text = ' '.join(text_parts)
                avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
                
                processing_time = time.time() - start_time
                
                result = OCRResult(
                    text=full_text,
                    confidence=float(avg_confidence),
                    bounding_boxes=bounding_boxes,
                    language=','.join(self.languages),
                    processing_time=processing_time
                )
                
                logger.info(f"OCR completed in {processing_time:.2f}s, confidence: {avg_confidence:.2f}")
                return result
            
            # Fallback на Tesseract
            elif self.tesseract_available:
                text = pytesseract.image_to_string(image)
                
                processing_time = time.time() - start_time
                
                result = OCRResult(
                    text=text,
                    confidence=0.8,  # Tesseract не дает confidence
                    bounding_boxes=[],
                    language='tesseract',
                    processing_time=processing_time
                )
                
                logger.info(f"Tesseract OCR completed in {processing_time:.2f}s")
                return result
            
            else:
                logger.error("No OCR engine available")
                return None
        
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return None
    
    def extract_text_from_video(self, video_path: str, frame_interval: int = 30) -> List[OCRResult]:
        """Извлечь текст из видео"""
        try:
            results = []
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Could not open video: {video_path}")
                return results
            
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Обрабатываем каждый N-й кадр
                if frame_count % frame_interval == 0:
                    if self.reader:
                        ocr_results = self.reader.readtext(frame)
                        
                        text_parts = []
                        for (bbox, text, conf) in ocr_results:
                            text_parts.append(text)
                        
                        full_text = ' '.join(text_parts)
                        
                        if full_text.strip():
                            result = OCRResult(
                                text=full_text,
                                confidence=0.8,
                                bounding_boxes=[],
                                language=','.join(self.languages),
                                processing_time=0
                            )
                            results.append(result)
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted text from {len(results)} frames")
            return results
        
        except Exception as e:
            logger.error(f"Error extracting text from video: {e}")
            return []


class ProductionFaceRecognition:
    """Полнофункциональное распознавание лиц"""
    
    def __init__(self):
        self.known_faces = {}
        self.known_encodings = []
        self.face_counter = 0
        self.available = FACE_RECOGNITION_AVAILABLE
        
        if not self.available:
            logger.warning("Face recognition not available")
    
    def detect_faces(self, image_path: str) -> List[FaceDetection]:
        """Детектировать лица на изображении"""
        if not self.available:
            logger.warning("Face recognition not available")
            return []
        
        try:
            image = face_recognition.load_image_file(image_path)
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            detections = []
            
            for face_location, face_encoding in zip(face_locations, face_encodings):
                # Распознаем лицо
                matches = face_recognition.compare_faces(
                    self.known_encodings,
                    face_encoding,
                    tolerance=0.6
                )
                
                name = "Unknown"
                confidence = 0.0
                
                face_distances = face_recognition.face_distance(
                    self.known_encodings,
                    face_encoding
                )
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = list(self.known_faces.keys())[best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                
                detection = FaceDetection(
                    face_id=self.face_counter,
                    location=face_location,
                    confidence=float(confidence),
                    encoding=face_encoding,
                    name=name
                )
                
                detections.append(detection)
                self.face_counter += 1
            
            logger.info(f"Detected {len(detections)} faces")
            return detections
        
        except Exception as e:
            logger.error(f"Error detecting faces: {e}")
            return []
    
    def add_known_face(self, name: str, image_path: str) -> bool:
        """Добавить известное лицо"""
        if not self.available:
            return False
        
        try:
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                self.known_faces[name] = image_path
                self.known_encodings.append(face_encodings[0])
                logger.info(f"Added known face: {name}")
                return True
            else:
                logger.warning(f"No face found in image: {image_path}")
                return False
        
        except Exception as e:
            logger.error(f"Error adding known face: {e}")
            return False
    
    def recognize_faces(self, image_path: str) -> List[FaceDetection]:
        """Распознать лица на изображении"""
        return self.detect_faces(image_path)


class ProductionBarcodeRecognition:
    """Полнофункциональное распознавание штрих-кодов"""
    
    def __init__(self):
        self.available = PYZBAR_AVAILABLE
        
        if not self.available:
            logger.warning("Barcode recognition not available (pyzbar not installed)")
    
    def detect_barcodes(self, image_path: str) -> List[BarcodeDetection]:
        """Детектировать штрих-коды на изображении"""
        if not self.available:
            logger.warning("Barcode recognition not available")
            return []
        
        try:
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Could not read image: {image_path}")
                return []
            
            barcodes = pyzbar.decode(image)
            detections = []
            
            for barcode in barcodes:
                detection = BarcodeDetection(
                    type=barcode.type,
                    data=barcode.data.decode('utf-8'),
                    location=tuple(barcode.rect),
                    confidence=0.95
                )
                detections.append(detection)
                logger.info(f"Detected barcode: {barcode.type} - {barcode.data.decode('utf-8')}")
            
            return detections
        
        except Exception as e:
            logger.error(f"Error detecting barcodes: {e}")
            return []
    
    def detect_qr_codes(self, image_path: str) -> List[BarcodeDetection]:
        """Детектировать QR коды"""
        detections = self.detect_barcodes(image_path)
        return [d for d in detections if d.type == 'QRCODE']


class ProductionVisionSystem:
    """Полнофункциональная система компьютерного зрения"""
    
    def __init__(self):
        self.ocr_engine = ProductionOCREngine()
        self.face_recognition = ProductionFaceRecognition()
        self.barcode_recognition = ProductionBarcodeRecognition()
        self.history = []
    
    def analyze_image(self, image_path: str) -> Dict:
        """Полный анализ изображения"""
        try:
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'image_path': image_path,
                'ocr': None,
                'faces': [],
                'barcodes': []
            }
            
            # OCR
            ocr_result = self.ocr_engine.extract_text_from_image(image_path)
            if ocr_result:
                analysis['ocr'] = ocr_result.to_dict()
            
            # Лица
            faces = self.face_recognition.detect_faces(image_path)
            analysis['faces'] = [f.to_dict() for f in faces]
            
            # Штрих-коды
            barcodes = self.barcode_recognition.detect_barcodes(image_path)
            analysis['barcodes'] = [b.to_dict() for b in barcodes]
            
            self.history.append(analysis)
            logger.info("Image analysis completed")
            return analysis
        
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {}
    
    def get_history(self) -> List[Dict]:
        """Получить историю анализов"""
        return self.history
    
    def export_history(self, filepath: str) -> bool:
        """Экспортировать историю в JSON"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.info(f"History exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error exporting history: {e}")
            return False


# Экспорт основных классов
__all__ = [
    'ProductionOCREngine',
    'ProductionFaceRecognition',
    'ProductionBarcodeRecognition',
    'ProductionVisionSystem',
    'OCRResult',
    'FaceDetection',
    'BarcodeDetection'
]

