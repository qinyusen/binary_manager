#!/usr/bin/env python3
"""
快速测试脚本 - 验证 Release Portal 核心功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from release_portal.initializer import create_container, DatabaseInitializer
from release_portal.domain.value_objects import ResourceType, AccessLevel
from datetime import datetime, timedelta


def test_basic_functionality():
    """测试基本功能"""
    print("=" * 60)
    print("Release Portal 核心功能测试")
    print("=" * 60)
    
    # 1. 初始化
    print("\n[1] 初始化数据库...")
    db_path = './data/portal_test.db'
    initializer = DatabaseInitializer(db_path)
    initializer.initialize()
    print("✓ 数据库初始化成功")
    
    # 2. 创建容器
    print("\n[2] 创建服务容器...")
    container = create_container(db_path)
    print("✓ 服务容器创建成功")
    
    # 3. 测试用户注册
    print("\n[3] 测试用户注册...")
    try:
        admin = container.auth_service.register(
            username='test_admin',
            email='test_admin@diggo.com',
            password='test123',
            role_id='role_admin'
        )
        print(f"✓ 管理员注册成功: {admin.username}")
    except Exception as e:
        print(f"✗ 管理员注册失败: {e}")
        return False
    
    # 4. 测试登录
    print("\n[4] 测试登录...")
    try:
        token = container.auth_service.login('test_admin', 'test123')
        print("✓ 登录成功")
    except Exception as e:
        print(f"✗ 登录失败: {e}")
        return False
    
    # 5. 测试 Token 验证
    print("\n[5] 测试 Token 验证...")
    try:
        print(f"  生成的 Token: {token[:50]}...")
        
        # 测试 token 解析
        parts = token.split('.')
        print(f"  Token 部分: {len(parts)}")
        
        # 先测试 token 验证
        payload = container.auth_service.verify_token(token)
        print(f"  Token payload: {payload}")
        
        if payload:
            print(f"  Payload user_id: {payload.get('user_id')}")
        
        user = container.auth_service.get_user_from_token(token)
        if user:
            print(f"✓ Token 验证成功: {user.username}")
        else:
            print(f"✗ Token 验证失败: get_user_from_token 返回 None")
            return False
    except Exception as e:
        print(f"✗ Token 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 6. 测试许可证创建
    print("\n[6] 测试许可证创建...")
    try:
        license = container.license_service.create_license(
            organization='Test Org',
            access_level=AccessLevel.FULL_ACCESS,
            allowed_resource_types=[ResourceType.BSP, ResourceType.DRIVER],
            expires_at=datetime.now() + timedelta(days=30)
        )
        print(f"✓ 许可证创建成功: {license.license_id}")
    except Exception as e:
        print(f"✗ 许可证创建失败: {e}")
        return False
    
    # 7. 测试发布草稿创建
    print("\n[7] 测试发布草稿创建...")
    try:
        release = container.release_service.create_draft(
            resource_type=ResourceType.BSP,
            version='v1.0.0-test',
            publisher_id=user.user_id,
            description='Test BSP release'
        )
        print(f"✓ 发布草稿创建成功: {release.release_id}")
    except Exception as e:
        print(f"✗ 发布草稿创建失败: {e}")
        return False
    
    # 8. 测试查询发布
    print("\n[8] 测试查询发布...")
    try:
        releases = container.release_service.list_releases()
        print(f"✓ 查询发布成功: 找到 {len(releases)} 个发布")
    except Exception as e:
        print(f"✗ 查询发布失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("所有测试通过！ ✓")
    print("=" * 60)
    return True


if __name__ == '__main__':
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
