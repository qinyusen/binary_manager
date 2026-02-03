from abc import ABC, abstractmethod
from typing import Optional, Dict, List
from ..entities import FileInfo


class StorageRepository(ABC):
    
    @abstractmethod
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        pass
    
    @abstractmethod
    def download_file(self, remote_path: str, local_path: str) -> bool:
        pass
    
    @abstractmethod
    def file_exists(self, remote_path: str) -> bool:
        pass
    
    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        pass
    
    @abstractmethod
    def list_files(self, prefix: str) -> List[str]:
        pass
    
    @abstractmethod
    def get_file_url(self, remote_path: str, expiration: int = 3600) -> Optional[str]:
        pass
    
    @abstractmethod
    def verify_file(self, local_path: str, expected_hash: str) -> bool:
        pass
