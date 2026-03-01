from typing import Optional, List, Dict
from datetime import datetime
from ..value_objects import Permission, ResourceType


class Role:
    def __init__(
        self,
        role_id: str,
        name: str,
        description: Optional[str] = None
    ):
        if not role_id or not isinstance(role_id, str):
            raise ValueError("Role ID must be a non-empty string")
        if not name or not isinstance(name, str):
            raise ValueError("Role name must be a non-empty string")
        
        self._role_id = role_id
        self._name = name
        self._description = description
        self._permissions: List[Permission] = []
    
    @property
    def role_id(self) -> str:
        return self._role_id
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> Optional[str]:
        return self._description
    
    @property
    def permissions(self) -> List[Permission]:
        return self._permissions.copy()
    
    def add_permission(self, permission: Permission) -> None:
        if permission not in self._permissions:
            self._permissions.append(permission)
    
    def remove_permission(self, permission: Permission) -> None:
        if permission in self._permissions:
            self._permissions.remove(permission)
    
    def has_permission(self, resource: str, resource_type: ResourceType) -> bool:
        return any(p.allows(resource, resource_type) for p in self._permissions)
    
    def to_dict(self) -> Dict:
        return {
            'role_id': self._role_id,
            'name': self._name,
            'description': self._description,
            'permissions': [p.to_dict() for p in self._permissions]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Role':
        role = cls(
            role_id=data['role_id'],
            name=data['name'],
            description=data.get('description')
        )
        for perm_data in data.get('permissions', []):
            role.add_permission(Permission.from_dict(perm_data))
        return role
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Role):
            return False
        return self._role_id == other._role_id
    
    def __hash__(self) -> int:
        return hash(self._role_id)
    
    def __repr__(self) -> str:
        return f"Role(id='{self._role_id}', name='{self._name}')"
