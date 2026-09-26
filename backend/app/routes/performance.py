"""
性能监控相关API路由
"""
from fastapi import APIRouter
from app.utils.performance_monitor import PerformanceMonitor

router = APIRouter(prefix="/performance", tags=["性能监控"])

# 全局性能监控实例
perf_monitor = PerformanceMonitor()


@router.get("/status")
async def get_performance_status():
    """获取性能状态"""
    return perf_monitor.get_performance_report()


@router.get("/resources")
async def get_resource_usage():
    """获取资源使用情况"""
    return perf_monitor.resource_manager.get_system_resources()


@router.get("/concurrency")
async def get_concurrency_settings():
    """获取并发设置"""
    return {
        'current_concurrency': perf_monitor.adaptive_concurrency.current_concurrency,
        'min_concurrency': perf_monitor.adaptive_concurrency.min_concurrency,
        'max_concurrency': perf_monitor.adaptive_concurrency.max_concurrency,
        'avg_response_time': perf_monitor.adaptive_concurrency.get_average_response_time()
    }


@router.post("/concurrency/adjust")
async def adjust_concurrency():
    """手动调整并发数"""
    perf_monitor.adaptive_concurrency.adjust_concurrency(
        perf_monitor.resource_manager
    )
    return {
        'new_concurrency': perf_monitor.adaptive_concurrency.current_concurrency
    }
