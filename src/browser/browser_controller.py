"""
Browser Controller module for Daur-AI using Playwright.
Provides high-level browser automation capabilities.
"""
from playwright.sync_api import sync_playwright, Browser, Page
from typing import Optional, Dict, List, Union
import logging
import json
import os

class BrowserController:
    def __init__(self, headless: bool = True):
        """Initialize browser controller with configurable headless mode."""
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.active_pages: Dict[str, Page] = {}
        self.logger = logging.getLogger(__name__)

    def start(self) -> bool:
        """Start the browser instance."""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=self.headless)
            return True
        except Exception as e:
            self.logger.error(f"Failed to start browser: {str(e)}")
            return False

    def stop(self) -> bool:
        """Stop the browser instance and cleanup."""
        try:
            for page in self.active_pages.values():
                page.close()
            self.active_pages.clear()
            
            if self.browser:
                self.browser.close()
            
            if self.playwright:
                self.playwright.stop()
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop browser: {str(e)}")
            return False

    def create_page(self, page_id: str = "default") -> Optional[Page]:
        """Create a new browser page with given ID."""
        try:
            if not self.browser:
                if not self.start():
                    return None
            
            page = self.browser.new_page()
            self.active_pages[page_id] = page
            return page
        except Exception as e:
            self.logger.error(f"Failed to create page: {str(e)}")
            return None

    def navigate(self, url: str, page_id: str = "default") -> bool:
        """Navigate to specified URL."""
        try:
            page = self._get_or_create_page(page_id)
            if not page:
                return False
            
            page.goto(url)
            return True
        except Exception as e:
            self.logger.error(f"Failed to navigate to {url}: {str(e)}")
            return False

    def take_screenshot(self, path: str, page_id: str = "default") -> bool:
        """Take screenshot of current page."""
        try:
            page = self._get_or_create_page(page_id)
            if not page:
                return False
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(path), exist_ok=True)
            page.screenshot(path=path)
            return True
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")
            return False

    def execute_script(self, script: str, page_id: str = "default") -> Optional[Union[str, dict, list]]:
        """Execute JavaScript in the page and return the result."""
        try:
            page = self._get_or_create_page(page_id)
            if not page:
                return None
            
            result = page.evaluate(script)
            return result
        except Exception as e:
            self.logger.error(f"Failed to execute script: {str(e)}")
            return None

    def fill_form(self, selectors: Dict[str, str], page_id: str = "default") -> bool:
        """Fill form fields using provided selector-value pairs."""
        try:
            page = self._get_or_create_page(page_id)
            if not page:
                return False

            for selector, value in selectors.items():
                page.fill(selector, value)
            return True
        except Exception as e:
            self.logger.error(f"Failed to fill form: {str(e)}")
            return False

    def click_element(self, selector: str, page_id: str = "default") -> bool:
        """Click an element on the page."""
        try:
            page = self._get_or_create_page(page_id)
            if not page:
                return False

            page.click(selector)
            return True
        except Exception as e:
            self.logger.error(f"Failed to click element: {str(e)}")
            return False

    def get_element_text(self, selector: str, page_id: str = "default") -> Optional[str]:
        """Get text content of an element."""
        try:
            page = self._get_or_create_page(page_id)
            if not page:
                return None

            element = page.query_selector(selector)
            return element.text_content() if element else None
        except Exception as e:
            self.logger.error(f"Failed to get element text: {str(e)}")
            return None

    def _get_or_create_page(self, page_id: str = "default") -> Optional[Page]:
        """Get existing page or create new one if doesn't exist."""
        if page_id not in self.active_pages:
            return self.create_page(page_id)
        return self.active_pages[page_id]