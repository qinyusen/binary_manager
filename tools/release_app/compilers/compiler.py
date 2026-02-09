"""
编译器抽象基类
定义编译器的通用接口
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional


class BaseCompiler(ABC):
    """编译器基类"""
    
    def __init__(self, project_dir: Path, build_dir: Optional[Path] = None):
        """
        初始化编译器
        
        Args:
            project_dir: 项目根目录
            build_dir: 构建目录，默认为项目目录下的build/
        """
        self.project_dir = Path(project_dir)
        self.build_dir = Path(build_dir) if build_dir else self.project_dir / 'build'
        self.build_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def compile(self, target: str = "all", verbose: bool = False) -> Dict:
        """
        编译项目
        
        Args:
            target: 编译目标（如all, clean等）
            verbose: 是否显示详细输出
        
        Returns:
            编译结果字典，包含 status, message, binary_path 等
        """
        pass
    
    @abstractmethod
    def clean(self) -> Dict:
        """
        清理构建目录
        
        Returns:
            清理结果字典
        """
        pass
    
    @abstractmethod
    def find_binary(self, binary_name: Optional[str] = None) -> Optional[Path]:
        """
        查找编译后的二进制文件
        
        Args:
            binary_name: 二进制文件名（可选）
        
        Returns:
            二进制文件的完整路径，如果未找到返回None
        """
        pass
    
    def get_build_info(self) -> Dict:
        """获取构建系统信息"""
        return {
            'project_dir': str(self.project_dir),
            'build_dir': str(self.build_dir),
            'compiler_type': self.__class__.__name__
        }
