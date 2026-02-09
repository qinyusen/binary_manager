"""
发布管理器
协调编译、打包和版本追踪的整个发布流程
"""

from pathlib import Path
from typing import Optional, Dict
import logging

from .compilers.c_compiler import CCompiler
from .compilers.generic_compiler import GenericCompiler
from .version_tracker import VersionTracker
from .utils import get_publisher_info, detect_build_system

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'binary_manager_v2' / 'core'))
from git_integration import GitIntegration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReleaseManager:
    """发布管理器"""
    
    def __init__(
        self,
        project_dir: Path,
        versions_dir: Optional[Path] = None,
        build_system: Optional[str] = None
    ):
        """
        初始化发布管理器
        
        Args:
            project_dir: 项目根目录
            versions_dir: 版本JSON文件存储目录
            build_system: 构建系统类型（自动检测）
        """
        self.project_dir = Path(project_dir)
        self.versions_dir = versions_dir or self.project_dir / 'versions'
        self.version_tracker = VersionTracker(self.versions_dir)
        self.build_system = build_system or detect_build_system(self.project_dir)
        
        logger.info(f"项目目录: {self.project_dir}")
        logger.info(f"版本目录: {self.versions_dir}")
        logger.info(f"构建系统: {self.build_system}")
    
    def get_compiler(self):
        """获取合适的编译器实例"""
        if self.build_system in ['cmake', 'make']:
            return CCompiler(self.project_dir, build_system=self.build_system)
        else:
            return GenericCompiler(self.project_dir)
    
    def release_binary(
        self,
        version: str,
        binary_name: Optional[str] = None,
        release_notes: str = "",
        clean_build: bool = False
    ) -> Dict:
        """
        发布二进制
        
        Args:
            version: 版本号
            binary_name: 二进制文件名（可选）
            release_notes: 发布说明
            clean_build: 是否清理后重新构建
        
        Returns:
            发布结果字典
        """
        logger.info(f"开始发布二进制版本: {version}")
        
        compiler = self.get_compiler()
        
        if clean_build:
            logger.info("清理构建目录...")
            compiler.clean()
        
        logger.info("开始编译...")
        compile_result = compiler.compile()
        
        if compile_result['status'] != 'success':
            return {
                'status': 'error',
                'message': f"编译失败: {compile_result['message']}"
            }
        
        binary_info = compiler.get_binary_info(binary_name)
        
        if not binary_info:
            return {
                'status': 'error',
                'message': '未找到编译后的二进制文件'
            }
        
        publisher_info = get_publisher_info()
        
        version_data = self.version_tracker.create_version_data(
            version=version,
            binary_info=binary_info,
            publisher_info=publisher_info,
            release_notes=release_notes,
            release_type="binary"
        )
        
        version_file = self.version_tracker.save_version_file(version_data)
        
        return {
            'status': 'success',
            'message': '二进制发布成功',
            'version': version,
            'binary_info': binary_info,
            'version_file': str(version_file)
        }
    
    def release_commit(
        self,
        version: str,
        release_notes: str = ""
    ) -> Dict:
        """
        发布commit（仅记录Git元数据）
        
        Args:
            version: 版本号
            release_notes: 发布说明
        
        Returns:
            发布结果字典
        """
        logger.info(f"开始记录commit版本: {version}")
        
        try:
            git = GitIntegration(str(self.project_dir))
            git_info = git.get_git_info()
            
            publisher_info = get_publisher_info()
            
            version_data = self.version_tracker.create_version_data(
                version=version,
                git_info=git_info,
                publisher_info=publisher_info,
                release_notes=release_notes,
                release_type="commit"
            )
            
            version_file = self.version_tracker.save_version_file(version_data)
            
            return {
                'status': 'success',
                'message': 'Commit发布成功',
                'version': version,
                'git_info': git_info,
                'version_file': str(version_file)
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Git信息提取失败: {str(e)}"
            }
    
    def release_both(
        self,
        version: str,
        binary_name: Optional[str] = None,
        release_notes: str = "",
        clean_build: bool = False
    ) -> Dict:
        """
        同时发布二进制和commit
        
        Args:
            version: 版本号
            binary_name: 二进制文件名
            release_notes: 发布说明
            clean_build: 是否清理后重新构建
        
        Returns:
            发布结果字典
        """
        logger.info(f"开始发布完整版本（二进制+commit）: {version}")
        
        binary_result = self.release_binary(version, binary_name, release_notes, clean_build)
        
        if binary_result['status'] != 'success':
            return binary_result
        
        commit_result = self.release_commit(version, release_notes)
        
        if commit_result['status'] != 'success':
            return commit_result
        
        version_data = self.version_tracker.load_version_file(version)
        
        version_data['binary'] = binary_result.get('binary_info')
        
        version_file = self.version_tracker.save_version_file(version_data)
        
        return {
            'status': 'success',
            'message': '完整发布成功（二进制+commit）',
            'version': version,
            'binary_info': binary_result.get('binary_info'),
            'git_info': commit_result.get('git_info'),
            'version_file': str(version_file)
        }
