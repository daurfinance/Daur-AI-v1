from typing import Optional, Dict, List, Any, Union
import logging
from pathlib import Path
import json
import asyncio
from .playwright_utils import playwright_module
Browser = playwright_module.Browser
Page = playwright_module.Page
ElementHandle = playwright_module.ElementHandle 
Response = playwright_module.Response
async_playwright = playwright_module.async_playwright
import base64

class BrowserAutomation:
    """Компонент для автоматизации браузера с использованием Playwright."""
    
    def __init__(self, headless: bool = True):
        self.logger = logging.getLogger(__name__)
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
    async def init(self) -> None:
        """Инициализирует браузер."""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=self.headless)
            self.page = await self.browser.new_page()
        except Exception as e:
            self.logger.error(f"Failed to initialize browser: {e}")
            raise
            
    async def close(self) -> None:
        """Закрывает браузер."""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
            
    async def navigate(self, url: str) -> bool:
        """Переходит по указанному URL.
        
        Args:
            url: URL для перехода
            
        Returns:
            True если навигация успешна
        """
        if not self.page:
            await self.init()
            
        try:
            await self.page.goto(url)
            return True
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            return False
            
    async def find_element(self, 
                          selector: str, 
                          timeout: int = 5000) -> Optional[ElementHandle]:
        """Находит элемент на странице.
        
        Args:
            selector: CSS селектор
            timeout: Таймаут в миллисекундах
            
        Returns:
            Найденный элемент или None
        """
        if not self.page:
            return None
            
        try:
            return await self.page.wait_for_selector(selector, timeout=timeout)
        except:
            return None
            
    async def click(self, selector: str) -> bool:
        """Кликает по элементу.
        
        Args:
            selector: CSS селектор
            
        Returns:
            True если клик успешен
        """
        element = await self.find_element(selector)
        if element:
            await element.click()
            return True
        return False
        
    async def type_text(self, selector: str, text: str) -> bool:
        """Вводит текст в поле.
        
        Args:
            selector: CSS селектор
            text: Текст для ввода
            
        Returns:
            True если ввод успешен
        """
        element = await self.find_element(selector)
        if element:
            await element.fill(text)
            return True
        return False

    async def take_screenshot(self, path: Optional[str] = None) -> Union[str, bool]:
        """Делает скриншот страницы.
        
        Args:
            path: Путь для сохранения скриншота. Если None, возвращает base64.
            
        Returns:
            base64 строка если path=None, иначе True/False
        """
        if not self.page:
            return False
            
        try:
            if path:
                await self.page.screenshot(path=path)
                return True
            else:
                screenshot_bytes = await self.page.screenshot()
                return base64.b64encode(screenshot_bytes).decode('utf-8')
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return False

    async def get_page_content(self) -> Optional[str]:
        """Получает HTML содержимое страницы.
        
        Returns:
            HTML страницы или None при ошибке
        """
        if not self.page:
            return None
            
        try:
            return await self.page.content()
        except Exception as e:
            self.logger.error(f"Failed to get page content: {e}")
            return None

    async def execute_script(self, script: str) -> Any:
        """Выполняет JavaScript код на странице.
        
        Args:
            script: JavaScript код для выполнения
            
        Returns:
            Результат выполнения скрипта
        """
        if not self.page:
            return None
            
        try:
            return await self.page.evaluate(script)
        except Exception as e:
            self.logger.error(f"Script execution failed: {e}")
            return None

    async def wait_for_network_idle(self, timeout: int = 5000) -> bool:
        """Ждет завершения сетевых запросов.
        
        Args:
            timeout: Таймаут в миллисекундах
            
        Returns:
            True если все запросы завершены
        """
        if not self.page:
            return False
            
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            return True
        except Exception as e:
            self.logger.error(f"Network idle wait failed: {e}")
            return False

    async def intercept_requests(self, url_pattern: str) -> List[Dict[str, Any]]:
        """Перехватывает сетевые запросы.
        
        Args:
            url_pattern: Паттерн URL для перехвата
            
        Returns:
            Список перехваченных запросов
        """
        if not self.page:
            return []
            
        requests = []
        
        async def handle_request(request):
            requests.append({
                "url": request.url,
                "method": request.method,
                "headers": request.headers,
                "post_data": request.post_data
            })
            
        await self.page.route(url_pattern, handle_request)
        return requests

    async def set_viewport(self, width: int, height: int) -> bool:
        """Устанавливает размер viewport.
        
        Args:
            width: Ширина viewport
            height: Высота viewport
            
        Returns:
            True если успешно
        """
        if not self.page:
            return False
            
        try:
            await self.page.set_viewport_size({"width": width, "height": height})
            return True
        except Exception as e:
            self.logger.error(f"Viewport setup failed: {e}")
            return False
            return True
        return False
        
    async def get_text(self, selector: str) -> Optional[str]:
        """Получает текст элемента.
        
        Args:
            selector: CSS селектор
            
        Returns:
            Текст элемента или None
        """
        element = await self.find_element(selector)
        if element:
            return await element.text_content()
        return None
        
    async def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """Получает значение атрибута элемента.
        
        Args:
            selector: CSS селектор
            attribute: Имя атрибута
            
        Returns:
            Значение атрибута или None
        """
        element = await self.find_element(selector)
        if element:
            return await element.get_attribute(attribute)
        return None
        
    async def wait_for_navigation(self, timeout: int = 5000) -> bool:
        """Ожидает завершения навигации.
        
        Args:
            timeout: Таймаут в миллисекундах
            
        Returns:
            True если навигация завершена
        """
        if not self.page:
            return False
            
        try:
            await self.page.wait_for_load_state("networkidle", timeout=timeout)
            return True
        except:
            return False
            
    async def screenshot(self, path: Path) -> bool:
        """Делает скриншот страницы.
        
        Args:
            path: Путь для сохранения скриншота
            
        Returns:
            True если скриншот сохранен
        """
        if not self.page:
            return False
            
        try:
            await self.page.screenshot(path=str(path))
            return True
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return False
            
    async def execute_script(self, script: str) -> Any:
        """Выполняет JavaScript на странице.
        
        Args:
            script: JavaScript код
            
        Returns:
            Результат выполнения скрипта
        """
        if not self.page:
            return None
            
        try:
            return await self.page.evaluate(script)
        except Exception as e:
            self.logger.error(f"Script execution failed: {e}")
            return None
            
    async def wait_for_selector(self, 
                               selector: str, 
                               timeout: int = 5000,
                               state: str = "visible") -> bool:
        """Ожидает появления элемента.
        
        Args:
            selector: CSS селектор
            timeout: Таймаут в миллисекундах
            state: Состояние элемента ("visible", "hidden", "attached", "detached")
            
        Returns:
            True если элемент появился
        """
        if not self.page:
            return False
            
        try:
            await self.page.wait_for_selector(
                selector, 
                timeout=timeout,
                state=state
            )
            return True
        except:
            return False
            
    async def get_elements(self, selector: str) -> List[ElementHandle]:
        """Находит все элементы по селектору.
        
        Args:
            selector: CSS селектор
            
        Returns:
            Список найденных элементов
        """
        if not self.page:
            return []
            
        try:
            return await self.page.query_selector_all(selector)
        except:
            return []
            
    async def fill_form(self, form_data: Dict[str, str]) -> bool:
        """Заполняет форму данными.
        
        Args:
            form_data: Словарь с селекторами и значениями полей
            
        Returns:
            True если форма заполнена успешно
        """
        success = True
        for selector, value in form_data.items():
            if not await self.type_text(selector, value):
                success = False
        return success