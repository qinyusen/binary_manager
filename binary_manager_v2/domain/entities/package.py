from typing import Optional, List, Dict, TYPE_CHECKING
from datetime import datetime
from ..value_objects import Hash, GitInfo, StorageLocation, PackageName

if TYPE_CHECKING:
    from .file_info import FileInfo


class Package:
    def __init__(
        self,
        package_name: PackageName,
        version: str,
        archive_hash: Hash,
        archive_size: int,
        file_count: int,
        git_info: Optional[GitInfo] = None,
        storage_location: Optional[StorageLocation] = None,
        publisher_id: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        self._package_name = package_name
        self._version = version
        self._archive_hash = archive_hash
        self._archive_size = archive_size
        self._file_count = file_count
        self._git_info = git_info
        self._storage_location = storage_location
        self._publisher_id = publisher_id
        self._description = description
        self._metadata = metadata or {}
        self._created_at = datetime.utcnow()
        self._files: List['FileInfo'] = []
    
    @property
    def package_name(self) -> PackageName:
        return self._package_name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def archive_hash(self) -> Hash:
        return self._archive_hash
    
    @property
    def archive_size(self) -> int:
        return self._archive_size
    
    @property
    def file_count(self) -> int:
        return self._file_count
    
    @property
    def git_info(self) -> Optional[GitInfo]:
        return self._git_info
    
    @property
    def storage_location(self) -> Optional[StorageLocation]:
        return self._storage_location
    
    @property
    def publisher_id(self) -> Optional[str]:
        return self._publisher_id
    
    @property
    def description(self) -> Optional[str]:
        return self._description
    
    @property
    def metadata(self) -> Dict:
        return self._metadata.copy()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def files(self) -> List['FileInfo']:
        return self._files.copy()
    
    def add_file(self, file_info: 'FileInfo') -> None:
        self._files.append(file_info)
    
    def with_storage(self, storage_location: StorageLocation) -> 'Package':
        self._storage_location = storage_location
        return self
    
    def to_dict(self) -> Dict:
        return {
            'package_name': str(self._package_name),
            'version': self._version,
            'archive_hash': str(self._archive_hash),
            'archive_size': self._archive_size,
            'file_count': self._file_count,
            'git_info': self._git_info.to_dict() if self._git_info else None,
            'storage_location': self._storage_location.to_dict() if self._storage_location else None,
            'publisher_id': self._publisher_id,
            'description': self._description,
            'metadata': self._metadata,
            'created_at': self._created_at.isoformat(),
            'files': [f.to_dict() for f in self._files]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Package':
        pkg = cls(
            package_name=PackageName(data['package_name']),
            version=data['version'],
            archive_hash=Hash.from_string(data['archive_hash']),
            archive_size=data['archive_size'],
            file_count=data['file_count'],
            git_info=GitInfo.from_dict(data['git_info']) if data.get('git_info') else None,
            storage_location=StorageLocation.from_dict(data['storage_location']) if data.get('storage_location') else None,
            publisher_id=data.get('publisher_id'),
            description=data.get('description'),
            metadata=data.get('metadata', {})
        )
        
        if 'created_at' in data:
            pkg._created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        
        for file_data in data.get('files', []):
            from .file_info import FileInfo
            pkg.add_file(FileInfo.from_dict(file_data))
        
        return pkg
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Package):
            return False
        return (self._package_name == other._package_name and 
                self._version == other._version and
                self._archive_hash == other._archive_hash)
    
    def __hash__(self) -> int:
        return hash((str(self._package_name), self._version, str(self._archive_hash)))
    
    def __repr__(self) -> str:
        return f"Package(name='{self._package_name}', version='{self._version}')"
