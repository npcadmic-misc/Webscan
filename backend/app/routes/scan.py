"""
扫描相关API路由
"""
from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from datetime import datetime

from app.models.scan_target import ScanConfig
from app.models.vulnerability import ScanResult

router = APIRouter(prefix="/scan", tags=["扫描"])

# 临时存储扫描任务（实际应该用数据库或消息队列）
active_scans = {}


@router.post("/start")
async def start_scan(config: ScanConfig):
    """启动扫描任务"""
    scan_id = str(uuid.uuid4())
    
    # 创建扫描任务
    scan_task = {
        "scan_id": scan_id,
        "config": config.dict(),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
        "progress": 0
    }
    
    active_scans[scan_id] = scan_task
    
    # TODO: 实际启动扫描逻辑
    
    return {
        "scan_id": scan_id,
        "message": "扫描任务已创建",
        "status": "pending"
    }


@router.get("/{scan_id}/status")
async def get_scan_status(scan_id: str):
    """获取扫描任务状态"""
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail="扫描任务不存在")
    
    return active_scans[scan_id]


@router.post("/{scan_id}/stop")
async def stop_scan(scan_id: str):
    """停止扫描任务"""
    if scan_id not in active_scans:
        raise HTTPException(status_code=404, detail="扫描任务不存在")
    
    active_scans[scan_id]["status"] = "stopped"
    active_scans[scan_id]["stopped_at"] = datetime.now().isoformat()
    
    return {"message": "扫描任务已停止"}


@router.get("/history")
async def get_scan_history():
    """获取扫描历史"""
    # TODO: 从文件系统读取历史记录
    return []
