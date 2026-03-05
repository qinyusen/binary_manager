"""
认证 REST API
"""
from flask import Blueprint, request, jsonify
from ....shared import AuthenticationError, ValidationError

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录
    
    Request:
        {
            "username": "string",
            "password": "string"
        }
    
    Response:
        {
            "token": "jwt_token",
            "user": {
                "user_id": "string",
                "username": "string",
                "email": "string",
                "role": {
                    "role_id": "string",
                    "name": "string",
                    "description": "string"
                }
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Missing request body'
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'error': 'Bad Request',
                'message': 'Username and password are required'
            }), 400
        
        # 登录
        from ...initializer import create_container
        container = create_container()
        
        token = container.auth_service.login(username, password)
        
        # 获取用户信息
        user_info = container.auth_service.verify_token(token)
        user = container.auth_service.get_user_from_token(token)
        
        return jsonify({
            'token': token,
            'user': {
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'role': {
                    'role_id': user.role.role_id,
                    'name': user.role.name,
                    'description': user.role.description
                }
            }
        }), 200
    
    except ValueError as e:
        return jsonify({
            'error': 'Unauthorized',
            'message': str(e)
        }), 401
    except Exception as e:
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500


@auth_bp.route('/verify', methods=['GET'])
def verify_token():
    """验证 Token 有效性"""
    from release_portal.presentation.web.auth_middleware import require_auth
    
    @require_auth
    def _verify():
        """验证 Token 有效性
        
        Headers:
            Authorization: Bearer <token>
        
        Response:
            {
                "valid": true,
                "user": {
                    "user_id": "string",
                    "username": "string",
                    "email": "string",
                    "role": {...}
                }
            }
        """
        try:
            user = getattr(request, 'current_user', None)
            
            if not user:
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'User not found'
                }), 401
            
            return jsonify({
                'valid': True,
                'user': {
                    'user_id': user.user_id,
                    'username': user.username,
                    'email': user.email,
                    'role': {
                        'role_id': user.role.role_id,
                        'name': user.role.name,
                        'description': user.role.description
                    }
                }
            }), 200
        
        except Exception as e:
            return jsonify({
                'error': 'Internal Server Error',
                'message': str(e)
            }), 500
    
    return _verify()


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    from release_portal.presentation.web.auth_middleware import require_auth
    
    @require_auth
    def _logout():
        """用户登出（客户端删除 Token）
        
        Headers:
            Authorization: Bearer <token>
        
        Response:
            {
                "message": "Logged out successfully"
            }
        """
        # 在 JWT 无状态场景下，登出主要由客户端处理（删除 Token）
        # 这里可以添加 Token 黑名单逻辑（如果需要）
        
        return jsonify({
            'message': 'Logged out successfully'
        }), 200
    
    return _logout()


@auth_bp.route('/register', methods=['POST'])
def register():
    """注册新用户"""
    from release_portal.presentation.web.auth_middleware import require_role
    
    @require_role('Admin')
    def _register():
        """注册新用户（仅管理员）
        
        Headers:
            Authorization: Bearer <token>
        
        Request:
            {
                "username": "string",
                "email": "string",
                "password": "string",
                "role_id": "string"
            }
        
        Response:
            {
                "user_id": "string",
                "username": "string",
                "email": "string",
                "role": {...}
            }
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Missing request body'
                }), 400
            
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            role_id = data.get('role_id')
            
            if not all([username, email, password, role_id]):
                return jsonify({
                    'error': 'Bad Request',
                    'message': 'Missing required fields'
                }), 400
            
            # 注册用户
            from ...initializer import create_container
            container = create_container()
            
            user = container.auth_service.register(
                username=username,
                email=email,
                password=password,
                role_id=role_id
            )
            
            return jsonify({
                'user_id': user.user_id,
                'username': user.username,
                'email': user.email,
                'role': {
                    'role_id': user.role.role_id,
                    'name': user.role.name,
                    'description': user.role.description
                }
            }), 201
        
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
    
    return _register()
