import os
import zipfile
from pathlib import Path
from typing import List, Tuple
from ..entities import FileInfo
from ..value_objects import Hash


class Packager:
    
    def __init__(self, output_dir: str = './releases'):
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
    
    def create_zip(
        self,
        source_dir: str,
        file_list: List[FileInfo],
        package_name: str,
        version: str
    ) -> dict:
        source_path = Path(source_dir)
        zip_name = f"{package_name}_v{version}.zip"
        zip_path = self._output_dir / zip_name
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in file_list:
                file_path = source_path / file_info.path
                if file_path.exists():
                    zipf.write(file_path, file_info.path)
        
        zip_size = zip_path.stat().st_size
        hash_calculator = HashCalculator('sha256')
        zip_hash = hash_calculator.calculate_file(str(zip_path))
        
        return {
            'archive_name': zip_name,
            'archive_path': str(zip_path),
            'size': zip_size,
            'file_count': len(file_list),
            'hash': str(zip_hash)
        }
    
    def extract_zip(self, zip_path: str, output_dir: str) -> List[str]:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        extracted_files = []
        
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(output_path)
            extracted_files = zipf.namelist()
        
        return extracted_files
    
    def verify_zip(self, zip_path: str, expected_hash: Hash) -> bool:
        hash_calculator = HashCalculator(expected_hash.algorithm)
        actual_hash = hash_calculator.calculate_file(zip_path)
        
        return actual_hash == expected_hash
    
    @property
    def output_dir(self) -> Path:
        return self._output_dir


from .hash_calculator import HashCalculator
