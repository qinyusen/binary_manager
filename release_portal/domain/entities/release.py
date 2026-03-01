from typing import Optional, Dict
from datetime import datetime
from ..value_objects import ResourceType, ReleaseStatus, ContentType


class Release:
    def __init__(
        self,
        release_id: str,
        resource_type: ResourceType,
        version: str,
        publisher_id: str,
        description: Optional[str] = None,
        changelog: Optional[str] = None
    ):
        if not release_id or not isinstance(release_id, str):
            raise ValueError("Release ID must be a non-empty string")
        if not isinstance(resource_type, ResourceType):
            raise ValueError("Resource type must be a ResourceType enum")
        if not version or not isinstance(version, str):
            raise ValueError("Version must be a non-empty string")
        if not publisher_id or not isinstance(publisher_id, str):
            raise ValueError("Publisher ID must be a non-empty string")
        
        self._release_id = release_id
        self._resource_type = resource_type
        self._version = version
        self._publisher_id = publisher_id
        self._description = description
        self._changelog = changelog
        self._content_packages: Dict[ContentType, str] = {}
        self._status = ReleaseStatus.DRAFT
        self._created_at = datetime.utcnow()
        self._published_at: Optional[datetime] = None
    
    @property
    def release_id(self) -> str:
        return self._release_id
    
    @property
    def resource_type(self) -> ResourceType:
        return self._resource_type
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def publisher_id(self) -> str:
        return self._publisher_id
    
    @property
    def description(self) -> Optional[str]:
        return self._description
    
    @description.setter
    def description(self, value: str) -> None:
        self._description = value
    
    @property
    def changelog(self) -> Optional[str]:
        return self._changelog
    
    @changelog.setter
    def changelog(self, value: str) -> None:
        self._changelog = value
    
    @property
    def content_packages(self) -> Dict[ContentType, str]:
        return self._content_packages.copy()
    
    @property
    def status(self) -> ReleaseStatus:
        return self._status
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def published_at(self) -> Optional[datetime]:
        return self._published_at
    
    def add_package(self, content_type: ContentType, package_id: str) -> None:
        if not isinstance(content_type, ContentType):
            raise ValueError("Content type must be a ContentType enum")
        if not package_id or not isinstance(package_id, str):
            raise ValueError("Package ID must be a non-empty string")
        self._content_packages[content_type] = package_id
    
    def remove_package(self, content_type: ContentType) -> None:
        if content_type in self._content_packages:
            del self._content_packages[content_type]
    
    def get_package_id(self, content_type: ContentType) -> Optional[str]:
        return self._content_packages.get(content_type)
    
    def has_package(self, content_type: ContentType) -> bool:
        return content_type in self._content_packages
    
    def publish(self) -> None:
        if self._status == ReleaseStatus.PUBLISHED:
            raise ValueError("Release is already published")
        self._status = ReleaseStatus.PUBLISHED
        self._published_at = datetime.utcnow()
    
    def archive(self) -> None:
        if self._status == ReleaseStatus.ARCHIVED:
            raise ValueError("Release is already archived")
        self._status = ReleaseStatus.ARCHIVED
    
    def unpublish(self) -> None:
        if self._status != ReleaseStatus.PUBLISHED:
            raise ValueError("Can only unpublish published releases")
        self._status = ReleaseStatus.DRAFT
        self._published_at = None
    
    def to_dict(self) -> Dict:
        return {
            'release_id': self._release_id,
            'resource_type': str(self._resource_type),
            'version': self._version,
            'publisher_id': self._publisher_id,
            'description': self._description,
            'changelog': self._changelog,
            'content_packages': {str(ct): pid for ct, pid in self._content_packages.items()},
            'status': str(self._status),
            'created_at': self._created_at.isoformat(),
            'published_at': self._published_at.isoformat() if self._published_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Release':
        release = cls(
            release_id=data['release_id'],
            resource_type=ResourceType.from_string(data['resource_type']),
            version=data['version'],
            publisher_id=data['publisher_id'],
            description=data.get('description'),
            changelog=data.get('changelog')
        )
        
        for ct_str, package_id in data.get('content_packages', {}).items():
            release.add_package(ContentType.from_string(ct_str), package_id)
        
        release._status = ReleaseStatus.from_string(data['status'])
        release._created_at = datetime.fromisoformat(data['created_at'])
        if data.get('published_at'):
            release._published_at = datetime.fromisoformat(data['published_at'])
        
        return release
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Release):
            return False
        return self._release_id == other._release_id
    
    def __hash__(self) -> int:
        return hash(self._release_id)
    
    def __repr__(self) -> str:
        return f"Release(id='{self._release_id}', type={self._resource_type}, version='{self._version}', status={self._status})"
