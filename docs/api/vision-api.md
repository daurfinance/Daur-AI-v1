# Vision API

The Vision API provides comprehensive screen analysis, OCR, object detection, and visual understanding capabilities that enable Daur AI to "see" and interpret screen content.

## Overview

The `VisionCore` class powers Daur AI's visual perception system, enabling it to read text, detect UI elements, recognize objects, and understand screen layouts across all platforms.

## Class: VisionCore

### Initialization

```python
from src.vision.vision_core import VisionCore

# Basic initialization
vision = VisionCore()

# With custom model configuration
vision = VisionCore(
    ocr_engine="tesseract",
    object_detection_model="yolov8",
    confidence_threshold=0.7
)
```

## Text Recognition (OCR)

### extract_text_from_screen()

Extract all text visible on the screen.

**Signature:**
```python
async def extract_text_from_screen(
    self,
    region: Optional[Tuple[int, int, int, int]] = None,
    language: str = "eng"
) -> str
```

**Parameters:**
- `region` (tuple, optional): (x, y, width, height) to extract from specific area
- `language` (str): OCR language code (default: "eng")

**Returns:**
- `str`: Extracted text

**Example:**
```python
# Extract all screen text
text = await vision.extract_text_from_screen()
print(text)

# Extract from specific region
text = await vision.extract_text_from_screen(region=(100, 100, 500, 300))

# Extract Russian text
text = await vision.extract_text_from_screen(language="rus")
```

---

### find_text()

Find specific text on screen and return its location.

**Signature:**
```python
async def find_text(
    self,
    text: str,
    case_sensitive: bool = False
) -> Optional[TextLocation]
```

**Parameters:**
- `text` (str): Text to find
- `case_sensitive` (bool): Whether search is case-sensitive

**Returns:**
- `TextLocation`: Object with coordinates and bounding box, or None if not found

**Example:**
```python
location = await vision.find_text("Submit")
if location:
    print(f"Found at ({location.x}, {location.y})")
    print(f"Bounding box: {location.bbox}")
```

---

### extract_text_from_image()

Extract text from an image file.

**Signature:**
```python
async def extract_text_from_image(
    self,
    image_path: str,
    language: str = "eng"
) -> str
```

**Parameters:**
- `image_path` (str): Path to image file
- `language` (str): OCR language code

**Returns:**
- `str`: Extracted text

**Example:**
```python
text = await vision.extract_text_from_image("/path/to/screenshot.png")
```

---

## Object Detection

### detect_objects()

Detect objects on screen using computer vision.

**Signature:**
```python
async def detect_objects(
    self,
    object_types: Optional[List[str]] = None,
    confidence: float = 0.7
) -> List[DetectedObject]
```

**Parameters:**
- `object_types` (list, optional): Specific object types to detect (e.g., ["button", "textbox"])
- `confidence` (float): Minimum confidence threshold (0.0-1.0)

**Returns:**
- `List[DetectedObject]`: List of detected objects with locations and confidence scores

**Example:**
```python
# Detect all objects
objects = await vision.detect_objects()

# Detect specific UI elements
buttons = await vision.detect_objects(object_types=["button"], confidence=0.8)

for obj in buttons:
    print(f"{obj.type} at ({obj.x}, {obj.y}) - confidence: {obj.confidence}")
```

---

### find_ui_element()

Find specific UI element by type and properties.

**Signature:**
```python
async def find_ui_element(
    self,
    element_type: str,
    properties: Optional[Dict[str, Any]] = None
) -> Optional[UIElement]
```

**Parameters:**
- `element_type` (str): Type of element ("button", "textbox", "dropdown", etc.)
- `properties` (dict, optional): Additional properties to match (text, color, size, etc.)

**Returns:**
- `UIElement`: Found element with location and properties, or None

**Example:**
```python
# Find a button with specific text
button = await vision.find_ui_element(
    element_type="button",
    properties={"text": "Submit", "color": "blue"}
)

if button:
    await controller.click(button.x, button.y)
```

---

## Screen Analysis

### capture_screen()

Capture current screen as image.

**Signature:**
```python
async def capture_screen(
    self,
    region: Optional[Tuple[int, int, int, int]] = None,
    save_path: Optional[str] = None
) -> np.ndarray
```

**Parameters:**
- `region` (tuple, optional): (x, y, width, height) to capture specific area
- `save_path` (str, optional): Path to save screenshot

**Returns:**
- `np.ndarray`: Screenshot as numpy array (RGB)

**Example:**
```python
# Capture full screen
screenshot = await vision.capture_screen()

# Capture and save specific region
screenshot = await vision.capture_screen(
    region=(0, 0, 1920, 1080),
    save_path="/tmp/screenshot.png"
)
```

---

### analyze_layout()

Analyze screen layout and structure.

**Signature:**
```python
async def analyze_layout(self) -> LayoutAnalysis
```

**Returns:**
- `LayoutAnalysis`: Object containing layout structure, regions, and hierarchy

**Example:**
```python
layout = await vision.analyze_layout()

print(f"Regions found: {len(layout.regions)}")
for region in layout.regions:
    print(f"  {region.type}: {region.bbox}")
```

---

### compare_screens()

Compare two screenshots to detect changes.

**Signature:**
```python
async def compare_screens(
    self,
    image1: Union[str, np.ndarray],
    image2: Union[str, np.ndarray],
    threshold: float = 0.95
) -> ScreenComparison
```

**Parameters:**
- `image1`, `image2`: Image paths or numpy arrays to compare
- `threshold` (float): Similarity threshold (0.0-1.0)

**Returns:**
- `ScreenComparison`: Comparison results with similarity score and differences

**Example:**
```python
before = await vision.capture_screen()
# Perform action...
after = await vision.capture_screen()

comparison = await vision.compare_screens(before, after)
print(f"Similarity: {comparison.similarity}")
print(f"Changed regions: {comparison.differences}")
```

---

## Image Processing

### find_image()

Find a template image on screen.

**Signature:**
```python
async def find_image(
    self,
    template_path: str,
    confidence: float = 0.8
) -> Optional[ImageMatch]
```

**Parameters:**
- `template_path` (str): Path to template image
- `confidence` (float): Match confidence threshold

**Returns:**
- `ImageMatch`: Match location and confidence, or None if not found

**Example:**
```python
match = await vision.find_image("/path/to/icon.png", confidence=0.9)
if match:
    await controller.click(match.center_x, match.center_y)
```

---

### wait_for_image()

Wait for an image to appear on screen.

**Signature:**
```python
async def wait_for_image(
    self,
    template_path: str,
    timeout: float = 10.0,
    confidence: float = 0.8
) -> Optional[ImageMatch]
```

**Parameters:**
- `template_path` (str): Path to template image
- `timeout` (float): Maximum wait time in seconds
- `confidence` (float): Match confidence threshold

**Returns:**
- `ImageMatch`: Match when found, or None if timeout

**Example:**
```python
# Wait for loading spinner to disappear
match = await vision.wait_for_image("/path/to/spinner.png", timeout=30)
if not match:
    print("Loading complete")
```

---

## Color Detection

### get_pixel_color()

Get color of pixel at specific coordinates.

**Signature:**
```python
def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]
```

**Parameters:**
- `x`, `y` (int): Pixel coordinates

**Returns:**
- `Tuple[int, int, int]`: RGB color values (0-255)

**Example:**
```python
r, g, b = vision.get_pixel_color(500, 300)
print(f"Color: RGB({r}, {g}, {b})")
```

---

### find_color()

Find all pixels matching a specific color.

**Signature:**
```python
async def find_color(
    self,
    color: Tuple[int, int, int],
    tolerance: int = 10,
    region: Optional[Tuple[int, int, int, int]] = None
) -> List[Tuple[int, int]]
```

**Parameters:**
- `color` (tuple): RGB color to find
- `tolerance` (int): Color matching tolerance (0-255)
- `region` (tuple, optional): Search area

**Returns:**
- `List[Tuple[int, int]]`: List of matching pixel coordinates

**Example:**
```python
# Find all red pixels
red_pixels = await vision.find_color((255, 0, 0), tolerance=20)
print(f"Found {len(red_pixels)} red pixels")
```

---

## Data Classes

### TextLocation

Location of found text on screen.

**Attributes:**
- `text` (str): The found text
- `x`, `y` (int): Center coordinates
- `bbox` (tuple): Bounding box (x, y, width, height)
- `confidence` (float): OCR confidence score

---

### DetectedObject

Detected object information.

**Attributes:**
- `type` (str): Object type
- `x`, `y` (int): Center coordinates
- `width`, `height` (int): Object dimensions
- `confidence` (float): Detection confidence
- `properties` (dict): Additional properties

---

### UIElement

UI element information.

**Attributes:**
- `type` (str): Element type
- `x`, `y` (int): Center coordinates
- `bbox` (tuple): Bounding box
- `properties` (dict): Element properties (text, color, state, etc.)

---

### ImageMatch

Image matching result.

**Attributes:**
- `x`, `y` (int): Top-left corner coordinates
- `center_x`, `center_y` (int): Center coordinates
- `width`, `height` (int): Match dimensions
- `confidence` (float): Match confidence

---

## Error Handling

```python
from src.exceptions import VisionException, OCRException

try:
    text = await vision.extract_text_from_screen()
except OCRException as e:
    print(f"OCR error: {e}")
except VisionException as e:
    print(f"Vision error: {e}")
```

---

## Best Practices

**OCR Accuracy**  
For best OCR results, ensure high-contrast text on clean backgrounds. Pre-process images if needed.

**Performance**  
Cache screen captures when performing multiple vision operations on the same screen state.

**Confidence Thresholds**  
Adjust confidence thresholds based on your use case. Higher values reduce false positives but may miss valid matches.

**Language Support**  
Install appropriate Tesseract language packs for non-English text recognition.

**Resource Usage**  
Vision operations can be CPU/GPU intensive. Use appropriate timeouts and consider batching operations.

---

## Complete Example

```python
import asyncio
from src.vision.vision_core import VisionCore
from src.input_controller import InputController

async def automate_form_filling():
    vision = VisionCore()
    controller = InputController()
    
    # Find and click the username field
    username_field = await vision.find_ui_element(
        element_type="textbox",
        properties={"placeholder": "Username"}
    )
    
    if username_field:
        await controller.click(username_field.x, username_field.y)
        await controller.type_text("user@example.com")
    
    # Find submit button by text
    submit_location = await vision.find_text("Submit")
    if submit_location:
        await controller.click(submit_location.x, submit_location.y)
    
    # Wait for success message
    success = await vision.wait_for_image(
        "/path/to/success_icon.png",
        timeout=10
    )
    
    if success:
        print("Form submitted successfully!")
    else:
        print("Submission may have failed")

asyncio.run(automate_form_filling())
```

---

*API Version: 2.0.0*  
*Last Updated: 2025-11-12*

