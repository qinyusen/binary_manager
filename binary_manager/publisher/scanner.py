import os
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default ignore patterns
DEFAULT_IGNORE_PATTERNS = [
    '.git',
    '__pycache__',
    '*.pyc',
    '.DS_Store',
    'node_modules',
    '.venv',
    'venv',
    '.env'
]


class FileScanner:
    def __init__(self, ignore_patterns=None):
        self.ignore_patterns = ignore_patterns or DEFAULT_IGNORE_PATTERNS

    def _should_ignore(self, file_path: Path) -> bool:
        for pattern in self.ignore_patterns:
            if pattern.startswith('.') or '*' in pattern:
                if file_path.name == pattern or file_path.match(pattern):
                    return True
                if any(part == pattern for part in file_path.parts):
                    return True
            else:
                if file_path.name == pattern:
                    return True
                if any(part == pattern for part in file_path.parts):
                    return True
        return False

    def calculate_file_hash(self, file_path: Path, algorithm='sha256') -> str:
        hash_func = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return f"{algorithm}:{hash_func.hexdigest()}"

    def get_file_info(self, file_path: Path, base_path: Path) -> Optional[Dict]:
        try:
            relative_path = file_path.relative_to(base_path)
            file_size = file_path.stat().st_size
            file_hash = self.calculate_file_hash(file_path)
            
            return {
                'path': str(relative_path),
                'size': file_size,
                'hash': file_hash
            }
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return None

    def scan_directory(self, directory: str) -> Tuple[List[Dict], Dict]:
        base_path = Path(directory)
        if not base_path.exists():
            raise ValueError(f"Directory does not exist: {directory}")
        
        if not base_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")

        file_list = []
        total_size = 0
        file_count = 0

        logger.info(f"Scanning directory: {directory}")

        for file_path in base_path.rglob('*'):
            if file_path.is_file() and not self._should_ignore(file_path):
                file_info = self.get_file_info(file_path, base_path)
                if file_info:
                    file_list.append(file_info)
                    total_size += file_info['size']
                    file_count += 1
                    logger.info(f"Found: {file_info['path']} ({file_info['size']} bytes)")

        logger.info(f"Scan complete: {file_count} files, {total_size} bytes")

        return file_list, {'total_files': file_count, 'total_size': total_size}


def generate_file_list(directory: str, ignore_patterns=None) -> List[Dict]:
    scanner = FileScanner(ignore_patterns)
    file_list, _ = scanner.scan_directory(directory)
    return file_list


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_list = generate_file_list(sys.argv[1])
        print(f"Found {len(file_list)} files")
        for f in file_list:
            print(f"  {f['path']}: {f['size']} bytes, {f['hash']}")
