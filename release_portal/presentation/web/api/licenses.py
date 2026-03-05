"""
许可证管理 REST API
"""
from flask import Blueprint, request, jsonify
from ..auth_middleware import require_auth, require_role
from release_portal.domain.value_objects import AccessLevel, ResourceType
from datetime import datetime, timedelta

licenses_bp = Blueprint('licenses', __name__)


@licenses_bp.route('', methods=['GET'])
@require_auth
def list_licenses():
    """列出所有许可证
    
    Query Parameters:
        active_only: 仅返回激活的许可证（true/false）
    
    Response:
        {
            "licenses": [...]
        }
    """
    try:
        from release_portal.initializer import create_container
        
        container = create_container()
        
        # 获取查询参数
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        
        # 列出许可证
        licenses = container.license_service.list_licenses(active_only=active_only)
        
        # 转换为字典
        licenses_data = [license.to_dict() for license in licenses]
        
        return jsonify({
            'licenses': licenses_data,
            'count': len(licenses_data)
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@licenses_bp.route('/<license_id>', methods=['GET'])
@require_auth
def get_license(license_id: str):
    """获取许可证详情
    
    Response:
        {
            "license": {...}
        }
    """
    try:
        from release_portal.initializer import create_container
        
        container = create_container()
        license = container.license_service.get_license(license_id)
        
        if not license:
            return jsonify({
                'error': 'Not Found',
                'message': f'License {license_id} not found'
            }), 404
        
        return jsonify({
            'license': license.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@licenses_bp.route('', methods=['POST'])
@require_role('Admin')
def create_license():
    """创建许可证（仅管理员）
    
    Request:
        {
            "organization": "string",
            "access_level": "FULL_ACCESS",
            "allowed_resource_types": ["BSP", "DRIVER"],
            "expires_at": "ISO8601",
            "days": 365  // 可选，与 expires_at 二选一
        }
    
    Response:
        {
            "license_id": "string",
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
        
        organization = data.get('organization')
        access_level_str = data.get('access_level')
        allowed_resource_types_str = data.get('allowed_resource_types', [])
        expires_at_str = data.get('expires_at')
        days = data.get('days')
        
        if not all([organization, access_level_str, allowed_resource_types_str]):
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing required fields'
            }), 400
        
        # 转换参数
        access_level = AccessLevel.from_string(access_level_str)
        allowed_resource_types = [
            ResourceType.from_string(rt) if isinstance(rt, str) else rt
            for rt in allowed_resource_types_str
        ]
        
        # 处理过期时间
        expires_at = None
        if expires_at_str:
            expires_at = datetime.fromisoformat(expires_at_str)
        elif days:
            expires_at = datetime.now() + timedelta(days=days)
        
        # 创建许可证
        from release_portal.initializer import create_container
        container = create_container()
        
        license = container.license_service.create_license(
            organization=organization,
            access_level=access_level,
            allowed_resource_types=allowed_resource_types,
            expires_at=expires_at
        )
        
        return jsonify(license.to_dict()), 201
    
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


@licenses_bp.route('/<license_id>/revoke', methods=['POST'])
@require_role('Admin')
def revoke_license(license_id: str):
    """撤销许可证（仅管理员）
    
    Response:
        {
            "message": "License revoked successfully"
        }
    """
    try:
        from release_portal.initializer import create_container
        
        container = create_container()
        container.license_service.revoke_license(license_id)
        
        return jsonify({
            'message': 'License revoked successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@licenses_bp.route('/<license_id>/activate', methods=['POST'])
@require_role('Admin')
def activate_license(license_id: str):
    """激活许可证（仅管理员）
    
    Response:
        {
            "message": "License activated successfully"
        }
    """
    try:
        from release_portal.initializer import create_container
        
        container = create_container()
        container.license_service.activate_license(license_id)
        
        return jsonify({
            'message': 'License activated successfully'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@licenses_bp.route('/<license_id>/extend', methods=['POST'])
@require_role('Admin')
def extend_license(license_id: str):
    """延期许可证（仅管理员）
    
    Request:
        {
            "days": 30,           // 延期天数
            "date": "ISO8601"     // 或延期到指定日期
        }
    
    Response:
        {
            "license": {...}
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing request body'
            }), 400
        
        days = data.get('days')
        date_str = data.get('date')
        
        if not days and not date_str:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Either days or date is required'
            }), 400
        
        # 延期
        from release_portal.initializer import create_container
        container = create_container()
        
        if days:
            license = container.license_service.extend_license(license_id, days=days)
        else:
            # 计算天数
            target_date = datetime.fromisoformat(date_str)
            current_license = container.license_service.get_license(license_id)
            if not current_license:
                return jsonify({
                    'error': 'Not Found',
                    'message': f'License {license_id} not found'
                }), 404
            
            current_expires = current_license.expires_at or datetime.now()
            days = (target_date - current_expires).days
            license = container.license_service.extend_license(license_id, days=days)
        
        return jsonify(license.to_dict()), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500
