"""
流程执行器 - 解析和执行自动化流程
"""
from typing import Dict, List, Any
from utils.logger import log_manager
from actions import *


# 动作执行函数映射
ACTION_MAP = {
    # 识别类
    'find_image': execute_find_image,
    'find_text': execute_find_text,
    'find_window': execute_find_window,
    'check_color': execute_check_color,
    
    # 操作类
    'click': execute_click,
    'double_click': execute_double_click,
    'drag': execute_drag,
    'scroll': execute_scroll,
    'type_text': execute_type_text,
    'hotkey': execute_hotkey,
    'launch_program': execute_launch_program,
    'activate_window': execute_activate_window,
    'close_window': execute_close_window,
    
    # 逻辑类
    'wait': execute_wait,
    'condition': execute_condition,
    'end': execute_end,
    
    # 数据类
    'variable': execute_variable,
    'clipboard_copy': execute_clipboard_copy,
    'clipboard_paste': execute_clipboard_paste,
    'message_box': execute_message_box,
    'log': execute_log,
    'screenshot': execute_screenshot
}


class FlowExecutor:
    """流程执行器"""
    
    def __init__(self, flow_data: Dict):
        """
        初始化执行器
        
        Args:
            flow_data: 流程数据
        """
        self.flow_data = flow_data
        self.nodes = {node['id']: node for node in flow_data.get('nodes', [])}
        self.connections = flow_data.get('connections', [])
        self.assets = flow_data.get('assets', [])
        self.context = {}  # 执行上下文（存储变量）
        self.is_running = False
        self.node_pass_count = {}  # 记录每个节点的经过次数
    
    def find_next_node(self, current_node_id: str, output: str = 'next') -> str:
        """
        根据输出找到下一个节点
        
        Args:
            current_node_id: 当前节点ID
            output: 输出类型 ('next', 'success', 'failure', 'true', 'false', etc.)
        
        Returns:
            下一个节点ID，如果没有则返回 None
        """
        # 查找连接
        for conn in self.connections:
            if conn['source'] == current_node_id:
                # 匹配输出句柄
                if conn.get('sourceHandle') == output or output == 'next':
                    return conn['target']
        
        return None
    
    def execute_node(self, node_id: str) -> Dict[str, Any]:
        """
        执行单个节点
        
        Args:
            node_id: 节点ID
        
        Returns:
            执行结果
        """
        if node_id not in self.nodes:
            log_manager.log(f"节点不存在: {node_id}", 'error')
            return {'success': False, 'output': 'next'}
        
        node = self.nodes[node_id]
        node_type = node['data']['type']
        params = node['data'].get('params', {})
        
        # 检查经过次数（开始和结束节点不检查）
        if node_type not in ['start', 'end']:
            # 增加经过次数
            self.node_pass_count[node_id] = self.node_pass_count.get(node_id, 0) + 1
            
            # 获取最大经过次数配置
            max_passes = params.get('max_passes', 999999)
            
            # 检查是否超过限制
            if self.node_pass_count[node_id] > max_passes:
                log_manager.log(
                    f"节点 {node_type} ({node_id}) 已达到最大经过次数 {max_passes}，终止流程",
                    'warning'
                )
                return {'success': False, 'output': 'end'}
        
        log_manager.log(f"执行节点: {node_type} ({node_id})", 'info')
        
        # 特殊处理开始节点
        if node_type == 'start':
            log_manager.log("流程开始", 'info')
            return {'success': True, 'output': 'next'}
        
        # 查找执行函数
        if node_type not in ACTION_MAP:
            log_manager.log(f"不支持的节点类型: {node_type}", 'error')
            return {'success': False, 'output': 'next'}
        
        # 执行动作
        execute_func = ACTION_MAP[node_type]
        
        try:
            # 根据节点类型传递不同参数
            if node_type in ['find_image']:
                result = execute_func(params, self.assets, self.context)
            else:
                result = execute_func(params, self.context)
            
            return result
        
        except Exception as e:
            log_manager.log(f"节点执行异常: {str(e)}", 'error')
            return {'success': False, 'output': 'next'}
    
    def execute(self) -> Dict[str, Any]:
        """
        执行整个流程
        
        Returns:
            执行结果
        """
        log_manager.clear_logs()
        log_manager.log("=" * 50, 'info')
        log_manager.log(f"开始执行流程: {self.flow_data.get('name', '未命名')}", 'info')
        log_manager.log("=" * 50, 'info')
        
        self.is_running = True
        
        # 查找开始节点
        start_node = None
        for node in self.nodes.values():
            if node['data']['type'] == 'start':
                start_node = node
                break
        
        if not start_node:
            log_manager.log("未找到开始节点", 'error')
            return {
                'success': False,
                'message': '未找到开始节点',
                'logs': log_manager.get_logs()
            }
        
        # 从开始节点执行
        current_node_id = start_node['id']
        max_steps = 1000  # 防止无限循环
        steps = 0
        
        while current_node_id and steps < max_steps:
            if not self.is_running:
                log_manager.log("流程已停止", 'warning')
                break
            
            # 执行当前节点
            result = self.execute_node(current_node_id)
            
            # 检查是否结束
            if result.get('output') == 'end':
                log_manager.log("流程正常结束", 'success')
                break
            
            # 查找下一个节点
            output_type = result.get('output', 'next')
            next_node_id = self.find_next_node(current_node_id, output_type)
            
            if not next_node_id:
                log_manager.log("已到达流程末尾", 'info')
                break
            
            current_node_id = next_node_id
            steps += 1
        
        if steps >= max_steps:
            log_manager.log("流程执行超过最大步数限制", 'error')
        
        log_manager.log("=" * 50, 'info')
        log_manager.log("流程执行完成", 'success')
        log_manager.log("=" * 50, 'info')
        
        self.is_running = False
        
        return {
            'success': True,
            'message': '流程执行完成',
            'logs': log_manager.get_logs()
        }
    
    def stop(self):
        """停止执行"""
        self.is_running = False
        log_manager.log("收到停止信号", 'warning')
