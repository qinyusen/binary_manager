"""
冷备份存储后端抽象基类
"""

import hashlib
from abc import ABC, abstractmethod
from typing import Dict, List


class ColdStorageBackend(ABC):
    """冷存储后端抽象基类"""

    @abstractmethod
    def store(self, backup_path: str, metadata: Dict) -> Dict:
        """存储备份到冷存储

        Args:
            backup_path: 本地备份文件路径
            metadata: 备份元数据

        Returns:
            存储后的元数据（包含存储位置、校验和等）
        """
        pass

    @abstractmethod
    def retrieve(self, backup_id: str, local_path: str) -> bool:
        """从冷存储检索备份

        Args:
            backup_id: 备份ID
            local_path: 本地存储路径

        Returns:
            是否成功检索
        """
        pass

    @abstractmethod
    def list_archives(self) -> List[Dict]:
        """列出所有归档

        Returns:
            归档元数据列表
        """
        pass

    @abstractmethod
    def delete(self, backup_id: str) -> bool:
        """删除归档

        Args:
            backup_id: 备份ID

        Returns:
            是否成功删除
        """
        pass

    def _calculate_checksum(self, file_path: str) -> str:
        """计算文件SHA256校验和

        Args:
            file_path: 文件路径

        Returns:
            SHA256校验和（十六进制字符串）
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
