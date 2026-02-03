from typing import Optional
from enum import Enum


class StorageType(Enum):
    LOCAL = 'local'
    S3 = 's3'


class StorageLocation:
    def __init__(
        self,
        storage_type: StorageType,
        path: str,
        bucket: Optional[str] = None,
        region: Optional[str] = None,
        key: Optional[str] = None
    ):
        self._storage_type = storage_type
        self._path = path
        self._bucket = bucket
        self._region = region
        self._key = key
    
    @property
    def storage_type(self) -> StorageType:
        return self._storage_type
    
    @property
    def path(self) -> str:
        return self._path
    
    @property
    def bucket(self) -> Optional[str]:
        return self._bucket
    
    @property
    def region(self) -> Optional[str]:
        return self._region
    
    @property
    def key(self) -> Optional[str]:
        return self._key
    
    @classmethod
    def local(cls, path: str) -> 'StorageLocation':
        return cls(StorageType.LOCAL, path)
    
    @classmethod
    def s3(cls, bucket: str, key: str, region: Optional[str] = None) -> 'StorageLocation':
        return cls(StorageType.S3, f's3://{bucket}/{key}', bucket, region, key)
    
    def to_dict(self) -> dict:
        return {
            'type': self._storage_type.value,
            'path': self._path,
            'bucket': self._bucket,
            'region': self._region,
            'key': self._key
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'StorageLocation':
        storage_type = StorageType(data.get('type', 'local'))
        return cls(
            storage_type=storage_type,
            path=data.get('path', ''),
            bucket=data.get('bucket'),
            region=data.get('region'),
            key=data.get('key')
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, StorageLocation):
            return False
        return self._path == other._path and self._storage_type == other._storage_type
    
    def __hash__(self) -> int:
        return hash((self._storage_type, self._path))
    
    def __repr__(self) -> str:
        return f"StorageLocation(type='{self._storage_type.value}', path='{self._path}')"
