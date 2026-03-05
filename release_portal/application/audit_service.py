"""
审计日志服务
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pathlib import Path

from ..domain.entities.audit_log import AuditLog, AuditAction, AuditLogFilter
from ..domain.repositories.audit_log_repository import AuditLogRepository
from ..infrastructure.repositories.sqlite_audit_log_repository import SQLiteAuditLogRepository


class AuditService:
    """审计日志服务"""
    
    def __init__(self, audit_repository: AuditLogRepository):
        """
        初始化审计服务
        
        Args:
            audit_repository: 审计日志仓储
        """
        self.audit_repository = audit_repository
    
    def log_action(
        self,
        action: AuditAction,
        user_id: str,
        username: str,
        role: str,
        ip_address: str = "",
        user_agent: str = "",
        resource_type: str = "",
        resource_id: str = "",
        resource_name: str = "",
        details: Dict[str, Any] = None,
        status: str = "SUCCESS",
        error_message: str = None
    ) -> AuditLog:
        """
        记录审计日志
        
        Args:
            action: 操作类型
            user_id: 用户ID
            username: 用户名
            role: 用户角色
            ip_address: IP地址
            user_agent: 用户代理
            resource_type: 资源类型
            resource_id: 资源ID
            resource_name: 资源名称
            details: 详细信息
            status: 状态
            error_message: 错误信息
        
        Returns:
            审计日志实体
        """
        audit_log = AuditLog(
            action=action,
            user_id=user_id,
            username=username,
            role=role,
            ip_address=ip_address,
            user_agent=user_agent,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            details=details or {},
            status=status,
            error_message=error_message
        )
        
        return self.audit_repository.save(audit_log)
    
    def query_logs(
        self,
        filters: Optional[AuditLogFilter] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """
        查询审计日志
        
        Args:
            filters: 过滤器
            limit: 限制数量
            offset: 偏移量
        
        Returns:
            审计日志列表
        """
        return self.audit_repository.find_all(filters, limit, offset)
    
    def get_log_count(self, filters: Optional[AuditLogFilter] = None) -> int:
        """
        获取日志数量
        
        Args:
            filters: 过滤器
        
        Returns:
            日志数量
        """
        return self.audit_repository.count(filters)
    
    def get_user_activity_summary(self, user_id: str, days: int = 30) -> Dict:
        """
        获取用户活动摘要
        
        Args:
            user_id: 用户ID
            days: 天数
        
        Returns:
            活动统计
        """
        return self.audit_repository.get_user_activity(user_id, days)
    
    def get_action_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, int]:
        """
        获取操作统计
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            操作统计字典
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        
        if not end_date:
            end_date = datetime.now()
        
        return self.audit_repository.get_action_statistics(
            start_date=start_date,
            end_date=end_date
        )
    
    def cleanup_old_logs(self, retention_days: int = 90) -> int:
        """
        清理旧日志
        
        Args:
            retention_days: 保留天数
        
        Returns:
            删除的日志数量
        """
        return self.audit_repository.delete_old_logs(retention_days)
    
    def get_audit_trail(
        self,
        resource_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[AuditLog]:
        """
        获取特定资源的审计跟踪
        
        Args:
            resource_id: 资源ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            审计日志列表
        """
        filters = AuditLogFilter(
            resource_id=resource_id,
            start_date=start_date,
            end_date=end_date
        )
        
        return self.audit_repository.find_all(filters, limit=1000)


class AuditLogger:
    """审计日志记录器（辅助类）"""
    
    def __init__(self, audit_service: AuditService):
        """初始化日志记录器"""
        self.audit_service = audit_service
    
    def log_login(
        self,
        user_id: str,
        username: str,
        role: str,
        ip_address: str,
        user_agent: str,
        success: bool = True
    ):
        """记录登录日志"""
        self.audit_service.log_action(
            action=AuditAction.LOGIN,
            user_id=user_id,
            username=username,
            role=role,
            ip_address=ip_address,
            user_agent=user_agent,
            status="SUCCESS" if success else "FAILED"
        )
    
    def log_logout(
        self,
        user_id: str,
        username: str,
        role: str,
        ip_address: str
    ):
        """记录登出日志"""
        self.audit_service.log_action(
            action=AuditAction.LOGOUT,
            user_id=user_id,
            username=username,
            role=role,
            ip_address=ip_address
        )
    
    def log_release_action(
        self,
        action: AuditAction,
        user_id: str,
        username: str,
        role: str,
        release_id: str,
        resource_type: str,
        details: Dict[str, Any] = None,
        status: str = "SUCCESS",
        error_message: str = None
    ):
        """记录发布相关操作"""
        self.audit_service.log_action(
            action=action,
            user_id=user_id,
            username=username,
            role=role,
            resource_type=resource_type,
            resource_id=release_id,
            details=details,
            status=status,
            error_message=error_message
        )
    
    def log_license_action(
        self,
        action: AuditAction,
        user_id: str,
        username: str,
        role: str,
        license_id: str,
        details: Dict[str, Any] = None
    ):
        """记录许可证相关操作"""
        self.audit_service.log_action(
            action=action,
            user_id=user_id,
            username=username,
            role=role,
            resource_type="LICENSE",
            resource_id=license_id,
            details=details
        )
    
    def log_backup_action(
        self,
        action: AuditAction,
        user_id: str,
        username: str,
        role: str,
        backup_filename: str = "",
        details: Dict[str, Any] = None
    ):
        """记录备份相关操作"""
        self.audit_service.log_action(
            action=action,
            user_id=user_id,
            username=username,
            role=role,
            resource_type="BACKUP",
            resource_id=backup_filename,
            details=details
        )
