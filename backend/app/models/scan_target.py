"""
扫描目标数据模型
"""
from pydantic import BaseModel, HttpUrl
from typing import Optional, List
from datetime import datetime


class ScanTarget(BaseModel):
    """扫描目标模型"""
    url: str
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = datetime.now()


class AuthConfig(BaseModel):
    """认证配置模型"""
    type: str = "cookie"  # cookie, token, bearer
    value: str
    header_name: Optional[str] = "Cookie"
    roles: Optional[List[dict]] = []  # 多角色支持


class ScanConfig(BaseModel):
    """扫描配置模型"""
    target_url: str
    auth_config: Optional[AuthConfig] = None
    scan_types: List[str] = ["basic"]  # basic, deep, api
    max_concurrency: int = 10
    rate_limit: int = 50
    timeout: int = 30
    max_depth: int = 5
    excluded_paths: List[str] = []
    custom_payloads: List[str] = []
    user_agent: Optional[str] = None
