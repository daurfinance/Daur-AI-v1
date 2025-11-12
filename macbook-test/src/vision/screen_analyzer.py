"""
Анализатор экрана с компьютерным зрением
Захватывает и анализирует содержимое экрана
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw
import logging
from typing import List, Dict, Tuple, Optional
import time
import os

# Настройка headless режима для sandbox
os.environ.setdefault('DISPLAY', ':99')

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    GUI_AVAILABLE = True
except Exception as e:
    logging.warning(f"GUI недоступен: {e}")
    GUI_AVAILABLE = False
    # Создаем заглушку для pyautogui
    class MockPyAutoGUI:
        @staticmethod
        def screenshot(region=None):
            # Возвращаем пустое изображение
            return Image.new('RGB', (800, 600), color='black')
        
        @staticmethod
        def size():
            class Size:
                width = 1920
                height = 1080
            return Size()
    
    pyautogui = MockPyAutoGUI()

class ScreenAnalyzer:
    """Анализатор экрана с возможностями компьютерного зрения"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Настройки pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # Кэш для скриншотов
        self.screenshot_cache = {}
        self.cache_timeout = 1.0  # секунды
        
        # Создаем директорию для сохранения скриншотов
        self.screenshots_dir = "/home/ubuntu/Daur-AI-v1/screenshots"
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
    def capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        Захватывает скриншот экрана
        
        Args:
            region: Область захвата (x, y, width, height)
            
        Returns:
            numpy array с изображением
        """
        try:
            if region:
                screenshot = pyautogui.screenshot(region=region)
            else:
                screenshot = pyautogui.screenshot()
                
            # Конвертируем в numpy array
            img_array = np.array(screenshot)
            
            # Конвертируем RGB в BGR для OpenCV
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            
            return img_bgr
            
        except Exception as e:
            self.logger.error(f"Ошибка захвата экрана: {e}")
            return np.array([])
    
    def save_screenshot(self, filename: str = None, region: Optional[Tuple[int, int, int, int]] = None) -> str:
        """
        Сохраняет скриншот в файл
        
        Args:
            filename: Имя файла (если None, генерируется автоматически)
            region: Область захвата
            
        Returns:
            Путь к сохраненному файлу
        """
        try:
            if filename is None:
                timestamp = int(time.time())
                filename = f"screenshot_{timestamp}.png"
                
            filepath = os.path.join(self.screenshots_dir, filename)
            
            img = self.capture_screen(region)
            if img.size > 0:
                cv2.imwrite(filepath, img)
                self.logger.info(f"Скриншот сохранен: {filepath}")
                return filepath
            else:
                raise Exception("Не удалось захватить изображение")
                
        except Exception as e:
            self.logger.error(f"Ошибка сохранения скриншота: {e}")
            return ""
    
    def find_template(self, template_path: str, threshold: float = 0.8, region: Optional[Tuple[int, int, int, int]] = None) -> List[Dict]:
        """
        Поиск шаблона на экране
        
        Args:
            template_path: Путь к изображению шаблона
            threshold: Порог совпадения (0.0 - 1.0)
            region: Область поиска
            
        Returns:
            Список найденных совпадений с координатами и уверенностью
        """
        try:
            # Захватываем экран
            screen = self.capture_screen(region)
            if screen.size == 0:
                return []
                
            # Загружаем шаблон
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                self.logger.error(f"Не удалось загрузить шаблон: {template_path}")
                return []
            
            # Выполняем поиск шаблона
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            
            # Находим все совпадения выше порога
            locations = np.where(result >= threshold)
            matches = []
            
            h, w = template.shape[:2]
            
            for pt in zip(*locations[::-1]):
                confidence = result[pt[1], pt[0]]
                matches.append({
                    'x': int(pt[0]),
                    'y': int(pt[1]),
                    'width': w,
                    'height': h,
                    'confidence': float(confidence),
                    'center_x': int(pt[0] + w/2),
                    'center_y': int(pt[1] + h/2)
                })
            
            # Сортируем по уверенности
            matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска шаблона: {e}")
            return []
    
    def detect_edges(self, image: np.ndarray = None, low_threshold: int = 50, high_threshold: int = 150) -> np.ndarray:
        """
        Обнаружение краев на изображении
        
        Args:
            image: Изображение (если None, захватывается экран)
            low_threshold: Нижний порог для Canny
            high_threshold: Верхний порог для Canny
            
        Returns:
            Изображение с выделенными краями
        """
        try:
            if image is None:
                image = self.capture_screen()
                
            if image.size == 0:
                return np.array([])
            
            # Конвертируем в градации серого
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Применяем размытие для уменьшения шума
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Обнаруживаем края
            edges = cv2.Canny(blurred, low_threshold, high_threshold)
            
            return edges
            
        except Exception as e:
            self.logger.error(f"Ошибка обнаружения краев: {e}")
            return np.array([])
    
    def find_contours(self, image: np.ndarray = None, min_area: int = 100) -> List[Dict]:
        """
        Поиск контуров на изображении
        
        Args:
            image: Изображение (если None, захватывается экран)
            min_area: Минимальная площадь контура
            
        Returns:
            Список контуров с их свойствами
        """
        try:
            if image is None:
                image = self.capture_screen()
                
            if image.size == 0:
                return []
            
            # Получаем края
            edges = self.detect_edges(image)
            
            # Находим контуры
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            results = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area >= min_area:
                    # Получаем ограничивающий прямоугольник
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Вычисляем дополнительные свойства
                    perimeter = cv2.arcLength(contour, True)
                    
                    results.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'area': float(area),
                        'perimeter': float(perimeter),
                        'center_x': int(x + w/2),
                        'center_y': int(y + h/2),
                        'aspect_ratio': float(w/h) if h > 0 else 0
                    })
            
            # Сортируем по площади
            results.sort(key=lambda x: x['area'], reverse=True)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска контуров: {e}")
            return []
    
    def analyze_colors(self, region: Optional[Tuple[int, int, int, int]] = None) -> Dict:
        """
        Анализ цветов на экране
        
        Args:
            region: Область анализа
            
        Returns:
            Статистика цветов
        """
        try:
            image = self.capture_screen(region)
            if image.size == 0:
                return {}
            
            # Конвертируем в RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Вычисляем средние значения каналов
            mean_colors = np.mean(image_rgb, axis=(0, 1))
            
            # Находим доминирующие цвета
            pixels = image_rgb.reshape(-1, 3)
            unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
            
            # Топ-5 цветов
            top_indices = np.argsort(counts)[-5:][::-1]
            dominant_colors = []
            
            for idx in top_indices:
                color = unique_colors[idx]
                count = counts[idx]
                percentage = (count / len(pixels)) * 100
                
                dominant_colors.append({
                    'color': [int(c) for c in color],
                    'count': int(count),
                    'percentage': float(percentage)
                })
            
            return {
                'mean_rgb': [float(c) for c in mean_colors],
                'dominant_colors': dominant_colors,
                'total_pixels': len(pixels),
                'unique_colors': len(unique_colors)
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка анализа цветов: {e}")
            return {}
    
    def get_screen_info(self) -> Dict:
        """
        Получает информацию о экране
        
        Returns:
            Информация о разрешении и размерах экрана
        """
        try:
            size = pyautogui.size()
            
            return {
                'width': size.width,
                'height': size.height,
                'aspect_ratio': size.width / size.height,
                'total_pixels': size.width * size.height
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка получения информации о экране: {e}")
            return {}
    
    def create_annotated_screenshot(self, elements: List[Dict], filename: str = None) -> str:
        """
        Создает аннотированный скриншот с выделенными элементами
        
        Args:
            elements: Список элементов для выделения
            filename: Имя файла для сохранения
            
        Returns:
            Путь к сохраненному файлу
        """
        try:
            # Захватываем экран
            screen = self.capture_screen()
            if screen.size == 0:
                return ""
            
            # Конвертируем в PIL Image для рисования
            screen_rgb = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(screen_rgb)
            draw = ImageDraw.Draw(pil_image)
            
            # Рисуем элементы
            for i, element in enumerate(elements):
                x = element.get('x', 0)
                y = element.get('y', 0)
                w = element.get('width', 0)
                h = element.get('height', 0)
                
                # Рисуем прямоугольник
                draw.rectangle([x, y, x+w, y+h], outline='red', width=2)
                
                # Добавляем номер
                draw.text((x, y-15), str(i+1), fill='red')
            
            # Сохраняем
            if filename is None:
                timestamp = int(time.time())
                filename = f"annotated_screenshot_{timestamp}.png"
                
            filepath = os.path.join(self.screenshots_dir, filename)
            pil_image.save(filepath)
            
            self.logger.info(f"Аннотированный скриншот сохранен: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Ошибка создания аннотированного скриншота: {e}")
            return ""
