"""
OCR Engine - Free Text Recognition
Uses Tesseract OCR for text extraction from screenshots
"""

import logging
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import subprocess
import json

logger = logging.getLogger(__name__)


class OCREngine:
    """Free OCR using Tesseract"""
    
    def __init__(self, language: str = "eng+rus"):
        """
        Initialize OCR engine
        
        Args:
            language: Tesseract language codes (e.g., 'eng', 'rus', 'eng+rus')
        """
        self.language = language
        self.tesseract_available = self._check_tesseract()
        
        if self.tesseract_available:
            logger.info(f"OCR engine initialized with language: {language}")
        else:
            logger.warning("Tesseract not found. OCR will not work.")
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract is installed"""
        try:
            result = subprocess.run(
                ['tesseract', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract all text from image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        if not self.tesseract_available:
            logger.error("Tesseract not available")
            return ""
        
        try:
            # Run Tesseract
            result = subprocess.run(
                ['tesseract', image_path, 'stdout', '-l', self.language],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                text = result.stdout.strip()
                logger.debug(f"Extracted {len(text)} characters from {image_path}")
                return text
            else:
                logger.error(f"Tesseract failed: {result.stderr}")
                return ""
                
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""
    
    def extract_text_with_boxes(self, image_path: str) -> List[Dict[str, any]]:
        """
        Extract text with bounding box coordinates
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of dicts with 'text', 'x', 'y', 'width', 'height', 'confidence'
        """
        if not self.tesseract_available:
            logger.error("Tesseract not available")
            return []
        
        try:
            # Run Tesseract with TSV output
            result = subprocess.run(
                ['tesseract', image_path, 'stdout', '-l', self.language, '--psm', '11', 'tsv'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Tesseract failed: {result.stderr}")
                return []
            
            # Parse TSV output
            lines = result.stdout.strip().split('\n')
            if len(lines) < 2:
                return []
            
            # Skip header
            boxes = []
            for line in lines[1:]:
                parts = line.split('\t')
                if len(parts) < 12:
                    continue
                
                try:
                    level = int(parts[0])
                    page_num = int(parts[1])
                    block_num = int(parts[2])
                    par_num = int(parts[3])
                    line_num = int(parts[4])
                    word_num = int(parts[5])
                    left = int(parts[6])
                    top = int(parts[7])
                    width = int(parts[8])
                    height = int(parts[9])
                    conf = float(parts[10]) if parts[10] != '-1' else 0
                    text = parts[11] if len(parts) > 11 else ''
                    
                    # Only include word-level (level 5) with text
                    if level == 5 and text.strip():
                        boxes.append({
                            'text': text,
                            'x': left,
                            'y': top,
                            'width': width,
                            'height': height,
                            'confidence': conf
                        })
                except (ValueError, IndexError):
                    continue
            
            logger.debug(f"Extracted {len(boxes)} text boxes from {image_path}")
            return boxes
            
        except Exception as e:
            logger.error(f"OCR with boxes error: {e}")
            return []
    
    def find_text(self, image_path: str, search_text: str) -> Optional[Tuple[int, int]]:
        """
        Find text in image and return its center coordinates
        
        Args:
            image_path: Path to image file
            search_text: Text to find
            
        Returns:
            (x, y) coordinates of text center, or None if not found
        """
        boxes = self.extract_text_with_boxes(image_path)
        
        search_lower = search_text.lower()
        for box in boxes:
            if search_lower in box['text'].lower():
                # Calculate center
                center_x = box['x'] + box['width'] // 2
                center_y = box['y'] + box['height'] // 2
                logger.debug(f"Found '{search_text}' at ({center_x}, {center_y})")
                return (center_x, center_y)
        
        logger.debug(f"Text '{search_text}' not found in image")
        return None
    
    def extract_buttons(self, image_path: str) -> List[Dict[str, any]]:
        """
        Extract potential button text and locations
        
        Args:
            image_path: Path to image file
            
        Returns:
            List of button candidates with text and coordinates
        """
        boxes = self.extract_text_with_boxes(image_path)
        
        # Filter for short text (likely buttons)
        buttons = []
        for box in boxes:
            text = box['text'].strip()
            word_count = len(text.split())
            
            # Buttons usually have 1-3 words
            if 1 <= word_count <= 3 and box['confidence'] > 60:
                buttons.append({
                    'text': text,
                    'x': box['x'] + box['width'] // 2,
                    'y': box['y'] + box['height'] // 2,
                    'confidence': box['confidence']
                })
        
        logger.debug(f"Found {len(buttons)} potential buttons")
        return buttons
    
    def is_available(self) -> bool:
        """Check if OCR is available"""
        return self.tesseract_available


# Singleton instance
_ocr_engine: Optional[OCREngine] = None


def get_ocr_engine() -> OCREngine:
    """Get singleton OCR engine instance"""
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = OCREngine()
    return _ocr_engine

