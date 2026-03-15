"""
FTP/FTPS冷备份存储后端
"""

import io
import json
import logging
from datetime import datetime
from ftplib import FTP, FTP_TLS
from pathlib import Path
from typing import Dict, List, Optional, Union

from .base import ColdStorageBackend

logger = logging.getLogger(__name__)


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

        self._ftp: Optional[Union[FTP, FTP_TLS]] = None
        self._metadata_file = f"{self.remote_path}/metadata.json"

    def _connect(self) -> None:
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

            if self.use_tls and isinstance(self._ftp, FTP_TLS):
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
        assert self._ftp is not None
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
        assert self._ftp is not None
        try:
            data = io.BytesIO()
            self._ftp.retrbinary(f"RETR {self._metadata_file}", data.write)
            return json.loads(data.getvalue().decode("utf-8"))
        except Exception as e:
            logger.debug(f"下载元数据失败: {e}")
            return {}

    def _upload_metadata(self, metadata: Dict) -> None:
        assert self._ftp is not None
        self._ensure_remote_dir()
        data = json.dumps(metadata, indent=2, ensure_ascii=False).encode("utf-8")
        self._ftp.storbinary(f"STOR {self._metadata_file}", io.BytesIO(data))

    def store(self, backup_path: str, metadata: Dict) -> Dict:
        source_path = Path(backup_path)
        if not source_path.exists():
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")

        self._connect()
        self._ensure_remote_dir()

        backup_id = metadata["backup_id"]
        remote_file = f"{self.remote_path}/{backup_id}.tar.gz"

        checksum = self._calculate_checksum(source_path)

        assert self._ftp is not None
        with open(source_path, "rb") as f:
            self._ftp.storbinary(f"STOR {remote_file}", f)

        all_metadata = self._download_metadata()
        archive_metadata = {
            **metadata,
            "storage_location": f"ftp://{self.host}{remote_file}",
            "checksum": checksum,
            "size": source_path.stat().st_size,
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

        assert self._ftp is not None
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

        assert self._ftp is not None
        try:
            self._ftp.delete(remote_file)
        except Exception as e:
            logger.debug(f"删除 FTP 文件失败: {e}")

        del all_metadata[backup_id]
        self._upload_metadata(all_metadata)
        return True
