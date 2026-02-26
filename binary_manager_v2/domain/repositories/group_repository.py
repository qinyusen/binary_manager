from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from ..entities import Group
from ..value_objects import PackageName


class GroupRepository(ABC):
    
    @abstractmethod
    def save(self, group: Group, created_by: str) -> Optional[int]:
        pass
    
    @abstractmethod
    def find_by_id(self, group_id: int) -> Optional[Group]:
        pass
    
    @abstractmethod
    def find_by_name_and_version(
        self,
        group_name: str,
        version: str
    ) -> Optional[Group]:
        pass
    
    @abstractmethod
    def find_by_name(self, group_name: str) -> List[Group]:
        pass
    
    @abstractmethod
    def find_by_creator(self, publisher_id: str) -> List[Group]:
        pass
    
    @abstractmethod
    def find_all(self, filters: Optional[Dict] = None) -> List[Group]:
        pass
    
    @abstractmethod
    def add_package(
        self,
        group_id: int,
        package_id: int,
        install_order: int = 0,
        required: bool = True
    ) -> bool:
        pass
    
    @abstractmethod
    def remove_package(self, group_id: int, package_id: int) -> bool:
        pass
    
    @abstractmethod
    def delete(self, group_id: int) -> bool:
        pass
    
    @abstractmethod
    def exists(self, group_name: str, version: str) -> bool:
        pass
