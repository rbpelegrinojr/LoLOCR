"""
OCR Processing for LoLOCR
Handles OCR-based text recognition from game screenshots
"""

import json
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

try:
    import numpy as np
except ImportError:
    np = None


class OCRProcessor:
    """
    OCR processor for extracting game data from screenshots.
    
    This is a placeholder implementation that can be extended with:
    - Tesseract (pytesseract)
    - EasyOCR
    - PaddleOCR
    - Azure Computer Vision API
    - Google Cloud Vision API
    """
    
    def __init__(self, debug: bool = False, save_crops: bool = False, output_dir: str = 'output'):
        """
        Initialize OCR processor.
        
        Args:
            debug: Enable debug mode (save intermediate images)
            save_crops: Save cropped scoreboard images
            output_dir: Directory for debug output
        """
        self.debug = debug
        self.save_crops = save_crops
        self.output_dir = Path(output_dir)
        self.debug_dir = self.output_dir / 'debug'
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
        # OCR engine (lazy loaded)
        self._ocr_engine = None
        self._ocr_backend = None
    
    def _load_ocr_engine(self) -> bool:
        """
        Load OCR engine (lazy load).
        
        Tries to load in order:
        1. EasyOCR (recommended, fast and accurate)
        2. PaddleOCR (alternative)
        3. pytesseract (fallback)
        
        Returns:
            True if OCR engine loaded successfully
        """
        if self._ocr_engine is not None:
            return True
        
        # Try EasyOCR
        try:
            import easyocr
            self._ocr_engine = easyocr.Reader(['en'], gpu=False)
            self._ocr_backend = 'easyocr'
            print("[INFO] Using EasyOCR engine")
            return True
        except ImportError:
            pass
        
        # Try PaddleOCR
        try:
            from paddleocr import PaddleOCR
            self._ocr_engine = PaddleOCR(use_angle_cls=True, lang='en')
            self._ocr_backend = 'paddleocr'
            print("[INFO] Using PaddleOCR engine")
            return True
        except ImportError:
            pass
        
        # Try pytesseract
        try:
            import pytesseract
            self._ocr_engine = pytesseract
            self._ocr_backend = 'pytesseract'
            print("[INFO] Using pytesseract engine")
            return True
        except ImportError:
            pass
        
        print("[WARNING] No OCR engine found. Install one with:")
        print("  pip install easyocr  # Recommended")
        print("  pip install paddleocr")
        print("  pip install pytesseract")
        return False
    
    def process_frame(self, frame) -> Optional[Dict[str, Any]]:
        """
        Process a frame and extract game data via OCR.
        
        Args:
            frame: Input frame (numpy array, BGR format)
            
        Returns:
            Dictionary with extracted game data or None if processing failed
        """
        if frame is None:
            return None
        
        try:
            # Save latest capture if debug enabled
            if self.debug:
                self._save_debug_image(frame, 'latest_capture.png')
            
            # Extract game data from frame
            # This is a placeholder that returns empty/default values
            # In a full implementation, this would:
            # 1. Detect scoreboard region
            # 2. Run OCR on relevant text areas
            # 3. Parse numbers and text
            # 4. Extract gold, kills, CS, etc.
            
            game_data = self._extract_game_data(frame)
            
            # Save OCR results if debug enabled
            if self.debug:
                self._save_debug_json(game_data, 'latest_ocr.json')
            
            return game_data
        
        except Exception as e:
            print(f"[ERROR] OCR processing failed: {e}")
            return None
    
    def _extract_game_data(self, frame) -> Dict[str, Any]:
        """
        Extract game data from frame using OCR.
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            Dictionary with extracted game data
        """
        # Placeholder implementation - returns default structure
        # In a real implementation, this would use OCR to extract:
        # - Team names
        # - Player names and champions
        # - Scores (kills, deaths, assists)
        # - Gold amounts
        # - CS counts
        # - Objective status
        # - Timers
        
        result = {
            'gametime': '',
            'teams': {
                'left': {
                    'name': '',
                    'gold': 0,
                    'kills': 0,
                    'towers': 0,
                    'dragons': 0,
                    'heralds': 0,
                    'barons': 0,
                },
                'right': {
                    'name': '',
                    'gold': 0,
                    'kills': 0,
                    'towers': 0,
                    'dragons': 0,
                    'heralds': 0,
                    'barons': 0,
                }
            },
            'players': {
                'left': [self._default_player() for _ in range(5)],
                'right': [self._default_player() for _ in range(5)]
            },
            'objectives': {
                'dragon_timer': 0,
                'baron_timer': 0,
                'herald_timer': 0,
                'elder_timer': 0,
            },
            'ocr_results': []
        }
        
        # If OCR engine is loaded, run OCR
        if self._load_ocr_engine():
            try:
                result['ocr_results'] = self._run_ocr(frame)
            except Exception as e:
                print(f"[WARNING] OCR extraction failed: {e}")
        
        return result
    
    def _run_ocr(self, frame) -> list:
        """
        Run OCR on frame.
        
        Args:
            frame: Input frame
            
        Returns:
            List of OCR results
        """
        if self._ocr_engine is None:
            return []
        
        try:
            if self._ocr_backend == 'easyocr':
                return self._run_easyocr(frame)
            elif self._ocr_backend == 'paddleocr':
                return self._run_paddleocr(frame)
            elif self._ocr_backend == 'pytesseract':
                return self._run_pytesseract(frame)
        except Exception as e:
            print(f"[WARNING] OCR execution failed: {e}")
        
        return []
    
    def _run_easyocr(self, frame) -> list:
        """Run EasyOCR on frame."""
        results = self._ocr_engine.readtext(frame, detail=1)
        return [
            {
                'text': result[1],
                'confidence': result[2],
                'bbox': result[0]
            }
            for result in results
        ]
    
    def _run_paddleocr(self, frame) -> list:
        """Run PaddleOCR on frame."""
        results = self._ocr_engine.ocr(frame, cls=True)
        output = []
        for line in results:
            for word_info in line:
                output.append({
                    'text': word_info[1][0],
                    'confidence': word_info[1][1],
                    'bbox': word_info[0]
                })
        return output
    
    def _run_pytesseract(self, frame) -> list:
        """Run pytesseract on frame."""
        data = self._ocr_engine.image_to_data(frame, output_type=self._ocr_engine.Output.DICT)
        output = []
        for i in range(len(data['text'])):
            if data['text'][i].strip():
                output.append({
                    'text': data['text'][i],
                    'confidence': data['conf'][i] / 100.0,
                    'bbox': [[data['left'][i], data['top'][i]],
                            [data['left'][i] + data['width'][i], data['top'][i]],
                            [data['left'][i] + data['width'][i], data['top'][i] + data['height'][i]],
                            [data['left'][i], data['top'][i] + data['height'][i]]]
                })
        return output
    
    @staticmethod
    def _default_player() -> Dict[str, Any]:
        """Return default player data."""
        return {
            'name': '',
            'champion': '',
            'level': 0,
            'kills': 0,
            'deaths': 0,
            'assists': 0,
            'cs': 0,
            'gold': 0,
        }
    
    def _save_debug_image(self, frame, filename: str) -> None:
        """Save debug image."""
        try:
            import cv2
            filepath = self.debug_dir / filename
            cv2.imwrite(str(filepath), frame)
        except ImportError:
            pass
        except Exception as e:
            print(f"[WARNING] Failed to save debug image: {e}")
    
    def _save_debug_json(self, data: Dict[str, Any], filename: str) -> None:
        """Save debug JSON."""
        try:
            filepath = self.debug_dir / filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            print(f"[WARNING] Failed to save debug JSON: {e}")
    
    def crop_scoreboard(self, frame, 
                       region: Tuple[int, int, int, int]) -> Optional:
        """
        Crop scoreboard region from frame.
        
        Args:
            frame: Input frame
            region: Crop region (x, y, width, height)
            
        Returns:
            Cropped frame or None if crop failed
        """
        try:
            x, y, w, h = region
            cropped = frame[y:y+h, x:x+w]
            
            if self.save_crops:
                self._save_debug_image(cropped, 'latest_scoreboard_crop.png')
            
            return cropped
        except Exception as e:
            print(f"[WARNING] Failed to crop scoreboard: {e}")
            return None
