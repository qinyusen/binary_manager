"""
下载 REST API
"""
from flask import Blueprint, request, jsonify, send_file
from ..auth_middleware import require_auth
import tempfile
import os

downloads_bp = Blueprint('downloads', __name__)


@downloads_bp.route('/<release_id>/packages', methods=['GET'])
@require_auth
def get_available_packages(release_id: str):
    """获取可下载的包列表（根据权限过滤）
    
    Response:
        {
            "packages": [
                {
                    "content_type": "BINARY",
                    "package_id": "string",
                    "package_name": "string",
                    "version": "string",
                    "size": 1024
                }
            ]
        }
    """
    try:
        from ...initializer import create_container
        
        container = create_container()
        
        # 获取当前用户
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'User not authenticated'
            }), 401
        
        # 获取可下载的包
        packages = container.download_service.get_available_packages(
            user_id=user.user_id,
            release_id=release_id
        )
        
        return jsonify({
            'packages': packages,
            'count': len(packages)
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Bad Request',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@downloads_bp.route('/<release_id>/download/<content_type>', methods=['GET'])
@require_auth
def download_package(release_id: str, content_type: str):
    """下载包
    
    Response: Binary file stream
    """
    try:
        from ...initializer import create_container
        
        container = create_container()
        
        # 获取当前用户
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'User not authenticated'
            }), 401
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 下载包到临时目录
            container.download_service.download_package(
                user_id=user.user_id,
                release_id=release_id,
                content_type=content_type,
                output_dir=temp_dir
            )
            
            # 查找下载的文件
            files = os.listdir(temp_dir)
            if not files:
                return jsonify({
                    'error': 'Not Found',
                    'message': 'Package file not found'
                }), 404
            
            package_file = os.path.join(temp_dir, files[0])
            
            # 发送文件
            return send_file(
                package_file,
                as_attachment=True,
                download_name=files[0]
            )
        
        finally:
            # 清理临时文件（在发送后）
            import atexit
            atexit.register(lambda: __import__('shutil').rmtree(temp_dir, ignore_errors=True))
    
    except ValueError as e:
        return jsonify({
            'error': 'Bad Request',
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@downloads_bp.route('/releases', methods=['GET'])
@require_auth
def list_downloadable_releases():
    """列出用户可下载的发布
    
    Response:
        {
            "releases": [...]
        }
    """
    try:
        from ...initializer import create_container
        
        container = create_container()
        
        # 获取当前用户
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'User not authenticated'
            }), 401
        
        # 获取可下载的发布
        releases = container.download_service.list_downloadable_releases(
            user_id=user.user_id
        )
        
        # 转换为字典
        releases_data = [release.to_dict() for release in releases]
        
        return jsonify({
            'releases': releases_data,
            'count': len(releases_data)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@downloads_bp.route('/license', methods=['GET'])
@require_auth
def get_user_license():
    """获取用户许可证信息
    
    Response:
        {
            "license": {
                "license_id": "string",
                "organization": "string",
                "access_level": "string",
                "allowed_resource_types": ["BSP", ...],
                "expires_at": "ISO8601",
                "is_active": true
            }
        }
    """
    try:
        from ...initializer import create_container
        
        container = create_container()
        
        # 获取当前用户
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'User not authenticated'
            }), 401
        
        # 获取许可证信息
        license_info = container.download_service.get_user_license_info(
            user_id=user.user_id
        )
        
        if not license_info:
            return jsonify({
                'license': None,
                'message': 'No license assigned'
            }), 200
        
        return jsonify({
            'license': license_info
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500
