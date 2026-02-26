import os
from pathlib import Path
from typing import List, Tuple, Optional, Set
from ..entities import FileInfo
from ..value_objects import Hash
from .hash_calculator import HashCalculator


class FileScanner:
    
    DEFAULT_IGNORE_PATTERNS = [
        '.git',
        '__pycache__',
        '*.pyc',
        '.DS_Store',
        'node_modules',
        '.venv',
        'venv',
        '.env',
        '*.egg-info',
        '.pytest_cache',
        '.mypy_cache',
        'dist',
        'build',
        '*.so'
    ]
    
    def __init__(self, ignore_patterns: Optional[List[str]] = None):
        self._ignore_patterns = ignore_patterns or self.DEFAULT_IGNORE_PATTERNS
    
    def scan_directory(self, directory: str) -> Tuple[List[FileInfo], dict]:
        base_path = Path(directory)
        if not base_path.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        if not base_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        file_list: List[FileInfo] = []
        total_size = 0
        file_count = 0
        
        for file_path in base_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore(file_path):
                try:
                    file_info = self._create_file_info(file_path, base_path)
                    if file_info:
                        file_list.append(file_info)
                        total_size += file_info.size
                        file_count += 1
                except Exception:
                    pass
        
        scan_info = {
            'total_files': file_count,
            'total_size': total_size
        }
        
        return file_list, scan_info
    
    def _should_ignore(self, file_path: Path) -> bool:
        for pattern in self._ignore_patterns:
            if self._matches_pattern(file_path, pattern):
                return True
        return False
    
    def _matches_pattern(self, file_path: Path, pattern: str) -> bool:
        if pattern.startswith('.'):
            if file_path.name == pattern:
                return True
            if any(part == pattern for part in file_path.parts):
                return True
        
        if '*' in pattern:
            if file_path.match(pattern):
                return True
        
        return file_path.name == pattern
    
    def _create_file_info(self, file_path: Path, base_path: Path) -> Optional[FileInfo]:
        try:
            relative_path = file_path.relative_to(base_path)
            file_size = file_path.stat().st_size
            
            hash_calculator = HashCalculator('sha256')
            file_hash = hash_calculator.calculate_file(str(file_path))
            
            return FileInfo(
                path=str(relative_path),
                size=file_size,
                hash_value=file_hash
            )
        except Exception:
            return None
