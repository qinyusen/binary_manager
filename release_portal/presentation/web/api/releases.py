"""
发布 REST API
"""
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import sys
import tempfile
import shutil

# 添加项目根目录到路径
_project_root = os.path.join(os.path.dirname(__file__), '../../../..')
sys.path.insert(0, _project_root)

from release_portal.presentation.web.auth_middleware import require_auth, require_role
from release_portal.domain.value_objects import ResourceType, ContentType, ReleaseStatus

releases_bp = Blueprint('releases', __name__)

ALLOWED_EXTENSIONS = {'.tar.gz', '.tar', '.zip'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB


@releases_bp.route('', methods=['GET'])
@require_auth
def list_releases():
    """列出所有发布
    
    Query Parameters:
        type: 资源类型（BSP, DRIVER, EXAMPLES）
        status: 状态（DRAFT, PUBLISHED, ARCHIVED）
    
    Response:
        {
            "releases": [
                {
                    "release_id": "string",
                    "resource_type": "string",
                    "version": "string",
                    "status": "string",
                    "publisher_id": "string",
                    "description": "string",
                    "changelog": "string",
                    "created_at": "ISO8601",
                    "published_at": "ISO8601"
                }
            ]
        }
    """
    try:
        from release_portal.initializer import create_container
        
        container = create_container()
        
        # 获取查询参数
        resource_type_str = request.args.get('type')
        status_str = request.args.get('status')
        
        # 转换参数
        resource_type = ResourceType.from_string(resource_type_str) if resource_type_str else None
        status = ReleaseStatus.from_string(status_str) if status_str else None
        
        # 列出发布
        if resource_type:
            releases = container.release_service.list_releases(resource_type=resource_type)
        elif status:
            releases = container.release_service.list_releases(status=status_str)
        else:
            releases = container.release_service.list_releases()
        
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


@releases_bp.route('/<release_id>', methods=['GET'])
@require_auth
def get_release(release_id: str):
    """获取发布详情
    
    Response:
        {
            "release": {...}
        }
    """
    try:
        from release_portal.initializer import create_container
        
        container = create_container()
        release = container.release_service.get_release(release_id)
        
        if not release:
            return jsonify({
                'error': 'Not Found',
                'message': f'Release {release_id} not found'
            }), 404
        
        return jsonify({
            'release': release.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


def allowed_file(filename: str) -> bool:
    """检查文件扩展名是否允许"""
    return any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS)


@releases_bp.route('/<release_id>/packages', methods=['POST'])
@require_auth
def upload_package(release_id: str):
    """上传包文件并添加到发布
    
    Request: multipart/form-data
        package_file: 包文件
        content_type: 内容类型 (SOURCE/BINARY/DOCUMENT)
    
    Response:
        {
            "package_id": "string",
            "message": "Package uploaded successfully"
        }
    """
    try:
        from release_portal.initializer import create_container
        
        container = create_container()
        
        # 检查文件是否存在
        if 'package_file' not in request.files:
            return jsonify({
                'error': 'Bad Request',
                'message': 'No file provided'
            }), 400
        
        file = request.files['package_file']
        
        if file.filename == '':
            return jsonify({
                'error': 'Bad Request',
                'message': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Bad Request',
                'message': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # 获取内容类型
        content_type_str = request.form.get('content_type', 'BINARY')
        try:
            content_type = ContentType.from_string(content_type_str)
        except ValueError as e:
            return jsonify({
                'error': 'Bad Request',
                'message': f'Invalid content_type: {content_type_str}'
            }), 400
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 保存上传的文件
            filename = secure_filename(file.filename)
            filepath = os.path.join(temp_dir, filename)
            file.save(filepath)
            
            # 如果是压缩文件，解压它
            extracted_dir = temp_dir
            if filename.endswith('.tar.gz') or filename.endswith('.tar'):
                import tarfile
                with tarfile.open(filepath, 'r:gz' if filename.endswith('.gz') else 'r') as tar:
                    tar.extractall(temp_dir)
                # 删除压缩文件
                os.remove(filepath)
            elif filename.endswith('.zip'):
                import zipfile
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                os.remove(filepath)
            
            # 获取当前用户
            user = getattr(request, 'current_user', None)
            if not user:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'User not authenticated'
                }), 401
            
            # 添加包到发布
            package_id = container.release_service.add_package(
                release_id=release_id,
                content_type=content_type,
                source_dir=extracted_dir,
                extract_git=False,
                user_id=user.user_id
            )
            
            return jsonify({
                'package_id': package_id,
                'message': 'Package uploaded successfully'
            }), 201
        
        finally:
            # 清理临时文件
            shutil.rmtree(temp_dir, ignore_errors=True)
    
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


@releases_bp.route('', methods=['POST'])
@require_auth
def create_release():
    """创建发布草稿
    
    Request:
        {
            "resource_type": "BSP",
            "version": "1.0.0",
            "description": "string",
            "changelog": "string"
        }
    
    Response:
        {
            "release_id": "string",
            "status": "DRAFT",
            ...
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing request body'
            }), 400
        
        resource_type_str = data.get('resource_type')
        version = data.get('version')
        description = data.get('description')
        changelog = data.get('changelog')
        
        if not resource_type_str or not version:
            return jsonify({
                'error': 'Bad Request',
                'message': 'resource_type and version are required'
            }), 400
        
        # 转换资源类型
        resource_type = ResourceType.from_string(resource_type_str)
        
        # 获取当前用户
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'User not authenticated'
            }), 401
        
        # 创建发布
        from release_portal.initializer import create_container
        container = create_container()
        
        release = container.release_service.create_draft(
            resource_type=resource_type,
            version=version,
            publisher_id=user.user_id,
            description=description,
            changelog=changelog
        )
        
        return jsonify(release.to_dict()), 201
    
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


@releases_bp.route('/<release_id>/publish', methods=['POST'])
@require_auth
def publish_release(release_id: str):
    """发布版本
    
    Response:
        {
            "release": {...}
        }
    """
    try:
        from release_portal.initializer import create_container
        
        container = create_container()
        
        # 获取当前用户
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'User not authenticated'
            }), 401
        
        # 发布
        release = container.release_service.publish_release(
            release_id=release_id,
            user_id=user.user_id
        )
        
        return jsonify(release.to_dict()), 200
    
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


@releases_bp.route('/<release_id>/archive', methods=['POST'])
@require_auth
def archive_release(release_id: str):
    """归档版本
    
    Response:
        {
            "release": {...}
        }
    """
    try:
        from release_portal.initializer import create_container
        
        container = create_container()
        
        # 获取当前用户
        user = getattr(request, 'current_user', None)
        if not user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'User not authenticated'
            }), 401
        
        # 归档
        release = container.release_service.archive_release(
            release_id=release_id,
            user_id=user.user_id
        )
        
        return jsonify(release.to_dict()), 200
    
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
