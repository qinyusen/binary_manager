"""
数据冷备份服务 - 兼容层
本文件已拆分为独立模块，此处保留原有接口用于向后兼容

新代码请直接导入新模块：
from release_portal.application.cold_backup import ColdBackupService, ColdBackupManager
"""

import warnings

# 发出迁移警告
warnings.warn(
    "cold_backup_service.py has been split into multiple modules. "
    "Please import from release_portal.application.cold_backup instead.",
    DeprecationWarning,
    stacklevel=2,
)

# 从新模块导入所有公共API
from .cold_backup import (
    # 存储后端
    ColdStorageBackend,
    LocalFileSystemBackend,
    S3ColdStorageBackend,
    # 核心服务
    ColdBackupService,
    # 管理器
    ColdBackupManager,
    backup_manager,
    initialize_backup_manager,
)

# 兼容原有导入
__all__ = [
    "ColdStorageBackend",
    "LocalFileSystemBackend",
    "S3ColdStorageBackend",
    "ColdBackupService",
    "ColdBackupManager",
    "backup_manager",
    "initialize_backup_manager",
]

# 为极端兼容场景，保留原文件中的类定义（可选）
# 实际使用时建议迁移到新的导入路径
