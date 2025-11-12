"""Fallback implementations for CV2 functionality."""
import logging
from typing import Optional, Tuple, Union
import numpy as np

logger = logging.getLogger(__name__)

class CV2Fallback:
    """Fallback implementations for essential OpenCV functionality."""
    
    def __init__(self):
        self.use_cv2 = False
        try:
            import cv2
            self.cv2 = cv2
            self.use_cv2 = True
            logger.info("Using OpenCV for image processing")
        except ImportError:
            logger.warning("OpenCV not available, using fallback implementation")
            self.cv2 = None
            
    def cvtColor(self, 
                 img: np.ndarray, 
                 code: int,
                 dst: Optional[np.ndarray] = None) -> np.ndarray:
        """Basic color space conversion fallback.
        
        Args:
            img: Input image as numpy array
            code: Color conversion code
            dst: Optional output array
            
        Returns:
            Converted image
        """
        if self.use_cv2:
            return self.cv2.cvtColor(img, code)
            
        # Implement basic conversions for common cases
        if code == self.COLOR_BGRA2BGR:
            return img[..., :3]  # Just drop alpha channel
        elif code == self.COLOR_BGR2GRAY:
            # Basic grayscale conversion using weighted sum
            return np.dot(img[..., :3], [0.114, 0.587, 0.299])
        elif code == self.COLOR_GRAY2BGR:
            return np.stack((img,)*3, axis=-1)
        else:
            logger.warning(f"Unsupported color conversion code: {code}")
            return img
            
    def resize(self, 
               img: np.ndarray, 
               dsize: Tuple[int, int],
               fx: Optional[float] = None,
               fy: Optional[float] = None,
               interpolation: int = None) -> np.ndarray:
        """Basic image resize fallback using numpy.
        
        Args:
            img: Input image
            dsize: Output size (w,h)
            fx: Scale factor x
            fy: Scale factor y
            interpolation: Interpolation method (ignored in fallback)
            
        Returns:
            Resized image
        """
        if self.use_cv2:
            return self.cv2.resize(img, dsize, fx=fx, fy=fy, interpolation=interpolation)
            
        # Basic nearest neighbor scaling
        h, w = img.shape[:2]
        if dsize[0] == 0 or dsize[1] == 0:
            if fx is None:
                fx = fy
            if fy is None:
                fy = fx
            dsize = (int(w * fx), int(h * fy))
            
        output = np.zeros((dsize[1], dsize[0]) + img.shape[2:], dtype=img.dtype)
        x_ratio = float(w - 1) / (dsize[0] - 1) if dsize[0] > 1 else 0
        y_ratio = float(h - 1) / (dsize[1] - 1) if dsize[1] > 1 else 0
        
        for i in range(dsize[1]):
            y = int(i * y_ratio)
            for j in range(dsize[0]):
                x = int(j * x_ratio)
                output[i,j] = img[y,x]
                
        return output
        
    def threshold(self,
                 img: np.ndarray,
                 thresh: float,
                 maxval: float,
                 type: int) -> Tuple[float, np.ndarray]:
        """Basic thresholding fallback.
        
        Args:
            img: Input image
            thresh: Threshold value
            maxval: Maximum value
            type: Threshold type
            
        Returns:
            Tuple of (threshold value, thresholded image)
        """
        if self.use_cv2:
            return self.cv2.threshold(img, thresh, maxval, type)
            
        # Basic binary threshold
        output = np.zeros_like(img)
        output[img > thresh] = maxval
        return thresh, output
        
    def findContours(self,
                    img: np.ndarray,
                    mode: int,
                    method: int) -> Tuple[np.ndarray, np.ndarray]:
        """Stub for contour finding - returns empty contours.
        
        This is a complex operation that requires proper OpenCV.
        The fallback just returns empty results.
        
        Args:
            img: Input image
            mode: Contour retrieval mode
            method: Contour approximation method
            
        Returns:
            Tuple of (contours, hierarchy)
        """
        if self.use_cv2:
            return self.cv2.findContours(img, mode, method)
            
        logger.warning("Contour finding requires OpenCV - returning empty results")
        return np.array([]), np.array([])
        
    # Color conversion constants
    COLOR_BGR2GRAY = 6
    COLOR_BGRA2BGR = 4
    COLOR_GRAY2BGR = 8
    
    # Threshold types
    THRESH_BINARY = 0
    THRESH_BINARY_INV = 1
    
    # Contour constants  
    RETR_EXTERNAL = 0
    RETR_LIST = 1
    CHAIN_APPROX_SIMPLE = 1
    
    # Interpolation constants
    INTER_NEAREST = 0
    INTER_LINEAR = 1
    INTER_AREA = 3

# Global instance
cv = CV2Fallback()