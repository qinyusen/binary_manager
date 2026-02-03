from typing import Optional, List, Dict
from datetime import datetime
from ..value_objects import Hash, GitInfo, StorageLocation, PackageName


class FileInfo:
    def __init__(self, path: str, size: int, hash_value: Hash):
        self._path = path
        self._size = size
        self._hash = hash_value
    
    @property
    def path(self) -> str:
        return self._path
    
    @property
    def size(self) -> int:
        return self._size
    
    @property
    def hash(self) -> Hash:
        return self._hash
    
    def to_dict(self) -> Dict:
        return {
            'path': self._path,
            'size': self._size,
            'hash': str(self._hash)
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FileInfo':
        return cls(
            path=data['path'],
            size=data['size'],
            hash_value=Hash.from_string(data['hash'])
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, FileInfo):
            return False
        return self._path == other._path and self._hash == other._hash
    
    def __repr__(self) -> str:
        return f"FileInfo(path='{self._path}', size={self._size})"


class Publisher:
    def __init__(self, publisher_id: str, hostname: str):
        self._publisher_id = publisher_id
        self._hostname = hostname
        self._created_at = datetime.utcnow()
    
    @property
    def publisher_id(self) -> str:
        return self._publisher_id
    
    @property
    def hostname(self) -> str:
        return self._hostname
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    def to_dict(self) -> Dict:
        return {
            'publisher_id': self._publisher_id,
            'hostname': self._hostname,
            'created_at': self._created_at.isoformat()
        }
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Publisher):
            return False
        return self._publisher_id == other._publisher_id
    
    def __hash__(self) -> int:
        return hash(self._publisher_id)
    
    def __repr__(self) -> str:
        return f"Publisher(id='{self._publisher_id}', hostname='{self._hostname}')"
