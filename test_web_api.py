"""
测试 Web API

运行方式：
python test_web_api.py
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from release_portal.initializer import create_container, DatabaseInitializer


def test_web_api():
    """测试 Web API"""
    print("=" * 60)
    print("测试 Release Portal Web API")
    print("=" * 60)
    
    # 1. 初始化数据库
    print("\n[1] 初始化数据库...")
    db_path = "./data/portal_web_test.db"
    
    import os
    if os.path.exists(db_path):
        os.remove(db_path)
    
    initializer = DatabaseInitializer(db_path)
    initializer.initialize()
    print(f"✓ 数据库初始化成功: {db_path}")
    
    # 2. 创建容器
    print("\n[2] 创建服务容器...")
    container = create_container(db_path)
    print("✓ 服务容器创建成功")
    
    # 3. 创建测试用户
    print("\n[3] 创建测试用户...")
    admin = container.auth_service.register(
        username='admin',
        email='admin@example.com',
        password='admin123',
        role_id='role_admin'
    )
    print(f"✓ 创建管理员: {admin.username}")
    
    publisher = container.auth_service.register(
        username='publisher',
        email='publisher@example.com',
        password='pub123',
        role_id='role_publisher'
    )
    print(f"✓ 创建发布者: {publisher.username}")
    
    # 4. 测试认证 API
    print("\n[4] 测试认证 API...")
    token = container.auth_service.login('admin', 'admin123')
    print(f"✓ 登录成功，Token: {token[:50]}...")
    
    # 5. 测试发布 API
    print("\n[5] 测试发布 API...")
    from release_portal.domain.value_objects import ResourceType
    
    release = container.release_service.create_draft(
        resource_type=ResourceType.BSP,
        version='1.0.0',
        publisher_id=admin.user_id,
        description='测试发布',
        changelog='初始版本'
    )
    print(f"✓ 创建发布: {release.release_id}")
    
    # 6. 测试许可证 API
    print("\n[6] 测试许可证 API...")
    from release_portal.domain.value_objects import AccessLevel
    from datetime import datetime, timedelta
    
    license = container.license_service.create_license(
        organization='测试公司',
        access_level=AccessLevel.FULL_ACCESS,
        allowed_resource_types=[ResourceType.BSP],
        expires_at=datetime.now() + timedelta(days=365)
    )
    print(f"✓ 创建许可证: {license.license_id}")
    
    print("\n" + "=" * 60)
    print("✓ Web API 测试完成！")
    print("=" * 60)
    
    print("\n启动 Web 服务器：")
    print("  export FLASK_APP=release_portal.presentation.web.app")
    print("  export FLASK_ENV=development")
    print("  flask run --port 5000")
    print("\n然后访问：")
    print("  http://localhost:5000")
    print("\n测试账户：")
    print("  管理员: admin / admin123")
    print("  发布者: publisher / pub123")


if __name__ == '__main__':
    try:
        test_web_api()
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
