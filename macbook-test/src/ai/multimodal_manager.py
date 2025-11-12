"""
Мультимодальный AI менеджер
Обработка изображений, видео, аудио и текста
"""

import asyncio
import time
import logging
import base64
import json
import io
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

# Импорт AI компонентов
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from .enhanced_model_manager import EnhancedModelManager
    from .ollama_model import OllamaModel
    from .openai_model import OpenAIModel
except ImportError:
    EnhancedModelManager = None
    OllamaModel = None
    OpenAIModel = None

class MultimodalAIManager:
    """Менеджер мультимодальных AI моделей"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # AI модели
        self.text_model = None
        self.vision_model = None
        self.audio_model = None
        
        # Базовый менеджер
        self.base_manager = EnhancedModelManager() if EnhancedModelManager else None
        
        # Настройки
        self.supported_image_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
        self.supported_video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        self.supported_audio_formats = ['.mp3', '.wav', '.ogg', '.m4a', '.flac']
        
        # Кэш обработанных медиа
        self.media_cache = {}
        self.analysis_cache = {}
        
        # Статистика
        self.stats = {
            'images_processed': 0,
            'videos_processed': 0,
            'audio_processed': 0,
            'text_generated': 0,
            'multimodal_queries': 0
        }
        
        # Инициализация
        self._initialize()
    
    def _initialize(self):
        """Инициализация мультимодального менеджера"""
        try:
            # Инициализация базового менеджера
            if self.base_manager:
                self.text_model = self.base_manager
            
            self.logger.info("Мультимодальный AI менеджер инициализирован")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации: {e}")
    
    def is_available(self) -> bool:
        """Проверяет доступность мультимодальных возможностей"""
        return self.base_manager is not None
    
    async def analyze_image(self, image_data: Union[str, bytes, np.ndarray], 
                          query: str = "Опиши что видишь на изображении") -> Dict:
        """
        Анализирует изображение с помощью AI
        
        Args:
            image_data: Данные изображения (путь, bytes или numpy array)
            query: Запрос для анализа
            
        Returns:
            Результат анализа
        """
        try:
            start_time = time.time()
            
            # Подготовка изображения
            image = self._prepare_image(image_data)
            if image is None:
                return {'success': False, 'error': 'Не удалось подготовить изображение'}
            
            # Создание кэш-ключа
            cache_key = self._create_cache_key('image', image_data, query)
            
            # Проверка кэша
            if cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key]
                cached_result['from_cache'] = True
                return cached_result
            
            # Анализ изображения
            result = await self._analyze_image_with_ai(image, query)
            
            # Дополнительная обработка
            if result['success']:
                # Добавление метаданных
                result.update({
                    'image_size': image.shape[:2] if isinstance(image, np.ndarray) else None,
                    'processing_time': time.time() - start_time,
                    'timestamp': time.time(),
                    'from_cache': False
                })
                
                # Кэширование результата
                self.analysis_cache[cache_key] = result
                
                # Обновление статистики
                self.stats['images_processed'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа изображения: {e}")
            return {'success': False, 'error': str(e)}
    
    async def analyze_video(self, video_path: str, 
                          query: str = "Опиши что происходит в видео",
                          frame_interval: int = 30) -> Dict:
        """
        Анализирует видео с помощью AI
        
        Args:
            video_path: Путь к видео файлу
            query: Запрос для анализа
            frame_interval: Интервал между анализируемыми кадрами
            
        Returns:
            Результат анализа
        """
        try:
            start_time = time.time()
            
            if not os.path.exists(video_path):
                return {'success': False, 'error': 'Видео файл не найден'}
            
            # Создание кэш-ключа
            cache_key = self._create_cache_key('video', video_path, query)
            
            # Проверка кэша
            if cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key]
                cached_result['from_cache'] = True
                return cached_result
            
            # Извлечение кадров
            frames = self._extract_video_frames(video_path, frame_interval)
            if not frames:
                return {'success': False, 'error': 'Не удалось извлечь кадры из видео'}
            
            # Анализ кадров
            frame_analyses = []
            for i, frame in enumerate(frames):
                frame_query = f"{query} (кадр {i+1}/{len(frames)})"
                frame_result = await self._analyze_image_with_ai(frame, frame_query)
                
                if frame_result['success']:
                    frame_analyses.append({
                        'frame_number': i + 1,
                        'timestamp': i * frame_interval / 30.0,  # Предполагаем 30 FPS
                        'analysis': frame_result['analysis']
                    })
            
            # Создание общего анализа
            if frame_analyses:
                summary_query = f"Создай общее описание видео на основе анализа {len(frame_analyses)} кадров: " + \
                              "; ".join([fa['analysis'] for fa in frame_analyses])
                
                summary_result = await self._generate_text_response(summary_query)
                
                result = {
                    'success': True,
                    'video_path': video_path,
                    'total_frames_analyzed': len(frame_analyses),
                    'frame_analyses': frame_analyses,
                    'summary': summary_result.get('response', 'Не удалось создать общий анализ'),
                    'processing_time': time.time() - start_time,
                    'timestamp': time.time(),
                    'from_cache': False
                }
                
                # Кэширование результата
                self.analysis_cache[cache_key] = result
                
                # Обновление статистики
                self.stats['videos_processed'] += 1
                
                return result
            
            else:
                return {'success': False, 'error': 'Не удалось проанализировать ни одного кадра'}
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа видео: {e}")
            return {'success': False, 'error': str(e)}
    
    async def analyze_audio(self, audio_path: str, 
                          query: str = "Опиши что слышно в аудио") -> Dict:
        """
        Анализирует аудио с помощью AI
        
        Args:
            audio_path: Путь к аудио файлу
            query: Запрос для анализа
            
        Returns:
            Результат анализа
        """
        try:
            start_time = time.time()
            
            if not os.path.exists(audio_path):
                return {'success': False, 'error': 'Аудио файл не найден'}
            
            # Создание кэш-ключа
            cache_key = self._create_cache_key('audio', audio_path, query)
            
            # Проверка кэша
            if cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key]
                cached_result['from_cache'] = True
                return cached_result
            
            # Анализ аудио (базовая реализация)
            audio_info = self._get_audio_info(audio_path)
            
            # Создание описания на основе метаданных
            description_query = f"Создай описание аудио файла со следующими характеристиками: {audio_info}. {query}"
            
            analysis_result = await self._generate_text_response(description_query)
            
            if analysis_result['success']:
                result = {
                    'success': True,
                    'audio_path': audio_path,
                    'audio_info': audio_info,
                    'analysis': analysis_result['response'],
                    'processing_time': time.time() - start_time,
                    'timestamp': time.time(),
                    'from_cache': False
                }
                
                # Кэширование результата
                self.analysis_cache[cache_key] = result
                
                # Обновление статистики
                self.stats['audio_processed'] += 1
                
                return result
            
            else:
                return {'success': False, 'error': 'Не удалось проанализировать аудио'}
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа аудио: {e}")
            return {'success': False, 'error': str(e)}
    
    async def multimodal_query(self, query: str, media_files: List[str] = None, 
                             context: str = None) -> Dict:
        """
        Выполняет мультимодальный запрос
        
        Args:
            query: Основной запрос
            media_files: Список медиа файлов для анализа
            context: Дополнительный контекст
            
        Returns:
            Результат мультимодального анализа
        """
        try:
            start_time = time.time()
            
            # Создание кэш-ключа
            cache_key = self._create_cache_key('multimodal', str(media_files), query + str(context))
            
            # Проверка кэша
            if cache_key in self.analysis_cache:
                cached_result = self.analysis_cache[cache_key]
                cached_result['from_cache'] = True
                return cached_result
            
            # Анализ медиа файлов
            media_analyses = []
            
            if media_files:
                for media_file in media_files:
                    if not os.path.exists(media_file):
                        continue
                    
                    file_ext = Path(media_file).suffix.lower()
                    
                    if file_ext in self.supported_image_formats:
                        analysis = await self.analyze_image(media_file, query)
                        if analysis['success']:
                            media_analyses.append({
                                'type': 'image',
                                'file': media_file,
                                'analysis': analysis['analysis']
                            })
                    
                    elif file_ext in self.supported_video_formats:
                        analysis = await self.analyze_video(media_file, query)
                        if analysis['success']:
                            media_analyses.append({
                                'type': 'video',
                                'file': media_file,
                                'analysis': analysis['summary']
                            })
                    
                    elif file_ext in self.supported_audio_formats:
                        analysis = await self.analyze_audio(media_file, query)
                        if analysis['success']:
                            media_analyses.append({
                                'type': 'audio',
                                'file': media_file,
                                'analysis': analysis['analysis']
                            })
            
            # Создание комплексного ответа
            if media_analyses or context:
                combined_query = f"Основной запрос: {query}\n"
                
                if context:
                    combined_query += f"Контекст: {context}\n"
                
                if media_analyses:
                    combined_query += "Анализ медиа файлов:\n"
                    for i, analysis in enumerate(media_analyses, 1):
                        combined_query += f"{i}. {analysis['type'].upper()} ({analysis['file']}): {analysis['analysis']}\n"
                
                combined_query += "\nДай комплексный ответ, учитывая всю предоставленную информацию."
                
                response_result = await self._generate_text_response(combined_query)
                
                if response_result['success']:
                    result = {
                        'success': True,
                        'query': query,
                        'media_files': media_files or [],
                        'media_analyses': media_analyses,
                        'context': context,
                        'response': response_result['response'],
                        'processing_time': time.time() - start_time,
                        'timestamp': time.time(),
                        'from_cache': False
                    }
                    
                    # Кэширование результата
                    self.analysis_cache[cache_key] = result
                    
                    # Обновление статистики
                    self.stats['multimodal_queries'] += 1
                    
                    return result
            
            # Если нет медиа файлов, выполняем обычный текстовый запрос
            text_result = await self._generate_text_response(query)
            
            if text_result['success']:
                result = {
                    'success': True,
                    'query': query,
                    'media_files': [],
                    'media_analyses': [],
                    'context': context,
                    'response': text_result['response'],
                    'processing_time': time.time() - start_time,
                    'timestamp': time.time(),
                    'from_cache': False
                }
                
                return result
            
            return {'success': False, 'error': 'Не удалось обработать запрос'}
            
        except Exception as e:
            self.logger.error(f"Ошибка мультимодального запроса: {e}")
            return {'success': False, 'error': str(e)}
    
    def _prepare_image(self, image_data: Union[str, bytes, np.ndarray]) -> Optional[np.ndarray]:
        """Подготавливает изображение для анализа"""
        try:
            if isinstance(image_data, str):
                # Путь к файлу
                if os.path.exists(image_data):
                    image = cv2.imread(image_data)
                    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if image is not None else None
                else:
                    return None
            
            elif isinstance(image_data, bytes):
                # Байтовые данные
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB) if image is not None else None
            
            elif isinstance(image_data, np.ndarray):
                # Numpy array
                return image_data
            
            else:
                return None
            
        except Exception as e:
            self.logger.error(f"Ошибка подготовки изображения: {e}")
            return None
    
    async def _analyze_image_with_ai(self, image: np.ndarray, query: str) -> Dict:
        """Анализирует изображение с помощью AI модели"""
        try:
            # Базовый анализ изображения
            height, width = image.shape[:2]
            
            # Определение основных цветов
            colors = self._analyze_image_colors(image)
            
            # Определение яркости
            brightness = np.mean(image)
            
            # Создание описания на основе визуальных характеристик
            visual_description = f"Изображение размером {width}x{height} пикселей. "
            visual_description += f"Средняя яркость: {brightness:.1f}. "
            visual_description += f"Основные цвета: {', '.join(colors)}. "
            
            # Генерация ответа с помощью текстовой модели
            analysis_query = f"{query}. Визуальные характеристики: {visual_description}"
            
            response = await self._generate_text_response(analysis_query)
            
            if response['success']:
                return {
                    'success': True,
                    'analysis': response['response'],
                    'visual_characteristics': {
                        'size': {'width': width, 'height': height},
                        'brightness': brightness,
                        'colors': colors
                    }
                }
            else:
                return {'success': False, 'error': 'Не удалось проанализировать изображение'}
            
        except Exception as e:
            self.logger.error(f"Ошибка AI анализа изображения: {e}")
            return {'success': False, 'error': str(e)}
    
    def _analyze_image_colors(self, image: np.ndarray) -> List[str]:
        """Анализирует основные цвета изображения"""
        try:
            # Упрощенный анализ цветов
            mean_color = np.mean(image, axis=(0, 1))
            
            colors = []
            
            # Определение доминирующего цвета
            if mean_color[0] > mean_color[1] and mean_color[0] > mean_color[2]:
                colors.append("красный")
            elif mean_color[1] > mean_color[0] and mean_color[1] > mean_color[2]:
                colors.append("зеленый")
            elif mean_color[2] > mean_color[0] and mean_color[2] > mean_color[1]:
                colors.append("синий")
            
            # Определение яркости
            brightness = np.mean(mean_color)
            if brightness > 200:
                colors.append("светлый")
            elif brightness < 50:
                colors.append("темный")
            
            return colors if colors else ["нейтральный"]
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа цветов: {e}")
            return ["неопределенный"]
    
    def _extract_video_frames(self, video_path: str, frame_interval: int) -> List[np.ndarray]:
        """Извлекает кадры из видео"""
        try:
            cap = cv2.VideoCapture(video_path)
            frames = []
            frame_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
                
                frame_count += 1
                
                # Ограничение количества кадров
                if len(frames) >= 10:
                    break
            
            cap.release()
            return frames
            
        except Exception as e:
            self.logger.error(f"Ошибка извлечения кадров: {e}")
            return []
    
    def _get_audio_info(self, audio_path: str) -> Dict:
        """Получает информацию об аудио файле"""
        try:
            # Базовая информация о файле
            file_size = os.path.getsize(audio_path)
            file_ext = Path(audio_path).suffix.lower()
            
            return {
                'file_size': file_size,
                'format': file_ext,
                'estimated_duration': file_size / 16000,  # Примерная оценка
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения информации об аудио: {e}")
            return {}
    
    async def _generate_text_response(self, query: str) -> Dict:
        """Генерирует текстовый ответ"""
        try:
            if self.base_manager:
                response = await asyncio.to_thread(self.base_manager.generate_response, query)
                
                if response:
                    self.stats['text_generated'] += 1
                    return {'success': True, 'response': response}
            
            # Fallback ответ
            return {
                'success': True, 
                'response': f"Анализ запроса: {query[:100]}... (AI модель недоступна, используется базовый анализ)"
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка генерации текста: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_cache_key(self, media_type: str, data: Any, query: str) -> str:
        """Создает ключ для кэширования"""
        try:
            import hashlib
            
            # Создание хэша из данных
            data_str = str(data) + query
            cache_key = f"{media_type}_{hashlib.md5(data_str.encode()).hexdigest()}"
            
            return cache_key
            
        except Exception as e:
            self.logger.error(f"Ошибка создания кэш-ключа: {e}")
            return f"{media_type}_{time.time()}"
    
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Возвращает поддерживаемые форматы"""
        return {
            'images': self.supported_image_formats,
            'videos': self.supported_video_formats,
            'audio': self.supported_audio_formats
        }
    
    def get_statistics(self) -> Dict:
        """Возвращает статистику работы"""
        return {
            **self.stats,
            'cache_size': len(self.analysis_cache),
            'media_cache_size': len(self.media_cache),
            'base_manager_available': self.base_manager is not None
        }
    
    def clear_cache(self):
        """Очищает кэш"""
        self.media_cache.clear()
        self.analysis_cache.clear()
        self.logger.info("Кэш мультимодального менеджера очищен")
    
    def cleanup(self):
        """Очистка ресурсов"""
        try:
            self.clear_cache()
            
            if self.base_manager:
                # Очистка базового менеджера если есть метод
                if hasattr(self.base_manager, 'cleanup'):
                    self.base_manager.cleanup()
            
            self.logger.info("Ресурсы мультимодального менеджера очищены")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
