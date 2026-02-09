"""
C/C++编译器实现
支持CMake和Make构建系统
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict
import logging

from .compiler import BaseCompiler
from ..utils import find_binary_file, calculate_file_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CCompiler(BaseCompiler):
    """C/C++项目编译器"""
    
    def __init__(self, project_dir: Path, build_dir: Optional[Path] = None, build_system: Optional[str] = None):
        """
        初始化C++编译器
        
        Args:
            project_dir: 项目根目录
            build_dir: 构建目录
            build_system: 构建系统类型 (cmake/make)，自动检测
        """
        super().__init__(project_dir, build_dir)
        
        self.build_system = build_system or self._detect_build_system()
        logger.info(f"检测到构建系统: {self.build_system or '未知'}")
        
        if not self.build_system:
            raise ValueError("无法检测构建系统（需要CMakeLists.txt或Makefile）")
    
    def _detect_build_system(self) -> Optional[str]:
        """检测构建系统类型"""
        if (self.project_dir / 'CMakeLists.txt').exists():
            return 'cmake'
        elif (self.project_dir / 'Makefile').exists():
            return 'make'
        return None
    
    def compile(self, target: str = "all", verbose: bool = False) -> Dict:
        """
        编译项目
        
        Args:
            target: 编译目标
            verbose: 是否显示详细输出
        
        Returns:
            编译结果
        """
        logger.info(f"开始编译项目（构建系统: {self.build_system}）")
        
        try:
            if self.build_system == 'cmake':
                return self._compile_cmake(target, verbose)
            elif self.build_system == 'make':
                return self._compile_make(target, verbose)
            else:
                return {
                    'status': 'error',
                    'message': f'不支持的构建系统: {self.build_system}'
                }
        except Exception as e:
            logger.error(f"编译失败: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _compile_cmake(self, target: str, verbose: bool) -> Dict:
        """使用CMake编译"""
        if not shutil.which('cmake'):
            return {
                'status': 'error',
                'message': '未找到cmake命令'
            }
        
        cmake_args = [
            'cmake',
            '-S', str(self.project_dir),
            '-B', str(self.build_dir),
            '-DCMAKE_BUILD_TYPE=Release'
        ]
        
        if verbose:
            cmake_args.append('-DCMAKE_VERBOSE_MAKEFILE=ON')
        
        logger.info(f"运行: {' '.join(cmake_args)}")
        result = subprocess.run(cmake_args, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {
                'status': 'error',
                'message': f'CMake配置失败: {result.stderr}'
            }
        
        build_args = [
            'cmake',
            '--build', str(self.build_dir),
            '--config', 'Release',
            '--', '-j4'
        ]
        
        if target and target != 'all':
            build_args.extend(['--target', target])
        
        logger.info(f"运行: {' '.join(build_args)}")
        result = subprocess.run(build_args, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {
                'status': 'error',
                'message': f'编译失败: {result.stderr}'
            }
        
        binary_path = self.find_binary()
        
        return {
            'status': 'success',
            'message': 'CMake编译成功',
            'build_system': 'cmake',
            'binary_path': str(binary_path) if binary_path else None
        }
    
    def _compile_make(self, target: str, verbose: bool) -> Dict:
        """使用Make编译"""
        if not shutil.which('make'):
            return {
                'status': 'error',
                'message': '未找到make命令'
            }
        
        make_args = ['make', '-C', str(self.project_dir), '-j4']
        
        if verbose:
            make_args.append('VERBOSE=1')
        
        if target and target != 'all':
            make_args.append(target)
        
        logger.info(f"运行: {' '.join(make_args)}")
        result = subprocess.run(make_args, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {
                'status': 'error',
                'message': f'Make编译失败: {result.stderr}'
            }
        
        binary_path = self.find_binary()
        
        return {
            'status': 'success',
            'message': 'Make编译成功',
            'build_system': 'make',
            'binary_path': str(binary_path) if binary_path else None
        }
    
    def clean(self) -> Dict:
        """清理构建目录"""
        try:
            if self.build_system == 'cmake':
                result = subprocess.run(
                    ['cmake', '--build', str(self.build_dir), '--target', 'clean'],
                    capture_output=True, text=True
                )
            elif self.build_system == 'make':
                result = subprocess.run(
                    ['make', '-C', str(self.project_dir), 'clean'],
                    capture_output=True, text=True
                )
            else:
                return {'status': 'error', 'message': '未知的构建系统'}
            
            if result.returncode == 0:
                return {'status': 'success', 'message': '清理成功'}
            else:
                return {'status': 'error', 'message': result.stderr}
        
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def find_binary(self, binary_name: Optional[str] = None) -> Optional[Path]:
        """查找编译后的二进制文件"""
        return find_binary_file(self.project_dir, binary_name)
    
    def get_binary_info(self, binary_name: Optional[str] = None) -> Optional[Dict]:
        """
        获取二进制文件的详细信息
        
        Returns:
            包含 path, hash, size 等信息的字典
        """
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
