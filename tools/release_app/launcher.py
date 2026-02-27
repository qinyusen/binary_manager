#!/usr/bin/env python3
"""
Release App 启动器
自动选择最佳的界面模式
"""

import sys
import os
from pathlib import Path


def check_curses_support():
    """检查是否支持curses"""
    try:
        import curses
        # 测试curses是否可用
        curses.setupterm()
        return True
    except:
        return False


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Release App - 交互式发布管理工具')
    parser.add_argument('--project-dir', type=str, default='.', help='项目目录')
    parser.add_argument('--tui', action='store_true', help='使用TUI界面（如果支持）')
    parser.add_argument('--cli', action='store_true', help='使用CLI界面（问答式）')
    
    args = parser.parse_args()
    
    # 决定使用哪种界面
    use_tui = False
    
    if args.cli:
        use_tui = False
    elif args.tui:
        use_tui = True
    else:
        # 自动检测
        use_tui = check_curses_support()
    
    if use_tui:
        print("启动TUI界面...")
        try:
            from tools.release_app.tui.curses_cli import main_curses
            sys.argv = ['release_app', '--project-dir', args.project_dir]
            main_curses()
        except Exception as e:
            print(f"TUI启动失败: {e}")
            print("回退到CLI模式...")
            from tools.release_app.cli import main as main_cli
            main_cli()
    else:
        from tools.release_app.cli import main as main_cli
        sys.argv = ['release_app', '--project-dir', args.project_dir]
        main_cli()


if __name__ == '__main__':
    main()
