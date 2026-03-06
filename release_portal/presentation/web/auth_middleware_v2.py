"""
认证中间件 - TDD重构版
精简代码，保持功能不变
"""
from functools import wraps
from flask import request, jsonify
from ...shared import AuthenticationError


def require_auth(f):
    """要求认证（简化版）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 验证 Token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Unauthorized', 'message': '缺少认证信息'}), 401
        
        # 验证用户
        from ...initializer import create_container
        container = create_container()
        
        try:
            user_info = container.auth_service.verify_token(auth_header[7:])
            if not user_info:
                return jsonify({'error': 'Unauthorized', 'message': 'Token无效或已过期'}), 401
            
            user = container.auth_service.get_user_from_token(auth_header[7:])
            if not user:
                return jsonify({'error': 'Unauthorized', 'message': '用户不存在'}), 401
            
            request.current_user = user
            return f(*args, **kwargs)
        
        except Exception:
            return jsonify({'error': 'Unauthorized', 'message': '认证失败'}), 401
    
    return decorated


def require_role(*allowed_roles):
    """要求特定角色（简化版）"""
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated(*args, **kwargs):
            user = getattr(request, 'current_user', None)
            if not user or user.role.name not in allowed_roles:
                return jsonify({'error': 'Forbidden', 'message': '权限不足'}), 403
            return f(*args, **kwargs)
        return decorated
    return decorator


def require_permission(resource: str):
    """要求特定权限（预留）"""
    return require_auth  # 暂时等同于 require_auth
