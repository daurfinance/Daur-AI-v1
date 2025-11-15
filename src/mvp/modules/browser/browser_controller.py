"""
Browser Controller - Chrome and Safari Automation
Uses Selenium for browser control
"""

import logging
from typing import Optional, List, Dict
import time
from pathlib import Path

logger = logging.getLogger(__name__)


class BrowserController:
    """Control Chrome and Safari browsers"""
    
    def __init__(self, browser: str = 'chrome'):
        """
        Initialize browser controller
        
        Args:
            browser: 'chrome' or 'safari'
        """
        self.browser = browser
        self.driver = None
        self.available = False
        
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.common.keys import Keys
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            self.webdriver = webdriver
            self.By = By
            self.Keys = Keys
            self.WebDriverWait = WebDriverWait
            self.EC = EC
            
            self.available = True
            logger.info(f"Browser controller initialized for {browser}")
            
        except ImportError:
            logger.error("Selenium not installed. Browser control will not work.")
    
    def is_available(self) -> bool:
        """Check if browser control is available"""
        return self.available
    
    def start(self) -> bool:
        """
        Start browser
        
        Returns:
            True if successful
        """
        if not self.available:
            return False
        
        try:
            if self.browser == 'chrome':
                options = self.webdriver.ChromeOptions()
                # options.add_argument('--headless')  # Uncomment for headless mode
                self.driver = self.webdriver.Chrome(options=options)
            
            elif self.browser == 'safari':
                self.driver = self.webdriver.Safari()
            
            else:
                logger.error(f"Unsupported browser: {self.browser}")
                return False
            
            logger.info(f"{self.browser} browser started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False
    
    def stop(self):
        """Stop browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser stopped")
            except Exception as e:
                logger.error(f"Error stopping browser: {e}")
            finally:
                self.driver = None
    
    def navigate(self, url: str) -> bool:
        """
        Navigate to URL
        
        Args:
            url: URL to navigate to
            
        Returns:
            True if successful
        """
        if not self.driver:
            logger.error("Browser not started")
            return False
        
        try:
            self.driver.get(url)
            logger.info(f"Navigated to {url}")
            return True
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    def search_google(self, query: str) -> bool:
        """
        Search on Google
        
        Args:
            query: Search query
            
        Returns:
            True if successful
        """
        if not self.navigate("https://www.google.com"):
            return False
        
        try:
            # Find search box
            search_box = self.driver.find_element(self.By.NAME, "q")
            search_box.send_keys(query)
            search_box.send_keys(self.Keys.RETURN)
            
            logger.info(f"Searched Google for: {query}")
            return True
            
        except Exception as e:
            logger.error(f"Google search failed: {e}")
            return False
    
    def click_element(self, selector: str, by: str = 'css') -> bool:
        """
        Click element
        
        Args:
            selector: Element selector
            by: Selector type ('css', 'xpath', 'id', 'name')
            
        Returns:
            True if successful
        """
        if not self.driver:
            return False
        
        try:
            by_type = {
                'css': self.By.CSS_SELECTOR,
                'xpath': self.By.XPATH,
                'id': self.By.ID,
                'name': self.By.NAME
            }.get(by, self.By.CSS_SELECTOR)
            
            element = self.driver.find_element(by_type, selector)
            element.click()
            
            logger.debug(f"Clicked element: {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return False
    
    def type_text(self, selector: str, text: str, by: str = 'css') -> bool:
        """
        Type text into element
        
        Args:
            selector: Element selector
            text: Text to type
            by: Selector type
            
        Returns:
            True if successful
        """
        if not self.driver:
            return False
        
        try:
            by_type = {
                'css': self.By.CSS_SELECTOR,
                'xpath': self.By.XPATH,
                'id': self.By.ID,
                'name': self.By.NAME
            }.get(by, self.By.CSS_SELECTOR)
            
            element = self.driver.find_element(by_type, selector)
            element.clear()
            element.send_keys(text)
            
            logger.debug(f"Typed text into {selector}")
            return True
            
        except Exception as e:
            logger.error(f"Type text failed: {e}")
            return False
    
    def get_page_title(self) -> str:
        """Get current page title"""
        if self.driver:
            return self.driver.title
        return ""
    
    def get_current_url(self) -> str:
        """Get current URL"""
        if self.driver:
            return self.driver.current_url
        return ""
    
    def take_screenshot(self, filepath: str) -> bool:
        """
        Take screenshot of current page
        
        Args:
            filepath: Path to save screenshot
            
        Returns:
            True if successful
        """
        if not self.driver:
            return False
        
        try:
            self.driver.save_screenshot(filepath)
            logger.debug(f"Screenshot saved: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return False
    
    def execute_script(self, script: str) -> any:
        """
        Execute JavaScript
        
        Args:
            script: JavaScript code
            
        Returns:
            Script return value
        """
        if not self.driver:
            return None
        
        try:
            return self.driver.execute_script(script)
        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            return None
    
    def wait_for_element(
        self,
        selector: str,
        by: str = 'css',
        timeout: int = 10
    ) -> bool:
        """
        Wait for element to be present
        
        Args:
            selector: Element selector
            by: Selector type
            timeout: Timeout in seconds
            
        Returns:
            True if element found
        """
        if not self.driver:
            return False
        
        try:
            by_type = {
                'css': self.By.CSS_SELECTOR,
                'xpath': self.By.XPATH,
                'id': self.By.ID,
                'name': self.By.NAME
            }.get(by, self.By.CSS_SELECTOR)
            
            wait = self.WebDriverWait(self.driver, timeout)
            wait.until(self.EC.presence_of_element_located((by_type, selector)))
            
            return True
            
        except Exception as e:
            logger.error(f"Wait for element failed: {e}")
            return False
    
    def get_page_text(self) -> str:
        """Get all text from current page"""
        if not self.driver:
            return ""
        
        try:
            return self.driver.find_element(self.By.TAG_NAME, "body").text
        except Exception as e:
            logger.error(f"Get page text failed: {e}")
            return ""
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


def get_browser_controller(browser: str = 'chrome') -> BrowserController:
    """
    Get browser controller instance
    
    Args:
        browser: 'chrome' or 'safari'
        
    Returns:
        BrowserController instance
    """
    return BrowserController(browser)

