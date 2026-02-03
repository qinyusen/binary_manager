#!/usr/bin/env python3

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from binary_manager_v2.domain import (
    PackageName, Hash, GitInfo, StorageLocation, StorageType,
    FileInfo, Package, Group
)
from binary_manager_v2.domain.services import (
    HashCalculator, FileScanner, Packager
)
from binary_manager_v2.shared import Logger

def test_domain_layer():
    print("Testing Domain Layer...")
    
    pkg_name = PackageName("my_app")
    hash_val = Hash.from_string("sha256:abc123")
    
    print(f"  PackageName: {pkg_name}")
    print(f"  Hash: {hash_val}")
    
    git_info = GitInfo(
        commit_hash="abc123def456",
        commit_short="abc123",
        branch="main",
        author="Test User"
    )
    print(f"  GitInfo: {git_info}")
    
    storage = StorageLocation.s3("my-bucket", "packages/my_app/1.0.0/app.zip")
    print(f"  Storage: {storage}")
    
    print("✓ Domain Layer tests passed!")

def test_domain_services():
    print("\nTesting Domain Services...")
    
    scanner = FileScanner()
    hash_calc = HashCalculator('sha256')
    
    test_string = "test content"
    file_hash = hash_calc.calculate_string(test_string)
    print(f"  String hash: {file_hash}")
    
    print("✓ Domain Services tests passed!")

def test_shared_utils():
    print("\nTesting Shared Utilities...")
    
    logger = Logger.get('test')
    logger.info("Test log message")
    
    print("✓ Shared Utilities tests passed!")

if __name__ == '__main__':
    try:
        test_domain_layer()
        test_domain_services()
        test_shared_utils()
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
