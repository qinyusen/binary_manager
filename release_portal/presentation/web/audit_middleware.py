"""
审计日志装饰器 - 用于记录所有操作
"""

from functools import wraps
from flask import request, g
from typing import Callable, Optional
from datetime import datetime

from ...application.audit_service import AuditLogger, AuditService
from ...domain.entities.audit_log import AuditAction


class AuditMiddleware:
    """审计中间件类"""
    
    def __init__(self, audit_service: AuditService):
        """初始化中间件"""
        self.audit_service = audit_service
        self.logger = AuditLogger(audit_service)
    
    def get_request_info(self) -> dict:
        """获取请求信息"""
        return {
            'ip_address': request.remote_addr or '',
            'user_agent': request.headers.get('User-Agent', ''),
            'request_method': request.method,
            'request_path': request.path,
            'query_params': dict(request.args),
            'form_data': dict(request.form) if request.form else {}
        }


def get_audit_middleware() -> Optional[AuditMiddleware]:
    """获取审计中间件实例"""
    # 尝试从 Flask g 对象获取
    if hasattr(g, 'audit_middleware'):
        return g.audit_middleware
    return None


def audit_log(action: AuditAction):
    """
    审计日志装饰器工厂
    
    Args:
        action: 操作类型
    """
    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            # 获取审计中间件
            middleware = get_audit_middleware()
            if not middleware:
                return func(*args, **kwargs)
            
            # 获取用户信息
            user = getattr(g, 'current_user', None)
            if not user:
                return func(*args, **kwargs)
            
            # 获取请求信息
            request_info = get_request_info()
            
            # 执行原函数
            try:
                result = func(*args, **kwargs)
                
                # 记录成功的审计日志
                middleware.logger.log_action(
                    action=action,
                    user_id=user.user_id,
                    username=user.username,
                    role=user.role.name,
                    ip_address=request_info['ip_address'],
                    user_agent=request_info['user_agent'],
                    status="SUCCESS"
                )
                
                return result
            
            except Exception as e:
                # 记录失败的审计日志
                middleware.logger.log_action(
                    action=action,
                    user_id=user.user_id,
                    username=user.username,
                    role=user.role.name,
                    ip_address=request_info['ip_address'],
                    user_agent=request_info['user_agent'],
                    status="FAILED",
                    error_message=str(e)
                )
                
                raise
        
        return wrapped
    
    return decorator


# 快捷审计日志记录函数

def log_audit(
    action: AuditAction,
    user_id: str,
    username: str,
    role: str,
    resource_type: str = "",
    resource_id: str = "",
    resource_name: str = "",
    details: dict = None
):
    """
    直接记录审计日志的辅助函数
    
    Args:
        action: 操作类型
        user_id: 用户ID
        username: 用户名
        role: 角色
        resource_type: 资源类型
        resource_id: 资源ID
        resource_name: 资源名称
        details: 详细信息
    """
    middleware = get_audit_middleware()
    if middleware:
        middleware.audit_service.log_action(
            action=action,
            user_id=user_id,
            username=username,
            role=role,
            ip_address="",  # 从请求上下文获取
            user_agent="",
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details,
            status="SUCCESS"
        )
