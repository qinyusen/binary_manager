"""
SFTP冷备份存储后端
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .base import ColdStorageBackend

logger = logging.getLogger(__name__)

# 尝试导入可选依赖
try:
    import paramiko

    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False


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
        """初始化SFTP后端

        Args:
            host: SFTP服务器地址
            port: SFTP服务器端口
            username: 用户名
            password: 密码
            key_path: SSH私钥路径
            remote_path: 远程存储路径
            timeout: 连接超时时间（秒）
        """
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
        """建立SFTP连接"""
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
        """断开SFTP连接"""
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
        """确保远程目录存在"""
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
        """从远程服务器加载元数据"""
        try:
            with self._sftp_client.open(self._metadata_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    def _save_metadata(self, metadata: Dict) -> None:
        """保存元数据到远程服务器"""
        self._ensure_remote_dir()
        with self._sftp_client.open(self._metadata_file, "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

    def store(self, backup_path: str, metadata: Dict) -> Dict:
        """存储备份到SFTP服务器"""
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
        """从SFTP服务器检索备份"""
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
        """列出SFTP服务器上的所有归档"""
        self._connect()
        all_metadata = self._load_metadata()
        return list(all_metadata.values())

    def delete(self, backup_id: str) -> bool:
        """从SFTP服务器删除归档"""
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
