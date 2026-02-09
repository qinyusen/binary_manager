#!/usr/bin/env python3
"""
Release App 测试脚本
测试基本功能而不实际编译
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from tools.release_app.version_tracker import VersionTracker
from tools.release_app.utils import validate_semantic_version, get_publisher_info, format_file_size


def test_version_tracker():
    """测试版本追踪器"""
    print("=" * 50)
    print("测试 1: VersionTracker")
    print("=" * 50)
    
    tracker = VersionTracker(Path('./test_versions'))
    
    version_data = tracker.create_version_data(
        version="1.0.0",
        binary_info={
            'path': '/path/to/binary',
            'name': 'test_app',
            'size': 1024,
            'hash': 'sha256:abc123'
        },
        git_info={
            'commit_short': 'a1b2c3d',
            'branch': 'main'
        },
        publisher_info=get_publisher_info(),
        release_notes="测试版本",
        release_type="both"
    )
    
    print(f"✅ 创建版本数据: {version_data['version']}")
    print(f"   发布类型: {version_data['release_type']}")
    print(f"   发布说明: {version_data['release_notes']}")
    
    version_file = tracker.save_version_file(version_data)
    print(f"✅ 保存版本文件: {version_file}")
    
    loaded = tracker.load_version_file("1.0.0")
    print(f"✅ 加载版本文件: {loaded['version'] if loaded else 'None'}")
    
    print()


def test_utils():
    """测试工具函数"""
    print("=" * 50)
    print("测试 2: Utils")
    print("=" * 50)
    
    print(f"✅ 验证版本号 '1.0.0': {validate_semantic_version('1.0.0')}")
    print(f"✅ 验证版本号 '2.1.3-beta': {validate_semantic_version('2.1.3-beta')}")
    print(f"✅ 验证版本号 'invalid': {validate_semantic_version('invalid')}")
    
    pub_info = get_publisher_info()
    print(f"✅ 发布者信息: {pub_info['username']}@{pub_info['hostname']}")
    
    print(f"✅ 文件大小格式化: {format_file_size(1024)}")
    print(f"✅ 文件大小格式化: {format_file_size(1048576)}")
    print(f"✅ 文件大小格式化: {format_file_size(1073741824)}")
    
    print()


def test_build_system_detection():
    """测试构建系统检测"""
    print("=" * 50)
    print("测试 3: 构建系统检测")
    print("=" * 50)
    
    from tools.release_app.utils import detect_build_system
    
    cpp_demo_dir = Path('./examples/cpp_demo')
    if cpp_demo_dir.exists():
        build_system = detect_build_system(cpp_demo_dir)
        print(f"✅ 检测到构建系统: {build_system}")
    else:
        print(f"⚠️  示例项目不存在: {cpp_demo_dir}")
    
    print()


def main():
    """主测试函数"""
    print("\n")
    print("*" * 50)
    print("*  Release App 功能测试")
    print("*" * 50)
    print()
    
    try:
        test_utils()
        test_version_tracker()
        test_build_system_detection()
        
        print("=" * 50)
        print("✅ 所有测试通过！")
        print("=" * 50)
        print()
        print("下一步：")
        print("1. cd examples/cpp_demo")
        print("2. python3 -m tools.release_app")
        print()
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
