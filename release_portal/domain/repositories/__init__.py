from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.user import User
from ..entities.role import Role
from ..entities.license import License
from ..entities.release import Release
from ..value_objects import ResourceType, ReleaseStatus


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[User]:
        pass
    
    @abstractmethod
    def delete(self, user_id: str) -> None:
        pass
    
    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        pass
    
    @abstractmethod
    def exists_by_email(self, email: str) -> bool:
        pass


class RoleRepository(ABC):
    @abstractmethod
    def save(self, role: Role) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, role_id: str) -> Optional[Role]:
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Role]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Role]:
        pass
    
    @abstractmethod
    def delete(self, role_id: str) -> None:
        pass


class LicenseRepository(ABC):
    @abstractmethod
    def save(self, license_obj: License) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, license_id: str) -> Optional[License]:
        pass
    
    @abstractmethod
    def find_by_organization(self, organization: str) -> List[License]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[License]:
        pass
    
    @abstractmethod
    def find_active(self) -> List[License]:
        pass
    
    @abstractmethod
    def delete(self, license_id: str) -> None:
        pass
    
    @abstractmethod
    def exists_by_id(self, license_id: str) -> bool:
        pass


class ReleaseRepository(ABC):
    @abstractmethod
    def save(self, release: Release) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, release_id: str) -> Optional[Release]:
        pass
    
    @abstractmethod
    def find_by_resource_type(self, resource_type: ResourceType) -> List[Release]:
        pass
    
    @abstractmethod
    def find_by_version(self, resource_type: ResourceType, version: str) -> Optional[Release]:
        pass
    
    @abstractmethod
    def find_by_status(self, status: ReleaseStatus) -> List[Release]:
        pass
    
    @abstractmethod
    def find_by_publisher(self, publisher_id: str) -> List[Release]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Release]:
        pass
    
    @abstractmethod
    def delete(self, release_id: str) -> None:
        pass
    
    @abstractmethod
    def exists_by_id(self, release_id: str) -> bool:
        pass
