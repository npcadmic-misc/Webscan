"""
认证和会话管理模块
"""
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from loguru import logger
import httpx


class SessionManager:
    """会话管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionInfo] = {}
    
    def create_session(self, session_id: str, auth_config: dict) -> 'SessionInfo':
        """创建新会话"""
        session = SessionInfo(
            session_id=session_id,
            auth_type=auth_config.get('type', 'cookie'),
            auth_value=auth_config.get('value', ''),
            header_name=auth_config.get('header_name', 'Cookie'),
            created_at=datetime.now(),
            last_used=datetime.now()
        )
        
        self.sessions[session_id] = session
        logger.info(f"创建会话: {session_id}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional['SessionInfo']:
        """获取会话信息"""
        return self.sessions.get(session_id)
    
    def update_session(self, session_id: str, **kwargs) -> bool:
        """更新会话信息"""
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        for key, value in kwargs.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        session.last_used = datetime.now()
        return True
    
    def remove_session(self, session_id: str) -> bool:
        """删除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"删除会话: {session_id}")
            return True
        return False
    
    def list_sessions(self) -> List[Dict]:
        """列出所有会话"""
        return [
            {
                'session_id': s.session_id,
                'auth_type': s.auth_type,
                'created_at': s.created_at.isoformat(),
                'last_used': s.last_used.isoformat(),
                'is_active': s.is_active
            }
            for s in self.sessions.values()
        ]


class SessionInfo:
    """会话信息"""
    
    def __init__(
        self,
        session_id: str,
        auth_type: str,
        auth_value: str,
        header_name: str = "Cookie",
        created_at: datetime = None,
        last_used: datetime = None
    ):
        self.session_id = session_id
        self.auth_type = auth_type  # cookie, token, bearer
        self.auth_value = auth_value
        self.header_name = header_name
        self.created_at = created_at or datetime.now()
        self.last_used = last_used or datetime.now()
        self.is_active = True
        self.roles: List[Dict] = []  # 多角色支持
    
    def add_role(self, role_name: str, auth_value: str):
        """添加角色"""
        self.roles.append({
            'name': role_name,
            'auth_value': auth_value,
            'added_at': datetime.now().isoformat()
        })
    
    def switch_role(self, role_name: str) -> Optional[str]:
        """切换角色"""
        for role in self.roles:
            if role['name'] == role_name:
                old_value = self.auth_value
                self.auth_value = role['auth_value']
                self.last_used = datetime.now()
                logger.info(f"切换角色: {role_name}")
                return old_value
        return None
    
    def refresh(self):
        """刷新会话"""
        self.last_used = datetime.now()
        logger.debug(f"会话刷新: {self.session_id}")
    
    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """检查会话是否过期"""
        return (datetime.now() - self.last_used) > timedelta(minutes=timeout_minutes)
    
    def to_headers(self) -> Dict[str, str]:
        """转换为HTTP头"""
        headers = {}
        
        if self.auth_type == 'cookie':
            headers['Cookie'] = self.auth_value
        elif self.auth_type == 'token':
            headers[self.header_name] = self.auth_value
        elif self.auth_type == 'bearer':
            headers['Authorization'] = f'Bearer {self.auth_value}'
        
        return headers
    
    def apply_to_client(self, client: httpx.AsyncClient):
        """应用到HTTP客户端"""
        headers = self.to_headers()
        client.headers.update(headers)
        self.refresh()


class AuthManager:
    """认证管理器"""
    
    def __init__(self):
        self.session_manager = SessionManager()
    
    def create_authenticated_client(
        self,
        auth_config: dict,
        timeout: int = 30
    ) -> httpx.AsyncClient:
        """创建已认证的HTTP客户端"""
        client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True
        )
        
        if auth_config:
            session_id = f"session_{int(datetime.now().timestamp())}"
            session = self.session_manager.create_session(session_id, auth_config)
            session.apply_to_client(client)
        
        return client
    
    def add_multi_role_support(
        self,
        session_id: str,
        roles: List[Dict]
    ) -> bool:
        """添加多角色支持"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return False
        
        for role in roles:
            session.add_role(
                role_name=role.get('name', 'default'),
                auth_value=role.get('auth_value', '')
            )
        
        logger.info(f"为会话 {session_id} 添加了 {len(roles)} 个角色")
        return True
    
    def switch_session_role(
        self,
        session_id: str,
        role_name: str
    ) -> bool:
        """切换会话角色"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return False
        
        old_value = session.switch_role(role_name)
        return old_value is not None
    
    def cleanup_expired_sessions(self, timeout_minutes: int = 60):
        """清理过期会话"""
        expired_sessions = [
            sid for sid, session in self.session_manager.sessions.items()
            if session.is_expired(timeout_minutes)
        ]
        
        for sid in expired_sessions:
            self.session_manager.remove_session(sid)
        
        if expired_sessions:
            logger.info(f"清理了 {len(expired_sessions)} 个过期会话")
