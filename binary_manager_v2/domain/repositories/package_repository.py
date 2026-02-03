from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from ..entities import Package
from ..value_objects import PackageName


class PackageRepository(ABC):
    
    @abstractmethod
    def save(self, package: Package, git_info: Dict) -> Optional[int]:
        pass
    
    @abstractmethod
    def find_by_name_and_version(
        self,
        package_name: PackageName,
        version: str
    ) -> Optional[Package]:
        pass
    
    @abstractmethod
    def find_by_name(self, package_name: PackageName) -> List[Package]:
        pass
    
    @abstractmethod
    def find_by_git_commit(self, commit_hash: str) -> List[Package]:
        pass
    
    @abstractmethod
    def find_by_publisher(self, publisher_id: str) -> List[Package]:
        pass
    
    @abstractmethod
    def find_all(self) -> List[Package]:
        pass
    
    @abstractmethod
    def delete(self, package_id: int) -> bool:
        pass
    
    @abstractmethod
    def exists(self, package_name: PackageName, version: str, git_commit: str) -> bool:
        pass
