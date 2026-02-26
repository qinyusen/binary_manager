#!/usr/bin/env python3
"""
Binary Manager V2 - 交互式发布工具

提供友好的命令行交互界面，简化发布流程
"""
import sys
import os
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from binary_manager_v2.application.publisher_service import PublisherService
from binary_manager_v2.domain.services import FileScanner, HashCalculator
from binary_manager_v2.infrastructure.git.git_service import GitService
from binary_manager_v2.infrastructure.storage.local_storage import LocalStorage
from binary_manager_v2.infrastructure.storage.s3_storage import S3Storage


class Colors:
    """终端颜色"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*60}{Colors.END}\n")


def print_info(text):
    """打印信息"""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def print_success(text):
    """打印成功信息"""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_warning(text):
    """打印警告"""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_error(text):
    """打印错误"""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_step(step, total, text):
    """打印步骤"""
    print(f"\n{Colors.BOLD}[{step}/{total}] {text}{Colors.END}")


def input_prompt(prompt, default=None, required=True):
    """输入提示"""
    if default:
        full_prompt = f"{Colors.CYAN}➜ {prompt} [{default}]: {Colors.END}"
    else:
        full_prompt = f"{Colors.CYAN}➜ {prompt}: {Colors.END}"
    
    value = input(full_prompt).strip()
    
    if not value and default:
        return default
    if not value and required:
        print_warning("此项为必填，请重新输入")
        return input_prompt(prompt, default, required)
    
    return value


def input_yes_no(prompt, default=True):
    """是/否输入"""
    default_str = "Y/n" if default else "y/N"
    full_prompt = f"{Colors.CYAN}➜ {prompt} [{default_str}]: {Colors.END}"
    
    value = input(full_prompt).strip().lower()
    
    if not value:
        return default
    
    return value in ['y', 'yes', '是', 'true', '1']


def input_choice(prompt, choices, default=0):
    """选择输入"""
    print(f"\n{Colors.YELLOW}{prompt}:{Colors.END}")
    for i, choice in enumerate(choices):
        marker = "→" if i == default else " "
        print(f"  {marker} {i + 1}. {choice}")
    
    choice_input = input(f"\n{Colors.CYAN}➜ 请选择 [1-{len(choices)}]: {Colors.END}").strip()
    
    if not choice_input:
        return default
    
    try:
        index = int(choice_input) - 1
        if 0 <= index < len(choices):
            return index
        print_error(f"请输入 1-{len(choices)} 之间的数字")
        return input_choice(prompt, choices, default)
    except ValueError:
        print_error("请输入有效的数字")
        return input_choice(prompt, choices, default)


def validate_source_dir(path_str):
    """验证源目录"""
    path = Path(path_str).expanduser().resolve()
    
    if not path.exists():
        print_error(f"目录不存在: {path}")
        return None
    
    if not path.is_dir():
        print_error(f"不是目录: {path}")
        return None
    
    return path


def validate_package_name(name):
    """验证包名"""
    if not name:
        print_error("包名不能为空")
        return None
    
    # 简单验证：只允许字母、数字、下划线、中划线
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        print_warning("包名建议只包含字母、数字、下划线和中划线")
    
    return name


def validate_version(version):
    """验证版本号"""
    if not version:
        print_error("版本号不能为空")
        return None
    
    # 简单的语义化版本验证
    import re
    if not re.match(r'^\d+\.\d+\.\d+', version):
        print_warning("版本号格式建议为: 主版本.次版本.修订号 (如 1.0.0)")
    
    return version


def display_file_list(files):
    """显示文件列表"""
    if not files:
        print_warning("未找到文件")
        return
    
    print(f"\n{Colors.GREEN}找到 {len(files)} 个文件:{Colors.END}")
    
    # 按类型分组
    by_type = {}
    for file_info in files:
        ext = Path(file_info.path).suffix or '无扩展名'
        if ext not in by_type:
            by_type[ext] = []
        by_type[ext].append(file_info)
    
    for ext, file_list in sorted(by_type.items()):
        print(f"\n  {Colors.CYAN}{ext} 文件 ({len(file_list)}):{Colors.END}")
        for file_info in file_list[:5]:  # 只显示前5个
            print(f"    - {file_info.path} ({file_info.size} bytes)")
        if len(file_list) > 5:
            print(f"    ... 还有 {len(file_list) - 5} 个文件")


def interactive_publish():
    """交互式发布流程"""
    print_header("Binary Manager V2 - 交互式发布工具")
    
    total_steps = 7
    
    # 步骤1: 输入源目录
    print_step(1, total_steps, "指定源目录")
    print_info("请输入要发布的源目录路径")
    
    while True:
        source_dir_str = input_prompt("源目录", default=".")
        source_dir = validate_source_dir(source_dir_str)
        if source_dir:
            break
    
    print_success(f"源目录: {source_dir}")
    
    # 步骤2: 扫描文件
    print_step(2, total_steps, "扫描文件")
    print_info("正在扫描文件...")
    
    try:
        file_scanner = FileScanner()
        files, scan_info = file_scanner.scan_directory(str(source_dir))
        print_success(f"扫描完成，找到 {len(files)} 个文件")
        display_file_list(files)
    except Exception as e:
        print_error(f"扫描失败: {e}")
        return
    
    # 确认继续
    if not input_yes_no("\n是否继续发布?", default=True):
        print_warning("发布已取消")
        return
    
    # 步骤3: 输入包名
    print_step(3, total_steps, "设置包信息")
    package_name = None
    while not package_name:
        package_name = validate_package_name(
            input_prompt("包名", default=source_dir.name)
        )
    
    # 步骤4: 输入版本号
    version = None
    while not version:
        version = validate_version(
            input_prompt("版本号", default="1.0.0")
        )
    
    # 步骤5: 输入描述
    description = input_prompt("描述", default="", required=False)
    
    # 步骤6: 选择存储类型
    print_step(5, total_steps, "选择存储位置")
    storage_type = input_choice(
        "存储位置",
        ["本地存储", "S3云存储"],
        default=0
    )
    
    storage_path = "./releases"
    s3_bucket = None
    s3_region = None
    
    if storage_type == 0:  # 本地存储
        storage_path_input = input_prompt("存储路径", default="./releases", required=False)
        if storage_path_input:
            storage_path = storage_path_input
    else:  # S3存储
        s3_bucket = input_prompt("S3 Bucket名称", required=True)
        s3_region = input_prompt("AWS区域", default="us-east-1", required=False)
        s3_access_key = input_prompt("Access Key ID", required=True)
        s3_secret_key = input_prompt("Secret Access Key", required=True)
        
        # 创建S3存储
        storage = S3Storage(
            bucket=s3_bucket,
            region=s3_region,
            access_key=s3_access_key,
            secret_key=s3_secret_key
        )
    
    # 步骤7: 确认并发布
    print_step(7, total_steps, "确认发布信息")
    print(f"\n{Colors.BOLD}发布信息摘要:{Colors.END}")
    print(f"  源目录:   {source_dir}")
    print(f"  包名:     {package_name}")
    print(f"  版本:     {version}")
    print(f"  描述:     {description or '无'}")
    print(f"  文件数:   {len(files)}")
    print(f"  总大小:   {sum(f.size for f in files)} bytes")
    
    if storage_type == 0:
        print(f"  存储:     本地 ({storage_path})")
    else:
        print(f"  存储:     S3 ({s3_bucket}/{s3_region})")
    
    # 确认发布
    if not input_yes_no("\n确认发布?", default=True):
        print_warning("发布已取消")
        return
    
    # 执行发布
    print("\n" + "="*60)
    print_info("开始发布...")
    print("="*60 + "\n")
    
    try:
        publisher = PublisherService(
            storage_path=storage_path,
            db_path="./binary_manager_v2/database/binary_manager.db"
        )
        
        if storage_type == 0:
            # 本地发布
            result = publisher.publish(
                source_dir=str(source_dir),
                package_name=package_name,
                version=version,
                description=description
            )
        else:
            # S3发布
            result = publisher.publish_to_s3(
                source_dir=str(source_dir),
                package_name=package_name,
                version=version,
                s3_storage=storage,
                description=description
            )
        
        # 发布成功
        print("\n" + "="*60)
        print_success("发布成功!")
        print("="*60 + "\n")
        
        print(f"  包名:        {result['package'].package_name}")
        print(f"  版本:        {result['package'].version}")
        print(f"  包ID:        {result['package_id']}")
        print(f"  存档文件:    {result['archive_path']}")
        print(f"  配置文件:    {result['config_path']}")
        
        if result['package'].git_info:
            print(f"\n  Git信息:")
            print(f"    分支:    {result['package'].git_info.branch}")
            print(f"    提交:    {result['package'].git_info.commit_short}")
            if result['package'].git_info.commit_message:
                msg = result['package'].git_info.commit_message[:50]
                print(f"    消息:    {msg}...")
        
        print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}{Colors.BOLD}{'🎉 发布完成！':^58}{Colors.END}")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
        
    except Exception as e:
        print("\n" + "="*60)
        print_error("发布失败")
        print("="*60 + "\n")
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()


def quick_publish(source_dir=None, package_name=None, version="1.0.0"):
    """快速发布（使用默认值）"""
    if not source_dir:
        print_error("请指定源目录")
        return
    
    source_path = Path(source_dir).expanduser().resolve()
    if not source_path.exists():
        print_error(f"源目录不存在: {source_path}")
        return
    
    if not package_name:
        package_name = source_path.name
    
    print_info(f"快速发布: {package_name} {version}")
    print(f"  源目录: {source_path}")
    
    try:
        publisher = PublisherService(
            storage_path="./releases",
            db_path="./binary_manager_v2/database/binary_manager.db"
        )
        
        result = publisher.publish(
            source_dir=str(source_path),
            package_name=package_name,
            version=version,
            description=f"{package_name} {version}"
        )
        
        print_success(f"发布成功: {package_name} v{version}")
        print(f"  包ID: {result['package_id']}")
        
    except Exception as e:
        print_error(f"发布失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Binary Manager V2 - 交互式发布工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 交互式发布
  python3 publish_tool.py
  
  # 快速发布
  python3 publish_tool.py --quick ./my_project my_app 1.0.0
  
  # 查看帮助
  python3 publish_tool.py --help
        """
    )
    
    parser.add_argument(
        '--quick',
        nargs=2,
        metavar=('SOURCE', 'NAME'),
        help='快速发布模式: SOURCE_DIR PACKAGE_NAME'
    )
    
    parser.add_argument(
        '--version',
        metavar='VERSION',
        default='1.0.0',
        help='版本号 (默认: 1.0.0)'
    )
    
    args = parser.parse_args()
    
    try:
        if args.quick:
            # 快速发布模式
            source_dir, package_name = args.quick
            quick_publish(source_dir, package_name, args.version)
        else:
            # 交互式发布模式
            interactive_publish()
    except KeyboardInterrupt:
        print_warning("\n\n用户取消")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
