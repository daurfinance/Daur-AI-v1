#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль распознавания QR и штрих-кодов
Детектирование и декодирование QR кодов и штрих-кодов

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
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
    import pyzbar.pyzbar as pyzbar
except ImportError:
    pyzbar = None

try:
    from pyzbar.pyzbar import ZBarSymbol
except ImportError:
    ZBarSymbol = None


class BarcodeType(Enum):
    """Типы штрих-кодов"""
    QR_CODE = "QR_CODE"
    CODE_128 = "CODE_128"
    CODE_39 = "CODE_39"
    EAN_13 = "EAN_13"
    EAN_8 = "EAN_8"
    UPCA = "UPCA"
    UPCE = "UPCE"
    PDF417 = "PDF417"
    DATAMATRIX = "DATAMATRIX"
    UNKNOWN = "UNKNOWN"


@dataclass
class BarcodeData:
    """Данные штрих-кода"""
    barcode_type: BarcodeType
    data: str
    location: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float = 1.0
    quality: str = "good"  # good, fair, poor
    timestamp: datetime = field(default_factory=datetime.now)


class BarcodeRecognitionModule:
    """Модуль распознавания штрих-кодов и QR кодов"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.barcode_recognition')
        self.barcode_history: List[BarcodeData] = []
        self.logger.info("Barcode Recognition Module инициализирован")
    
    # ==================== РАСПОЗНАВАНИЕ ШТРИХ-КОДОВ ====================
    
    def detect_barcodes_in_image(self, image_path: str) -> List[BarcodeData]:
        """
        Детектировать штрих-коды на изображении
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            List[BarcodeData]: Список найденных штрих-кодов
        """
        if not pyzbar or not cv2:
            self.logger.warning("pyzbar или cv2 не установлены")
            return []
        
        try:
            # Загрузить изображение
            image = cv2.imread(image_path)
            
            if image is None:
                self.logger.error(f"Не удалось загрузить изображение: {image_path}")
                return []
            
            # Преобразовать в серый
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Найти штрих-коды
            barcodes = pyzbar.decode(gray)
            
            results = []
            
            for barcode in barcodes:
                # Получить данные
                barcode_data = barcode.data.decode('utf-8')
                barcode_type = self._parse_barcode_type(barcode.type)
                
                # Получить координаты
                (x, y, w, h) = barcode.rect
                
                barcode_obj = BarcodeData(
                    barcode_type=barcode_type,
                    data=barcode_data,
                    location=(x, y, w, h),
                    confidence=0.95
                )
                
                results.append(barcode_obj)
            
            self.barcode_history.extend(results)
            
            self.logger.info(f"Найдено {len(results)} штрих-кодов на изображении: {image_path}")
            return results
        
        except Exception as e:
            self.logger.error(f"Ошибка детектирования штрих-кодов: {e}")
            return []
    
    def detect_barcodes_in_video(self, video_path: str, frame_skip: int = 5) -> List[BarcodeData]:
        """
        Детектировать штрих-коды в видео
        
        Args:
            video_path: Путь к видео
            frame_skip: Пропускать каждый N-й кадр
            
        Returns:
            List[BarcodeData]: Список найденных штрих-кодов
        """
        if not pyzbar or not cv2:
            self.logger.warning("pyzbar или cv2 не установлены")
            return []
        
        try:
            cap = cv2.VideoCapture(video_path)
            barcodes = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                frame_count += 1
                
                # Пропустить кадры
                if frame_count % frame_skip != 0:
                    continue
                
                # Преобразовать в серый
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Найти штрих-коды
                detected = pyzbar.decode(gray)
                
                for barcode in detected:
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = self._parse_barcode_type(barcode.type)
                    
                    (x, y, w, h) = barcode.rect
                    
                    barcode_obj = BarcodeData(
                        barcode_type=barcode_type,
                        data=barcode_data,
                        location=(x, y, w, h),
                        confidence=0.95
                    )
                    
                    barcodes.append(barcode_obj)
            
            cap.release()
            
            self.barcode_history.extend(barcodes)
            
            self.logger.info(f"Найдено {len(barcodes)} штрих-кодов в видео: {video_path}")
            return barcodes
        
        except Exception as e:
            self.logger.error(f"Ошибка детектирования штрих-кодов в видео: {e}")
            return []
    
    def _parse_barcode_type(self, barcode_type_str: str) -> BarcodeType:
        """Парсить тип штрих-кода"""
        type_map = {
            'QRCODE': BarcodeType.QR_CODE,
            'CODE128': BarcodeType.CODE_128,
            'CODE39': BarcodeType.CODE_39,
            'EAN13': BarcodeType.EAN_13,
            'EAN8': BarcodeType.EAN_8,
            'UPCA': BarcodeType.UPCA,
            'UPCE': BarcodeType.UPCE,
            'PDF417': BarcodeType.PDF417,
            'DATAMATRIX': BarcodeType.DATAMATRIX
        }
        
        return type_map.get(barcode_type_str, BarcodeType.UNKNOWN)
    
    # ==================== АНАЛИЗ ШТРИХ-КОДОВ ====================
    
    def draw_barcode_boxes(self, image_path: str, output_path: str,
                          barcodes: Optional[List[BarcodeData]] = None) -> bool:
        """
        Нарисовать прямоугольники вокруг штрих-кодов
        
        Args:
            image_path: Путь к исходному изображению
            output_path: Путь для сохранения результата
            barcodes: Список штрих-кодов (если None, будут найдены автоматически)
            
        Returns:
            bool: Успешность операции
        """
        if not cv2:
            self.logger.warning("cv2 не установлен")
            return False
        
        try:
            # Загрузить изображение
            image = cv2.imread(image_path)
            
            # Найти штрих-коды если не переданы
            if barcodes is None:
                barcodes = self.detect_barcodes_in_image(image_path)
            
            # Нарисовать прямоугольники
            for barcode in barcodes:
                x, y, w, h = barcode.location
                
                # Нарисовать прямоугольник
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Добавить текст
                label = f"{barcode.barcode_type.value}: {barcode.data[:20]}"
                cv2.putText(image, label, (x, y - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Сохранить результат
            cv2.imwrite(output_path, image)
            
            self.logger.info(f"Результат сохранен: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка рисования прямоугольников: {e}")
            return False
    
    def validate_qr_code(self, qr_data: str) -> Dict[str, Any]:
        """
        Валидировать QR код
        
        Args:
            qr_data: Данные QR кода
            
        Returns:
            Dict: Результаты валидации
        """
        validation = {
            'is_valid': False,
            'data_type': 'unknown',
            'length': len(qr_data),
            'contains_url': False,
            'contains_email': False,
            'contains_phone': False,
            'contains_wifi': False
        }
        
        # Проверить URL
        if qr_data.startswith('http://') or qr_data.startswith('https://'):
            validation['data_type'] = 'url'
            validation['contains_url'] = True
            validation['is_valid'] = True
        
        # Проверить email
        elif '@' in qr_data and '.' in qr_data:
            validation['data_type'] = 'email'
            validation['contains_email'] = True
            validation['is_valid'] = True
        
        # Проверить WiFi
        elif qr_data.startswith('WIFI:'):
            validation['data_type'] = 'wifi'
            validation['contains_wifi'] = True
            validation['is_valid'] = True
        
        # Проверить телефон
        elif qr_data.startswith('tel:') or qr_data.startswith('+'):
            validation['data_type'] = 'phone'
            validation['contains_phone'] = True
            validation['is_valid'] = True
        
        # Обычный текст
        else:
            validation['data_type'] = 'text'
            validation['is_valid'] = True
        
        return validation
    
    def parse_wifi_qr(self, qr_data: str) -> Optional[Dict[str, str]]:
        """
        Парсить WiFi QR код
        
        Args:
            qr_data: Данные QR кода
            
        Returns:
            Optional[Dict]: Параметры WiFi
        """
        if not qr_data.startswith('WIFI:'):
            return None
        
        try:
            # Парсить формат: WIFI:T:WPA;S:SSID;P:PASSWORD;;
            wifi_params = {}
            
            # Удалить префикс WIFI:
            data = qr_data[5:-2]  # Удалить WIFI: и ;;
            
            # Парсить параметры
            parts = data.split(';')
            for part in parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    
                    if key == 'T':
                        wifi_params['security'] = value
                    elif key == 'S':
                        wifi_params['ssid'] = value
                    elif key == 'P':
                        wifi_params['password'] = value
                    elif key == 'H':
                        wifi_params['hidden'] = value == 'true'
            
            return wifi_params if wifi_params else None
        
        except Exception as e:
            self.logger.error(f"Ошибка парсинга WiFi QR: {e}")
            return None
    
    # ==================== СТАТИСТИКА ====================
    
    def get_barcode_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику по штрих-кодам
        
        Returns:
            Dict: Статистика
        """
        stats = {
            'total_barcodes': len(self.barcode_history),
            'by_type': {},
            'unique_data': len(set(b.data for b in self.barcode_history))
        }
        
        for barcode in self.barcode_history:
            barcode_type = barcode.barcode_type.value
            if barcode_type not in stats['by_type']:
                stats['by_type'][barcode_type] = 0
            stats['by_type'][barcode_type] += 1
        
        return stats
    
    # ==================== ИСТОРИЯ ====================
    
    def get_barcode_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить историю штрих-кодов"""
        return [
            {
                'type': b.barcode_type.value,
                'data': b.data,
                'confidence': b.confidence,
                'timestamp': b.timestamp.isoformat()
            }
            for b in self.barcode_history[-limit:]
        ]
    
    def clear_history(self):
        """Очистить историю"""
        self.barcode_history.clear()
        self.logger.info("История штрих-кодов очищена")


# Глобальный экземпляр
_barcode_recognition_module = None


def get_barcode_recognition_module() -> BarcodeRecognitionModule:
    """Получить модуль распознавания штрих-кодов"""
    global _barcode_recognition_module
    if _barcode_recognition_module is None:
        _barcode_recognition_module = BarcodeRecognitionModule()
    return _barcode_recognition_module

