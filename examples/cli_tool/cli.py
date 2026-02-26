#!/usr/bin/env python3
"""
CLI Tool - 命令行工具
一个功能丰富的命令行工具示例
"""
import sys
import argparse
from pathlib import Path
from commands.file_ops import FileCommands
from commands.text_ops import TextCommands
from commands.sys_ops import SystemCommands
from utils import print_banner, print_error, print_success


class CLI:
    """命令行工具主类"""
    
    def __init__(self):
        """初始化CLI"""
        self.parser = self._create_parser()
        self.file_commands = FileCommands()
        self.text_commands = TextCommands()
        self.sys_commands = SystemCommands()
    
    def _create_parser(self):
        """创建参数解析器"""
        parser = argparse.ArgumentParser(
            prog='cli_tool',
            description='功能丰富的命令行工具',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        subparsers = parser.add_subparsers(dest='command', help='可用命令')
        
        # 文件操作命令
        file_parser = subparsers.add_parser('file', help='文件操作')
        file_subparsers = file_parser.add_subparsers(dest='file_command')
        
        # file stats
        file_subparsers.add_parser('stats', help='统计文件信息').add_argument('path', help='文件路径')
        
        # file find-duplicates
        file_subparsers.add_parser('find-duplicates', help='查找重复文件').add_argument('path', help='目录路径')
        
        # file rename
        rename_parser = file_subparsers.add_parser('rename', help='批量重命名')
        rename_parser.add_argument('path', help='目录路径')
        rename_parser.add_argument('--pattern', help='文件名模式', default='*')
        rename_parser.add_argument('--prefix', help='文件名前缀', default='')
        
        # 文本处理命令
        text_parser = subparsers.add_parser('text', help='文本处理')
        text_subparsers = text_parser.add_subparsers(dest='text_command')
        
        # text count
        text_subparsers.add_parser('count', help='统计文本').add_argument('path', help='文件路径')
        
        # text replace
        replace_parser = text_subparsers.add_parser('replace', help='搜索替换')
        replace_parser.add_argument('path', help='文件路径')
        replace_parser.add_argument('--old', help='要替换的文本', required=True)
        replace_parser.add_argument('--new', help='替换后的文本', required=True)
        
        # text format-json
        text_subparsers.add_parser('format-json', help='格式化JSON').add_argument('path', help='JSON文件路径')
        
        # 系统操作命令
        sys_parser = subparsers.add_parser('sys', help='系统操作')
        sys_subparsers = sys_parser.add_subparsers(dest='sys_command')
        
        # sys info
        sys_subparsers.add_parser('info', help='系统信息')
        
        # sys disk
        sys_subparsers.add_parser('disk', help='磁盘使用')
        
        # sys processes
        sys_subparsers.add_parser('processes', help='进程列表')
        
        return parser
    
    def run(self, args=None):
        """运行CLI"""
        if args is None:
            args = sys.argv[1:]
        
        # 如果没有参数，显示帮助
        if not args:
            print_banner()
            self.parser.print_help()
            return 0
        
        # 解析参数
        parsed_args = self.parser.parse_args(args)
        
        # 执行命令
        try:
            if parsed_args.command == 'file':
                return self._run_file_command(parsed_args)
            elif parsed_args.command == 'text':
                return self._run_text_command(parsed_args)
            elif parsed_args.command == 'sys':
                return self._run_sys_command(parsed_args)
            else:
                self.parser.print_help()
                return 0
        except Exception as e:
            print_error(f"错误: {e}")
            return 1
    
    def _run_file_command(self, args):
        """运行文件操作命令"""
        if args.file_command == 'stats':
            result = self.file_commands.stats(args.path)
            print(f"\n文件统计信息:")
            print(f"  路径: {result['path']}")
            print(f"  大小: {result['size']} 字节")
            print(f"  行数: {result['lines']}")
            print(f"  单词数: {result['words']}")
            print_success("完成!")
            return 0
        elif args.file_command == 'find-duplicates':
            duplicates = self.file_commands.find_duplicates(args.path)
            if duplicates:
                print(f"\n发现 {len(duplicates)} 组重复文件:")
                for group in duplicates:
                    print(f"\n  组 {group['id']}:")
                    for file in group['files']:
                        print(f"    - {file}")
            else:
                print("\n未发现重复文件")
            print_success("完成!")
            return 0
        elif args.file_command == 'rename':
            count = self.file_commands.rename(args.path, args.pattern, args.prefix)
            print(f"\n已重命名 {count} 个文件")
            print_success("完成!")
            return 0
        else:
            self.parser.print_help()
            return 1
    
    def _run_text_command(self, args):
        """运行文本处理命令"""
        if args.text_command == 'count':
            result = self.text_commands.count(args.path)
            print(f"\n文本统计:")
            print(f"  字符数: {result['chars']}")
            print(f"  单词数: {result['words']}")
            print(f"  行数: {result['lines']}")
            print_success("完成!")
            return 0
        elif args.text_command == 'replace':
            count = self.text_commands.replace(args.path, args.old, args.new)
            print(f"\n已替换 {count} 处")
            print_success("完成!")
            return 0
        elif args.text_command == 'format-json':
            self.text_commands.format_json(args.path)
            print_success(f"已格式化 {args.path}")
            return 0
        else:
            self.parser.print_help()
            return 1
    
    def _run_sys_command(self, args):
        """运行系统操作命令"""
        if args.sys_command == 'info':
            info = self.sys_commands.info()
            print(f"\n系统信息:")
            print(f"  操作系统: {info['os']}")
            print(f"  架构: {info['arch']}")
            print(f"  主机名: {info['hostname']}")
            print(f"  Python版本: {info['python_version']}")
            print_success("完成!")
            return 0
        elif args.sys_command == 'disk':
            disks = self.sys_commands.disk()
            print(f"\n磁盘使用:")
            for disk in disks:
                print(f"  {disk['device']}: {disk['used']} / {disk['total']} ({disk['percent']}%)")
            print_success("完成!")
            return 0
        elif args.sys_command == 'processes':
            processes = self.sys_commands.processes()
            print(f"\n进程列表 (前10个):")
            for proc in processes[:10]:
                print(f"  {proc['pid']}: {proc['name']} ({proc['cpu']}% CPU)")
            print_success("完成!")
            return 0
        else:
            self.parser.print_help()
            return 1


def main():
    """主函数"""
    print_banner()
    cli = CLI()
    sys.exit(cli.run())


if __name__ == "__main__":
    main()
