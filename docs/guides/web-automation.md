# Web Automation Guide

**Version**: 2.0  
**Last Updated**: 2025-11-12  
**Difficulty**: Intermediate

---

## Introduction

Web automation is one of the most powerful features of Daur AI, enabling you to automate interactions with websites, scrape data, perform testing, and execute complex workflows across multiple web applications. This comprehensive guide covers everything from basic navigation to advanced scraping techniques.

Modern web automation requires handling dynamic content, JavaScript-heavy applications, authentication flows, and anti-bot measures. Daur AI provides robust tools to handle all these challenges through its integration with Playwright and intelligent element detection.

---

## Table of Contents

1. [Browser Setup](#browser-setup)
2. [Navigation and Page Loading](#navigation-and-page-loading)
3. [Element Interaction](#element-interaction)
4. [Form Automation](#form-automation)
5. [Data Extraction](#data-extraction)
6. [Authentication Handling](#authentication-handling)
7. [Advanced Techniques](#advanced-techniques)
8. [Best Practices](#best-practices)
9. [Complete Examples](#complete-examples)

---

## Browser Setup

### Initializing the Browser

The browser automation system in Daur AI is built on Playwright, providing reliable cross-browser automation capabilities. You can initialize the browser in either headless or headed mode depending on your needs.

```python
from src.browser.browser_automation import BrowserAutomation
import asyncio

async def setup_browser():
    # Headless mode (no visible browser window)
    browser_headless = BrowserAutomation(headless=True)
    await browser_headless.init()
    
    # Headed mode (visible browser window for debugging)
    browser_headed = BrowserAutomation(headless=False)
    await browser_headed.init()
    
    return browser_headed

browser = asyncio.run(setup_browser())
```

Headless mode is faster and uses less resources, making it ideal for production environments and continuous integration. Headed mode is useful during development to see what the browser is doing and debug issues.

### Browser Configuration

You can configure various browser options to customize behavior:

```python
config = {
    "headless": False,
    "viewport": {"width": 1920, "height": 1080},
    "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "timeout": 30000,  # milliseconds
    "slow_mo": 100  # slow down operations by 100ms for debugging
}

browser = BrowserAutomation(**config)
await browser.init()
```

The viewport size affects how websites render, particularly responsive designs. Setting a realistic user agent helps avoid detection as an automated browser.

---

## Navigation and Page Loading

### Basic Navigation

Navigating to a URL is the foundation of web automation. Daur AI provides several methods to handle different navigation scenarios.

```python
async def navigate_example():
    browser = BrowserAutomation(headless=False)
    await browser.init()
    
    # Simple navigation
    await browser.navigate("https://www.example.com")
    
    # Navigation with wait for specific element
    await browser.navigate("https://www.github.com")
    await browser.wait_for_selector("input[name='q']")
    
    # Navigation with network idle wait
    await browser.navigate("https://www.example.com")
    await browser.wait_for_network_idle()
    
    await browser.close()

asyncio.run(navigate_example())
```

### Handling Page Load States

Modern web applications often load content dynamically. Daur AI provides multiple strategies to ensure pages are fully loaded before interaction.

```python
async def wait_for_page_load():
    await browser.navigate("https://dynamic-website.com")
    
    # Wait for specific element
    await browser.wait_for_selector("#content-loaded")
    
    # Wait for network to be idle
    await browser.wait_for_network_idle(timeout=10000)
    
    # Wait for JavaScript to complete
    await browser.wait_for_function("document.readyState === 'complete'")
    
    # Custom wait condition
    await browser.wait_for_function(
        "document.querySelectorAll('.item').length >= 10"
    )
```

### Multi-Page Navigation

When automating workflows that span multiple pages, proper navigation management is essential.

```python
async def multi_page_workflow():
    browser = BrowserAutomation(headless=False)
    await browser.init()
    
    # Navigate through multiple pages
    pages = [
        "https://example.com/page1",
        "https://example.com/page2",
        "https://example.com/page3"
    ]
    
    results = []
    for url in pages:
        await browser.navigate(url)
        await browser.wait_for_network_idle()
        
        # Extract data from each page
        data = await browser.get_page_content()
        results.append(data)
        
        # Optional delay between pages
        await asyncio.sleep(1)
    
    await browser.close()
    return results
```

---

## Element Interaction

### Finding Elements

Daur AI supports multiple methods to locate elements on a page, providing flexibility for different scenarios.

```python
async def find_elements_examples():
    # Find by CSS selector
    button = await browser.find_element("button.submit")
    
    # Find by text content
    link = await browser.find_element("text=Click here")
    
    # Find by ID
    input_field = await browser.find_element("#username")
    
    # Find by XPath
    element = await browser.find_element("//div[@class='container']//button")
    
    # Find with timeout
    element = await browser.find_element("button", timeout=10000)
```

### Clicking Elements

Clicking is one of the most common interactions in web automation. Daur AI provides robust clicking that handles various edge cases.

```python
async def clicking_examples():
    # Simple click
    await browser.click("button#submit")
    
    # Click with wait
    await browser.click("a.nav-link")
    await browser.wait_for_network_idle()
    
    # Double click
    await browser.double_click("div.item")
    
    # Right click
    await browser.right_click("div.context-menu-trigger")
    
    # Click at specific coordinates
    await browser.click_at_position(100, 200)
```

### Typing Text

Text input is fundamental to form automation and search functionality.

```python
async def typing_examples():
    # Type in input field
    await browser.type_text("input#search", "automation")
    
    # Clear and type
    await browser.clear_and_type("input#email", "user@example.com")
    
    # Type with delay (more human-like)
    await browser.type_text("textarea", "Long text content", delay=100)
    
    # Press Enter after typing
    await browser.type_text("input#search", "query")
    await browser.press_key("Enter")
```

### Selecting Options

Dropdown menus and select elements require special handling.

```python
async def select_examples():
    # Select by value
    await browser.select_option("select#country", value="us")
    
    # Select by label
    await browser.select_option("select#size", label="Large")
    
    # Select by index
    await browser.select_option("select#quantity", index=2)
    
    # Multiple selection
    await browser.select_option(
        "select#colors",
        values=["red", "blue", "green"]
    )
```

---

## Form Automation

### Simple Form Submission

Automating form submission is a common task in web automation, from login forms to data entry.

```python
async def submit_simple_form():
    browser = BrowserAutomation(headless=False)
    await browser.init()
    
    # Navigate to form page
    await browser.navigate("https://example.com/contact")
    
    # Fill form fields
    await browser.type_text("input#name", "John Doe")
    await browser.type_text("input#email", "john@example.com")
    await browser.type_text("textarea#message", "This is a test message")
    
    # Select from dropdown
    await browser.select_option("select#subject", label="General Inquiry")
    
    # Check checkbox
    await browser.click("input#agree-terms")
    
    # Submit form
    await browser.click("button[type='submit']")
    
    # Wait for success message
    await browser.wait_for_selector(".success-message")
    
    await browser.close()

asyncio.run(submit_simple_form())
```

### Complex Form Handling

Real-world forms often have validation, dynamic fields, and multi-step processes.

```python
async def handle_complex_form():
    await browser.navigate("https://example.com/registration")
    
    # Step 1: Personal Information
    await browser.type_text("input#first-name", "John")
    await browser.type_text("input#last-name", "Doe")
    await browser.type_text("input#email", "john.doe@example.com")
    
    # Handle date picker
    await browser.click("input#birthdate")
    await browser.click("button[aria-label='Previous month']")
    await browser.click("button[aria-label='15']")
    
    # Click Next
    await browser.click("button.next-step")
    await browser.wait_for_selector(".step-2")
    
    # Step 2: Address Information
    await browser.type_text("input#address", "123 Main St")
    await browser.type_text("input#city", "New York")
    await browser.select_option("select#state", value="NY")
    await browser.type_text("input#zip", "10001")
    
    # Click Next
    await browser.click("button.next-step")
    await browser.wait_for_selector(".step-3")
    
    # Step 3: Review and Submit
    await browser.click("input#confirm")
    await browser.click("button.submit")
    
    # Wait for confirmation
    await browser.wait_for_selector(".confirmation-page")
```

### File Upload

Handling file uploads requires special consideration for security and browser restrictions.

```python
async def upload_file_example():
    # Navigate to upload page
    await browser.navigate("https://example.com/upload")
    
    # Set file input
    file_path = "/path/to/document.pdf"
    await browser.set_input_files("input[type='file']", file_path)
    
    # Upload multiple files
    file_paths = [
        "/path/to/file1.jpg",
        "/path/to/file2.jpg",
        "/path/to/file3.jpg"
    ]
    await browser.set_input_files("input#multi-upload", file_paths)
    
    # Submit upload
    await browser.click("button#upload-submit")
    
    # Wait for upload completion
    await browser.wait_for_selector(".upload-complete")
```

---

## Data Extraction

### Extracting Text Content

Web scraping often involves extracting text from specific elements or entire pages.

```python
async def extract_text_examples():
    await browser.navigate("https://news.example.com")
    
    # Extract single element text
    title = await browser.get_text("h1.article-title")
    print(f"Title: {title}")
    
    # Extract multiple elements
    headlines = await browser.get_all_text(".headline")
    for headline in headlines:
        print(f"- {headline}")
    
    # Extract with structure
    articles = await browser.evaluate("""
        () => {
            return Array.from(document.querySelectorAll('.article')).map(article => ({
                title: article.querySelector('h2').textContent,
                author: article.querySelector('.author').textContent,
                date: article.querySelector('.date').textContent,
                summary: article.querySelector('.summary').textContent
            }));
        }
    """)
    
    return articles
```

### Extracting Attributes

Sometimes you need to extract element attributes like URLs, IDs, or data attributes.

```python
async def extract_attributes():
    # Extract href from links
    links = await browser.evaluate("""
        () => Array.from(document.querySelectorAll('a'))
            .map(a => a.href)
    """)
    
    # Extract image sources
    images = await browser.evaluate("""
        () => Array.from(document.querySelectorAll('img'))
            .map(img => ({
                src: img.src,
                alt: img.alt
            }))
    """)
    
    # Extract data attributes
    items = await browser.evaluate("""
        () => Array.from(document.querySelectorAll('[data-id]'))
            .map(el => ({
                id: el.dataset.id,
                name: el.dataset.name,
                price: el.dataset.price
            }))
    """)
    
    return {"links": links, "images": images, "items": items}
```

### Scraping Tables

Tables are a common data structure on web pages that require special handling for extraction.

```python
async def scrape_table():
    await browser.navigate("https://example.com/data-table")
    
    # Extract table data
    table_data = await browser.evaluate("""
        () => {
            const table = document.querySelector('table');
            const headers = Array.from(table.querySelectorAll('th'))
                .map(th => th.textContent.trim());
            
            const rows = Array.from(table.querySelectorAll('tbody tr'))
                .map(row => {
                    const cells = Array.from(row.querySelectorAll('td'))
                        .map(td => td.textContent.trim());
                    
                    const rowData = {};
                    headers.forEach((header, index) => {
                        rowData[header] = cells[index];
                    });
                    
                    return rowData;
                });
            
            return rows;
        }
    """)
    
    return table_data
```

---

## Authentication Handling

### Login Automation

Automating login processes requires careful handling of credentials and session management.

```python
async def login_example():
    browser = BrowserAutomation(headless=False)
    await browser.init()
    
    # Navigate to login page
    await browser.navigate("https://example.com/login")
    
    # Enter credentials
    await browser.type_text("input#username", "your_username")
    await browser.type_text("input#password", "your_password")
    
    # Handle remember me checkbox
    await browser.click("input#remember-me")
    
    # Submit login form
    await browser.click("button[type='submit']")
    
    # Wait for redirect to dashboard
    await browser.wait_for_selector(".dashboard")
    
    # Verify login success
    user_name = await browser.get_text(".user-profile .name")
    print(f"Logged in as: {user_name}")
    
    return browser  # Return browser with active session
```

### Session Persistence

Maintaining sessions across multiple automation runs improves efficiency and reduces login frequency.

```python
async def save_and_load_session():
    # Save session
    browser = BrowserAutomation(headless=False)
    await browser.init()
    
    # Login
    await login_example()
    
    # Save cookies
    cookies = await browser.get_cookies()
    with open("session_cookies.json", "w") as f:
        json.dump(cookies, f)
    
    await browser.close()
    
    # Load session in new browser instance
    browser_new = BrowserAutomation(headless=False)
    await browser_new.init()
    
    # Load cookies
    with open("session_cookies.json") as f:
        cookies = json.load(f)
    
    await browser_new.set_cookies(cookies)
    
    # Navigate to protected page
    await browser_new.navigate("https://example.com/dashboard")
    # Should be logged in without entering credentials
```

---

## Advanced Techniques

### Handling Dynamic Content

Modern web applications load content dynamically using JavaScript, requiring special techniques to ensure data is available before extraction.

```python
async def handle_infinite_scroll():
    await browser.navigate("https://example.com/feed")
    
    # Scroll to load more content
    previous_height = 0
    while True:
        # Scroll to bottom
        current_height = await browser.evaluate("document.body.scrollHeight")
        await browser.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        # Wait for new content to load
        await asyncio.sleep(2)
        
        # Check if new content loaded
        new_height = await browser.evaluate("document.body.scrollHeight")
        if new_height == current_height:
            break  # No more content
        
        current_height = new_height
    
    # Extract all loaded content
    items = await browser.get_all_text(".feed-item")
    return items
```

### Working with Iframes

Iframes create separate document contexts that require special handling.

```python
async def handle_iframe():
    await browser.navigate("https://example.com/page-with-iframe")
    
    # Switch to iframe
    iframe = await browser.find_element("iframe#content-frame")
    frame = await iframe.content_frame()
    
    # Interact with elements inside iframe
    await frame.click("button.iframe-button")
    text = await frame.get_text("div.iframe-content")
    
    # Switch back to main frame
    # (automatically handled when using browser methods)
```

### Handling Popups and Dialogs

Popups, alerts, and confirmation dialogs require event listeners to handle properly.

```python
async def handle_dialogs():
    # Setup dialog handler
    browser.page.on("dialog", lambda dialog: dialog.accept())
    
    # Click button that triggers alert
    await browser.click("button#show-alert")
    # Alert will be automatically accepted
    
    # Handle with custom logic
    async def handle_confirm(dialog):
        print(f"Dialog message: {dialog.message}")
        if "confirm" in dialog.message.lower():
            await dialog.accept()
        else:
            await dialog.dismiss()
    
    browser.page.on("dialog", handle_confirm)
```

---

## Best Practices

### Error Handling

Robust error handling ensures your automation continues working even when unexpected issues occur.

```python
async def robust_automation():
    browser = None
    try:
        browser = BrowserAutomation(headless=False)
        await browser.init()
        
        await browser.navigate("https://example.com")
        
        # Try to find element with fallback
        try:
            await browser.click("button#primary")
        except Exception:
            # Fallback to alternative selector
            await browser.click("button.submit")
        
        # Extract data with error handling
        try:
            data = await browser.get_text(".content")
        except Exception as e:
            logger.error(f"Failed to extract data: {e}")
            data = None
        
        return data
        
    except Exception as e:
        logger.error(f"Automation failed: {e}")
        raise
    finally:
        if browser:
            await browser.close()
```

### Rate Limiting

Respect website resources by implementing appropriate delays between requests.

```python
async def respectful_scraping():
    urls = ["https://example.com/page1", "https://example.com/page2", ...]
    
    results = []
    for url in urls:
        await browser.navigate(url)
        data = await extract_page_data()
        results.append(data)
        
        # Delay between requests (1-3 seconds)
        await asyncio.sleep(random.uniform(1, 3))
    
    return results
```

---

## Complete Examples

### E-commerce Product Scraper

```python
async def scrape_products():
    """Complete example: Scrape product information from e-commerce site."""
    browser = BrowserAutomation(headless=True)
    await browser.init()
    
    try:
        # Navigate to category page
        await browser.navigate("https://example-shop.com/electronics")
        await browser.wait_for_network_idle()
        
        # Extract all products
        products = await browser.evaluate("""
            () => {
                return Array.from(document.querySelectorAll('.product-card')).map(card => ({
                    name: card.querySelector('.product-name').textContent.trim(),
                    price: card.querySelector('.price').textContent.trim(),
                    rating: card.querySelector('.rating').textContent.trim(),
                    url: card.querySelector('a').href,
                    image: card.querySelector('img').src
                }));
            }
        """)
        
        # Visit each product page for detailed info
        detailed_products = []
        for product in products[:5]:  # Limit to first 5 for example
            await browser.navigate(product['url'])
            await browser.wait_for_selector('.product-details')
            
            details = await browser.evaluate("""
                () => ({
                    description: document.querySelector('.description').textContent.trim(),
                    specs: Array.from(document.querySelectorAll('.spec-item'))
                        .map(item => ({
                            name: item.querySelector('.spec-name').textContent.trim(),
                            value: item.querySelector('.spec-value').textContent.trim()
                        })),
                    reviews_count: document.querySelector('.reviews-count').textContent.trim()
                })
            """)
            
            detailed_products.append({**product, **details})
            await asyncio.sleep(1)  # Rate limiting
        
        return detailed_products
        
    finally:
        await browser.close()

# Run the scraper
products = asyncio.run(scrape_products())
print(f"Scraped {len(products)} products")
```

---

**Last Updated**: 2025-11-12  
**Version**: 2.0  
**Author**: Manus AI

