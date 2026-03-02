"""
认证中间件
"""
from functools import wraps
from flask import request, jsonify
from ...shared import AuthenticationError


def require_auth(f):
    """要求用户认证的装饰器
    
    验证请求头中的 JWT Token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from ...initializer import create_container
        
        # 获取 Token
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Missing Authorization header'
            }), 401
        
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid Authorization header format'
            }), 401
        
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # 验证 Token
        container = create_container()
        try:
            user_info = container.auth_service.verify_token(token)
            if not user_info:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Invalid or expired token'
                }), 401
            
            # 获取完整用户信息
            user = container.auth_service.get_user_from_token(token)
            if not user:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'User not found'
                }), 401
            
            # 将用户信息添加到请求上下文
            request.current_user = user
            request.user_info = user_info
            
            return f(*args, **kwargs)
        
        except Exception as e:
            return jsonify({
                'error': 'Unauthorized',
                'message': str(e)
            }), 401
    
    return decorated_function


def require_role(*allowed_roles):
    """要求特定角色的装饰器
    
    Args:
        allowed_roles: 允许的角色名称列表
    """
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            user = getattr(request, 'current_user', None)
            
            if not user:
                return jsonify({
                    'error': 'Forbidden',
                    'message': 'User not authenticated'
                }), 403
            
            if user.role.name not in allowed_roles:
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'Insufficient permissions. Required role: {", ".join(allowed_roles)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_permission(resource: str):
    """要求特定权限的装饰器
    
    Args:
        resource: 资源操作名称（如 'publish', 'download'）
    """
    def decorator(f):
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            from ...domain.value_objects import Permission
            
            user = getattr(request, 'current_user', None)
            
            if not user:
                return jsonify({
                    'error': 'Forbidden',
                    'message': 'User not authenticated'
                }), 403
            
            # 检查用户是否有权限
            if not user.has_permission(resource):
                return jsonify({
                    'error': 'Forbidden',
                    'message': f'Permission denied: {resource}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
