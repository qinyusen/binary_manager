import os
import json
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Packager:
    def __init__(self, output_dir: str = './releases'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def create_zip(self, source_dir: str, file_list: List[Dict], 
                   package_name: str, version: str) -> Dict:
        source_path = Path(source_dir)
        zip_name = f"{package_name}_v{version}.zip"
        zip_path = self.output_dir / zip_name
        
        logger.info(f"Creating zip archive: {zip_path}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in file_list:
                file_path = source_path / file_info['path']
                zipf.write(file_path, file_info['path'])
                logger.debug(f"Added to zip: {file_info['path']}")
        
        zip_size = zip_path.stat().st_size
        zip_hash = self.calculate_zip_hash(zip_path)
        
        logger.info(f"Zip created: {zip_name} ({zip_size} bytes)")
        
        return {
            'archive_name': zip_name,
            'archive_path': str(zip_path),
            'size': zip_size,
            'file_count': len(file_list),
            'hash': zip_hash
        }

    def calculate_zip_hash(self, zip_path: Path, algorithm='sha256') -> str:
        hash_func = hashlib.new(algorithm)
        with open(zip_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        return f"{algorithm}:{hash_func.hexdigest()}"

    def generate_json_config(self, package_name: str, version: str, 
                           file_list: List[Dict], zip_info: Dict,
                           download_url: Optional[str] = None) -> Dict:
        config = {
            'package_name': package_name,
            'version': version,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'file_info': {
                'archive_name': zip_info['archive_name'],
                'size': zip_info['size'],
                'file_count': zip_info['file_count'],
                'hash': zip_info['hash']
            },
            'files': file_list
        }
        
        if download_url:
            config['download_url'] = download_url
            
        return config

    def save_config(self, config_data: Dict, package_name: str, version: str) -> str:
        config_name = f"{package_name}_v{version}.json"
        config_path = self.output_dir / config_name
        
        logger.info(f"Saving config: {config_path}")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Config saved: {config_name}")
        return str(config_path)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        from scanner import generate_file_list
        
        source_dir = sys.argv[1]
        version = sys.argv[2] if len(sys.argv) > 2 else '1.0.0'
        package_name = sys.argv[3] if len(sys.argv) > 3 else 'test_package'
        
        file_list = generate_file_list(source_dir)
        packager = Packager()
        zip_info = packager.create_zip(source_dir, file_list, package_name, version)
        config = packager.generate_json_config(package_name, version, file_list, zip_info)
        config_path = packager.save_config(config, package_name, version)
        
        print(f"Package created successfully!")
        print(f"Config: {config_path}")
        print(f"Archive: {zip_info['archive_path']}")
