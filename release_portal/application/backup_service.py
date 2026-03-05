"""
数据备份服务

提供数据库和文件的备份、恢复功能
"""

import os
import sqlite3
import shutil
import tarfile
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import hashlib


class BackupService:
    """数据备份服务"""
    
    def __init__(self, db_path: str, storage_path: str, backup_dir: str = "./backups"):
        """
        初始化备份服务
        
        Args:
            db_path: 数据库文件路径
            storage_path: 存储目录路径
            backup_dir: 备份文件存储目录
        """
        self.db_path = db_path
        self.storage_path = storage_path
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, name: Optional[str] = None, 
                     include_storage: bool = True) -> Dict[str, any]:
        """
        创建备份
        
        Args:
            name: 备份名称（可选）
            include_storage: 是否包含存储文件
        
        Returns:
            备份信息字典
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = name or f"backup_{timestamp}"
        backup_filename = f"{backup_name}.tar.gz"
        backup_path = self.backup_dir / backup_filename
        
        # 创建临时目录
        temp_dir = self.backup_dir / f"temp_{timestamp}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # 1. 备份数据库
            db_backup_path = temp_dir / "portal.db"
            shutil.copy2(self.db_path, db_backup_path)
            
            # 2. 备份存储文件（如果需要）
            if include_storage and os.path.exists(self.storage_path):
                storage_backup_path = temp_dir / "storage"
                if os.path.isdir(self.storage_path):
                    shutil.copytree(self.storage_path, storage_backup_path)
                else:
                    shutil.copy2(self.storage_path, storage_backup_path)
            
            # 3. 创建备份元数据
            metadata = {
                "name": backup_name,
                "created_at": datetime.now().isoformat(),
                "database_size": os.path.getsize(db_backup_path),
                "includes_storage": include_storage,
                "db_path": self.db_path,
                "storage_path": self.storage_path
            }
            
            if include_storage and os.path.exists(self.storage_path):
                metadata["storage_size"] = self._get_dir_size(storage_backup_path)
            
            metadata_path = temp_dir / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # 4. 创建压缩包
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(temp_dir, arcname=backup_name)
            
            # 5. 计算校验和
            checksum = self._calculate_checksum(backup_path)
            
            # 6. 获取文件大小
            file_size = os.path.getsize(backup_path)
            
            return {
                "backup_id": backup_name,
                "filename": backup_filename,
                "path": str(backup_path),
                "size": file_size,
                "checksum": checksum,
                "created_at": metadata["created_at"],
                "includes_storage": include_storage,
                "metadata": metadata
            }
        
        finally:
            # 清理临时目录
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def restore_backup(self, backup_filename: str, 
                      target_db_path: Optional[str] = None,
                      target_storage_path: Optional[str] = None) -> Dict[str, any]:
        """
        恢复备份
        
        Args:
            backup_filename: 备份文件名
            target_db_path: 目标数据库路径（可选，默认使用原路径）
            target_storage_path: 目标存储路径（可选，默认使用原路径）
        
        Returns:
            恢复信息字典
        """
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            raise ValueError(f"Backup file not found: {backup_filename}")
        
        # 创建临时目录
        temp_dir = self.backup_dir / f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        temp_dir.mkdir(exist_ok=True)
        
        try:
            # 1. 解压备份文件
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(temp_dir)
            
            # 2. 查找解压后的目录
            extracted_dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
            if not extracted_dirs:
                raise ValueError("Invalid backup file: no data found")
            
            backup_dir = extracted_dirs[0]
            
            # 3. 读取元数据
            metadata_path = backup_dir / "metadata.json"
            if metadata_path.exists():
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            else:
                metadata = {}
            
            # 4. 恢复数据库
            db_backup_path = backup_dir / "portal.db"
            if db_backup_path.exists():
                target_db = target_db_path or self.db_path
                
                # 备份当前数据库
                if os.path.exists(target_db):
                    backup_current = f"{target_db}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    shutil.copy2(target_db, backup_current)
                
                # 恢复数据库
                shutil.copy2(db_backup_path, target_db)
            else:
                raise ValueError("Database backup not found in backup file")
            
            # 5. 恢复存储文件（如果存在）
            storage_backup_path = backup_dir / "storage"
            if storage_backup_path.exists():
                target_storage = target_storage_path or self.storage_path
                
                # 备份当前存储
                if os.path.exists(target_storage):
                    backup_current_storage = f"{target_storage}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    if os.path.isdir(target_storage):
                        shutil.copytree(target_storage, backup_current_storage)
                    else:
                        shutil.copy2(target_storage, backup_current_storage)
                
                # 恢复存储
                if os.path.isdir(target_storage):
                    shutil.rmtree(target_storage)
                
                if os.path.isdir(storage_backup_path):
                    shutil.copytree(storage_backup_path, target_storage)
                else:
                    shutil.copy2(storage_backup_path, target_storage)
            
            return {
                "success": True,
                "backup_filename": backup_filename,
                "restored_at": datetime.now().isoformat(),
                "metadata": metadata
            }
        
        finally:
            # 清理临时目录
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def list_backups(self) -> List[Dict[str, any]]:
        """
        列出所有备份
        
        Returns:
            备份信息列表
        """
        backups = []
        
        for backup_file in self.backup_dir.glob("*.tar.gz"):
            try:
                # 获取文件信息
                stat = backup_file.stat()
                
                # 尝试读取元数据
                metadata = self._read_metadata_from_file(backup_file)
                
                backups.append({
                    "filename": backup_file.name,
                    "size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "checksum": self._calculate_checksum(backup_file),
                    "metadata": metadata
                })
            
            except Exception as e:
                # 如果无法读取备份，跳过
                continue
        
        # 按创建时间倒序排列
        backups.sort(key=lambda x: x["created_at"], reverse=True)
        
        return backups
    
    def delete_backup(self, backup_filename: str) -> bool:
        """
        删除备份
        
        Args:
            backup_filename: 备份文件名
        
        Returns:
            是否删除成功
        """
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            return False
        
        try:
            backup_path.unlink()
            return True
        except Exception:
            return False
    
    def get_backup_info(self, backup_filename: str) -> Optional[Dict[str, any]]:
        """
        获取备份信息
        
        Args:
            backup_filename: 备份文件名
        
        Returns:
            备份信息字典
        """
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            return None
        
        stat = backup_path.stat()
        metadata = self._read_metadata_from_file(backup_path)
        
        return {
            "filename": backup_filename,
            "size": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "checksum": self._calculate_checksum(backup_path),
            "metadata": metadata
        }
    
    def download_backup(self, backup_filename: str) -> Optional[str]:
        """
        获取备份文件路径（用于下载）
        
        Args:
            backup_filename: 备份文件名
        
        Returns:
            备份文件路径
        """
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            return None
        
        return str(backup_path)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _get_dir_size(self, directory: Path) -> int:
        """计算目录大小"""
        total_size = 0
        
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
        
        return total_size
    
    def _read_metadata_from_file(self, backup_path: Path) -> Optional[Dict]:
        """从备份文件中读取元数据"""
        import tempfile
        
        temp_dir = None
        try:
            temp_dir = Path(tempfile.mkdtemp())
            
            # 解压备份文件
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(temp_dir)
            
            # 查找元数据文件
            metadata_files = list(temp_dir.glob("*/metadata.json"))
            
            if metadata_files:
                with open(metadata_files[0], 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            return None
        
        except Exception:
            return None
        
        finally:
            if temp_dir and temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
