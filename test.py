#!/usr/bin/env python3
"""
测试脚本 - 验证发布器和下载器功能
"""
import os
import shutil
import sys

def cleanup():
    """清理测试文件"""
    dirs_to_remove = ['test_releases', 'test_downloads']
    for d in dirs_to_remove:
        if os.path.exists(d):
            shutil.rmtree(d)
    print("✓ 清理完成")

def test_publisher():
    """测试发布器"""
    print("\n========================================")
    print("测试发布器...")
    print("========================================")
    
    os.system('python3 binary_manager/publisher/main.py '
              '--source binary_manager/examples/my_app '
              '--output test_releases '
              '--version 1.0.0 '
              '--name test_app')
    
    if not os.path.exists('test_releases/test_app_v1.0.0.zip'):
        print("✗ 发布器测试失败：未生成zip文件")
        return False
    
    if not os.path.exists('test_releases/test_app_v1.0.0.json'):
        print("✗ 发布器测试失败：未生成JSON配置文件")
        return False
    
    print("✓ 发布器测试通过")
    return True

def test_downloader():
    """测试下载器"""
    print("\n========================================")
    print("测试下载器...")
    print("========================================")
    
    os.system('python3 binary_manager/downloader/main.py '
              '--config test_releases/test_app_v1.0.0.json '
              '--output test_downloads/test_app')
    
    if not os.path.exists('test_downloads/test_app/test_app'):
        print("✗ 下载器测试失败：未解压文件")
        return False
    
    print("✓ 下载器测试通过")
    return True

def verify_integrity():
    """验证文件完整性"""
    print("\n========================================")
    print("验证文件完整性...")
    print("========================================")
    
    exit_code = os.system('diff -r binary_manager/examples/my_app test_downloads/test_app/test_app')
    
    if exit_code == 0:
        print("✓ 文件完整性验证通过")
        return True
    else:
        print("✗ 文件完整性验证失败")
        return False

def main():
    print("========================================")
    print("Binary Manager - 功能测试")
    print("========================================")
    
    cleanup()
    
    try:
        results = []
        results.append(("发布器", test_publisher()))
        results.append(("下载器", test_downloader()))
        results.append(("完整性验证", verify_integrity()))
        
        print("\n========================================")
        print("测试结果汇总")
        print("========================================")
        
        all_passed = True
        for test_name, passed in results:
            status = "✓ 通过" if passed else "✗ 失败"
            print(f"{test_name}: {status}")
            if not passed:
                all_passed = False
        
        print("========================================")
        
        if all_passed:
            print("所有测试通过！")
            print("\n生成的文件:")
            print("  - test_releases/test_app_v1.0.0.zip")
            print("  - test_releases/test_app_v1.0.0.json")
            print("  - test_downloads/test_app/ (解压目录)")
        else:
            print("部分测试失败，请检查日志")
            sys.exit(1)
            
    except Exception as e:
        print(f"测试过程出错: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
