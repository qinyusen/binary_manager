#!/usr/bin/env python3
"""
Binary Manager v2 - 完整功能测试脚本
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def test_git_integration():
    """测试Git集成"""
    print('\n' + '='*60)
    print('测试1: Git集成功能')
    print('='*60)
    
    from binary_manager_v2.core.git_integration import extract_git_info
    
    git_info = extract_git_info('.')
    
    print(f'✓ Commit哈希: {git_info.get("commit_hash", "N/A")}')
    print(f'✓ 短哈希: {git_info.get("commit_short", "N/A")}')
    print(f'✓ 分支: {git_info.get("branch", "N/A")}')
    print(f'✓ Tag: {git_info.get("tag", "N/A")}')
    print(f'✓ 作者: {git_info.get("author", "N/A")}')
    print(f'✓ 提交时间: {git_info.get("commit_time", "N/A")}')
    print(f'✓ 是否有未提交更改: {git_info.get("is_dirty", False)}')
    
    if git_info.get('commit_hash'):
        print('✅ Git集成测试通过')
        return True
    else:
        print('✗ Git集成测试失败')
        return False


def test_database():
    """测试数据库"""
    print('\n' + '='*60)
    print('测试2: 数据库功能')
    print('='*60)
    
    from binary_manager_v2.core.database_manager import DatabaseManager
    from binary_manager_v2.core.git_integration import extract_git_info
    
    try:
        # 获取Git信息
        git_info = extract_git_info('.')
        
        with DatabaseManager(auto_init=True) as db:
            print(f'✓ Publisher ID: {db.publisher_id}')
            
            stats = db.get_statistics()
            print(f'✓ 总包数: {stats["total_packages"]}')
            print(f'✓ 总Group数: {stats["total_groups"]}')
            print(f'✓ 发布者数: {stats["total_publishers"]}')
            
            # 创建一个测试包信息
            test_package = {
                'package_name': 'test_package',
                'version': '1.0.0',
                'file_info': {
                    'archive_name': 'test.zip',
                    'size': 1024,
                    'file_count': 1,
                    'hash': 'sha256:abc123'
                },
                'storage': {
                    'type': 'local',
                    'path': '/tmp/test.zip'
                }
            }
            
            package_id = db.save_package(test_package, git_info)
            print(f'✓ 保存测试包，ID: {package_id}')
            
            # 查询包
            packages = db.query_packages({'package_name': 'test_package'})
            print(f'✓ 查询到 {len(packages)} 个测试包')
            
            if packages:
                pkg = packages[0]
                print(f'  - 包名: {pkg["package_name"]}')
                print(f'  - 版本: {pkg["version"]}')
                print(f'  - Git commit: {pkg["git_commit_short"]}')
                print(f'  - 发布者: {pkg["publisher_id"]}')
            
            print('✅ 数据库测试通过')
            return True
            
    except Exception as e:
        print(f'✗ 数据库测试失败: {e}')
        import traceback
        traceback.print_exc()
        return False


def test_group():
    """测试Group功能"""
    print('\n' + '='*60)
    print('测试3: Group功能')
    print('='*60)
    
    from binary_manager_v2.core.database_manager import DatabaseManager

    import sys
    sys.path.insert(0, str(Path(__file__).parent / 'binary_manager_v2'))
    from group.group_manager import GroupManager
    
    try:
        with DatabaseManager(auto_init=True) as db:
            with GroupManager() as gm:
                # 创建Group
                result = gm.create_group(
                    group_name='test_group',
                    version='1.0.0',
                    packages=[
                        {
                            'package_name': 'test_package',
                            'version': '1.0.0',
                            'install_order': 1,
                            'required': True
                        }
                    ],
                    description='测试Group',
                    environment_config={'debug': True}
                )
                
                print(f'✓ Group创建成功，ID: {result["group_id"]}')
                
                # 导出Group
                group_json_path = '/tmp/test_group.json'
                gm.export_group(result['group_id'], '/tmp')
                
                import os
                if os.path.exists(group_json_path):
                    print(f'✓ Group导出成功: {group_json_path}')
                else:
                    print(f'✗ Group导出失败')
                    return False
                
                # 列出Groups
                groups = gm.list_groups()
                print(f'✓ 查询到 {len(groups)} 个Group')
                
                for group in groups:
                    print(f'  - {group["group_name"]} v{group["version"]} (ID: {group["id"]})')
                
                print('✅ Group测试通过')
                return True
                
    except Exception as e:
        print(f'✗ Group测试失败: {e}')
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print('='*60)
    print('Binary Manager v2 - 功能测试')
    print('='*60)
    
    results = []
    
    try:
        results.append(('Git集成', test_git_integration()))
    except Exception as e:
        print(f'\n✗ Git集成测试出错: {e}')
        results.append(('Git集成', False))
    
    try:
        results.append(('数据库', test_database()))
    except Exception as e:
        print(f'\n✗ 数据库测试出错: {e}')
        results.append(('数据库', False))
    
    try:
        results.append(('Group', test_group()))
    except Exception as e:
        print(f'\n✗ Group测试出错: {e}')
        results.append(('Group', False))
    
    # 汇总结果
    print('\n' + '='*60)
    print('测试结果汇总')
    print('='*60)
    
    for test_name, passed in results:
        status = '✅ 通过' if passed else '✗ 失败'
        print(f'{test_name}: {status}')
    
    all_passed = all(result for _, result in results)
    
    print('='*60)
    if all_passed:
        print('✅ 所有测试通过！')
    else:
        print('⚠️  部分测试失败')
    print('='*60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
