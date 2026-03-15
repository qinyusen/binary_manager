import sqlite3
import logging
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseConfig:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path


class BaseSQLiteRepository:
    def __init__(self, db_path: str = ":memory:"):
        self._db_path = db_path

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            conn.close()

    def _execute_query(self, query: str, params: tuple = ()):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def _execute_update(self, query: str, params: tuple = ()):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.lastrowid
