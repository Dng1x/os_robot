"""
识别类动作执行
"""
from typing import Dict, Any, Optional, Tuple
from utils.image_match import find_image_on_screen, check_color_match
from utils.window_manager import find_window
from utils.logger import log_manager


def execute_find_image(params: Dict[str, Any], assets: list, context: Dict) -> Dict[str, Any]:
    """
    执行找图动作
    
    Args:
        params: 参数字典
        assets: 素材列表
        context: 执行上下文（存储变量）
    
    Returns:
        执行结果 {'success': bool, 'found': bool, 'position': tuple, 'output': str}
    """
    image_name = params.get('image')
    confidence = params.get('confidence', 0.8)
    timeout = params.get('timeout', 5)
    region = params.get('region')
    
    # 查找素材
    asset = next((a for a in assets if a['name'] == image_name), None)
    if not asset:
        log_manager.log(f"找不到素材: {image_name}", 'error')
        context['found'] = False
        context['position'] = None
        return {'success': True, 'found': False, 'position': None, 'output': 'failure'}
    
    log_manager.log(f"正在查找图片: {image_name}，精度: {confidence}", 'info')
    
    # 解析搜索区域
    search_region = None
    if region:
        try:
            parts = [int(x.strip()) for x in region.split(',')]
            if len(parts) == 4:
                search_region = tuple(parts)
        except:
            pass
    
    # 执行图像搜索（带超时）
    import time
    start_time = time.time()
    position = None
    
    while time.time() - start_time < timeout:
        position = find_image_on_screen(
            asset['path'],
            confidence,
            search_region
        )
        
        if position:
            break
        
        time.sleep(0.5)
    
    if position:
        # 找到图片 - 从 success 出口输出
        log_manager.log(f"找到图片，位置: {position}", 'success')
        context['found'] = True
        context['position'] = position
        return {
            'success': True,
            'found': True,
            'position': position,
            'output': 'success'  # 从成功出口
        }
    else:
        # 未找到图片 - 从 failure 出口输出
        log_manager.log(f"未找到图片: {image_name}", 'warning')
        context['found'] = False
        context['position'] = None
        return {
            'success': True,
            'found': False,
            'position': None,
            'output': 'failure'  # 从失败出口
        }


def execute_find_text(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行 OCR 文字识别
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    text = params.get('text')
    region = params.get('region')
    language = params.get('language', '中英混合')
    
    log_manager.log(f"正在识别文字: {text}", 'info')
    
    try:
        from paddleocr import PaddleOCR
        import pyautogui
        import numpy as np
        
        # 初始化 OCR
        use_lang = 'ch' if '中文' in language else 'en'
        ocr = PaddleOCR(use_angle_cls=True, lang=use_lang, show_log=False)
        
        # 截图
        if region:
            parts = [int(x.strip()) for x in region.split(',')]
            if len(parts) == 4:
                screenshot = pyautogui.screenshot(region=tuple(parts))
            else:
                screenshot = pyautogui.screenshot()
        else:
            screenshot = pyautogui.screenshot()
        
        # 转换为 numpy 数组
        img_array = np.array(screenshot)
        
        # OCR 识别
        result = ocr.ocr(img_array, cls=True)
        
        # 查找目标文字
        found = False
        position = None
        recognized_text = ""
        
        if result and result[0]:
            for line in result[0]:
                detected_text = line[1][0]
                recognized_text += detected_text + " "
                
                if text in detected_text:
                    # 计算文字中心位置
                    box = line[0]
                    x = int(sum([p[0] for p in box]) / 4)
                    y = int(sum([p[1] for p in box]) / 4)
                    position = (x, y)
                    found = True
                    break
        
        if found:
            log_manager.log(f"找到文字，位置: {position}", 'success')
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
            log_manager.log(f"未找到文字: {text}", 'warning')
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
        log_manager.log(f"OCR 识别失败: {str(e)}", 'error')
        return {
            'success': False,
            'found': False,
            'position': None,
            'output': 'failure'
        }


def execute_find_window(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行查找窗口
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    title = params.get('title')
    match_mode = params.get('match_mode', '包含')
    
    log_manager.log(f"正在查找窗口: {title}", 'info')
    
    window = find_window(title, match_mode)
    
    if window:
        log_manager.log(f"找到窗口: {window.title}", 'success')
        context['found'] = True
        context['window_handle'] = window
        return {
            'success': True,
            'found': True,
            'window_handle': window,
            'output': 'success'
        }
    else:
        log_manager.log(f"未找到窗口: {title}", 'warning')
        context['found'] = False
        context['window_handle'] = None
        return {
            'success': False,
            'found': False,
            'window_handle': None,
            'output': 'failure'
        }


def execute_check_color(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行颜色检查
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    position = params.get('position')
    color = params.get('color', '#FF0000')
    tolerance = params.get('tolerance', 10)
    
    # 解析位置
    try:
        x, y = [int(p.strip()) for p in position.split(',')]
    except:
        log_manager.log(f"位置格式错误: {position}", 'error')
        return {'success': False, 'matched': False, 'output': 'failure'}
    
    log_manager.log(f"检查位置 ({x}, {y}) 的颜色", 'info')
    
    matched = check_color_match(x, y, color, tolerance)
    
    if matched:
        log_manager.log(f"颜色匹配", 'success')
        context['matched'] = True
        return {'success': True, 'matched': True, 'output': 'success'}
    else:
        log_manager.log(f"颜色不匹配", 'warning')
        context['matched'] = False
        return {'success': False, 'matched': False, 'output': 'failure'}
