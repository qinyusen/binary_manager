"""
针对合并后的ReleaseService v2的补充测试用例
验证精简版功能与原版完全兼容
"""

import pytest
from unittest.mock import Mock, patch
from release_portal.application.release_service import ReleaseService
from release_portal.domain.entities.release import Release
from release_portal.domain.value_objects import ResourceType, ContentType, ReleaseStatus
from release_portal.domain.repositories import ReleaseRepository
from release_portal.domain.services import IStorageService
from release_portal.application.test_runner import PrePublishValidator, TestResult


class TestReleaseServiceV2Compatibility:
    """测试ReleaseService v2的兼容性和新特性"""

    @pytest.fixture
    def mock_repository(self):
        """模拟发布仓储"""
        return Mock(spec=ReleaseRepository)

    @pytest.fixture
    def mock_storage(self):
        """模拟存储服务"""
        storage = Mock(spec=IStorageService)
        storage.publish_package = Mock(
            return_value={
                "package_id": "pkg_123",
                "archive_path": "/path/to/archive.zip",
            }
        )
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
            authorization_service=mock_auth_service,
        )

    def test_v2_class_implements_all_methods(self, service):
        """验证v2版本实现了所有公有方法"""
        # 核心业务方法
        assert hasattr(service, "create_draft")
        assert hasattr(service, "add_package")
        assert hasattr(service, "publish_release")
        assert hasattr(service, "archive_release")
        assert hasattr(service, "get_release")
        assert hasattr(service, "list_releases")

        # 私有辅助方法
        assert hasattr(service, "_get_and_validate_release")
        assert hasattr(service, "_run_tests_if_needed")
        assert hasattr(service, "_log")

    def test_v2_code_size_reduction(self):
        """验证v2版本代码确实精简了"""
        import os

        v2_path = os.path.join(
            os.path.dirname(__file__),
            "../../release_portal/application/release_service.py",
        )
        backup_path = os.path.join(
            os.path.dirname(__file__),
            "../../release_portal/application/release_service_v1_backup.py",
        )

        if os.path.exists(backup_path):
            with open(v2_path, "r") as f:
                v2_lines = len(f.readlines())

            with open(backup_path, "r") as f:
                v1_lines = len(f.readlines())

            # 验证代码减少至少20%
            assert v2_lines < v1_lines * 0.8, (
                f"v2版本({v2_lines}行)比v1({v1_lines}行)减少不足20%"
            )

    def test_get_and_validate_release_combined_logic(self, service, mock_repository):
        """测试合并后的验证逻辑"""
        # 测试不存在的发布
        mock_repository.find_by_id.return_value = None
        with pytest.raises(ValueError, match="发布 'rel_123' 不存在"):
            service._get_and_validate_release("rel_123", "user_123")

        # 测试已发布的发布不能修改
        mock_release = Mock(spec=Release)
        mock_release.status = ReleaseStatus.PUBLISHED
        mock_repository.find_by_id.return_value = mock_release

        with pytest.raises(ValueError, match="只能修改草稿状态的发布"):
            service._get_and_validate_release("rel_123", "user_123")

        # 测试权限验证
        mock_release.status = ReleaseStatus.DRAFT
        service._auth.can_publish.return_value = False

        with pytest.raises(ValueError, match="无权发布 BSP 类型的资源"):
            mock_release.resource_type = ResourceType.BSP
            service._get_and_validate_release("rel_123", "user_123")

    def test_audit_log_action_names_correct(
        self, service, mock_repository, mock_storage, mock_auth_service
    ):
        """测试审计日志使用正确的枚举值"""
        mock_audit = Mock()
        service._audit = mock_audit

        # 创建草稿
        mock_repository.save = Mock()
        release = service.create_draft(ResourceType.BSP, "1.0.0", "user_123")

        # 验证使用RELEASE_CREATE
        assert mock_audit.log_action.called
        call_args = mock_audit.log_action.call_args
        from release_portal.domain.entities.audit_log import AuditAction

        assert call_args[1]["action"] == AuditAction.RELEASE_CREATE

        # 添加包
        mock_repository.find_by_id.return_value = release
        package_id = service.add_package(
            release.release_id, ContentType.BINARY, "/tmp/source"
        )

        # 验证使用UPLOAD_PACKAGE
        assert mock_audit.log_action.call_count == 2
        call_args = mock_audit.log_action.call_args
        assert call_args[1]["action"] == AuditAction.UPLOAD_PACKAGE

        # 发布
        release.add_package = Mock()
        package_id = service.add_package(
            release_id=release.release_id,
            content_type=ContentType.BINARY,
            source_dir="/tmp/test",
            user_id="pub_123",
        )

        assert package_id == "pkg_123"
        assert release.add_package.called

        # 发布
        release.publish = Mock()
        release.has_package = Mock(return_value=True)
        published = service.publish_release(release.release_id, "pub_123")
        assert published is not None
        assert release.publish.called

    def test_pre_publish_test_integration(self, service, mock_repository):
        """测试发布前测试集成"""
        service._test_enabled = True
        service._test_validator = Mock(spec=PrePublishValidator)

        # 测试通过的情况
        service._test_validator.validate_before_publish.return_value = TestResult(
            passed=True, total_tests=10, passed_tests=10, failed_tests=0
        )

        mock_release = Mock(spec=Release)
        mock_release.status = ReleaseStatus.DRAFT
        mock_release.has_package = Mock(return_value=True)
        mock_repository.find_by_id.return_value = mock_release

        result = service.publish_release("rel_123", "user_123", run_tests=True)
        assert result is not None

        # 测试失败的情况
        service._test_validator.validate_before_publish.return_value = TestResult(
            passed=False, total_tests=10, passed_tests=8, failed_tests=2
        )

        with pytest.raises(ValueError, match="发布前测试失败"):
            service.publish_release("rel_123", "user_123", run_tests=True)
