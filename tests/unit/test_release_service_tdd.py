"""
ReleaseService TDD 测试套件
遵循测试驱动开发原则
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from release_portal.application.release_service import ReleaseService
from release_portal.domain.entities.release import Release
from release_portal.domain.value_objects import ResourceType, ContentType, ReleaseStatus
from release_portal.domain.repositories import ReleaseRepository
from release_portal.domain.services import IStorageService
from release_portal.application.test_runner import PrePublishValidator, TestResult


class TestReleaseService:
    """ReleaseService 测试类 - TDD 方式"""
    
    @pytest.fixture
    def mock_repository(self):
        """模拟发布仓储"""
        return Mock(spec=ReleaseRepository)
    
    @pytest.fixture
    def mock_storage(self):
        """模拟存储服务"""
        storage = Mock(spec=IStorageService)
        storage.publish_package = Mock(return_value={
            'package_id': 'pkg_123',
            'archive_path': '/path/to/archive.zip'
        })
        return storage
    
    @pytest.fixture
    def mock_auth_service(self):
        """模拟认证服务"""
        auth = Mock()
        auth.can_publish = Mock(return_value=True)
        return auth
    
    @pytest.fixture
    def service(self, mock_repository, mock_storage, mock_auth_service):
        """创建服务实例"""
        return ReleaseService(
            release_repository=mock_repository,
            storage_service=mock_storage,
            authorization_service=mock_auth_service
        )
    
    def test_create_draft_success(self, service, mock_repository):
        """测试成功创建草稿"""
        # Arrange
        resource_type = ResourceType.BSP
        version = "1.0.0"
        publisher_id = "user_123"
        description = "Test BSP"
        
        # Act
        release = service.create_draft(
            resource_type=resource_type,
            version=version,
            publisher_id=publisher_id,
            description=description
        )
        
        # Assert
        assert release.resource_type == resource_type
        assert release.version == version
        assert release.publisher_id == publisher_id
        assert release.description == description
        assert release.status == ReleaseStatus.DRAFT
        mock_repository.save.assert_called_once()
    
    def test_add_package_to_draft(self, service, mock_repository, mock_storage):
        """测试添加包到草稿"""
        # Arrange
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="user_123"
        )
        mock_repository.find_by_id = Mock(return_value=release)
        
        # Act
        package_id = service.add_package(
            release_id="rel_123",
            content_type=ContentType.BINARY,
            source_dir="/path/to/source",
            extract_git=False,
            user_id="user_123"
        )
        
        # Assert
        assert package_id == "pkg_123"
        assert release.has_package(ContentType.BINARY)
        mock_storage.publish_package.assert_called_once()
        mock_repository.save.assert_called_once()
    
    def test_add_package_to_published_release_fails(self, service, mock_repository):
        """测试不能给已发布的发布添加包"""
        # Arrange
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="user_123"
        )
        release.publish()  # 设置为已发布
        mock_repository.find_by_id = Mock(return_value=release)
        
        # Act & Assert
        with pytest.raises(ValueError, match="只能添加到草稿"):
            service.add_package(
                release_id="rel_123",
                content_type=ContentType.BINARY,
                source_dir="/path/to/source"
            )
    
    def test_publish_release_success(self, service, mock_repository):
        """测试成功发布"""
        # Arrange
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="user_123"
        )
        release.add_package(ContentType.BINARY, "pkg_123")
        mock_repository.find_by_id = Mock(return_value=release)
        
        # Act
        result = service.publish_release(release_id="rel_123")
        
        # Assert
        assert result.status == ReleaseStatus.PUBLISHED
        assert result.published_at is not None
        mock_repository.save.assert_called_once()
    
    def test_publish_release_without_binary_fails(self, service, mock_repository):
        """测试没有二进制包的发布不能发布"""
        # Arrange
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="user_123"
        )
        mock_repository.find_by_id = Mock(return_value=release)
        
        # Act & Assert
        with pytest.raises(ValueError, match="至少有一个二进制包"):
            service.publish_release(release_id="rel_123")
    
    def test_archive_release(self, service, mock_repository):
        """测试归档发布"""
        # Arrange
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="user_123"
        )
        mock_repository.find_by_id = Mock(return_value=release)
        
        # Act
        result = service.archive_release(release_id="rel_123")
        
        # Assert
        assert result.status == ReleaseStatus.ARCHIVED
        mock_repository.save.assert_called_once()
    
    def test_get_release(self, service, mock_repository):
        """测试获取发布"""
        # Arrange
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="user_123"
        )
        mock_repository.find_by_id = Mock(return_value=release)
        
        # Act
        result = service.get_release("rel_123")
        
        # Assert
        assert result == release
        mock_repository.find_by_id.assert_called_once_with("rel_123")
    
    def test_list_releases_by_type(self, service, mock_repository):
        """测试按类型列出发布"""
        # Arrange
        releases = [Mock(), Mock()]
        mock_repository.find_by_resource_type = Mock(return_value=releases)
        
        # Act
        result = service.list_releases(resource_type=ResourceType.BSP)
        
        # Assert
        assert result == releases
        mock_repository.find_by_resource_type.assert_called_once_with(ResourceType.BSP)
    
    def test_add_package_checks_permission(self, service, mock_repository, mock_auth_service):
        """测试添加包时检查权限"""
        # Arrange
        mock_auth_service.can_publish = Mock(return_value=False)
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="user_123"
        )
        mock_repository.find_by_id = Mock(return_value=release)
        
        # Act & Assert
        with pytest.raises(ValueError, match="权限"):
            service.add_package(
                release_id="rel_123",
                content_type=ContentType.BINARY,
                source_dir="/path/to/source",
                user_id="user_123"
            )
        
        mock_auth_service.can_publish.assert_called_once()


class TestReleaseServiceWithTests:
    """ReleaseService 自动化测试功能测试"""
    
    @pytest.fixture
    def service_with_tests(self, mock_repository, mock_storage, mock_auth_service):
        """创建启用测试的服务"""
        return ReleaseService(
            release_repository=mock_repository,
            storage_service=mock_storage,
            authorization_service=mock_auth_service,
            enable_pre_publish_tests=True,
            test_level="critical"
        )
    
    @pytest.fixture
    def mock_repository(self):
        """模拟发布仓储"""
        return Mock(spec=ReleaseRepository)
    
    @pytest.fixture
    def mock_storage(self):
        """模拟存储服务"""
        storage = Mock(spec=IStorageService)
        storage.publish_package = Mock(return_value={
            'package_id': 'pkg_123',
            'archive_path': '/path/to/archive.zip'
        })
        return storage
    
    @pytest.fixture
    def mock_auth_service(self):
        """模拟认证服务"""
        auth = Mock()
        auth.can_publish = Mock(return_value=True)
        return auth
    
    def test_publish_with_tests_pass(self, service_with_tests, mock_repository):
        """测试发布时运行测试且通过"""
        # Arrange
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="user_123"
        )
        release.add_package(ContentType.BINARY, "pkg_123")
        mock_repository.find_by_id = Mock(return_value=release)
        
        # Mock test validator
        test_result = TestResult(
            passed=True,
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
            duration=30.0
        )
        with patch.object(service_with_tests._test_validator, 'validate_before_publish', return_value=test_result):
            # Act
            result = service_with_tests.publish_release(
                release_id="rel_123",
                run_tests=True
            )
        
        # Assert
        assert result.status == ReleaseStatus.PUBLISHED
    
    def test_publish_with_tests_fails(self, service_with_tests, mock_repository):
        """测试发布时测试失败阻止发布"""
        # Arrange
        release = Release(
            release_id="rel_123",
            resource_type=ResourceType.BSP,
            version="1.0.0",
            publisher_id="user_123"
        )
        release.add_package(ContentType.BINARY, "pkg_123")
        mock_repository.find_by_id = Mock(return_value=release)
        
        # Mock test validator - 测试失败
        test_result = TestResult(
            passed=False,
            total_tests=10,
            passed_tests=5,
            failed_tests=5,
            duration=30.0
        )
        with patch.object(service_with_tests._test_validator, 'validate_before_publish', return_value=test_result):
            # Act & Assert
            with pytest.raises(ValueError, match="测试失败"):
                service_with_tests.publish_release(
                    release_id="rel_123",
                    run_tests=True
                )


class TestReleaseServiceEdgeCases:
    """边界情况和异常测试"""
    
    @pytest.fixture
    def mock_repository(self):
        return Mock(spec=ReleaseRepository)
    
    @pytest.fixture
    def mock_storage(self):
        storage = Mock(spec=IStorageService)
        storage.publish_package = Mock(return_value={
            'package_id': 'pkg_123',
            'archive_path': '/path/to/archive.zip'
        })
        return storage
    
    @pytest.fixture
    def service(self, mock_repository, mock_storage):
        return ReleaseService(
            release_repository=mock_repository,
            storage_service=mock_storage
        )
    
    def test_get_nonexistent_release(self, service, mock_repository):
        """测试获取不存在的发布"""
        # Arrange
        mock_repository.find_by_id = Mock(return_value=None)
        
        # Act
        result = service.get_release("nonexistent")
        
        # Assert
        assert result is None
    
    def test_add_package_to_nonexistent_release(self, service, mock_repository):
        """测试向不存在的发布添加包"""
        # Arrange
        mock_repository.find_by_id = Mock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            service.add_package(
                release_id="nonexistent",
                content_type=ContentType.BINARY,
                source_dir="/path/to/source"
            )
    
    def test_publish_nonexistent_release(self, service, mock_repository):
        """测试发布不存在的发布"""
        # Arrange
        mock_repository.find_by_id = Mock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="not found"):
            service.publish_release(release_id="nonexistent")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
