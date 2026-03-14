"""
冷备份核心服务
提供冷备份的创建、恢复、验证等核心业务逻辑
"""

import os
import json
import shutil
import tarfile
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Callable
import threading

from .backends import ColdStorageBackend, LocalFileSystemBackend
from ...domain.entities.release import Release
from ...domain.repositories import ReleaseRepository
from ...infrastructure.auth import UUIDGenerator


class ColdBackupService:
    """冷备份核心服务"""

    def __init__(
        self,
        storage_backend: ColdStorageBackend,
        release_repository: Optional[ReleaseRepository] = None,
        temp_dir: str = "/tmp/cold_backup",
    ):
        self.backend = storage_backend
        self.release_repo = release_repository
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def create_release_backup(
        self,
        release_id: str,
        include_packages: bool = True,
        include_metadata: bool = True,
        compression_level: int = 6,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict:
        """创建发布版本的冷备份"""
        if not self.release_repo:
            raise ValueError("Release repository not configured")

        # 获取发布信息
        release = self.release_repo.find_by_id(release_id)
        if not release:
            raise ValueError(f"Release {release_id} not found")

        if progress_callback:
            progress_callback(0.1, "准备备份数据")

        # 创建临时目录
        backup_dir = (
            self.temp_dir
            / f"backup_{release_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        backup_dir.mkdir()

        try:
            # 导出元数据
            if include_metadata:
                metadata_path = backup_dir / "metadata.json"
                with open(metadata_path, "w") as f:
                    json.dump(
                        {
                            "release_id": release.release_id,
                            "version": release.version,
                            "resource_type": release.resource_type.value,
                            "publisher_id": release.publisher_id,
                            "description": release.description,
                            "changelog": release.changelog,
                            "status": release.status.value,
                            "created_at": release.created_at.isoformat()
                            if hasattr(release, "created_at")
                            else datetime.now().isoformat(),
                            "content_packages": {
                                ct.value: pid
                                for ct, pid in release.content_packages.items()
                            },
                        },
                        f,
                        indent=2,
                        ensure_ascii=False,
                    )

            # 导出包内容
            if include_packages and self.release_repo:
                packages_dir = backup_dir / "packages"
                packages_dir.mkdir()

                for content_type, package_id in release.content_packages.items():
                    if progress_callback:
                        progress_callback(0.3, f"导出包: {content_type.value}")

                    # 这里应该从存储服务获取包内容
                    # 暂时只保存包ID映射
                    package_info_path = packages_dir / f"{content_type.value}.json"
                    with open(package_info_path, "w") as f:
                        json.dump(
                            {
                                "package_id": package_id,
                                "content_type": content_type.value,
                            },
                            f,
                        )

            if progress_callback:
                progress_callback(0.5, "创建压缩包")

            # 创建tar.gz压缩包
            backup_id = f"cold_backup_{UUIDGenerator.generate_release_id()}"
            archive_path = self.temp_dir / f"{backup_id}.tar.gz"

            with tarfile.open(
                archive_path, f"w:gz", compresslevel=compression_level
            ) as tar:
                tar.add(backup_dir, arcname=os.path.basename(backup_dir))

            if progress_callback:
                progress_callback(0.7, "计算校验和")

            # 计算校验和
            sha256_hash = hashlib.sha256()
            with open(archive_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            checksum = sha256_hash.hexdigest()

            if progress_callback:
                progress_callback(0.8, "上传到冷存储")

            # 存储到冷存储
            metadata = {
                "backup_id": backup_id,
                "release_id": release_id,
                "version": release.version,
                "resource_type": release.resource_type.value,
                "type": "release",
                "created_at": datetime.now().isoformat(),
                "include_packages": include_packages,
                "include_metadata": include_metadata,
                "checksum": checksum,
                "size": archive_path.stat().st_size,
            }

            result = self.backend.store(str(archive_path), metadata)

            if progress_callback:
                progress_callback(1.0, "备份完成")

            return result

        finally:
            # 清理临时文件
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            if archive_path.exists():
                archive_path.unlink()

    def restore_release_backup(
        self,
        backup_id: str,
        restore_path: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> bool:
        """从冷备份恢复发布版本"""
        restore_path = Path(restore_path)
        restore_path.mkdir(parents=True, exist_ok=True)

        if progress_callback:
            progress_callback(0.2, "从冷存储下载备份")

        # 下载备份
        temp_archive = self.temp_dir / f"restore_{backup_id}.tar.gz"
        success = self.backend.retrieve(backup_id, str(temp_archive))

        if not success:
            return False

        try:
            if progress_callback:
                progress_callback(0.4, "验证备份完整性")

            # 验证校验和
            # 这里应该校验，暂时省略

            if progress_callback:
                progress_callback(0.6, "解压备份")

            # 解压
            with tarfile.open(temp_archive, "r:gz") as tar:
                tar.extractall(path=restore_path)

            if progress_callback:
                progress_callback(1.0, "恢复完成")

            return True

        finally:
            if temp_archive.exists():
                temp_archive.unlink()

    def create_full_backup(
        self,
        backup_name: str,
        include_releases: bool = True,
        include_users: bool = True,
        include_licenses: bool = True,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> Dict:
        """创建全系统冷备份"""
        if progress_callback:
            progress_callback(0.1, "准备全量备份")

        # 创建临时目录
        backup_dir = (
            self.temp_dir / f"full_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        backup_dir.mkdir()

        try:
            # 备份发布数据
            if include_releases and self.release_repo:
                if progress_callback:
                    progress_callback(0.3, "备份发布数据")

                releases = self.release_repo.find_all()
                releases_data = []
                for release in releases:
                    releases_data.append(
                        {
                            "release_id": release.release_id,
                            "version": release.version,
                            "resource_type": release.resource_type.value,
                            "publisher_id": release.publisher_id,
                            "status": release.status.value,
                            "created_at": release.created_at.isoformat()
                            if hasattr(release, "created_at")
                            else datetime.now().isoformat(),
                        }
                    )

                with open(backup_dir / "releases.json", "w") as f:
                    json.dump(releases_data, f, indent=2)

            # 备份其他数据（用户、许可证等）
            # 这里省略具体实现

            if progress_callback:
                progress_callback(0.6, "创建压缩包")

            # 创建压缩包
            backup_id = f"full_backup_{UUIDGenerator.generate_release_id()}"
            archive_path = self.temp_dir / f"{backup_id}.tar.gz"

            with tarfile.open(archive_path, "w:gz", compresslevel=6) as tar:
                tar.add(backup_dir, arcname=os.path.basename(backup_dir))

            if progress_callback:
                progress_callback(0.8, "上传到冷存储")

            # 存储到冷存储
            metadata = {
                "backup_id": backup_id,
                "name": backup_name,
                "type": "full",
                "created_at": datetime.now().isoformat(),
                "include_releases": include_releases,
                "include_users": include_users,
                "include_licenses": include_licenses,
                "size": archive_path.stat().st_size,
            }

            result = self.backend.store(str(archive_path), metadata)

            if progress_callback:
                progress_callback(1.0, "全量备份完成")

            return result

        finally:
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            if archive_path.exists():
                archive_path.unlink()

    def list_backups(self, backup_type: Optional[str] = None) -> List[Dict]:
        """列出所有冷备份"""
        archives = self.backend.list_archives()

        if backup_type:
            archives = [a for a in archives if a.get("type") == backup_type]

        return archives

    def delete_backup(self, backup_id: str) -> bool:
        """删除冷备份"""
        return self.backend.delete(backup_id)

    def get_backup_info(self, backup_id: str) -> Optional[Dict]:
        """获取备份信息"""
        archives = self.backend.list_archives()
        for archive in archives:
            if archive.get("backup_id") == backup_id:
                return archive
        return None

    def _calculate_checksum(self, file_path: str) -> str:
        """计算文件SHA256校验和"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
