from typing import Optional, Dict
from datetime import datetime
from .role import Role


class User:
    def __init__(
        self,
        user_id: str,
        username: str,
        email: str,
        password_hash: str,
        role: Role,
        license_id: Optional[str] = None
    ):
        if not user_id or not isinstance(user_id, str):
            raise ValueError("User ID must be a non-empty string")
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")
        if not email or not isinstance(email, str):
            raise ValueError("Email must be a non-empty string")
        if not password_hash or not isinstance(password_hash, str):
            raise ValueError("Password hash must be a non-empty string")
        if not isinstance(role, Role):
            raise ValueError("Role must be a Role instance")
        
        self._user_id = user_id
        self._username = username
        self._email = email
        self._password_hash = password_hash
        self._role = role
        self._license_id = license_id
        self._created_at = datetime.utcnow()
        self._is_active = True
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def password_hash(self) -> str:
        return self._password_hash
    
    @property
    def role(self) -> Role:
        return self._role
    
    @property
    def license_id(self) -> Optional[str]:
        return self._license_id
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    def deactivate(self) -> None:
        self._is_active = False
    
    def activate(self) -> None:
        self._is_active = True
    
    def verify_password(self, password: str, hash_func) -> bool:
        return hash_func(password.encode()).hexdigest() == self._password_hash
    
    def has_permission(self, resource: str, resource_type: str) -> bool:
        if not self._is_active:
            return False
        from ..value_objects import ResourceType
        rt = ResourceType.from_string(resource_type) if isinstance(resource_type, str) else resource_type
        return self._role.has_permission(resource, rt)
    
    def to_dict(self, include_sensitive: bool = False) -> Dict:
        data = {
            'user_id': self._user_id,
            'username': self._username,
            'email': self._email,
            'role': self._role.to_dict(),
            'license_id': self._license_id,
            'created_at': self._created_at.isoformat(),
            'is_active': self._is_active
        }
        if include_sensitive:
            data['password_hash'] = self._password_hash
        return data
    
    @classmethod
    def from_dict(cls, data: Dict, role: Role) -> 'User':
        user = cls(
            user_id=data['user_id'],
            username=data['username'],
            email=data['email'],
            password_hash=data.get('password_hash', ''),
            role=role,
            license_id=data.get('license_id')
        )
        user._created_at = datetime.fromisoformat(data['created_at'])
        user._is_active = data.get('is_active', True)
        return user
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return self._user_id == other._user_id
    
    def __hash__(self) -> int:
        return hash(self._user_id)
    
    def __repr__(self) -> str:
        return f"User(id='{self._user_id}', username='{self._username}', role='{self._role.name}')"
