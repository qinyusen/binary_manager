import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from ...domain.repositories import GroupRepository
from ...domain.entities import Group
from ...shared.logger import Logger


class SQLiteGroupRepository(GroupRepository):
    """SQLite分组仓储实现"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / 'database' / 'binary_manager.db')
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        self.logger = Logger.get(self.__class__.__name__)
        self.logger.info(f"Database initialized: {self.db_path}")
    
    def save(self, group: Group, created_by: str) -> Optional[int]:
        """保存分组"""
        cursor = self.conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO groups (
                    group_name, version, created_at, updated_at,
                    created_by, description, environment_config, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                group.group_name,
                group.version,
                now, now,
                created_by,
                group.description,
                json.dumps(group.environment_config),
                json.dumps(group.metadata)
            ))
            
            group_id = cursor.lastrowid
            
            for pkg in group.packages:
                cursor.execute('''
                    INSERT INTO group_packages (group_id, package_id, install_order, required)
                    VALUES (?, ?, ?, ?)
                ''', (
                    group_id,
                    pkg.package_id,
                    pkg.install_order,
                    1 if pkg.required else 0
                ))
            
            self.conn.commit()
            self.logger.info(f"Group saved with ID: {group_id}")
            return group_id
            
        except sqlite3.IntegrityError as e:
            self.logger.warning(f"Group already exists: {e}")
            cursor.execute('''
                SELECT id FROM groups WHERE group_name = ? AND version = ?
            ''', (group.group_name, group.version))
            row = cursor.fetchone()
            return row['id'] if row else None
    
    def find_by_id(self, group_id: int) -> Optional[Group]:
        """根据ID查找分组"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM groups WHERE id = ?', (group_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_group(row)
        return None
    
    def find_by_name_and_version(self, name: str, version: str) -> Optional[Group]:
        """根据名称和版本查找分组"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM groups WHERE group_name = ? AND version = ?',
            (name, version)
        )
        row = cursor.fetchone()
        
        if row:
            return self._row_to_group(row)
        return None
    
    def find_all(self, filters: Optional[Dict] = None) -> List[Group]:
        """查找所有分组"""
        cursor = self.conn.cursor()
        
        query = 'SELECT * FROM groups WHERE 1=1'
        params = []
        
        if filters:
            if 'group_name' in filters:
                query += ' AND group_name = ?'
                params.append(filters['group_name'])
            if 'version' in filters:
                query += ' AND version = ?'
                params.append(filters['version'])
            if 'created_by' in filters:
                query += ' AND created_by = ?'
                params.append(filters['created_by'])
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [self._row_to_group(row) for row in rows]
    
    def find_by_name(self, group_name: str) -> List[Group]:
        """根据名称查找分组"""
        return self.find_all({'group_name': group_name})
    
    def find_by_creator(self, publisher_id: str) -> List[Group]:
        """根据创建者查找分组"""
        return self.find_all({'created_by': publisher_id})
    
    def delete(self, group_id: int) -> bool:
        """删除分组"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM groups WHERE id = ?', (group_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def exists(self, name: str, version: str) -> bool:
        """检查分组是否存在"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT 1 FROM groups WHERE group_name = ? AND version = ?',
            (name, version)
        )
        return cursor.fetchone() is not None
    
    def add_package(self, group_id: int, package_id: int, 
                   install_order: int = 0, required: bool = True) -> bool:
        """添加包到分组"""
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO group_packages (group_id, package_id, install_order, required)
                VALUES (?, ?, ?, ?)
            ''', (group_id, package_id, install_order, 1 if required else 0))
            
            self.conn.commit()
            self.logger.info(f"Package {package_id} added to group {group_id}")
            return True
            
        except sqlite3.IntegrityError:
            cursor.execute('''
                UPDATE group_packages 
                SET install_order = ?, required = ?
                WHERE group_id = ? AND package_id = ?
            ''', (install_order, 1 if required else 0, group_id, package_id))
            self.conn.commit()
            return True
    
    def remove_package(self, group_id: int, package_id: int) -> bool:
        """从分组移除包"""
        cursor = self.conn.cursor()
        cursor.execute(
            'DELETE FROM group_packages WHERE group_id = ? AND package_id = ?',
            (group_id, package_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    def _row_to_group(self, row: sqlite3.Row) -> Group:
        """将数据库行转换为Group实体"""
        from ...domain.entities import GroupPackage
        
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT package_id, install_order, required FROM group_packages WHERE group_id = ? ORDER BY install_order',
            (row['id'],)
        )
        package_rows = cursor.fetchall()
        
        packages = [
            GroupPackage(
                package_id=r['package_id'],
                install_order=r['install_order'],
                required=bool(r['required'])
            )
            for r in package_rows
        ]
        
        return Group(
            group_name=row['group_name'],
            version=row['version'],
            packages=packages,
            description=row['description'],
            environment_config=json.loads(row['environment_config']) if row['environment_config'] else {},
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
