"""
日志处理工具
"""
import logging
from datetime import datetime
from typing import List
from queue import Queue

# 全局日志队列
log_queue = Queue()


class LogManager:
    """日志管理器"""
    
    def __init__(self):
        self.logs: List[dict] = []
        self.setup_logger()
    
    def setup_logger(self):
        """设置日志记录器"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def log(self, message: str, level: str = 'info'):
        """记录日志"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message
        }
        
        self.logs.append(log_entry)
        log_queue.put(log_entry)
        
        # 同时输出到控制台
        if level == 'error':
            self.logger.error(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'success':
            self.logger.info(f'✓ {message}')
        else:
            self.logger.info(message)
    
    def get_logs(self) -> List[dict]:
        """获取所有日志"""
        return self.logs
    
    def clear_logs(self):
        """清空日志"""
        self.logs.clear()
        # 清空队列
        while not log_queue.empty():
            log_queue.get()


# 全局日志管理器实例
log_manager = LogManager()
