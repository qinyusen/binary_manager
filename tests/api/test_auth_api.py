"""
认证 API 集成测试
"""

import pytest


class TestAuthAPI:
    """认证 API 测试类"""
    
    def test_login_success(self, client, test_users):
        """测试成功登录"""
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'admin123'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert 'user' in data
        assert data['user']['username'] == 'admin'
    
    def test_login_wrong_password(self, client, test_users):
        """测试错误密码登录"""
        response = client.post('/api/auth/login', json={
            'username': 'admin',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_login_nonexistent_user(self, client):
        """测试不存在的用户登录"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password'
        })
        
        assert response.status_code == 401
    
    def test_verify_token_valid(self, client, auth_tokens):
        """测试验证有效 token"""
        response = client.get('/api/auth/verify', headers={
            'Authorization': f'Bearer {auth_tokens["admin"]}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'admin'
    
    def test_verify_token_invalid(self, client):
        """测试验证无效 token"""
        response = client.get('/api/auth/verify', headers={
            'Authorization': 'Bearer invalid_token'
        })
        
        assert response.status_code == 401
    
    def test_verify_token_missing(self, client):
        """测试缺少 token 的验证请求"""
        response = client.get('/api/auth/verify')
        
        assert response.status_code == 401
    
    def test_logout_success(self, client, auth_tokens):
        """测试登出"""
        response = client.post('/api/auth/logout', headers={
            'Authorization': f'Bearer {auth_tokens["admin"]}'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
    
    def test_register_user_as_admin(self, client, auth_tokens):
        """测试管理员注册新用户"""
        response = client.post('/api/auth/register', 
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
            json={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'newpass123',
                'role_id': 'role_publisher'
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.get_json()
        assert 'user_id' in data or 'username' in data
    
    def test_register_user_as_non_admin(self, client, auth_tokens):
        """测试非管理员注册用户应该失败"""
        response = client.post('/api/auth/register',
            headers={'Authorization': f'Bearer {auth_tokens["publisher"]}'},
            json={
                'username': 'newuser2',
                'email': 'newuser2@example.com',
                'password': 'newpass123'
            }
        )
        
        assert response.status_code == 403
    
    def test_register_duplicate_username(self, client, auth_tokens):
        """测试注册重复用户名"""
        response = client.post('/api/auth/register',
            headers={'Authorization': f'Bearer {auth_tokens["admin"]}'},
            json={
                'username': 'admin',  # 已存在
                'email': 'another@example.com',
                'password': 'pass123'
            }
        )
        
        assert response.status_code == 400
