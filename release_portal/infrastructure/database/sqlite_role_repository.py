import json
from typing import List, Optional
from ...domain.entities.role import Role
from ...domain.value_objects import ResourceType, Permission
from ...domain.repositories import RoleRepository
from .base_repository import BaseSQLiteRepository


class SQLiteRoleRepository(BaseSQLiteRepository, RoleRepository):
    def save(self, role: Role) -> None:
        self._execute_update(
            "INSERT OR REPLACE INTO roles (role_id, name, description) VALUES (?, ?, ?)",
            (role.role_id, role.name, role.description)
        )
        
        self._execute_update(
            "DELETE FROM role_permissions WHERE role_id = ?",
            (role.role_id,)
        )
        
        for permission in role.permissions:
            for resource_type in permission.resource_types:
                self._execute_update(
                    "INSERT INTO role_permissions (role_id, permission, resource_type) VALUES (?, ?, ?)",
                    (role.role_id, permission.resource, str(resource_type))
                )
    
    def find_by_id(self, role_id: str) -> Optional[Role]:
        rows = self._execute_query(
            "SELECT * FROM roles WHERE role_id = ?",
            (role_id,)
        )
        if not rows:
            return None
        return self._row_to_role(rows[0])
    
    def find_by_name(self, name: str) -> Optional[Role]:
        rows = self._execute_query(
            "SELECT * FROM roles WHERE name = ?",
            (name,)
        )
        if not rows:
            return None
        return self._row_to_role(rows[0])
    
    def find_all(self) -> List[Role]:
        rows = self._execute_query("SELECT * FROM roles ORDER BY name")
        return [self._row_to_role(row) for row in rows]
    
    def delete(self, role_id: str) -> None:
        self._execute_update(
            "DELETE FROM roles WHERE role_id = ?",
            (role_id,)
        )
    
    def _row_to_role(self, row) -> Role:
        role = Role(
            role_id=row['role_id'],
            name=row['name'],
            description=row['description']
        )
        
        perm_rows = self._execute_query(
            "SELECT DISTINCT permission FROM role_permissions WHERE role_id = ?",
            (row['role_id'],)
        )
        
        for perm_row in perm_rows:
            resource_type_rows = self._execute_query(
                "SELECT resource_type FROM role_permissions WHERE role_id = ? AND permission = ?",
                (row['role_id'], perm_row['permission'])
            )
            resource_types = {
                ResourceType.from_string(rt_row['resource_type'])
                for rt_row in resource_type_rows
            }
            permission = Permission(
                resource=perm_row['permission'],
                resource_types=resource_types
            )
            role.add_permission(permission)
        
        return role
