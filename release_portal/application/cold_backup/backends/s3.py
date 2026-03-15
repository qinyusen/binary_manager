"""
S3兼容冷备份存储后端（支持AWS Glacier）
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .base import ColdStorageBackend

logger = logging.getLogger(__name__)

# 尝试导入可选依赖
try:
    import boto3
    from botocore.exceptions import ClientError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


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
        """初始化S3后端

        Args:
            bucket_name: S3存储桶名称
            access_key: AWS访问密钥
            secret_key: AWS秘密密钥
            endpoint_url: 自定义端点URL（用于兼容S3的服务）
            region_name: AWS区域
            storage_class: 存储类别（STANDARD, GLACIER, DEEP_ARCHIVE）
        """
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
        checksum = self._calculate_checksum(str(backup_path))

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
