"""
发布 REST API
"""
from flask import Blueprint, request, jsonify, send_file
from ..auth_middleware import require_auth, require_role
from ...domain.value_objects import ResourceType, ContentType, ReleaseStatus

releases_bp = Blueprint('releases', __name__)


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
        from ...initializer import create_container
        
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
        from ...initializer import create_container
        
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
        from ...initializer import create_container
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
        from ...initializer import create_container
        
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
        from ...initializer import create_container
        
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
