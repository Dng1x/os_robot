"""
数据类动作执行
"""
import pyperclip
from typing import Dict, Any
from utils.logger import log_manager


def execute_variable(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行变量操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        mode = params.get('mode', '设置变量')
        
        if mode == '设置变量':
            assignment = params.get('assignment', '')
            
            log_manager.log(f"执行赋值: {assignment}", 'info')
            
            # 解析赋值等式（如: my_pos = position）
            if '=' in assignment:
                left, right = assignment.split('=', 1)
                var_name = left.strip()
                source = right.strip()
                
                # 从上下文获取源变量的值
                if source in context:
                    value = context[source]
                    context[var_name] = value
                    log_manager.log(f"变量 {var_name} = {value}", 'success')
                else:
                    # 尝试评估表达式
                    try:
                        # 替换上下文中的变量
                        for key, val in context.items():
                            source = source.replace(key, repr(val))
                        value = eval(source)
                        context[var_name] = value
                        log_manager.log(f"变量 {var_name} = {value}", 'success')
                    except:
                        log_manager.log(f"无法解析赋值: {assignment}", 'error')
                        return {'success': False, 'output': 'next'}
            
        else:  # 读取变量
            read_var = params.get('read_var', '')
            if read_var in context:
                value = context[read_var]
                log_manager.log(f"读取变量 {read_var} = {value}", 'info')
            else:
                log_manager.log(f"变量 {read_var} 不存在", 'warning')
        
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"变量操作失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_clipboard_copy(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行复制到剪贴板操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        content = params.get('content', '')
        
        # 替换变量
        for key, value in context.items():
            content = content.replace(f'{{{key}}}', str(value))
        
        log_manager.log(f"复制到剪贴板: {content[:50]}...", 'info')
        
        pyperclip.copy(content)
        
        log_manager.log("复制成功", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"复制失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_clipboard_paste(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行从剪贴板粘贴操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        log_manager.log("从剪贴板获取内容", 'info')
        
        content = pyperclip.paste()
        context['clipboard_content'] = content
        
        log_manager.log(f"获取内容: {content[:50]}...", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"粘贴失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_message_box(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行弹窗提示操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        import tkinter as tk
        from tkinter import messagebox
        
        content = params.get('content', '')
        title = params.get('title', '提示')
        
        # 替换变量
        for key, value in context.items():
            content = content.replace(f'{{{key}}}', str(value))
        
        log_manager.log(f"显示弹窗: {title}", 'info')
        
        # 创建隐藏的主窗口
        root = tk.Tk()
        root.withdraw()
        
        # 显示消息框
        messagebox.showinfo(title, content)
        
        root.destroy()
        
        log_manager.log("弹窗已关闭", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"弹窗显示失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_log(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行日志记录操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        content = params.get('content', '')
        level = params.get('level', '信息')
        
        # 替换变量
        for key, value in context.items():
            content = content.replace(f'{{{key}}}', str(value))
        
        # 转换级别
        level_map = {'信息': 'info', '警告': 'warning', '错误': 'error'}
        log_level = level_map.get(level, 'info')
        
        log_manager.log(content, log_level)
        
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"日志记录失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_screenshot(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行截图操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        import pyautogui
        
        path = params.get('path', 'screenshot.png')
        region = params.get('region')
        
        log_manager.log(f"截图保存到: {path}", 'info')
        
        if region:
            parts = [int(x.strip()) for x in region.split(',')]
            if len(parts) == 4:
                screenshot = pyautogui.screenshot(region=tuple(parts))
            else:
                screenshot = pyautogui.screenshot()
        else:
            screenshot = pyautogui.screenshot()
        
        screenshot.save(path)
        
        log_manager.log("截图成功", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"截图失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}
