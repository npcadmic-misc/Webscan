"""
报告相关API路由
"""
from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter(prefix="/report", tags=["报告"])


@router.get("/{scan_id}")
async def get_report(scan_id: str, format: str = "html"):
    """获取扫描报告"""
    # TODO: 从文件系统读取报告
    return {
        "scan_id": scan_id,
        "format": format,
        "message": "报告生成功能待实现"
    }


@router.post("/generate")
async def generate_report(scan_id: str, format: str = "html"):
    """生成扫描报告"""
    # TODO: 实现报告生成逻辑
    return {
        "scan_id": scan_id,
        "format": format,
        "message": "报告生成中..."
    }


@router.get("/list")
async def list_reports():
    """列出所有报告"""
    # TODO: 从文件系统读取报告列表
    return []
