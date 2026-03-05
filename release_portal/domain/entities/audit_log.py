"""
审计日志模型和实体
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum


class AuditAction(Enum):
    """审计动作类型"""
    
    # 认证相关
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    LOGIN_FAILED = "LOGIN_FAILED"
    REGISTER = "REGISTER"
    PASSWORD_CHANGE = "PASSWORD_CHANGE"
    
    # 发布相关
    RELEASE_CREATE = "RELEASE_CREATE"
    RELEASE_UPDATE = "RELEASE_UPDATE"
    RELEASE_DELETE = "RELEASE_DELETE"
    RELEASE_PUBLISH = "RELEASE_PUBLISH"
    RELEASE_ARCHIVE = "RELEASE_ARCHIVE"
    UPLOAD_PACKAGE = "UPLOAD_PACKAGE"
    
    # 下载相关
    DOWNLOAD = "DOWNLOAD"
    DOWNLOAD_LIST = "DOWNLOAD_LIST"
    
    # 许可证相关
    LICENSE_CREATE = "LICENSE_CREATE"
    LICENSE_UPDATE = "LICENSE_UPDATE"
    LICENSE_DELETE = "LICENSE_DELETE"
    LICENSE_REVOKE = "LICENSE_REVOKE"
    LICENSE_ACTIVATE = "LICENSE_ACTIVATE"
    LICENSE_EXTEND = "LICENSE_EXTEND"
    LICENSE_ASSIGN = "LICENSE_ASSIGN"
    
    # 备份相关
    BACKUP_CREATE = "BACKUP_CREATE"
    BACKUP_RESTORE = "BACKUP_RESTORE"
    BACKUP_DELETE = "BACKUP_DELETE"
    BACKUP_DOWNLOAD = "BACKUP_DOWNLOAD"
    COLD_BACKUP_CREATE = "COLD_BACKUP_CREATE"
    COLD_BACKUP_RETRIEVE = "COLD_BACKUP_RETRIEVE"
    COLD_BACKUP_DELETE = "COLD_BACKUP_DELETE"
    
    # 用户管理
    USER_CREATE = "USER_CREATE"
    USER_UPDATE = "USER_UPDATE"
    USER_DELETE = "USER_DELETE"
    ROLE_CHANGE = "ROLE_CHANGE"
    
    # 系统相关
    CONFIG_CHANGE = "CONFIG_CHANGE"
    SYSTEM_STARTUP = "SYSTEM_STARTUP"
    SYSTEM_SHUTDOWN = "SYSTEM_SHUTDOWN"


@dataclass
class AuditLog:
    """审计日志实体"""
    
    id: Optional[int] = None
    action: AuditAction = None
    user_id: str = ""
    username: str = ""
    role: str = ""
    ip_address: str = ""
    user_agent: str = ""
    resource_type: str = ""
    resource_id: str = ""
    resource_name: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    status: str = "SUCCESS"  # SUCCESS, FAILED
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'action': self.action.value if self.action else None,
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'resource_name': self.resource_name,
            'details': self.details,
            'status': self.status,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, user={self.username}, status={self.status})>"


@dataclass
class AuditLogFilter:
    """审计日志查询过滤器"""
    
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: Optional[str] = None
    username: Optional[str] = None
    action: Optional[AuditAction] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    status: Optional[str] = None
    ip_address: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action.value if self.action else None,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'status': self.status,
            'ip_address': self.ip_address
        }
