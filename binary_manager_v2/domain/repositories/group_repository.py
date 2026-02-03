from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from ..entities import Group
from ..value_objects import PackageName


class GroupRepository(ABC):
    
    @abstractmethod
    def save(self, group: Group) -> Optional[int]:
        pass
    
    @abstractmethod
    def find_by_name_and_version(
        self,
        group_name: PackageName,
        version: str
    ) -> Optional[Group]:
        pass
    
    @abstractmethod
    def find_by_name(self, group_name: PackageName) -> List[Group]:
        pass
    
    @abstractmethod
    def find_by_creator(self, publisher_id: str) -> List[Group]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Group]:
        pass
    
    @abstractmethod
    def add_package_to_group(
        self,
        group_id: int,
        package_id: int,
        install_order: int = 0,
        required: bool = True
    ) -> None:
        pass
    
    @abstractmethod
    def get_group_packages(self, group_id: int) -> List[Dict]:
        pass
    
    @abstractmethod
    def delete(self, group_id: int) -> bool:
        pass
    
    @abstractmethod
    def exists(self, group_name: PackageName, version: str) -> bool:
        pass
