import json
import zipfile
from pathlib import Path
from typing import Optional, Dict, List
from ..domain.entities import Package
from ..domain.services import Packager
from ..infrastructure.storage import LocalStorage, S3Storage
from ..infrastructure.database import SQLitePackageRepository
from ..shared.logger import Logger
from ..shared.progress import ConsoleProgress


class DownloaderService:
    """下载服务 - 处理包的下载和安装"""
    
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
        self.progress = ConsoleProgress()
    
    def download_by_config(self, config_path: str, output_dir: str) -> Dict:
        """根据配置文件下载包"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise ValueError(f"Config file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        package_name = config['package_name']
        version = config['version']
        archive_name = config['file_info']['archive_name']
        expected_hash = config['file_info']['hash']
        download_url = config.get('download_url')
        
        self.logger.info(f"Downloading {package_name} v{version}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        archive_path = output_path / archive_name
        
        if download_url:
            self._download_from_url(download_url, archive_path)
        else:
            self._download_from_storage(archive_name, archive_path)
        
        if not self._verify_hash(archive_path, expected_hash):
            raise ValueError(f"Hash verification failed for {archive_path}")
        
        self._extract_package(archive_path, output_path)
        
        self.logger.info(f"Package downloaded to: {output_path}")
        
        return {
            'package_name': package_name,
            'version': version,
            'output_path': str(output_path),
            'archive_path': str(archive_path)
        }
    
    def download_by_id(self, package_id: int, output_dir: str) -> Dict:
        """根据数据库ID下载包"""
        package = self.package_repository.find_by_id(package_id)
        if package is None:
            raise ValueError(f"Package not found: {package_id}")
        
        return self._download_package(package, output_dir)
    
    def download_by_name_version(self, package_name: str, version: str, output_dir: str) -> Dict:
        """根据名称和版本下载包"""
        package = self.package_repository.find_by_name_and_version(package_name, version)
        if package is None:
            raise ValueError(f"Package not found: {package_name} v{version}")
        
        return self._download_package(package, output_dir)
    
    def download_group(self, group_id: int, output_dir: str) -> Dict:
        """下载分组中的所有包"""
        from ..infrastructure.database import SQLiteGroupRepository
        
        group_repo = SQLiteGroupRepository(self.package_repository.db_path)
        group = group_repo.find_by_id(group_id)
        
        if group is None:
            raise ValueError(f"Group not found: {group_id}")
        
        self.logger.info(f"Downloading group: {group.group_name} v{group.version}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        downloaded = []
        
        for pkg_ref in sorted(group.packages, key=lambda p: p.install_order):
            package = self.package_repository.find_by_id(pkg_ref.package_id)
            if package is None:
                if pkg_ref.required:
                    self.logger.error(f"Required package not found: {pkg_ref.package_id}")
                    raise ValueError(f"Required package not found: {pkg_ref.package_id}")
                else:
                    self.logger.warning(f"Optional package not found: {pkg_ref.package_id}")
                    continue
            
            pkg_output = output_path / str(package.package_name)
            result = self._download_package(package, str(pkg_output))
            downloaded.append(result)
        
        self.logger.info(f"Downloaded {len(downloaded)} packages")
        
        return {
            'group_name': group.group_name,
            'version': group.version,
            'packages': downloaded
        }
    
    def _download_package(self, package: Package, output_dir: str) -> Dict:
        """下载单个包"""
        self.logger.info(f"Downloading {package.package_name} v{package.version}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        archive_name = f"{package.package_name}_v{package.version}.zip"
        archive_path = output_path / archive_name
        
        if package.storage_location:
            if package.storage_location.storage_type.value == 's3':
                self._download_from_s3(package.storage_location.path, archive_path)
            else:
                self._download_from_storage(package.storage_location.path, archive_path)
        else:
            local_archive = self.storage.base_path / archive_name
            if local_archive.exists():
                import shutil
                shutil.copy2(local_archive, archive_path)
            else:
                raise ValueError(f"Package archive not found: {archive_name}")
        
        if not self._verify_hash(archive_path, str(package.archive_hash)):
            raise ValueError(f"Hash verification failed for {archive_path}")
        
        self._extract_package(archive_path, output_path)
        
        return {
            'package_name': str(package.package_name),
            'version': package.version,
            'output_path': str(output_path),
            'archive_path': str(archive_path)
        }
    
    def _download_from_url(self, url: str, output_path: Path) -> None:
        """从URL下载"""
        import requests
        
        self.logger.info(f"Downloading from URL: {url}")
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        self.progress.start(total_size, desc=f"Downloading {output_path.name}")
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    self.progress.update(len(chunk))
        
        self.progress.finish()
    
    def _download_from_s3(self, s3_key: str, output_path: Path) -> None:
        """从S3下载"""
        self.logger.info(f"Downloading from S3: {s3_key}")
        
        s3_storage = S3Storage(
            bucket_name='',
            access_key=None,
            secret_key=None
        )
        
        s3_storage.download_file(s3_key, str(output_path))
    
    def _download_from_storage(self, archive_name: str, output_path: Path) -> None:
        """从本地存储下载"""
        source = self.storage.base_path / archive_name
        if not source.exists():
            raise ValueError(f"Archive not found in storage: {archive_name}")
        
        import shutil
        shutil.copy2(source, output_path)
        self.logger.info(f"Copied from storage: {archive_name}")
    
    def _verify_hash(self, file_path: Path, expected_hash: str) -> bool:
        """验证文件哈希"""
        self.logger.info(f"Verifying hash for: {file_path}")
        
        actual_hash = self.storage.verify_file(str(file_path), expected_hash)
        
        if actual_hash:
            self.logger.info("Hash verification passed")
            return True
        else:
            self.logger.error("Hash verification failed")
            return False
    
    def _extract_package(self, archive_path: Path, output_dir: Path) -> None:
        """解压包"""
        self.logger.info(f"Extracting: {archive_path}")
        
        with zipfile.ZipFile(archive_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        self.logger.info(f"Extracted to: {output_dir}")
