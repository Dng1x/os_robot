#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automation Flow Runner - Standalone Version
Independent flow executor without backend server
"""

import json
import os
import sys
import time
import logging
import subprocess
import re
import base64
from io import BytesIO
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# ============================================================================
# Third-party imports with error handling
# ============================================================================
try:
    import pyautogui
    import pyperclip
    import cv2
    import numpy as np
    from PIL import Image
    import pygetwindow as gw
except ImportError as e:
    print(f"[ERROR] Missing required library: {e}")
    print("\nPlease install dependencies:")
    print("  Windows: run_install_deps.bat")
    print("  Linux/Mac: run_install_deps.sh")
    print("  Or manually: pip install -r requirements.txt")
    input("\nPress Enter to exit...")
    sys.exit(1)

# PyAutoGUI safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


# ============================================================================
# Logger - Simple console logger without Queue
# ============================================================================
class SimpleLogger:
    """Simple logger for console output"""
    
    def __init__(self):
        self.logs = []
        self.setup_logger()
    
    def setup_logger(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message: str, level: str = 'info'):
        """Log a message"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        
        self.logs.append(log_entry)
        
        # Print to console
        if level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'success':
            self.logger.info(f'✓ {message}')
        else:
            self.logger.info(message)
    
    def get_logs(self) -> List[dict]:
        """Get all logs"""
        return self.logs
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs.clear()


# Global logger instance
log_manager = SimpleLogger()


# ============================================================================
# Image Matching Utilities
# ============================================================================
def load_image_from_path(image_path: str) -> Optional[np.ndarray]:
    """Load image from file path"""
    if not os.path.exists(image_path):
        log_manager.log(f"Image file not found: {image_path}", 'error')
        return None
    
    try:
        img = cv2.imread(image_path)
        if img is None:
            log_manager.log(f"Failed to load image: {image_path}", 'error')
        return img
    except Exception as e:
        log_manager.log(f"Error loading image: {e}", 'error')
        return None


def preprocess_image(img: np.ndarray, method: str = 'adaptive') -> np.ndarray:
    """
    Preprocess image for robust matching
    
    Args:
        img: Input image
        method: Preprocessing method
            - 'grayscale': Convert to grayscale
            - 'adaptive': Adaptive threshold (best for UI elements)
            - 'edge': Edge detection
            - 'normalize': Histogram equalization
    
    Returns:
        Preprocessed image
    """
    if method == 'grayscale':
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img
    
    elif method == 'adaptive':
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        # Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Adaptive threshold
        binary = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        return binary
    
    elif method == 'edge':
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        # Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)
        return edges
    
    elif method == 'normalize':
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        # Histogram equalization
        return cv2.equalizeHist(gray)
    
    return img


def find_image_multiscale(
    screen_img: np.ndarray,
    template_img: np.ndarray,
    confidence: float = 0.8,
    scales: Optional[List[float]] = None,
    offset: Tuple[int, int] = (0, 0)
) -> Optional[Tuple[int, int, float, float]]:
    """
    Multi-scale template matching for DPI-independent recognition
    
    Args:
        screen_img: Screen image
        template_img: Template image
        confidence: Minimum confidence threshold (0.0-1.0)
        scales: Scale factors to try (default covers 100%-200% DPI)
        offset: Coordinate offset (for region search)
    
    Returns:
        (center_x, center_y, best_scale, best_confidence) or None
    """
    if scales is None:
        # Default scales cover common DPI settings:
        # 100%, 110%, 120%, 125%, 130%, 140%, 150%, 175%, 200%
        scales = [0.8, 0.9, 1.0, 1.1, 1.2, 1.25, 1.3, 1.4, 1.5, 1.75, 2.0]
    
    template_h, template_w = template_img.shape[:2]
    screen_h, screen_w = screen_img.shape[:2]
    
    best_match = None
    best_val = confidence
    best_scale = 1.0
    
    offset_x, offset_y = offset
    
    for scale in scales:
        # Calculate scaled dimensions
        scaled_w = int(template_w * scale)
        scaled_h = int(template_h * scale)
        
        # Skip invalid sizes
        if scaled_w < 10 or scaled_h < 10:
            continue
        if scaled_w > screen_w or scaled_h > screen_h:
            continue
        
        # Resize template
        # Use INTER_AREA for downscaling, INTER_CUBIC for upscaling
        interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
        scaled_template = cv2.resize(template_img, (scaled_w, scaled_h), interpolation=interpolation)
        
        # Template matching
        result = cv2.matchTemplate(screen_img, scaled_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # Update best match
        if max_val > best_val:
            best_val = max_val
            best_scale = scale
            center_x = max_loc[0] + scaled_w // 2 + offset_x
            center_y = max_loc[1] + scaled_h // 2 + offset_y
            best_match = (center_x, center_y, best_scale, best_val)
    
    return best_match


def find_image_on_screen(
    template_path: str,
    confidence: float = 0.8,
    region: Optional[Tuple[int, int, int, int]] = None,
    enable_multiscale: bool = True,
    enable_preprocessing: bool = True,
    preprocessing_method: str = 'adaptive'
) -> Optional[Tuple[int, int]]:
    """
    Find image on screen with enhanced cross-device compatibility
    
    Args:
        template_path: Path to template image
        confidence: Match confidence (0.0-1.0)
        region: Search region (x, y, width, height)
        enable_multiscale: Enable multi-scale matching (recommended)
        enable_preprocessing: Enable image preprocessing (recommended)
        preprocessing_method: 'adaptive', 'edge', 'grayscale', or 'normalize'
    
    Returns:
        Center coordinates (x, y), None if not found
    """
    # Screenshot
    if region:
        x, y, w, h = region
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        offset_x, offset_y = x, y
    else:
        screenshot = pyautogui.screenshot()
        offset_x, offset_y = 0, 0
    
    # Convert to OpenCV format
    screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Load template image
    template_img = load_image_from_path(template_path)
    if template_img is None:
        return None
    
    # Apply preprocessing if enabled
    if enable_preprocessing:
        screen_processed = preprocess_image(screen_img, preprocessing_method)
        template_processed = preprocess_image(template_img, preprocessing_method)
    else:
        screen_processed = screen_img
        template_processed = template_img
    
    # Try multi-scale matching if enabled
    if enable_multiscale:
        result = find_image_multiscale(
            screen_processed, 
            template_processed, 
            confidence,
            offset=(offset_x, offset_y)
        )
        
        if result:
            center_x, center_y, scale, conf = result
            log_manager.log(f"Found at scale {scale:.2f}x with confidence {conf:.3f}", 'info')
            return (center_x, center_y)
    else:
        # Fallback to single-scale matching
        result = cv2.matchTemplate(screen_processed, template_processed, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            template_h, template_w = template_processed.shape[:2]
            center_x = max_loc[0] + template_w // 2 + offset_x
            center_y = max_loc[1] + template_h // 2 + offset_y
            return (center_x, center_y)
    
    return None


def get_screen_color(x: int, y: int) -> Tuple[int, int, int]:
    """Get color at screen position"""
    pixel = pyautogui.screenshot(region=(x, y, 1, 1))
    rgb = pixel.getpixel((0, 0))
    return rgb


def check_color_match(
    x: int,
    y: int,
    target_color: str,
    tolerance: int = 10
) -> bool:
    """Check if color at position matches target"""
    current_rgb = get_screen_color(x, y)
    
    # Parse target color
    target_color = target_color.lstrip('#')
    target_rgb = tuple(int(target_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Check each channel difference
    for c, t in zip(current_rgb, target_rgb):
        if abs(c - t) > tolerance:
            return False
    
    return True


# ============================================================================
# Window Management Utilities
# ============================================================================
def find_window(title: str, match_mode: str = '包含') -> Optional[object]:
    """Find window by title"""
    all_windows = gw.getAllTitles()
    
    for window_title in all_windows:
        if match_mode == '完全匹配':
            if window_title == title:
                return gw.getWindowsWithTitle(window_title)[0]
        elif match_mode == '包含':
            if title in window_title:
                return gw.getWindowsWithTitle(window_title)[0]
        elif match_mode == '正则':
            if re.search(title, window_title):
                return gw.getWindowsWithTitle(window_title)[0]
    
    return None


def activate_window(window) -> bool:
    """Activate window"""
    try:
        if window.isMinimized:
            window.restore()
        window.activate()
        return True
    except Exception as e:
        log_manager.log(f"Failed to activate window: {e}", 'error')
        return False


def close_window(window) -> bool:
    """Close window"""
    try:
        window.close()
        return True
    except Exception as e:
        log_manager.log(f"Failed to close window: {e}", 'error')
        return False


# ============================================================================
# Action Execution Functions - Recognition
# ============================================================================
def execute_find_image(params: Dict[str, Any], assets: list, context: Dict) -> Dict[str, Any]:
    """Execute find image action"""
    # Get asset name from params (try different possible keys)
    asset_name = params.get('image') or params.get('asset') or params.get('asset_name')
    confidence = params.get('confidence', 0.8)
    timeout = params.get('timeout', 5)
    region = params.get('region')
    
    # If no asset name specified, use first asset
    if not asset_name:
        if len(assets) > 0:
            asset = assets[0]
            log_manager.log(f"No asset specified in params, using first asset: {asset.get('name', 'unnamed')}", 'warning')
        else:
            log_manager.log("No assets available", 'error')
            context['found'] = False
            context['position'] = None
            return {'success': False, 'found': False, 'position': None, 'output': 'failure'}
    else:
        # Find asset by name
        asset = None
        for a in assets:
            if a.get('name') == asset_name:
                asset = a
                break
        
        if not asset:
            log_manager.log(f"Asset not found: {asset_name}", 'error')
            log_manager.log(f"Available assets: {[a.get('name') for a in assets]}", 'info')
            context['found'] = False
            context['position'] = None
            return {'success': False, 'found': False, 'position': None, 'output': 'failure'}
    
    display_name = asset.get('name', 'unnamed')
    asset_path = asset.get('path', '')
    
    if not asset_path:
        log_manager.log(f"Asset has no path: {display_name}", 'error')
        context['found'] = False
        context['position'] = None
        return {'success': False, 'found': False, 'position': None, 'output': 'failure'}
    
    log_manager.log(f"Finding image: {display_name}, path: {asset_path}", 'info')
    log_manager.log(f"Confidence: {confidence}, Timeout: {timeout}s", 'info')
    
    # Parse search region
    search_region = None
    if region:
        try:
            parts = [int(x.strip()) for x in region.split(',')]
            if len(parts) == 4:
                search_region = tuple(parts)
        except:
            pass
    
    # Execute image search with timeout
    start_time = time.time()
    position = None
    
    while time.time() - start_time < timeout:
        position = find_image_on_screen(
            asset_path,
            confidence,
            search_region
        )
        
        if position:
            break
        
        time.sleep(0.5)
    
    if position:
        log_manager.log(f"Image found at: {position}", 'success')
        context['found'] = True
        context['position'] = position
        return {
            'success': True,
            'found': True,
            'position': position,
            'output': 'success'
        }
    else:
        log_manager.log(f"Image not found: {display_name}", 'warning')
        context['found'] = False
        context['position'] = None
        return {
            'success': False,
            'found': False,
            'position': None,
            'output': 'failure'
        }


def execute_find_text(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute OCR text recognition"""
    text = params.get('text')
    region = params.get('region')
    language = params.get('language', '中英混合')
    
    log_manager.log(f"Recognizing text: {text}", 'info')
    
    try:
        from paddleocr import PaddleOCR
        
        # Initialize OCR
        use_lang = 'ch' if '中文' in language else 'en'
        ocr = PaddleOCR(use_angle_cls=True, lang=use_lang, show_log=False)
        
        # Screenshot
        if region:
            parts = [int(x.strip()) for x in region.split(',')]
            if len(parts) == 4:
                screenshot = pyautogui.screenshot(region=tuple(parts))
            else:
                screenshot = pyautogui.screenshot()
        else:
            screenshot = pyautogui.screenshot()
        
        # Convert to numpy array
        img_array = np.array(screenshot)
        
        # OCR recognition
        result = ocr.ocr(img_array, cls=True)
        
        # Find target text
        found = False
        position = None
        recognized_text = ""
        
        if result and result[0]:
            for line in result[0]:
                detected_text = line[1][0]
                recognized_text += detected_text + " "
                
                if text in detected_text:
                    # Calculate text center position
                    box = line[0]
                    x = int(sum([p[0] for p in box]) / 4)
                    y = int(sum([p[1] for p in box]) / 4)
                    position = (x, y)
                    found = True
                    break
        
        if found:
            log_manager.log(f"Text found at: {position}", 'success')
            context['found'] = True
            context['position'] = position
            context['text_content'] = recognized_text.strip()
            return {
                'success': True,
                'found': True,
                'position': position,
                'output': 'success'
            }
        else:
            log_manager.log(f"Text not found: {text}", 'warning')
            context['found'] = False
            context['position'] = None
            context['text_content'] = recognized_text.strip()
            return {
                'success': False,
                'found': False,
                'position': None,
                'output': 'failure'
            }
    
    except Exception as e:
        log_manager.log(f"OCR recognition failed: {str(e)}", 'error')
        return {
            'success': False,
            'found': False,
            'position': None,
            'output': 'failure'
        }


def execute_find_window(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute find window"""
    title = params.get('title')
    match_mode = params.get('match_mode', '包含')
    
    log_manager.log(f"Finding window: {title}", 'info')
    
    window = find_window(title, match_mode)
    
    if window:
        log_manager.log(f"Window found: {window.title}", 'success')
        context['found'] = True
        context['window_handle'] = window
        return {
            'success': True,
            'found': True,
            'window_handle': window,
            'output': 'success'
        }
    else:
        log_manager.log(f"Window not found: {title}", 'warning')
        context['found'] = False
        context['window_handle'] = None
        return {
            'success': False,
            'found': False,
            'window_handle': None,
            'output': 'failure'
        }


def execute_check_color(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute color check"""
    position = params.get('position')
    color = params.get('color', '#FF0000')
    tolerance = params.get('tolerance', 10)
    
    # Parse position
    try:
        x, y = [int(p.strip()) for p in position.split(',')]
    except:
        log_manager.log(f"Invalid position format: {position}", 'error')
        return {'success': False, 'matched': False, 'output': 'failure'}
    
    log_manager.log(f"Checking color at ({x}, {y})", 'info')
    
    matched = check_color_match(x, y, color, tolerance)
    
    if matched:
        log_manager.log(f"Color matched", 'success')
        context['matched'] = True
        return {'success': True, 'matched': True, 'output': 'success'}
    else:
        log_manager.log(f"Color not matched", 'warning')
        context['matched'] = False
        return {'success': False, 'matched': False, 'output': 'failure'}


# ============================================================================
# Action Execution Functions - Operations
# ============================================================================
def get_position(params: Dict[str, Any], context: Dict) -> tuple:
    """Get position coordinates"""
    position_type = params.get('position_type', '使用变量')
    
    if position_type == '使用变量':
        position_var = params.get('position_var', 'position')
        offset_x = params.get('offset_x', 0)
        offset_y = params.get('offset_y', 0)
        
        # Get variable from context
        pos = context.get(position_var)
        if pos and isinstance(pos, (tuple, list)) and len(pos) >= 2:
            return (pos[0] + offset_x, pos[1] + offset_y)
        else:
            raise ValueError(f"Variable {position_var} does not exist or is invalid")
    
    else:  # Fixed coordinates
        x = params.get('fixed_x', 0)
        y = params.get('fixed_y', 0)
        return (x, y)


def execute_click(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute click operation"""
    try:
        x, y = get_position(params, context)
        
        button = params.get('button', '左键')
        clicks = params.get('clicks', 1)
        
        # Convert button name
        button_map = {'左键': 'left', '右键': 'right', '中键': 'middle'}
        pyautogui_button = button_map.get(button, 'left')
        
        log_manager.log(f"Clicking at: ({x}, {y}), button: {button}", 'info')
        
        pyautogui.click(x, y, clicks=clicks, button=pyautogui_button)
        
        log_manager.log("Click completed", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Click failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_double_click(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute double click operation"""
    try:
        x, y = get_position(params, context)
        
        log_manager.log(f"Double clicking at: ({x}, {y})", 'info')
        
        pyautogui.doubleClick(x, y)
        
        log_manager.log("Double click completed", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Double click failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_drag(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute drag operation"""
    try:
        # Get start position
        from_type = params.get('from_type', '使用变量')
        if from_type == '使用变量':
            from_var = params.get('from_var', 'position')
            from_pos = context.get(from_var)
            if not from_pos:
                raise ValueError(f"Variable {from_var} does not exist")
            from_x, from_y = from_pos[0], from_pos[1]
        else:
            from_x = params.get('from_x', 0)
            from_y = params.get('from_y', 0)
        
        # Get end position
        to_type = params.get('to_type', '固定坐标')
        if to_type == '使用变量':
            to_var = params.get('to_var', '')
            to_pos = context.get(to_var)
            if not to_pos:
                raise ValueError(f"Variable {to_var} does not exist")
            to_x, to_y = to_pos[0], to_pos[1]
        elif to_type == '相对偏移':
            to_x = from_x + params.get('to_x', 0)
            to_y = from_y + params.get('to_y', 0)
        else:
            to_x = params.get('to_x', 0)
            to_y = params.get('to_y', 0)
        
        duration = params.get('duration', 0.5)
        
        log_manager.log(f"Dragging: ({from_x}, {from_y}) → ({to_x}, {to_y})", 'info')
        
        pyautogui.moveTo(from_x, from_y)
        pyautogui.dragTo(to_x, to_y, duration=duration)
        
        log_manager.log("Drag completed", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Drag failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_scroll(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute scroll operation"""
    try:
        direction = params.get('direction', '向下')
        amount = params.get('amount', 100)
        
        # Convert scroll direction
        scroll_amount = -amount if direction == '向下' else amount
        
        log_manager.log(f"Scrolling: {direction} {amount}", 'info')
        
        pyautogui.scroll(scroll_amount)
        
        log_manager.log("Scroll completed", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Scroll failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_type_text(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute type text operation"""
    try:
        text = params.get('text', '')
        interval = params.get('interval', 0.1)
        
        log_manager.log(f"Typing text: {text[:20]}...", 'info')
        
        pyautogui.write(text, interval=interval)
        
        log_manager.log("Type completed", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Type failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_hotkey(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute hotkey operation"""
    try:
        keys = params.get('keys', '')
        
        log_manager.log(f"Pressing hotkey: {keys}", 'info')
        
        # Parse hotkey (e.g. 'ctrl+c')
        key_list = [k.strip() for k in keys.split('+')]
        pyautogui.hotkey(*key_list)
        
        log_manager.log("Hotkey executed", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Hotkey failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_launch_program(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute launch program operation"""
    try:
        path = params.get('path', '')
        args = params.get('args', '')
        
        log_manager.log(f"Launching program: {path}", 'info')
        
        if args:
            subprocess.Popen([path] + args.split())
        else:
            subprocess.Popen([path])
        
        log_manager.log("Program launched", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Program launch failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_activate_window(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute activate window operation"""
    try:
        window = context.get('window_handle')
        
        if not window:
            log_manager.log("Window handle not found", 'error')
            return {'success': False, 'output': 'next'}
        
        log_manager.log(f"Activating window: {window.title}", 'info')
        
        success = activate_window(window)
        
        if success:
            log_manager.log("Window activated", 'success')
            return {'success': True, 'output': 'next'}
        else:
            log_manager.log("Window activation failed", 'error')
            return {'success': False, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Activate window failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_close_window(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute close window operation"""
    try:
        window = context.get('window_handle')
        
        if not window:
            log_manager.log("Window handle not found", 'error')
            return {'success': False, 'output': 'next'}
        
        log_manager.log(f"Closing window: {window.title}", 'info')
        
        success = close_window(window)
        
        if success:
            log_manager.log("Window closed", 'success')
            return {'success': True, 'output': 'next'}
        else:
            log_manager.log("Window close failed", 'error')
            return {'success': False, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Close window failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


# ============================================================================
# Action Execution Functions - Logic
# ============================================================================
def execute_wait(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute wait operation"""
    try:
        duration = params.get('duration', 1.0)
        
        log_manager.log(f"Waiting {duration} seconds", 'info')
        
        time.sleep(duration)
        
        log_manager.log("Wait completed", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Wait failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_condition(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute condition check"""
    try:
        condition = params.get('condition', '')
        
        log_manager.log(f"Checking condition: {condition}", 'info')
        
        # Simple condition evaluation (should be safer in production)
        # Replace variables
        for key, value in context.items():
            condition = condition.replace(f'{{{key}}}', str(value))
        
        # Evaluate condition
        result = eval(condition)
        
        if result:
            log_manager.log("Condition is true", 'success')
            return {'success': True, 'output': 'true'}
        else:
            log_manager.log("Condition is false", 'info')
            return {'success': True, 'output': 'false'}
    
    except Exception as e:
        log_manager.log(f"Condition check failed: {str(e)}", 'error')
        return {'success': False, 'output': 'false'}


def execute_end(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute end operation"""
    log_manager.log("Flow ended", 'success')
    return {'success': True, 'output': 'end'}


# ============================================================================
# Action Execution Functions - Data
# ============================================================================
def execute_variable(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute variable operation"""
    try:
        mode = params.get('mode', '设置变量')
        
        if mode == '设置变量':
            assignment = params.get('assignment', '')
            
            log_manager.log(f"Executing assignment: {assignment}", 'info')
            
            # Parse assignment (e.g. my_pos = position)
            if '=' in assignment:
                left, right = assignment.split('=', 1)
                var_name = left.strip()
                source = right.strip()
                
                # Get value from context
                if source in context:
                    value = context[source]
                    context[var_name] = value
                    log_manager.log(f"Variable {var_name} = {value}", 'success')
                else:
                    # Try to evaluate expression
                    try:
                        # Replace context variables
                        for key, val in context.items():
                            source = source.replace(key, repr(val))
                        value = eval(source)
                        context[var_name] = value
                        log_manager.log(f"Variable {var_name} = {value}", 'success')
                    except:
                        log_manager.log(f"Cannot parse assignment: {assignment}", 'error')
                        return {'success': False, 'output': 'next'}
        
        else:  # Read variable
            read_var = params.get('read_var', '')
            if read_var in context:
                value = context[read_var]
                log_manager.log(f"Read variable {read_var} = {value}", 'info')
            else:
                log_manager.log(f"Variable {read_var} does not exist", 'warning')
        
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Variable operation failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_clipboard_copy(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute copy to clipboard operation"""
    try:
        content = params.get('content', '')
        
        # Replace variables
        for key, value in context.items():
            content = content.replace(f'{{{key}}}', str(value))
        
        log_manager.log(f"Copying to clipboard: {content[:50]}...", 'info')
        
        pyperclip.copy(content)
        
        log_manager.log("Copy completed", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Copy failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_clipboard_paste(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute paste from clipboard operation"""
    try:
        log_manager.log("Getting clipboard content", 'info')
        
        content = pyperclip.paste()
        context['clipboard_content'] = content
        
        log_manager.log(f"Got content: {content[:50]}...", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Paste failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_message_box(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute message box operation"""
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        content = params.get('content', '')
        title = params.get('title', '提示')
        
        # Replace variables
        for key, value in context.items():
            content = content.replace(f'{{{key}}}', str(value))
        
        log_manager.log(f"Showing message box: {title}", 'info')
        
        # Create hidden main window
        root = tk.Tk()
        root.withdraw()
        
        # Show message box
        messagebox.showinfo(title, content)
        
        root.destroy()
        
        log_manager.log("Message box closed", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Message box failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_log(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute log operation"""
    try:
        content = params.get('content', '')
        level = params.get('level', '信息')
        
        # Replace variables
        for key, value in context.items():
            content = content.replace(f'{{{key}}}', str(value))
        
        # Convert level
        level_map = {'信息': 'info', '警告': 'warning', '错误': 'error'}
        log_level = level_map.get(level, 'info')
        
        log_manager.log(content, log_level)
        
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Log operation failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_screenshot(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """Execute screenshot operation"""
    try:
        path = params.get('path', 'screenshot.png')
        region = params.get('region')
        
        log_manager.log(f"Saving screenshot to: {path}", 'info')
        
        if region:
            parts = [int(x.strip()) for x in region.split(',')]
            if len(parts) == 4:
                screenshot = pyautogui.screenshot(region=tuple(parts))
            else:
                screenshot = pyautogui.screenshot()
        else:
            screenshot = pyautogui.screenshot()
        
        screenshot.save(path)
        
        log_manager.log("Screenshot saved", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"Screenshot failed: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


# ============================================================================
# Flow Executor
# ============================================================================
# Action execution function mapping
ACTION_MAP = {
    # Recognition
    'find_image': execute_find_image,
    'find_text': execute_find_text,
    'find_window': execute_find_window,
    'check_color': execute_check_color,
    
    # Operation
    'click': execute_click,
    'double_click': execute_double_click,
    'drag': execute_drag,
    'scroll': execute_scroll,
    'type_text': execute_type_text,
    'hotkey': execute_hotkey,
    'launch_program': execute_launch_program,
    'activate_window': execute_activate_window,
    'close_window': execute_close_window,
    
    # Logic
    'wait': execute_wait,
    'condition': execute_condition,
    'end': execute_end,
    
    # Data
    'variable': execute_variable,
    'clipboard_copy': execute_clipboard_copy,
    'clipboard_paste': execute_clipboard_paste,
    'message_box': execute_message_box,
    'log': execute_log,
    'screenshot': execute_screenshot
}


class FlowExecutor:
    """Flow executor"""
    
    def __init__(self, flow_data: Dict):
        """Initialize executor"""
        self.flow_data = flow_data
        self.nodes = {node['id']: node for node in flow_data.get('nodes', [])}
        self.connections = flow_data.get('connections', [])
        self.assets = flow_data.get('assets', [])
        self.context = {}
        self.is_running = False
        self.node_pass_count = {}
        
        # Get script directory
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_dir = os.path.join(self.script_dir, 'assets')
        
        # Ensure assets directory exists
        os.makedirs(self.assets_dir, exist_ok=True)
        
        # Process assets: convert base64 to files
        self._process_assets()
    
    def _process_assets(self):
        """Process assets: convert base64 to files and update paths"""
        for asset in self.assets:
            asset_path = asset.get('path', '')
            asset_name = asset.get('name', '')
            asset_id = asset.get('id', '')
            
            # If path is base64, save to file
            if asset_path.startswith('data:image'):
                try:
                    log_manager.log(f"Converting base64 asset to file: {asset_name}", 'info')
                    
                    # Extract base64 data
                    if ',' in asset_path:
                        base64_data = asset_path.split(',')[1]
                    else:
                        base64_data = asset_path
                    
                    # Decode base64
                    img_data = base64.b64decode(base64_data)
                    
                    # Determine file extension from mime type
                    if 'image/png' in asset_path:
                        ext = 'png'
                    elif 'image/jpeg' in asset_path or 'image/jpg' in asset_path:
                        ext = 'jpg'
                    else:
                        ext = 'png'  # default
                    
                    # Generate filename: use asset name or id
                    if asset_name:
                        filename = f"{asset_name}.{ext}"
                    else:
                        filename = f"{asset_id}.{ext}"
                    
                    # Save to assets folder
                    file_path = os.path.join(self.assets_dir, filename)
                    with open(file_path, 'wb') as f:
                        f.write(img_data)
                    
                    # Update asset path to file path
                    asset['path'] = file_path
                    log_manager.log(f"Saved asset to: {file_path}", 'success')
                    
                except Exception as e:
                    log_manager.log(f"Failed to process base64 asset: {e}", 'error')
            
            # If path is absolute, convert to relative
            elif os.path.isabs(asset_path):
                filename = os.path.basename(asset_path)
                new_path = os.path.join(self.assets_dir, filename)
                
                # Check if file exists in assets folder
                if os.path.exists(new_path):
                    asset['path'] = new_path
                else:
                    log_manager.log(f"Asset file not found: {filename}", 'warning')
            
            # If path is relative, make it absolute
            elif asset_path and not os.path.isabs(asset_path):
                # Assume it's relative to script directory
                if not asset_path.startswith('.'):
                    asset_path = os.path.join('.', asset_path)
                asset['path'] = os.path.join(self.script_dir, asset_path)
    
    def find_next_node(self, current_node_id: str, output: str = 'next') -> str:
        """Find next node based on output"""
        for conn in self.connections:
            if conn['source'] == current_node_id:
                if conn.get('sourceHandle') == output or output == 'next':
                    return conn['target']
        return None
    
    def execute_node(self, node_id: str) -> Dict[str, Any]:
        """Execute single node"""
        if node_id not in self.nodes:
            log_manager.log(f"Node not found: {node_id}", 'error')
            return {'success': False, 'output': 'next'}
        
        node = self.nodes[node_id]
        node_type = node['data']['type']
        params = node['data'].get('params', {})
        
        # Check pass count (skip start and end nodes)
        if node_type not in ['start', 'end']:
            self.node_pass_count[node_id] = self.node_pass_count.get(node_id, 0) + 1
            max_passes = params.get('max_passes', 999999)
            
            if self.node_pass_count[node_id] > max_passes:
                log_manager.log(
                    f"Node {node_type} ({node_id}) reached max passes {max_passes}, terminating",
                    'warning'
                )
                return {'success': False, 'output': 'end'}
        
        log_manager.log(f"Executing node: {node_type} ({node_id})", 'info')
        
        # Special handling for start node
        if node_type == 'start':
            log_manager.log("Flow started", 'info')
            return {'success': True, 'output': 'next'}
        
        # Find execution function
        if node_type not in ACTION_MAP:
            log_manager.log(f"Unsupported node type: {node_type}", 'error')
            return {'success': False, 'output': 'next'}
        
        # Execute action
        execute_func = ACTION_MAP[node_type]
        
        try:
            # Pass different parameters based on node type
            if node_type in ['find_image']:
                result = execute_func(params, self.assets, self.context)
            else:
                result = execute_func(params, self.context)
            
            return result
        
        except Exception as e:
            log_manager.log(f"Node execution error: {str(e)}", 'error')
            return {'success': False, 'output': 'next'}
    
    def execute(self) -> Dict[str, Any]:
        """Execute entire flow"""
        log_manager.clear_logs()
        log_manager.log("=" * 50, 'info')
        log_manager.log(f"Starting flow: {self.flow_data.get('name', 'Unnamed')}", 'info')
        log_manager.log("=" * 50, 'info')
        
        self.is_running = True
        
        # Find start node
        start_node = None
        for node in self.nodes.values():
            if node['data']['type'] == 'start':
                start_node = node
                break
        
        if not start_node:
            log_manager.log("Start node not found", 'error')
            return {
                'success': False,
                'message': 'Start node not found',
                'logs': log_manager.get_logs()
            }
        
        # Execute from start node
        current_node_id = start_node['id']
        max_steps = 1000  # Prevent infinite loops
        steps = 0
        
        while current_node_id and steps < max_steps:
            if not self.is_running:
                log_manager.log("Flow stopped", 'warning')
                break
            
            # Execute current node
            result = self.execute_node(current_node_id)
            
            # Check if ended
            if result.get('output') == 'end':
                log_manager.log("Flow ended normally", 'success')
                break
            
            # Find next node
            output_type = result.get('output', 'next')
            next_node_id = self.find_next_node(current_node_id, output_type)
            
            if not next_node_id:
                log_manager.log("Reached end of flow", 'info')
                break
            
            current_node_id = next_node_id
            steps += 1
        
        if steps >= max_steps:
            log_manager.log("Flow exceeded max steps limit", 'error')
        
        log_manager.log("=" * 50, 'info')
        log_manager.log("Flow execution completed", 'success')
        log_manager.log("=" * 50, 'info')
        
        self.is_running = False
        
        return {
            'success': True,
            'message': 'Flow execution completed',
            'logs': log_manager.get_logs()
        }
    
    def stop(self):
        """Stop execution"""
        self.is_running = False
        log_manager.log("Stop signal received", 'warning')


# ============================================================================
# Main Entry Point
# ============================================================================
def main():
    """Main function"""
    print("""
    ╔════════════════════════════════════════════╗
    ║   Automation Flow Runner v1.0              ║
    ║   Standalone Executor                      ║
    ╚════════════════════════════════════════════╝
    """)
    
    # Find flow.json file
    flow_file = 'flow.json'
    
    if not os.path.exists(flow_file):
        log_manager.log(f"Error: {flow_file} not found", 'error')
        log_manager.log("Please ensure flow.json is in the same directory as runner.py", 'error')
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    try:
        # Load flow data
        log_manager.log(f"Loading flow from: {flow_file}", 'info')
        with open(flow_file, 'r', encoding='utf-8') as f:
            flow_data = json.load(f)
        
        # Create executor
        executor = FlowExecutor(flow_data)
        
        # Execute flow
        result = executor.execute()
        
        if result['success']:
            print("\n✓ Execution successful")
        else:
            print("\n✗ Execution failed")
    
    except KeyboardInterrupt:
        print("\n\nFlow interrupted by user")
    
    except Exception as e:
        log_manager.log(f"Error: {e}", 'error')
        import traceback
        traceback.print_exc()
    
    finally:
        input("\nPress Enter to exit...")


if __name__ == '__main__':
    main()
