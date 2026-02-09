"""
工具函数模块
提供各种辅助功能
"""

import os
import socket
import platform
from pathlib import Path
from typing import Dict, Optional
import hashlib


def calculate_file_hash(file_path: Path, algorithm: str = 'sha256') -> str:
    """计算文件的哈希值"""
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)
    return f"{algorithm}:{hash_func.hexdigest()}"


def get_publisher_info() -> Dict:
    """获取发布者信息"""
    return {
        'hostname': socket.gethostname(),
        'username': os.getenv('USER', os.getenv('USERNAME', 'unknown')),
        'os': platform.system(),
        'arch': platform.machine()
    }


def find_binary_file(project_dir: Path, binary_name: Optional[str] = None) -> Optional[Path]:
    """
    查找编译后的二进制文件
    优先查找 build/ 和 bin/ 目录
    """
    search_paths = ['build', 'bin', 'output', 'dist']
    
    for search_path in search_paths:
        build_dir = project_dir / search_path
        if not build_dir.exists():
            continue
        
        if binary_name:
            binary_path = build_dir / binary_name
            if binary_path.exists() and binary_path.is_file():
                return binary_path
        
        for file_path in build_dir.rglob('*'):
            if file_path.is_file() and is_executable(file_path):
                return file_path
    
    return None


def is_executable(file_path: Path) -> bool:
    """检查文件是否为可执行文件"""
    if platform.system() == 'Windows':
        return file_path.suffix.lower() in ['.exe', '.com', '.bat']
    
    return os.access(file_path, os.X_OK)


def detect_build_system(project_dir: Path) -> Optional[str]:
    """
    检测项目的构建系统
    返回: 'cmake', 'make', 'meson', 'autoconf', None
    """
    if (project_dir / 'CMakeLists.txt').exists():
        return 'cmake'
    elif (project_dir / 'Makefile').exists():
        return 'make'
    elif (project_dir / 'meson.build').exists():
        return 'meson'
    elif (project_dir / 'configure').exists() or (project_dir / 'configure.ac').exists():
        return 'autoconf'
    
    return None


def get_current_git_commit(repo_dir: Path) -> Optional[str]:
    """获取当前Git commit hash（简化版）"""
    import subprocess
    
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return None


def validate_semantic_version(version: str) -> bool:
    """验证语义化版本号格式"""
    import re
    pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
    return re.match(pattern, version) is not None


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"
