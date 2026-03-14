"""
冷备份存储后端实现
包含抽象基类和各种存储后端的具体实现
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

# 尝试导入可选依赖
try:
    import boto3
    from botocore.exceptions import ClientError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

try:
    import paramiko

    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False


class ColdStorageBackend(ABC):
    """冷存储后端抽象基类"""

    @abstractmethod
    def store(self, backup_path: str, metadata: Dict) -> Dict:
        """存储备份到冷存储"""
        pass

    @abstractmethod
    def retrieve(self, backup_id: str, local_path: str) -> bool:
        """从冷存储检索备份"""
        pass

    @abstractmethod
    def list_archives(self) -> List[Dict]:
        """列出所有归档"""
        pass

    @abstractmethod
    def delete(self, backup_id: str) -> bool:
        """删除归档"""
        pass

    def _calculate_checksum(self, file_path: str) -> str:
        """计算文件SHA256校验和"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class LocalFileSystemBackend(ColdStorageBackend):
    """本地文件系统冷存储后端"""

    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path).expanduser().resolve()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_path / "metadata.json"
        self._load_metadata()

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


class S3ColdStorageBackend(ColdStorageBackend):
    """S3兼容冷存储后端（支持AWS Glacier）"""

    def __init__(
        self,
        bucket_name: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        region_name: str = "us-east-1",
        storage_class: str = "GLACIER",  # STANDARD | GLACIER | DEEP_ARCHIVE
    ):
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for S3 backend")

        self.bucket_name = bucket_name
        self.storage_class = storage_class

        # 初始化S3客户端
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            region_name=region_name,
        )

        # 确保bucket存在
        try:
            self.s3.head_bucket(Bucket=bucket_name)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region_name},
                )
            else:
                raise

    def store(self, backup_path: str, metadata: Dict) -> Dict:
        """存储备份到S3"""
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")

        backup_id = metadata["backup_id"]
        object_key = f"cold_backups/{backup_id}.tar.gz"

        # 计算校验和
        checksum = self._calculate_checksum(backup_path)

        # 上传到S3
        with open(backup_path, "rb") as f:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=object_key,
                Body=f,
                StorageClass=self.storage_class,
                Metadata={
                    "backup_id": backup_id,
                    "checksum": checksum,
                    "version": metadata["version"],
                    "resource_type": metadata["resource_type"],
                    "created_at": metadata["created_at"],
                },
            )

        # 获取对象信息
        response = self.s3.head_object(Bucket=self.bucket_name, Key=object_key)

        return {
            **metadata,
            "storage_location": f"s3://{self.bucket_name}/{object_key}",
            "checksum": checksum,
            "size": response["ContentLength"],
            "storage_class": self.storage_class,
            "stored_at": datetime.now().isoformat(),
            "etag": response["ETag"].strip('"'),
        }

    def retrieve(self, backup_id: str, local_path: str) -> bool:
        """从S3检索备份"""
        object_key = f"cold_backups/{backup_id}.tar.gz"

        try:
            # 检查对象是否存在
            self.s3.head_object(Bucket=self.bucket_name, Key=object_key)

            # 下载文件
            self.s3.download_file(self.bucket_name, object_key, local_path)
            return True

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise

    def list_archives(self) -> List[Dict]:
        """列出S3中的所有归档"""
        archives = []
        continuation_token = None

        while True:
            kwargs = {"Bucket": self.bucket_name, "Prefix": "cold_backups/"}
            if continuation_token:
                kwargs["ContinuationToken"] = continuation_token

            response = self.s3.list_objects_v2(**kwargs)

            if "Contents" in response:
                for obj in response["Contents"]:
                    key = obj["Key"]
                    if key.endswith(".tar.gz"):
                        backup_id = key.split("/")[-1].replace(".tar.gz", "")

                        # 获取元数据
                        head = self.s3.head_object(Bucket=self.bucket_name, Key=key)
                        metadata = head.get("Metadata", {})

                        archives.append(
                            {
                                "backup_id": backup_id,
                                "storage_location": f"s3://{self.bucket_name}/{key}",
                                "size": obj["Size"],
                                "last_modified": obj["LastModified"].isoformat(),
                                "storage_class": obj.get("StorageClass", "STANDARD"),
                                "version": metadata.get("version"),
                                "resource_type": metadata.get("resource_type"),
                                "checksum": metadata.get("checksum"),
                            }
                        )

            if not response.get("IsTruncated"):
                break
            continuation_token = response.get("NextContinuationToken")

        return archives

    def delete(self, backup_id: str) -> bool:
        """从S3删除归档"""
        object_key = f"cold_backups/{backup_id}.tar.gz"

        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:
            return False
