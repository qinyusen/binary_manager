"""
S3兼容冷备份存储后端（支持AWS Glacier）
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from .base import ColdStorageBackend

if TYPE_CHECKING:
    import boto3
    from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import ClientError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None  # type: ignore
    ClientError = Exception  # type: ignore


class S3ColdStorageBackend(ColdStorageBackend):
    """S3兼容冷存储后端（支持AWS Glacier）"""

    def __init__(
        self,
        bucket_name: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        region_name: str = "us-east-1",
        storage_class: str = "GLACIER",
    ):
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for S3 backend")

        self.bucket_name = bucket_name
        self.storage_class = storage_class

        self.s3 = boto3.client(  # type: ignore
            "s3",
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
            region_name=region_name,
        )

        try:
            self.s3.head_bucket(Bucket=bucket_name)
        except ClientError:  # type: ignore
            self.s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region_name},
            )

    def store(self, backup_path: str, metadata: Dict) -> Dict:
        source_path = Path(backup_path)
        if not source_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")

        backup_id = metadata["backup_id"]
        object_key = f"cold_backups/{backup_id}.tar.gz"

        checksum = self._calculate_checksum(source_path)

        with open(source_path, "rb") as f:
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
        object_key = f"cold_backups/{backup_id}.tar.gz"

        try:
            self.s3.head_object(Bucket=self.bucket_name, Key=object_key)
            self.s3.download_file(self.bucket_name, object_key, local_path)
            return True
        except ClientError:  # type: ignore
            return False

    def list_archives(self) -> List[Dict]:
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
        object_key = f"cold_backups/{backup_id}.tar.gz"

        try:
            self.s3.delete_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError:  # type: ignore
            return False
