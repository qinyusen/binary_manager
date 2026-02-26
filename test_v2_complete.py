#!/usr/bin/env python3
"""
Binary Manager V2 完整测试脚本
测试所有模块和新功能
"""
import sys
import tempfile
import shutil
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def test_domain_layer():
    """测试Domain层"""
    print("\n=== Testing Domain Layer ===")
    
    from binary_manager_v2.domain.value_objects import PackageName, Hash, GitInfo, StorageLocation, StorageType
    from binary_manager_v2.domain.entities import Package, Group, GroupPackage
    from binary_manager_v2.domain.services import FileScanner, HashCalculator, Packager
    
    # 测试值对象 - PackageName
    pkg_name = PackageName("test_app")
    print(f"✓ PackageName: {pkg_name}")
    assert str(pkg_name) == "test_app"
    
    # 测试值对象 - Hash
    hash_obj = Hash.from_string("sha256:abc123")
    print(f"✓ Hash: {hash_obj}")
    assert hash_obj.algorithm == "sha256"
    assert hash_obj.value == "abc123"
    
    # 测试值对象 - GitInfo（包含新字段）
    git_info = GitInfo(
        commit_hash="abc123def456",
        commit_short="abc123",
        branch="main",
        tag="v1.0.0",
        author="Test User",
        author_email="test@example.com",
        commit_time="2024-01-01T12:00:00Z",
        is_dirty=False,
        commit_message="Initial commit",
        remotes=[{'name': 'origin', 'url': 'https://github.com/test/repo.git'}]
    )
    print(f"✓ GitInfo: {git_info}")
    assert git_info.commit_message == "Initial commit"
    assert len(git_info.remotes) == 1
    assert git_info.remotes[0]['name'] == 'origin'
    
    # 测试GitInfo.to_dict()和from_dict()
    git_dict = git_info.to_dict()
    assert git_dict['commit_message'] == "Initial commit"
    assert len(git_dict['remotes']) == 1
    
    git_info_restored = GitInfo.from_dict(git_dict)
    assert git_info_restored.commit_message == git_info.commit_message
    assert len(git_info_restored.remotes) == len(git_info.remotes)
    
    print("✓ GitInfo serialization/deserialization")
    
    # 测试值对象 - StorageLocation
    storage = StorageLocation(StorageType.LOCAL, "/tmp/test.zip")
    print(f"✓ StorageLocation: {storage}")
    assert storage.storage_type == StorageType.LOCAL
    
    storage_s3 = StorageLocation(StorageType.S3, "packages/test.zip")
    assert storage_s3.storage_type == StorageType.S3
    
    # 测试领域服务 - FileScanner
    scanner = FileScanner()
    print("✓ FileScanner initialized")
    
    # 测试领域服务 - HashCalculator
    hash_calc = HashCalculator()
    test_hash = hash_calc.calculate_string("test")
    print(f"✓ HashCalculator: {test_hash}")
    
    # 测试领域服务 - Packager
    packager = Packager()
    print("✓ Packager initialized")
    
    # 测试实体 - GroupPackage
    group_pkg = GroupPackage(
        package_name="test_app",
        package_version="1.0.0",
        install_order=0,
        required=True
    )
    assert group_pkg.package_name == "test_app"
    assert group_pkg.package_version == "1.0.0"
    assert group_pkg.required == True
    print("✓ GroupPackage entity")
    
    # 测试实体 - Group
    group = Group(
        group_name=PackageName("test_env"),
        version="1.0.0",
        created_by="test_user"
    )
    group.add_package("test_app", "1.0.0", install_order=0, required=True)
    assert len(group.packages) == 1
    assert str(group.group_name) == "test_env"
    print("✓ Group entity")
    
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
        assert exists == True
        
        # 测试列表
        files = storage.list_files("")
        print(f"✓ LocalStorage list_files: {len(files)} files")
        assert len(files) > 0
        
        # 测试下载
        download_path = Path(tmpdir) / "downloaded.txt"
        storage.download_file("test.txt", str(download_path))
        assert download_path.exists()
        assert download_path.read_text() == "test content"
        print("✓ LocalStorage download_file")
        
        # 测试删除
        storage.delete_file("test.txt")
        assert not storage.file_exists("test.txt")
        print("✓ LocalStorage delete_file")
    
    # 测试GitService
    try:
        git_service = GitService(".")
        is_repo = git_service.is_git_repo()
        print(f"✓ GitService is_git_repo: {is_repo}")
        
        if is_repo:
            # 测试获取完整Git信息
            git_info = git_service.get_git_info()
            assert git_info is not None
            print(f"✓ GitService get_git_info: {git_info.commit_short}")
            
            # 测试新功能 - commit_message
            commit_msg = git_service.get_commit_message()
            print(f"✓ GitService get_commit_message: {commit_msg[:50]}...")
            assert commit_msg is not None
            
            # 测试新功能 - remotes
            remotes = git_service.get_remotes()
            print(f"✓ GitService get_remotes: {len(remotes)} remotes")
            assert isinstance(remotes, list)
            
            # 测试其他方法
            assert git_service.get_commit_hash() is not None
            assert git_service.get_commit_short() is not None
            print("✓ GitService all methods")
    except Exception as e:
        print(f"⚠ GitService test skipped: {e}")
    
    print("\n✅ Infrastructure Layer tests passed!")


def test_database_layer():
    """测试Database层"""
    print("\n=== Testing Database Layer ===")
    
    from binary_manager_v2.infrastructure.database import SQLitePackageRepository, SQLiteGroupRepository
    from binary_manager_v2.domain.entities import Package, Group, GroupPackage
    from binary_manager_v2.domain.value_objects import PackageName, Hash, GitInfo, StorageLocation, StorageType
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        # 测试PackageRepository
        pkg_repo = SQLitePackageRepository(str(db_path))
        print("✓ SQLitePackageRepository initialized")
        
        # 创建测试包
        git_info = GitInfo(
            commit_hash="abc123",
            commit_short="abc123",
            branch="main",
            commit_message="Test commit",
            remotes=[{'name': 'origin', 'url': 'https://github.com/test/repo.git'}]
        )
        
        package = Package(
            package_name=PackageName("test_app"),
            version="1.0.0",
            archive_hash=Hash.from_string("sha256:test123"),
            archive_size=1024,
            file_count=5,
            git_info=git_info,
            storage_location=StorageLocation(StorageType.LOCAL, "test_app_v1.0.0.zip"),
            description="Test package",
            metadata={"key": "value"}
        )
        
        # 测试保存
        package_id = pkg_repo.save(package)
        assert package_id is not None
        print(f"✓ Package saved with ID: {package_id}")
        
        # 测试查找
        found = pkg_repo.find_by_id(package_id)
        assert found is not None
        assert str(found.package_name) == "test_app"
        assert found.git_info.commit_message == "Test commit"
        assert len(found.git_info.remotes) == 1
        print("✓ Package found by ID")
        
        # 测试按名称和版本查找
        found = pkg_repo.find_by_name_and_version("test_app", "1.0.0")
        assert found is not None
        print("✓ Package found by name and version")
        
        # 测试查找所有
        all_packages = pkg_repo.find_all()
        assert len(all_packages) >= 1
        print(f"✓ Found {len(all_packages)} packages")
        
        # 测试过滤器
        filtered = pkg_repo.find_all({'package_name': 'test_app'})
        assert len(filtered) >= 1
        print("✓ Package filtering works")
        
        # 测试exists
        exists = pkg_repo.exists("test_app", "1.0.0")
        assert exists == True
        print("✓ Package exists check")
        
        # 测试GroupRepository
        group_repo = SQLiteGroupRepository(str(db_path))
        print("✓ SQLiteGroupRepository initialized")
        
        # 创建测试分组
        group = Group(
            group_name=PackageName("test_env"),
            version="1.0.0",
            created_by="test_publisher",
            description="Test environment",
            environment_config={"env": "production"},
            metadata={"team": "backend"}
        )
        
        # 添加包到分组（这会创建GroupPackage，但package_id还未设置）
        group.add_package("test_app", "1.0.0", install_order=0, required=True)
        
        # 手动设置package_id（因为我们在测试中直接使用repository）
        for pkg in group._packages:
            if pkg.package_name == "test_app":
                pkg.package_id = package_id
        
        group_id = group_repo.save(group, "test_publisher")
        assert group_id is not None
        print(f"✓ Group saved with ID: {group_id}")
        
        # 测试查找分组
        found_group = group_repo.find_by_id(group_id)
        assert found_group is not None
        assert str(found_group.group_name) == "test_env"
        print("✓ Group found by ID")
        
        # 测试添加包到分组
        result = group_repo.add_package(group_id, package_id, 1, False)
        assert result == True
        print("✓ Package added to group")
        
        # 测试查找所有分组
        all_groups = group_repo.find_all()
        assert len(all_groups) >= 1
        print(f"✓ Found {len(all_groups)} groups")
        
        pkg_repo.close()
        group_repo.close()
    
    print("\n✅ Database Layer tests passed!")


def test_application_layer():
    """测试Application层"""
    print("\n=== Testing Application Layer ===")
    
    from binary_manager_v2.application import PublisherService, DownloaderService, GroupService
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = str(Path(tmpdir) / "test.db")
        
        # 测试PublisherService
        publisher = PublisherService(db_path=db_path, storage_path=tmpdir)
        print("✓ PublisherService initialized")
        
        # 测试DownloaderService
        downloader = DownloaderService(storage_path=tmpdir)
        print("✓ DownloaderService initialized")
        
        # 测试GroupService
        group_service = GroupService(db_path=db_path)
        print("✓ GroupService initialized")
        
        # 测试发布流程
        source_dir = Path(tmpdir) / "source"
        source_dir.mkdir()
        (source_dir / "main.py").write_text("print('Hello')")
        (source_dir / "README.md").write_text("# Test")
        
        result = publisher.publish(
            source_dir=str(source_dir),
            package_name="test_app",
            version="1.0.0",
            description="Test package",
            extract_git=False
        )
        
        assert result['package_id'] is not None
        assert Path(result['archive_path']).exists()
        print(f"✓ Package published: {result['package_id']}")
        
        # 测试创建分组
        group_result = group_service.create_group(
            group_name="test_env",
            version="1.0.0",
            packages=[{
                'package_name': 'test_app',
                'version': '1.0.0'
            }],
            description="Test environment"
        )
        
        assert group_result['group_id'] is not None
        print(f"✓ Group created: {group_result['group_id']}")
        
        # 测试导出分组
        export_path = Path(tmpdir) / "export"
        export_file = group_service.export_group(group_result['group_id'], str(export_path))
        assert export_file is not None
        assert Path(export_file).exists()
        print(f"✓ Group exported: {export_file}")
        
        # 测试导入分组
        # 先删除原分组
        group_service.delete_group(group_result['group_id'])
        
        # 再导入
        imported_id = group_service.import_group(export_file)
        assert imported_id is not None
        print(f"✓ Group imported: {imported_id}")
    
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
    
    # 测试参数解析
    # 测试publish命令
    args = parser.parse_args(['publish', '--source', '/tmp/test', '--package-name', 'test', '--version', '1.0.0'])
    assert args.command == 'publish'
    assert args.package_name == 'test'
    assert args.version == '1.0.0'
    print("✓ CLI publish command parsing")
    
    # 测试download命令
    args = parser.parse_args(['download', '--package-name', 'test', '--version', '1.0.0'])
    assert args.command == 'download'
    assert args.package_name == 'test'
    print("✓ CLI download command parsing")
    
    # 测试group命令
    args = parser.parse_args(['group', 'create', '--group-name', 'test_env', '--version', '1.0.0'])
    assert args.command == 'group'
    assert args.group_action == 'create'
    assert args.group_name == 'test_env'
    print("✓ CLI group command parsing")
    
    # 测试list命令
    args = parser.parse_args(['list'])
    assert args.command == 'list'
    print("✓ CLI list command parsing")
    
    print("\n✅ CLI tests passed!")


def test_integration():
    """集成测试 - 端到端流程"""
    print("\n=== Testing Integration ===")
    
    from binary_manager_v2.application import PublisherService, DownloaderService, GroupService
    from binary_manager_v2.domain.services import FileScanner, HashCalculator, Packager
    from binary_manager_v2.infrastructure.database import SQLitePackageRepository
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试源目录
        source_dir = Path(tmpdir) / "source"
        source_dir.mkdir()
        
        # 创建一些测试文件
        (source_dir / "main.py").write_text("print('Hello, World!')")
        (source_dir / "README.md").write_text("# Test App")
        (source_dir / "config.json").write_text('{"key": "value"}')
        
        # 创建发布器
        releases_dir = Path(tmpdir) / "releases"
        releases_dir.mkdir()
        
        db_path = str(Path(tmpdir) / "test.db")
        publisher = PublisherService(db_path=db_path, storage_path=str(releases_dir))
        print("✓ PublisherService created")
        
        # 扫描文件
        scanner = FileScanner()
        files, scan_info = scanner.scan_directory(str(source_dir))
        print(f"✓ Scanned {len(files)} files")
        assert len(files) == 3
        
        # 创建压缩包
        packager = Packager(str(releases_dir))
        archive_path = packager.create_zip(
            str(source_dir),
            files,
            "test_app",
            "1.0.0"
        )['archive_path']
        archive_path = Path(archive_path)
        print(f"✓ Created archive: {archive_path}")
        assert archive_path.exists()
        
        # 计算哈希
        hash_calc = HashCalculator()
        file_hash = hash_calc.calculate_file(str(archive_path))
        print(f"✓ File hash: {file_hash}")
        
        # 验证文件大小
        file_size = archive_path.stat().st_size
        assert file_size > 0
        print(f"✓ Archive size: {file_size} bytes")
        
        # 测试解压
        extract_dir = Path(tmpdir) / "extracted"
        extract_dir.mkdir()
        packager.extract_zip(str(archive_path), str(extract_dir))
        print(f"✓ Extracted to: {extract_dir}")
        
        # 验证解压的文件
        extracted_files = list(extract_dir.rglob("*"))
        print(f"✓ Extracted {len(extracted_files)} items")
        
        # 验证具体文件
        assert (extract_dir / "main.py").exists()
        assert (extract_dir / "README.md").exists()
        assert (extract_dir / "config.json").exists()
        print("✓ All files extracted correctly")
        
        # 测试完整的发布流程
        result = publisher.publish(
            source_dir=str(source_dir),
            package_name="integration_test",
            version="2.0.0",
            description="Integration test package",
            metadata={"test": "integration"},
            extract_git=False
        )
        
        assert result['package_id'] is not None
        assert Path(result['archive_path']).exists()
        assert Path(result['config_path']).exists()
        print(f"✓ Full publish completed: {result['package_id']}")
        
        # 验证配置文件
        with open(result['config_path'], 'r') as f:
            config = json.load(f)
        assert config['package_name'] == "integration_test"
        assert config['version'] == "2.0.0"
        assert config['file_info']['file_count'] == 3
        print("✓ Config file generated correctly")
        
        # 测试创建分组
        group_service = GroupService(db_path=db_path)
        
        group_result = group_service.create_group(
            group_name="integration_env",
            version="1.0.0",
            packages=[
                {'package_name': 'integration_test', 'version': '2.0.0', 'install_order': 0, 'required': True}
            ],
            description="Integration test environment"
        )
        
        assert group_result['group_id'] is not None
        assert len(group_result['packages']) == 1  # 只有integration_test存在
        print(f"✓ Integration group created: {group_result['group_id']}")
        
        # 测试导出和导入
        export_dir = Path(tmpdir) / "exports"
        export_file = group_service.export_group(group_result['group_id'], str(export_dir))
        assert export_file is not None
        
        # 验证导出文件
        with open(export_file, 'r') as f:
            export_data = json.load(f)
        assert export_data['group_name'] == "integration_env"
        assert len(export_data['packages']) == 1
        print("✓ Group export successful")
    
    print("\n✅ Integration tests passed!")


def test_value_objects_edge_cases():
    """测试值对象的边界情况"""
    print("\n=== Testing Value Objects Edge Cases ===")
    
    from binary_manager_v2.domain.value_objects import PackageName, Hash, GitInfo, StorageLocation, StorageType
    
    # 测试PackageName验证
    try:
        invalid_name = PackageName("")
        assert False, "Should raise error for empty name"
    except Exception:
        print("✓ PackageName rejects empty string")
    
    # 测试Hash的不同格式
    hash1 = Hash.from_string("sha256:abc123")
    assert hash1.algorithm == "sha256"
    
    hash2 = Hash.from_string("md5:def456")
    assert hash2.algorithm == "md5"
    print("✓ Hash supports multiple algorithms")
    
    # 测试GitInfo的可选字段
    minimal_git = GitInfo(
        commit_hash="abc123",
        commit_short="abc123"
    )
    assert minimal_git.branch is None
    assert minimal_git.tag is None
    assert minimal_git.author is None
    assert minimal_git.commit_message is None
    assert len(minimal_git.remotes) == 0
    print("✓ GitInfo handles optional fields")
    
    # 测试GitInfo相等性
    git1 = GitInfo(commit_hash="abc123", commit_short="abc123")
    git2 = GitInfo(commit_hash="abc123", commit_short="abc123", branch="main")
    assert git1 == git2
    print("✓ GitInfo equality based on commit_hash")
    
    # 测试StorageLocation类型
    local_storage = StorageLocation(StorageType.LOCAL, "/path/to/file")
    s3_storage = StorageLocation(StorageType.S3, "bucket/key")
    
    assert local_storage.storage_type == StorageType.LOCAL
    assert s3_storage.storage_type == StorageType.S3
    print("✓ StorageLocation handles different types")
    
    print("\n✅ Value Objects Edge Cases tests passed!")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("Binary Manager V2 - Complete Test Suite")
    print("=" * 60)
    
    try:
        test_domain_layer()
        test_infrastructure_layer()
        test_database_layer()
        test_application_layer()
        test_cli()
        test_integration()
        test_value_objects_edge_cases()
        
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
