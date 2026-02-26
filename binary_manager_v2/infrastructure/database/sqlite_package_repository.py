import sqlite3
import json
import uuid
import socket
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from ...domain.repositories import PackageRepository
from ...domain.entities import Package
from ...shared.logger import Logger


class SQLitePackageRepository(PackageRepository):
    """SQLite包仓储实现"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / 'database' / 'binary_manager.db')
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        self.logger = Logger.get(self.__class__.__name__)
        self._initialize_database()
        self.publisher_id = self._get_or_create_publisher_id()
        
        self.logger.info(f"Database initialized: {self.db_path}")
        self.logger.info(f"Publisher ID: {self.publisher_id}")
    
    def _get_or_create_publisher_id(self) -> str:
        """获取或创建发布者ID"""
        hostname = socket.gethostname()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT publisher_id FROM publishers WHERE hostname = ?', (hostname,))
            row = cursor.fetchone()
            
            if row:
                publisher_id = row['publisher_id']
                cursor.execute(
                    'UPDATE publishers SET last_active_at = ? WHERE publisher_id = ?',
                    (datetime.utcnow().isoformat(), publisher_id)
                )
            else:
                publisher_id = f"{uuid.uuid4()}@{hostname}"
                cursor.execute(
                    '''INSERT INTO publishers 
                       (publisher_id, hostname, first_seen_at, last_active_at, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (publisher_id, hostname, datetime.utcnow().isoformat(), 
                     datetime.utcnow().isoformat(), datetime.utcnow().isoformat(), 
                     datetime.utcnow().isoformat())
                )
            
            self.conn.commit()
            return publisher_id
        except sqlite3.OperationalError as e:
            if 'no such table' in str(e):
                publisher_id = f"{uuid.uuid4()}@{hostname}"
                self.logger.warning(f"Publishers table not found, using generated ID: {publisher_id}")
                return publisher_id
            raise
    
    def save(self, package: Package) -> Optional[int]:
        """保存包"""
        cursor = self.conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        git_info = package.git_info
        storage = package.storage_location
        
        try:
            cursor.execute('''
                INSERT INTO packages (
                    package_name, version, created_at, updated_at,
                    publisher_id, publisher_hostname,
                    git_commit_hash, git_commit_short, git_branch, git_tag,
                    git_author, git_author_email, git_commit_time, git_commit_message, git_remotes, git_is_dirty,
                    archive_name, archive_size, archive_hash, file_count,
                    storage_type, storage_path, description, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(package.package_name),
                package.version,
                now, now,
                self.publisher_id,
                socket.gethostname(),
                git_info.commit_hash if git_info else '',
                git_info.commit_short if git_info else '',
                git_info.branch if git_info else None,
                git_info.tag if git_info else None,
                git_info.author if git_info else None,
                git_info.author_email if git_info else None,
                git_info.commit_time if git_info else None,
                git_info.commit_message if git_info else None,
                json.dumps(git_info.remotes) if git_info and git_info.remotes else None,
                1 if git_info and git_info.is_dirty else 0,
                f"{package.package_name}_v{package.version}.zip",
                package.archive_size,
                str(package.archive_hash),
                package.file_count,
                storage.storage_type.value if storage else 'local',
                storage.path if storage else '',
                package.description,
                json.dumps(package.metadata)
            ))
            
            package_id = cursor.lastrowid
            self.conn.commit()
            self.logger.info(f"Package saved with ID: {package_id}")
            return package_id
            
        except sqlite3.IntegrityError as e:
            self.logger.warning(f"Package already exists: {e}")
            cursor.execute('''
                SELECT id FROM packages 
                WHERE package_name = ? AND version = ? AND git_commit_hash = ?
            ''', (str(package.package_name), package.version, 
                   git_info.commit_hash if git_info else ''))
            row = cursor.fetchone()
            return row['id'] if row else None
    
    def find_by_id(self, package_id: int) -> Optional[Package]:
        """根据ID查找包"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM packages WHERE id = ?', (package_id,))
        row = cursor.fetchone()
        
        if row:
            return self._row_to_package(row)
        return None
    
    def find_by_name_and_version(self, name: str, version: str) -> Optional[Package]:
        """根据名称和版本查找包"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM packages WHERE package_name = ? AND version = ?',
            (name, version)
        )
        row = cursor.fetchone()
        
        if row:
            return self._row_to_package(row)
        return None
    
    def find_all(self, filters: Optional[Dict] = None) -> List[Package]:
        """查找所有包"""
        cursor = self.conn.cursor()
        
        query = 'SELECT * FROM packages WHERE 1=1'
        params = []
        
        if filters:
            if 'package_name' in filters:
                query += ' AND package_name = ?'
                params.append(filters['package_name'])
            if 'version' in filters:
                query += ' AND version = ?'
                params.append(filters['version'])
            if 'publisher_id' in filters:
                query += ' AND publisher_id = ?'
                params.append(filters['publisher_id'])
            if 'git_branch' in filters:
                query += ' AND git_branch = ?'
                params.append(filters['git_branch'])
        
        query += ' ORDER BY created_at DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        return [self._row_to_package(row) for row in rows]
    
    def find_by_name(self, package_name: str) -> List[Package]:
        """根据名称查找包"""
        return self.find_all({'package_name': package_name})
    
    def find_by_git_commit(self, commit_hash: str) -> List[Package]:
        """根据Git commit查找包"""
        cursor = self.conn.cursor()
        cursor.execute(
            'SELECT * FROM packages WHERE git_commit_hash = ?',
            (commit_hash,)
        )
        rows = cursor.fetchall()
        return [self._row_to_package(row) for row in rows]
    
    def find_by_publisher(self, publisher_id: str) -> List[Package]:
        """根据发布者查找包"""
        return self.find_all({'publisher_id': publisher_id})
    
    def delete(self, package_id: int) -> bool:
        """删除包"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM packages WHERE id = ?', (package_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def exists(self, name: str, version: str, git_commit: Optional[str] = None) -> bool:
        """检查包是否存在"""
        cursor = self.conn.cursor()
        
        if git_commit:
            cursor.execute(
                'SELECT 1 FROM packages WHERE package_name = ? AND version = ? AND git_commit_hash = ?',
                (name, version, git_commit)
            )
        else:
            cursor.execute(
                'SELECT 1 FROM packages WHERE package_name = ? AND version = ?',
                (name, version)
            )
        
        return cursor.fetchone() is not None
    
    def _row_to_package(self, row: sqlite3.Row) -> Package:
        """将数据库行转换为Package实体"""
        from ...domain.value_objects import Hash, GitInfo, StorageLocation, PackageName
        
        git_info = None
        if row['git_commit_hash']:
            # 转换为dict以便使用.get()方法
            row_dict = dict(row)
            
            # 处理git_remotes - 可能是None
            remotes = []
            if row_dict.get('git_remotes'):
                try:
                    remotes = json.loads(row_dict['git_remotes'])
                except (json.JSONDecodeError, TypeError):
                    remotes = []
            
            git_info = GitInfo(
                commit_hash=row['git_commit_hash'],
                commit_short=row['git_commit_short'],
                branch=row['git_branch'],
                tag=row['git_tag'],
                author=row['git_author'],
                author_email=row['git_author_email'],
                commit_time=row['git_commit_time'],
                commit_message=row_dict.get('git_commit_message'),
                remotes=remotes,
                is_dirty=bool(row['git_is_dirty'])
            )
        
        storage = None
        if row['storage_path']:
            from ...domain.value_objects import StorageType
            storage = StorageLocation(
                storage_type=StorageType(row['storage_type']),
                path=row['storage_path']
            )
        
        return Package(
            id=row['id'],
            package_name=PackageName(row['package_name']),
            version=row['version'],
            archive_hash=Hash.from_string(row['archive_hash']),
            archive_size=row['archive_size'],
            file_count=row['file_count'],
            git_info=git_info,
            storage_location=storage,
            publisher_id=row['publisher_id'],
            description=row['description'],
            metadata=json.loads(row['metadata']) if row['metadata'] else {}
        )
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _initialize_database(self):
        """初始化数据库表"""
        cursor = self.conn.cursor()
        
        # 创建publishers表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS publishers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                publisher_id TEXT NOT NULL UNIQUE,
                hostname TEXT NOT NULL,
                first_seen_at TEXT NOT NULL,
                last_active_at TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 创建packages表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_name TEXT NOT NULL,
                version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                publisher_id TEXT NOT NULL,
                publisher_hostname TEXT NOT NULL,
                git_commit_hash TEXT NOT NULL,
                git_commit_short TEXT NOT NULL,
                git_branch TEXT,
                git_tag TEXT,
                git_author TEXT,
                git_author_email TEXT,
                git_commit_time TEXT,
                git_commit_message TEXT,
                git_remotes TEXT,
                git_is_dirty INTEGER DEFAULT 0,
                archive_name TEXT NOT NULL,
                archive_size INTEGER NOT NULL,
                archive_hash TEXT NOT NULL,
                file_count INTEGER NOT NULL,
                storage_type TEXT NOT NULL DEFAULT 'local',
                storage_path TEXT NOT NULL,
                s3_bucket TEXT,
                s3_key TEXT,
                description TEXT,
                metadata TEXT,
                UNIQUE(package_name, version, git_commit_hash)
            )
        ''')
        
        # 添加新列（如果表已存在且没有这些列）
        try:
            cursor.execute('ALTER TABLE packages ADD COLUMN git_commit_message TEXT')
        except sqlite3.OperationalError:
            pass  # 列已存在
        
        try:
            cursor.execute('ALTER TABLE packages ADD COLUMN git_remotes TEXT')
        except sqlite3.OperationalError:
            pass  # 列已存在
        
        # 创建groups表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT NOT NULL,
                version TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                created_by TEXT NOT NULL,
                description TEXT,
                environment_config TEXT,
                metadata TEXT,
                UNIQUE(group_name, version)
            )
        ''')
        
        # 创建group_packages表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id INTEGER NOT NULL,
                package_id INTEGER NOT NULL,
                package_name TEXT NOT NULL,
                package_version TEXT NOT NULL,
                install_order INTEGER DEFAULT 0,
                required INTEGER DEFAULT 1,
                FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
                FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE,
                UNIQUE(group_id, package_id)
            )
        ''')
        
        # 添加新列到group_packages（如果表已存在且没有这些列）
        try:
            cursor.execute('ALTER TABLE group_packages ADD COLUMN package_name TEXT')
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute('ALTER TABLE group_packages ADD COLUMN package_version TEXT')
        except sqlite3.OperationalError:
            pass
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_packages_name_version ON packages(package_name, version)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_packages_git_commit ON packages(git_commit_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_packages_publisher ON packages(publisher_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_groups_name_version ON groups(group_name, version)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_group_packages_group ON group_packages(group_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_group_packages_package ON group_packages(package_id)')
        
        self.conn.commit()
