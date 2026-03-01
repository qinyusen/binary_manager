#!/usr/bin/env python3
"""
快速入门示例 - 地瓜机器人发布平台 V3

这个脚本演示了如何使用发布平台的基本功能。
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from release_portal.initializer import create_container, DatabaseInitializer
from release_portal.domain.value_objects import ResourceType, ContentType, AccessLevel
from datetime import datetime, timedelta
import tempfile
import shutil


def quick_start_example():
    """快速入门示例"""
    print("=" * 70)
    print("地瓜机器人发布平台 V3 - 快速入门示例")
    print("=" * 70)
    
    # 步骤 1: 初始化数据库
    print("\n[步骤 1] 初始化数据库...")
    db_path = "./data/quickstart.db"
    initializer = DatabaseInitializer(db_path)
    initializer.initialize()
    print(f"✓ 数据库初始化成功: {db_path}")
    
    # 创建容器
    container = create_container(db_path)
    print("✓ 服务容器创建成功")
    
    # 步骤 2: 创建用户
    print("\n[步骤 2] 创建用户...")
    
    # 创建发布者
    publisher = container.auth_service.register(
        username='publisher',
        email='publisher@example.com',
        password='pub123',
        role_id='role_publisher'
    )
    print(f"✓ 创建发布者: {publisher.username}")
    
    # 创建客户
    customer = container.auth_service.register(
        username='customer',
        email='customer@example.com',
        password='cust123',
        role_id='role_customer'
    )
    print(f"✓ 创建客户: {customer.username}")
    
    # 步骤 3: 登录
    print("\n[步骤 3] 用户登录...")
    publisher_token = container.auth_service.login('publisher', 'pub123')
    print(f"✓ 发布者登录成功")
    
    customer_token = container.auth_service.login('customer', 'cust123')
    print(f"✓ 客户登录成功")
    
    # 步骤 4: 创建许可证
    print("\n[步骤 4] 为客户创建许可证...")
    license = container.license_service.create_license(
        organization='客户公司',
        access_level=AccessLevel.BINARY_ACCESS,
        allowed_resource_types=[ResourceType.BSP],
        expires_at=datetime.now() + timedelta(days=365)
    )
    print(f"✓ 许可证创建成功: {license.license_id}")
    print(f"  - 组织: {license.organization}")
    print(f"  - 访问级别: {license.access_level.value}")
    print(f"  - 资源类型: {[rt.value for rt in license.allowed_resource_types]}")
    
    # 分配许可证给客户
    container.auth_service.assign_license_to_user(customer.user_id, license.license_id)
    print(f"✓ 许可证已分配给客户: {customer.username}")
    
    # 步骤 5: 发布 BSP
    print("\n[步骤 5] 发布 BSP...")
    release = container.release_service.create_draft(
        resource_type=ResourceType.BSP,
        version='1.0.0',
        publisher_id=publisher.user_id,
        description='地瓜机器人 BSP v1.0.0',
        changelog='初始版本发布'
    )
    print(f"✓ 创建发布草稿: {release.release_id}")
    print(f"  - 资源类型: {release.resource_type.value}")
    print(f"  - 版本: {release.version}")
    print(f"  - 状态: {release.status.value}")
    
    # 创建临时测试文件
    test_dir = tempfile.mkdtemp()
    try:
        # 创建测试文件
        test_file = Path(test_dir) / "README.md"
        test_file.write_text("# BSP v1.0.0\n\n这是地瓜机器人 BSP 的第一个版本。")
        
        # 添加文档包
        package_id = container.release_service.add_package(
            release_id=release.release_id,
            content_type=ContentType.DOCUMENT,
            source_dir=test_dir,
            extract_git=False,
            user_id=publisher.user_id
        )
        print(f"✓ 添加文档包: {package_id}")
        
        # 添加二进制包
        package_id = container.release_service.add_package(
            release_id=release.release_id,
            content_type=ContentType.BINARY,
            source_dir=test_dir,
            extract_git=False,
            user_id=publisher.user_id
        )
        print(f"✓ 添加二进制包: {package_id}")
        
        # 发布版本
        release = container.release_service.publish_release(
            release_id=release.release_id,
            user_id=publisher.user_id
        )
        print(f"✓ 发布成功: {release.release_id}")
    
    finally:
        # 清理临时目录
        shutil.rmtree(test_dir)
    
    # 步骤 6: 客户查看和下载
    print("\n[步骤 6] 客户查看可下载的内容...")
    
    # 获取可下载的包
    packages = container.download_service.get_available_packages(
        user_id=customer.user_id,
        release_id=release.release_id
    )
    
    print(f"✓ 可下载的包数量: {len(packages)}")
    for pkg in packages:
        print(f"  - {pkg['content_type']}: {pkg['package_name']} v{pkg['version']}")
    
    # 步骤 7: 列出所有发布
    print("\n[步骤 7] 列出所有发布...")
    all_releases = container.release_service.list_releases()
    print(f"✓ 总发布数量: {len(all_releases)}")
    for rel in all_releases:
        print(f"  - {rel.release_id}: {rel.resource_type.value} v{rel.version} ({rel.status.value})")
    
    # 步骤 8: 查看许可证信息
    print("\n[步骤 8] 查看许可证信息...")
    license_info = container.download_service.get_user_license_info(customer.user_id)
    if license_info:
        print(f"✓ 客户许可证信息:")
        print(f"  - 许可证 ID: {license_info['license_id']}")
        print(f"  - 组织: {license_info['organization']}")
        print(f"  - 访问级别: {license_info['access_level']}")
        print(f"  - 资源类型: {', '.join(license_info['allowed_resource_types'])}")
        print(f"  - 过期时间: {license_info['expires_at']}")
        print(f"  - 状态: {'激活' if license_info['is_active'] else '未激活'}")
    
    print("\n" + "=" * 70)
    print("✓ 快速入门示例完成！")
    print("=" * 70)
    
    print("\n后续步骤:")
    print("  1. 使用 CLI 工具: release-portal --help")
    print("  2. 查看完整文档: USER_MANUAL.md")
    print("  3. 运行完整示例: python examples/demo_portal.py")
    print("\n测试账户:")
    print("  发布者: publisher / pub123")
    print("  客户: customer / cust123")
    print(f"\n数据库文件: {db_path}")


if __name__ == '__main__':
    try:
        quick_start_example()
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
