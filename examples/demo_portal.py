#!/usr/bin/env python3
"""
示例脚本：演示如何使用 Release Portal API

这个脚本展示了如何：
1. 初始化数据库
2. 创建用户和许可证
3. 发布资源
4. 下载资源（根据权限）
"""

from release_portal.initializer import create_container, DatabaseInitializer
from release_portal.domain.value_objects import ResourceType, AccessLevel, ContentType
from datetime import datetime, timedelta


def main():
    print("=" * 60)
    print("地瓜机器人发布平台 V3 - 示例脚本")
    print("=" * 60)
    
    # 1. 初始化数据库
    print("\n[1] 初始化数据库...")
    initializer = DatabaseInitializer('./data/portal_demo.db')
    initializer.initialize()
    print("✓ 数据库初始化完成")
    
    # 创建服务容器
    container = create_container('./data/portal_demo.db')
    print("✓ 服务容器创建完成")
    
    # 2. 创建管理员账户
    print("\n[2] 创建管理员账户...")
    try:
        admin = container.auth_service.register(
            username='admin',
            email='admin@diggo.com',
            password='admin123',
            role_id='role_admin'
        )
        print(f"✓ 管理员账户创建成功: {admin.username}")
    except ValueError as e:
        print(f"! 管理员账户已存在: {e}")
        admin = container.user_repository.find_by_username('admin')
    
    # 3. 创建发布者账户
    print("\n[3] 创建发布者账户...")
    try:
        publisher = container.auth_service.register(
            username='engineer',
            email='engineer@diggo.com',
            password='engineer123',
            role_id='role_publisher'
        )
        print(f"✓ 发布者账户创建成功: {publisher.username}")
    except ValueError as e:
        print(f"! 发布者账户已存在: {e}")
        publisher = container.user_repository.find_by_username('engineer')
    
    # 4. 创建客户许可证
    print("\n[4] 创建客户许可证...")
    try:
        # 完全访问许可证
        full_license = container.license_service.create_license(
            organization='Premium Customer',
            access_level=AccessLevel.FULL_ACCESS,
            allowed_resource_types=[ResourceType.BSP, ResourceType.DRIVER, ResourceType.EXAMPLES],
            expires_at=datetime.now() + timedelta(days=365),
            metadata={'contact': 'premium@example.com'}
        )
        print(f"✓ 完全访问许可证创建成功: {full_license.license_id}")
        
        # 受限访问许可证
        binary_license = container.license_service.create_license(
            organization='Standard Customer',
            access_level=AccessLevel.BINARY_ACCESS,
            allowed_resource_types=[ResourceType.BSP, ResourceType.DRIVER],
            expires_at=datetime.now() + timedelta(days=180),
            metadata={'contact': 'standard@example.com'}
        )
        print(f"✓ 受限访问许可证创建成功: {binary_license.license_id}")
    except ValueError as e:
        print(f"! 许可证创建失败: {e}")
    
    # 5. 创建客户账户
    print("\n[5] 创建客户账户...")
    try:
        # Premium 客户
        premium_customer = container.auth_service.register(
            username='premium_user',
            email='premium@example.com',
            password='premium123',
            role_id='role_customer',
            license_id=full_license.license_id
        )
        print(f"✓ Premium 客户创建成功: {premium_customer.username}")
        print(f"  - 许可证: {premium_customer.license_id}")
        print(f"  - 访问级别: FULL_ACCESS")
    except ValueError as e:
        print(f"! Premium 客户已存在: {e}")
        premium_customer = container.user_repository.find_by_username('premium_user')
        license_premium = container.license_repository.find_by_id(premium_customer.license_id)
        print(f"  - 许可证: {license_premium.organization if license_premium else 'N/A'}")
    
    try:
        # Standard 客户
        standard_customer = container.auth_service.register(
            username='standard_user',
            email='standard@example.com',
            password='standard123',
            role_id='role_customer',
            license_id=binary_license.license_id
        )
        print(f"✓ Standard 客户创建成功: {standard_customer.username}")
        print(f"  - 许可证: {standard_customer.license_id}")
        print(f"  - 访问级别: BINARY_ACCESS")
    except ValueError as e:
        print(f"! Standard 客户已存在: {e}")
        standard_customer = container.user_repository.find_by_username('standard_user')
        license_standard = container.license_repository.find_by_id(standard_customer.license_id)
        print(f"  - 许可证: {license_standard.organization if license_standard else 'N/A'}")
    
    # 6. 模拟发布流程（使用发布者账户）
    print("\n[6] 创建发布草稿...")
    try:
        release = container.release_service.create_draft(
            resource_type=ResourceType.BSP,
            version='v1.0.0',
            publisher_id=publisher.user_id,
            description='地瓜机器人 BSP v1.0.0',
            changelog='初始版本发布'
        )
        print(f"✓ 发布草稿创建成功: {release.release_id}")
        print(f"  - 类型: {release.resource_type.value}")
        print(f"  - 版本: {release.version}")
        print(f"  - 状态: {release.status.value}")
    except ValueError as e:
        print(f"! 发布草稿创建失败: {e}")
    
    # 7. 演示权限检查
    print("\n[7] 演示权限检查...")
    
    # Premium 客户可以下载所有类型
    print(f"\nPremium 用户 ({premium_customer.username}):")
    print(f"  - 可下载 BSP 源码: {full_license.allows_content_type('SOURCE')}")
    print(f"  - 可下载 BSP 二进制: {full_license.allows_content_type('BINARY')}")
    print(f"  - 可下载 BSP 文档: {full_license.allows_content_type('DOCUMENT')}")
    
    # Standard 客户只能下载二进制和文档
    print(f"\nStandard 用户 ({standard_customer.username}):")
    print(f"  - 可下载 BSP 源码: {binary_license.allows_content_type('SOURCE')}")
    print(f"  - 可下载 BSP 二进制: {binary_license.allows_content_type('BINARY')}")
    print(f"  - 可下载 BSP 文档: {binary_license.allows_content_type('DOCUMENT')}")
    
    # 8. 列出所有许可证
    print("\n[8] 列出所有许可证...")
    licenses = container.license_service.list_licenses()
    for lic in licenses:
        print(f"  - {lic.organization} ({lic.access_level.value})")
        print(f"    资源类型: {', '.join([rt.value for rt in lic.allowed_resource_types])}")
        if lic.expires_at:
            print(f"    到期时间: {lic.expires_at.strftime('%Y-%m-%d')}")
    
    # 9. 列出所有用户
    print("\n[9] 列出所有用户...")
    users = container.user_repository.find_all()
    for user in users:
        print(f"  - {user.username} ({user.role.name})")
        if user.license_id:
            license = container.license_repository.find_by_id(user.license_id)
            print(f"    许可证: {license.organization if license else 'N/A'}")
    
    print("\n" + "=" * 60)
    print("示例脚本执行完成！")
    print("=" * 60)
    print("\n数据库文件: ./data/portal_demo.db")
    print("\n测试账户:")
    print("  管理员: admin / admin123")
    print("  发布者: engineer / engineer123")
    print("  Premium 客户: premium_user / premium123")
    print("  Standard 客户: standard_user / standard123")
    print("\n使用 CLI 进行测试:")
    print("  python -m release_portal.presentation.cli login --username admin")
    print("  python -m release_portal.presentation.cli list")
    print("=" * 60)


if __name__ == '__main__':
    main()
