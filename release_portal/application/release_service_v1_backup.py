from typing import Optional, Dict, TYPE_CHECKING
from ..domain.entities.release import Release
from ..domain.entities.audit_log import AuditAction
from ..domain.value_objects import ResourceType, ContentType
from ..domain.repositories import ReleaseRepository
from ..domain.services import IStorageService
from ..infrastructure.auth import UUIDGenerator
from .test_runner import PrePublishValidator, TestResult

if TYPE_CHECKING:
    from .audit_service import AuditService


class ReleaseService:
    """发布服务，负责管理资源的发布流程"""
    
    def __init__(
        self,
        release_repository: ReleaseRepository,
        storage_service: IStorageService,
        authorization_service=None,
        audit_service: Optional['AuditService'] = None,
        enable_pre_publish_tests: bool = False,
        test_level: str = "critical"
    ):
        self._release_repository = release_repository
        self._storage_service = storage_service
        self._authorization_service = authorization_service
        self._audit_service = audit_service
        self._enable_pre_publish_tests = enable_pre_publish_tests
        self._test_level = test_level
        self._test_validator: Optional[PrePublishValidator] = None
        
        if enable_pre_publish_tests:
            self._test_validator = PrePublishValidator()
    
    def create_draft(
        self,
        resource_type: ResourceType,
        version: str,
        publisher_id: str,
        description: Optional[str] = None,
        changelog: Optional[str] = None
    ) -> Release:
        """创建草稿版本的发布
        
        Args:
            resource_type: 资源类型（BSP/DRIVER/EXAMPLES）
            version: 版本号
            publisher_id: 发布者ID
            description: 描述
            changelog: 变更日志
            
        Returns:
            创建的 Release 对象
        """
        release_id = UUIDGenerator.generate_release_id()
        
        release = Release(
            release_id=release_id,
            resource_type=resource_type,
            version=version,
            publisher_id=publisher_id,
            description=description,
            changelog=changelog
        )
        
        self._release_repository.save(release)
        
        # 记录审计日志
        if self._audit_service:
            self._audit_service.log_action(
                action=AuditAction.CREATE,
                user_id=publisher_id,
                username='',  # 可从 user_repo 获取
                role='Publisher',  # 可从 user 获取
                resource_type=str(resource_type.value),
                resource_id=release_id,
                details={
                    'version': version,
                    'description': description
                }
            )
        
        return release
    
    def add_package(
        self,
        release_id: str,
        content_type: ContentType,
        source_dir: str,
        extract_git: bool = True,
        user_id: Optional[str] = None
    ) -> str:
        """为发布添加包
        
        Args:
            release_id: 发布ID
            content_type: 内容类型（SOURCE/BINARY/DOCUMENT）
            source_dir: 源代码目录
            extract_git: 是否从 git 提取信息
            user_id: 用户ID（用于权限验证，可选）
            
        Returns:
            包ID
        """
        release = self._release_repository.find_by_id(release_id)
        if not release:
            raise ValueError(f"Release '{release_id}' not found")
        
        if release.status.value != 'DRAFT':
            raise ValueError("Can only add packages to draft releases")
        
        if self._authorization_service and user_id:
            if not self._authorization_service.can_publish(user_id, release.resource_type):
                raise ValueError(f"User does not have permission to publish {release.resource_type.value}")
        
        package_name = f"{release.resource_type.value.lower()}-diggo-{release.version.replace('.', '-')}-{content_type.value.lower()}"
        
        result = self._storage_service.publish_package(
            source_dir=source_dir,
            package_name=package_name,
            version=release.version,
            extract_git=extract_git
        )
        
        package_id = result['package_id']
        release.add_package(content_type, package_id)
        self._release_repository.save(release)
        
        # 记录审计日志
        if self._audit_service:
            self._audit_service.log_action(
                action=AuditAction.UPLOAD,
                user_id=user_id or 'system',
                username='',
                role='Publisher',
                resource_type=str(release.resource_type.value),
                resource_id=release_id,
                details={
                    'content_type': str(content_type.value),
                    'package_id': package_id
                }
            )
        
        return package_id
    
    def publish_release(
        self, 
        release_id: str, 
        user_id: Optional[str] = None,
        run_tests: Optional[bool] = None,
        test_level: Optional[str] = None
    ) -> Release:
        """发布版本
        
        Args:
            release_id: 发布ID
            user_id: 用户ID（用于权限验证，可选）
            run_tests: 是否运行测试（None表示使用默认配置）
            test_level: 测试级别（critical/all/api/integration）
            
        Returns:
            发布的 Release 对象
            
        Raises:
            ValueError: 发布失败或测试未通过
        """
        release = self._release_repository.find_by_id(release_id)
        if not release:
            raise ValueError(f"Release '{release_id}' not found")
        
        if self._authorization_service and user_id:
            if not self._authorization_service.can_publish(user_id, release.resource_type):
                raise ValueError(f"User does not have permission to publish {release.resource_type.value}")
        
        if not release.has_package(ContentType.BINARY):
            raise ValueError("Release must have at least a binary package")
        
        # 发布前测试验证
        should_run_tests = run_tests if run_tests is not None else self._enable_pre_publish_tests
        if should_run_tests and self._test_validator:
            level = test_level or self._test_level
            print(f"\n🧪 发布前测试验证（级别: {level}）...")
            
            test_result = self._test_validator.validate_before_publish(
                release_id=release_id,
                test_level=level
            )
            
            if not test_result.passed:
                raise ValueError(
                    f"发布前测试失败，无法发布版本。\n"
                    f"测试结果: {test_result.passed_tests}/{test_result.total_tests} 通过\n"
                    f"失败: {test_result.failed_tests}\n"
                    f"错误: {'; '.join(test_result.errors[:3])}"
                )
            
            print(f"✅ 测试验证通过，继续发布...")
        
        old_status = release.status.value
        release.publish()
        self._release_repository.save(release)
        
        # 记录审计日志
        if self._audit_service:
            self._audit_service.log_action(
                action=AuditAction.PUBLISH,
                user_id=user_id or 'system',
                username='',
                role='Publisher',
                resource_type=str(release.resource_type.value),
                resource_id=release_id,
                details={
                    'version': release.version,
                    'old_status': old_status,
                    'new_status': release.status.value,
                    'tests_run': should_run_tests
                }
            )
        
        return release
    
    def archive_release(self, release_id: str, user_id: Optional[str] = None) -> Release:
        """归档版本
        
        Args:
            release_id: 发布ID
            user_id: 用户ID（用于权限验证，可选）
            
        Returns:
            归档的 Release 对象
        """
        release = self._release_repository.find_by_id(release_id)
        if not release:
            raise ValueError(f"Release '{release_id}' not found")
        
        if self._authorization_service and user_id:
            if not self._authorization_service.can_publish(user_id, release.resource_type):
                raise ValueError(f"User does not have permission to publish {release.resource_type.value}")
        
        old_status = release.status.value
        release.archive()
        self._release_repository.save(release)
        
        # 记录审计日志
        if self._audit_service:
            self._audit_service.log_action(
                action=AuditAction.ARCHIVE,
                user_id=user_id or 'system',
                username='',
                role='Publisher',
                resource_type=str(release.resource_type.value),
                resource_id=release_id,
                details={
                    'version': release.version,
                    'old_status': old_status,
                    'new_status': release.status.value
                }
            )
        
        return release
    
    def get_release(self, release_id: str) -> Optional[Release]:
        """获取发布信息"""
        return self._release_repository.find_by_id(release_id)
    
    def list_releases(
        self,
        resource_type: Optional[ResourceType] = None,
        status: Optional[str] = None
    ):
        """列出发布"""
        if resource_type:
            return self._release_repository.find_by_resource_type(resource_type)
        elif status:
            from ..domain.value_objects import ReleaseStatus
            return self._release_repository.find_by_status(ReleaseStatus.from_string(status))
        else:
            return self._release_repository.find_all()
