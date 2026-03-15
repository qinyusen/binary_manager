"""
冷备份存储后端抽象基类
"""

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Union


class ColdStorageBackend(ABC):
    """冷存储后端抽象基类"""

    @abstractmethod
    def store(self, backup_path: str, metadata: Dict) -> Dict:
        pass

    @abstractmethod
    def retrieve(self, backup_id: str, local_path: str) -> bool:
        pass

    @abstractmethod
    def list_archives(self) -> List[Dict]:
        pass

    @abstractmethod
    def delete(self, backup_id: str) -> bool:
        pass

    def _calculate_checksum(self, file_path: Union[str, Path]) -> str:
        file_path = Path(file_path)
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
