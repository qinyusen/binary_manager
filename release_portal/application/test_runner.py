"""
自动化测试运行器 - 发布前自动测试

提供发布前自动运行测试套件的功能
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class TestResult:
    """测试结果"""
    passed: bool
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    duration: float = 0.0
    output: str = ""
    errors: Optional[List[str]] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'passed': self.passed,
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'skipped_tests': self.skipped_tests,
            'duration': self.duration,
            'errors': self.errors
        }


class TestRunner:
    """测试运行器"""

    def __init__(self, project_root: Optional[Path] = None):
        """
        初始化测试运行器
        
        Args:
            project_root: 项目根目录，默认为当前目录向上两级
        """
        if project_root is None:
            # 默认为当前文件向上两级
            project_root = Path(__file__).parent.parent
        
        self.project_root = Path(project_root)
        self.tests_dir = self.project_root / "tests"
        self.pytest_ini = self.project_root / "pytest.ini"

    def run_all_tests(self, verbose: bool = True) -> TestResult:
        """
        运行所有测试
        
        Args:
            verbose: 是否显示详细输出
            
        Returns:
            TestResult: 测试结果
        """
        return self._run_pytest([], verbose=verbose)

    def run_specific_tests(self, 
                          test_path: str,
                          verbose: bool = True) -> TestResult:
        """
        运行特定测试
        
        Args:
            test_path: 测试路径或文件
            verbose: 是否显示详细输出
            
        Returns:
            TestResult: 测试结果
        """
        return self._run_pytest([test_path], verbose=verbose)

    def run_api_tests(self, verbose: bool = True) -> TestResult:
        """运行 API 测试"""
        return self._run_pytest(["tests/api/"], verbose=verbose)

    def run_integration_tests(self, verbose: bool = True) -> TestResult:
        """运行集成测试"""
        return self._run_pytest(["tests/integration/"], verbose=verbose)

    def run_critical_tests(self, verbose: bool = True) -> TestResult:
        """
        运行关键测试（发布前必须通过的测试）
        
        Returns:
            TestResult: 测试结果
        """
        critical_tests = [
            "tests/api/test_auth_api.py::TestAuthAPI::test_login_success",
            "tests/api/test_releases_api.py::TestReleasesAPI::test_create_release",
            "tests/api/test_releases_api.py::TestReleasesAPI::test_publish_release",
            "tests/integration/test_end_to_end.py::TestEndToEndReleaseWorkflow::test_complete_release_workflow",
        ]
        
        return self._run_pytest(critical_tests, verbose=verbose)

    def _run_pytest(self, 
                   args: List[str],
                   verbose: bool = True) -> TestResult:
        """
        运行 pytest
        
        Args:
            args: pytest 参数
            verbose: 是否显示详细输出
            
        Returns:
            TestResult: 测试结果
        """
        cmd = [sys.executable, "-m", "pytest"]
        
        # 添加参数
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")  # quiet 模式
        
        # 添加测试路径或参数
        cmd.extend(args)
        
        # 添加 JSON 报告参数（用于解析结果）
        cmd.extend([
            "--tb=no",
            "--no-header",
            "-ra"  # summary of all test results
        ])
        
        try:
            # 运行测试
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            # 解析结果
            return self._parse_test_result(result)
            
        except subprocess.TimeoutExpired:
            return TestResult(
                passed=False,
                output="测试运行超时（5分钟）",
                errors=["测试超时"]
            )
        except Exception as e:
            return TestResult(
                passed=False,
                output=f"测试运行出错: {str(e)}",
                errors=[str(e)]
            )

    def _parse_test_result(self, result: subprocess.CompletedProcess) -> TestResult:
        """
        解析 pytest 结果
        
        Args:
            result: subprocess 运行结果
            
        Returns:
            TestResult: 解析后的测试结果
        """
        output = result.stdout + result.stderr
        passed = result.returncode == 0
        
        # 解析测试统计
        total = passed_tests = failed = skipped = 0
        duration = 0.0
        
        # 尝试从输出中解析测试数量
        # 示例输出: "5 passed, 2 failed in 3.45s"
        for line in output.split('\n'):
            if 'passed' in line or 'failed' in line or 'skipped' in line:
                # 提取数字
                import re
                numbers = re.findall(r'\d+', line)
                if len(numbers) >= 1:
                    total = sum(int(n) for n in numbers)
                
                # 提取 passed, failed, skipped
                if 'passed' in line:
                    match = re.search(r'(\d+)\s+passed', line)
                    if match:
                        passed_tests = int(match.group(1))
                
                if 'failed' in line:
                    match = re.search(r'(\d+)\s+failed', line)
                    if match:
                        failed = int(match.group(1))
                
                if 'skipped' in line:
                    match = re.search(r'(\d+)\s+skipped', line)
                    if match:
                        skipped = int(match.group(1))
            
            # 提取耗时
            if 'in' in line and ('s' in line or 'sec' in line):
                import re
                match = re.search(r'(\d+\.?\d*)\s*s', line)
                if match:
                    duration = float(match.group(1))
        
        # 收集错误信息
        errors = []
        if not passed:
            # 从输出中提取失败测试
            for line in output.split('\n'):
                if 'FAILED' in line:
                    errors.append(line.strip())
        
        return TestResult(
            passed=passed,
            total_tests=total or passed_tests + failed + skipped,
            passed_tests=passed_tests,
            failed_tests=failed,
            skipped_tests=skipped,
            duration=duration,
            output=output,
            errors=errors[:10]  # 最多保存10个错误
        )

    def check_test_environment(self) -> Dict[str, bool]:
        """
        检查测试环境
        
        Returns:
            Dict: 环境检查结果
        """
        checks = {}
        
        # 检查 pytest 是否安装
        try:
            import pytest
            checks['pytest_installed'] = True
        except ImportError:
            checks['pytest_installed'] = False
        
        # 检查测试目录
        checks['tests_dir_exists'] = self.tests_dir.exists()
        
        # 检查 pytest.ini
        checks['pytest_ini_exists'] = self.pytest_ini.exists()
        
        # 检查测试文件
        if checks['tests_dir_exists']:
            test_files = list(self.tests_dir.rglob("test_*.py"))
            checks['has_test_files'] = len(test_files) > 0
            checks['test_file_count'] = len(test_files)
        else:
            checks['has_test_files'] = False
            checks['test_file_count'] = 0
        
        return checks


class PrePublishValidator:
    """发布前验证器"""

    def __init__(self, test_runner: Optional[TestRunner] = None):
        """
        初始化验证器
        
        Args:
            test_runner: 测试运行器，如果不提供则创建默认实例
        """
        if test_runner is None:
            self.test_runner = TestRunner()
        else:
            self.test_runner = test_runner
        
        self.validation_history = []

    def validate_before_publish(self, 
                               release_id: str,
                               test_level: str = "critical") -> TestResult:
        """
        发布前验证
        
        Args:
            release_id: 发布 ID
            test_level: 测试级别
                - "critical": 只运行关键测试（快速）
                - "all": 运行所有测试（完整）
                - "api": 只运行 API 测试
                - "integration": 只运行集成测试
                
        Returns:
            TestResult: 测试结果
        """
        print(f"\n{'='*60}")
        print(f"🧪 发布前验证 - Release ID: {release_id}")
        print(f"📋 测试级别: {test_level}")
        print(f"{'='*60}\n")
        
        # 检查测试环境
        env_checks = self.test_runner.check_test_environment()
        
        if not env_checks.get('pytest_installed'):
            return TestResult(
                passed=False,
                output="❌ pytest 未安装，无法运行测试",
                errors=["pytest 未安装"]
            )
        
        if not env_checks.get('has_test_files'):
            return TestResult(
                passed=False,
                output="❌ 没有找到测试文件",
                errors=["测试文件不存在"]
            )
        
        print(f"✅ 测试环境检查通过")
        print(f"   - pytest: 已安装")
        print(f"   - 测试文件: {env_checks.get('test_file_count', 0)} 个\n")
        
        # 根据测试级别运行测试
        start_time = datetime.now()
        
        if test_level == "critical":
            print("🔍 运行关键测试...")
            result = self.test_runner.run_critical_tests(verbose=False)
        elif test_level == "all":
            print("🔍 运行所有测试...")
            result = self.test_runner.run_all_tests(verbose=False)
        elif test_level == "api":
            print("🔍 运行 API 测试...")
            result = self.test_runner.run_api_tests(verbose=False)
        elif test_level == "integration":
            print("🔍 运行集成测试...")
            result = self.test_runner.run_integration_tests(verbose=False)
        else:
            return TestResult(
                passed=False,
                output=f"❌ 未知的测试级别: {test_level}",
                errors=[f"未知的测试级别: {test_level}"]
            )
        
        duration = (datetime.now() - start_time).total_seconds()
        result.duration = duration
        
        # 记录历史
        self.validation_history.append({
            'release_id': release_id,
            'test_level': test_level,
            'result': result.to_dict(),
            'timestamp': datetime.now().isoformat()
        })
        
        # 打印结果
        print(f"\n{'='*60}")
        if result.passed:
            print(f"✅ 测试通过！")
        else:
            print(f"❌ 测试失败！")
        
        print(f"📊 测试统计:")
        print(f"   - 总计: {result.total_tests} 个")
        print(f"   - 通过: {result.passed_tests} 个")
        print(f"   - 失败: {result.failed_tests} 个")
        print(f"   - 跳过: {result.skipped_tests} 个")
        print(f"   - 耗时: {result.duration:.2f} 秒")
        
        if result.errors:
            print(f"\n❌ 失败的测试:")
            for error in result.errors[:5]:
                print(f"   - {error}")
        
        print(f"{'='*60}\n")
        
        return result

    def get_validation_history(self) -> List[Dict]:
        """获取验证历史"""
        return self.validation_history

    def can_publish(self, test_result: TestResult) -> bool:
        """
        判断是否可以发布
        
        Args:
            test_result: 测试结果
            
        Returns:
            bool: 是否可以发布
        """
        return test_result.passed


# 便捷函数
def run_tests_before_publish(release_id: str, 
                            test_level: str = "critical") -> bool:
    """
    发布前运行测试（便捷函数）
    
    Args:
        release_id: 发布 ID
        test_level: 测试级别
        
    Returns:
        bool: 测试是否通过
    """
    validator = PrePublishValidator()
    result = validator.validate_before_publish(release_id, test_level)
    return result.passed


if __name__ == "__main__":
    # 测试代码
    print("测试运行器演示\n")
    
    # 创建测试运行器
    runner = TestRunner()
    
    # 检查环境
    print("1. 检查测试环境:")
    checks = runner.check_test_environment()
    for key, value in checks.items():
        status = "✅" if value else "❌"
        print(f"   {status} {key}: {value}")
    
    print("\n2. 运行关键测试:")
    validator = PrePublishValidator()
    result = validator.validate_before_publish("test_release_001", "critical")
    
    print(f"\n3. 结果: {'可以发布' if result.passed else '不能发布'}")
