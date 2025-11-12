"""
Браузерный контроллер с визуальным распознаванием
Автоматизация браузера с использованием компьютерного зрения
"""

import asyncio
import time
import logging
import base64
import json
import re
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import cv2
import numpy as np

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Импорт OCR компонентов
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from drivers.video_ocr_engine import VideoOCREngine
except ImportError:
    VideoOCREngine = None

class VisualBrowserController:
    """Контроллер браузера с визуальным распознаванием"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Playwright компоненты
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # OCR движок
        self.ocr_engine = VideoOCREngine() if VideoOCREngine else None
        
        # Настройки
        self.viewport_size = {'width': 1280, 'height': 720}
        self.user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
        # Кэш элементов
        self.element_cache = {}
        self.screenshot_cache = {}
        
        # Статистика
        self.stats = {
            'pages_visited': 0,
            'elements_found': 0,
            'ocr_operations': 0,
            'actions_performed': 0
        }
        
        # Инициализация
        self._initialize()
    
    def _initialize(self):
        """Инициализация контроллера"""
        try:
            if not PLAYWRIGHT_AVAILABLE:
                self.logger.error("Playwright недоступен")
                return
            
            self.logger.info("Браузерный контроллер с визуальным распознаванием инициализирован")
            
        except Exception as e:
            self.logger.error(f"Ошибка инициализации: {e}")
    
    async def start_browser(self, headless: bool = True, browser_type: str = 'chromium') -> bool:
        """
        Запускает браузер
        
        Args:
            headless: Запуск в headless режиме
            browser_type: Тип браузера ('chromium', 'firefox', 'webkit')
            
        Returns:
            Успешность запуска
        """
        try:
            if not PLAYWRIGHT_AVAILABLE:
                self.logger.error("Playwright недоступен")
                return False
            
            # Запуск Playwright
            self.playwright = await async_playwright().start()
            
            # Выбор браузера
            if browser_type == 'chromium':
                browser_launcher = self.playwright.chromium
            elif browser_type == 'firefox':
                browser_launcher = self.playwright.firefox
            elif browser_type == 'webkit':
                browser_launcher = self.playwright.webkit
            else:
                self.logger.error(f"Неизвестный тип браузера: {browser_type}")
                return False
            
            # Запуск браузера
            self.browser = await browser_launcher.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            # Создание контекста
            self.context = await self.browser.new_context(
                viewport=self.viewport_size,
                user_agent=self.user_agent,
                ignore_https_errors=True
            )
            
            # Создание страницы
            self.page = await self.context.new_page()
            
            self.logger.info(f"Браузер {browser_type} запущен (headless: {headless})")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка запуска браузера: {e}")
            return False
    
    async def navigate_to(self, url: str, wait_for: str = 'networkidle') -> Dict:
        """
        Переходит на страницу
        
        Args:
            url: URL для перехода
            wait_for: Условие ожидания ('load', 'domcontentloaded', 'networkidle')
            
        Returns:
            Информация о переходе
        """
        try:
            if not self.page:
                return {'success': False, 'error': 'Браузер не запущен'}
            
            start_time = time.time()
            
            # Переход на страницу
            response = await self.page.goto(url, wait_until=wait_for, timeout=30000)
            
            # Ожидание загрузки
            await self.page.wait_for_load_state('networkidle', timeout=10000)
            
            # Получение информации о странице
            title = await self.page.title()
            current_url = self.page.url
            
            # Создание скриншота
            screenshot = await self.page.screenshot(full_page=False)
            
            # Обновление статистики
            self.stats['pages_visited'] += 1
            
            result = {
                'success': True,
                'url': current_url,
                'title': title,
                'status_code': response.status if response else 0,
                'load_time': time.time() - start_time,
                'screenshot_size': len(screenshot)
            }
            
            self.logger.info(f"Переход на {url} выполнен за {result['load_time']:.2f}с")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка перехода на {url}: {e}")
            return {'success': False, 'error': str(e)}
    
    async def take_screenshot(self, full_page: bool = False) -> Optional[bytes]:
        """
        Делает скриншот страницы
        
        Args:
            full_page: Скриншот всей страницы
            
        Returns:
            Данные скриншота
        """
        try:
            if not self.page:
                return None
            
            screenshot = await self.page.screenshot(full_page=full_page)
            
            # Кэширование скриншота
            timestamp = time.time()
            self.screenshot_cache[timestamp] = screenshot
            
            # Очистка старых скриншотов
            if len(self.screenshot_cache) > 10:
                oldest_key = min(self.screenshot_cache.keys())
                del self.screenshot_cache[oldest_key]
            
            return screenshot
            
        except Exception as e:
            self.logger.error(f"Ошибка создания скриншота: {e}")
            return None
    
    async def find_elements_by_text(self, text: str, exact_match: bool = False) -> List[Dict]:
        """
        Находит элементы по тексту с использованием OCR
        
        Args:
            text: Искомый текст
            exact_match: Точное совпадение
            
        Returns:
            Список найденных элементов
        """
        try:
            if not self.page:
                return []
            
            elements = []
            
            # 1. Поиск через DOM
            dom_elements = await self._find_dom_elements_by_text(text, exact_match)
            elements.extend(dom_elements)
            
            # 2. Поиск через OCR
            if self.ocr_engine:
                ocr_elements = await self._find_ocr_elements_by_text(text, exact_match)
                elements.extend(ocr_elements)
            
            # Удаление дубликатов
            unique_elements = self._deduplicate_elements(elements)
            
            self.stats['elements_found'] += len(unique_elements)
            
            return unique_elements
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска элементов по тексту '{text}': {e}")
            return []
    
    async def _find_dom_elements_by_text(self, text: str, exact_match: bool) -> List[Dict]:
        """Поиск элементов через DOM"""
        try:
            elements = []
            
            # XPath для поиска текста
            if exact_match:
                xpath = f"//*[text()='{text}']"
            else:
                xpath = f"//*[contains(text(), '{text}')]"
            
            # Поиск элементов
            dom_elements = await self.page.query_selector_all(f"xpath={xpath}")
            
            for element in dom_elements:
                try:
                    # Получение информации об элементе
                    bounding_box = await element.bounding_box()
                    if not bounding_box:
                        continue
                    
                    tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
                    element_text = await element.text_content()
                    
                    elements.append({
                        'type': 'dom',
                        'element': element,
                        'text': element_text,
                        'tag': tag_name,
                        'bbox': bounding_box,
                        'confidence': 1.0
                    })
                    
                except Exception as e:
                    self.logger.debug(f"Ошибка обработки DOM элемента: {e}")
                    continue
            
            return elements
            
        except Exception as e:
            self.logger.error(f"Ошибка поиска DOM элементов: {e}")
            return []
    
    async def _find_ocr_elements_by_text(self, text: str, exact_match: bool) -> List[Dict]:
        """Поиск элементов через OCR"""
        try:
            if not self.ocr_engine:
                return []
            
            # Получение скриншота
            screenshot_data = await self.take_screenshot()
            if not screenshot_data:
                return []
            
            # Конвертация в OpenCV формат
            nparr = np.frombuffer(screenshot_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return []
            
            # OCR анализ
            ocr_results = self.ocr_engine.extract_text_from_frame(frame)
            self.stats['ocr_operations'] += 1
            
            # Поиск совпадений
            elements = []
            search_text = text.lower() if not exact_match else text
            
            for ocr_result in ocr_results:
                result_text = ocr_result['text']
                
                # Проверка совпадения
                match = False
                if exact_match:
                    match = result_text == text
                else:
                    match = search_text in result_text.lower()
                
                if match:
                    elements.append({
                        'type': 'ocr',
                        'element': None,
                        'text': result_text,
                        'tag': 'text',
                        'bbox': {
                            'x': ocr_result['bbox']['x'],
                            'y': ocr_result['bbox']['y'],
                            'width': ocr_result['bbox']['width'],
                            'height': ocr_result['bbox']['height']
                        },
                        'confidence': ocr_result['confidence']
                    })
            
            return elements
            
        except Exception as e:
            self.logger.error(f"Ошибка OCR поиска: {e}")
            return []
    
    def _deduplicate_elements(self, elements: List[Dict]) -> List[Dict]:
        """Удаляет дубликаты элементов"""
        try:
            unique_elements = []
            seen_positions = set()
            
            for element in elements:
                bbox = element['bbox']
                position = (bbox['x'], bbox['y'], bbox['width'], bbox['height'])
                
                if position not in seen_positions:
                    unique_elements.append(element)
                    seen_positions.add(position)
            
            return unique_elements
            
        except Exception as e:
            self.logger.error(f"Ошибка удаления дубликатов: {e}")
            return elements
    
    async def click_element(self, element_info: Dict) -> Dict:
        """
        Кликает по элементу
        
        Args:
            element_info: Информация об элементе
            
        Returns:
            Результат клика
        """
        try:
            if not self.page:
                return {'success': False, 'error': 'Браузер не запущен'}
            
            if element_info['type'] == 'dom' and element_info['element']:
                # Клик по DOM элементу
                await element_info['element'].click()
                
            else:
                # Клик по координатам (OCR элемент)
                bbox = element_info['bbox']
                x = bbox['x'] + bbox['width'] // 2
                y = bbox['y'] + bbox['height'] // 2
                
                await self.page.mouse.click(x, y)
            
            self.stats['actions_performed'] += 1
            
            # Ожидание после клика
            await self.page.wait_for_timeout(500)
            
            return {'success': True, 'action': 'click', 'element': element_info['text']}
            
        except Exception as e:
            self.logger.error(f"Ошибка клика по элементу: {e}")
            return {'success': False, 'error': str(e)}
    
    async def type_text(self, element_info: Dict, text: str) -> Dict:
        """
        Вводит текст в элемент
        
        Args:
            element_info: Информация об элементе
            text: Текст для ввода
            
        Returns:
            Результат ввода
        """
        try:
            if not self.page:
                return {'success': False, 'error': 'Браузер не запущен'}
            
            if element_info['type'] == 'dom' and element_info['element']:
                # Ввод в DOM элемент
                await element_info['element'].fill(text)
                
            else:
                # Клик по координатам и ввод
                bbox = element_info['bbox']
                x = bbox['x'] + bbox['width'] // 2
                y = bbox['y'] + bbox['height'] // 2
                
                await self.page.mouse.click(x, y)
                await self.page.keyboard.type(text)
            
            self.stats['actions_performed'] += 1
            
            return {'success': True, 'action': 'type', 'text': text}
            
        except Exception as e:
            self.logger.error(f"Ошибка ввода текста: {e}")
            return {'success': False, 'error': str(e)}
    
    async def scroll_page(self, direction: str = 'down', amount: int = 3) -> Dict:
        """
        Прокручивает страницу
        
        Args:
            direction: Направление ('up', 'down', 'left', 'right')
            amount: Количество прокруток
            
        Returns:
            Результат прокрутки
        """
        try:
            if not self.page:
                return {'success': False, 'error': 'Браузер не запущен'}
            
            # Определение направления прокрутки
            scroll_map = {
                'down': (0, 300),
                'up': (0, -300),
                'right': (300, 0),
                'left': (-300, 0)
            }
            
            if direction not in scroll_map:
                return {'success': False, 'error': f'Неизвестное направление: {direction}'}
            
            delta_x, delta_y = scroll_map[direction]
            
            # Выполнение прокрутки
            for _ in range(amount):
                await self.page.mouse.wheel(delta_x, delta_y)
                await self.page.wait_for_timeout(100)
            
            self.stats['actions_performed'] += 1
            
            return {'success': True, 'action': 'scroll', 'direction': direction, 'amount': amount}
            
        except Exception as e:
            self.logger.error(f"Ошибка прокрутки: {e}")
            return {'success': False, 'error': str(e)}
    
    async def wait_for_element(self, text: str, timeout: int = 10000) -> Optional[Dict]:
        """
        Ожидает появления элемента
        
        Args:
            text: Текст элемента
            timeout: Таймаут ожидания (мс)
            
        Returns:
            Информация об элементе или None
        """
        try:
            if not self.page:
                return None
            
            start_time = time.time()
            
            while (time.time() - start_time) * 1000 < timeout:
                elements = await self.find_elements_by_text(text)
                
                if elements:
                    return elements[0]
                
                await self.page.wait_for_timeout(500)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Ошибка ожидания элемента: {e}")
            return None
    
    async def extract_page_content(self) -> Dict:
        """
        Извлекает содержимое страницы
        
        Returns:
            Содержимое страницы
        """
        try:
            if not self.page:
                return {}
            
            # Базовая информация
            title = await self.page.title()
            url = self.page.url
            
            # HTML содержимое
            html_content = await self.page.content()
            
            # Текстовое содержимое
            text_content = await self.page.evaluate('() => document.body.innerText')
            
            # Ссылки
            links = await self.page.evaluate('''
                () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                    text: a.textContent.trim(),
                    href: a.href,
                    title: a.title
                }))
            ''')
            
            # Изображения
            images = await self.page.evaluate('''
                () => Array.from(document.querySelectorAll('img[src]')).map(img => ({
                    src: img.src,
                    alt: img.alt,
                    title: img.title
                }))
            ''')
            
            # OCR анализ (если доступен)
            ocr_text = []
            if self.ocr_engine:
                screenshot_data = await self.take_screenshot()
                if screenshot_data:
                    nparr = np.frombuffer(screenshot_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if frame is not None:
                        ocr_results = self.ocr_engine.extract_text_from_frame(frame)
                        ocr_text = [r['text'] for r in ocr_results]
            
            return {
                'title': title,
                'url': url,
                'text_content': text_content,
                'html_length': len(html_content),
                'links': links,
                'images': images,
                'ocr_text': ocr_text,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Ошибка извлечения содержимого: {e}")
            return {}
    
    async def execute_javascript(self, script: str) -> Any:
        """
        Выполняет JavaScript код
        
        Args:
            script: JavaScript код
            
        Returns:
            Результат выполнения
        """
        try:
            if not self.page:
                return None
            
            result = await self.page.evaluate(script)
            
            self.stats['actions_performed'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения JavaScript: {e}")
            return None
    
    async def perform_complex_action(self, action_sequence: List[Dict]) -> List[Dict]:
        """
        Выполняет последовательность сложных действий
        
        Args:
            action_sequence: Последовательность действий
            
        Returns:
            Результаты выполнения
        """
        try:
            results = []
            
            for action in action_sequence:
                action_type = action.get('type')
                
                if action_type == 'navigate':
                    result = await self.navigate_to(action['url'])
                
                elif action_type == 'find_and_click':
                    elements = await self.find_elements_by_text(action['text'])
                    if elements:
                        result = await self.click_element(elements[0])
                    else:
                        result = {'success': False, 'error': f"Элемент '{action['text']}' не найден"}
                
                elif action_type == 'find_and_type':
                    elements = await self.find_elements_by_text(action['target_text'])
                    if elements:
                        result = await self.type_text(elements[0], action['input_text'])
                    else:
                        result = {'success': False, 'error': f"Элемент '{action['target_text']}' не найден"}
                
                elif action_type == 'scroll':
                    result = await self.scroll_page(action.get('direction', 'down'), action.get('amount', 3))
                
                elif action_type == 'wait':
                    await self.page.wait_for_timeout(action.get('timeout', 1000))
                    result = {'success': True, 'action': 'wait'}
                
                elif action_type == 'screenshot':
                    screenshot = await self.take_screenshot(action.get('full_page', False))
                    result = {'success': screenshot is not None, 'action': 'screenshot'}
                
                else:
                    result = {'success': False, 'error': f'Неизвестное действие: {action_type}'}
                
                results.append(result)
                
                # Пауза между действиями
                await self.page.wait_for_timeout(action.get('delay', 500))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Ошибка выполнения сложного действия: {e}")
            return [{'success': False, 'error': str(e)}]
    
    def get_statistics(self) -> Dict:
        """Возвращает статистику работы"""
        return {
            **self.stats,
            'browser_active': self.browser is not None,
            'page_active': self.page is not None,
            'ocr_available': self.ocr_engine is not None,
            'element_cache_size': len(self.element_cache),
            'screenshot_cache_size': len(self.screenshot_cache)
        }
    
    async def cleanup(self):
        """Очистка ресурсов"""
        try:
            if self.page:
                await self.page.close()
                self.page = None
            
            if self.context:
                await self.context.close()
                self.context = None
            
            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            
            if self.ocr_engine:
                self.ocr_engine.cleanup()
            
            # Очистка кэшей
            self.element_cache.clear()
            self.screenshot_cache.clear()
            
            self.logger.info("Ресурсы браузерного контроллера очищены")
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки ресурсов: {e}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
