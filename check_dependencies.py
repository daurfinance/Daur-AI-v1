#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Checker for Daur AI Intelligent Agent
Checks if all required modules can be imported
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

print("="*60)
print("🔍 Checking Daur AI Dependencies")
print("="*60)
print()

dependencies = [
    ("OpenAI Client", "src.ai.openai_client", "OpenAIClient"),
    ("Input Controller", "src.input.controller", "InputController"),
    ("Screen Capture", "src.vision.screen_capture", "ScreenCapture"),
    ("OCR Engine", "src.vision.ocr_engine", "OCREngine"),
    ("Object Detector", "src.vision.object_detector", "ObjectDetector"),
    ("UI Element Detector", "src.vision.ui_element_detector", "UIElementDetector"),
    ("Intelligent Agent", "src.ai.intelligent_agent", "IntelligentAgent"),
]

failed = []
success = 0

for name, module_path, class_name in dependencies:
    try:
        # Try to import module
        parts = module_path.split('.')
        module = __import__(module_path, fromlist=[class_name])
        
        # Try to get class
        cls = getattr(module, class_name)
        
        print(f"✓ {name:25} - OK")
        success += 1
        
    except Exception as e:
        print(f"✗ {name:25} - FAILED: {e}")
        failed.append((name, str(e)))

print()
print("="*60)
print(f"Results: {success}/{len(dependencies)} dependencies OK")
print("="*60)

if failed:
    print()
    print("❌ Failed dependencies:")
    for name, error in failed:
        print(f"  • {name}: {error}")
    print()
    print("Please install missing dependencies:")
    print("  pip install -r requirements-macos.txt")
    sys.exit(1)
else:
    print()
    print("✅ All dependencies are available!")
    print()
    print("You can now run:")
    print("  python3 daur_chat.py")
    print()
    sys.exit(0)

