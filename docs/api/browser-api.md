# Browser Automation API

The Browser Automation API provides powerful web automation capabilities using Playwright, enabling Daur AI to interact with websites, scrape data, fill forms, and execute complex web workflows.

## Overview

The `BrowserAutomation` class provides a high-level interface for browser automation with support for multiple browser engines (Chromium, Firefox, WebKit), headless mode, and advanced features like network interception and screenshot capture.

## Class: BrowserAutomation

### Initialization

```python
from src.browser.browser_automation import BrowserAutomation

# Basic initialization (Chromium, headless)
browser = BrowserAutomation()

# Custom configuration
browser = BrowserAutomation(
    browser_type="firefox",
    headless=False,
    viewport_size=(1920, 1080)
)

# Initialize browser
await browser.initialize()
```

## Navigation

### navigate()

Navigate to a URL.

**Signature:**
```python
async def navigate(
    self,
    url: str,
    wait_until: str = "load"
) -> None
```

**Parameters:**
- `url` (str): URL to navigate to
- `wait_until` (str): When to consider navigation complete ("load", "domcontentloaded", "networkidle")

**Example:**
```python
await browser.navigate("https://example.com")
await browser.navigate("https://example.com", wait_until="networkidle")
```

---

### go_back()

Navigate back in history.

**Signature:**
```python
async def go_back(self) -> None
```

**Example:**
```python
await browser.go_back()
```

---

### go_forward()

Navigate forward in history.

**Signature:**
```python
async def go_forward(self) -> None
```

---

### reload()

Reload current page.

**Signature:**
```python
async def reload(self, hard: bool = False) -> None
```

**Parameters:**
- `hard` (bool): Perform hard reload (bypass cache)

**Example:**
```python
await browser.reload(hard=True)
```

---

## Element Interaction

### click()

Click an element.

**Signature:**
```python
async def click(
    self,
    selector: str,
    wait_for: bool = True,
    timeout: float = 30.0
) -> None
```

**Parameters:**
- `selector` (str): CSS selector or XPath
- `wait_for` (bool): Wait for element to be visible and enabled
- `timeout` (float): Maximum wait time in seconds

**Example:**
```python
# CSS selector
await browser.click("#submit-button")

# XPath
await browser.click("//button[text()='Submit']")

# With custom timeout
await browser.click(".slow-button", timeout=60.0)
```

---

### fill()

Fill an input field.

**Signature:**
```python
async def fill(
    self,
    selector: str,
    value: str,
    clear_first: bool = True
) -> None
```

**Parameters:**
- `selector` (str): CSS selector for input element
- `value` (str): Value to fill
- `clear_first` (bool): Clear existing value before filling

**Example:**
```python
await browser.fill("#username", "user@example.com")
await browser.fill("#password", "secretpass")
```

---

### type_text()

Type text with realistic delays.

**Signature:**
```python
async def type_text(
    self,
    selector: str,
    text: str,
    delay: float = 0.1
) -> None
```

**Parameters:**
- `selector` (str): CSS selector for input element
- `text` (str): Text to type
- `delay` (float): Delay between keystrokes in seconds

**Example:**
```python
await browser.type_text("#search", "Daur AI", delay=0.05)
```

---

### select_option()

Select option from dropdown.

**Signature:**
```python
async def select_option(
    self,
    selector: str,
    value: Optional[str] = None,
    label: Optional[str] = None,
    index: Optional[int] = None
) -> None
```

**Parameters:**
- `selector` (str): CSS selector for select element
- `value` (str, optional): Option value
- `label` (str, optional): Option label text
- `index` (int, optional): Option index

**Example:**
```python
# Select by value
await browser.select_option("#country", value="US")

# Select by label
await browser.select_option("#country", label="United States")

# Select by index
await browser.select_option("#country", index=0)
```

---

### check()

Check a checkbox or radio button.

**Signature:**
```python
async def check(self, selector: str) -> None
```

**Example:**
```python
await browser.check("#agree-terms")
```

---

### uncheck()

Uncheck a checkbox.

**Signature:**
```python
async def uncheck(self, selector: str) -> None
```

---

## Data Extraction

### get_text()

Get text content of an element.

**Signature:**
```python
async def get_text(self, selector: str) -> str
```

**Parameters:**
- `selector` (str): CSS selector

**Returns:**
- `str`: Element text content

**Example:**
```python
title = await browser.get_text("h1")
print(f"Page title: {title}")
```

---

### get_attribute()

Get attribute value of an element.

**Signature:**
```python
async def get_attribute(
    self,
    selector: str,
    attribute: str
) -> Optional[str]
```

**Parameters:**
- `selector` (str): CSS selector
- `attribute` (str): Attribute name

**Returns:**
- `str`: Attribute value, or None if not found

**Example:**
```python
href = await browser.get_attribute("a.link", "href")
src = await browser.get_attribute("img", "src")
```

---

### get_all_text()

Get text from all matching elements.

**Signature:**
```python
async def get_all_text(self, selector: str) -> List[str]
```

**Parameters:**
- `selector` (str): CSS selector

**Returns:**
- `List[str]`: List of text contents

**Example:**
```python
items = await browser.get_all_text(".product-name")
for item in items:
    print(item)
```

---

### extract_table()

Extract data from HTML table.

**Signature:**
```python
async def extract_table(
    self,
    selector: str,
    include_header: bool = True
) -> List[List[str]]
```

**Parameters:**
- `selector` (str): CSS selector for table
- `include_header` (bool): Include header row

**Returns:**
- `List[List[str]]`: Table data as 2D list

**Example:**
```python
data = await browser.extract_table("#data-table")
for row in data:
    print(row)
```

---

## Form Automation

### fill_form()

Fill multiple form fields at once.

**Signature:**
```python
async def fill_form(
    self,
    fields: Dict[str, str],
    submit: bool = False,
    submit_selector: Optional[str] = None
) -> None
```

**Parameters:**
- `fields` (dict): Mapping of selectors to values
- `submit` (bool): Submit form after filling
- `submit_selector` (str, optional): Selector for submit button

**Example:**
```python
await browser.fill_form({
    "#username": "user@example.com",
    "#password": "secretpass",
    "#remember-me": "checked"
}, submit=True, submit_selector="#login-button")
```

---

### upload_file()

Upload file to input element.

**Signature:**
```python
async def upload_file(
    self,
    selector: str,
    file_path: str
) -> None
```

**Parameters:**
- `selector` (str): CSS selector for file input
- `file_path` (str): Path to file to upload

**Example:**
```python
await browser.upload_file("#file-upload", "/path/to/document.pdf")
```

---

## Waiting & Synchronization

### wait_for_selector()

Wait for element to appear.

**Signature:**
```python
async def wait_for_selector(
    self,
    selector: str,
    state: str = "visible",
    timeout: float = 30.0
) -> None
```

**Parameters:**
- `selector` (str): CSS selector
- `state` (str): Element state ("visible", "attached", "hidden")
- `timeout` (float): Maximum wait time in seconds

**Example:**
```python
await browser.wait_for_selector(".success-message", timeout=10.0)
```

---

### wait_for_url()

Wait for URL to match pattern.

**Signature:**
```python
async def wait_for_url(
    self,
    url_pattern: str,
    timeout: float = 30.0
) -> None
```

**Parameters:**
- `url_pattern` (str): URL pattern (supports wildcards)
- `timeout` (float): Maximum wait time

**Example:**
```python
await browser.wait_for_url("**/dashboard", timeout=10.0)
```

---

### wait_for_load_state()

Wait for page load state.

**Signature:**
```python
async def wait_for_load_state(
    self,
    state: str = "load"
) -> None
```

**Parameters:**
- `state` (str): Load state ("load", "domcontentloaded", "networkidle")

**Example:**
```python
await browser.wait_for_load_state("networkidle")
```

---

## Screenshots & PDFs

### screenshot()

Take screenshot of page or element.

**Signature:**
```python
async def screenshot(
    self,
    path: str,
    selector: Optional[str] = None,
    full_page: bool = False
) -> bytes
```

**Parameters:**
- `path` (str): Path to save screenshot
- `selector` (str, optional): Selector for element screenshot
- `full_page` (bool): Capture full scrollable page

**Returns:**
- `bytes`: Screenshot data

**Example:**
```python
# Full page screenshot
await browser.screenshot("/tmp/page.png", full_page=True)

# Element screenshot
await browser.screenshot("/tmp/element.png", selector="#chart")
```

---

### pdf()

Generate PDF of page.

**Signature:**
```python
async def pdf(
    self,
    path: str,
    format: str = "A4",
    print_background: bool = True
) -> bytes
```

**Parameters:**
- `path` (str): Path to save PDF
- `format` (str): Page format ("A4", "Letter", etc.)
- `print_background` (bool): Include background graphics

**Returns:**
- `bytes`: PDF data

**Example:**
```python
await browser.pdf("/tmp/page.pdf", format="A4")
```

---

## JavaScript Execution

### evaluate()

Execute JavaScript in page context.

**Signature:**
```python
async def evaluate(
    self,
    script: str,
    *args
) -> Any
```

**Parameters:**
- `script` (str): JavaScript code to execute
- `*args`: Arguments to pass to script

**Returns:**
- `Any`: Script return value

**Example:**
```python
# Get page title
title = await browser.evaluate("document.title")

# Scroll to bottom
await browser.evaluate("window.scrollTo(0, document.body.scrollHeight)")

# With arguments
result = await browser.evaluate("(a, b) => a + b", 5, 3)
```

---

## Network Control

### set_extra_headers()

Set custom HTTP headers.

**Signature:**
```python
async def set_extra_headers(self, headers: Dict[str, str]) -> None
```

**Parameters:**
- `headers` (dict): HTTP headers to set

**Example:**
```python
await browser.set_extra_headers({
    "Authorization": "Bearer token123",
    "Custom-Header": "value"
})
```

---

### intercept_requests()

Intercept and modify network requests.

**Signature:**
```python
async def intercept_requests(
    self,
    pattern: str,
    handler: Callable
) -> None
```

**Parameters:**
- `pattern` (str): URL pattern to intercept
- `handler` (callable): Function to handle requests

**Example:**
```python
async def block_ads(route, request):
    if "ads" in request.url:
        await route.abort()
    else:
        await route.continue_()

await browser.intercept_requests("**/*", block_ads)
```

---

## Cookie Management

### get_cookies()

Get all cookies.

**Signature:**
```python
async def get_cookies(self) -> List[Dict[str, Any]]
```

**Returns:**
- `List[dict]`: List of cookie objects

**Example:**
```python
cookies = await browser.get_cookies()
for cookie in cookies:
    print(f"{cookie['name']}: {cookie['value']}")
```

---

### set_cookies()

Set cookies.

**Signature:**
```python
async def set_cookies(self, cookies: List[Dict[str, Any]]) -> None
```

**Parameters:**
- `cookies` (list): List of cookie objects

**Example:**
```python
await browser.set_cookies([{
    "name": "session",
    "value": "abc123",
    "domain": "example.com",
    "path": "/"
}])
```

---

### clear_cookies()

Clear all cookies.

**Signature:**
```python
async def clear_cookies(self) -> None
```

---

## Browser Management

### new_page()

Open a new page/tab.

**Signature:**
```python
async def new_page(self) -> None
```

**Example:**
```python
await browser.new_page()
```

---

### close_page()

Close current page.

**Signature:**
```python
async def close_page(self) -> None
```

---

### close()

Close browser.

**Signature:**
```python
async def close(self) -> None
```

**Example:**
```python
await browser.close()
```

---

## Error Handling

```python
from src.exceptions import BrowserException, NavigationException

try:
    await browser.navigate("https://example.com")
    await browser.click("#button")
except NavigationException as e:
    print(f"Navigation failed: {e}")
except BrowserException as e:
    print(f"Browser error: {e}")
```

---

## Best Practices

**Selectors**  
Use stable selectors (IDs, data attributes) instead of fragile ones (classes, positions).

**Waiting**  
Always wait for elements before interacting. Use appropriate wait strategies for dynamic content.

**Error Handling**  
Implement retry logic for network-dependent operations.

**Resource Cleanup**  
Always close browsers when done to free resources.

**Headless Mode**  
Use headless mode for production, headed mode for debugging.

---

## Complete Example

```python
import asyncio
from src.browser.browser_automation import BrowserAutomation

async def scrape_product_data():
    browser = BrowserAutomation(headless=True)
    await browser.initialize()
    
    try:
        # Navigate to product page
        await browser.navigate("https://example.com/products")
        
        # Wait for products to load
        await browser.wait_for_selector(".product-card")
        
        # Extract product names and prices
        names = await browser.get_all_text(".product-name")
        prices = await browser.get_all_text(".product-price")
        
        products = list(zip(names, prices))
        
        # Take screenshot
        await browser.screenshot("/tmp/products.png", full_page=True)
        
        return products
        
    finally:
        await browser.close()

# Run scraper
products = asyncio.run(scrape_product_data())
for name, price in products:
    print(f"{name}: {price}")
```

---

*API Version: 2.0.0*  
*Last Updated: 2025-11-12*

