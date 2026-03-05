"""
REST API 蓝图
"""
import sys
import os

# 添加项目根目录到路径，以便可以导入 shared 模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from .auth import auth_bp
from .releases import releases_bp
from .downloads import downloads_bp
from .licenses import licenses_bp
from .backup import backup_bp
from .cold_backup import cold_backup_bp

__all__ = ['auth_bp', 'releases_bp', 'downloads_bp', 'licenses_bp', 'backup_bp', 'cold_backup_bp']
