import json
from pathlib import Path
from typing import Dict, List, Optional
import logging
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from binary_manager_v2.core.database_manager import DatabaseManager

try:
    from binary_manager_v2.core.sync_manager import SyncManager
    SYNC_MANAGER_AVAILABLE = True
except ImportError:
    SYNC_MANAGER_AVAILABLE = False
    SyncManager = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GroupManager:
    """Group管理器，处理包的组合和管理"""
    
    def __init__(self, db_path: Optional[str] = None, s3_config: Optional[Dict] = None):
        self.db_manager = DatabaseManager(db_path)
        self.sync_manager = None
        
        if s3_config and s3_config.get('enabled', False) and SYNC_MANAGER_AVAILABLE:
            self.sync_manager = SyncManager(
                bucket_name=s3_config['bucket'],
                access_key=s3_config.get('access_key'),
                secret_key=s3_config.get('secret_key'),
                region=s3_config.get('region', 'us-east-1')
            )
            logger.info("S3 sync enabled for Group Manager")
    
    def create_group(self, group_name: str, version: str, 
                    packages: List[Dict], description: str = None,
                    environment_config: Dict = None, metadata: Dict = None) -> Dict:
        """创建Group"""
        from datetime import datetime
        import socket
        
        group_info = {
            'group_name': group_name,
            'version': version,
            'created_by': self.db_manager.publisher_id,
            'description': description,
            'environment_config': environment_config,
            'metadata': metadata
        }
        
        group_id = self.db_manager.create_group(group_info)
        
        if group_id is None:
            raise ValueError(f"Failed to create group: {group_name} v{version}")
        
        logger.info(f"Group created with ID: {group_id}")
        
        added_packages = []
        for pkg in packages:
            package_id = self._find_or_create_package(pkg)
            
            self.db_manager.add_package_to_group(
                group_id=group_id,
                package_id=package_id,
                install_order=pkg.get('install_order', 0),
                required=pkg.get('required', True)
            )
            
            added_packages.append({
                'package_id': package_id,
                'package_name': pkg.get('package_name'),
                'version': pkg.get('version')
            })
            
            logger.info(f"Added package {pkg.get('package_name')} v{pkg.get('version')} to group")
        
        return {
            'group_id': group_id,
            'group_info': group_info,
            'packages': added_packages
        }
    
    def _find_or_create_package(self, pkg_spec: Dict) -> int:
        """查找或创建包"""
        package = self.db_manager.get_package_by_name_version(
            pkg_spec['package_name'],
            pkg_spec['version']
        )
        
        if package:
            return package['id']
        
        logger.warning(f"Package not found: {pkg_spec['package_name']} v{pkg_spec['version']}")
        raise ValueError(f"Package not found: {pkg_spec['package_name']} v{pkg_spec['version']}")
    
    def add_dependency(self, group_id: int, package_name: str, 
                     depends_on: str, constraint_type: str = 'exact',
                     version_constraint: str = None) -> None:
        """添加依赖关系"""
        group = self.db_manager.query_groups({'id': group_id})[0]
        
        package = self._find_package_in_group(group_id, package_name)
        depends_on_package = self._find_package_in_group(group_id, depends_on)
        
        if not package or not depends_on_package:
            raise ValueError("One or more packages not found in group")
        
        self.db_manager.add_dependency(
            group_id=group_id,
            package_id=package['id'],
            depends_on_package_id=depends_on_package['id'],
            constraint_type=constraint_type,
            version_constraint=version_constraint
        )
        
        logger.info(f"Added dependency: {package_name} -> {depends_on}")
    
    def _find_package_in_group(self, group_id: int, package_name: str) -> Optional[Dict]:
        """在Group中查找包"""
        packages = self.db_manager.get_group_packages(group_id)
        for pkg in packages:
            if pkg['package_name'] == package_name:
                return pkg
        return None
    
    def export_group(self, group_id: int, output_dir: str) -> str:
        """导出Group为JSON文件"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        group = self.db_manager.query_groups({'id': group_id})[0]
        packages = self.db_manager.get_group_packages(group_id)
        
        group_json = self._build_group_json(group, packages)
        
        filename = f"{group['group_name']}_v{group['version']}.json"
        file_path = output_path / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(group_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Group exported to: {file_path}")
        
        if self.sync_manager:
            self.sync_manager.upload_group_config(group_json, str(file_path))
        
        return str(file_path)
    
    def _build_group_json(self, group: Dict, packages: List[Dict]) -> Dict:
        """构建Group JSON"""
        return {
            'group_name': group['group_name'],
            'version': group['version'],
            'created_at': group['created_at'],
            'created_by': group['created_by'],
            'description': group['description'],
            'environment_config': json.loads(group['environment_config']) if group['environment_config'] else {},
            'packages': [
                {
                    'package_name': pkg['package_name'],
                    'version': pkg['version'],
                    'git_commit': pkg['git_commit_hash'],
                    'git_commit_short': pkg['git_commit_short'],
                    'install_order': pkg['install_order'],
                    'required': pkg['required'],
                    'archive_name': pkg['archive_name'],
                    'archive_size': pkg['archive_size'],
                    'archive_hash': pkg['archive_hash']
                }
                for pkg in packages
            ],
            'storage': {
                'type': 's3' if self.sync_manager else 'local',
                'bucket': self.sync_manager.bucket_name if self.sync_manager else None
            }
        }
    
    def import_group(self, group_json_path: str) -> int:
        """从JSON导入Group"""
        with open(group_json_path, 'r', encoding='utf-8') as f:
            group_json = json.load(f)
        
        return self.create_group(
            group_name=group_json['group_name'],
            version=group_json['version'],
            packages=group_json['packages'],
            description=group_json.get('description'),
            environment_config=group_json.get('environment_config'),
            metadata=group_json.get('metadata')
        )
    
    def list_groups(self, group_name: str = None) -> List[Dict]:
        """列出所有Groups"""
        filters = {}
        if group_name:
            filters['group_name'] = group_name
        
        return self.db_manager.query_groups(filters)
    
    def get_group_packages(self, group_id: int) -> List[Dict]:
        """获取Group中的所有包"""
        return self.db_manager.get_group_packages(group_id)
    
    def resolve_dependencies(self, group_id: int) -> List[Dict]:
        """解析依赖关系，返回按安装顺序排列的包列表"""
        packages = self.db_manager.get_group_packages(group_id)
        
        sorted_packages = sorted(packages, key=lambda x: x['install_order'])
        
        for pkg in sorted_packages:
            pkg['dependencies'] = []
        
        return sorted_packages
    
    def close(self):
        """关闭数据库连接"""
        self.db_manager.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def create_group(group_name: str, version: str, packages: List[Dict],
                db_path: str = None, s3_config: Dict = None) -> Dict:
    """创建Group的便捷函数"""
    manager = GroupManager(db_path, s3_config)
    
    try:
        result = manager.create_group(group_name, version, packages)
        return result
    except Exception as e:
        logger.error(f"Failed to create group: {e}")
        raise
    finally:
        manager.close()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'create':
            print("Group creation requires proper input")
            print("Use create_group() function programmatically")
        
        elif command == 'list':
            manager = GroupManager()
            groups = manager.list_groups()
            
            print(f"Found {len(groups)} groups:")
            for group in groups:
                print(f"  - {group['group_name']} v{group['version']} (ID: {group['id']})")
            
            manager.close()
        
        elif command == 'export':
            if len(sys.argv) > 2:
                group_id = int(sys.argv[2])
                output_dir = sys.argv[3] if len(sys.argv) > 3 else './groups'
                
                manager = GroupManager()
                manager.export_group(group_id, output_dir)
                manager.close()
    
    else:
        print("Usage: python group_manager.py <list|export> [args]")
