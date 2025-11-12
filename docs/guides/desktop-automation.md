# Desktop Automation Guide

**Version**: 2.0  
**Last Updated**: 2025-11-12  
**Difficulty**: Intermediate

---

## Introduction

Desktop automation enables you to control any application on your computer, from native applications to legacy software that lacks APIs. Using computer vision and input control, Daur AI can interact with desktop applications just as a human would, making it possible to automate virtually any desktop workflow.

This guide covers the essential techniques for desktop automation including screen analysis, mouse and keyboard control, window management, and building robust automation workflows that work reliably across different environments.

---

## Table of Contents

1. [Understanding Desktop Automation](#understanding-desktop-automation)
2. [Screen Analysis](#screen-analysis)
3. [Mouse Control](#mouse-control)
4. [Keyboard Control](#keyboard-control)
5. [Window Management](#window-management)
6. [Image Recognition](#image-recognition)
7. [OCR and Text Recognition](#ocr-and-text-recognition)
8. [Building Workflows](#building-workflows)
9. [Complete Examples](#complete-examples)

---

## Understanding Desktop Automation

### How It Works

Desktop automation in Daur AI operates through three primary mechanisms that work together to provide comprehensive control over desktop applications.

**Computer Vision** analyzes the screen to locate elements, read text, and understand the current state of applications. This is accomplished through OCR (Optical Character Recognition) for text extraction and image matching for visual element detection.

**Input Control** simulates human interaction through mouse movements, clicks, and keyboard input. The system can precisely control cursor position, perform various types of clicks, and type text with realistic timing.

**Window Management** handles application windows, allowing the automation to switch between applications, resize windows, and manage multiple applications simultaneously.

### When to Use Desktop Automation

Desktop automation is ideal for several scenarios where other automation approaches are not feasible. Legacy applications that lack modern APIs or command-line interfaces can only be automated through UI interaction. Applications with complex GUIs that require visual verification benefit from computer vision capabilities. Workflows that span multiple applications can be unified through desktop automation.

---

## Screen Analysis

### Capturing Screenshots

Screen capture is the foundation of desktop automation, providing the visual information needed for analysis and decision-making.

```python
from src.vision.optimized_screen_capture import OptimizedScreenCapture

# Initialize screen capture
screen_capture = OptimizedScreenCapture()

# Capture full screen
screenshot = screen_capture.capture_screen()
print(f"Captured screen: {screenshot.shape}")

# Capture specific region
region = (100, 100, 500, 400)  # x, y, width, height
region_screenshot = screen_capture.capture_region(region)

# Save screenshot
screen_capture.save_screenshot(screenshot, "screen.png")
```

### Analyzing Screen Content

Once you have captured the screen, you can analyze it to understand what is displayed and make decisions about next actions.

```python
from src.vision.screen_analyzer import ScreenAnalyzer

# Initialize analyzer
analyzer = ScreenAnalyzer()

# Analyze full screen
analysis = analyzer.analyze_screen()

print(f"Detected {len(analysis['elements'])} elements")
print(f"Found text: {analysis['text']}")
print(f"Detected buttons: {analysis['buttons']}")
print(f"Detected input fields: {analysis['input_fields']}")

# Analyze specific region
region_analysis = analyzer.analyze_region((100, 100, 500, 400))
```

### Finding Elements on Screen

Locating specific elements on the screen is crucial for reliable automation. Daur AI provides multiple methods to find elements based on different criteria.

```python
# Find element by text
element = analyzer.find_element_by_text("Submit")
if element:
    print(f"Found 'Submit' at position: {element['position']}")

# Find element by image
template_image = "button_template.png"
matches = analyzer.find_element_by_image(template_image, threshold=0.8)
for match in matches:
    print(f"Found match at: {match['position']} with confidence: {match['confidence']}")

# Find element by color
red_elements = analyzer.find_elements_by_color((255, 0, 0), tolerance=30)
```

---

## Mouse Control

### Basic Mouse Operations

Mouse control is essential for interacting with desktop applications. Daur AI provides precise mouse control with various types of clicks and movements.

```python
from src.input.input_controller import InputController

# Initialize input controller
input_ctrl = InputController()

# Move mouse to position
input_ctrl.move_mouse(500, 300)

# Click at current position
input_ctrl.click()

# Click at specific position
input_ctrl.click_at(500, 300)

# Double click
input_ctrl.double_click_at(500, 300)

# Right click
input_ctrl.right_click_at(500, 300)

# Drag and drop
input_ctrl.drag_and_drop(
    start_x=100, start_y=100,
    end_x=500, end_y=300
)
```

### Smooth Mouse Movement

Natural mouse movement appears more human-like and can help avoid detection in applications with anti-automation measures.

```python
# Move mouse smoothly (human-like)
input_ctrl.move_mouse_smooth(
    target_x=800,
    target_y=600,
    duration=0.5  # seconds
)

# Move with random variation
input_ctrl.move_mouse_natural(
    target_x=800,
    target_y=600,
    variation=10  # pixels of random variation
)
```

### Advanced Clicking

Different applications may require different types of mouse interactions beyond simple clicks.

```python
# Click and hold
input_ctrl.mouse_down(500, 300)
time.sleep(1)
input_ctrl.mouse_up()

# Scroll
input_ctrl.scroll(amount=5, direction="down")
input_ctrl.scroll(amount=3, direction="up")

# Horizontal scroll
input_ctrl.scroll_horizontal(amount=5, direction="right")
```

---

## Keyboard Control

### Typing Text

Keyboard automation allows you to input text into applications, fill forms, and execute keyboard shortcuts.

```python
# Type text
input_ctrl.type_text("Hello, World!")

# Type with delay (more human-like)
input_ctrl.type_text("Slower typing", delay=0.1)

# Type with random delay
input_ctrl.type_text_natural("Natural typing", min_delay=0.05, max_delay=0.15)

# Clear existing text and type new
input_ctrl.clear_field()
input_ctrl.type_text("New text")
```

### Keyboard Shortcuts

Many desktop applications rely heavily on keyboard shortcuts for efficient operation.

```python
# Press single key
input_ctrl.press_key("Enter")

# Press key combination
input_ctrl.press_keys(["ctrl", "c"])  # Copy
input_ctrl.press_keys(["ctrl", "v"])  # Paste
input_ctrl.press_keys(["ctrl", "s"])  # Save

# Press multiple shortcuts in sequence
input_ctrl.press_keys(["ctrl", "a"])  # Select all
input_ctrl.press_keys(["ctrl", "c"])  # Copy
input_ctrl.press_keys(["alt", "tab"])  # Switch window
input_ctrl.press_keys(["ctrl", "v"])  # Paste

# Hold key while performing action
input_ctrl.key_down("shift")
input_ctrl.click_at(100, 100)
input_ctrl.click_at(500, 500)  # Shift-click for range selection
input_ctrl.key_up("shift")
```

### Special Keys

Handling special keys like function keys, arrow keys, and modifier keys.

```python
# Function keys
input_ctrl.press_key("F5")  # Refresh
input_ctrl.press_key("F11")  # Fullscreen

# Arrow keys
input_ctrl.press_key("Up")
input_ctrl.press_key("Down")
input_ctrl.press_key("Left")
input_ctrl.press_key("Right")

# Navigation keys
input_ctrl.press_key("Home")
input_ctrl.press_key("End")
input_ctrl.press_key("PageUp")
input_ctrl.press_key("PageDown")

# Other special keys
input_ctrl.press_key("Tab")
input_ctrl.press_key("Escape")
input_ctrl.press_key("Delete")
input_ctrl.press_key("Backspace")
```

---

## Window Management

### Managing Application Windows

Controlling application windows is essential for complex workflows that involve multiple applications.

```python
import pygetwindow as gw

# List all windows
windows = gw.getAllWindows()
for window in windows:
    print(f"{window.title}: {window.size}")

# Find specific window
notepad = gw.getWindowsWithTitle("Notepad")[0]

# Activate window (bring to front)
notepad.activate()

# Resize window
notepad.resizeTo(800, 600)

# Move window
notepad.moveTo(100, 100)

# Maximize/minimize
notepad.maximize()
notepad.minimize()
notepad.restore()

# Close window
notepad.close()
```

### Multi-Application Workflows

Automating workflows that span multiple applications requires careful window management.

```python
async def multi_app_workflow():
    """Example: Copy data from Excel to Email."""
    
    # Open Excel
    excel = gw.getWindowsWithTitle("Excel")[0]
    excel.activate()
    time.sleep(0.5)
    
    # Select and copy data
    input_ctrl.click_at(200, 200)  # Click cell
    input_ctrl.press_keys(["ctrl", "c"])  # Copy
    
    # Switch to email application
    email = gw.getWindowsWithTitle("Mail")[0]
    email.activate()
    time.sleep(0.5)
    
    # Click compose button
    input_ctrl.click_at(100, 100)
    time.sleep(1)
    
    # Paste data
    input_ctrl.press_keys(["ctrl", "v"])
    
    # Type additional content
    input_ctrl.type_text("Please review the attached data.")
```

---

## Image Recognition

### Template Matching

Image recognition allows you to find UI elements by their visual appearance, which is especially useful for applications with custom controls.

```python
from src.vision.cv2_utils import find_template_on_screen

# Find button by template image
template = "button_template.png"
matches = find_template_on_screen(template, threshold=0.8)

if matches:
    best_match = matches[0]
    print(f"Found button at: {best_match['position']}")
    
    # Click the button
    x, y = best_match['center']
    input_ctrl.click_at(x, y)
```

### Multiple Template Matching

Finding all instances of a UI element on the screen.

```python
# Find all checkboxes
checkbox_template = "checkbox.png"
checkboxes = find_template_on_screen(
    checkbox_template,
    threshold=0.85,
    find_all=True
)

print(f"Found {len(checkboxes)} checkboxes")

# Check all checkboxes
for checkbox in checkboxes:
    x, y = checkbox['center']
    input_ctrl.click_at(x, y)
    time.sleep(0.2)
```

### Adaptive Template Matching

Handling variations in UI appearance due to themes, scaling, or different states.

```python
# Try multiple template variations
templates = [
    "button_normal.png",
    "button_hover.png",
    "button_pressed.png"
]

button_found = False
for template in templates:
    matches = find_template_on_screen(template, threshold=0.75)
    if matches:
        x, y = matches[0]['center']
        input_ctrl.click_at(x, y)
        button_found = True
        break

if not button_found:
    print("Button not found with any template")
```

---

## OCR and Text Recognition

### Extracting Text from Screen

OCR (Optical Character Recognition) enables reading text from the screen, which is essential for data extraction and verification.

```python
from src.vision.screen_recognition import ScreenRecognition

# Initialize screen recognition
screen_rec = ScreenRecognition()

# Extract all text from screen
text_data = screen_rec.extract_text_from_screen()
print(f"Extracted text: {text_data}")

# Extract text from specific region
region = (100, 100, 500, 400)
region_text = screen_rec.extract_text_from_region(region)
print(f"Region text: {region_text}")

# Find text on screen
search_text = "Submit"
positions = screen_rec.find_text_on_screen(search_text)
if positions:
    print(f"Found '{search_text}' at: {positions}")
```

### Advanced OCR Techniques

Improving OCR accuracy through preprocessing and configuration.

```python
# Configure OCR for better accuracy
ocr_config = {
    "language": "eng",
    "psm": 6,  # Assume uniform block of text
    "oem": 3   # Default OCR Engine Mode
}

screen_rec = ScreenRecognition(ocr_config=ocr_config)

# Preprocess image for better OCR
from PIL import Image, ImageEnhance

def preprocess_for_ocr(image_path):
    """Enhance image for better OCR results."""
    img = Image.open(image_path)
    
    # Convert to grayscale
    img = img.convert('L')
    
    # Increase contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    
    # Increase sharpness
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)
    
    return img

# Use preprocessed image for OCR
preprocessed = preprocess_for_ocr("screenshot.png")
text = screen_rec.extract_text_from_image(preprocessed)
```

---

## Building Workflows

### Creating Robust Workflows

Production-ready desktop automation requires error handling, verification, and retry logic.

```python
class DesktopWorkflow:
    """Base class for desktop automation workflows."""
    
    def __init__(self):
        self.input_ctrl = InputController()
        self.screen_rec = ScreenRecognition()
        self.max_retries = 3
    
    def wait_for_element(self, element_text, timeout=10):
        """Wait for element to appear on screen."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            positions = self.screen_rec.find_text_on_screen(element_text)
            if positions:
                return positions[0]
            time.sleep(0.5)
        raise TimeoutError(f"Element '{element_text}' not found")
    
    def click_element(self, element_text, timeout=10):
        """Find and click element by text."""
        position = self.wait_for_element(element_text, timeout)
        self.input_ctrl.click_at(position['x'], position['y'])
        time.sleep(0.5)
    
    def verify_element_present(self, element_text):
        """Verify element is present on screen."""
        positions = self.screen_rec.find_text_on_screen(element_text)
        return len(positions) > 0
    
    def retry_on_failure(self, func, *args, **kwargs):
        """Retry function on failure."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
                time.sleep(2)
```

### Example: Data Entry Workflow

```python
class DataEntryWorkflow(DesktopWorkflow):
    """Automated data entry workflow."""
    
    def enter_customer_data(self, customer_data):
        """Enter customer information into application."""
        
        # Open application
        self.click_element("New Customer")
        self.wait_for_element("Customer Form")
        
        # Fill form fields
        fields = [
            ("Name", customer_data['name']),
            ("Email", customer_data['email']),
            ("Phone", customer_data['phone']),
            ("Address", customer_data['address'])
        ]
        
        for field_name, value in fields:
            # Click field label
            self.click_element(field_name)
            time.sleep(0.2)
            
            # Clear existing value
            self.input_ctrl.press_keys(["ctrl", "a"])
            
            # Type new value
            self.input_ctrl.type_text(value)
            time.sleep(0.2)
        
        # Submit form
        self.click_element("Save")
        
        # Verify success
        if self.verify_element_present("Customer saved successfully"):
            print(f"Successfully saved customer: {customer_data['name']}")
            return True
        else:
            raise Exception("Failed to save customer")

# Usage
workflow = DataEntryWorkflow()
customer = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '555-0123',
    'address': '123 Main St'
}
workflow.enter_customer_data(customer)
```

---

## Complete Examples

### Example 1: Automated Report Generation

```python
async def generate_report_workflow():
    """
    Complete workflow: Generate and email monthly report.
    
    Steps:
    1. Open reporting application
    2. Select date range
    3. Generate report
    4. Export to PDF
    5. Open email client
    6. Attach report and send
    """
    
    input_ctrl = InputController()
    screen_rec = ScreenRecognition()
    
    try:
        # Step 1: Open reporting application
        print("Opening reporting application...")
        report_app = gw.getWindowsWithTitle("Reports")[0]
        report_app.activate()
        time.sleep(1)
        
        # Step 2: Select date range
        print("Setting date range...")
        # Click date range dropdown
        date_dropdown_pos = screen_rec.find_text_on_screen("Date Range")[0]
        input_ctrl.click_at(date_dropdown_pos['x'], date_dropdown_pos['y'])
        time.sleep(0.5)
        
        # Select "Last Month"
        last_month_pos = screen_rec.find_text_on_screen("Last Month")[0]
        input_ctrl.click_at(last_month_pos['x'], last_month_pos['y'])
        
        # Step 3: Generate report
        print("Generating report...")
        generate_btn_pos = screen_rec.find_text_on_screen("Generate")[0]
        input_ctrl.click_at(generate_btn_pos['x'], generate_btn_pos['y'])
        
        # Wait for report to generate
        time.sleep(5)
        
        # Step 4: Export to PDF
        print("Exporting to PDF...")
        input_ctrl.press_keys(["ctrl", "e"])  # Export shortcut
        time.sleep(1)
        
        # Select PDF format
        pdf_option_pos = screen_rec.find_text_on_screen("PDF")[0]
        input_ctrl.click_at(pdf_option_pos['x'], pdf_option_pos['y'])
        
        # Click Export button
        export_btn_pos = screen_rec.find_text_on_screen("Export")[0]
        input_ctrl.click_at(export_btn_pos['x'], export_btn_pos['y'])
        
        # Wait for export
        time.sleep(3)
        
        # Step 5: Open email client
        print("Opening email client...")
        email_app = gw.getWindowsWithTitle("Mail")[0]
        email_app.activate()
        time.sleep(1)
        
        # Compose new email
        input_ctrl.press_keys(["ctrl", "n"])
        time.sleep(1)
        
        # Fill email
        input_ctrl.type_text("manager@company.com")
        input_ctrl.press_key("Tab")
        input_ctrl.type_text("Monthly Report - " + datetime.now().strftime("%B %Y"))
        input_ctrl.press_key("Tab")
        input_ctrl.type_text("Please find attached the monthly report.")
        
        # Attach file
        input_ctrl.press_keys(["ctrl", "shift", "a"])
        time.sleep(1)
        
        # Type file path
        report_path = os.path.expanduser("~/Downloads/report.pdf")
        input_ctrl.type_text(report_path)
        input_ctrl.press_key("Enter")
        time.sleep(1)
        
        # Send email
        input_ctrl.press_keys(["ctrl", "Enter"])
        
        print("Report generated and emailed successfully!")
        return True
        
    except Exception as e:
        print(f"Workflow failed: {e}")
        return False

# Run workflow
asyncio.run(generate_report_workflow())
```

### Example 2: Automated Testing

```python
class ApplicationTester(DesktopWorkflow):
    """Automated testing for desktop application."""
    
    def __init__(self, app_name):
        super().__init__()
        self.app_name = app_name
        self.test_results = []
    
    def test_login(self, username, password):
        """Test login functionality."""
        test_name = "Login Test"
        print(f"Running {test_name}...")
        
        try:
            # Click login button
            self.click_element("Login")
            
            # Enter credentials
            self.input_ctrl.type_text(username)
            self.input_ctrl.press_key("Tab")
            self.input_ctrl.type_text(password)
            self.input_ctrl.press_key("Enter")
            
            # Verify successful login
            time.sleep(2)
            if self.verify_element_present("Welcome"):
                self.test_results.append({
                    "test": test_name,
                    "status": "PASS",
                    "message": "Login successful"
                })
                return True
            else:
                self.test_results.append({
                    "test": test_name,
                    "status": "FAIL",
                    "message": "Welcome message not found"
                })
                return False
                
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "ERROR",
                "message": str(e)
            })
            return False
    
    def test_navigation(self, menu_items):
        """Test navigation menu."""
        test_name = "Navigation Test"
        print(f"Running {test_name}...")
        
        try:
            for item in menu_items:
                self.click_element(item)
                time.sleep(1)
                
                if not self.verify_element_present(item):
                    self.test_results.append({
                        "test": test_name,
                        "status": "FAIL",
                        "message": f"Failed to navigate to {item}"
                    })
                    return False
            
            self.test_results.append({
                "test": test_name,
                "status": "PASS",
                "message": "All navigation items working"
            })
            return True
            
        except Exception as e:
            self.test_results.append({
                "test": test_name,
                "status": "ERROR",
                "message": str(e)
            })
            return False
    
    def generate_test_report(self):
        """Generate test report."""
        print("\n" + "="*50)
        print("TEST REPORT")
        print("="*50)
        
        passed = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        errors = sum(1 for r in self.test_results if r['status'] == 'ERROR')
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        print("\nDetailed Results:")
        
        for result in self.test_results:
            status_symbol = "✓" if result['status'] == "PASS" else "✗"
            print(f"{status_symbol} {result['test']}: {result['status']}")
            print(f"  Message: {result['message']}")
        
        print("="*50)

# Run tests
tester = ApplicationTester("MyApp")
tester.test_login("testuser", "testpass")
tester.test_navigation(["Home", "Settings", "About"])
tester.generate_test_report()
```

---

**Last Updated**: 2025-11-12  
**Version**: 2.0  
**Author**: Manus AI

