"""
错误处理和容错机制模块
"""
import asyncio
from typing import Optional, Callable, Any, Dict
from datetime import datetime
from loguru import logger
from enum import Enum


class ErrorSeverity(str, Enum):
    """错误严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ScanError:
    """扫描错误"""
    
    def __init__(
        self,
        error_type: str,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.LOW,
        recoverable: bool = True,
        context: Dict = None
    ):
        self.error_type = error_type
        self.message = message
        self.severity = severity
        self.recoverable = recoverable
        self.context = context or {}
        self.timestamp = datetime.now()
        self.attempt_count = 0
    
    def to_dict(self) -> Dict:
        return {
            'error_type': self.error_type,
            'message': self.message,
            'severity': self.severity.value,
            'recoverable': self.recoverable,
            'timestamp': self.timestamp.isoformat(),
            'attempt_count': self.attempt_count,
            'context': self.context
        }


class ErrorHandler:
    """错误处理器"""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.errors: list = []
        self.critical_errors: list = []
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        error_context: str = "",
        **kwargs
    ) -> Any:
        """带重试的执行函数"""
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                
                if attempt > 1:
                    logger.info(f"重试成功: {error_context} (第{attempt}次尝试)")
                
                return result
            
            except Exception as e:
                last_error = e
                scan_error = ScanError(
                    error_type=type(e).__name__,
                    message=str(e),
                    severity=ErrorSeverity.MEDIUM if attempt < self.max_retries else ErrorSeverity.HIGH,
                    recoverable=attempt < self.max_retries,
                    context={'context': error_context, 'attempt': attempt}
                )
                scan_error.attempt_count = attempt
                
                self.errors.append(scan_error)
                logger.warning(f"执行失败 [{error_context}] (尝试 {attempt}/{self.max_retries}): {str(e)}")
                
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * attempt  # 指数退避
                    logger.debug(f"等待 {wait_time}秒后重试...")
                    await asyncio.sleep(wait_time)
        
        # 所有重试都失败
        critical_error = ScanError(
            error_type=type(last_error).__name__,
            message=f"多次重试后仍然失败: {str(last_error)}",
            severity=ErrorSeverity.CRITICAL,
            recoverable=False,
            context={'context': error_context, 'max_attempts': self.max_retries}
        )
        self.critical_errors.append(critical_error)
        logger.error(f"关键错误 [{error_context}]: {str(last_error)}")
        
        raise last_error
    
    def handle_error_gracefully(
        self,
        func: Callable,
        *args,
        default_value: Any = None,
        error_context: str = "",
        **kwargs
    ) -> Any:
        """优雅地处理错误，返回默认值"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            scan_error = ScanError(
                error_type=type(e).__name__,
                message=str(e),
                severity=ErrorSeverity.LOW,
                recoverable=True,
                context={'context': error_context}
            )
            self.errors.append(scan_error)
            
            logger.warning(f"错误已捕获并处理 [{error_context}]: {str(e)}")
            return default_value
    
    async def handle_async_error_gracefully(
        self,
        func: Callable,
        *args,
        default_value: Any = None,
        error_context: str = "",
        **kwargs
    ) -> Any:
        """优雅地处理异步错误"""
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            scan_error = ScanError(
                error_type=type(e).__name__,
                message=str(e),
                severity=ErrorSeverity.LOW,
                recoverable=True,
                context={'context': error_context}
            )
            self.errors.append(scan_error)
            
            logger.warning(f"异步错误已捕获并处理 [{error_context}]: {str(e)}")
            return default_value
    
    def get_error_summary(self) -> Dict:
        """获取错误摘要"""
        return {
            'total_errors': len(self.errors),
            'critical_errors': len(self.critical_errors),
            'recent_errors': [e.to_dict() for e in self.errors[-10:]],
            'critical_error_list': [e.to_dict() for e in self.critical_errors]
        }
    
    def clear_errors(self):
        """清除错误记录"""
        self.errors.clear()
        self.critical_errors.clear()
    
    def has_critical_errors(self) -> bool:
        """检查是否有严重错误"""
        return len(self.critical_errors) > 0


class CrashRecovery:
    """崩溃恢复管理器"""
    
    def __init__(self, state_file: str = "data/scan_state.json"):
        self.state_file = state_file
        self.checkpoint_interval = 60  # 每60秒保存一次状态
    
    async def save_checkpoint(self, scan_id: str, state: Dict):
        """保存检查点"""
        import json
        from pathlib import Path
        
        try:
            checkpoint = {
                'scan_id': scan_id,
                'timestamp': datetime.now().isoformat(),
                'state': state
            }
            
            Path(self.state_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"检查点已保存: {scan_id}")
        
        except Exception as e:
            logger.error(f"保存检查点失败: {str(e)}")
    
    async def load_checkpoint(self, scan_id: str) -> Optional[Dict]:
        """加载检查点"""
        import json
        from pathlib import Path
        
        try:
            if not Path(self.state_file).exists():
                return None
            
            with open(self.state_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            
            if checkpoint.get('scan_id') == scan_id:
                logger.info(f"找到检查点: {scan_id}")
                return checkpoint.get('state')
            
            return None
        
        except Exception as e:
            logger.error(f"加载检查点失败: {str(e)}")
            return None
    
    async def cleanup_checkpoint(self):
        """清理检查点"""
        from pathlib import Path
        
        try:
            if Path(self.state_file).exists():
                Path(self.state_file).unlink()
                logger.info("检查点已清理")
        except Exception as e:
            logger.error(f"清理检查点失败: {str(e)}")
