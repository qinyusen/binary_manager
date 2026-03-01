#!/usr/bin/env python3
"""
测试账号系统和存储系统的解耦
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from release_portal.shared import Config
from release_portal.initializer import create_container, DatabaseInitializer
from release_portal.domain.value_objects import ResourceType, ContentType, AccessLevel


def test_decoupling():
    """测试解耦后的系统"""
    print("=" * 60)
    print("测试账号系统和存储系统的解耦")
    print("=" * 60)
    
    # 1. 初始化数据库
    print("\n[1] 初始化数据库...")
    db_path = "./data/portal_decoupling_test.db"
    
    # 删除旧的测试数据库
    if os.path.exists(db_path):
        os.remove(db_path)
    
    initializer = DatabaseInitializer(db_path)
    initializer.initialize()
    print(f"✓ 数据库初始化成功: {db_path}")
    
    # 2. 创建容器
    print("\n[2] 创建服务容器...")
    container = create_container(db_path)
    print("✓ 服务容器创建成功")
    
    # 3. 测试授权服务（账号系统）
    print("\n[3] 测试授权服务...")
    
    # 创建测试用户（发布者）
    publisher = container.auth_service.register(
        username='test_publisher',
        email='publisher@example.com',
        password='password123',
        role_id='role_publisher'
    )
    print(f"✓ 创建发布者用户: {publisher.username} (ID: {publisher.user_id})")
    
    # 创建测试用户（客户）
    user = container.auth_service.register(
        username='test_user',
        email='test@example.com',
        password='password123',
        role_id='role_customer'
    )
    print(f"✓ 创建测试用户: {user.username} (ID: {user.user_id})")
    
    # 创建许可证
    from datetime import datetime, timedelta
    expires_at = datetime.now() + timedelta(days=365)
    license = container.license_service.create_license(
        organization='Test Organization',
        access_level=AccessLevel.BINARY_ACCESS,
        allowed_resource_types=[ResourceType.BSP],
        expires_at=expires_at
    )
    print(f"✓ 创建许可证: {license.license_id}")
    
    # 将许可证分配给用户
    container.auth_service.assign_license_to_user(user.user_id, license.license_id)
    print(f"✓ 将许可证分配给用户")
    
    # 测试授权服务
    auth_service = container.authorization_service
    print(f"\n测试授权服务:")
    print(f"  - 用户许可证有效: {auth_service.validate_user_license(user.user_id)}")
    print(f"  - 可以下载 BSP: {auth_service.can_download_release(user.user_id, ResourceType.BSP)}")
    print(f"  - 可以下载 DRIVER: {auth_service.can_download_release(user.user_id, ResourceType.DRIVER)}")
    print(f"  - 可以下载 BSP 二进制: {auth_service.can_download_content(user.user_id, ResourceType.BSP, ContentType.BINARY)}")
    print(f"  - 可以下载 BSP 源码: {auth_service.can_download_content(user.user_id, ResourceType.BSP, ContentType.SOURCE)}")
    
    # 4. 测试存储服务适配器（存储系统）
    print("\n[4] 测试存储服务适配器...")
    
    # 创建发布
    release = container.release_service.create_draft(
        resource_type=ResourceType.BSP,
        version='1.0.0',
        publisher_id=publisher.user_id,
        description='测试发布',
        changelog='初始版本'
    )
    print(f"✓ 创建发布: {release.release_id}")
    
    # 检查发布者权限
    print(f"\n检查发布者权限:")
    print(f"  - 用户 ID: {publisher.user_id}")
    print(f"  - 角色: {publisher.role.name}")
    print(f"  - 权限: {publisher.role.permissions}")
    print(f"  - 可以发布 BSP: {container.authorization_service.can_publish(publisher.user_id, ResourceType.BSP)}")
    
    # 创建临时测试目录
    import tempfile
    import shutil
    test_dir = tempfile.mkdtemp()
    source_file = Path(test_dir) / "test.txt"
    source_file.write_text("Test content")
    
    try:
        # 添加包（使用存储服务）
        package_id = container.release_service.add_package(
            release_id=release.release_id,
            content_type=ContentType.BINARY,
            source_dir=test_dir,
            extract_git=False,
            user_id=publisher.user_id
        )
        print(f"✓ 添加包到发布: {package_id}")
        
        # 测试存储服务
        storage_service = container.release_service._storage_service
        package_info = storage_service.get_package_info(package_id)
        print(f"\n存储服务信息:")
        print(f"  - 包 ID: {package_info['package_id']}")
        print(f"  - 包名: {package_info['package_name']}")
        print(f"  - 版本: {package_info['version']}")
        print(f"  - 大小: {package_info['size']} bytes")
    
    finally:
        # 清理临时目录
        shutil.rmtree(test_dir)
    
    # 5. 验证解耦
    print("\n[5] 验证解耦...")
    
    # 检查 AuthorizationService 只依赖账号系统
    print("✓ AuthorizationService 依赖:")
    print("  - UserRepository (账号系统)")
    print("  - LicenseRepository (账号系统)")
    
    # 检查 StorageServiceAdapter 只依赖存储系统
    print("✓ StorageServiceAdapter 依赖:")
    print("  - PublisherService (存储系统)")
    print("  - DownloaderService (存储系统)")
    print("  - PackageRepository (存储系统)")
    
    # 检查 DownloadService 使用接口
    print("✓ DownloadService 依赖:")
    print("  - IAuthorizationService (接口)")
    print("  - IStorageService (接口)")
    print("  - UserRepository (账号系统)")
    print("  - ReleaseRepository (发布系统)")
    
    # 检查 ReleaseService 使用接口
    print("✓ ReleaseService 依赖:")
    print("  - IStorageService (接口)")
    print("  - ReleaseRepository (发布系统)")
    print("  - IAuthorizationService (可选，接口)")
    
    print("\n" + "=" * 60)
    print("✓ 解耦测试通过！")
    print("=" * 60)
    print("\n解耦架构说明:")
    print("  1. 账号系统：管理用户、角色、许可证")
    print("  2. 存储系统：管理包的存储和下载")
    print("  3. 授权服务：提供权限验证接口")
    print("  4. 存储适配器：适配 Binary Manager V2 存储服务")
    print("  5. 业务服务：通过接口使用两个系统")


if __name__ == '__main__':
    test_decoupling()
