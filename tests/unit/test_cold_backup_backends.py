"""
冷备份存储后端单元测试
"""

import hashlib
import json
import os
import tarfile
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from release_portal.application.cold_backup.backends import (
    BOTO3_AVAILABLE,
    PARAMIKO_AVAILABLE,
    ColdStorageBackend,
    FTPColdStorageBackend,
    LocalFileSystemBackend,
    S3ColdStorageBackend,
    SFTPColdStorageBackend,
)


class TestColdStorageBackendBase:
    """测试 ColdStorageBackend 抽象基类"""

    def test_is_abstract_class(self):
        with pytest.raises(TypeError):
            ColdStorageBackend()

    def test_calculate_checksum(self, tmp_path):
        class ConcreteBackend(ColdStorageBackend):
            def store(self, backup_path, metadata):
                pass

            def retrieve(self, backup_id, local_path):
                pass

            def list_archives(self):
                pass

            def delete(self, backup_id):
                pass

        backend = ConcreteBackend()
        test_file = tmp_path / "test.txt"
        test_content = b"test content for checksum"
        test_file.write_bytes(test_content)

        expected = hashlib.sha256(test_content).hexdigest()
        result = backend._calculate_checksum(str(test_file))

        assert result == expected
        assert len(result) == 64


class TestLocalFileSystemBackend:
    """测试本地文件系统后端"""

    @pytest.fixture
    def backend(self, tmp_path):
        storage_path = tmp_path / "cold_storage"
        return LocalFileSystemBackend(str(storage_path))

    @pytest.fixture
    def sample_backup_file(self, tmp_path):
        backup_file = tmp_path / "backup.tar.gz"
        with tarfile.open(backup_file, "w:gz") as tar:
            info = tarfile.TarInfo(name="test.txt")
            info.size = 12
            tar.addfile(info)
        return backup_file

    @pytest.fixture
    def sample_metadata(self):
        return {
            "backup_id": "test-backup-001",
            "version": "1.0.0",
            "resource_type": "BSP",
            "created_at": "2026-03-15T12:00:00",
        }

    def test_init_creates_storage_directory(self, tmp_path):
        storage_path = tmp_path / "new_storage"
        assert not storage_path.exists()

        LocalFileSystemBackend(str(storage_path))

        assert storage_path.exists()

    def test_init_expands_home_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = os.path.join(tmpdir, "cold_storage")
            backend = LocalFileSystemBackend(storage_path)
            assert backend.storage_path.exists()

    def test_list_archives_empty(self, backend):
        archives = backend.list_archives()
        assert archives == []

    def test_store_success(self, backend, sample_backup_file, sample_metadata):
        result = backend.store(str(sample_backup_file), sample_metadata)

        assert result["backup_id"] == "test-backup-001"
        assert "storage_path" in result
        assert "checksum" in result
        assert "size" in result
        assert "stored_at" in result
        assert Path(result["storage_path"]).exists()

    def test_store_file_not_found(self, backend, sample_metadata):
        with pytest.raises(FileNotFoundError):
            backend.store("/nonexistent/backup.tar.gz", sample_metadata)

    def test_retrieve_success(
        self, backend, sample_backup_file, sample_metadata, tmp_path
    ):
        backend.store(str(sample_backup_file), sample_metadata)

        retrieve_path = tmp_path / "retrieved.tar.gz"
        success = backend.retrieve("test-backup-001", str(retrieve_path))

        assert success is True
        assert retrieve_path.exists()

    def test_retrieve_not_found(self, backend, tmp_path):
        retrieve_path = tmp_path / "retrieved.tar.gz"
        success = backend.retrieve("nonexistent-backup", str(retrieve_path))

        assert success is False
        assert not retrieve_path.exists()

    def test_list_archives_after_store(
        self, backend, sample_backup_file, sample_metadata
    ):
        backend.store(str(sample_backup_file), sample_metadata)

        archives = backend.list_archives()

        assert len(archives) == 1
        assert archives[0]["backup_id"] == "test-backup-001"

    def test_delete_success(self, backend, sample_backup_file, sample_metadata):
        backend.store(str(sample_backup_file), sample_metadata)

        success = backend.delete("test-backup-001")

        assert success is True
        archives = backend.list_archives()
        assert len(archives) == 0

    def test_delete_not_found(self, backend):
        success = backend.delete("nonexistent-backup")
        assert success is False

    def test_checksum_verification(
        self, backend, sample_backup_file, sample_metadata, tmp_path
    ):
        result = backend.store(str(sample_backup_file), sample_metadata)

        stored_checksum = result["checksum"]
        expected = hashlib.sha256(sample_backup_file.read_bytes()).hexdigest()

        assert stored_checksum == expected

    def test_multiple_archives(self, backend, sample_backup_file, tmp_path):
        for i in range(3):
            metadata = {
                "backup_id": f"backup-{i}",
                "version": "1.0.0",
                "resource_type": "BSP",
                "created_at": "2026-03-15T12:00:00",
            }
            backend.store(str(sample_backup_file), metadata)

        archives = backend.list_archives()
        assert len(archives) == 3


@pytest.mark.skipif(not BOTO3_AVAILABLE, reason="boto3 not installed")
class TestS3ColdStorageBackend:
    """测试 S3 后端（使用 Mock）"""

    @pytest.fixture
    def mock_s3_client(self):
        with patch(
            "release_portal.application.cold_backup.backends.s3.boto3"
        ) as mock_boto3:
            mock_client = MagicMock()
            mock_boto3.client.return_value = mock_client
            mock_client.head_bucket.return_value = {}
            yield mock_client

    @pytest.fixture
    def backend(self, mock_s3_client):
        return S3ColdStorageBackend(
            bucket_name="test-bucket",
            access_key="test-key",
            secret_key="test-secret",
            region_name="us-east-1",
        )

    @pytest.fixture
    def sample_backup_file(self, tmp_path):
        backup_file = tmp_path / "backup.tar.gz"
        backup_file.write_bytes(b"test backup content")
        return backup_file

    @pytest.fixture
    def sample_metadata(self):
        return {
            "backup_id": "test-backup-001",
            "version": "1.0.0",
            "resource_type": "BSP",
            "created_at": "2026-03-15T12:00:00",
        }

    def test_init_creates_bucket_if_not_exists(self, mock_s3_client):
        from botocore.exceptions import ClientError

        error_response = {"Error": {"Code": "404"}}
        mock_s3_client.head_bucket.side_effect = ClientError(
            error_response, "HeadBucket"
        )

        S3ColdStorageBackend(bucket_name="new-bucket")

        mock_s3_client.create_bucket.assert_called_once()

    def test_store_success(
        self, backend, mock_s3_client, sample_backup_file, sample_metadata
    ):
        mock_s3_client.head_object.return_value = {
            "ContentLength": 100,
            "ETag": '"abc123"',
        }

        result = backend.store(str(sample_backup_file), sample_metadata)

        assert result["backup_id"] == "test-backup-001"
        assert "s3://test-bucket/" in result["storage_location"]
        mock_s3_client.put_object.assert_called_once()

    def test_retrieve_success(self, backend, mock_s3_client, tmp_path):
        mock_s3_client.head_object.return_value = {}

        local_path = str(tmp_path / "retrieved.tar.gz")
        success = backend.retrieve("test-backup-001", local_path)

        assert success is True
        mock_s3_client.download_file.assert_called_once()

    def test_retrieve_not_found(self, backend, mock_s3_client, tmp_path):
        from botocore.exceptions import ClientError

        error_response = {"Error": {"Code": "404"}}
        mock_s3_client.head_object.side_effect = ClientError(
            error_response, "HeadObject"
        )

        local_path = str(tmp_path / "retrieved.tar.gz")
        success = backend.retrieve("nonexistent", local_path)

        assert success is False

    def test_list_archives(self, backend, mock_s3_client):
        mock_s3_client.list_objects_v2.return_value = {
            "Contents": [
                {
                    "Key": "cold_backups/backup-001.tar.gz",
                    "Size": 1000,
                    "LastModified": MagicMock(isoformat=lambda: "2026-03-15T12:00:00"),
                    "StorageClass": "GLACIER",
                }
            ],
            "IsTruncated": False,
        }
        mock_s3_client.head_object.return_value = {"Metadata": {"version": "1.0.0"}}

        archives = backend.list_archives()

        assert len(archives) == 1
        assert archives[0]["backup_id"] == "backup-001"

    def test_delete_success(self, backend, mock_s3_client):
        success = backend.delete("test-backup-001")

        assert success is True
        mock_s3_client.delete_object.assert_called_once()


@pytest.mark.skipif(not PARAMIKO_AVAILABLE, reason="paramiko not installed")
class TestSFTPColdStorageBackend:
    """测试 SFTP 后端（使用 Mock）"""

    @pytest.fixture
    def mock_paramiko(self):
        with patch(
            "release_portal.application.cold_backup.backends.sftp.paramiko"
        ) as mock:
            mock_ssh = MagicMock()
            mock_sftp = MagicMock()
            mock.SSHClient.return_value = mock_ssh
            mock_ssh.open_sftp.return_value = mock_sftp
            mock.AutoAddPolicy.return_value = MagicMock()
            yield mock, mock_ssh, mock_sftp

    @pytest.fixture
    def backend(self, mock_paramiko):
        _, _, mock_sftp = mock_paramiko
        backend = SFTPColdStorageBackend(
            host="sftp.example.com",
            port=22,
            username="testuser",
            password="testpass",
            remote_path="/cold_backups",
        )
        backend._sftp_client = mock_sftp
        return backend

    @pytest.fixture
    def sample_backup_file(self, tmp_path):
        backup_file = tmp_path / "backup.tar.gz"
        backup_file.write_bytes(b"test backup content")
        return backup_file

    @pytest.fixture
    def sample_metadata(self):
        return {
            "backup_id": "test-backup-001",
            "version": "1.0.0",
            "resource_type": "BSP",
            "created_at": "2026-03-15T12:00:00",
        }

    def test_init_requires_paramiko(self):
        with patch(
            "release_portal.application.cold_backup.backends.sftp.PARAMIKO_AVAILABLE",
            False,
        ):
            with pytest.raises(ImportError, match="paramiko is required"):
                SFTPColdStorageBackend(host="test.com")

    def test_store_success(
        self, backend, mock_paramiko, sample_backup_file, sample_metadata
    ):
        _, _, mock_sftp = mock_paramiko
        mock_sftp.open.return_value.__enter__ = MagicMock()
        mock_sftp.open.return_value.__exit__ = MagicMock()

        result = backend.store(str(sample_backup_file), sample_metadata)

        assert result["backup_id"] == "test-backup-001"
        assert "sftp://" in result["storage_location"]
        mock_sftp.put.assert_called_once()

    def test_retrieve_success(self, backend, mock_paramiko, tmp_path):
        _, _, mock_sftp = mock_paramiko
        mock_sftp.open.return_value.__enter__ = MagicMock(return_value=MagicMock())
        mock_sftp.open.return_value.__exit__ = MagicMock()

        local_path = str(tmp_path / "retrieved.tar.gz")
        success = backend.retrieve("test-backup-001", local_path)

        mock_sftp.get.assert_called_once()

    def test_list_archives(self, backend, mock_paramiko):
        _, _, mock_sftp = mock_paramiko
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(
            return_value=MagicMock(
                read=MagicMock(
                    return_value=b'{"backup-001": {"backup_id": "backup-001"}}'
                )
            )
        )
        mock_file.__exit__ = MagicMock()
        mock_sftp.open.return_value = mock_file

        archives = backend.list_archives()

        assert isinstance(archives, list)

    def test_delete_success(self, backend, mock_paramiko):
        _, _, mock_sftp = mock_paramiko
        mock_file = MagicMock()
        mock_file.__enter__ = MagicMock(
            return_value=MagicMock(
                read=MagicMock(
                    return_value=b'{"test-backup-001": {"backup_id": "test-backup-001"}}'
                )
            )
        )
        mock_file.__exit__ = MagicMock()
        mock_sftp.open.return_value = mock_file

        success = backend.delete("test-backup-001")

        mock_sftp.remove.assert_called_once()


class TestFTPColdStorageBackend:
    """测试 FTP 后端（使用 Mock）"""

    @pytest.fixture
    def mock_ftp(self):
        with patch(
            "release_portal.application.cold_backup.backends.ftp.FTP_TLS"
        ) as mock_ftp_class:
            mock_ftp_instance = MagicMock()
            mock_ftp_class.return_value = mock_ftp_instance
            yield mock_ftp_instance

    @pytest.fixture
    def backend(self, mock_ftp):
        backend = FTPColdStorageBackend(
            host="ftp.example.com",
            port=21,
            username="testuser",
            password="testpass",
            remote_path="/cold_backups",
            use_tls=True,
        )
        backend._ftp = mock_ftp
        return backend

    @pytest.fixture
    def sample_backup_file(self, tmp_path):
        backup_file = tmp_path / "backup.tar.gz"
        backup_file.write_bytes(b"test backup content")
        return backup_file

    @pytest.fixture
    def sample_metadata(self):
        return {
            "backup_id": "test-backup-001",
            "version": "1.0.0",
            "resource_type": "BSP",
            "created_at": "2026-03-15T12:00:00",
        }

    def test_default_credentials(self):
        backend = FTPColdStorageBackend(host="ftp.example.com")
        assert backend.username == "anonymous"
        assert backend.password == ""

    def test_store_success(
        self, backend, mock_ftp, sample_backup_file, sample_metadata
    ):
        result = backend.store(str(sample_backup_file), sample_metadata)

        assert result["backup_id"] == "test-backup-001"
        assert "ftp://" in result["storage_location"]
        mock_ftp.storbinary.assert_called()

    def test_retrieve_success(self, backend, mock_ftp, tmp_path):
        local_path = str(tmp_path / "retrieved.tar.gz")

        success = backend.retrieve("test-backup-001", local_path)

        mock_ftp.retrbinary.assert_called()

    def test_list_archives(self, backend, mock_ftp):
        archives = backend.list_archives()

        assert isinstance(archives, list)

    def test_delete_success(self, backend, mock_ftp):
        with patch.object(
            backend,
            "_download_metadata",
            return_value={"test-backup-001": {"backup_id": "test-backup-001"}},
        ):
            with patch.object(backend, "_upload_metadata"):
                success = backend.delete("test-backup-001")

                assert success is True
                mock_ftp.delete.assert_called()


class TestBackwardsCompatibility:
    """测试向后兼容性"""

    def test_import_from_backends_module(self):
        from release_portal.application.cold_backup.backends import (
            BOTO3_AVAILABLE,
            PARAMIKO_AVAILABLE,
            ColdStorageBackend,
            FTPColdStorageBackend,
            LocalFileSystemBackend,
            S3ColdStorageBackend,
            SFTPColdStorageBackend,
        )

        assert ColdStorageBackend is not None
        assert LocalFileSystemBackend is not None
        assert S3ColdStorageBackend is not None
        assert SFTPColdStorageBackend is not None
        assert FTPColdStorageBackend is not None

    def test_import_from_submodules(self):
        from release_portal.application.cold_backup.backends.base import (
            ColdStorageBackend,
        )
        from release_portal.application.cold_backup.backends.ftp import (
            FTPColdStorageBackend,
        )
        from release_portal.application.cold_backup.backends.local import (
            LocalFileSystemBackend,
        )
        from release_portal.application.cold_backup.backends.s3 import (
            S3ColdStorageBackend,
        )
        from release_portal.application.cold_backup.backends.sftp import (
            SFTPColdStorageBackend,
        )

        assert ColdStorageBackend is not None
        assert LocalFileSystemBackend is not None

    def test_same_classes(self):
        from release_portal.application.cold_backup.backends import (
            LocalFileSystemBackend as L1,
        )
        from release_portal.application.cold_backup.backends.local import (
            LocalFileSystemBackend as L2,
        )

        assert L1 is L2
