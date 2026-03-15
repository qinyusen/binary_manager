"""
冷备份存储后端实现
包含抽象基类和各种存储后端的具体实现
"""

import os
import json
import shutil
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

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


class SFTPColdStorageBackend(ColdStorageBackend):
    """SFTP冷存储后端"""

    def __init__(
        self,
        host: str,
        port: int = 22,
        username: Optional[str] = None,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        remote_path: str = "/cold_backups",
        timeout: int = 30,
    ):
        if not PARAMIKO_AVAILABLE:
            raise ImportError("paramiko is required for SFTP backend")

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key_path = key_path
        self.remote_path = remote_path.rstrip("/")
        self.timeout = timeout

        self._ssh_client: Optional[paramiko.SSHClient] = None
        self._sftp_client: Optional[paramiko.SFTPClient] = None
        self._metadata_file = f"{self.remote_path}/metadata.json"

    def _connect(self) -> None:
        if self._sftp_client is not None:
            return

        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs = {
            "hostname": self.host,
            "port": self.port,
            "username": self.username,
            "timeout": self.timeout,
            "allow_agent": False,
            "look_for_keys": False,
        }

        if self.password:
            connect_kwargs["password"] = self.password
        elif self.key_path:
            connect_kwargs["key_filename"] = self.key_path

        try:
            self._ssh_client.connect(**connect_kwargs)
            self._sftp_client = self._ssh_client.open_sftp()
        except Exception as e:
            self._disconnect()
            raise ConnectionError(f"Failed to connect to SFTP server: {e}")

    def _disconnect(self) -> None:
        if self._sftp_client:
            try:
                self._sftp_client.close()
            except Exception as e:
                logger.debug(f"关闭 SFTP 连接时出错: {e}")
            self._sftp_client = None

        if self._ssh_client:
            try:
                self._ssh_client.close()
            except Exception as e:
                logger.debug(f"关闭 SSH 连接时出错: {e}")
            self._ssh_client = None

    def _ensure_remote_dir(self) -> None:
        try:
            self._sftp_client.stat(self.remote_path)
        except FileNotFoundError:
            parts = self.remote_path.split("/")
            current = ""
            for part in parts:
                if not part:
                    continue
                current += f"/{part}"
                try:
                    self._sftp_client.stat(current)
                except FileNotFoundError:
                    self._sftp_client.mkdir(current)

    def _load_metadata(self) -> Dict:
        try:
            with self._sftp_client.open(self._metadata_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def _save_metadata(self, metadata: Dict) -> None:
        self._ensure_remote_dir()
        with self._sftp_client.open(self._metadata_file, "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def store(self, backup_path: str, metadata: Dict) -> Dict:
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")

        self._connect()
        self._ensure_remote_dir()

        backup_id = metadata["backup_id"]
        remote_file = f"{self.remote_path}/{backup_id}.tar.gz"

        checksum = self._calculate_checksum(backup_path)

        self._sftp_client.put(str(backup_path), remote_file)

        all_metadata = self._load_metadata()
        archive_metadata = {
            **metadata,
            "storage_location": f"sftp://{self.host}{remote_file}",
            "checksum": checksum,
            "size": backup_path.stat().st_size,
            "stored_at": datetime.now().isoformat(),
        }
        all_metadata[backup_id] = archive_metadata
        self._save_metadata(all_metadata)

        return archive_metadata

    def retrieve(self, backup_id: str, local_path: str) -> bool:
        self._connect()

        all_metadata = self._load_metadata()
        if backup_id not in all_metadata:
            return False

        remote_file = f"{self.remote_path}/{backup_id}.tar.gz"

        try:
            self._sftp_client.get(remote_file, local_path)
            return True
        except FileNotFoundError:
            return False

    def list_archives(self) -> List[Dict]:
        self._connect()
        all_metadata = self._load_metadata()
        return list(all_metadata.values())

    def delete(self, backup_id: str) -> bool:
        self._connect()

        all_metadata = self._load_metadata()
        if backup_id not in all_metadata:
            return False

        remote_file = f"{self.remote_path}/{backup_id}.tar.gz"

        try:
            self._sftp_client.remove(remote_file)
        except FileNotFoundError:
            pass

        del all_metadata[backup_id]
        self._save_metadata(all_metadata)
        return True


class FTPColdStorageBackend(ColdStorageBackend):
    """FTP/FTPS冷存储后端"""

    def __init__(
        self,
        host: str,
        port: int = 21,
        username: Optional[str] = None,
        password: Optional[str] = None,
        remote_path: str = "/cold_backups",
        use_tls: bool = True,
        passive_mode: bool = True,
        timeout: int = 30,
    ):
        self.host = host
        self.port = port
        self.username = username or "anonymous"
        self.password = password or ""
        self.remote_path = remote_path.rstrip("/")
        self.use_tls = use_tls
        self.passive_mode = passive_mode
        self.timeout = timeout

        self._ftp = None
        self._metadata_file = f"{self.remote_path}/metadata.json"

    def _connect(self) -> None:
        from ftplib import FTP, FTP_TLS

        if self._ftp is not None:
            try:
                self._ftp.voidcmd("NOOP")
                return
            except Exception as e:
                logger.debug(f"FTP 连接检查失败，将重新连接: {e}")
                self._ftp = None

        try:
            if self.use_tls:
                self._ftp = FTP_TLS(timeout=self.timeout)
            else:
                self._ftp = FTP(timeout=self.timeout)

            self._ftp.connect(self.host, self.port)
            self._ftp.login(self.username, self.password)

            if self.use_tls and hasattr(self._ftp, "prot_p"):
                self._ftp.prot_p()

            self._ftp.set_pasv(self.passive_mode)
        except Exception as e:
            self._disconnect()
            raise ConnectionError(f"Failed to connect to FTP server: {e}")

    def _disconnect(self) -> None:
        if self._ftp:
            try:
                self._ftp.quit()
            except Exception as e:
                logger.debug(f"FTP quit 失败: {e}")
            try:
                self._ftp.close()
            except Exception as e:
                logger.debug(f"FTP close 失败: {e}")
            self._ftp = None

    def _ensure_remote_dir(self) -> None:
        parts = self.remote_path.strip("/").split("/")
        current = ""
        for part in parts:
            current += f"/{part}"
            try:
                self._ftp.cwd(current)
            except Exception:
                try:
                    self._ftp.mkd(current)
                except Exception as e:
                    logger.debug(f"创建目录失败 {current}: {e}")
        self._ftp.cwd("/")

    def _download_metadata(self) -> Dict:
        import io

        try:
            data = io.BytesIO()
            self._ftp.retrbinary(f"RETR {self._metadata_file}", data.write)
            return json.loads(data.getvalue().decode("utf-8"))
        except Exception as e:
            logger.debug(f"下载元数据失败: {e}")
            return {}

    def _upload_metadata(self, metadata: Dict) -> None:
        import io

        self._ensure_remote_dir()
        data = json.dumps(metadata, indent=2, ensure_ascii=False).encode("utf-8")
        self._ftp.storbinary(f"STOR {self._metadata_file}", io.BytesIO(data))

    def store(self, backup_path: str, metadata: Dict) -> Dict:
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")

        self._connect()
        self._ensure_remote_dir()

        backup_id = metadata["backup_id"]
        remote_file = f"{self.remote_path}/{backup_id}.tar.gz"

        checksum = self._calculate_checksum(backup_path)

        with open(backup_path, "rb") as f:
            self._ftp.storbinary(f"STOR {remote_file}", f)

        all_metadata = self._download_metadata()
        archive_metadata = {
            **metadata,
            "storage_location": f"ftp://{self.host}{remote_file}",
            "checksum": checksum,
            "size": backup_path.stat().st_size,
            "stored_at": datetime.now().isoformat(),
        }
        all_metadata[backup_id] = archive_metadata
        self._upload_metadata(all_metadata)

        return archive_metadata

    def retrieve(self, backup_id: str, local_path: str) -> bool:
        self._connect()

        all_metadata = self._download_metadata()
        if backup_id not in all_metadata:
            return False

        remote_file = f"{self.remote_path}/{backup_id}.tar.gz"

        try:
            with open(local_path, "wb") as f:
                self._ftp.retrbinary(f"RETR {remote_file}", f.write)
            return True
        except Exception as e:
            logger.warning(f"从 FTP 检索文件失败: {e}")
            return False

    def list_archives(self) -> List[Dict]:
        self._connect()
        all_metadata = self._download_metadata()
        return list(all_metadata.values())

    def delete(self, backup_id: str) -> bool:
        self._connect()

        all_metadata = self._download_metadata()
        if backup_id not in all_metadata:
            return False

        remote_file = f"{self.remote_path}/{backup_id}.tar.gz"

        try:
            self._ftp.delete(remote_file)
        except Exception as e:
            logger.debug(f"删除 FTP 文件失败: {e}")

        del all_metadata[backup_id]
        self._upload_metadata(all_metadata)
        return True
