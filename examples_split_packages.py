#!/usr/bin/env python3
"""
Binary Manager V2 - 分包发布示例

演示如何将一个项目的不同部分（二进制、头文件、文档）分开发布，
但通过相同的版本号关联，并支持独立下载。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from binary_manager_v2.application.publisher_service import PublisherService
from binary_manager_v2.application.downloader_service import DownloaderService
from binary_manager_v2.application.group_service import GroupService
from binary_manager_v2.infrastructure.database.sqlite_package_repository import SQLitePackageRepository
from binary_manager_v2.infrastructure.storage.local_storage import LocalStorage
import tempfile
import shutil


def create_sample_project_structure():
    """创建示例项目结构"""
    tmp_dir = tempfile.mkdtemp(prefix="my_project_")
    base_path = Path(tmp_dir)
    
    # 创建二进制包目录
    bin_path = base_path / "my_project-bin"
    bin_path.mkdir(parents=True)
    (bin_path / "README.md").write_text("# My Project Binaries\n\nBinary files for My Project v1.0.0")
    (bin_path / "libmyproject.so").write_text("ELF Binary content")
    (bin_path / "myproject").write_text("ELF Executable content")
    
    # 创建头文件包目录
    headers_path = base_path / "my_project-headers"
    headers_path.mkdir(parents=True)
    (headers_path / "README.md").write_text("# My Project Headers\n\nHeader files for My Project v1.0.0")
    (headers_path / "include").mkdir()
    (headers_path / "include" / "myproject.h").write_text("""
#ifndef MYPROJECT_H
#define MYPROJECT_H

void myproject_init(void);
void myproject_cleanup(void);

#endif
""")
    (headers_path / "include" / "myproject_types.h").write_text("""
#ifndef MYPROJECT_TYPES_H
#define MYPROJECT_TYPES_H

typedef struct {
    int id;
    char name[64];
} myproject_t;

#endif
""")
    
    # 创建文档包目录
    docs_path = base_path / "my_project-docs"
    docs_path.mkdir(parents=True)
    (docs_path / "README.md").write_text("# My Project Documentation\n\nDocumentation for My Project v1.0.0")
    (docs_path / "manual.pdf").write_text("%PDF-1.4 fake pdf content")
    (docs_path / "api_reference.html").write_text("<html><body>API Reference</body></html>")
    (docs_path / "examples").mkdir()
    (docs_path / "examples" / "example1.c").write_text("// Example code 1")
    (docs_path / "examples" / "example2.c").write_text("// Example code 2")
    
    return tmp_dir, bin_path, headers_path, docs_path


def example_1_separate_publishing():
    """示例1: 分开发布不同部分"""
    print("\n" + "="*70)
    print("示例1: 分包发布 - 分别发布二进制、头文件、文档")
    print("="*70)
    
    publisher = PublisherService(
        storage_path="./releases",
        db_path="./binary_manager_v2/database/binary_manager.db"
    )
    
    tmp_dir, bin_path, headers_path, docs_path = create_sample_project_structure()
    
    try:
        # 发布二进制包
        print("\n📦 发布二进制包...")
        result1 = publisher.publish(
            source_dir=str(bin_path),
            package_name="my_project-bin",
            version="1.0.0",
            description="My Project v1.0.0 - Binaries"
        )
        print(f"   ✅ 二进制包发布成功: {result1['package'].package_name} v{result1['package'].version}")
        
        # 发布头文件包
        print("\n📦 发布头文件包...")
        result2 = publisher.publish(
            source_dir=str(headers_path),
            package_name="my_project-headers",
            version="1.0.0",
            description="My Project v1.0.0 - Headers"
        )
        print(f"   ✅ 头文件包发布成功: {result2['package'].package_name} v{result2['package'].version}")
        
        # 发布文档包
        print("\n📦 发布文档包...")
        result3 = publisher.publish(
            source_dir=str(docs_path),
            package_name="my_project-docs",
            version="1.0.0",
            description="My Project v1.0.0 - Documentation"
        )
        print(f"   ✅ 文档包发布成功: {result3['package'].package_name} v{result3['package'].version}")
        
        print("\n✅ 所有包发布完成！")
        print("   三个包使用相同的版本号 1.0.0，但可以独立管理和下载")
        
    finally:
        # 清理临时目录
        shutil.rmtree(tmp_dir, ignore_errors=True)


def example_2_independent_download():
    """示例2: 独立下载不同部分"""
    print("\n" + "="*70)
    print("示例2: 独立下载 - 分别下载需要的部分")
    print("="*70)
    
    downloader = DownloaderService(
        storage_path="./releases",
        db_path="./binary_manager_v2/database/binary_manager.db"
    )
    
    # 场景1: 只需要运行程序，下载二进制包
    print("\n📥 场景1: 用户只需要运行程序")
    print("   下载: my_project-bin:1.0.0")
    
    try:
        output_path = Path("./test_downloads/bin_only")
        result = downloader.download_by_name_version(
            package_name="my_project-bin",
            version="1.0.0",
            output_dir=str(output_path)
        )
        print(f"   ✅ 下载成功: {output_path}")
        print(f"   📄 包含: {list(output_path.glob('*'))}")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    # 场景2: 需要开发，下载二进制+头文件
    print("\n📥 场景2: 开发者需要编译自己的代码")
    print("   下载: my_project-bin:1.0.0 + my_project-headers:1.0.0")
    
    try:
        output_path1 = Path("./test_downloads/dev_env")
        result1 = downloader.download_by_name_version(
            package_name="my_project-bin",
            version="1.0.0",
            output_dir=str(output_path1 / "bin")
        )
        
        result2 = downloader.download_by_name_version(
            package_name="my_project-headers",
            version="1.0.0",
            output_dir=str(output_path1 / "headers")
        )
        print(f"   ✅ 下载成功: {output_path1}")
        print(f"   📄 二进制: {list((output_path1 / 'bin').glob('*'))}")
        print(f"   📄 头文件: {list((output_path1 / 'headers').glob('*'))}")
    except Exception as e:
        print(f"   ⚠️  {e}")
    
    # 场景3: 需要完整文档
    print("\n📥 场景3: 技术写作者需要文档")
    print("   下载: my_project-docs:1.0.0")
    
    try:
        output_path = Path("./test_downloads/docs_only")
        result = downloader.download_by_name_version(
            package_name="my_project-docs",
            version="1.0.0",
            output_dir=str(output_path)
        )
        print(f"   ✅ 下载成功: {output_path}")
        print(f"   📄 包含: {list(output_path.glob('*'))}")
    except Exception as e:
        print(f"   ⚠️  {e}")


def example_3_version_matching():
    """示例3: 通过Group管理版本匹配"""
    print("\n" + "="*70)
    print("示例3: 版本匹配 - 使用Group管理同一版本的多个包")
    print("="*70)
    
    group_service = GroupService(
        db_path="./binary_manager_v2/database/binary_manager.db"
    )
    
    # 创建完整环境组（包含所有部分）
    print("\n🔧 创建完整开发环境组...")
    result = group_service.create_group(
        group_name="my_project_full",
        version="1.0.0",
        packages=[
            {"package_name": "my_project-bin", "version": "1.0.0"},
            {"package_name": "my_project-headers", "version": "1.0.0"},
            {"package_name": "my_project-docs", "version": "1.0.0"}
        ]
    )
    print(f"   ✅ 组创建成功: {result}")
    
    # 创建运行时环境组（只需要二进制）
    print("\n🔧 创建运行时环境组...")
    result = group_service.create_group(
        group_name="my_project_runtime",
        version="1.0.0",
        packages=[
            {"package_name": "my_project-bin", "version": "1.0.0"}
        ]
    )
    print(f"   ✅ 组创建成功: {result}")
    
    # 创建开发环境组（二进制+头文件）
    print("\n🔧 创建开发环境组...")
    result = group_service.create_group(
        group_name="my_project_dev",
        version="1.0.0",
        packages=[
            {"package_name": "my_project-bin", "version": "1.0.0"},
            {"package_name": "my_project-headers", "version": "1.0.0"}
        ]
    )
    print(f"   ✅ 组创建成功: {result}")
    
    print("\n💡 使用场景:")
    print("   - my_project_full:  完整安装（二进制+头文件+文档）")
    print("   - my_project_runtime: 生产部署（仅二进制）")
    print("   - my_project_dev:     开发环境（二进制+头文件）")


def example_4_version_query():
    """示例4: 查询特定版本的所有部分"""
    print("\n" + "="*70)
    print("示例4: 版本查询 - 查找特定版本的所有相关包")
    print("="*70)
    
    package_repo = SQLitePackageRepository(
        db_path="./binary_manager_v2/database/binary_manager.db"
    )
    
    version = "1.0.0"
    print(f"\n🔍 查找 my_project 系列包的版本 {version}:")
    
    # 查找所有相关包
    packages = package_repo.find_all()
    my_project_packages = [
        p for p in packages 
        if str(p.package_name).startswith("my_project-") and str(p.version) == version
    ]
    
    print(f"\n找到 {len(my_project_packages)} 个包:")
    for pkg in my_project_packages:
        pkg_type = str(pkg.package_name).split("-")[1].capitalize()
        print(f"\n  📦 {pkg.package_name}")
        print(f"     类型: {pkg_type}")
        print(f"     版本: {pkg.version}")
        print(f"     大小: {pkg.archive_size} 字节")
        print(f"     文件数: {pkg.file_count}")


def example_5_partial_upgrade():
    """示例5: 部分升级"""
    print("\n" + "="*70)
    print("示例5: 部分升级 - 只升级特定部分")
    print("="*70)
    
    publisher = PublisherService(
        storage_path="./releases",
        db_path="./binary_manager_v2/database/binary_manager.db"
    )
    
    print("\n📀 发布版本 1.0.1 - 只更新头文件（添加新API）")
    
    tmp_dir = tempfile.mkdtemp(prefix="my_project_")
    headers_path = Path(tmp_dir) / "my_project-headers"
    headers_path.mkdir(parents=True)
    
    try:
        # 添加新的头文件
        (headers_path / "README.md").write_text("# My Project Headers\n\nHeader files for My Project v1.0.1")
        (headers_path / "include").mkdir()
        (headers_path / "include" / "myproject.h").write_text("/* v1.0.1 - Updated */")
        (headers_path / "include" / "myproject_v2.h").write_text("/* New API in v1.0.1 */")
        
        # 发布新版本的头文件
        result = publisher.publish(
            source_dir=str(headers_path),
            package_name="my_project-headers",
            version="1.0.1",
            description="My Project v1.0.1 - Headers (New API)"
        )
        
        print(f"   ✅ 头文件包升级成功: {result['package'].package_name} v{result['package'].version}")
        
        print("\n💡 现在有两个版本可用:")
        print("   - my_project-bin:1.0.0      (未变化)")
        print("   - my_project-headers:1.0.0  (旧版本)")
        print("   - my_project-headers:1.0.1  (新版本，包含新API)")
        print("   - my_project-docs:1.0.0     (未变化)")
        
        print("\n🎯 开发者可以选择:")
        print("   - 保守: 使用 1.0.0 版本的所有组件")
        print("   - 激进: 使用 headers:1.0.1 + 其他组件:1.0.0")
        
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def example_6_metadata_filtering():
    """示例6: 使用元数据分类"""
    print("\n" + "="*70)
    print("示例6: 元数据分类 - 通过metadata标记包类型")
    print("="*70)
    
    publisher = PublisherService(
        storage_path="./releases",
        db_path="./binary_manager_v2/database/binary_manager.db"
    )
    
    print("\n📋 发布带有类型标记的包...")
    
    tmp_dir, bin_path, headers_path, docs_path = create_sample_project_structure()
    
    try:
        # 发布时添加元数据标记
        print("\n发布二进制包（类型: binary）")
        result1 = publisher.publish(
            source_dir=str(bin_path),
            package_name="myapp",
            version="2.0.0",
            description="MyApp v2.0.0",
            metadata={"type": "binary", "platform": "linux", "arch": "x86_64"}
        )
        
        print("发布头文件包（类型: headers）")
        result2 = publisher.publish(
            source_dir=str(headers_path),
            package_name="myapp",
            version="2.0.0",
            description="MyApp v2.0.0 Headers",
            metadata={"type": "headers", "language": "C"}
        )
        
        print("发布文档包（类型: docs）")
        result3 = publisher.publish(
            source_dir=str(docs_path),
            package_name="myapp",
            version="2.0.0",
            description="MyApp v2.0.0 Documentation",
            metadata={"type": "docs", "format": "html+pdf"}
        )
        
        print(f"\n✅ 发布完成！所有包都使用相同的名称 'myapp' 和版本 '2.0.0'")
        print("   通过 metadata['type'] 区分不同类型")
        
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main():
    """运行所有示例"""
    print("\n" + "="*70)
    print("Binary Manager V2 - 分包发布示例")
    print("演示如何支持将一个项目的不同部分分开独立发布和下载")
    print("="*70)
    
    try:
        # 示例1: 分开发布
        example_1_separate_publishing()
        
        # 示例2: 独立下载
        example_2_independent_download()
        
        # 示例3: 版本匹配
        example_3_version_matching()
        
        # 示例4: 版本查询
        example_4_version_query()
        
        # 示例5: 部分升级
        example_5_partial_upgrade()
        
        # 示例6: 元数据分类
        example_6_metadata_filtering()
        
        print("\n" + "="*70)
        print("✅ 所有示例演示完成！")
        print("="*70)
        
        print("\n📊 总结 - Binary Manager V2 完全支持分包发布场景：")
        print("\n1️⃣  命名规范方案:")
        print("    - 使用不同的 package_name: project-bin, project-headers, project-docs")
        print("    - 使用相同的 version 保持版本一致")
        print("    - 优点: 清晰明确，易于管理")
        
        print("\n2️⃣  元数据标记方案:")
        print("    - 使用相同的 package_name 和 version")
        print("    - 通过 metadata['type'] 区分: binary/headers/docs")
        print("    - 优点: 更灵活的查询和过滤")
        
        print("\n3️⃣  Group管理:")
        print("    - 创建不同用途的组（完整版、运行时、开发版）")
        print("    - 一次下载整个环境")
        print("    - 便于版本匹配和环境配置")
        
        print("\n4️⃣  独立下载:")
        print("    - 每个部分可以独立下载")
        print("    - 支持按需获取")
        print("    - 节省带宽和存储空间")
        
        print("\n5️⃣  版本管理:")
        print("    - 支持部分升级（如只更新头文件）")
        print("    - 保持向后兼容")
        print("    - 灵活的版本组合")
        
        print("\n✅ Binary Manager V2 完全满足嵌入式项目的分包发布需求！")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
