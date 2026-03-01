from typing import List, Dict, Optional
from ..domain.entities.user import User
from ..domain.entities.release import Release
from ..domain.value_objects import ContentType
from ..domain.repositories import UserRepository, ReleaseRepository
from ..domain.services import IStorageService, IAuthorizationService


class DownloadService:
    """下载服务，负责处理包下载和权限过滤"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        release_repository: ReleaseRepository,
        storage_service: IStorageService,
        authorization_service: IAuthorizationService
    ):
        self._user_repository = user_repository
        self._release_repository = release_repository
        self._storage_service = storage_service
        self._authorization_service = authorization_service
    
    def get_available_packages(self, user_id: str, release_id: str) -> List[Dict]:
        """获取用户可下载的包列表
        
        Args:
            user_id: 用户ID
            release_id: 发布ID
            
        Returns:
            可下载的包列表
        """
        if not self._authorization_service.validate_user_license(user_id):
            raise ValueError("User does not have an active license")
        
        release = self._release_repository.find_by_id(release_id)
        if not release:
            raise ValueError(f"Release '{release_id}' not found")
        
        if not self._authorization_service.can_download_release(user_id, release.resource_type):
            raise ValueError(f"License does not allow access to {release.resource_type.value}")
        
        available_packages = []
        
        for content_type, package_id in release.content_packages.items():
            if self._authorization_service.can_download_content(
                user_id,
                release.resource_type,
                content_type
            ):
                package_info = self._storage_service.get_package_info(package_id)
                available_packages.append({
                    'content_type': str(content_type),
                    'package_id': package_id,
                    'package_name': package_info['package_name'],
                    'version': package_info['version'],
                    'size': package_info['size']
                })
        
        return available_packages
    
    def download_package(self, user_id: str, release_id: str, content_type: str, output_dir: str) -> None:
        """下载包
        
        Args:
            user_id: 用户ID
            release_id: 发布ID
            content_type: 内容类型
            output_dir: 输出目录
        """
        if not self._authorization_service.validate_user_license(user_id):
            raise ValueError("User does not have an active license")
        
        release = self._release_repository.find_by_id(release_id)
        if not release:
            raise ValueError(f"Release '{release_id}' not found")
        
        ct = ContentType.from_string(content_type)
        package_id = release.get_package_id(ct)
        if not package_id:
            raise ValueError(f"Release does not have {content_type} package")
        
        if not self._authorization_service.can_download_content(
            user_id,
            release.resource_type,
            ct
        ):
            raise ValueError(f"License does not allow downloading {content_type}")
        
        self._storage_service.download_package(str(package_id), output_dir)
    
    def list_downloadable_releases(self, user_id: str) -> List[Release]:
        """列出用户可下载的发布
        
        Args:
            user_id: 用户ID
            
        Returns:
            可下载的发布列表
        """
        if not self._authorization_service.validate_user_license(user_id):
            return []
        
        user = self._user_repository.find_by_id(user_id)
        if not user:
            return []
        
        license_info = self._authorization_service.get_user_license_info(user_id)
        if not license_info:
            return []
        
        all_releases = self._release_repository.find_all()
        downloadable = []
        
        for release in all_releases:
            if self._authorization_service.can_download_release(user_id, release.resource_type):
                downloadable.append(release)
        
        return downloadable
    
    def get_user_license_info(self, user_id: str) -> Optional[dict]:
        """获取用户许可证信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            许可证信息字典
        """
        return self._authorization_service.get_user_license_info(user_id)
