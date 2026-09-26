"""
进度监控和实时反馈模块
"""
import asyncio
from typing import Dict, Optional, List, Callable
from datetime import datetime
from loguru import logger
from enum import Enum


class ScanStatus(str, Enum):
    """扫描状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"
    PAUSED = "paused"


class ProgressInfo:
    """进度信息"""
    
    def __init__(self, scan_id: str):
        self.scan_id = scan_id
        self.status = ScanStatus.PENDING
        self.progress_percentage = 0
        self.current_url = ""
        self.current_module = ""
        self.total_urls = 0
        self.scanned_urls = 0
        self.total_modules = 0
        self.completed_modules = 0
        self.vulnerabilities_found = 0
        self.start_time: Optional[datetime] = None
        self.estimated_end_time: Optional[datetime] = None
        self.messages: List[str] = []
        self.errors: List[str] = []
    
    def update_progress(
        self,
        percentage: int = None,
        current_url: str = None,
        current_module: str = None,
        message: str = None
    ):
        """更新进度"""
        if percentage is not None:
            self.progress_percentage = min(100, max(0, percentage))
        
        if current_url:
            self.current_url = current_url
        
        if current_module:
            self.current_module = current_module
        
        if message:
            self.messages.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
            # 只保留最近100条消息
            if len(self.messages) > 100:
                self.messages = self.messages[-100:]
        
        logger.debug(f"进度更新 [{self.scan_id}]: {percentage}% - {current_module} - {current_url}")
    
    def add_vulnerability(self):
        """添加漏洞计数"""
        self.vulnerabilities_found += 1
    
    def add_error(self, error: str):
        """添加错误信息"""
        self.errors.append(f"[{datetime.now().strftime('%H:%M:%S')}] {error}")
        logger.error(f"扫描错误 [{self.scan_id}]: {error}")
    
    def calculate_eta(self):
        """计算预计完成时间"""
        if not self.start_time or self.progress_percentage == 0:
            return None
        
        elapsed = datetime.now() - self.start_time
        if self.progress_percentage > 0:
            total_estimated = elapsed.total_seconds() / (self.progress_percentage / 100)
            remaining = total_estimated - elapsed.total_seconds()
            self.estimated_end_time = datetime.now() + __import__('datetime').timedelta(seconds=remaining)
            return remaining
        
        return None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'scan_id': self.scan_id,
            'status': self.status.value,
            'progress_percentage': self.progress_percentage,
            'current_url': self.current_url,
            'current_module': self.current_module,
            'total_urls': self.total_urls,
            'scanned_urls': self.scanned_urls,
            'total_modules': self.total_modules,
            'completed_modules': self.completed_modules,
            'vulnerabilities_found': self.vulnerabilities_found,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'estimated_end_time': self.estimated_end_time.isoformat() if self.estimated_end_time else None,
            'messages': self.messages[-20:],  # 返回最近20条消息
            'errors': self.errors[-10:]  # 返回最近10条错误
        }


class ProgressManager:
    """进度管理器"""
    
    def __init__(self):
        self.progress_info: Dict[str, ProgressInfo] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
    
    def create_progress(self, scan_id: str) -> ProgressInfo:
        """创建进度跟踪器"""
        progress = ProgressInfo(scan_id)
        progress.start_time = datetime.now()
        self.progress_info[scan_id] = progress
        self.callbacks[scan_id] = []
        
        logger.info(f"创建进度跟踪器: {scan_id}")
        return progress
    
    def get_progress(self, scan_id: str) -> Optional[ProgressInfo]:
        """获取进度信息"""
        return self.progress_info.get(scan_id)
    
    def update_progress(
        self,
        scan_id: str,
        **kwargs
    ) -> bool:
        """更新进度"""
        progress = self.progress_info.get(scan_id)
        if not progress:
            return False
        
        progress.update_progress(**kwargs)
        
        # 通知回调
        self._notify_callbacks(scan_id, progress)
        
        return True
    
    def set_status(self, scan_id: str, status: ScanStatus):
        """设置状态"""
        progress = self.progress_info.get(scan_id)
        if progress:
            progress.status = status
            
            if status == ScanStatus.RUNNING and not progress.start_time:
                progress.start_time = datetime.now()
            elif status in [ScanStatus.COMPLETED, ScanStatus.FAILED, ScanStatus.STOPPED]:
                progress.progress_percentage = 100
            
            self._notify_callbacks(scan_id, progress)
    
    def register_callback(self, scan_id: str, callback: Callable):
        """注册进度回调"""
        if scan_id not in self.callbacks:
            self.callbacks[scan_id] = []
        
        self.callbacks[scan_id].append(callback)
        logger.debug(f"注册进度回调: {scan_id}")
    
    def unregister_callback(self, scan_id: str, callback: Callable):
        """取消注册回调"""
        if scan_id in self.callbacks:
            self.callbacks[scan_id].remove(callback)
    
    def _notify_callbacks(self, scan_id: str, progress: ProgressInfo):
        """通知回调"""
        if scan_id in self.callbacks:
            for callback in self.callbacks[scan_id]:
                try:
                    callback(progress.to_dict())
                except Exception as e:
                    logger.error(f"回调执行失败: {str(e)}")
    
    def remove_progress(self, scan_id: str):
        """移除进度跟踪器"""
        if scan_id in self.progress_info:
            del self.progress_info[scan_id]
        if scan_id in self.callbacks:
            del self.callbacks[scan_id]
    
    def list_all_progress(self) -> List[Dict]:
        """列出所有进度"""
        return [info.to_dict() for info in self.progress_info.values()]
