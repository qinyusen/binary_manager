"""
数据冷备份服务

支持将备份数据归档到长期存储介质，如：
- 本地文件系统
- S3 兼容存储（包括 AWS Glacier）
- FTP/SFTP 服务器
- 本地磁带/磁盘

冷备份特点：
- 定期执行
- 长期保存
- 低成本存储
- 恢复时间较长
- 用于灾难恢复
"""

import os
import sys
import json
import shutil
import tarfile
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Callable
from abc import ABC, abstractmethod
import threading
import schedule
import time


class ColdStorageBackend(ABC):
    """冷存储后端抽象基类"""
    
    @abstractmethod
    def store(self, backup_path: str, metadata: Dict) -> Dict:
        """存储备份到冷存储"""
        pass
    
    @abstractmethod
    def retrieve(self, backup_id: str, local_path: str) -> bool:
        """从冷存储检索备份"""
        pass
    
    @abstractmethod
    def list_archives(self) -> List[Dict]:
        """列出所有归档"""
        pass
    
    @abstractmethod
    def delete(self, backup_id: str) -> bool:
        """删除归档"""
        pass
    
    @abstractmethod
    def get_storage_info(self) -> Dict:
        """获取存储信息"""
        pass


class LocalFileSystemBackend(ColdStorageBackend):
    """本地文件系统后端"""
    
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.storage_path / "archive_metadata.json"
        self._load_metadata()
    
    def _load_metadata(self):
        """加载元数据"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = {}
    
    def _save_metadata(self):
        """保存元数据"""
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
    
    def store(self, backup_path: str, metadata: Dict) -> Dict:
        """存储备份到本地文件系统"""
        archive_id = metadata.get('name', f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        archive_filename = f"{archive_id}.tar.gz"
        archive_path = self.storage_path / archive_filename
        
        # 复制备份文件
        shutil.copy2(backup_path, archive_path)
        
        # 计算校验和
        checksum = self._calculate_checksum(archive_path)
        
        # 创建归档元数据
        archive_metadata = {
            'archive_id': archive_id,
            'filename': archive_filename,
            'size': os.path.getsize(archive_path),
            'checksum': checksum,
            'stored_at': datetime.now().isoformat(),
            'backup_metadata': metadata,
            'storage_type': 'local',
            'storage_path': str(self.storage_path)
        }
        
        # 保存元数据
        self.metadata[archive_id] = archive_metadata
        self._save_metadata()
        
        return archive_metadata
    
    def retrieve(self, backup_id: str, local_path: str) -> bool:
        """从本地文件系统检索备份"""
        if backup_id not in self.metadata:
            return False
        
        archive_metadata = self.metadata[backup_id]
        archive_path = self.storage_path / archive_metadata['filename']
        
        if not archive_path.exists():
            return False
        
        shutil.copy2(archive_path, local_path)
        return True
    
    def list_archives(self) -> List[Dict]:
        """列出所有归档"""
        return list(self.metadata.values())
    
    def delete(self, backup_id: str) -> bool:
        """删除归档"""
        if backup_id not in self.metadata:
            return False
        
        archive_metadata = self.metadata[backup_id]
        archive_path = self.storage_path / archive_metadata['filename']
        
        if archive_path.exists():
            archive_path.unlink()
        
        del self.metadata[backup_id]
        self._save_metadata()
        
        return True
    
    def get_storage_info(self) -> Dict:
        """获取存储信息"""
        total_size = sum(m['size'] for m in self.metadata.values())
        return {
            'storage_type': 'local',
            'storage_path': str(self.storage_path),
            'archive_count': len(self.metadata),
            'total_size': total_size,
            'available_space': shutil.disk_usage(self.storage_path).free
        }
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class S3ColdStorageBackend(ColdStorageBackend):
    """S3 兼容存储后端（支持 AWS Glacier）"""
    
    def __init__(self, bucket: str, prefix: str = "", 
                 region: str = "us-east-1",
                 storage_class: str = "GLACIER"):
        """
        初始化 S3 后端
        
        Args:
            bucket: S3 bucket 名称
            prefix: 对象前缀
            region: AWS 区域
            storage_class: 存储类型（STANDARD, GLACIER, DEEP_ARCHIVE）
        """
        self.bucket = bucket
        self.prefix = prefix
        self.region = region
        self.storage_class = storage_class
        
        # 尝试导入 boto3
        try:
            import boto3
            self.s3_client = boto3.client('s3', region_name=region)
            self.boto3_available = True
        except ImportError:
            self.boto3_available = False
            print("Warning: boto3 not available. Install with: pip install boto3")
    
    def store(self, backup_path: str, metadata: Dict) -> Dict:
        """存储备份到 S3"""
        if not self.boto3_available:
            raise RuntimeError("boto3 is not installed")
        
        archive_id = metadata.get('name', f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        object_key = f"{self.prefix}{archive_id}.tar.gz"
        
        # 计算校验和
        with open(backup_path, 'rb') as f:
            file_content = f.read()
        checksum = hashlib.sha256(file_content).hexdigest()
        
        # 上传到 S3
        extra_args = {}
        if self.storage_class:
            extra_args['StorageClass'] = self.storage_class
        
        self.s3_client.upload_file(
            backup_path,
            self.bucket,
            object_key,
            ExtraArgs=extra_args
        )
        
        # 获取对象信息
        response = self.s3_client.head_object(Bucket=self.bucket, Key=object_key)
        
        return {
            'archive_id': archive_id,
            'object_key': object_key,
            'bucket': self.bucket,
            'size': response['ContentLength'],
            'checksum': checksum,
            'stored_at': datetime.now().isoformat(),
            'backup_metadata': metadata,
            'storage_type': 's3',
            'storage_class': self.storage_class,
            'region': self.region
        }
    
    def retrieve(self, backup_id: str, local_path: str) -> bool:
        """从 S3 检索备份"""
        if not self.boto3_available:
            return False
        
        # 如果是 GLACIER 存储需要先恢复
        try:
            object_key = f"{self.prefix}{backup_id}.tar.gz"
            self.s3_client.download_file(
                self.bucket,
                object_key,
                local_path
            )
            return True
        except Exception:
            return False
    
    def list_archives(self) -> List[Dict]:
        """列出 S3 中的归档"""
        if not self.boto3_available:
            return []
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket, Prefix=self.prefix)
            
            archives = []
            for page in pages:
                for obj in page.get('Contents', []):
                    archives.append({
                        'archive_id': obj['Key'].replace(self.prefix, '').replace('.tar.gz', ''),
                        'object_key': obj['Key'],
                        'size': obj['Size'],
                        'stored_at': obj['LastModified'].isoformat(),
                        'storage_type': 's3'
                    })
            
            return archives
        except Exception:
            return []
    
    def delete(self, backup_id: str) -> bool:
        """删除 S3 归档"""
        if not self.boto3_available:
            return False
        
        try:
            object_key = f"{self.prefix}{backup_id}.tar.gz"
            self.s3_client.delete_object(Bucket=self.bucket, Key=object_key)
            return True
        except Exception:
            return False
    
    def get_storage_info(self) -> Dict:
        """获取 S3 存储信息"""
        return {
            'storage_type': 's3',
            'bucket': self.bucket,
            'prefix': self.prefix,
            'region': self.region,
            'storage_class': self.storage_class
        }


class ColdBackupService:
    """冷备份服务"""
    
    def __init__(self, backup_dir: str, cold_storage_backend: ColdStorageBackend,
                 retention_days: int = 365):
        """
        初始化冷备份服务
        
        Args:
            backup_dir: 热备份目录
            cold_storage_backend: 冷存储后端
            retention_days: 保留天数
        """
        self.backup_dir = Path(backup_dir)
        self.cold_storage = cold_storage_backend
        self.retention_days = retention_days
        self.scheduler_running = False
        self.scheduler_thread = None
        
        # 归档元数据
        self.archive_metadata_file = self.backup_dir / "cold_archive_metadata.json"
        self._load_archive_metadata()
    
    def _load_archive_metadata(self):
        """加载归档元数据"""
        if self.archive_metadata_file.exists():
            with open(self.archive_metadata_file, 'r', encoding='utf-8') as f:
                self.archive_metadata = json.load(f)
        else:
            self.archive_metadata = {}
    
    def _save_archive_metadata(self):
        """保存归档元数据"""
        with open(self.archive_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.archive_metadata, f, indent=2, ensure_ascii=False)
    
    def create_cold_backup(self, backup_name: Optional[str] = None,
                          include_storage: bool = True) -> Dict:
        """
        创建冷备份
        
        Args:
            backup_name: 备份名称
            include_storage: 是否包含存储文件
        
        Returns:
            归档信息
        """
        from release_portal.application.backup_service import BackupService
        
        # 1. 创建热备份
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        hot_backup_name = backup_name or f"hot_backup_{timestamp}"
        
        backup_service = BackupService(
            db_path='./data/portal.db',
            storage_path='./releases',
            backup_dir=str(self.backup_dir)
        )
        
        backup_info = backup_service.create_backup(
            name=hot_backup_name,
            include_storage=include_storage
        )
        
        # 2. 归档到冷存储
        backup_path = backup_info['path']
        
        archive_metadata = self.cold_storage.store(
            backup_path=backup_path,
            metadata=backup_info
        )
        
        # 3. 保存归档记录
        archive_id = archive_metadata['archive_id']
        self.archive_metadata[archive_id] = {
            'archive_id': archive_id,
            'hot_backup_name': hot_backup_name,
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=self.retention_days)).isoformat(),
            'status': 'archived',
            'metadata': archive_metadata
        }
        self._save_archive_metadata()
        
        # 4. 可选：删除热备份文件
        # os.remove(backup_path)
        
        return archive_metadata
    
    def retrieve_from_cold_storage(self, archive_id: str, 
                                   restore_path: str) -> bool:
        """
        从冷存储检索备份
        
        Args:
            archive_id: 归档 ID
            restore_path: 恢复路径
        
        Returns:
            是否成功
        """
        if archive_id not in self.archive_metadata:
            return False
        
        return self.cold_storage.retrieve(archive_id, restore_path)
    
    def list_cold_archives(self) -> List[Dict]:
        """列出所有冷归档"""
        archives = []
        
        for archive_id, metadata in self.archive_metadata.items():
            archive_info = {
                'archive_id': archive_id,
                'hot_backup_name': metadata['hot_backup_name'],
                'created_at': metadata['created_at'],
                'expires_at': metadata['expires_at'],
                'status': metadata['status'],
                'metadata': metadata['metadata']
            }
            archives.append(archive_info)
        
        # 按创建时间倒序
        archives.sort(key=lambda x: x['created_at'], reverse=True)
        
        return archives
    
    def delete_cold_archive(self, archive_id: str) -> bool:
        """删除冷归档"""
        if archive_id not in self.archive_metadata:
            return False
        
        success = self.cold_storage.delete(archive_id)
        
        if success:
            del self.archive_metadata[archive_id]
            self._save_archive_metadata()
        
        return success
    
    def cleanup_expired_archives(self) -> int:
        """清理过期的归档"""
        now = datetime.now()
        expired_archives = []
        
        for archive_id, metadata in list(self.archive_metadata.items()):
            expires_at = datetime.fromisoformat(metadata['expires_at'])
            if now > expires_at:
                if self.delete_cold_archive(archive_id):
                    expired_archives.append(archive_id)
        
        return len(expired_archives)
    
    def get_storage_info(self) -> Dict:
        """获取冷存储信息"""
        return self.cold_storage.get_storage_info()
    
    def schedule_automatic_backup(self, interval_hours: int = 24):
        """
        定时自动备份
        
        Args:
            interval_hours: 备份间隔（小时）
        """
        def backup_job():
            try:
                print(f"[{datetime.now()}] Starting automatic cold backup...")
                self.create_cold_backup()
                print(f"[{datetime.now()}] Automatic cold backup completed")
            except Exception as e:
                print(f"[{datetime.now()}] Automatic cold backup failed: {e}")
        
        schedule.every(interval_hours).hours.do(backup_job)
        
        # 启动调度器
        if not self.scheduler_running:
            self.scheduler_running = True
            self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.scheduler_thread.start()
    
    def _run_scheduler(self):
        """运行调度器"""
        while self.scheduler_running:
            schedule.run_pending()
            time.sleep(60)
    
    def stop_scheduler(self):
        """停止调度器"""
        self.scheduler_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
    
    def get_backup_policy(self) -> Dict:
        """获取备份策略"""
        return {
            'retention_days': self.retention_days,
            'scheduler_running': self.scheduler_running,
            'storage_backend': type(self.cold_storage).__name__,
            'storage_info': self.get_storage_info(),
            'archive_count': len(self.archive_metadata)
        }


class ColdBackupManager:
    """冷备份管理器（单例模式）"""
    
    _instance = None
    _service = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self, backup_dir: str, storage_type: str = "local",
                 storage_config: Dict = None):
        """
        初始化冷备份服务
        
        Args:
            backup_dir: 备份目录
            storage_type: 存储类型（local, s3）
            storage_config: 存储配置
        """
        # 创建存储后端
        if storage_type == "local":
            backend = LocalFileSystemBackend(
                storage_path=storage_config.get('storage_path', './cold_storage')
            )
        elif storage_type == "s3":
            backend = S3ColdStorageBackend(
                bucket=storage_config.get('bucket', ''),
                prefix=storage_config.get('prefix', 'cold_backups/'),
                region=storage_config.get('region', 'us-east-1'),
                storage_class=storage_config.get('storage_class', 'GLACIER')
            )
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
        
        # 创建服务
        self._service = ColdBackupService(
            backup_dir=backup_dir,
            cold_storage_backend=backend,
            retention_days=storage_config.get('retention_days', 365)
        )
        
        return self._service
    
    def get_service(self) -> ColdBackupService:
        """获取冷备份服务实例"""
        if self._service is None:
            raise RuntimeError("ColdBackupService not initialized. Call initialize() first.")
        return self._service
