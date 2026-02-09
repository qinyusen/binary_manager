"""
交互式命令行界面
Release App的主入口
"""

import sys
from pathlib import Path
import logging

from .release_manager import ReleaseManager
from .utils import validate_semantic_version, format_file_size, get_current_git_commit

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class ReleaseCLI:
    """交互式发布CLI"""
    
    def __init__(self, project_dir: Path = None):
        """
        初始化CLI
        
        Args:
            project_dir: 项目目录，默认为当前目录
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.manager = ReleaseManager(self.project_dir)
    
    def display_banner(self):
        """显示欢迎横幅"""
        print("\n" + "=" * 50)
        print("  Release App - 交互式发布管理工具")
        print("=" * 50)
        print()
    
    def display_git_info(self):
        """显示当前Git信息"""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'binary_manager_v2' / 'core'))
            from git_integration import GitIntegration
            git = GitIntegration(str(self.project_dir))
            git_info = git.get_git_info()
            
            print("📌 当前Git状态:")
            print(f"   分支: {git_info.get('branch', 'N/A')}")
            print(f"   提交: {git_info.get('commit_short', 'N/A')}")
            print(f"   作者: {git_info.get('author', 'N/A')}")
            print(f"   状态: {'有未提交的更改' if git_info.get('is_dirty') else '干净'}")
            print()
        except:
            print("⚠️  无法获取Git信息")
            print()
    
    def prompt_release_type(self) -> str:
        """询问发布类型"""
        print("请选择发布类型:")
        print("  [1] 仅二进制 (编译 + 打包)")
        print("  [2] 仅提交记录 (记录Git元数据)")
        print("  [3] 完整发布 (二进制 + 提交记录)")
        print()
        
        while True:
            choice = input("请输入选项 [1-3]: ").strip()
            if choice in ['1', '2', '3']:
                return {'1': 'binary', '2': 'commit', '3': 'both'}[choice]
            print("❌ 无效选项，请重新输入")
    
    def prompt_version(self) -> str:
        """询问版本号"""
        print()
        while True:
            version = input("请输入版本号 (例如 1.0.0): ").strip()
            if not version:
                print("❌ 版本号不能为空")
                continue
            
            if not validate_semantic_version(version):
                print("⚠️  版本号格式不符合语义化版本规范 (SemVer)")
                confirm = input("是否继续？ [y/N]: ").strip().lower()
                if confirm != 'y':
                    continue
            
            if self.manager.version_tracker.version_exists(version):
                print(f"⚠️  版本 {version} 已存在")
                confirm = input("是否覆盖？ [y/N]: ").strip().lower()
                if confirm != 'y':
                    continue
            
            return version
    
    def prompt_release_notes(self) -> str:
        """询问发布说明"""
        print()
        print("请输入发布说明 (留空则跳过):")
        print("提示: 输入完成后按回车确认")
        notes = input("> ").strip()
        return notes
    
    def prompt_binary_name(self) -> str:
        """询问二进制文件名（可选）"""
        print()
        print("是否指定二进制文件名？ (留空则自动检测)")
        binary_name = input("二进制文件名: ").strip()
        return binary_name if binary_name else None
    
    def prompt_clean_build(self) -> bool:
        """询问是否清理构建"""
        print()
        confirm = input("是否清理后重新构建？ [y/N]: ").strip().lower()
        return confirm == 'y'
    
    def display_result(self, result: dict):
        """显示发布结果"""
        print()
        print("=" * 50)
        
        if result['status'] == 'success':
            print("✅ " + result['message'])
            print(f"   版本: {result['version']}")
            
            if 'binary_info' in result and result['binary_info']:
                info = result['binary_info']
                print(f"   二进制: {info.get('name', 'N/A')}")
                print(f"   大小: {format_file_size(info.get('size', 0))}")
                print(f"   哈希: {info.get('hash', 'N/A')[:20]}...")
            
            if 'git_info' in result and result['git_info']:
                info = result['git_info']
                print(f"   Commit: {info.get('commit_short', 'N/A')}")
            
            print(f"   版本文件: {result.get('version_file', 'N/A')}")
        else:
            print("❌ " + result['message'])
        
        print("=" * 50)
        print()
    
    def run(self):
        """运行主流程"""
        self.display_banner()
        self.display_git_info()
        
        release_type = self.prompt_release_type()
        version = self.prompt_version()
        release_notes = self.prompt_release_notes()
        
        result = None
        
        if release_type == 'binary':
            binary_name = self.prompt_binary_name()
            clean_build = self.prompt_clean_build()
            
            print()
            print("⏳ 开始发布...")
            result = self.manager.release_binary(
                version=version,
                binary_name=binary_name,
                release_notes=release_notes,
                clean_build=clean_build
            )
        
        elif release_type == 'commit':
            print()
            print("⏳ 开始发布...")
            result = self.manager.release_commit(
                version=version,
                release_notes=release_notes
            )
        
        elif release_type == 'both':
            binary_name = self.prompt_binary_name()
            clean_build = self.prompt_clean_build()
            
            print()
            print("⏳ 开始发布...")
            result = self.manager.release_both(
                version=version,
                binary_name=binary_name,
                release_notes=release_notes,
                clean_build=clean_build
            )
        
        self.display_result(result)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Release App - 交互式发布管理工具')
    parser.add_argument(
        '--project-dir',
        type=str,
        default='.',
        help='项目目录（默认为当前目录）'
    )
    
    args = parser.parse_args()
    
    try:
        cli = ReleaseCLI(Path(args.project_dir))
        cli.run()
    except KeyboardInterrupt:
        print("\n\n⚠️  用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
