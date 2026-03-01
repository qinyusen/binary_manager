from typing import Protocol, Optional
from ..value_objects import ResourceType, ContentType


class IAuthorizationService(Protocol):
    """授权服务接口，用于验证用户权限"""
    
    def can_download_release(
        self,
        user_id: str,
        resource_type: ResourceType
    ) -> bool:
        """验证用户是否可以下载指定类型的资源
        
        Args:
            user_id: 用户ID
            resource_type: 资源类型
            
        Returns:
            是否有权限
        """
        ...
    
    def can_download_content(
        self,
        user_id: str,
        resource_type: ResourceType,
        content_type: ContentType
    ) -> bool:
        """验证用户是否可以下载指定内容类型
        
        Args:
            user_id: 用户ID
            resource_type: 资源类型
            content_type: 内容类型
            
        Returns:
            是否有权限
        """
        ...
    
    def can_publish(self, user_id: str, resource_type: ResourceType) -> bool:
        """验证用户是否可以发布指定类型的资源
        
        Args:
            user_id: 用户ID
            resource_type: 资源类型
            
        Returns:
            是否有权限
        """
        ...
    
    def get_user_license_info(self, user_id: str) -> Optional[dict]:
        """获取用户的许可证信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            许可证信息字典，如果用户没有许可证则返回 None
        """
        ...
    
    def validate_user_license(self, user_id: str) -> bool:
        """验证用户的许可证是否有效
        
        Args:
            user_id: 用户ID
            
        Returns:
            许可证是否有效
        """
        ...
