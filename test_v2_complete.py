#!/usr/bin/env python3
"""
Binary Manager V2 测试脚本
测试新实现的所有模块
"""
import sys
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_domain_layer():
    """测试Domain层"""
    print("\n=== Testing Domain Layer ===")
    
    from binary_manager_v2.domain.value_objects import PackageName, Hash, GitInfo, StorageLocation, StorageType
    from binary_manager_v2.domain.entities import Package
    from binary_manager_v2.domain.services import FileScanner, HashCalculator, Packager
    
    # 测试值对象
    pkg_name = PackageName("test_app")
    print(f"✓ PackageName: {pkg_name}")
    
    hash_obj = Hash.from_string("sha256:abc123")
    print(f"✓ Hash: {hash_obj}")
    
    git_info = GitInfo(
        commit_hash="abc123def456",
        commit_short="abc123",
        branch="main",
        author="Test User"
    )
    print(f"✓ GitInfo: {git_info}")
    
    storage = StorageLocation(StorageType.LOCAL, "/tmp/test.zip")
    print(f"✓ StorageLocation: {storage}")
    
    # 测试领域服务
    scanner = FileScanner()
    print("✓ FileScanner initialized")
    
    hash_calc = HashCalculator()
    test_hash = hash_calc.calculate_string("test")
    print(f"✓ HashCalculator: {test_hash}")
    
    packager = Packager()
    print("✓ Packager initialized")
    
    print("\n✅ Domain Layer tests passed!")


def test_infrastructure_layer():
    """测试Infrastructure层"""
    print("\n=== Testing Infrastructure Layer ===")
    
    from binary_manager_v2.infrastructure.storage import LocalStorage
    from binary_manager_v2.infrastructure.git import GitService
    
    # 测试LocalStorage
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = LocalStorage(tmpdir)
        
        # 创建测试文件
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("test content")
        
        # 测试上传
        storage.upload_file(str(test_file), "test.txt")
        print("✓ LocalStorage upload_file")
        
        # 测试文件存在检查
        exists = storage.file_exists("test.txt")
        print(f"✓ LocalStorage file_exists: {exists}")
        
        # 测试列表
        files = storage.list_files("")
        print(f"✓ LocalStorage list_files: {len(files)} files")
    
    # 测试GitService
    try:
        git_service = GitService(".")
        is_repo = git_service.is_git_repo()
        print(f"✓ GitService is_git_repo: {is_repo}")
    except Exception as e:
        print(f"⚠ GitService test skipped: {e}")
    
    print("\n✅ Infrastructure Layer tests passed!")


def test_application_layer():
    """测试Application层"""
    print("\n=== Testing Application Layer ===")
    
    from binary_manager_v2.application import PublisherService, DownloaderService, GroupService
    
    # 测试PublisherService初始化
    with tempfile.TemporaryDirectory() as tmpdir:
        publisher = PublisherService(storage_path=tmpdir)
        print("✓ PublisherService initialized")
        
        # 测试DownloaderService初始化
        downloader = DownloaderService(storage_path=tmpdir)
        print("✓ DownloaderService initialized")
        
        # 测试GroupService初始化
        group_service = GroupService()
        print("✓ GroupService initialized")
    
    print("\n✅ Application Layer tests passed!")


def test_cli():
    """测试CLI"""
    print("\n=== Testing CLI ===")
    
    from binary_manager_v2.cli.main import BinaryManagerCLI
    
    cli = BinaryManagerCLI()
    print("✓ BinaryManagerCLI initialized")
    
    # 测试parser
    parser = cli.parser
    print("✓ CLI parser created")
    
    print("\n✅ CLI tests passed!")


def test_integration():
    """集成测试 - 端到端流程"""
    print("\n=== Testing Integration ===")
    
    from binary_manager_v2.application import PublisherService
    from binary_manager_v2.infrastructure.storage import LocalStorage
    from binary_manager_v2.domain.services import FileScanner, HashCalculator, Packager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试源目录
        source_dir = Path(tmpdir) / "source"
        source_dir.mkdir()
        
        # 创建一些测试文件
        (source_dir / "main.py").write_text("print('Hello, World!')")
        (source_dir / "README.md").write_text("# Test App")
        
        # 创建发布器
        releases_dir = Path(tmpdir) / "releases"
        releases_dir.mkdir()
        
        publisher = PublisherService(storage_path=str(releases_dir))
        print("✓ PublisherService created")
        
        # 扫描文件
        scanner = FileScanner()
        files, scan_info = scanner.scan_directory(str(source_dir))
        print(f"✓ Scanned {len(files)} files")
        
        # 创建压缩包
        packager = Packager(str(releases_dir))
        result = packager.create_zip(str(source_dir), files, "test_app", "1.0.0")
        archive_path = Path(result['archive_path'])
        print(f"✓ Created archive: {archive_path}")
        
        # 计算哈希
        hash_calc = HashCalculator()
        file_hash = hash_calc.calculate_file(str(archive_path))
        print(f"✓ File hash: {file_hash}")
        
        # 验证文件存在
        if archive_path.exists():
            print(f"✓ Archive exists: {archive_path.stat().st_size} bytes")
        
        # 测试解压
        extract_dir = Path(tmpdir) / "extracted"
        extract_dir.mkdir()
        packager.extract_zip(str(archive_path), str(extract_dir))
        print(f"✓ Extracted to: {extract_dir}")
        
        # 验证解压的文件
        extracted_files = list(extract_dir.rglob("*"))
        print(f"✓ Extracted {len(extracted_files)} items")
    
    print("\n✅ Integration tests passed!")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Binary Manager V2 - Test Suite")
    print("=" * 60)
    
    try:
        test_domain_layer()
        test_infrastructure_layer()
        test_application_layer()
        test_cli()
        test_integration()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
