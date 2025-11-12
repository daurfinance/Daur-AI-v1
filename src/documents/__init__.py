#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль работы с чертежами и документами
"""

from .document_manager import (
    DocumentFormat,
    DrawingFormat,
    CADFormat,
    Document,
    Drawing,
    CADModel,
    DocumentProcessor,
    DrawingProcessor,
    CADProcessor,
    DocumentManager,
    get_document_processor,
    get_drawing_processor,
    get_cad_processor,
    get_document_manager
)

__all__ = [
    'DocumentFormat',
    'DrawingFormat',
    'CADFormat',
    'Document',
    'Drawing',
    'CADModel',
    'DocumentProcessor',
    'DrawingProcessor',
    'CADProcessor',
    'DocumentManager',
    'get_document_processor',
    'get_drawing_processor',
    'get_cad_processor',
    'get_document_manager'
]

