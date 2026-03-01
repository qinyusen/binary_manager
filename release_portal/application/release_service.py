from typing import Optional, Dict
from ..domain.entities.release import Release
from ..domain.value_objects import ResourceType, ContentType
from ..domain.repositories import ReleaseRepository
from ..domain.services import IStorageService
from ..infrastructure.auth import UUIDGenerator


class ReleaseService:
    """发布服务，负责管理资源的发布流程"""
    
    def __init__(
        self,
        release_repository: ReleaseRepository,
        storage_service: IStorageService,
        authorization_service=None
    ):
        self._release_repository = release_repository
        self._storage_service = storage_service
        self._authorization_service = authorization_service
    
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
        
        return package_id
    
    def publish_release(self, release_id: str, user_id: Optional[str] = None) -> Release:
        """发布版本
        
        Args:
            release_id: 发布ID
            user_id: 用户ID（用于权限验证，可选）
            
        Returns:
            发布的 Release 对象
        """
        release = self._release_repository.find_by_id(release_id)
        if not release:
            raise ValueError(f"Release '{release_id}' not found")
        
        if self._authorization_service and user_id:
            if not self._authorization_service.can_publish(user_id, release.resource_type):
                raise ValueError(f"User does not have permission to publish {release.resource_type.value}")
        
        if not release.has_package(ContentType.BINARY):
            raise ValueError("Release must have at least a binary package")
        
        release.publish()
        self._release_repository.save(release)
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
        
        release.archive()
        self._release_repository.save(release)
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
