from typing import List, Optional
from ...domain.entities.user import User
from ...domain.entities.role import Role
from ...domain.repositories import UserRepository
from .sqlite_role_repository import SQLiteRoleRepository
from .base_repository import BaseSQLiteRepository


class SQLiteUserRepository(BaseSQLiteRepository, UserRepository):
    def __init__(self, db_path: str = ":memory:", role_repository: Optional[SQLiteRoleRepository] = None):
        super().__init__(db_path)
        self._role_repository = role_repository or SQLiteRoleRepository(db_path)
    
    def save(self, user: User) -> None:
        self._execute_update(
            """INSERT OR REPLACE INTO users 
               (user_id, username, email, password_hash, role_id, license_id, is_active, created_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user.user_id,
                user.username,
                user.email,
                user.password_hash,
                user.role.role_id,
                user.license_id,
                user.is_active,
                user.created_at.isoformat()
            )
        )
    
    def find_by_id(self, user_id: str) -> Optional[User]:
        rows = self._execute_query(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        if not rows:
            return None
        return self._row_to_user(rows[0])
    
    def find_by_username(self, username: str) -> Optional[User]:
        rows = self._execute_query(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        if not rows:
            return None
        return self._row_to_user(rows[0])
    
    def find_by_email(self, email: str) -> Optional[User]:
        rows = self._execute_query(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
        if not rows:
            return None
        return self._row_to_user(rows[0])
    
    def find_all(self) -> List[User]:
        rows = self._execute_query("SELECT * FROM users ORDER BY username")
        return [self._row_to_user(row) for row in rows]
    
    def delete(self, user_id: str) -> None:
        self._execute_update(
            "DELETE FROM users WHERE user_id = ?",
            (user_id,)
        )
    
    def exists_by_username(self, username: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM users WHERE username = ?",
                (username,)
            )
            return cursor.fetchone() is not None
    
    def exists_by_email(self, email: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM users WHERE email = ?",
                (email,)
            )
            return cursor.fetchone() is not None
    
    def _row_to_user(self, row) -> User:
        from datetime import datetime
        
        role = self._role_repository.find_by_id(row['role_id'])
        if not role:
            raise ValueError(f"Role not found for user: {row['user_id']}")
        
        user = User(
            user_id=row['user_id'],
            username=row['username'],
            email=row['email'],
            password_hash=row['password_hash'],
            role=role,
            license_id=row['license_id']
        )
        user._created_at = datetime.fromisoformat(row['created_at'])
        user._is_active = bool(row['is_active'])
        return user
