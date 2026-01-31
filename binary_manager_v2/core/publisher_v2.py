import os
import sys
import json
from pathlib import Path
from typing import Dict, Optional
import logging

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from binary_manager_v2.core.git_integration import GitIntegration, extract_git_info
from binary_manager_v2.core.database_manager import DatabaseManager
from binary_manager_v2.core.sync_manager import SyncManager

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'binary_manager' / 'publisher'))
from scanner import FileScanner
from packager import Packager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PublisherV2:
    """升级版发布器，支持Git集成和数据库"""
    
    def __init__(self, db_path: str = None, s3_config: Dict = None):
        self.db_manager = DatabaseManager(db_path)
        self.sync_manager = None
        
        if s3_config and s3_config.get('enabled', False):
            self.sync_manager = SyncManager(
                bucket_name=s3_config['bucket'],
                access_key=s3_config.get('access_key'),
                secret_key=s3_config.get('secret_key'),
                region=s3_config.get('region', 'us-east-1')
            )
            logger.info("S3 sync enabled")
    
    def publish(self, source_dir: str, output_dir: str, package_name: str,
                version: str, upload_to_s3: bool = False, 
                description: str = None, metadata: Dict = None) -> Dict:
        """发布包"""
        source_path = Path(source_dir)
        if not source_path.exists():
            raise ValueError(f"Source directory does not exist: {source_dir}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Publishing {package_name} v{version}")
        logger.info(f"Source: {source_dir}")
        logger.info(f"Output: {output_dir}")
        
        git_info = self._extract_git_info(source_dir)
        logger.info(f"Git commit: {git_info.get('commit_short', 'N/A')}")
        
        file_list, scan_info = self._scan_files(source_dir)
        logger.info(f"Scanned {scan_info['total_files']} files ({scan_info['total_size']} bytes)")
        
        zip_info = self._create_package(source_dir, file_list, package_name, 
                                      version, output_dir)
        logger.info(f"Created package: {zip_info['archive_name']} ({zip_info['size']} bytes)")
        
        package_info = self._build_package_info(
            package_name, version, git_info, zip_info, file_list,
            description, metadata
        )
        
        package_id = self.db_manager.save_package(package_info, git_info)
        logger.info(f"Package saved to database with ID: {package_id}")
        
        config_path = self._save_config(package_info, output_dir)
        logger.info(f"Config saved: {config_path}")
        
        if upload_to_s3 and self.sync_manager:
            self._upload_to_s3(package_info, zip_info, config_path)
        
        return {
            'package_id': package_id,
            'package_info': package_info,
            'zip_info': zip_info,
            'config_path': config_path
        }
    
    def _extract_git_info(self, repo_path: str) -> Dict:
        """提取Git信息"""
        try:
            git = GitIntegration(repo_path)
            return git.get_git_info()
        except Exception as e:
            logger.warning(f"Failed to extract Git info: {e}")
            return {}
    
    def _scan_files(self, source_dir: str) -> tuple:
        """扫描文件"""
        scanner = FileScanner()
        file_list, scan_info = scanner.scan_directory(source_dir)
        return file_list, scan_info
    
    def _create_package(self, source_dir: str, file_list: list, 
                        package_name: str, version: str, output_dir: str) -> Dict:
        """创建zip包"""
        packager = Packager(output_dir)
        return packager.create_zip(source_dir, file_list, package_name, version)
    
    def _build_package_info(self, package_name: str, version: str, 
                          git_info: Dict, zip_info: Dict, file_list: list,
                          description: str = None, metadata: Dict = None) -> Dict:
        """构建包信息"""
        from datetime import datetime
        
        package_info = {
            'package_name': package_name,
            'version': version,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'publisher': {
                'publisher_id': self.db_manager.publisher_id,
                'hostname': __import__('socket').gethostname()
            },
            'git_info': git_info,
            'file_info': {
                'archive_name': zip_info['archive_name'],
                'size': zip_info['size'],
                'file_count': zip_info['file_count'],
                'hash': zip_info['hash']
            },
            'files': file_list,
            'storage': {
                'type': 's3' if self.sync_manager else 'local',
                'path': str(zip_info['archive_path'])
            }
        }
        
        if description:
            package_info['description'] = description
        
        if metadata:
            package_info['metadata'] = metadata
        
        if self.sync_manager:
            package_info['storage']['s3_bucket'] = self.sync_manager.bucket_name
            package_info['storage']['s3_key'] = f"packages/{package_name}/{version}/{zip_info['archive_name']}"
        
        return package_info
    
    def _save_config(self, package_info: Dict, output_dir: str) -> str:
        """保存配置文件"""
        package_name = package_info['package_name']
        version = package_info['version']
        config_name = f"{package_name}_v{version}.json"
        config_path = Path(output_dir) / config_name
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(package_info, f, indent=2, ensure_ascii=False)
        
        return str(config_path)
    
    def _upload_to_s3(self, package_info: Dict, zip_info: Dict, 
                      config_path: str) -> None:
        """上传到S3"""
        logger.info("Uploading to S3...")
        
        success = self.sync_manager.upload_package(
            package_info,
            zip_info['archive_path']
        )
        
        if success:
            logger.info("Package uploaded to S3 successfully")
        else:
            logger.error("Failed to upload package to S3")
        
        config_s3_key = f"packages/{package_info['package_name']}/{package_info['version']}/config.json"
        self.sync_manager.upload_file(config_path, config_s3_key)
    
    def get_publisher_info(self) -> Dict:
        """获取发布者信息"""
        return {
            'publisher_id': self.db_manager.publisher_id,
            'hostname': __import__('socket').gethostname(),
            'database_path': str(self.db_manager.db_path)
        }
    
    def list_packages(self, package_name: str = None) -> list:
        """列出发布的包"""
        filters = {}
        if package_name:
            filters['package_name'] = package_name
        
        return self.db_manager.query_packages(filters)
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()


def publish_package(source_dir: str, output_dir: str, package_name: str,
                  version: str, upload: bool = False, s3_config: Dict = None) -> Dict:
    """发布包的便捷函数"""
    publisher = PublisherV2(s3_config=s3_config)
    
    try:
        result = publisher.publish(
            source_dir, output_dir, package_name, version,
            upload_to_s3=upload
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Publish failed: {e}")
        raise
    finally:
        publisher.close()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        source = sys.argv[1]
        version = sys.argv[2] if len(sys.argv) > 2 else '1.0.0'
        name = sys.argv[3] if len(sys.argv) > 3 else Path(source).name
        
        result = publish_package(
            source_dir=source,
            output_dir='./releases_v2',
            package_name=name,
            version=version,
            upload=False
        )
        
        print(f"\nPackage published successfully!")
        print(f"Package ID: {result['package_id']}")
        print(f"Config: {result['config_path']}")
    else:
        print("Usage: python publisher_v2.py <source_dir> [version] [package_name]")
