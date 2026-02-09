"""
版本追踪模块
管理版本信息的生成和存储
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional


class VersionTracker:
    """版本追踪器"""
    
    def __init__(self, versions_dir: Path = None):
        """
        初始化版本追踪器
        
        Args:
            versions_dir: 版本JSON文件存储目录，默认为当前目录下的versions/
        """
        if versions_dir is None:
            versions_dir = Path.cwd() / 'versions'
        
        self.versions_dir = Path(versions_dir)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
    
    def create_version_data(
        self,
        version: str,
        binary_info: Optional[Dict] = None,
        git_info: Optional[Dict] = None,
        publisher_info: Optional[Dict] = None,
        release_notes: str = "",
        release_type: str = "both"
    ) -> Dict:
        """
        创建版本数据结构
        
        Args:
            version: 版本号（语义化版本）
            binary_info: 二进制文件信息
            git_info: Git信息
            publisher_info: 发布者信息
            release_notes: 发布说明
            release_type: 发布类型 (binary/commit/both)
        
        Returns:
            完整的版本数据字典
        """
        version_data = {
            "version": version,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "release_type": release_type,
            "release_notes": release_notes
        }
        
        if binary_info:
            version_data["binary"] = binary_info
        
        if git_info:
            version_data["git"] = git_info
        
        if publisher_info:
            version_data["publisher"] = publisher_info
        
        return version_data
    
    def save_version_file(self, version_data: Dict, filename: Optional[str] = None) -> Path:
        """
        保存版本JSON文件
        
        Args:
            version_data: 版本数据字典
            filename: 文件名，默认为 {version}.json
        
        Returns:
            保存的文件路径
        """
        if filename is None:
            filename = f"{version_data['version']}.json"
        
        version_file = self.versions_dir / filename
        
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2, ensure_ascii=False)
        
        return version_file
    
    def load_version_file(self, version: str) -> Optional[Dict]:
        """
        加载版本JSON文件
        
        Args:
            version: 版本号
        
        Returns:
            版本数据字典，如果文件不存在返回None
        """
        version_file = self.versions_dir / f"{version}.json"
        
        if not version_file.exists():
            return None
        
        with open(version_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_versions(self) -> list:
        """列出所有版本"""
        versions = []
        
        for version_file in sorted(self.versions_dir.glob('*.json')):
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
                versions.append({
                    'version': version_data.get('version'),
                    'created_at': version_data.get('created_at'),
                    'release_type': version_data.get('release_type'),
                    'file': str(version_file)
                })
        
        return versions
    
    def get_latest_version(self) -> Optional[Dict]:
        """获取最新的版本信息"""
        versions = self.list_versions()
        if not versions:
            return None
        
        latest = versions[-1]
        return self.load_version_file(latest['version'])
    
    def version_exists(self, version: str) -> bool:
        """检查版本是否已存在"""
        version_file = self.versions_dir / f"{version}.json"
        return version_file.exists()
