import os
import shutil
import hashlib
from pathlib import Path
from typing import Optional, Dict, List
from ...domain.repositories import StorageRepository
from ...shared.logger import Logger


class LocalStorage(StorageRepository):
    """本地文件存储实现"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.logger = Logger.get(self.__class__.__name__)
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict] = None
    ) -> bool:
        try:
            src = Path(local_path)
            dst = self.base_path / remote_path
            
            if not src.exists():
                self.logger.error(f"Source file not found: {local_path}")
                return False
            
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            
            if metadata:
                meta_path = dst.with_suffix('.meta')
                import json
                with open(meta_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            self.logger.info(f"Copied {local_path} to {dst}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to upload file: {e}")
            return False
    
    def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            src = self.base_path / remote_path
            dst = Path(local_path)
            
            if not src.exists():
                self.logger.error(f"Remote file not found: {remote_path}")
                return False
            
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            
            self.logger.info(f"Copied {src} to {local_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to download file: {e}")
            return False
    
    def file_exists(self, remote_path: str) -> bool:
        return (self.base_path / remote_path).exists()
    
    def delete_file(self, remote_path: str) -> bool:
        try:
            file_path = self.base_path / remote_path
            if file_path.exists():
                file_path.unlink()
                
                meta_path = file_path.with_suffix('.meta')
                if meta_path.exists():
                    meta_path.unlink()
                
                self.logger.info(f"Deleted {remote_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete file: {e}")
            return False
    
    def list_files(self, prefix: str) -> List[str]:
        try:
            base = self.base_path / prefix
            if not base.exists():
                return []
            
            if base.is_file():
                return [prefix]
            
            files = []
            for file_path in base.rglob('*'):
                if file_path.is_file() and not file_path.name.endswith('.meta'):
                    rel_path = file_path.relative_to(self.base_path)
                    files.append(str(rel_path))
            
            return sorted(files)
        except Exception as e:
            self.logger.error(f"Failed to list files: {e}")
            return []
    
    def get_file_url(self, remote_path: str, expiration: int = 3600) -> Optional[str]:
        return f"file://{self.base_path / remote_path}"
    
    def verify_file(self, local_path: str, expected_hash: str) -> bool:
        try:
            if ':' in expected_hash:
                algorithm, hash_value = expected_hash.split(':', 1)
            else:
                algorithm = 'sha256'
                hash_value = expected_hash
            
            hash_func = hashlib.new(algorithm)
            with open(local_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hash_func.update(chunk)
            
            actual_hash = hash_func.hexdigest()
            return actual_hash.lower() == hash_value.lower()
        except Exception as e:
            self.logger.error(f"Failed to verify file: {e}")
            return False
