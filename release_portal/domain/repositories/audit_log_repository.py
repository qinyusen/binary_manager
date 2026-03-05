"""
审计日志仓储接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime

from ..entities.audit_log import AuditLog, AuditAction, AuditLogFilter


class AuditLogRepository(ABC):
    """审计日志仓储接口"""
    
    @abstractmethod
    def save(self, audit_log: AuditLog) -> AuditLog:
        """保存审计日志"""
        pass
    
    @abstractmethod
    def find_by_id(self, log_id: int) -> Optional[AuditLog]:
        """根据ID查找审计日志"""
        pass
    
    @abstractmethod
    def find_all(self, filters: Optional[AuditLogFilter] = None,
                limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """查找审计日志"""
        pass
    
    @abstractmethod
    def count(self, filters: Optional[AuditLogFilter] = None) -> int:
        """统计审计日志数量"""
        pass
    
    @abstractmethod
    def delete_old_logs(self, days: int) -> int:
        """删除旧日志"""
        pass
    
    @abstractmethod
    def get_user_activity(self, user_id: str, days: int = 30) -> Dict:
        """获取用户活动统计"""
        pass
    
    @abstractmethod
    def get_action_statistics(self, start_date: datetime, 
                           end_date: datetime) -> Dict[str, int]:
        """获取操作统计"""
        pass
