#!/usr/bin/env python3
"""
Binary Manager V2 使用示例
演示如何使用Binary Manager V2的API进行发布和下载操作
"""
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from binary_manager_v2.application.publisher_service import PublisherService
from binary_manager_v2.application.downloader_service import DownloaderService
from binary_manager_v2.application.group_service import GroupService
from binary_manager_v2.infrastructure.database.sqlite_package_repository import SQLitePackageRepository
from binary_manager_v2.infrastructure.database.sqlite_group_repository import SQLiteGroupRepository
from binary_manager_v2.infrastructure.storage.local_storage import LocalStorage


def example_1_publish_simple_app():
    """示例1: 发布simple_app"""
    print("\n" + "="*60)
    print("示例1: 发布 simple_app")
    print("="*60)
    
    # 创建服务实例
    publisher = PublisherService(
        storage_path="./releases",
        db_path="./binary_manager_v2/database/binary_manager.db"
    )
    
    # 发布应用
    source_dir = "./examples/simple_app"
    package_name = "simple_app"
    version = "1.0.0"
    
    try:
        result = publisher.publish(
            source_dir=source_dir,
            package_name=package_name,
            version=version,
            description="Simple Calculator Application"
        )
        
        package = result['package']
        print(f"✅ 发布成功!")
        print(f"   包名: {package.package_name}")
        print(f"   版本: {package.version}")
        print(f"   文件数: {package.file_count}")
        print(f"   大小: {package.archive_size} 字节")
        if package.git_info:
            print(f"   Git提交: {package.git_info.commit_short}")
        
    except Exception as e:
        print(f"❌ 发布失败: {e}")
        import traceback
        traceback.print_exc()


def example_2_list_packages():
    """示例2: 列出所有包"""
    print("\n" + "="*60)
    print("示例2: 列出所有包")
    print("="*60)
    
    package_repo = SQLitePackageRepository(db_path="./binary_manager_v2/database/binary_manager.db")
    
    try:
        packages = package_repo.find_all()
        print(f"✅ 找到 {len(packages)} 个包:\n")
        
        for pkg in packages:
            print(f"  📦 {pkg.package_name} v{pkg.version}")
            print(f"     文件: {len(pkg.files)} 个")
            print(f"     大小: {pkg.archive_size} 字节")
            if pkg.git_info:
                print(f"     Git: {pkg.git_info.branch} - {pkg.git_info.commit_short}")
            print()
            
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()


def example_3_download_package():
    """示例3: 下载包"""
    print("\n" + "="*60)
    print("示例3: 下载包")
    print("="*60)
    
    downloader = DownloaderService(
        storage_path="./releases",
        db_path="./binary_manager_v2/database/binary_manager.db"
    )
    
    package_name = "simple_app"
    version = "1.0.0"
    output_path = "./test_downloads/simple_app"
    
    try:
        result = downloader.download(
            package_name=package_name,
            version=version,
            output_path=output_path,
            verify=True
        )
        
        print(f"✅ 下载成功!")
        print(f"   结果: {result}")
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        import traceback
        traceback.print_exc()


def example_4_create_group():
    """示例4: 创建包组"""
    print("\n" + "="*60)
    print("示例4: 创建包组")
    print("="*60)
    
    group_service = GroupService(
        db_path="./binary_manager_v2/database/binary_manager.db"
    )
    
    group_name = "demo_environment"
    version = "1.0.0"
    packages = [
        {"package_name": "simple_app", "version": "1.0.0"}
    ]
    
    try:
        result = group_service.create_group(
            group_name=group_name,
            version=version,
            packages=packages
        )
        
        print(f"✅ 组创建成功!")
        print(f"   结果: {result}")
        
    except Exception as e:
        print(f"❌ 组创建失败: {e}")
        import traceback
        traceback.print_exc()


def example_5_search_package():
    """示例5: 搜索包"""
    print("\n" + "="*60)
    print("示例5: 搜索包")
    print("="*60)
    
    package_repo = SQLitePackageRepository(db_path="./binary_manager_v2/database/binary_manager.db")
    
    package_name = "simple_app"
    
    try:
        # 查找特定版本
        pkg = package_repo.find_by_name_and_version(
            name=package_name,
            version="1.0.0"
        )
        
        if pkg:
            print(f"✅ 找到包:")
            print(f"   名称: {pkg.package_name}")
            print(f"   版本: {pkg.version}")
            print(f"   发布者ID: {pkg.publisher_id}")
            print(f"   文件列表:")
            for f in pkg.files:
                print(f"     - {f.path} ({f.size} 字节)")
                print(f"       SHA256: {f.hash}")
        else:
            print("❌ 未找到包")
            
    except Exception as e:
        print(f"❌ 搜索失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("Binary Manager V2 使用示例")
    print("="*60)
    
    # 运行示例
    example_1_publish_simple_app()
    example_2_list_packages()
    # example_3_download_package()  # 可选：测试下载
    example_4_create_group()
    example_5_search_package()
    
    print("\n" + "="*60)
    print("所有示例运行完成!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
