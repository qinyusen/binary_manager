from typing import Dict
from ..domain.services import IStorageService
from binary_manager_v2.application import PublisherService, DownloaderService
from binary_manager_v2.domain.entities import Package
from binary_manager_v2.infrastructure.database import SQLitePackageRepository


class StorageServiceAdapter:
    """存储服务适配器，将 Binary Manager V2 的服务适配到 IStorageService 接口"""
    
    def __init__(
        self,
        publisher_service: PublisherService,
        downloader_service: DownloaderService,
        package_repository
    ):
        self._publisher_service = publisher_service
        self._downloader_service = downloader_service
        self._package_repository = package_repository
    
    def publish_package(
        self,
        source_dir: str,
        package_name: str,
        version: str,
        extract_git: bool = True
    ) -> dict:
        """发布包到存储系统"""
        result = self._publisher_service.publish(
            source_dir=source_dir,
            package_name=package_name,
            version=version,
            extract_git=extract_git
        )
        return {'package_id': str(result['package_id'])}
    
    def download_package(self, package_id: str, output_dir: str) -> None:
        """从存储系统下载包"""
        self._downloader_service.download_by_id(int(package_id), output_dir)
    
    def get_package_info(self, package_id: str) -> dict:
        """获取包信息"""
        package = self._package_repository.find_by_id(int(package_id))
        if not package:
            raise ValueError(f"Package '{package_id}' not found")
        
        return {
            'package_id': package_id,
            'package_name': str(package.package_name),
            'version': package.version,
            'size': package.archive_size,
            'created_at': package.created_at.isoformat()
        }
