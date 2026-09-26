"""
性能优化和资源管理模块
"""
import asyncio
import time
import psutil
from typing import Dict, Optional
from datetime import datetime
from loguru import logger


class ResourceManager:
    """资源管理器"""
    
    def __init__(
        self,
        max_cpu_percent: float = 80.0,
        max_memory_percent: float = 80.0,
        check_interval: float = 5.0
    ):
        self.max_cpu_percent = max_cpu_percent
        self.max_memory_percent = max_memory_percent
        self.check_interval = check_interval
        self.process = psutil.Process()
        self.resource_history: list = []
    
    def get_cpu_usage(self) -> float:
        """获取CPU使用率"""
        return self.process.cpu_percent(interval=0.1)
    
    def get_memory_usage(self) -> Dict[str, float]:
        """获取内存使用情况"""
        memory_info = self.process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # MB
            'vms_mb': memory_info.vms / 1024 / 1024,  # MB
            'percent': self.process.memory_percent()
        }
    
    def get_system_resources(self) -> Dict:
        """获取系统资源使用情况"""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        return {
            'cpu_percent': cpu_percent,
            'memory_total_gb': memory.total / 1024 / 1024 / 1024,
            'memory_available_gb': memory.available / 1024 / 1024 / 1024,
            'memory_percent': memory.percent,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_resource_limits(self) -> Dict[str, bool]:
        """检查资源是否超过限制"""
        cpu_usage = self.get_cpu_usage()
        memory_usage = self.get_memory_usage()
        
        limits = {
            'cpu_ok': cpu_usage < self.max_cpu_percent,
            'memory_ok': memory_usage['percent'] < self.max_memory_percent
        }
        
        if not limits['cpu_ok']:
            logger.warning(f"CPU使用率过高: {cpu_usage}% (限制: {self.max_cpu_percent}%)")
        
        if not limits['memory_ok']:
            logger.warning(f"内存使用率过高: {memory_usage['percent']}% (限制: {self.max_memory_percent}%)")
        
        # 记录历史
        self.resource_history.append({
            'cpu': cpu_usage,
            'memory': memory_usage['percent'],
            'timestamp': datetime.now().isoformat()
        })
        
        # 只保留最近100条记录
        if len(self.resource_history) > 100:
            self.resource_history = self.resource_history[-100:]
        
        return limits
    
    def get_resource_summary(self) -> Dict:
        """获取资源使用摘要"""
        if not self.resource_history:
            return {}
        
        cpu_values = [r['cpu'] for r in self.resource_history]
        memory_values = [r['memory'] for r in self.resource_history]
        
        return {
            'avg_cpu': sum(cpu_values) / len(cpu_values),
            'max_cpu': max(cpu_values),
            'avg_memory': sum(memory_values) / len(memory_values),
            'max_memory': max(memory_values),
            'current': self.get_system_resources()
        }


class AdaptiveConcurrency:
    """自适应并发控制器"""
    
    def __init__(
        self,
        min_concurrency: int = 1,
        max_concurrency: int = 50,
        initial_concurrency: int = 10,
        adjustment_threshold: float = 0.8
    ):
        self.min_concurrency = min_concurrency
        self.max_concurrency = max_concurrency
        self.current_concurrency = initial_concurrency
        self.adjustment_threshold = adjustment_threshold
        self.response_times: list = []
        self.last_adjustment_time = time.time()
        self.adjustment_cooldown = 10  # 调整冷却时间（秒）
    
    def record_response_time(self, response_time: float):
        """记录响应时间"""
        self.response_times.append(response_time)
        
        # 只保留最近50个响应时间
        if len(self.response_times) > 50:
            self.response_times = self.response_times[-50:]
    
    def get_average_response_time(self) -> float:
        """获取平均响应时间"""
        if not self.response_times:
            return 0
        
        return sum(self.response_times) / len(self.response_times)
    
    def should_adjust(self) -> bool:
        """是否应该调整并发数"""
        return (time.time() - self.last_adjustment_time) > self.adjustment_cooldown
    
    def adjust_concurrency(self, resource_manager: ResourceManager):
        """根据资源使用情况调整并发数"""
        if not self.should_adjust():
            return
        
        resources = resource_manager.get_system_resources()
        avg_response = self.get_average_response_time()
        
        old_concurrency = self.current_concurrency
        
        # CPU或内存使用率过高时，降低并发
        if resources['cpu_percent'] > 80 or resources['memory_percent'] > 80:
            self.current_concurrency = max(
                self.min_concurrency,
                self.current_concurrency - 5
            )
            logger.info(f"资源使用率高，降低并发: {old_concurrency} -> {self.current_concurrency}")
        
        # 响应时间过长时，降低并发
        elif avg_response > 5.0:  # 平均响应时间超过5秒
            self.current_concurrency = max(
                self.min_concurrency,
                self.current_concurrency - 3
            )
            logger.info(f"响应时间过长，降低并发: {old_concurrency} -> {self.current_concurrency}")
        
        # 资源充足且响应快时，提高并发
        elif resources['cpu_percent'] < 50 and resources['memory_percent'] < 50 and avg_response < 1.0:
            self.current_concurrency = min(
                self.max_concurrency,
                self.current_concurrency + 5
            )
            logger.info(f"资源充足，提高并发: {old_concurrency} -> {self.current_concurrency}")
        
        self.last_adjustment_time = time.time()
    
    def get_semaphore(self) -> asyncio.Semaphore:
        """获取信号量"""
        return asyncio.Semaphore(self.current_concurrency)


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.resource_manager = ResourceManager()
        self.adaptive_concurrency = AdaptiveConcurrency()
        self.start_time = None
        self.metrics: Dict = {}
    
    def start_monitoring(self):
        """开始监控"""
        self.start_time = time.time()
        logger.info("性能监控已启动")
    
    def get_elapsed_time(self) -> float:
        """获取已用时间（秒）"""
        if not self.start_time:
            return 0
        return time.time() - self.start_time
    
    def format_elapsed_time(self) -> str:
        """格式化已用时间"""
        elapsed = self.get_elapsed_time()
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        if hours > 0:
            return f"{hours}小时{minutes}分钟{seconds}秒"
        elif minutes > 0:
            return f"{minutes}分钟{seconds}秒"
        else:
            return f"{seconds}秒"
    
    def estimate_remaining_time(
        self,
        total_items: int,
        completed_items: int
    ) -> Optional[float]:
        """估算剩余时间"""
        if completed_items == 0 or not self.start_time:
            return None
        
        elapsed = self.get_elapsed_time()
        items_per_second = completed_items / elapsed
        remaining_items = total_items - completed_items
        
        if items_per_second > 0:
            return remaining_items / items_per_second
        
        return None
    
    def get_performance_report(self) -> Dict:
        """获取性能报告"""
        return {
            'elapsed_time': self.format_elapsed_time(),
            'elapsed_seconds': self.get_elapsed_time(),
            'resources': self.resource_manager.get_resource_summary(),
            'concurrency': self.adaptive_concurrency.current_concurrency,
            'avg_response_time': self.adaptive_concurrency.get_average_response_time()
        }
