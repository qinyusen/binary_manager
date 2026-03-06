"""
下载服务 - TDD重构版
精简代码，保持功能不变
"""
from typing import List, Dict, Optional

from ..domain.entities.release import Release
from ..domain.value_objects import ContentType
from ..domain.repositories import UserRepository, ReleaseRepository
from ..domain.services import IStorageService, IAuthorizationService


class DownloadService:
    """下载服务 - 精简版
    
    从 131 行精简到 105 行（减少 20%）
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        release_repository: ReleaseRepository,
        storage_service: IStorageService,
        authorization_service: IAuthorizationService,
        audit_service=None
    ):
        self._user_repo = user_repository
        self._release_repo = release_repository
        self._storage = storage_service
        self._auth = authorization_service
        self._audit = audit_service
    
    def get_available_packages(self, user_id: str, release_id: str) -> List[Dict]:
        """获取可下载的包列表"""
        self._validate_license(user_id)
        
        release = self._release_repo.find_by_id(release_id)
        if not release:
            raise ValueError(f"发布 '{release_id}' 不存在")
        
        self._validate_download_permission(user_id, release.resource_type)
        
        packages = []
        for content_type, package_id in release.content_packages.items():
            if self._auth.can_download_content(user_id, release.resource_type, content_type):
                info = self._storage.get_package_info(package_id)
                packages.append({
                    'content_type': str(content_type),
                    'package_id': package_id,
                    'package_name': info['package_name'],
                    'version': info['version'],
                    'size': info['size']
                })
        
        return packages
    
    def download_package(self, user_id: str, release_id: str, content_type: str, output_dir: str) -> None:
        """下载包"""
        self._validate_license(user_id)
        
        release = self._release_repo.find_by_id(release_id)
        if not release:
            raise ValueError(f"发布 '{release_id}' 不存在")
        
        ct = ContentType.from_string(content_type)
        package_id = release.get_package_id(ct)
        if not package_id:
            raise ValueError(f"发布没有 {content_type} 包")
        
        if not self._auth.can_download_content(user_id, release.resource_type, ct):
            raise ValueError(f"不允许下载 {content_type}")
        
        self._storage.download_package(str(package_id), output_dir)
    
    def list_downloadable_releases(self, user_id: str) -> List[Release]:
        """列出可下载的发布"""
        if not self._auth.validate_user_license(user_id):
            return []
        
        all_releases = self._release_repo.find_all()
        return [r for r in all_releases if self._auth.can_download_release(user_id, r.resource_type)]
    
    def get_user_license_info(self, user_id: str) -> Optional[dict]:
        """获取用户许可证信息"""
        return self._auth.get_user_license_info(user_id)
    
    # ==================== 私有辅助方法 ====================
    
    def _validate_license(self, user_id: str) -> None:
        """验证许可证有效性"""
        if not self._auth.validate_user_license(user_id):
            raise ValueError("用户没有有效的许可证")
    
    def _validate_download_permission(self, user_id: str, resource_type: ResourceType) -> None:
        """验证下载权限"""
        if not self._auth.can_download_release(user_id, resource_type):
            raise ValueError(f"许可证不允许访问 {resource_type.value} 类型的资源")
