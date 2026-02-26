from pathlib import Path
from typing import Optional, Dict, List
from ..domain.entities import Group, GroupPackage
from ..infrastructure.database import SQLiteGroupRepository, SQLitePackageRepository
from ..shared.logger import Logger


class GroupService:
    """分组服务 - 管理包的组合和依赖"""
    
    def __init__(
        self,
        group_repository: Optional[SQLiteGroupRepository] = None,
        package_repository: Optional[SQLitePackageRepository] = None,
        db_path: Optional[str] = None
    ):
        self.group_repository = group_repository or SQLiteGroupRepository(db_path)
        self.package_repository = package_repository or SQLitePackageRepository(db_path)
        self.logger = Logger.get(self.__class__.__name__)
    
    def create_group(
        self,
        group_name: str,
        version: str,
        packages: List[Dict],
        description: Optional[str] = None,
        environment_config: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        created_by: Optional[str] = None
    ) -> Dict:
        """创建分组"""
        group_packages = []
        
        for pkg_spec in packages:
            package = self._find_package(pkg_spec)
            if package is None:
                raise ValueError(
                    f"Package not found: {pkg_spec['package_name']} v{pkg_spec['version']}"
                )
            
            group_packages.append(
                GroupPackage(
                    package_id=package_id_from_package(package),
                    install_order=pkg_spec.get('install_order', 0),
                    required=pkg_spec.get('required', True)
                )
            )
        
        group = Group(
            group_name=group_name,
            version=version,
            packages=group_packages,
            description=description,
            environment_config=environment_config or {},
            metadata=metadata or {}
        )
        
        publisher_id = created_by or self.package_repository.publisher_id
        group_id = self.group_repository.save(group, publisher_id)
        
        if group_id is None:
            raise ValueError(f"Failed to create group: {group_name} v{version}")
        
        self.logger.info(f"Group created with ID: {group_id}")
        
        return {
            'group_id': group_id,
            'group': group,
            'packages': group_packages
        }
    
    def add_package_to_group(
        self,
        group_id: int,
        package_name: str,
        version: str,
        install_order: int = 0,
        required: bool = True
    ) -> bool:
        """添加包到分组"""
        package = self.package_repository.find_by_name_and_version(package_name, version)
        if package is None:
            self.logger.error(f"Package not found: {package_name} v{version}")
            return False
        
        return self.group_repository.add_package(
            group_id,
            package_id_from_package(package),
            install_order,
            required
        )
    
    def remove_package_from_group(self, group_id: int, package_id: int) -> bool:
        """从分组移除包"""
        return self.group_repository.remove_package(group_id, package_id)
    
    def get_group(self, group_id: int) -> Optional[Group]:
        """获取分组"""
        return self.group_repository.find_by_id(group_id)
    
    def list_groups(self, filters: Optional[Dict] = None) -> List[Group]:
        """列出分组"""
        return self.group_repository.find_all(filters)
    
    def export_group(self, group_id: int, output_dir: str) -> Optional[str]:
        """导出分组为JSON"""
        import json
        
        group = self.group_repository.find_by_id(group_id)
        if group is None:
            self.logger.error(f"Group not found: {group_id}")
            return None
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        export_file = output_path / f"{group.group_name}_v{group.version}.json"
        
        export_data = {
            'group_name': group.group_name,
            'version': group.version,
            'description': group.description,
            'environment_config': group.environment_config,
            'metadata': group.metadata,
            'packages': []
        }
        
        for pkg in group.packages:
            package = self.package_repository.find_by_id(pkg.package_id)
            if package:
                export_data['packages'].append({
                    'package_name': str(package.package_name),
                    'version': package.version,
                    'install_order': pkg.install_order,
                    'required': pkg.required,
                    'git_commit': package.git_info.commit_short if package.git_info else None
                })
        
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Group exported to: {export_file}")
        return str(export_file)
    
    def import_group(self, group_json_path: str) -> Optional[int]:
        """从JSON导入分组"""
        import json
        
        json_path = Path(group_json_path)
        if not json_path.exists():
            self.logger.error(f"File not found: {group_json_path}")
            return None
        
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        packages = []
        for pkg_data in data.get('packages', []):
            package = self.package_repository.find_by_name_and_version(
                pkg_data['package_name'],
                pkg_data['version']
            )
            if package is None:
                self.logger.warning(
                    f"Package not found: {pkg_data['package_name']} v{pkg_data['version']}"
                )
                continue
            
            packages.append({
                'package_id': package_id_from_package(package),
                'install_order': pkg_data.get('install_order', 0),
                'required': pkg_data.get('required', True)
            })
        
        group_packages = [
            GroupPackage(
                package_id=p['package_id'],
                install_order=p['install_order'],
                required=p['required']
            )
            for p in packages
        ]
        
        group = Group(
            group_name=data['group_name'],
            version=data['version'],
            packages=group_packages,
            description=data.get('description'),
            environment_config=data.get('environment_config', {}),
            metadata=data.get('metadata', {})
        )
        
        group_id = self.group_repository.save(group, self.package_repository.publisher_id)
        self.logger.info(f"Group imported with ID: {group_id}")
        
        return group_id
    
    def delete_group(self, group_id: int) -> bool:
        """删除分组"""
        return self.group_repository.delete(group_id)
    
    def _find_package(self, pkg_spec: Dict) -> Optional:
        """查找包"""
        return self.package_repository.find_by_name_and_version(
            pkg_spec['package_name'],
            pkg_spec['version']
        )


def package_id_from_package(package) -> int:
    """从Package对象获取ID的辅助函数"""
    if hasattr(package, 'id'):
        return package.id
    if hasattr(package, '_id'):
        return package._id
    raise ValueError(f"Cannot extract ID from package: {package}")
