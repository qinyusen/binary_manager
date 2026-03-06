"""
DownloadService TDD 测试套件
"""
import pytest
from unittest.mock import Mock
from release_portal.application.download_service import DownloadService
from release_portal.domain.entities.release import Release
from release_portal.domain.entities.user import User
from release_portal.domain.value_objects import ResourceType, ContentType, AccessLevel, License
from release_portal.domain.repositories import UserRepository, ReleaseRepository
from release_portal.domain.services import IStorageService, IAuthorizationService


class TestDownloadService:
    """DownloadService 测试类"""
    
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
        auth.get_user_license_info = Mock(return_value={
            'access_level': 'FULL_ACCESS',
            'allowed_resource_types': [ResourceType.BSP]
        })
        return auth
    
    @pytest.fixture
    def service(self, mock_user_repo, mock_release_repo, mock_storage, mock_auth):
        return DownloadService(
            user_repository=mock_user_repo,
            release_repository=mock_release_repo,
            storage_service=mock_storage,
            authorization_service=mock_auth
        )
    
    def test_get_available_packages_full_access(self, service, mock_release_repo, mock_storage, mock_auth):
        """测试获取完全访问权限的可下载包"""
        # Arrange
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="pub_123"
        )
        release.add_package(ContentType.SOURCE, "pkg_source")
        release.add_package(ContentType.BINARY, "pkg_binary")
        release.add_package(ContentType.DOCUMENT, "pkg_doc")
        
        mock_release_repo.find_by_id = Mock(return_value=release)
        mock_storage.get_package_info = Mock(side_effect=[
            {'package_name': 'bsp-source', 'version': '1.0.0', 'size': 1024},
            {'package_name': 'bsp-binary', 'version': '1.0.0', 'size': 2048},
            {'package_name': 'bsp-doc', 'version': '1.0.0', 'size': 512}
        ])
        
        # Act
        packages = service.get_available_packages("user_123", "rel_123")
        
        # Assert
        assert len(packages) == 3
        assert {p['content_type'] for p in packages} == {'SOURCE', 'BINARY', 'DOCUMENT'}
    
    def test_get_available_packages_binary_access(self, service, mock_release_repo, mock_storage, mock_auth):
        """测试受限访问权限只能下载二进制和文档"""
        # Arrange
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="pub_123"
        )
        release.add_package(ContentType.SOURCE, "pkg_source")
        release.add_package(ContentType.BINARY, "pkg_binary")
        release.add_package(ContentType.DOCUMENT, "pkg_doc")
        
        mock_release_repo.find_by_id = Mock(return_value=release)
        mock_auth.can_download_content = Mock(side_effect=[
            False,  # SOURCE
            True,   # BINARY
            True    # DOCUMENT
        ])
        mock_storage.get_package_info = Mock(return_value={
            'package_name': 'bsp-binary', 'version': '1.0.0', 'size': 2048
        })
        
        # Act
        packages = service.get_available_packages("user_123", "rel_123")
        
        # Assert
        assert len(packages) == 2
        assert {p['content_type'] for p in packages} == {'BINARY', 'DOCUMENT'}
    
    def test_download_package_success(self, service, mock_release_repo, mock_storage, mock_auth):
        """测试成功下载包"""
        # Arrange
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="pub_123"
        )
        release.add_package(ContentType.BINARY, "pkg_binary")
        
        mock_release_repo.find_by_id = Mock(return_value=release)
        
        # Act
        service.download_package("user_123", "rel_123", "BINARY", "/tmp")
        
        # Assert
        mock_storage.download_package.assert_called_once_with("pkg_binary", "/tmp")
    
    def test_download_package_without_license_fails(self, service, mock_auth):
        """测试没有许可证不能下载"""
        # Arrange
        mock_auth.validate_user_license = Mock(return_value=False)
        
        # Act & Assert
        with pytest.raises(ValueError, match="许可证"):
            service.get_available_packages("user_123", "rel_123")
    
    def test_list_downloadable_releases(self, service, mock_user_repo, mock_release_repo, mock_auth):
        """测试列出可下载的发布"""
        # Arrange
        user = Mock()
        mock_user_repo.find_by_id = Mock(return_value=user)
        
        releases = [Mock(), Mock()]
        mock_release_repo.find_all = Mock(return_value=releases)
        
        # Act
        result = service.list_downloadable_releases("user_123")
        
        # Assert
        assert result == releases
    
    def test_get_user_license_info(self, service, mock_auth):
        """测试获取用户许可证信息"""
        # Arrange
        mock_auth.get_user_license_info = Mock(return_value={'license_id': 'lic_123'})
        
        # Act
        result = service.get_user_license_info("user_123")
        
        # Assert
        assert result == {'license_id': 'lic_123'}
        mock_auth.get_user_license_info.assert_called_once_with("user_123")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
