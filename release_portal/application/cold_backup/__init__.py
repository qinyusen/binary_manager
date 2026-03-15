"""
冷备份模块
提供冷备份的完整功能，包括存储后端、核心服务和调度管理器

使用示例：
```python
from release_portal.application.cold_backup import (
    ColdStorageBackend,
    LocalFileSystemBackend,
    S3ColdStorageBackend,
    ColdBackupService,
    ColdBackupManager,
    initialize_backup_manager
)

# 创建存储后端
backend = LocalFileSystemBackend("/data/cold_backup")

# 创建服务
service = ColdBackupService(backend)

# 创建备份
backup = service.create_release_backup("rel_123")

# 恢复备份
service.restore_release_backup(backup["backup_id"], "/tmp/restore")
```
"""

# 导出公共API
from .backends import (
    ColdStorageBackend,
    LocalFileSystemBackend,
    S3ColdStorageBackend,
    SFTPColdStorageBackend,
    FTPColdStorageBackend,
)
from .service import ColdBackupService
from .manager import ColdBackupManager, backup_manager, initialize_backup_manager

__all__ = [
    # 存储后端
    "ColdStorageBackend",
    "LocalFileSystemBackend",
    "S3ColdStorageBackend",
    "SFTPColdStorageBackend",
    "FTPColdStorageBackend",
    # 核心服务
    "ColdBackupService",
    # 管理器
    "ColdBackupManager",
    "backup_manager",
    "initialize_backup_manager",
]

# 版本信息
__version__ = "1.0.0"
__author__ = "Release Platform Team"
