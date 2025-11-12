# Troubleshooting Guide

**Version**: 2.0  
**Last Updated**: 2025-11-12

---

## Introduction

This comprehensive troubleshooting guide helps you diagnose and resolve common issues with Daur AI. Issues are organized by category with clear symptoms, causes, and solutions.

---

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Display and GUI Problems](#display-and-gui-problems)
3. [Browser Automation Issues](#browser-automation-issues)
4. [Vision and OCR Problems](#vision-and-ocr-problems)
5. [Input Control Issues](#input-control-issues)
6. [Performance Problems](#performance-problems)
7. [API and Integration Issues](#api-and-integration-issues)
8. [Logging and Debugging](#logging-and-debugging)

---

## Installation Issues

### Problem: ModuleNotFoundError

**Symptoms**: Import errors when trying to use Daur AI modules

```
ModuleNotFoundError: No module named 'src.agent.core'
```

**Causes**:
- Dependencies not installed
- Wrong Python version
- Not running from project directory

**Solutions**:

```bash
# Verify Python version (3.8+ required)
python3 --version

# Reinstall dependencies
pip3 install -r requirements.txt

# Verify installation
python3 -c "import src.agent.core; print('OK')"

# Run from project root directory
cd /path/to/Daur-AI-v1
python3 your_script.py
```

### Problem: Playwright Installation Failed

**Symptoms**: Browser automation fails with "Executable doesn't exist"

**Causes**:
- Playwright browsers not installed
- Permission issues

**Solutions**:

```bash
# Install Playwright browsers
python3 -m playwright install chromium

# If permission denied, use --user flag
python3 -m playwright install --user chromium

# Verify installation
python3 -m playwright install --help
```

### Problem: Tesseract OCR Not Found

**Symptoms**: OCR fails with "tesseract is not installed"

**Causes**:
- Tesseract not installed
- Not in system PATH

**Solutions**:

```bash
# Install Tesseract
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng

# Verify installation
tesseract --version

# Install additional languages if needed
sudo apt-get install tesseract-ocr-rus  # Russian
sudo apt-get install tesseract-ocr-spa  # Spanish
```

---

## Display and GUI Problems

### Problem: Cannot Open Display

**Symptoms**: Error when running GUI automation

```
tkinter.TclError: couldn't connect to display ":0"
```

**Causes**:
- No X11 display available
- Running in headless environment
- DISPLAY variable not set

**Solutions**:

```bash
# Option 1: Use Xvfb (virtual display)
sudo apt-get install xvfb
xvfb-run python3 your_script.py

# Option 2: Set DISPLAY variable
export DISPLAY=:0
python3 your_script.py

# Option 3: Use headless mode in code
browser = BrowserAutomation(headless=True)
```

### Problem: Screen Capture Returns Black Screen

**Symptoms**: Screenshots are completely black

**Causes**:
- Compositor issues
- GPU driver problems
- Wrong display server

**Solutions**:

```bash
# Check display server
echo $XDG_SESSION_TYPE  # Should show x11 or wayland

# For Wayland, switch to X11 or use different capture method
# Edit /etc/gdm3/custom.conf and uncomment:
# WaylandEnable=false

# Alternative: Use scrot for screenshots
sudo apt-get install scrot
scrot screenshot.png
```

### Problem: Mouse/Keyboard Control Not Working

**Symptoms**: Input commands have no effect

**Causes**:
- Insufficient permissions
- X11 extensions not installed
- Security restrictions

**Solutions**:

```bash
# Install required X11 libraries
sudo apt-get install libx11-dev libxtst-dev

# Check if user has input permissions
groups $USER  # Should include 'input'

# Add user to input group if needed
sudo usermod -a -G input $USER
# Log out and log back in

# Test with simple script
python3 -c "from pynput.mouse import Controller; m = Controller(); print(m.position)"
```

---

## Browser Automation Issues

### Problem: Browser Fails to Launch

**Symptoms**: Browser automation throws timeout or connection errors

**Causes**:
- Browser binary not found
- Port already in use
- Insufficient resources

**Solutions**:

```python
# Add error handling and logging
import logging
logging.basicConfig(level=logging.DEBUG)

try:
    browser = BrowserAutomation(headless=False)
    await browser.init()
except Exception as e:
    print(f"Browser launch failed: {e}")
    # Check if port is in use
    import subprocess
    subprocess.run(["lsof", "-i", ":9222"])
```

```bash
# Kill existing browser processes
pkill -9 chromium
pkill -9 chrome

# Reinstall browser
python3 -m playwright install --force chromium
```

### Problem: Element Not Found

**Symptoms**: `find_element()` returns None or times out

**Causes**:
- Element not loaded yet
- Wrong selector
- Element in iframe
- Dynamic content

**Solutions**:

```python
# Increase timeout
element = await browser.find_element("button", timeout=30000)

# Wait for page load
await browser.wait_for_network_idle()

# Try multiple selectors
selectors = ["button#submit", "button.submit", "input[type='submit']"]
for selector in selectors:
    element = await browser.find_element(selector)
    if element:
        break

# Check if element is in iframe
iframes = await browser.page.query_selector_all("iframe")
for iframe in iframes:
    frame = await iframe.content_frame()
    element = await frame.query_selector("button")
    if element:
        break
```

### Problem: Click Not Working

**Symptoms**: Element found but click has no effect

**Causes**:
- Element not clickable
- Element covered by another element
- Page not fully loaded

**Solutions**:

```python
# Wait for element to be clickable
await browser.wait_for_selector("button", state="visible")
await asyncio.sleep(0.5)  # Additional wait

# Scroll element into view
await browser.evaluate("""
    document.querySelector('button').scrollIntoView()
""")

# Force click using JavaScript
await browser.evaluate("""
    document.querySelector('button').click()
""")

# Try clicking at element center
element = await browser.find_element("button")
box = await element.bounding_box()
await browser.page.mouse.click(
    box['x'] + box['width'] / 2,
    box['y'] + box['height'] / 2
)
```

---

## Vision and OCR Problems

### Problem: OCR Returns Gibberish

**Symptoms**: Extracted text is incorrect or unreadable

**Causes**:
- Low image quality
- Wrong language setting
- Poor contrast
- Small text size

**Solutions**:

```python
# Preprocess image for better OCR
from PIL import Image, ImageEnhance, ImageFilter

def enhance_for_ocr(image_path):
    img = Image.open(image_path)
    
    # Convert to grayscale
    img = img.convert('L')
    
    # Increase size (better for small text)
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    
    # Apply threshold
    img = img.point(lambda x: 0 if x < 128 else 255)
    
    return img

# Use enhanced image
enhanced = enhance_for_ocr("screenshot.png")
text = screen_rec.extract_text_from_image(enhanced)
```

```python
# Configure Tesseract for better accuracy
import pytesseract

custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
text = pytesseract.image_to_string(image, config=custom_config)
```

### Problem: Template Matching Fails

**Symptoms**: `find_element_by_image()` doesn't find expected elements

**Causes**:
- Threshold too high
- Image scaling differences
- Color variations
- Template doesn't match exactly

**Solutions**:

```python
# Lower threshold
matches = find_template_on_screen(template, threshold=0.7)

# Try grayscale matching
import cv2
screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
matches = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)

# Try multiple scales
scales = [0.8, 0.9, 1.0, 1.1, 1.2]
for scale in scales:
    resized_template = cv2.resize(template, None, fx=scale, fy=scale)
    matches = find_template_on_screen(resized_template, threshold=0.75)
    if matches:
        break

# Use feature matching instead
from src.vision.feature_matching import find_by_features
matches = find_by_features(screen, template)
```

---

## Input Control Issues

### Problem: Keyboard Input Goes to Wrong Window

**Symptoms**: Text appears in different application

**Causes**:
- Window focus lost
- Timing issues
- Window manager interference

**Solutions**:

```python
# Ensure window is focused
import pygetwindow as gw

window = gw.getWindowsWithTitle("Target App")[0]
window.activate()
time.sleep(0.5)  # Wait for focus

# Verify focus before typing
active_window = gw.getActiveWindow()
if active_window.title != "Target App":
    raise Exception("Wrong window focused")

input_ctrl.type_text("Your text here")
```

### Problem: Mouse Clicks Miss Target

**Symptoms**: Clicks land in wrong location

**Causes**:
- Screen scaling/DPI issues
- Coordinate system mismatch
- Window position changed

**Solutions**:

```python
# Account for DPI scaling
import ctypes
ctypes.windll.shcore.SetProcessDpiAwareness(2)

# Get accurate window position
window = gw.getWindowsWithTitle("App")[0]
window_x, window_y = window.left, window.top

# Click relative to window
relative_x, relative_y = 100, 50
absolute_x = window_x + relative_x
absolute_y = window_y + relative_y
input_ctrl.click_at(absolute_x, absolute_y)

# Verify click position
print(f"Clicking at: {absolute_x}, {absolute_y}")
```

---

## Performance Problems

### Problem: Automation Running Slowly

**Symptoms**: Operations take much longer than expected

**Causes**:
- Excessive delays
- Inefficient element finding
- Too many screenshots
- Network latency

**Solutions**:

```python
# Reduce unnecessary delays
# Bad
time.sleep(5)  # Fixed delay

# Good
await browser.wait_for_selector("element", timeout=10000)  # Wait only as needed

# Cache element lookups
elements_cache = {}

def find_element_cached(selector):
    if selector not in elements_cache:
        elements_cache[selector] = browser.find_element(selector)
    return elements_cache[selector]

# Optimize screenshot frequency
# Only capture when needed
if need_to_verify:
    screenshot = screen_capture.capture_screen()

# Use headless mode for better performance
browser = BrowserAutomation(headless=True)
```

### Problem: High Memory Usage

**Symptoms**: Memory consumption grows over time

**Causes**:
- Memory leaks
- Screenshots not released
- Browser instances not closed

**Solutions**:

```python
# Properly close resources
try:
    browser = BrowserAutomation()
    await browser.init()
    # ... operations ...
finally:
    await browser.close()

# Clear screenshot cache
screen_capture.clear_cache()

# Monitor memory usage
import psutil
process = psutil.Process()
print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")

# Restart browser periodically
operation_count = 0
for task in tasks:
    if operation_count % 100 == 0:
        await browser.close()
        await browser.init()
    
    # Process task
    operation_count += 1
```

---

## API and Integration Issues

### Problem: OpenAI API Errors

**Symptoms**: AI features fail with API errors

**Causes**:
- Invalid API key
- Rate limiting
- Quota exceeded
- Network issues

**Solutions**:

```python
# Verify API key
import openai
openai.api_key = "your-api-key"

try:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "test"}]
    )
    print("API key valid")
except openai.error.AuthenticationError:
    print("Invalid API key")
except openai.error.RateLimitError:
    print("Rate limit exceeded, wait and retry")
except openai.error.APIError as e:
    print(f"API error: {e}")

# Implement retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def call_openai_api():
    return openai.ChatCompletion.create(...)
```

---

## Logging and Debugging

### Enable Debug Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daur_ai_debug.log'),
        logging.StreamHandler()
    ]
)

# Get logger
logger = logging.getLogger(__name__)

# Log operations
logger.debug("Starting automation")
logger.info("Processing item 1")
logger.warning("Retrying operation")
logger.error("Operation failed")
```

### Capture Screenshots on Failure

```python
def automation_with_error_capture():
    try:
        # Automation operations
        pass
    except Exception as e:
        # Capture screenshot on error
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"error_{timestamp}.png"
        screen_capture.save_screenshot(screenshot_path)
        
        logger.error(f"Error occurred: {e}")
        logger.error(f"Screenshot saved to: {screenshot_path}")
        raise
```

### Common Debug Commands

```bash
# Check running processes
ps aux | grep python
ps aux | grep chromium

# Check open ports
sudo lsof -i -P -n | grep LISTEN

# Monitor system resources
top
htop

# Check logs
tail -f logs/daur_ai.log
journalctl -f

# Test display
xdpyinfo
echo $DISPLAY

# Test input devices
xinput list
```

---

## Getting Additional Help

If your issue is not covered in this guide:

1. **Check Logs**: Review log files in `logs/` directory for detailed error messages

2. **Search Issues**: Check GitHub issues for similar problems: https://github.com/daurfinance/Daur-AI-v1/issues

3. **Create Issue**: If problem persists, create a detailed issue report including:
   - Operating system and version
   - Python version
   - Full error message and stack trace
   - Steps to reproduce
   - Relevant code snippet
   - Log files

4. **Community Support**: Join community discussions for help from other users

---

**Last Updated**: 2025-11-12  
**Version**: 2.0  
**Author**: Manus AI

