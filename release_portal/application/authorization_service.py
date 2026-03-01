from typing import Optional
from ..domain.services import IAuthorizationService
from ..domain.value_objects import ResourceType, ContentType, Permission
from ..domain.entities.user import User
from ..domain.entities.license import License
from ..domain.repositories import UserRepository, LicenseRepository


class AuthorizationService:
    """授权服务实现，负责权限验证逻辑"""
    
    def __init__(
        self,
        user_repository: UserRepository,
        license_repository: LicenseRepository
    ):
        self._user_repository = user_repository
        self._license_repository = license_repository
    
    def can_download_release(
        self,
        user_id: str,
        resource_type: ResourceType
    ) -> bool:
        """验证用户是否可以下载指定类型的资源"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            return False
        
        if not user.license_id:
            return False
        
        license = self._license_repository.find_by_id(user.license_id)
        if not license or not license.is_active:
            return False
        
        return license.allows_resource_type(resource_type)
    
    def can_download_content(
        self,
        user_id: str,
        resource_type: ResourceType,
        content_type: ContentType
    ) -> bool:
        """验证用户是否可以下载指定内容类型"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            return False
        
        if not user.license_id:
            return False
        
        license = self._license_repository.find_by_id(user.license_id)
        if not license or not license.is_active:
            return False
        
        if not license.allows_resource_type(resource_type):
            return False
        
        return license.allows_content_type(content_type.value)
    
    def can_publish(self, user_id: str, resource_type: ResourceType) -> bool:
        """验证用户是否可以发布指定类型的资源"""
        user = self._user_repository.find_by_id(user_id)
        if not user:
            return False
        
        return user.has_permission('publish', resource_type.value)
    
    def get_user_license_info(self, user_id: str) -> Optional[dict]:
        """获取用户的许可证信息"""
        user = self._user_repository.find_by_id(user_id)
        if not user or not user.license_id:
            return None
        
        license = self._license_repository.find_by_id(user.license_id)
        if not license:
            return None
        
        return license.to_dict()
    
    def validate_user_license(self, user_id: str) -> bool:
        """验证用户的许可证是否有效"""
        user = self._user_repository.find_by_id(user_id)
        if not user or not user.license_id:
            return False
        
        license = self._license_repository.find_by_id(user.license_id)
        return license is not None and license.is_active
