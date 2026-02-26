from pathlib import Path
from typing import Optional, Dict, List
from ..domain.services import FileScanner, HashCalculator, Packager
from ..domain.entities import Package, FileInfo
from ..domain.value_objects import PackageName, Hash, StorageLocation, StorageType, GitInfo
from ..infrastructure.git import GitService
from ..infrastructure.storage import LocalStorage, S3Storage
from ..infrastructure.database import SQLitePackageRepository
from ..shared.logger import Logger


class PublisherService:
    """发布服务 - 协调发布流程"""
    
    def __init__(
        self,
        package_repository: Optional[SQLitePackageRepository] = None,
        storage: Optional[LocalStorage] = None,
        db_path: Optional[str] = None,
        storage_path: Optional[str] = None
    ):
        self.package_repository = package_repository or SQLitePackageRepository(db_path)
        self.storage = storage or LocalStorage(storage_path or './releases')
        self.logger = Logger.get(self.__class__.__name__)
    
    def publish(
        self,
        source_dir: str,
        package_name: str,
        version: str,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        ignore_patterns: Optional[List[str]] = None,
        extract_git: bool = True
    ) -> Dict:
        """发布包"""
        source_path = Path(source_dir).resolve()
        if not source_path.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")
        
        self.logger.info(f"Publishing {package_name} v{version}")
        self.logger.info(f"Source: {source_dir}")
        
        git_info = None
        if extract_git:
            git_service = GitService(str(source_path))
            if git_service.is_git_repo():
                git_info = git_service.get_git_info()
                self.logger.info(f"Git commit: {git_info.commit_short if git_info else 'N/A'}")
        
        file_scanner = FileScanner(ignore_patterns)
        files, scan_info = file_scanner.scan_directory(str(source_path))
        self.logger.info(f"Scanned {len(files)} files")
        
        hash_calculator = HashCalculator()
        packager = Packager(str(self.storage.base_path))
        
        archive_name = f"{package_name}_v{version}.zip"
        result = packager.create_zip(str(source_path), files, package_name, version)
        archive_path = result['archive_path']
        
        archive_hash = hash_calculator.calculate_file(str(archive_path))
        archive_size = result['size']
        
        package = Package(
            package_name=PackageName(package_name),
            version=version,
            archive_hash=archive_hash,
            archive_size=archive_size,
            file_count=len(files),
            git_info=git_info,
            storage_location=StorageLocation(StorageType.LOCAL, archive_name),
            description=description,
            metadata=metadata or {}
        )
        
        for file_info in files:
            package.add_file(file_info)
        
        package_id = self.package_repository.save(package)
        self.logger.info(f"Package saved to database with ID: {package_id}")
        
        config_path = self._save_config(package, self.storage.base_path)
        self.logger.info(f"Config saved: {config_path}")
        
        return {
            'package_id': package_id,
            'package': package,
            'archive_path': str(archive_path),
            'config_path': config_path
        }
    
    def publish_to_s3(
        self,
        source_dir: str,
        package_name: str,
        version: str,
        s3_storage: S3Storage,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        ignore_patterns: Optional[List[str]] = None,
        extract_git: bool = True
    ) -> Dict:
        """发布包到S3"""
        source_path = Path(source_dir).resolve()
        if not source_path.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")
        
        self.logger.info(f"Publishing {package_name} v{version} to S3")
        
        git_info = None
        if extract_git:
            git_service = GitService(str(source_path))
            if git_service.is_git_repo():
                git_info = git_service.get_git_info()
        
        file_scanner = FileScanner(ignore_patterns)
        files, scan_info = file_scanner.scan_directory(str(source_path))
        
        hash_calculator = HashCalculator()
        
        temp_dir = Path('/tmp')
        packager = Packager(str(temp_dir))
        
        archive_name = f"{package_name}_v{version}.zip"
        result = packager.create_zip(str(source_path), files, package_name, version)
        temp_archive_path = result['archive_path']
        
        archive_hash = hash_calculator.calculate_file(str(temp_archive_path))
        archive_size = result['size']
        
        s3_key = f"packages/{package_name}/{version}/{archive_name}"
        s3_storage.upload_file(str(temp_archive_path), s3_key)
        
        package = Package(
            package_name=PackageName(package_name),
            version=version,
            archive_hash=archive_hash,
            archive_size=archive_size,
            file_count=len(files),
            git_info=git_info,
            storage_location=StorageLocation(StorageType.S3, s3_key),
            description=description,
            metadata=metadata or {}
        )
        
        for file_info in files:
            package.add_file(file_info)
        
        package_id = self.package_repository.save(package)
        self.logger.info(f"Package saved to database with ID: {package_id}")
        
        temp_archive_path.unlink()
        
        return {
            'package_id': package_id,
            'package': package,
            's3_key': s3_key
        }
    
    def _save_config(self, package: Package, output_dir: Path) -> str:
        """保存配置文件"""
        import json
        
        config_path = output_dir / f"{package.package_name}_v{package.version}.json"
        
        config_data = {
            'package_name': str(package.package_name),
            'version': package.version,
            'created_at': package.created_at.isoformat(),
            'file_info': {
                'archive_name': f"{package.package_name}_v{package.version}.zip",
                'size': package.archive_size,
                'file_count': package.file_count,
                'hash': str(package.archive_hash)
            },
            'files': [f.to_dict() for f in package.files],
            'git_info': package.git_info.to_dict() if package.git_info else None,
            'storage': package.storage_location.to_dict() if package.storage_location else None,
            'description': package.description,
            'metadata': package.metadata
        }
        
        with open(config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        return str(config_path)
