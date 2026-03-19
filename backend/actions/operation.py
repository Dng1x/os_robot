"""
操作类动作执行
"""
import pyautogui
import time
import subprocess
from typing import Dict, Any
from utils.logger import log_manager
from utils.window_manager import activate_window, close_window


# PyAutoGUI 安全设置
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


def get_position(params: Dict[str, Any], context: Dict) -> tuple:
    """
    获取位置坐标
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        (x, y) 坐标元组
    """
    position_type = params.get('position_type', '使用变量')
    
    if position_type == '使用变量':
        position_var = params.get('position_var', 'position')
        offset_x = params.get('offset_x', 0)
        offset_y = params.get('offset_y', 0)
        
        # 从上下文获取变量
        pos = context.get(position_var)
        if pos and isinstance(pos, (tuple, list)) and len(pos) >= 2:
            return (pos[0] + offset_x, pos[1] + offset_y)
        else:
            raise ValueError(f"变量 {position_var} 不存在或格式错误")
    
    else:  # 固定坐标
        x = params.get('fixed_x', 0)
        y = params.get('fixed_y', 0)
        return (x, y)


def execute_click(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行点击操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        # 获取位置
        x, y = get_position(params, context)
        
        button = params.get('button', '左键')
        clicks = params.get('clicks', 1)
        
        # 转换按钮名称
        button_map = {'左键': 'left', '右键': 'right', '中键': 'middle'}
        pyautogui_button = button_map.get(button, 'left')
        
        log_manager.log(f"点击位置: ({x}, {y}), 按钮: {button}", 'info')
        
        pyautogui.click(x, y, clicks=clicks, button=pyautogui_button)
        
        log_manager.log("点击完成", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"点击失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_double_click(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行双击操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        x, y = get_position(params, context)
        
        log_manager.log(f"双击位置: ({x}, {y})", 'info')
        
        pyautogui.doubleClick(x, y)
        
        log_manager.log("双击完成", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"双击失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_drag(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行拖拽操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        # 获取起点
        from_type = params.get('from_type', '使用变量')
        if from_type == '使用变量':
            from_var = params.get('from_var', 'position')
            from_pos = context.get(from_var)
            if not from_pos:
                raise ValueError(f"变量 {from_var} 不存在")
            from_x, from_y = from_pos[0], from_pos[1]
        else:
            from_x = params.get('from_x', 0)
            from_y = params.get('from_y', 0)
        
        # 获取终点
        to_type = params.get('to_type', '固定坐标')
        if to_type == '使用变量':
            to_var = params.get('to_var', '')
            to_pos = context.get(to_var)
            if not to_pos:
                raise ValueError(f"变量 {to_var} 不存在")
            to_x, to_y = to_pos[0], to_pos[1]
        elif to_type == '相对偏移':
            to_x = from_x + params.get('to_x', 0)
            to_y = from_y + params.get('to_y', 0)
        else:
            to_x = params.get('to_x', 0)
            to_y = params.get('to_y', 0)
        
        duration = params.get('duration', 0.5)
        
        log_manager.log(f"拖拽: ({from_x}, {from_y}) → ({to_x}, {to_y})", 'info')
        
        pyautogui.moveTo(from_x, from_y)
        pyautogui.dragTo(to_x, to_y, duration=duration)
        
        log_manager.log("拖拽完成", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"拖拽失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_scroll(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行滚动操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        direction = params.get('direction', '向下')
        amount = params.get('amount', 100)
        
        # 转换滚动方向
        scroll_amount = -amount if direction == '向下' else amount
        
        log_manager.log(f"滚动: {direction} {amount}", 'info')
        
        pyautogui.scroll(scroll_amount)
        
        log_manager.log("滚动完成", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"滚动失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_type_text(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行输入文字操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        text = params.get('text', '')
        interval = params.get('interval', 0.1)
        
        log_manager.log(f"输入文字: {text[:20]}...", 'info')
        
        pyautogui.write(text, interval=interval)
        
        log_manager.log("输入完成", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"输入失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_hotkey(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行快捷键操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        keys = params.get('keys', '')
        
        log_manager.log(f"按下快捷键: {keys}", 'info')
        
        # 解析快捷键（如 'ctrl+c'）
        key_list = [k.strip() for k in keys.split('+')]
        pyautogui.hotkey(*key_list)
        
        log_manager.log("快捷键执行完成", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"快捷键执行失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_launch_program(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行启动程序操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        path = params.get('path', '')
        args = params.get('args', '')
        
        log_manager.log(f"启动程序: {path}", 'info')
        
        if args:
            subprocess.Popen([path] + args.split())
        else:
            subprocess.Popen([path])
        
        log_manager.log("程序启动成功", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"程序启动失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_activate_window(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行激活窗口操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        window = context.get('window_handle')
        
        if not window:
            log_manager.log("未找到窗口句柄", 'error')
            return {'success': False, 'output': 'next'}
        
        log_manager.log(f"激活窗口: {window.title}", 'info')
        
        success = activate_window(window)
        
        if success:
            log_manager.log("窗口激活成功", 'success')
            return {'success': True, 'output': 'next'}
        else:
            log_manager.log("窗口激活失败", 'error')
            return {'success': False, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"激活窗口失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_close_window(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行关闭窗口操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        window = context.get('window_handle')
        
        if not window:
            log_manager.log("未找到窗口句柄", 'error')
            return {'success': False, 'output': 'next'}
        
        log_manager.log(f"关闭窗口: {window.title}", 'info')
        
        success = close_window(window)
        
        if success:
            log_manager.log("窗口关闭成功", 'success')
            return {'success': True, 'output': 'next'}
        else:
            log_manager.log("窗口关闭失败", 'error')
            return {'success': False, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"关闭窗口失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}
