"""Mock implementations of Playwright classes for testing."""
import logging
from typing import Optional, Dict, List, Any, Union, Callable, Awaitable
import asyncio
from pathlib import Path
import json
import base64

logger = logging.getLogger(__name__)

class MockElementHandle:
    """Mock implementation of Playwright ElementHandle."""
    
    def __init__(self, page: "MockPage", selector: str):
        self.page = page
        self.selector = selector
        self._is_visible = True
        self._bounding_box = {"x": 0, "y": 0, "width": 100, "height": 30}
        self._text_content = ""
        
    async def click(self, **kwargs):
        """Simulate clicking the element."""
        if not self._is_visible:
            raise Exception("Element is not visible")
        logger.info(f"Clicked element: {self.selector}")
        
    async def type(self, text: str, **kwargs):
        """Simulate typing into the element."""
        if not self._is_visible:
            raise Exception("Element is not visible")
        logger.info(f"Typed text into element {self.selector}: {text}")
        
    async def fill(self, value: str):
        """Simulate filling form element."""
        if not self._is_visible:
            raise Exception("Element is not visible")
        logger.info(f"Filled element {self.selector} with value: {value}")
        
    async def press(self, key: str):
        """Simulate pressing a key."""
        logger.info(f"Pressed key {key} on element {self.selector}")
        
    async def is_visible(self) -> bool:
        """Check if element is visible."""
        return self._is_visible
        
    async def bounding_box(self) -> Optional[Dict[str, float]]:
        """Get element's bounding box."""
        return self._bounding_box if self._is_visible else None
        
    async def text_content(self) -> str:
        """Get element's text content."""
        return self._text_content
        
    async def get_attribute(self, name: str) -> Optional[str]:
        """Get element attribute."""
        return f"mock_{name}_value"
        
    async def screenshot(self, **kwargs) -> bytes:
        """Take element screenshot."""
        return b"mock_screenshot_data"

class MockResponse:
    """Mock implementation of Playwright Response."""
    
    def __init__(self, status: int = 200):
        self.status = status
        self._body = b"mock_response_body"
        self.headers = {"content-type": "text/html"}
        
    async def body(self) -> bytes:
        """Get response body."""
        return self._body
        
    async def text(self) -> str:
        """Get response text."""
        return self._body.decode()
        
    async def json(self) -> Any:
        """Get response as JSON."""
        return {"status": "success"}

class MockPage:
    """Mock implementation of Playwright Page."""
    
    def __init__(self, browser: "MockBrowser"):
        self.browser = browser
        self.url = "about:blank"
        self._content = "<html><body>Mock page</body></html>"
        self._viewport_size = {"width": 1280, "height": 720}
        self._listeners: Dict[str, List[Callable]] = {}
        
    async def goto(self, url: str, **kwargs) -> MockResponse:
        """Navigate to URL."""
        self.url = url
        logger.info(f"Navigated to: {url}")
        return MockResponse()
        
    async def close(self):
        """Close page."""
        logger.info("Closed page")
        
    async def screenshot(self, **kwargs) -> bytes:
        """Take page screenshot."""
        return b"mock_screenshot_data"
        
    async def content(self) -> str:
        """Get page content."""
        return self._content
        
    async def evaluate(self, expression: str) -> Any:
        """Evaluate JavaScript."""
        logger.info(f"Evaluated JS: {expression}")
        return None
        
    async def wait_for_selector(self, selector: str, **kwargs) -> Optional[MockElementHandle]:
        """Wait for element matching selector."""
        return MockElementHandle(self, selector)
        
    async def query_selector(self, selector: str) -> Optional[MockElementHandle]:
        """Find element matching selector."""
        return MockElementHandle(self, selector)
        
    async def query_selector_all(self, selector: str) -> List[MockElementHandle]:
        """Find all elements matching selector."""
        return [MockElementHandle(self, selector)]
        
    def on(self, event: str, callback: Callable):
        """Add event listener."""
        if event not in self._listeners:
            self._listeners[event] = []
        self._listeners[event].append(callback)
        
    async def reload(self):
        """Reload page."""
        logger.info("Reloaded page")
        
    async def set_viewport_size(self, viewport: Dict[str, int]):
        """Set viewport size."""
        self._viewport_size = viewport

class MockBrowserContext:
    """Mock implementation of Playwright BrowserContext."""
    
    def __init__(self, browser: "MockBrowser"):
        self.browser = browser
        
    async def new_page(self) -> MockPage:
        """Create new page."""
        return MockPage(self.browser)
        
    async def close(self):
        """Close context."""
        pass

class MockBrowser:
    """Mock implementation of Playwright Browser."""
    
    def __init__(self):
        pass
        
    async def new_context(self, **kwargs) -> MockBrowserContext:
        """Create new browser context."""
        return MockBrowserContext(self)
        
    async def new_page(self) -> MockPage:
        """Create new page."""
        context = await self.new_context()
        return await context.new_page()
        
    async def close(self):
        """Close browser."""
        pass

class MockPlaywright:
    """Mock implementation of Playwright."""
    
    def __init__(self):
        self.chromium = MockBrowserLauncher()
        self.firefox = MockBrowserLauncher()
        self.webkit = MockBrowserLauncher()
        
    async def stop(self):
        """Stop Playwright."""
        pass

class MockBrowserLauncher:
    """Mock implementation of Playwright browser launcher."""
    
    async def launch(self, **kwargs) -> MockBrowser:
        """Launch browser."""
        return MockBrowser()

async def async_playwright() -> MockPlaywright:
    """Create mock async Playwright instance."""
    return MockPlaywright()

def sync_playwright() -> MockPlaywright:
    """Create mock sync Playwright instance."""
    return MockPlaywright()