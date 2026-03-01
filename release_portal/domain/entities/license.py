from typing import Optional, List, Dict, Set
from datetime import datetime
from ..value_objects import ResourceType, AccessLevel


class License:
    def __init__(
        self,
        license_id: str,
        organization: str,
        access_level: AccessLevel,
        allowed_resource_types: Set[ResourceType],
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict] = None
    ):
        if not license_id or not isinstance(license_id, str):
            raise ValueError("License ID must be a non-empty string")
        if not organization or not isinstance(organization, str):
            raise ValueError("Organization must be a non-empty string")
        if not isinstance(access_level, AccessLevel):
            raise ValueError("Access level must be an AccessLevel enum")
        if not allowed_resource_types or not isinstance(allowed_resource_types, set):
            raise ValueError("Allowed resource types must be a non-empty set")
        
        self._license_id = license_id
        self._organization = organization
        self._access_level = access_level
        self._allowed_resource_types = allowed_resource_types.copy()
        self._expires_at = expires_at
        self._metadata = metadata or {}
        self._created_at = datetime.utcnow()
        self._is_active = True
    
    @property
    def license_id(self) -> str:
        return self._license_id
    
    @property
    def organization(self) -> str:
        return self._organization
    
    @property
    def access_level(self) -> AccessLevel:
        return self._access_level
    
    @property
    def allowed_resource_types(self) -> Set[ResourceType]:
        return self._allowed_resource_types.copy()
    
    @property
    def expires_at(self) -> Optional[datetime]:
        return self._expires_at
    
    @property
    def metadata(self) -> Dict:
        return self._metadata.copy()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def is_active(self) -> bool:
        if not self._is_active:
            return False
        if self._expires_at and self._expires_at < datetime.utcnow():
            return False
        return True
    
    def deactivate(self) -> None:
        self._is_active = False
    
    def activate(self) -> None:
        self._is_active = True
    
    def allows_resource_type(self, resource_type: ResourceType) -> bool:
        return resource_type in self._allowed_resource_types
    
    def allows_content_type(self, content_type: str) -> bool:
        if self._access_level == AccessLevel.FULL_ACCESS:
            return True
        elif self._access_level == AccessLevel.BINARY_ACCESS:
            return content_type in ['BINARY', 'DOCUMENT']
        return False
    
    def is_expired(self) -> bool:
        if self._expires_at is None:
            return False
        return self._expires_at < datetime.utcnow()
    
    def to_dict(self) -> Dict:
        return {
            'license_id': self._license_id,
            'organization': self._organization,
            'access_level': str(self._access_level),
            'allowed_resource_types': [str(rt) for rt in self._allowed_resource_types],
            'expires_at': self._expires_at.isoformat() if self._expires_at else None,
            'created_at': self._created_at.isoformat(),
            'is_active': self._is_active,
            'metadata': self._metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'License':
        license_obj = cls(
            license_id=data['license_id'],
            organization=data['organization'],
            access_level=AccessLevel.from_string(data['access_level']),
            allowed_resource_types={ResourceType.from_string(rt) for rt in data['allowed_resource_types']},
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            metadata=data.get('metadata', {})
        )
        license_obj._created_at = datetime.fromisoformat(data['created_at'])
        license_obj._is_active = data.get('is_active', True)
        return license_obj
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, License):
            return False
        return self._license_id == other._license_id
    
    def __hash__(self) -> int:
        return hash(self._license_id)
    
    def __repr__(self) -> str:
        return f"License(id='{self._license_id}', org='{self._organization}', level={self._access_level})"
