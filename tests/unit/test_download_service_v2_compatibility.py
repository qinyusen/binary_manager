"""
针对合并后的DownloadService v2的补充测试用例
验证精简版功能与原版完全兼容
"""

import pytest
from unittest.mock import Mock
from release_portal.application.download_service import DownloadService
from release_portal.domain.entities.release import Release
from release_portal.domain.value_objects import ResourceType, ContentType, AccessLevel
from release_portal.domain.repositories import UserRepository, ReleaseRepository
from release_portal.domain.services import IStorageService, IAuthorizationService


class TestDownloadServiceV2Compatibility:
    """测试DownloadService v2的兼容性和新特性"""

    @pytest.fixture
    def mock_user_repo(self):
        return Mock(spec=UserRepository)

    @pytest.fixture
    def mock_release_repo(self):
        return Mock(spec=ReleaseRepository)

    @pytest.fixture
    def mock_storage(self):
        return Mock(spec=IStorageService)

    @pytest.fixture
    def mock_auth(self):
        auth = Mock(spec=IAuthorizationService)
        auth.validate_user_license = Mock(return_value=True)
        auth.can_download_release = Mock(return_value=True)
        auth.can_download_content = Mock(return_value=True)
        auth.get_user_license_info = Mock(
            return_value={
                "access_level": AccessLevel.FULL_ACCESS,
                "allowed_resource_types": [ResourceType.BSP],
            }
        )
        return auth

    @pytest.fixture
    def service(self, mock_user_repo, mock_release_repo, mock_storage, mock_auth):
        return DownloadService(
            user_repository=mock_user_repo,
            release_repository=mock_release_repo,
            storage_service=mock_storage,
            authorization_service=mock_auth,
        )

    def test_v2_class_implements_all_methods(self, service):
        """验证v2版本实现了所有公有方法"""
        # 核心业务方法
        assert hasattr(service, "get_available_packages")
        assert hasattr(service, "download_package")
        assert hasattr(service, "list_downloadable_releases")
        assert hasattr(service, "get_user_license_info")

        # 私有辅助方法
        assert hasattr(service, "_validate_license")
        assert hasattr(service, "_validate_download_permission")

    def test_v2_code_size_reduction(self):
        """验证v2版本代码确实精简了"""
        import os

        v2_path = os.path.join(
            os.path.dirname(__file__),
            "../../release_portal/application/download_service.py",
        )
        backup_path = os.path.join(
            os.path.dirname(__file__),
            "../../release_portal/application/download_service_v1_backup.py",
        )

        if os.path.exists(backup_path):
            with open(v2_path, "r") as f:
                v2_lines = len(f.readlines())

            with open(backup_path, "r") as f:
                v1_lines = len(f.readlines())

            # 验证代码减少至少15%
            assert v2_lines < v1_lines * 0.85, (
                f"v2版本({v2_lines}行)比v1({v1_lines}行)减少不足15%"
            )

    def test_validate_license_method(self, service, mock_auth):
        """测试提取的许可证验证方法"""
        # 测试有效许可证
        mock_auth.validate_user_license.return_value = True
        service._validate_license("user_123")  # 不抛异常就是成功

        # 测试无效许可证
        mock_auth.validate_user_license.return_value = False
        with pytest.raises(ValueError, match="用户没有有效的许可证"):
            service._validate_license("user_123")

    def test_validate_download_permission_method(self, service, mock_auth):
        """测试提取的下载权限验证方法"""
        # 测试有权限
        mock_auth.can_download_release.return_value = True
        service._validate_download_permission("user_123", ResourceType.BSP)  # 不抛异常

        # 测试无权限
        mock_auth.can_download_release.return_value = False
        with pytest.raises(ValueError, match="许可证不允许访问 BSP 类型的资源"):
            service._validate_download_permission("user_123", ResourceType.BSP)

    def test_get_available_packages_full_access(
        self, service, mock_release_repo, mock_storage, mock_auth
    ):
        """测试获取可用包列表（完全访问权限）"""
        mock_release = Mock(spec=Release)
        mock_release.resource_type = ResourceType.BSP
        mock_release.content_packages = {
            ContentType.SOURCE: "pkg_source",
            ContentType.BINARY: "pkg_binary",
            ContentType.DOCUMENT: "pkg_doc",
        }
        mock_release_repo.find_by_id.return_value = mock_release

        mock_storage.get_package_info.side_effect = [
            {"package_name": "bsp-source-1.0.0", "version": "1.0.0", "size": 1024},
            {"package_name": "bsp-binary-1.0.0", "version": "1.0.0", "size": 2048},
            {"package_name": "bsp-doc-1.0.0", "version": "1.0.0", "size": 512},
        ]

        packages = service.get_available_packages("user_123", "rel_123")

        assert len(packages) == 3
        assert any(p["content_type"] == str(ContentType.SOURCE) for p in packages)
        assert any(p["content_type"] == str(ContentType.BINARY) for p in packages)
        assert any(p["content_type"] == str(ContentType.DOCUMENT) for p in packages)

    def test_get_available_packages_binary_only(
        self, service, mock_release_repo, mock_storage, mock_auth
    ):
        """测试获取可用包列表（仅二进制权限）"""

        # 更改权限为仅二进制访问
        def mock_can_download(user_id, resource_type, content_type):
            return content_type in [ContentType.BINARY, ContentType.DOCUMENT]

        mock_auth.can_download_content.side_effect = mock_can_download

        mock_release = Mock(spec=Release)
        mock_release.resource_type = ResourceType.BSP
        mock_release.content_packages = {
            ContentType.SOURCE: "pkg_source",
            ContentType.BINARY: "pkg_binary",
            ContentType.DOCUMENT: "pkg_doc",
        }
        mock_release_repo.find_by_id.return_value = mock_release

        mock_storage.get_package_info.side_effect = [
            {"package_name": "bsp-binary-1.0.0", "version": "1.0.0", "size": 2048},
            {"package_name": "bsp-doc-1.0.0", "version": "1.0.0", "size": 512},
        ]

        packages = service.get_available_packages("user_123", "rel_123")

        # 应该只能看到二进制包和文档包
        assert len(packages) == 2
        assert not any(p["content_type"] == str(ContentType.SOURCE) for p in packages)
        assert any(p["content_type"] == str(ContentType.BINARY) for p in packages)
        assert any(p["content_type"] == str(ContentType.DOCUMENT) for p in packages)

    def test_list_downloadable_releases(self, service, mock_release_repo, mock_auth):
        """测试列出可下载的发布"""
        mock_releases = [
            Mock(resource_type=ResourceType.BSP),
            Mock(resource_type=ResourceType.DRIVER),
            Mock(resource_type=ResourceType.EXAMPLES),
        ]
        mock_release_repo.find_all.return_value = mock_releases

        # 全部允许下载
        mock_auth.can_download_release.return_value = True
        releases = service.list_downloadable_releases("user_123")
        assert len(releases) == 3

        # 只允许下载BSP
        def mock_can_download(user_id, resource_type):
            return resource_type == ResourceType.BSP

        mock_auth.can_download_release.side_effect = mock_can_download
        releases = service.list_downloadable_releases("user_123")
        assert len(releases) == 1
        assert releases[0].resource_type == ResourceType.BSP

    def test_download_package_success(
        self, service, mock_release_repo, mock_storage, mock_auth
    ):
        """测试成功下载包"""
        mock_release = Mock(spec=Release)
        mock_release.resource_type = ResourceType.BSP
        mock_release.get_package_id = Mock(return_value="pkg_123")
        mock_release_repo.find_by_id.return_value = mock_release

        service.download_package("user_123", "rel_123", "BINARY", "/tmp/output")

        mock_storage.download_package.assert_called_once_with("pkg_123", "/tmp/output")

    def test_download_package_no_permission(
        self, service, mock_release_repo, mock_auth
    ):
        """测试无权限下载包"""
        mock_release = Mock(spec=Release)
        mock_release.resource_type = ResourceType.BSP
        mock_release.get_package_id = Mock(return_value="pkg_123")
        mock_release_repo.find_by_id.return_value = mock_release

        mock_auth.can_download_content.return_value = False

        with pytest.raises(ValueError, match="不允许下载 BINARY"):
            service.download_package("user_123", "rel_123", "BINARY", "/tmp/output")

    def test_v2_backward_compatibility(
        self, service, mock_release_repo, mock_storage, mock_auth
    ):
        """测试v2版本与原有API的兼容性"""
        # 验证原有API调用方式不变
        mock_release = Mock(spec=Release)
        mock_release.resource_type = ResourceType.BSP
        mock_release.content_packages = {ContentType.BINARY: "pkg_123"}
        mock_release.get_package_id = Mock(return_value="pkg_123")
        mock_release_repo.find_by_id.return_value = mock_release

        mock_storage.get_package_info.return_value = {
            "package_name": "bsp-binary-1.0.0",
            "version": "1.0.0",
            "size": 2048,
        }

        # 原有调用方式应该正常工作
        packages = service.get_available_packages("user_123", "rel_123")
        assert len(packages) == 1

        license_info = service.get_user_license_info("user_123")
        assert license_info["access_level"] == AccessLevel.FULL_ACCESS
