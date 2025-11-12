#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Daur-AI: Модуль генерации фото и видео
Включает создание, редактирование и обработку медиа файлов

Версия: 2.0
Дата: 25.10.2025
Автор: Manus AI
"""

import logging
import os
import subprocess
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import json


class ImageFormat(Enum):
    """Форматы изображений"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    BMP = "bmp"
    GIF = "gif"


class VideoCodec(Enum):
    """Видео кодеки"""
    H264 = "h264"
    H265 = "hevc"
    VP9 = "vp9"
    AV1 = "av1"


class AudioCodec(Enum):
    """Аудио кодеки"""
    AAC = "aac"
    MP3 = "mp3"
    OPUS = "opus"
    FLAC = "flac"


@dataclass
class ImageSettings:
    """Настройки изображения"""
    width: int = 1920
    height: int = 1080
    quality: int = 95
    format: ImageFormat = ImageFormat.PNG
    background_color: Tuple[int, int, int] = (255, 255, 255)


@dataclass
class VideoSettings:
    """Настройки видео"""
    width: int = 1920
    height: int = 1080
    fps: int = 30
    bitrate: str = "5000k"
    duration: float = 10.0
    video_codec: VideoCodec = VideoCodec.H264
    audio_codec: AudioCodec = AudioCodec.AAC
    sample_rate: int = 48000


class ImageProcessor:
    """Обработчик изображений"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.image_processor')
    
    def create_image(self, settings: ImageSettings) -> Image.Image:
        """
        Создать новое изображение
        
        Args:
            settings: Настройки изображения
            
        Returns:
            Image: Объект изображения
        """
        img = Image.new(
            'RGB',
            (settings.width, settings.height),
            settings.background_color
        )
        self.logger.info(f"Создано изображение {settings.width}x{settings.height}")
        return img
    
    def add_text(self, image: Image.Image, text: str, position: Tuple[int, int],
                 font_size: int = 40, color: Tuple[int, int, int] = (0, 0, 0),
                 font_path: Optional[str] = None) -> Image.Image:
        """
        Добавить текст на изображение
        
        Args:
            image: Изображение
            text: Текст
            position: Позиция (x, y)
            font_size: Размер шрифта
            color: Цвет текста
            font_path: Путь к файлу шрифта
            
        Returns:
            Image: Обработанное изображение
        """
        draw = ImageDraw.Draw(image)
        
        try:
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = ImageFont.load_default()
        except Exception as e:
            font = ImageFont.load_default()
        
        draw.text(position, text, fill=color, font=font)
        self.logger.info(f"Текст добавлен: {text}")
        return image
    
    def resize(self, image: Image.Image, width: int, height: int) -> Image.Image:
        """
        Изменить размер изображения
        
        Args:
            image: Изображение
            width: Новая ширина
            height: Новая высота
            
        Returns:
            Image: Измененное изображение
        """
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        self.logger.info(f"Изображение изменено на {width}x{height}")
        return resized
    
    def crop(self, image: Image.Image, box: Tuple[int, int, int, int]) -> Image.Image:
        """
        Обрезать изображение
        
        Args:
            image: Изображение
            box: Координаты обрезки (left, top, right, bottom)
            
        Returns:
            Image: Обрезанное изображение
        """
        cropped = image.crop(box)
        self.logger.info(f"Изображение обрезано")
        return cropped
    
    def rotate(self, image: Image.Image, angle: float) -> Image.Image:
        """
        Повернуть изображение
        
        Args:
            image: Изображение
            angle: Угол поворота в градусах
            
        Returns:
            Image: Повернутое изображение
        """
        rotated = image.rotate(angle, expand=True)
        self.logger.info(f"Изображение повернуто на {angle} градусов")
        return rotated
    
    def apply_filter(self, image: Image.Image, filter_type: str) -> Image.Image:
        """
        Применить фильтр
        
        Args:
            image: Изображение
            filter_type: Тип фильтра (blur, sharpen, smooth, etc.)
            
        Returns:
            Image: Обработанное изображение
        """
        if filter_type == 'blur':
            filtered = image.filter(ImageFilter.GaussianBlur(radius=2))
        elif filter_type == 'sharpen':
            filtered = image.filter(ImageFilter.SHARPEN)
        elif filter_type == 'smooth':
            filtered = image.filter(ImageFilter.SMOOTH)
        elif filter_type == 'edge':
            filtered = image.filter(ImageFilter.FIND_EDGES)
        else:
            filtered = image
        
        self.logger.info(f"Фильтр '{filter_type}' применен")
        return filtered
    
    def adjust_brightness(self, image: Image.Image, factor: float) -> Image.Image:
        """
        Отрегулировать яркость
        
        Args:
            image: Изображение
            factor: Коэффициент (1.0 = оригинал, <1.0 = темнее, >1.0 = светлее)
            
        Returns:
            Image: Обработанное изображение
        """
        enhancer = ImageEnhance.Brightness(image)
        adjusted = enhancer.enhance(factor)
        self.logger.info(f"Яркость отрегулирована на {factor}")
        return adjusted
    
    def adjust_contrast(self, image: Image.Image, factor: float) -> Image.Image:
        """
        Отрегулировать контраст
        
        Args:
            image: Изображение
            factor: Коэффициент
            
        Returns:
            Image: Обработанное изображение
        """
        enhancer = ImageEnhance.Contrast(image)
        adjusted = enhancer.enhance(factor)
        self.logger.info(f"Контраст отрегулирован на {factor}")
        return adjusted
    
    def save(self, image: Image.Image, filepath: str, quality: int = 95):
        """
        Сохранить изображение
        
        Args:
            image: Изображение
            filepath: Путь к файлу
            quality: Качество (для JPEG)
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        if filepath.lower().endswith('.jpg') or filepath.lower().endswith('.jpeg'):
            image.save(filepath, 'JPEG', quality=quality)
        elif filepath.lower().endswith('.png'):
            image.save(filepath, 'PNG')
        elif filepath.lower().endswith('.webp'):
            image.save(filepath, 'WEBP', quality=quality)
        else:
            image.save(filepath)
        
        self.logger.info(f"Изображение сохранено: {filepath}")


class VideoProcessor:
    """Обработчик видео"""
    
    def __init__(self):
        """Инициализация"""
        self.logger = logging.getLogger('daur_ai.video_processor')
        self.ffmpeg_available = self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> bool:
        """Проверить наличие FFmpeg"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except Exception as e:
            self.logger.warning(f"FFmpeg не найден. Некоторые функции недоступны.: {e}")
            return False
    
    def create_video_from_images(self, image_paths: List[str], output_path: str,
                                fps: int = 30, duration_per_image: float = 1.0) -> bool:
        """
        Создать видео из изображений
        
        Args:
            image_paths: Список путей к изображениям
            output_path: Путь к выходному видео
            fps: Кадры в секунду
            duration_per_image: Длительность каждого изображения в секундах
            
        Returns:
            bool: Успешность операции
        """
        if not self.ffmpeg_available:
            self.logger.error("FFmpeg не доступен")
            return False
        
        try:
            # Создаем список файлов
            list_file = '/tmp/images.txt'
            with open(list_file, 'w') as f:
                for img_path in image_paths:
                    f.write(f"file '{img_path}'\n")
                    f.write(f"duration {duration_per_image}\n")
            
            # Запускаем FFmpeg
            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-r', str(fps),
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            self.logger.info(f"Видео создано: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка создания видео: {e}")
            return False
    
    def extract_frames(self, video_path: str, output_dir: str, fps: int = 1) -> bool:
        """
        Извлечь кадры из видео
        
        Args:
            video_path: Путь к видео
            output_dir: Директория для сохранения кадров
            fps: Кадры в секунду для извлечения
            
        Returns:
            bool: Успешность операции
        """
        if not self.ffmpeg_available:
            self.logger.error("FFmpeg не доступен")
            return False
        
        try:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', f'fps={fps}',
                f'{output_dir}/frame_%04d.png'
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            self.logger.info(f"Кадры извлечены в {output_dir}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка извлечения кадров: {e}")
            return False
    
    def add_audio(self, video_path: str, audio_path: str, output_path: str) -> bool:
        """
        Добавить аудио к видео
        
        Args:
            video_path: Путь к видео
            audio_path: Путь к аудио
            output_path: Путь к выходному видео
            
        Returns:
            bool: Успешность операции
        """
        if not self.ffmpeg_available:
            self.logger.error("FFmpeg не доступен")
            return False
        
        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            self.logger.info(f"Аудио добавлено: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка добавления аудио: {e}")
            return False
    
    def convert_format(self, input_path: str, output_path: str,
                      codec: VideoCodec = VideoCodec.H264) -> bool:
        """
        Конвертировать видео в другой формат
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            codec: Видео кодек
            
        Returns:
            bool: Успешность операции
        """
        if not self.ffmpeg_available:
            self.logger.error("FFmpeg не доступен")
            return False
        
        try:
            codec_map = {
                VideoCodec.H264: 'libx264',
                VideoCodec.H265: 'libx265',
                VideoCodec.VP9: 'libvpx-vp9',
                VideoCodec.AV1: 'libaom-av1'
            }
            
            cmd = [
                'ffmpeg', '-y',
                '-i', input_path,
                '-c:v', codec_map.get(codec, 'libx264'),
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            subprocess.run(cmd, capture_output=True, check=True)
            self.logger.info(f"Видео конвертировано: {output_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"Ошибка конвертирования: {e}")
            return False


class MediaManager:
    """Менеджер медиа файлов"""
    
    def __init__(self):
        """Инициализация"""
        self.image_processor = ImageProcessor()
        self.video_processor = VideoProcessor()
        self.logger = logging.getLogger('daur_ai.media_manager')
    
    def create_thumbnail(self, image_path: str, output_path: str,
                        width: int = 300, height: int = 300) -> bool:
        """
        Создать миниатюру изображения
        
        Args:
            image_path: Путь к изображению
            output_path: Путь к миниатюре
            width: Ширина миниатюры
            height: Высота миниатюры
            
        Returns:
            bool: Успешность операции
        """
        try:
            img = Image.open(image_path)
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            self.image_processor.save(img, output_path)
            return True
        except Exception as e:
            self.logger.error(f"Ошибка создания миниатюры: {e}")
            return False
    
    def batch_process_images(self, input_dir: str, output_dir: str,
                            operation: str = 'resize', **kwargs) -> int:
        """
        Пакетная обработка изображений
        
        Args:
            input_dir: Директория с исходными изображениями
            output_dir: Директория для сохранения обработанных
            operation: Операция (resize, rotate, filter, etc.)
            **kwargs: Параметры операции
            
        Returns:
            int: Количество обработанных файлов
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        processed = 0
        for img_file in Path(input_dir).glob('*'):
            if img_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']:
                try:
                    img = Image.open(img_file)
                    
                    if operation == 'resize':
                        img = self.image_processor.resize(img, kwargs.get('width', 1920),
                                                        kwargs.get('height', 1080))
                    elif operation == 'rotate':
                        img = self.image_processor.rotate(img, kwargs.get('angle', 90))
                    elif operation == 'filter':
                        img = self.image_processor.apply_filter(img, kwargs.get('filter_type', 'blur'))
                    
                    output_path = os.path.join(output_dir, img_file.name)
                    self.image_processor.save(img, output_path)
                    processed += 1
                
                except Exception as e:
                    self.logger.error(f"Ошибка обработки {img_file}: {e}")
        
        self.logger.info(f"Обработано {processed} изображений")
        return processed


# Глобальные экземпляры
_image_processor = None
_video_processor = None
_media_manager = None


def get_image_processor() -> ImageProcessor:
    """Получить обработчик изображений"""
    global _image_processor
    if _image_processor is None:
        _image_processor = ImageProcessor()
    return _image_processor


def get_video_processor() -> VideoProcessor:
    """Получить обработчик видео"""
    global _video_processor
    if _video_processor is None:
        _video_processor = VideoProcessor()
    return _video_processor


def get_media_manager() -> MediaManager:
    """Получить менеджер медиа"""
    global _media_manager
    if _media_manager is None:
        _media_manager = MediaManager()
    return _media_manager

