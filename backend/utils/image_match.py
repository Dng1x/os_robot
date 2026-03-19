"""
图像匹配工具 - v2.0 Enhanced Cross-Device Recognition
"""
import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
from typing import Optional, Tuple, List


def base64_to_image(base64_str: str) -> np.ndarray:
    """将 base64 字符串转换为 OpenCV 图像"""
    # 移除 data:image/png;base64, 前缀
    if ',' in base64_str:
        base64_str = base64_str.split(',')[1]
    
    # 解码 base64
    img_data = base64.b64decode(base64_str)
    
    # 转换为 PIL Image
    pil_image = Image.open(BytesIO(img_data))
    
    # 转换为 OpenCV 格式 (BGR)
    opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    return opencv_image


def preprocess_image(img: np.ndarray, method: str = 'adaptive') -> np.ndarray:
    """
    图像预处理以提高匹配鲁棒性
    
    Args:
        img: 输入图像
        method: 预处理方法
            - 'grayscale': 转灰度
            - 'adaptive': 自适应阈值 (最适合UI元素)
            - 'edge': 边缘检测
            - 'normalize': 直方图均衡化
    
    Returns:
        预处理后的图像
    """
    if method == 'grayscale':
        if len(img.shape) == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return img
    
    elif method == 'adaptive':
        # 转灰度
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        # 高斯模糊去噪
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # 自适应阈值
        binary = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        return binary
    
    elif method == 'edge':
        # 转灰度
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        # 高斯模糊
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Canny边缘检测
        edges = cv2.Canny(blurred, 50, 150)
        return edges
    
    elif method == 'normalize':
        # 转灰度
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        # 直方图均衡化
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
    多尺度模板匹配，适应不同DPI设置
    
    Args:
        screen_img: 屏幕图像
        template_img: 模板图像
        confidence: 最小置信度阈值 (0.0-1.0)
        scales: 缩放比例列表 (默认覆盖100%-200% DPI)
        offset: 坐标偏移 (用于区域搜索)
    
    Returns:
        (center_x, center_y, best_scale, best_confidence) 或 None
    """
    if scales is None:
        # 默认缩放范围覆盖常见DPI设置:
        # 100%, 110%, 120%, 125%, 130%, 140%, 150%, 175%, 200%
        scales = [0.8, 0.9, 1.0, 1.1, 1.2, 1.25, 1.3, 1.4, 1.5, 1.75, 2.0]
    
    template_h, template_w = template_img.shape[:2]
    screen_h, screen_w = screen_img.shape[:2]
    
    best_match = None
    best_val = confidence
    best_scale = 1.0
    
    offset_x, offset_y = offset
    
    for scale in scales:
        # 计算缩放后尺寸
        scaled_w = int(template_w * scale)
        scaled_h = int(template_h * scale)
        
        # 跳过无效尺寸
        if scaled_w < 10 or scaled_h < 10:
            continue
        if scaled_w > screen_w or scaled_h > screen_h:
            continue
        
        # 缩放模板
        # 缩小使用INTER_AREA，放大使用INTER_CUBIC
        interpolation = cv2.INTER_AREA if scale < 1.0 else cv2.INTER_CUBIC
        scaled_template = cv2.resize(template_img, (scaled_w, scaled_h), interpolation=interpolation)
        
        # 模板匹配
        result = cv2.matchTemplate(screen_img, scaled_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # 更新最佳匹配
        if max_val > best_val:
            best_val = max_val
            best_scale = scale
            center_x = max_loc[0] + scaled_w // 2 + offset_x
            center_y = max_loc[1] + scaled_h // 2 + offset_y
            best_match = (center_x, center_y, best_scale, best_val)
    
    return best_match


def find_image_on_screen(
    template_base64: str,
    confidence: float = 0.8,
    region: Optional[Tuple[int, int, int, int]] = None,
    enable_multiscale: bool = True,
    enable_preprocessing: bool = True,
    preprocessing_method: str = 'adaptive'
) -> Optional[Tuple[int, int]]:
    """
    在屏幕上查找图片 - 增强跨设备兼容性
    
    Args:
        template_base64: 目标图片的 base64 字符串
        confidence: 匹配置信度 (0.0-1.0)
        region: 搜索区域 (x, y, width, height)
        enable_multiscale: 启用多尺度匹配 (推荐)
        enable_preprocessing: 启用图像预处理 (推荐)
        preprocessing_method: 'adaptive', 'edge', 'grayscale', 或 'normalize'
    
    Returns:
        图片中心坐标 (x, y)，未找到返回 None
    """
    import pyautogui
    
    # 截取屏幕
    if region:
        x, y, w, h = region
        screenshot = pyautogui.screenshot(region=(x, y, w, h))
        offset_x, offset_y = x, y
    else:
        screenshot = pyautogui.screenshot()
        offset_x, offset_y = 0, 0
    
    # 转换为 OpenCV 格式
    screen_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # 加载模板图片
    template_img = base64_to_image(template_base64)
    
    # 应用预处理
    if enable_preprocessing:
        screen_processed = preprocess_image(screen_img, preprocessing_method)
        template_processed = preprocess_image(template_img, preprocessing_method)
    else:
        screen_processed = screen_img
        template_processed = template_img
    
    # 尝试多尺度匹配
    if enable_multiscale:
        result = find_image_multiscale(
            screen_processed, 
            template_processed, 
            confidence,
            offset=(offset_x, offset_y)
        )
        
        if result:
            center_x, center_y, scale, conf = result
            print(f"Found at scale {scale:.2f}x with confidence {conf:.3f}")
            return (center_x, center_y)
    else:
        # 单尺度匹配
        result = cv2.matchTemplate(screen_processed, template_processed, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            template_h, template_w = template_processed.shape[:2]
            center_x = max_loc[0] + template_w // 2 + offset_x
            center_y = max_loc[1] + template_h // 2 + offset_y
            return (center_x, center_y)
    
    return None


def get_screen_color(x: int, y: int) -> Tuple[int, int, int]:
    """
    获取屏幕指定位置的颜色
    
    Args:
        x: X坐标
        y: Y坐标
    
    Returns:
        RGB 颜色值 (r, g, b)
    """
    import pyautogui
    
    # 截取 1x1 像素
    pixel = pyautogui.screenshot(region=(x, y, 1, 1))
    rgb = pixel.getpixel((0, 0))
    
    return rgb


def check_color_match(
    x: int,
    y: int,
    target_color: str,
    tolerance: int = 10
) -> bool:
    """
    检查指定位置的颜色是否匹配
    
    Args:
        x: X坐标
        y: Y坐标
        target_color: 目标颜色 (hex格式如 '#FF0000')
        tolerance: 容差值 (0-255)
    
    Returns:
        是否匹配
    """
    # 获取当前颜色
    current_rgb = get_screen_color(x, y)
    
    # 解析目标颜色
    target_color = target_color.lstrip('#')
    target_rgb = tuple(int(target_color[i:i+2], 16) for i in (0, 2, 4))
    
    # 检查每个通道的差异
    for c, t in zip(current_rgb, target_rgb):
        if abs(c - t) > tolerance:
            return False
    
    return True
