"""
Real Browser Automation with Selenium
Полнофункциональная автоматизация браузера с реальной интеграцией Selenium
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
from dataclasses import dataclass
import json

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException, 
        StaleElementReferenceException, WebDriverException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logging.warning("Selenium not available. Install with: pip install selenium")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserType(Enum):
    """Типы браузеров"""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


class WaitStrategy(Enum):
    """Стратегии ожидания элементов"""
    PRESENCE = "presence"
    VISIBILITY = "visibility"
    CLICKABLE = "clickable"
    STALENESS = "staleness"


@dataclass
class BrowserConfig:
    """Конфигурация браузера"""
    browser_type: BrowserType = BrowserType.CHROME
    headless: bool = False
    window_size: Tuple[int, int] = (1920, 1080)
    user_agent: Optional[str] = None
    proxy: Optional[str] = None
    timeout: int = 10
    implicit_wait: int = 5


@dataclass
class WebElement:
    """Веб элемент"""
    selector: str
    by: str
    text: str = ""
    tag_name: str = ""
    attributes: Dict[str, str] = None


class RealBrowserAutomation:
    """Реальная автоматизация браузера с Selenium"""
    
    def __init__(self, config: BrowserConfig = None):
        """
        Инициализация браузера
        
        Args:
            config: Конфигурация браузера
        """
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required. Install with: pip install selenium")
        
        self.config = config or BrowserConfig()
        self.logger = logging.getLogger(__name__)
        self.driver = None
        self.wait = None
        self.actions = None
        self.current_url = ""
        self.history = []
    
    def start(self) -> bool:
        """Запустить браузер"""
        try:
            options = self._get_browser_options()
            
            if self.config.browser_type == BrowserType.CHROME:
                self.driver = webdriver.Chrome(options=options)
            elif self.config.browser_type == BrowserType.FIREFOX:
                self.driver = webdriver.Firefox(options=options)
            elif self.config.browser_type == BrowserType.EDGE:
                self.driver = webdriver.Edge(options=options)
            elif self.config.browser_type == BrowserType.SAFARI:
                self.driver = webdriver.Safari()
            else:
                self.logger.error(f"Unsupported browser: {self.config.browser_type}")
                return False
            
            # Установка размера окна
            self.driver.set_window_size(*self.config.window_size)
            
            # Инициализация вспомогательных объектов
            self.wait = WebDriverWait(self.driver, self.config.timeout)
            self.actions = ActionChains(self.driver)
            self.driver.implicitly_wait(self.config.implicit_wait)
            
            self.logger.info(f"Browser {self.config.browser_type.value} started successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Error starting browser: {e}")
            return False
    
    def _get_browser_options(self):
        """Получить опции браузера"""
        if self.config.browser_type == BrowserType.CHROME:
            from selenium.webdriver.chrome.options import Options
            options = Options()
        elif self.config.browser_type == BrowserType.FIREFOX:
            from selenium.webdriver.firefox.options import Options
            options = Options()
        elif self.config.browser_type == BrowserType.EDGE:
            from selenium.webdriver.edge.options import Options
            options = Options()
        else:
            return None
        
        if self.config.headless:
            options.add_argument("--headless")
        
        if self.config.user_agent:
            options.add_argument(f"user-agent={self.config.user_agent}")
        
        if self.config.proxy:
            options.add_argument(f"--proxy-server={self.config.proxy}")
        
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        return options
    
    def stop(self) -> bool:
        """Остановить браузер"""
        try:
            if self.driver:
                self.driver.quit()
            self.logger.info("Browser stopped")
            return True
        except Exception as e:
            self.logger.error(f"Error stopping browser: {e}")
            return False
    
    def navigate(self, url: str) -> bool:
        """Перейти на URL"""
        try:
            self.driver.get(url)
            self.current_url = url
            self.history.append(url)
            self.logger.info(f"Navigated to: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Error navigating to {url}: {e}")
            return False
    
    def go_back(self) -> bool:
        """Вернуться на предыдущую страницу"""
        try:
            self.driver.back()
            self.current_url = self.driver.current_url
            self.logger.info("Went back")
            return True
        except Exception as e:
            self.logger.error(f"Error going back: {e}")
            return False
    
    def go_forward(self) -> bool:
        """Перейти на следующую страницу"""
        try:
            self.driver.forward()
            self.current_url = self.driver.current_url
            self.logger.info("Went forward")
            return True
        except Exception as e:
            self.logger.error(f"Error going forward: {e}")
            return False
    
    def refresh(self) -> bool:
        """Обновить страницу"""
        try:
            self.driver.refresh()
            self.logger.info("Page refreshed")
            return True
        except Exception as e:
            self.logger.error(f"Error refreshing page: {e}")
            return False
    
    def find_element(self, selector: str, by: str = "css") -> Optional[WebElement]:
        """Найти элемент на странице"""
        try:
            by_type = self._get_by_type(by)
            element = self.wait.until(EC.presence_of_element_located((by_type, selector)))
            
            return WebElement(
                selector=selector,
                by=by,
                text=element.text,
                tag_name=element.tag_name,
                attributes=element.get_attribute("*")
            )
        except TimeoutException:
            self.logger.warning(f"Element not found: {selector}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element {selector}: {e}")
            return None
    
    def find_elements(self, selector: str, by: str = "css") -> List[WebElement]:
        """Найти все элементы по селектору"""
        try:
            by_type = self._get_by_type(by)
            elements = self.driver.find_elements(by_type, selector)
            
            result = []
            for element in elements:
                result.append(WebElement(
                    selector=selector,
                    by=by,
                    text=element.text,
                    tag_name=element.tag_name,
                    attributes=element.get_attribute("*")
                ))
            
            self.logger.info(f"Found {len(result)} elements: {selector}")
            return result
        except Exception as e:
            self.logger.error(f"Error finding elements {selector}: {e}")
            return []
    
    def click(self, selector: str, by: str = "css") -> bool:
        """Кликнуть на элемент"""
        try:
            by_type = self._get_by_type(by)
            element = self.wait.until(EC.element_to_be_clickable((by_type, selector)))
            element.click()
            self.logger.info(f"Clicked: {selector}")
            return True
        except Exception as e:
            self.logger.error(f"Error clicking {selector}: {e}")
            return False
    
    def type_text(self, selector: str, text: str, by: str = "css", clear: bool = True) -> bool:
        """Ввести текст в элемент"""
        try:
            by_type = self._get_by_type(by)
            element = self.wait.until(EC.presence_of_element_located((by_type, selector)))
            
            if clear:
                element.clear()
            
            element.send_keys(text)
            self.logger.info(f"Typed text in: {selector}")
            return True
        except Exception as e:
            self.logger.error(f"Error typing text in {selector}: {e}")
            return False
    
    def submit_form(self, selector: str, by: str = "css") -> bool:
        """Отправить форму"""
        try:
            by_type = self._get_by_type(by)
            form = self.driver.find_element(by_type, selector)
            form.submit()
            self.logger.info(f"Form submitted: {selector}")
            return True
        except Exception as e:
            self.logger.error(f"Error submitting form {selector}: {e}")
            return False
    
    def get_page_source(self) -> str:
        """Получить исходный код страницы"""
        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Error getting page source: {e}")
            return ""
    
    def get_page_title(self) -> str:
        """Получить заголовок страницы"""
        try:
            return self.driver.title
        except Exception as e:
            self.logger.error(f"Error getting page title: {e}")
            return ""
    
    def get_cookies(self) -> Dict[str, str]:
        """Получить все cookies"""
        try:
            cookies = self.driver.get_cookies()
            result = {}
            for cookie in cookies:
                result[cookie['name']] = cookie['value']
            return result
        except Exception as e:
            self.logger.error(f"Error getting cookies: {e}")
            return {}
    
    def set_cookie(self, name: str, value: str) -> bool:
        """Установить cookie"""
        try:
            self.driver.add_cookie({'name': name, 'value': value})
            self.logger.info(f"Cookie set: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error setting cookie {name}: {e}")
            return False
    
    def delete_cookie(self, name: str) -> bool:
        """Удалить cookie"""
        try:
            self.driver.delete_cookie(name)
            self.logger.info(f"Cookie deleted: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting cookie {name}: {e}")
            return False
    
    def clear_cookies(self) -> bool:
        """Очистить все cookies"""
        try:
            self.driver.delete_all_cookies()
            self.logger.info("All cookies cleared")
            return True
        except Exception as e:
            self.logger.error(f"Error clearing cookies: {e}")
            return False
    
    def take_screenshot(self, filepath: str) -> bool:
        """Сделать скриншот"""
        try:
            self.driver.save_screenshot(filepath)
            self.logger.info(f"Screenshot saved: {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return False
    
    def execute_script(self, script: str, *args) -> Any:
        """Выполнить JavaScript"""
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"Error executing script: {e}")
            return None
    
    def wait_for_element(self, selector: str, by: str = "css", timeout: int = None) -> bool:
        """Ждать появления элемента"""
        try:
            timeout = timeout or self.config.timeout
            by_type = self._get_by_type(by)
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by_type, selector))
            )
            self.logger.info(f"Element appeared: {selector}")
            return True
        except TimeoutException:
            self.logger.warning(f"Timeout waiting for element: {selector}")
            return False
    
    def hover(self, selector: str, by: str = "css") -> bool:
        """Навести курсор на элемент"""
        try:
            by_type = self._get_by_type(by)
            element = self.driver.find_element(by_type, selector)
            self.actions.move_to_element(element).perform()
            self.logger.info(f"Hovered over: {selector}")
            return True
        except Exception as e:
            self.logger.error(f"Error hovering over {selector}: {e}")
            return False
    
    def drag_and_drop(self, source: str, target: str, by: str = "css") -> bool:
        """Перетащить элемент"""
        try:
            by_type = self._get_by_type(by)
            source_element = self.driver.find_element(by_type, source)
            target_element = self.driver.find_element(by_type, target)
            self.actions.drag_and_drop(source_element, target_element).perform()
            self.logger.info(f"Dragged {source} to {target}")
            return True
        except Exception as e:
            self.logger.error(f"Error dragging and dropping: {e}")
            return False
    
    def scroll_to_element(self, selector: str, by: str = "css") -> bool:
        """Прокрутить до элемента"""
        try:
            by_type = self._get_by_type(by)
            element = self.driver.find_element(by_type, selector)
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            self.logger.info(f"Scrolled to: {selector}")
            return True
        except Exception as e:
            self.logger.error(f"Error scrolling to {selector}: {e}")
            return False
    
    def scroll(self, x: int, y: int) -> bool:
        """Прокрутить страницу"""
        try:
            self.driver.execute_script(f"window.scrollBy({x}, {y});")
            self.logger.info(f"Scrolled by: {x}, {y}")
            return True
        except Exception as e:
            self.logger.error(f"Error scrolling: {e}")
            return False
    
    def get_element_text(self, selector: str, by: str = "css") -> str:
        """Получить текст элемента"""
        try:
            by_type = self._get_by_type(by)
            element = self.driver.find_element(by_type, selector)
            return element.text
        except Exception as e:
            self.logger.error(f"Error getting element text: {e}")
            return ""
    
    def get_element_attribute(self, selector: str, attribute: str, by: str = "css") -> str:
        """Получить атрибут элемента"""
        try:
            by_type = self._get_by_type(by)
            element = self.driver.find_element(by_type, selector)
            return element.get_attribute(attribute)
        except Exception as e:
            self.logger.error(f"Error getting element attribute: {e}")
            return ""
    
    def switch_to_frame(self, selector: str, by: str = "css") -> bool:
        """Переключиться на iframe"""
        try:
            by_type = self._get_by_type(by)
            frame = self.driver.find_element(by_type, selector)
            self.driver.switch_to.frame(frame)
            self.logger.info(f"Switched to frame: {selector}")
            return True
        except Exception as e:
            self.logger.error(f"Error switching to frame: {e}")
            return False
    
    def switch_to_default_content(self) -> bool:
        """Вернуться к основному контенту"""
        try:
            self.driver.switch_to.default_content()
            self.logger.info("Switched to default content")
            return True
        except Exception as e:
            self.logger.error(f"Error switching to default content: {e}")
            return False
    
    def accept_alert(self) -> bool:
        """Принять alert"""
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
            self.logger.info("Alert accepted")
            return True
        except Exception as e:
            self.logger.error(f"Error accepting alert: {e}")
            return False
    
    def dismiss_alert(self) -> bool:
        """Отклонить alert"""
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
            self.logger.info("Alert dismissed")
            return True
        except Exception as e:
            self.logger.error(f"Error dismissing alert: {e}")
            return False
    
    def _get_by_type(self, by: str):
        """Получить тип селектора"""
        by_map = {
            "css": By.CSS_SELECTOR,
            "xpath": By.XPATH,
            "id": By.ID,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "tag": By.TAG_NAME,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT
        }
        return by_map.get(by.lower(), By.CSS_SELECTOR)
    
    def get_current_url(self) -> str:
        """Получить текущий URL"""
        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"Error getting current URL: {e}")
            return ""
    
    def get_window_handles(self) -> List[str]:
        """Получить все окна браузера"""
        try:
            return self.driver.window_handles
        except Exception as e:
            self.logger.error(f"Error getting window handles: {e}")
            return []
    
    def switch_to_window(self, handle: str) -> bool:
        """Переключиться на окно"""
        try:
            self.driver.switch_to.window(handle)
            self.logger.info(f"Switched to window: {handle}")
            return True
        except Exception as e:
            self.logger.error(f"Error switching to window: {e}")
            return False
    
    def close_window(self) -> bool:
        """Закрыть текущее окно"""
        try:
            self.driver.close()
            self.logger.info("Window closed")
            return True
        except Exception as e:
            self.logger.error(f"Error closing window: {e}")
            return False

