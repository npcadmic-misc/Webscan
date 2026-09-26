"""
WebSocket路由 - 实时推送扫描进度
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict
import json
import asyncio
from loguru import logger

router = APIRouter(prefix="/ws", tags=["WebSocket"])

# 存储WebSocket连接
websocket_connections: Dict[str, list] = {}


@router.websocket("/scan/{scan_id}")
async def scan_progress_websocket(websocket: WebSocket, scan_id: str):
    """扫描进度WebSocket"""
    await websocket.accept()
    
    if scan_id not in websocket_connections:
        websocket_connections[scan_id] = []
    
    websocket_connections[scan_id].append(websocket)
    logger.info(f"WebSocket连接已建立: {scan_id}")
    
    try:
        while True:
            # 接收客户端消息（可选）
            data = await websocket.receive_text()
            
            # 可以处理客户端请求
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket连接已断开: {scan_id}")
    except Exception as e:
        logger.error(f"WebSocket错误: {str(e)}")
    finally:
        if scan_id in websocket_connections:
            if websocket in websocket_connections[scan_id]:
                websocket_connections[scan_id].remove(websocket)


async def broadcast_progress(scan_id: str, progress_data: dict):
    """广播进度更新到所有连接的客户端"""
    if scan_id in websocket_connections:
        disconnected = []
        
        for ws in websocket_connections[scan_id]:
            try:
                await ws.send_json({
                    "type": "progress_update",
                    "data": progress_data
                })
            except Exception as e:
                logger.debug(f"WebSocket发送失败: {str(e)}")
                disconnected.append(ws)
        
        # 清理断开的连接
        for ws in disconnected:
            websocket_connections[scan_id].remove(ws)
