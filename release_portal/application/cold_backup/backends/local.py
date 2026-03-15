"""
本地文件系统冷备份存储后端
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from .base import ColdStorageBackend

logger = logging.getLogger(__name__)


class LocalFileSystemBackend(ColdStorageBackend):
    """本地文件系统冷存储后端"""

    def __init__(self, storage_path: str):
        """初始化本地文件系统后端

        Args:
            storage_path: 存储目录路径
        """
        self.storage_path = Path(storage_path).expanduser().resolve()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_path / "metadata.json"

    def _load_metadata(self) -> Dict:
        """加载元数据"""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self, metadata: Dict) -> None:
        """保存元数据"""
        with open(self.metadata_file, "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def store(self, backup_path: str, metadata: Dict) -> Dict:
        """存储备份到本地文件系统"""
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")

        backup_id = metadata["backup_id"]
        archive_path = self.storage_path / f"{backup_id}.tar.gz"

        # 复制文件
        shutil.copy2(backup_path, archive_path)

        # 计算校验和
        checksum = self._calculate_checksum(archive_path)

        # 更新元数据
        all_metadata = self._load_metadata()
        archive_metadata = {
            **metadata,
            "storage_path": str(archive_path),
            "checksum": checksum,
            "size": archive_path.stat().st_size,
            "stored_at": datetime.now().isoformat(),
        }
        all_metadata[backup_id] = archive_metadata
        self._save_metadata(all_metadata)

        return archive_metadata

    def retrieve(self, backup_id: str, local_path: str) -> bool:
        """从本地文件系统检索备份"""
        all_metadata = self._load_metadata()
        if backup_id not in all_metadata:
            return False

        archive_metadata = all_metadata[backup_id]
        source_path = Path(archive_metadata["storage_path"])

        if not source_path.exists():
            return False

        # 验证校验和
        if self._calculate_checksum(source_path) != archive_metadata["checksum"]:
            return False

        # 复制到目标路径
        shutil.copy2(source_path, local_path)
        return True

    def list_archives(self) -> List[Dict]:
        """列出所有本地归档"""
        all_metadata = self._load_metadata()
        return list(all_metadata.values())

    def delete(self, backup_id: str) -> bool:
        """删除本地归档"""
        all_metadata = self._load_metadata()
        if backup_id not in all_metadata:
            return False

        archive_metadata = all_metadata[backup_id]
        archive_path = Path(archive_metadata["storage_path"])

        if archive_path.exists():
            archive_path.unlink()

        del all_metadata[backup_id]
        self._save_metadata(all_metadata)
        return True
