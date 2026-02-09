"""
通用编译器实现
用于无需编译的项目（如Python、脚本等）
"""

from pathlib import Path
from typing import Optional, Dict
import logging

from .compiler import BaseCompiler
from ..utils import find_binary_file, calculate_file_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenericCompiler(BaseCompiler):
    """通用编译器（无需实际编译）"""
    
    def compile(self, target: str = "all", verbose: bool = False) -> Dict:
        """
        模拟编译过程
        
        Returns:
            成功结果
        """
        logger.info("通用编译器：跳过编译步骤")
        
        return {
            'status': 'success',
            'message': '无需编译（通用项目）',
            'build_system': 'generic',
            'binary_path': None
        }
    
    def clean(self) -> Dict:
        """清理（通用项目无需清理）"""
        return {
            'status': 'success',
            'message': '通用项目无需清理'
        }
    
    def find_binary(self, binary_name: Optional[str] = None) -> Optional[Path]:
        """查找主文件或二进制"""
        binary_path = find_binary_file(self.project_dir, binary_name)
        
        if not binary_path:
            logger.warning(f"未找到二进制文件: {binary_name}")
        
        return binary_path
    
    def get_binary_info(self, binary_name: Optional[str] = None) -> Optional[Dict]:
        """获取文件信息"""
        binary_path = self.find_binary(binary_name)
        
        if not binary_path:
            return None
        
        file_stat = binary_path.stat()
        file_hash = calculate_file_hash(binary_path)
        
        return {
            'path': str(binary_path),
            'relative_path': str(binary_path.relative_to(self.project_dir)),
            'name': binary_path.name,
            'size': file_stat.st_size,
            'hash': file_hash,
            'modified': file_stat.st_mtime
        }
