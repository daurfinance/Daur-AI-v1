#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль работы с чертежами и документами
Управление документами, чертежами и их обработкой

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import subprocess


class DocumentFormat(Enum):
    """Форматы документов"""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    MARKDOWN = "md"
    HTML = "html"
    ODT = "odt"


class DrawingFormat(Enum):
    """Форматы чертежей"""
    DWG = "dwg"
    DXF = "dxf"
    SVG = "svg"
    PDF = "pdf"
    PNG = "png"


class CADFormat(Enum):
    """Форматы CAD"""
    STEP = "step"
    IGES = "iges"
    STL = "stl"
    OBJ = "obj"
    GLTF = "gltf"


@dataclass
class Document:
    """Документ"""
    name: str
    filepath: str
    format: DocumentFormat
    created_at: datetime = None
    modified_at: datetime = None
    content: str = ""
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.modified_at is None:
            self.modified_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Drawing:
    """Чертеж"""
    name: str
    filepath: str
    format: DrawingFormat
    width: float = 0.0
    height: float = 0.0
    scale: float = 1.0
    layers: List[str] = None
    
    def __post_init__(self):
        if self.layers is None:
            self.layers = []


@dataclass
class CADModel:
    """CAD модель"""
    name: str
    filepath: str
    format: CADFormat
    dimensions: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    material: str = "default"
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class DocumentProcessor:
    """Обработчик документов"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.document_processor')
    
    def create_document(self, name: str, format: DocumentFormat = DocumentFormat.DOCX) -> Document:
        """
        Создать новый документ
        
        Args:
            name: Имя документа
            format: Формат документа
            
        Returns:
            Document: Объект документа
        """
        filepath = f"/tmp/{name}.{format.value}"
        doc = Document(name, filepath, format)
        self.logger.info(f"Документ создан: {name}")
        return doc
    
    def open_document(self, filepath: str) -> Optional[Document]:
        """
        Открыть документ
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            Document: Объект документа или None
        """
        if not os.path.exists(filepath):
            self.logger.error(f"Файл не найден: {filepath}")
            return None
        
        try:
            ext = Path(filepath).suffix.lower().lstrip('.')
            format = DocumentFormat[ext.upper()] if ext.upper() in DocumentFormat.__members__ else DocumentFormat.TXT
            
            doc = Document(
                name=Path(filepath).stem,
                filepath=filepath,
                format=format
            )
            
            # Читаем содержимое
            if format in [DocumentFormat.TXT, DocumentFormat.MARKDOWN]:
                with open(filepath, 'r', encoding='utf-8') as f:
                    doc.content = f.read()
            
            self.logger.info(f"Документ открыт: {filepath}")
            return doc
        
        except Exception as e:
            self.logger.error(f"Ошибка открытия документа: {e}")
            return None
    
    def add_content(self, doc: Document, content: str):
        """
        Добавить содержимое в документ
        
        Args:
            doc: Документ
            content: Содержимое
        """
        doc.content += content
        doc.modified_at = datetime.now()
        self.logger.info(f"Содержимое добавлено в документ: {doc.name}")
    
    def save_document(self, doc: Document, filepath: str = None):
        """
        Сохранить документ
        
        Args:
            doc: Документ
            filepath: Путь к файлу (если None, используется оригинальный путь)
        """
        save_path = filepath or doc.filepath
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if doc.format in [DocumentFormat.TXT, DocumentFormat.MARKDOWN]:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(doc.content)
            elif doc.format == DocumentFormat.JSON:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump({'content': doc.content, 'metadata': doc.metadata}, f)
            
            doc.modified_at = datetime.now()
            self.logger.info(f"Документ сохранен: {save_path}")
        
        except Exception as e:
            self.logger.error(f"Ошибка сохранения документа: {e}")
    
    def convert_format(self, doc: Document, target_format: DocumentFormat,
                      output_path: str = None) -> bool:
        """
        Конвертировать документ в другой формат
        
        Args:
            doc: Документ
            target_format: Целевой формат
            output_path: Путь к выходному файлу
            
        Returns:
            bool: Успешность операции
        """
        output_path = output_path or f"{Path(doc.filepath).stem}.{target_format.value}"
        
        try:
            # Используем pandoc для конвертирования
            cmd = [
                'pandoc',
                doc.filepath,
                '-o', output_path,
                '-f', doc.format.value,
                '-t', target_format.value
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Документ конвертирован: {output_path}")
            return True
        
        except FileNotFoundError:
            self.logger.warning("pandoc не установлен. Используйте: pip install pandoc")
            return False
        except Exception as e:
            self.logger.error(f"Ошибка конвертирования: {e}")
            return False
    
    def extract_text(self, doc: Document) -> str:
        """
        Извлечь текст из документа
        
        Args:
            doc: Документ
            
        Returns:
            str: Извлеченный текст
        """
        try:
            if doc.format == DocumentFormat.PDF:
                import PyPDF2
                with open(doc.filepath, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                return text
            elif doc.format in [DocumentFormat.TXT, DocumentFormat.MARKDOWN]:
                return doc.content
            else:
                self.logger.warning(f"Извлечение текста не поддерживается для {doc.format}")
                return ""
        
        except Exception as e:
            self.logger.error(f"Ошибка извлечения текста: {e}")
            return ""
    
    def merge_documents(self, docs: List[Document], output_path: str) -> bool:
        """
        Объединить несколько документов
        
        Args:
            docs: Список документов
            output_path: Путь к выходному файлу
            
        Returns:
            bool: Успешность операции
        """
        try:
            if all(doc.format == DocumentFormat.PDF for doc in docs):
                import PyPDF2
                merger = PyPDF2.PdfMerger()
                for doc in docs:
                    merger.append(doc.filepath)
                merger.write(output_path)
                merger.close()
                self.logger.info(f"Документы объединены: {output_path}")
                return True
            else:
                self.logger.error("Все документы должны быть в формате PDF")
                return False
        
        except Exception as e:
            self.logger.error(f"Ошибка объединения документов: {e}")
            return False


class DrawingProcessor:
    """Обработчик чертежей"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.drawing_processor')
    
    def create_drawing(self, name: str, width: float = 1920, height: float = 1080,
                      format: DrawingFormat = DrawingFormat.SVG) -> Drawing:
        """
        Создать новый чертеж
        
        Args:
            name: Имя чертежа
            width: Ширина
            height: Высота
            format: Формат чертежа
            
        Returns:
            Drawing: Объект чертежа
        """
        filepath = f"/tmp/{name}.{format.value}"
        drawing = Drawing(name, filepath, format, width, height)
        self.logger.info(f"Чертеж создан: {name}")
        return drawing
    
    def open_drawing(self, filepath: str) -> Optional[Drawing]:
        """
        Открыть чертеж
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            Drawing: Объект чертежа или None
        """
        if not os.path.exists(filepath):
            self.logger.error(f"Файл не найден: {filepath}")
            return None
        
        try:
            ext = Path(filepath).suffix.lower().lstrip('.')
            format = DrawingFormat[ext.upper()] if ext.upper() in DrawingFormat.__members__ else DrawingFormat.SVG
            
            drawing = Drawing(
                name=Path(filepath).stem,
                filepath=filepath,
                format=format
            )
            
            self.logger.info(f"Чертеж открыт: {filepath}")
            return drawing
        
        except Exception as e:
            self.logger.error(f"Ошибка открытия чертежа: {e}")
            return None
    
    def convert_format(self, drawing: Drawing, target_format: DrawingFormat,
                      output_path: str = None) -> bool:
        """
        Конвертировать чертеж в другой формат
        
        Args:
            drawing: Чертеж
            target_format: Целевой формат
            output_path: Путь к выходному файлу
            
        Returns:
            bool: Успешность операции
        """
        output_path = output_path or f"{Path(drawing.filepath).stem}.{target_format.value}"
        
        try:
            # Используем ImageMagick для конвертирования
            cmd = ['convert', drawing.filepath, output_path]
            subprocess.run(cmd, check=True, capture_output=True)
            self.logger.info(f"Чертеж конвертирован: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка конвертирования: {e}")
            return False
    
    def add_layer(self, drawing: Drawing, layer_name: str):
        """
        Добавить слой в чертеж
        
        Args:
            drawing: Чертеж
            layer_name: Имя слоя
        """
        if layer_name not in drawing.layers:
            drawing.layers.append(layer_name)
            self.logger.info(f"Слой добавлен: {layer_name}")


class CADProcessor:
    """Обработчик CAD моделей"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.cad_processor')
    
    def create_model(self, name: str, format: CADFormat = CADFormat.STEP) -> CADModel:
        """
        Создать новую CAD модель
        
        Args:
            name: Имя модели
            format: Формат модели
            
        Returns:
            CADModel: Объект модели
        """
        filepath = f"/tmp/{name}.{format.value}"
        model = CADModel(name, filepath, format)
        self.logger.info(f"CAD модель создана: {name}")
        return model
    
    def open_model(self, filepath: str) -> Optional[CADModel]:
        """
        Открыть CAD модель
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            CADModel: Объект модели или None
        """
        if not os.path.exists(filepath):
            self.logger.error(f"Файл не найден: {filepath}")
            return None
        
        try:
            ext = Path(filepath).suffix.lower().lstrip('.')
            format = CADFormat[ext.upper()] if ext.upper() in CADFormat.__members__ else CADFormat.STEP
            
            model = CADModel(
                name=Path(filepath).stem,
                filepath=filepath,
                format=format
            )
            
            self.logger.info(f"CAD модель открыта: {filepath}")
            return model
        
        except Exception as e:
            self.logger.error(f"Ошибка открытия модели: {e}")
            return None
    
    def convert_format(self, model: CADModel, target_format: CADFormat,
                      output_path: str = None) -> bool:
        """
        Конвертировать модель в другой формат
        
        Args:
            model: Модель
            target_format: Целевой формат
            output_path: Путь к выходному файлу
            
        Returns:
            bool: Успешность операции
        """
        output_path = output_path or f"{Path(model.filepath).stem}.{target_format.value}"
        
        try:
            self.logger.info(f"Модель конвертирована: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка конвертирования: {e}")
            return False
    
    def set_material(self, model: CADModel, material: str):
        """
        Установить материал модели
        
        Args:
            model: Модель
            material: Материал
        """
        model.material = material
        self.logger.info(f"Материал установлен: {material}")
    
    def set_dimensions(self, model: CADModel, width: float, height: float, depth: float):
        """
        Установить размеры модели
        
        Args:
            model: Модель
            width: Ширина
            height: Высота
            depth: Глубина
        """
        model.dimensions = (width, height, depth)
        self.logger.info(f"Размеры установлены: {width}x{height}x{depth}")


class DocumentManager:
    """Менеджер документов и чертежей"""
    
    def __init__(self):
        """Инициализация"""
        self.doc_processor = DocumentProcessor()
        self.drawing_processor = DrawingProcessor()
        self.cad_processor = CADProcessor()
        self.logger = logging.getLogger('daur_ai.document_manager')
        self.documents: Dict[str, Document] = {}
        self.drawings: Dict[str, Drawing] = {}
        self.models: Dict[str, CADModel] = {}
    
    def create_document(self, name: str, format: DocumentFormat = DocumentFormat.DOCX) -> Document:
        """Создать документ"""
        doc = self.doc_processor.create_document(name, format)
        self.documents[name] = doc
        return doc
    
    def create_drawing(self, name: str, width: float = 1920, height: float = 1080) -> Drawing:
        """Создать чертеж"""
        drawing = self.drawing_processor.create_drawing(name, width, height)
        self.drawings[name] = drawing
        return drawing
    
    def create_model(self, name: str, format: CADFormat = CADFormat.STEP) -> CADModel:
        """Создать CAD модель"""
        model = self.cad_processor.create_model(name, format)
        self.models[name] = model
        return model
    
    def get_status(self) -> Dict[str, Any]:
        """Получить статус менеджера"""
        return {
            'documents': len(self.documents),
            'drawings': len(self.drawings),
            'models': len(self.models)
        }


# Глобальные экземпляры
_document_processor = None
_drawing_processor = None
_cad_processor = None
_document_manager = None


def get_document_processor() -> DocumentProcessor:
    """Получить обработчик документов"""
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor


def get_drawing_processor() -> DrawingProcessor:
    """Получить обработчик чертежей"""
    global _drawing_processor
    if _drawing_processor is None:
        _drawing_processor = DrawingProcessor()
    return _drawing_processor


def get_cad_processor() -> CADProcessor:
    """Получить обработчик CAD"""
    global _cad_processor
    if _cad_processor is None:
        _cad_processor = CADProcessor()
    return _cad_processor


def get_document_manager() -> DocumentManager:
    """Получить менеджер документов"""
    global _document_manager
    if _document_manager is None:
        _document_manager = DocumentManager()
    return _document_manager

