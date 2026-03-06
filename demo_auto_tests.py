#!/usr/bin/env python3
"""
自动化测试功能演示脚本

演示发布前自动运行测试的功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_section(title: str):
    """打印分节标题"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_test_runner():
    """演示测试运行器"""
    print_section("1. 测试运行器演示")
    
    from release_portal.application.test_runner import TestRunner
    
    # 创建测试运行器
    runner = TestRunner(project_root)
    
    # 检查测试环境
    print("检查测试环境...")
    checks = runner.check_test_environment()
    
    for key, value in checks.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value}")
    
    if not checks.get('pytest_installed'):
        print("\n❌ pytest 未安装，请先安装:")
        print("   pip install pytest pytest-cov")
        return False
    
    print(f"\n✅ 测试环境就绪!")
    
    return True


def demo_pre_publish_validation():
    """演示发布前验证"""
    print_section("2. 发布前验证演示")
    
    from release_portal.application.test_runner import PrePublishValidator
    
    # 创建验证器
    validator = PrePublishValidator()
    
    # 运行关键测试
    print("运行关键测试（发布前必须通过）...\n")
    
    result = validator.validate_before_publish(
        release_id="demo_release_001",
        test_level="critical"
    )
    
    print(f"\n结果: {'✅ 可以发布' if validator.can_publish(result) else '❌ 不能发布'}")
    
    return result.passed


def demo_cli_usage():
    """演示 CLI 使用"""
    print_section("3. CLI 使用演示")
    
    print("发布时运行测试:\n")
    print("  # 快速测试（关键测试，约30秒）")
    print("  release-portal publish \\")
    print("    --type bsp \\")
    print("    --version v1.0.0 \\")
    print("    --binary-dir ./build \\")
    print("    --test \\")
    print("    --test-level critical")
    print()
    print("  # 完整测试（所有测试，约2分钟）")
    print("  release-portal publish \\")
    print("    --type bsp \\")
    print("    --version v1.0.0 \\")
    print("    --binary-dir ./build \\")
    print("    --test \\")
    print("    --test-level all")
    print()
    print("  # 只测试 API")
    print("  release-portal publish --test --test-level api ...")
    print()
    print("  # 只测试集成")
    print("  release-portal publish --test --test-level integration ...")


def demo_web_api_usage():
    """演示 Web API 使用"""
    print_section("4. Web API 使用演示")
    
    print("发布时运行测试:\n")
    print("  POST /api/releases/{release_id}/publish")
    print("  Headers:")
    print("    Authorization: Bearer <token>")
    print("  Body:")
    print('    {')
    print('      "run_tests": true,')
    print('      "test_level": "critical"')
    print('    }')
    print()
    print("使用 curl:")
    print('  curl -X POST \\')
    print('    -H "Authorization: Bearer <token>" \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"run_tests": true, "test_level": "critical"}\' \\')
    print('    http://localhost:5000/api/releases/{release_id}/publish')


def demo_programmatic_usage():
    """演示编程方式使用"""
    print_section("5. 编程方式使用演示")
    
    print("在代码中使用:\n")
    
    code_example = '''
from release_portal.initializer import create_container
from release_portal.application.test_runner import PrePublishValidator

# 创建容器
container = create_container()

# 创建验证器
validator = PrePublishValidator()

# 发布前验证
result = validator.validate_before_publish(
    release_id="rel_123",
    test_level="critical"
)

if result.passed:
    # 测试通过，发布
    release = container.release_service.publish_release(
        release_id="rel_123",
        user_id=user.user_id
    )
    print(f"✅ 发布成功: {release.release_id}")
else:
    print(f"❌ 测试失败，无法发布")
    print(f"通过: {result.passed_tests}/{result.total_tests}")
'''
    
    print(code_example)


def demo_test_levels():
    """演示不同测试级别"""
    print_section("6. 测试级别说明")
    
    print("支持的测试级别:\n")
    
    test_levels = {
        "critical": {
            "description": "关键测试",
            "tests": "认证、创建发布、发布流程、端到端工作流",
            "duration": "约 30 秒",
            "use_case": "推荐用于日常发布"
        },
        "all": {
            "description": "所有测试",
            "tests": "运行测试套件中的所有测试",
            "duration": "约 2 分钟",
            "use_case": "完整验证、重要版本发布"
        },
        "api": {
            "description": "API 测试",
            "tests": "只运行 API 端点测试",
            "duration": "约 1 分钟",
            "use_case": "验证 API 功能"
        },
        "integration": {
            "description": "集成测试",
            "tests": "只运行集成测试",
            "duration": "约 1 分钟",
            "use_case": "验证完整工作流"
        }
    }
    
    for level, info in test_levels.items():
        print(f"  📋 {level.upper()}")
        print(f"     描述: {info['description']}")
        print(f"     测试: {info['tests']}")
        print(f"     耗时: {info['duration']}")
        print(f"     用途: {info['use_case']}")
        print()


def main():
    """主函数"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "自动化测试功能演示" + " "*31 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        # 1. 测试运行器演示
        if not demo_test_runner():
            print("\n⚠️  测试环境未就绪，跳过其他演示")
            return
        
        # 2. 发布前验证演示
        demo_pre_publish_validation()
        
        # 3. CLI 使用演示
        demo_cli_usage()
        
        # 4. Web API 使用演示
        demo_web_api_usage()
        
        # 5. 编程方式使用演示
        demo_programmatic_usage()
        
        # 6. 测试级别说明
        demo_test_levels()
        
        # 总结
        print_section("总结")
        print("✅ 自动化测试功能已完全集成到发布系统!")
        print()
        print("功能特性:")
        print("  • 发布前自动运行测试")
        print("  • 多个测试级别可选")
        print("  • CLI 和 Web API 支持")
        print("  • 详细的测试报告")
        print("  • 测试失败自动阻止发布")
        print()
        print("下一步:")
        print("  1. 在实际发布中使用 --test 参数")
        print("  2. 配置 CI/CD 自动运行测试")
        print("  3. 根据项目需求调整测试级别")
        print()
        
    except Exception as e:
        print(f"\n❌ 演示过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
