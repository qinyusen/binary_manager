from typing import Optional, List, Dict
from datetime import datetime
from ..value_objects import PackageName


class Group:
    def __init__(
        self,
        group_name: PackageName,
        version: str,
        created_by: str,
        description: Optional[str] = None,
        environment_config: Optional[Dict] = None,
        metadata: Optional[Dict] = None
    ):
        self._group_name = group_name
        self._version = version
        self._created_by = created_by
        self._description = description
        self._environment_config = environment_config or {}
        self._metadata = metadata or {}
        self._created_at = datetime.utcnow()
        self._packages: List[GroupPackage] = []
    
    @property
    def group_name(self) -> PackageName:
        return self._group_name
    
    @property
    def version(self) -> str:
        return self._version
    
    @property
    def created_by(self) -> str:
        return self._created_by
    
    @property
    def description(self) -> Optional[str]:
        return self._description
    
    @property
    def environment_config(self) -> Dict:
        return self._environment_config.copy()
    
    @property
    def metadata(self) -> Dict:
        return self._metadata.copy()
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def packages(self) -> List['GroupPackage']:
        return self._packages.copy()
    
    def add_package(
        self,
        package_name: str,
        package_version: str,
        install_order: int = 0,
        required: bool = True
    ) -> None:
        group_pkg = GroupPackage(
            package_name=package_name,
            package_version=package_version,
            install_order=install_order,
            required=required
        )
        self._packages.append(group_pkg)
    
    def to_dict(self) -> Dict:
        return {
            'group_name': str(self._group_name),
            'version': self._version,
            'created_by': self._created_by,
            'description': self._description,
            'environment_config': self._environment_config,
            'metadata': self._metadata,
            'created_at': self._created_at.isoformat(),
            'packages': [p.to_dict() for p in self._packages]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Group':
        group = cls(
            group_name=PackageName(data['group_name']),
            version=data['version'],
            created_by=data['created_by'],
            description=data.get('description'),
            environment_config=data.get('environment_config'),
            metadata=data.get('metadata')
        )
        
        if 'created_at' in data:
            group._created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        
        for pkg_data in data.get('packages', []):
            group._packages.append(GroupPackage.from_dict(pkg_data))
        
        return group
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Group):
            return False
        return (self._group_name == other._group_name and
                self._version == other._version)
    
    def __hash__(self) -> int:
        return hash((str(self._group_name), self._version))
    
    def __repr__(self) -> str:
        return f"Group(name='{self._group_name}', version='{self._version}')"


class GroupPackage:
    def __init__(
        self,
        package_name: str,
        package_version: str,
        install_order: int = 0,
        required: bool = True,
        package_id: Optional[int] = None
    ):
        self._package_name = package_name
        self._package_version = package_version
        self._install_order = install_order
        self._required = required
        self._package_id = package_id
    
    @property
    def package_name(self) -> str:
        return self._package_name
    
    @property
    def package_version(self) -> str:
        return self._package_version
    
    @property
    def install_order(self) -> int:
        return self._install_order
    
    @property
    def required(self) -> bool:
        return self._required
    
    @property
    def package_id(self) -> Optional[int]:
        return self._package_id
    
    @package_id.setter
    def package_id(self, value: int) -> None:
        self._package_id = value
    
    def to_dict(self) -> Dict:
        return {
            'package_name': self._package_name,
            'package_version': self._package_version,
            'install_order': self._install_order,
            'required': self._required,
            'package_id': self._package_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GroupPackage':
        return cls(
            package_name=data['package_name'],
            package_version=data['package_version'],
            install_order=data.get('install_order', 0),
            required=data.get('required', True),
            package_id=data.get('package_id')
        )
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, GroupPackage):
            return False
        return (self._package_name == other._package_name and
                self._package_version == other._package_version)
    
    def __hash__(self) -> int:
        return hash((self._package_name, self._package_version))
    
    def __repr__(self) -> str:
        return f"GroupPackage(name='{self._package_name}', version='{self._package_version}')"
