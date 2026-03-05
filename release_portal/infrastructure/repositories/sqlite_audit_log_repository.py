"""
SQLite 审计日志仓储实现
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from pathlib import Path

from ..domain.repositories.audit_log_repository import AuditLogRepository
from ..entities.audit_log import AuditLog, AuditAction, AuditLogFilter


class SQLiteAuditLogRepository(AuditLogRepository):
    """SQLite 审计日志仓储实现"""
    
    def __init__(self, db_path: str):
        """初始化仓储
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建审计日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                user_id TEXT NOT NULL,
                username TEXT NOT NULL,
                role TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                resource_type TEXT,
                resource_id TEXT,
                resource_name TEXT,
                details TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引以提高查询性能
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id 
            ON audit_logs(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_logs_action 
            ON audit_logs(action)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp 
            ON audit_logs(timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id 
            ON audit_logs(resource_id)
        """)
        
        conn.commit()
        conn.close()
    
    def save(self, audit_log: AuditLog) -> AuditLog:
        """保存审计日志"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        details_json = json.dumps(audit_log.details, ensure_ascii=False)
        
        cursor.execute("""
            INSERT INTO audit_logs (
                action, user_id, username, role, ip_address, user_agent,
                resource_type, resource_id, resource_name, details,
                status, error_message, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            audit_log.action.value if audit_log.action else None,
            audit_log.user_id,
            audit_log.username,
            audit_log.role,
            audit_log.ip_address,
            audit_log.user_agent,
            audit_log.resource_type,
            audit_log.resource_id,
            audit_log.resource_name,
            details_json,
            audit_log.status,
            audit_log.error_message,
            audit_log.timestamp.isoformat()
        ))
        
        audit_log.id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return audit_log
    
    def find_by_id(self, log_id: int) -> Optional[AuditLog]:
        """根据ID查找审计日志"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, action, user_id, username, role, ip_address, user_agent,
                   resource_type, resource_id, resource_name, details,
                   status, error_message, timestamp
            FROM audit_logs
            WHERE id = ?
        """, (log_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return self._row_to_audit_log(row)
    
    def find_all(self, filters: Optional[AuditLogFilter] = None,
                limit: int = 100, offset: int = 0) -> List[AuditLog]:
        """查找审计日志"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 构建查询
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        
        if filters:
            if filters.start_date:
                query += " AND timestamp >= ?"
                params.append(filters.start_date.isoformat())
            
            if filters.end_date:
                query += " AND timestamp <= ?"
                params.append(filters.end_date.isoformat())
            
            if filters.user_id:
                query += " AND user_id = ?"
                params.append(filters.user_id)
            
            if filters.username:
                query += " AND username LIKE ?"
                params.append(f"%{filters.username}%")
            
            if filters.action:
                query += " AND action = ?"
                params.append(filters.action.value)
            
            if filters.resource_type:
                query += " AND resource_type = ?"
                params.append(filters.resource_type)
            
            if filters.resource_id:
                query += " AND resource_id = ?"
                params.append(filters.resource_id)
            
            if filters.status:
                query += " AND status = ?"
                params.append(filters.status)
            
            if filters.ip_address:
                query += " AND ip_address = ?"
                params.append(filters.ip_address)
        
        query += " ORDER BY timestamp DESC"
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_audit_log(row) for row in rows]
    
    def count(self, filters: Optional[AuditLogFilter] = None) -> int:
        """统计审计日志数量"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM audit_logs WHERE 1=1"
        params = []
        
        if filters:
            if filters.start_date:
                query += " AND timestamp >= ?"
                params.append(filters.start_date.isoformat())
            
            if filters.end_date:
                query += " AND timestamp <= ?"
                params.append(filters.end_date.isoformat())
            
            if filters.user_id:
                query += " AND user_id = ?"
                params.append(filters.user_id)
            
            if filters.action:
                query += " AND action = ?"
                params.append(filters.action.value)
            
            if filters.status:
                query += " AND status = ?"
                params.append(filters.status)
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def delete_old_logs(self, days: int) -> int:
        """删除旧日志"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM audit_logs
            WHERE timestamp < ?
        """, (cutoff_date.isoformat(),))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_user_activity(self, user_id: str, days: int = 30) -> Dict:
        """获取用户活动统计"""
        start_date = datetime.now() - timedelta(days=days)
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 总操作次数
        cursor.execute("""
            SELECT COUNT(*) as total,
                   COUNT(DISTINCT action) as unique_actions,
                   MAX(timestamp) as last_activity
            FROM audit_logs
            WHERE user_id = ? AND timestamp >= ?
        """, (user_id, start_date.isoformat()))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            'total_actions': row['total'],
            'unique_actions': row['unique_actions'],
            'last_activity': row['last_activity']
        }
    
    def get_action_statistics(self, start_date: datetime, 
                           end_date: datetime) -> Dict[str, int]:
        """获取操作统计"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT action, COUNT(*) as count
            FROM audit_logs
            WHERE timestamp >= ? AND timestamp <= ?
            GROUP BY action
            ORDER BY count DESC
        """, (start_date.isoformat(), end_date.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        return {row[0]: row[1] for row in rows}
    
    def _row_to_audit_log(self, row) -> AuditLog:
        """将数据库行转换为审计日志实体"""
        details = {}
        if row['details']:
            try:
                details = json.loads(row['details'])
            except:
                pass
        
        return AuditLog(
            id=row['id'],
            action=AuditAction(row['action']) if row['action'] else None,
            user_id=row['user_id'],
            username=row['username'],
            role=row['role'],
            ip_address=row['ip_address'] or '',
            user_agent=row['user_agent'] or '',
            resource_type=row['resource_type'] or '',
            resource_id=row['resource_id'] or '',
            resource_name=row['resource_name'] or '',
            details=details,
            status=row['status'],
            error_message=row['error_message'],
            timestamp=datetime.fromisoformat(row['timestamp'])
        )
