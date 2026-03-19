"""
逻辑类动作执行
"""
import time
from typing import Dict, Any
from utils.logger import log_manager


def execute_wait(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行等待操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    try:
        duration = params.get('duration', 1.0)
        
        log_manager.log(f"等待 {duration} 秒", 'info')
        
        time.sleep(duration)
        
        log_manager.log("等待完成", 'success')
        return {'success': True, 'output': 'next'}
    
    except Exception as e:
        log_manager.log(f"等待失败: {str(e)}", 'error')
        return {'success': False, 'output': 'next'}


def execute_condition(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行条件判断
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果，包含分支信息
    """
    try:
        condition = params.get('condition', '')
        
        log_manager.log(f"判断条件: {condition}", 'info')
        
        # 简单的条件评估（实际应该更安全）
        # 替换变量
        for key, value in context.items():
            condition = condition.replace(f'{{{key}}}', str(value))
        
        # 评估条件
        result = eval(condition)
        
        if result:
            log_manager.log("条件为真", 'success')
            return {'success': True, 'output': 'true'}
        else:
            log_manager.log("条件为假", 'info')
            return {'success': True, 'output': 'false'}
    
    except Exception as e:
        log_manager.log(f"条件判断失败: {str(e)}", 'error')
        return {'success': False, 'output': 'false'}


def execute_end(params: Dict[str, Any], context: Dict) -> Dict[str, Any]:
    """
    执行结束操作
    
    Args:
        params: 参数字典
        context: 执行上下文
    
    Returns:
        执行结果
    """
    log_manager.log("流程结束", 'success')
    return {'success': True, 'output': 'end'}
