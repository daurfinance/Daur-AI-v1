"""
Real Vision Analytics System
Полнофункциональная система анализа видения с реальной интеграцией
"""

import logging
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import os

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("pytesseract not available. Install with: pip install pytesseract")

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logging.warning("face_recognition not available. Install with: pip install face_recognition")

try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except ImportError:
    PYZBAR_AVAILABLE = False
    logging.warning("pyzbar not available. Install with: pip install pyzbar")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """Типы анализа"""
    OCR = "ocr"
    FACE_DETECTION = "face_detection"
    FACE_RECOGNITION = "face_recognition"
    BARCODE = "barcode"
    QR_CODE = "qr_code"
    OBJECT_DETECTION = "object_detection"
    EDGE_DETECTION = "edge_detection"
    COLOR_DETECTION = "color_detection"


@dataclass
class OCRResult:
    """Результат OCR"""
    text: str
    confidence: float
    bounding_boxes: List[Tuple[int, int, int, int]]
    languages: List[str]


@dataclass
class Face:
    """Обнаруженное лицо"""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    encoding: Optional[np.ndarray] = None
    name: Optional[str] = None


@dataclass
class Barcode:
    """Обнаруженный штрих-код"""
    data: str
    barcode_type: str
    x: int
    y: int
    width: int
    height: int
    confidence: float


class RealVisionAnalytics:
    """Реальная система анализа видения"""
    
    def __init__(self):
        """Инициализация системы видения"""
        self.logger = logging.getLogger(__name__)
        
        # Проверяем доступность модулей
        if not TESSERACT_AVAILABLE:
            self.logger.warning("OCR functionality will be limited without pytesseract")
        
        if not FACE_RECOGNITION_AVAILABLE:
            self.logger.warning("Face recognition will be limited without face_recognition")
        
        if not PYZBAR_AVAILABLE:
            self.logger.warning("Barcode detection will be limited without pyzbar")
        
        # Инициализируем каскад для обнаружения лиц
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Хранилище известных лиц
        self.known_faces = {}
        self.known_encodings = []
        self.known_names = []
        
        self.logger.info("Vision Analytics System initialized")
    
    # ===== OCR OPERATIONS =====
    
    def perform_ocr(self, image_path: str, languages: List[str] = None) -> Optional[OCRResult]:
        """
        Распознать текст на изображении
        
        Args:
            image_path: Путь к изображению
            languages: Языки для распознавания (например: ['rus', 'eng'])
        
        Returns:
            Optional[OCRResult]: Результат OCR или None
        """
        try:
            if not TESSERACT_AVAILABLE:
                self.logger.error("Tesseract not available")
                return None
            
            # Читаем изображение
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return None
            
            # Предварительная обработка
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            
            # Распознаём текст
            languages = languages or ['eng']
            lang_str = '+'.join(languages)
            
            text = pytesseract.image_to_string(gray, lang=lang_str)
            data = pytesseract.image_to_data(gray, lang=lang_str, output_type=pytesseract.Output.DICT)
            
            # Получаем bounding boxes
            bounding_boxes = []
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 0:
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    bounding_boxes.append((x, y, w, h))
            
            # Вычисляем среднюю уверенность
            confidences = [int(c) / 100.0 for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            self.logger.info(f"OCR completed: {len(text)} characters recognized")
            
            return OCRResult(
                text=text,
                confidence=avg_confidence,
                bounding_boxes=bounding_boxes,
                languages=languages
            )
        
        except Exception as e:
            self.logger.error(f"Error performing OCR: {e}")
            return None
    
    # ===== FACE DETECTION =====
    
    def detect_faces(self, image_path: str) -> List[Face]:
        """
        Обнаружить лица на изображении
        
        Args:
            image_path: Путь к изображению
        
        Returns:
            List[Face]: Список обнаруженных лиц
        """
        try:
            # Читаем изображение
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return []
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Обнаруживаем лица
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            result = []
            for (x, y, w, h) in faces:
                face = Face(
                    x=int(x),
                    y=int(y),
                    width=int(w),
                    height=int(h),
                    confidence=0.95
                )
                
                # Получаем кодирование лица если доступно
                if FACE_RECOGNITION_AVAILABLE:
                    face_roi = image[y:y+h, x:x+w]
                    try:
                        encodings = face_recognition.face_encodings(face_roi)
                        if encodings:
                            face.encoding = encodings[0]
                    except Exception as e:
                        self.logger.warning(f"Error encoding face: {e}")
                
                result.append(face)
            
            self.logger.info(f"Detected {len(result)} faces")
            return result
        
        except Exception as e:
            self.logger.error(f"Error detecting faces: {e}")
            return []
    
    def recognize_faces(self, image_path: str) -> List[Face]:
        """
        Распознать лица на изображении
        
        Args:
            image_path: Путь к изображению
        
        Returns:
            List[Face]: Список распознанных лиц
        """
        try:
            if not FACE_RECOGNITION_AVAILABLE:
                self.logger.error("face_recognition not available")
                return []
            
            # Читаем изображение
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return []
            
            # Преобразуем в RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Обнаруживаем лица
            face_locations = face_recognition.face_locations(rgb_image)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            result = []
            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                # Сравниваем с известными лицами
                matches = face_recognition.compare_faces(
                    self.known_encodings,
                    encoding,
                    tolerance=0.6
                )
                name = "Unknown"
                confidence = 0.0
                
                # Вычисляем расстояния
                face_distances = face_recognition.face_distance(
                    self.known_encodings,
                    encoding
                )
                
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_names[best_match_index]
                        confidence = 1 - face_distances[best_match_index]
                
                face = Face(
                    x=left,
                    y=top,
                    width=right - left,
                    height=bottom - top,
                    confidence=confidence,
                    encoding=encoding,
                    name=name
                )
                result.append(face)
            
            self.logger.info(f"Recognized {len(result)} faces")
            return result
        
        except Exception as e:
            self.logger.error(f"Error recognizing faces: {e}")
            return []
    
    def add_known_face(self, name: str, image_path: str) -> bool:
        """
        Добавить известное лицо
        
        Args:
            name: Имя человека
            image_path: Путь к изображению
        
        Returns:
            bool: Успешность добавления
        """
        try:
            if not FACE_RECOGNITION_AVAILABLE:
                self.logger.error("face_recognition not available")
                return False
            
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return False
            
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb_image)
            
            if not encodings:
                self.logger.warning(f"No faces found in image: {image_path}")
                return False
            
            self.known_names.append(name)
            self.known_encodings.append(encodings[0])
            self.known_faces[name] = image_path
            
            self.logger.info(f"Added known face: {name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error adding known face: {e}")
            return False
    
    # ===== BARCODE DETECTION =====
    
    def detect_barcodes(self, image_path: str) -> List[Barcode]:
        """
        Обнаружить штрих-коды и QR коды
        
        Args:
            image_path: Путь к изображению
        
        Returns:
            List[Barcode]: Список обнаруженных кодов
        """
        try:
            if not PYZBAR_AVAILABLE:
                self.logger.error("pyzbar not available")
                return []
            
            # Читаем изображение
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return []
            
            # Декодируем коды
            decoded_objects = decode(image)
            
            result = []
            for obj in decoded_objects:
                barcode = Barcode(
                    data=obj.data.decode('utf-8'),
                    barcode_type=obj.type,
                    x=obj.rect.left,
                    y=obj.rect.top,
                    width=obj.rect.width,
                    height=obj.rect.height,
                    confidence=0.95
                )
                result.append(barcode)
            
            self.logger.info(f"Detected {len(result)} barcodes")
            return result
        
        except Exception as e:
            self.logger.error(f"Error detecting barcodes: {e}")
            return []
    
    # ===== EDGE DETECTION =====
    
    def detect_edges(self, image_path: str, threshold1: int = 100, 
                     threshold2: int = 200) -> Optional[np.ndarray]:
        """
        Обнаружить края на изображении
        
        Args:
            image_path: Путь к изображению
            threshold1: Первый порог
            threshold2: Второй порог
        
        Returns:
            Optional[np.ndarray]: Изображение с обнаруженными краями
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return None
            
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, threshold1, threshold2)
            
            self.logger.info("Edge detection completed")
            return edges
        
        except Exception as e:
            self.logger.error(f"Error detecting edges: {e}")
            return None
    
    # ===== COLOR DETECTION =====
    
    def detect_color(self, image_path: str, color_range: Tuple[Tuple[int, int, int], 
                     Tuple[int, int, int]]) -> Optional[np.ndarray]:
        """
        Обнаружить цвет на изображении
        
        Args:
            image_path: Путь к изображению
            color_range: Диапазон цвета (lower_hsv, upper_hsv)
        
        Returns:
            Optional[np.ndarray]: Маска обнаруженного цвета
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return None
            
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            lower = np.array(color_range[0], dtype=np.uint8)
            upper = np.array(color_range[1], dtype=np.uint8)
            
            mask = cv2.inRange(hsv, lower, upper)
            
            self.logger.info("Color detection completed")
            return mask
        
        except Exception as e:
            self.logger.error(f"Error detecting color: {e}")
            return None
    
    # ===== UTILITY METHODS =====
    
    def save_image(self, image: np.ndarray, output_path: str) -> bool:
        """
        Сохранить изображение
        
        Args:
            image: Изображение
            output_path: Путь для сохранения
        
        Returns:
            bool: Успешность сохранения
        """
        try:
            cv2.imwrite(output_path, image)
            self.logger.info(f"Image saved: {output_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving image: {e}")
            return False
    
    def resize_image(self, image_path: str, width: int, height: int) -> Optional[np.ndarray]:
        """
        Изменить размер изображения
        
        Args:
            image_path: Путь к изображению
            width: Новая ширина
            height: Новая высота
        
        Returns:
            Optional[np.ndarray]: Изменённое изображение
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return None
            
            resized = cv2.resize(image, (width, height))
            self.logger.info(f"Image resized to {width}x{height}")
            return resized
        
        except Exception as e:
            self.logger.error(f"Error resizing image: {e}")
            return None
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Получить информацию об изображении
        
        Args:
            image_path: Путь к изображению
        
        Returns:
            Dict[str, Any]: Информация об изображении
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return {}
            
            height, width, channels = image.shape
            
            return {
                'width': width,
                'height': height,
                'channels': channels,
                'file_size': os.path.getsize(image_path),
                'format': os.path.splitext(image_path)[1]
            }
        
        except Exception as e:
            self.logger.error(f"Error getting image info: {e}")
            return {}
    
    def draw_faces(self, image_path: str, faces: List[Face], 
                   output_path: str) -> bool:
        """
        Нарисовать прямоугольники вокруг лиц
        
        Args:
            image_path: Путь к исходному изображению
            faces: Список лиц
            output_path: Путь для сохранения
        
        Returns:
            bool: Успешность операции
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return False
            
            for face in faces:
                cv2.rectangle(image, (face.x, face.y), 
                            (face.x + face.width, face.y + face.height),
                            (0, 255, 0), 2)
                
                if face.name:
                    cv2.putText(image, face.name, (face.x, face.y - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            return self.save_image(image, output_path)
        
        except Exception as e:
            self.logger.error(f"Error drawing faces: {e}")
            return False
    
    def draw_barcodes(self, image_path: str, barcodes: List[Barcode], 
                      output_path: str) -> bool:
        """
        Нарисовать прямоугольники вокруг кодов
        
        Args:
            image_path: Путь к исходному изображению
            barcodes: Список кодов
            output_path: Путь для сохранения
        
        Returns:
            bool: Успешность операции
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to read image: {image_path}")
                return False
            
            for barcode in barcodes:
                cv2.rectangle(image, (barcode.x, barcode.y),
                            (barcode.x + barcode.width, barcode.y + barcode.height),
                            (0, 255, 0), 2)
                
                cv2.putText(image, barcode.data, (barcode.x, barcode.y - 10),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            return self.save_image(image, output_path)
        
        except Exception as e:
            self.logger.error(f"Error drawing barcodes: {e}")
            return False

