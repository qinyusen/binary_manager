import sqlite3
from pathlib import Path
from typing import Optional
from ...shared.logger import Logger


class BaseSQLiteRepository:
    """SQLite仓储基类"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path(__file__).parent.parent.parent / 'database' / 'binary_manager.db')
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        
        self.logger = Logger.get(self.__class__.__name__)
        self.logger.info(f"Database initialized: {self.db_path}")
    
    def close(self):
        """关闭数据库连接"""
        self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
