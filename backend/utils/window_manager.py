"""
窗口管理工具
"""
import pygetwindow as gw
import re
from typing import Optional, List


def find_window(
    title: str,
    match_mode: str = '包含'
) -> Optional[object]:
    """
    根据标题查找窗口
    
    Args:
        title: 窗口标题
        match_mode: 匹配模式 ('完全匹配', '包含', '正则')
    
    Returns:
        窗口对象，未找到返回 None
    """
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
    """
    激活窗口
    
    Args:
        window: 窗口对象
    
    Returns:
        是否成功
    """
    try:
        if window.isMinimized:
            window.restore()
        window.activate()
        return True
    except Exception as e:
        print(f"激活窗口失败: {e}")
        return False


def close_window(window) -> bool:
    """
    关闭窗口
    
    Args:
        window: 窗口对象
    
    Returns:
        是否成功
    """
    try:
        window.close()
        return True
    except Exception as e:
        print(f"关闭窗口失败: {e}")
        return False


def get_window_list() -> List[str]:
    """
    获取所有窗口标题列表
    
    Returns:
        窗口标题列表
    """
    return gw.getAllTitles()
