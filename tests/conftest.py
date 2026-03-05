"""
Release Portal V3 - 集成测试套件

测试框架：pytest
测试覆盖：
  - API 端点测试
  - Web UI 功能测试
  - 文件上传测试
  - 认证和权限测试
  - 端到端工作流测试

运行方式：
  # 运行所有测试
  pytest tests/

  # 运行特定测试文件
  pytest tests/api/test_auth_api.py

  # 运行带覆盖率的测试
  pytest --cov=release_portal tests/

  # 运行并显示详细输出
  pytest -v tests/
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """创建测试数据库路径"""
    return str(tmp_path_factory.mktemp("data") / "test_portal.db")


@pytest.fixture(scope="session")
def db_initializer(test_db_path):
    """初始化测试数据库"""
    from release_portal.initializer import DatabaseInitializer
    
    import os
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    initializer = DatabaseInitializer(test_db_path)
    initializer.initialize()
    
    return initializer


@pytest.fixture(scope="function")
def container(db_initializer, test_db_path):
    """创建服务容器（每个测试函数一个新实例）"""
    from release_portal.initializer import create_container
    
    container = create_container(test_db_path)
    return container


@pytest.fixture(scope="function")
def app(container, test_db_path):
    """创建 Flask 应用"""
    from release_portal.presentation.web.app import create_app
    
    app = create_app(test_db_path)
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    return app


@pytest.fixture(scope="function")
def client(app):
    """创建 Flask 测试客户端"""
    return app.test_client()


@pytest.fixture
def test_users(container):
    """创建测试用户"""
    users = {}
    
    # 管理员
    admin = container.auth_service.register(
        username='admin',
        email='admin@example.com',
        password='admin123',
        role_id='role_admin'
    )
    users['admin'] = admin
    
    # 发布者
    publisher = container.auth_service.register(
        username='publisher',
        email='publisher@example.com',
        password='pub123',
        role_id='role_publisher'
    )
    users['publisher'] = publisher
    
    # 客户
    customer = container.auth_service.register(
        username='customer',
        email='customer@example.com',
        password='cust123',
        role_id='role_customer'
    )
    users['customer'] = customer
    
    return users


@pytest.fixture
def auth_tokens(container, test_users):
    """获取测试用户的认证 token"""
    tokens = {}
    
    for role, user in test_users.items():
        token = container.auth_service.login(user.username, user.username.replace('admin', 'admin123').replace('publisher', 'pub123').replace('customer', 'cust123'))
        tokens[role] = token
    
    return tokens


@pytest.fixture
def auth_headers(auth_tokens):
    """获取带认证的请求头"""
    headers = {}
    for role, token in auth_tokens.items():
        headers[role] = {'Authorization': f'Bearer {token}'}
    
    return headers


def assert_success_response(response, status_code=200):
    """断言成功响应"""
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}: {response.data}"
    return response


def assert_error_response(response, status_code):
    """断言错误响应"""
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}"
    data = response.get_json()
    assert 'error' in data or 'message' in data
    return data


def get_json(response):
    """获取 JSON 响应"""
    assert response.content_type.startswith('application/json')
    return response.get_json()
