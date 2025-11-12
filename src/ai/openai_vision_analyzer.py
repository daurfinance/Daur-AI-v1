#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: OpenAI Vision Analyzer
Анализ скриншотов и изображений с помощью OpenAI Vision API

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import base64
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


@dataclass
class ImageAnalysis:
    """Результаты анализа изображения"""
    image_path: str
    description: str
    objects: List[str] = field(default_factory=list)
    text_content: str = ""
    colors: List[str] = field(default_factory=list)
    scene_type: str = ""
    confidence: float = 0.0
    analysis_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class OpenAIVisionAnalyzer:
    """Анализатор изображений с помощью OpenAI Vision API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация
        
        Args:
            api_key: OpenAI API ключ (если None, используется переменная окружения)
        """
        self.logger = logging.getLogger('daur_ai.openai_vision_analyzer')
        
        if not OpenAI:
            self.logger.warning("OpenAI library not installed")
            self.client = None
            return
        
        try:
            # Использовать переданный ключ или переменную окружения
            if api_key:
                self.client = OpenAI(api_key=api_key)
            else:
                self.client = OpenAI()
            
            self.logger.info("OpenAI Vision Analyzer инициализирован")
        
        except Exception as e:
            self.logger.error(f"Ошибка инициализации OpenAI: {e}")
            self.client = None
        
        self.analysis_history: List[ImageAnalysis] = []
    
    # ==================== ОСНОВНОЙ АНАЛИЗ ====================
    
    def analyze_image(self, image_path: str, detailed: bool = True) -> Optional[ImageAnalysis]:
        """
        Анализировать изображение
        
        Args:
            image_path: Путь к изображению
            detailed: Детальный анализ
            
        Returns:
            Optional[ImageAnalysis]: Результаты анализа
        """
        if not self.client:
            self.logger.warning("OpenAI client not available")
            return None
        
        try:
            # Проверить существование файла
            if not os.path.exists(image_path):
                self.logger.error(f"Файл не найден: {image_path}")
                return None
            
            # Кодировать изображение в base64
            with open(image_path, 'rb') as image_file:
                image_data = base64.standard_b64encode(image_file.read()).decode('utf-8')
            
            # Определить тип изображения
            image_ext = os.path.splitext(image_path)[1].lower()
            media_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            media_type = media_type_map.get(image_ext, 'image/jpeg')
            
            # Создать промпт
            if detailed:
                prompt = """Проанализируй это изображение и предоставь подробный анализ:
1. Описание: Что ты видишь на изображении?
2. Объекты: Какие объекты присутствуют?
3. Текст: Какой текст видно на изображении?
4. Цвета: Какие основные цвета?
5. Тип сцены: Что это за сцена (офис, улица, дом и т.д.)?
6. Действия: Какие действия происходят?
7. Качество: Оцени качество изображения.

Ответь в формате JSON с ключами: description, objects, text, colors, scene_type, actions, quality"""
            else:
                prompt = "Кратко опиши что ты видишь на этом изображении в 1-2 предложениях"
            
            # Отправить запрос к OpenAI
            import time
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                max_tokens=1024
            )
            
            analysis_time = time.time() - start_time
            
            # Парсить ответ
            response_text = response.choices[0].message.content
            
            # Попытаться парсить JSON если это детальный анализ
            analysis_data = {
                'description': response_text,
                'objects': [],
                'text_content': '',
                'colors': [],
                'scene_type': '',
                'confidence': 0.9
            }
            
            if detailed:
                try:
                    import json
                    parsed = json.loads(response_text)
                    analysis_data.update(parsed)
                except (json.JSONDecodeError, ValueError) as e:
                    # Если не JSON, использовать как описание
                    analysis_data['description'] = response_text
            
            # Создать объект анализа
            analysis = ImageAnalysis(
                image_path=image_path,
                description=analysis_data.get('description', response_text),
                objects=analysis_data.get('objects', []),
                text_content=analysis_data.get('text', ''),
                colors=analysis_data.get('colors', []),
                scene_type=analysis_data.get('scene_type', ''),
                confidence=analysis_data.get('confidence', 0.9),
                analysis_time=analysis_time
            )
            
            self.analysis_history.append(analysis)
            
            self.logger.info(f"Анализ завершен: {image_path} ({analysis_time:.2f}s)")
            return analysis
        
        except Exception as e:
            self.logger.error(f"Ошибка анализа изображения: {e}")
            return None
    
    # ==================== СПЕЦИАЛИЗИРОВАННЫЙ АНАЛИЗ ====================
    
    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """
        Извлечь текст из изображения (OCR)
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            Optional[str]: Извлеченный текст
        """
        if not self.client:
            return None
        
        try:
            with open(image_path, 'rb') as image_file:
                image_data = base64.standard_b64encode(image_file.read()).decode('utf-8')
            
            image_ext = os.path.splitext(image_path)[1].lower()
            media_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            media_type = media_type_map.get(image_ext, 'image/jpeg')
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": "Извлеки весь текст с этого изображения. Верни только текст без комментариев."
                            }
                        ]
                    }
                ],
                max_tokens=2048
            )
            
            text = response.choices[0].message.content
            self.logger.info(f"Текст извлечен из: {image_path}")
            return text
        
        except Exception as e:
            self.logger.error(f"Ошибка извлечения текста: {e}")
            return None
    
    def detect_objects_in_image(self, image_path: str) -> Optional[List[Dict[str, Any]]]:
        """
        Детектировать объекты на изображении
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            Optional[List]: Список объектов с описаниями
        """
        if not self.client:
            return None
        
        try:
            with open(image_path, 'rb') as image_file:
                image_data = base64.standard_b64encode(image_file.read()).decode('utf-8')
            
            image_ext = os.path.splitext(image_path)[1].lower()
            media_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            media_type = media_type_map.get(image_ext, 'image/jpeg')
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": """Определи все объекты на этом изображении. 
Для каждого объекта предоставь:
- name: название объекта
- description: описание
- confidence: уверенность (0-1)
- location: примерное расположение (top, left, bottom, right в процентах)

Верни результат в формате JSON массива объектов."""
                            }
                        ]
                    }
                ],
                max_tokens=2048
            )
            
            response_text = response.choices[0].message.content
            
            try:
                import json
                objects = json.loads(response_text)
                self.logger.info(f"Объекты детектированы: {image_path}")
                return objects
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.warning(f"Не удалось парсить JSON ответ для объектов")
                return None
        
        except Exception as e:
            self.logger.error(f"Ошибка детектирования объектов: {e}")
            return None
    
    def analyze_screenshot_for_action(self, image_path: str, task: str) -> Optional[Dict[str, Any]]:
        """
        Анализировать скриншот для выполнения действия
        
        Args:
            image_path: Путь к скриншоту
            task: Описание задачи
            
        Returns:
            Optional[Dict]: Рекомендуемые действия
        """
        if not self.client:
            return None
        
        try:
            with open(image_path, 'rb') as image_file:
                image_data = base64.standard_b64encode(image_file.read()).decode('utf-8')
            
            image_ext = os.path.splitext(image_path)[1].lower()
            media_type_map = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            media_type = media_type_map.get(image_ext, 'image/jpeg')
            
            prompt = f"""Посмотри на этот скриншот и помоги выполнить задачу: {task}

Проанализируй:
1. Что видно на экране?
2. Какие элементы интерфейса доступны?
3. Какие действия нужно выполнить для выполнения задачи?
4. Где нужно кликнуть (координаты в процентах от размера экрана)?
5. Какой текст нужно ввести?

Верни результат в формате JSON с ключами:
- screen_analysis: анализ экрана
- required_actions: список требуемых действий
- click_locations: координаты для кликов (x, y в процентах)
- text_input: текст для ввода если требуется
- confidence: уверенность решения (0-1)"""
            
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                max_tokens=2048
            )
            
            response_text = response.choices[0].message.content
            
            try:
                import json
                actions = json.loads(response_text)
                self.logger.info(f"Анализ действий завершен: {image_path}")
                return actions
            except (json.JSONDecodeError, ValueError) as e:
                self.logger.warning(f"Не удалось парсить JSON ответ для действий")
                return {'analysis': response_text}
        
        except Exception as e:
            self.logger.error(f"Ошибка анализа действий: {e}")
            return None
    
    # ==================== ИСТОРИЯ ====================
    
    def get_analysis_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Получить историю анализов"""
        return [
            {
                'image_path': a.image_path,
                'description': a.description[:100],
                'objects_count': len(a.objects),
                'analysis_time': a.analysis_time,
                'timestamp': a.timestamp.isoformat()
            }
            for a in self.analysis_history[-limit:]
        ]
    
    def clear_history(self):
        """Очистить историю"""
        self.analysis_history.clear()
        self.logger.info("История анализов очищена")


# Глобальный экземпляр
_openai_vision_analyzer = None


def get_openai_vision_analyzer() -> OpenAIVisionAnalyzer:
    """Получить анализатор OpenAI Vision"""
    global _openai_vision_analyzer
    if _openai_vision_analyzer is None:
        _openai_vision_analyzer = OpenAIVisionAnalyzer()
    return _openai_vision_analyzer

