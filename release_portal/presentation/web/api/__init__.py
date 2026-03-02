"""
REST API 蓝图
"""
from .auth import auth_bp
from .releases import releases_bp
from .downloads import downloads_bp
from .licenses import licenses_bp

__all__ = ['auth_bp', 'releases_bp', 'downloads_bp', 'licenses_bp']
