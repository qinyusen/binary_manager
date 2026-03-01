from enum import Enum
from typing import Set, Dict


class ResourceType(Enum):
    BSP = "BSP"
    DRIVER = "DRIVER"
    EXAMPLES = "EXAMPLES"
    
    @classmethod
    def from_string(cls, value: str) -> 'ResourceType':
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"Invalid resource type: {value}. Must be one of {list(cls.__members__.keys())}")
    
    def __str__(self) -> str:
        return self.value


class ContentType(Enum):
    SOURCE = "SOURCE"
    BINARY = "BINARY"
    DOCUMENT = "DOCUMENT"
    
    @classmethod
    def from_string(cls, value: str) -> 'ContentType':
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"Invalid content type: {value}. Must be one of {list(cls.__members__.keys())}")
    
    def __str__(self) -> str:
        return self.value


class AccessLevel(Enum):
    FULL_ACCESS = "FULL_ACCESS"
    BINARY_ACCESS = "BINARY_ACCESS"
    
    @classmethod
    def from_string(cls, value: str) -> 'AccessLevel':
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"Invalid access level: {value}. Must be one of {list(cls.__members__.keys())}")
    
    def __str__(self) -> str:
        return self.value


class ReleaseStatus(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"
    
    @classmethod
    def from_string(cls, value: str) -> 'ReleaseStatus':
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"Invalid release status: {value}. Must be one of {list(cls.__members__.keys())}")
    
    def __str__(self) -> str:
        return self.value


class Permission:
    def __init__(self, resource: str, resource_types: Set[ResourceType] = None):
        if not resource or not isinstance(resource, str):
            raise ValueError("Resource must be a non-empty string")
        if resource_types is None:
            resource_types = set()
        if not isinstance(resource_types, set):
            raise ValueError("Resource types must be a set")
        
        self._resource = resource
        self._resource_types = resource_types.copy()
    
    @property
    def resource(self) -> str:
        return self._resource
    
    @property
    def resource_types(self) -> Set[ResourceType]:
        return self._resource_types.copy()
    
    def allows(self, resource: str, resource_type: ResourceType) -> bool:
        if self._resource != resource:
            return False
        if not self._resource_types:
            return True
        return resource_type in self._resource_types
    
    def to_dict(self) -> Dict:
        return {
            'resource': self._resource,
            'resource_types': [str(rt) for rt in self._resource_types]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Permission':
        return cls(
            resource=data['resource'],
            resource_types={ResourceType.from_string(rt) for rt in data['resource_types']}
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Permission):
            return False
        return self._resource == other._resource and self._resource_types == other._resource_types
    
    def __hash__(self) -> int:
        return hash((self._resource, frozenset(self._resource_types)))
    
    def __repr__(self) -> str:
        return f"Permission(resource='{self._resource}', types={[str(rt) for rt in self._resource_types]})"
