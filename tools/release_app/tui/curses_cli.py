"""
基于curses的交互式CLI
实现Release App的TUI界面
"""

import curses
import sys
from pathlib import Path
from typing import Optional, Dict

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.release_app.release_manager import ReleaseManager
from tools.release_app.utils import get_publisher_info, format_file_size
from .widgets import Menu, Form, ProgressBar, MessageBox, ConfirmDialog
from .utils import init_colors, draw_border, safe_addstr


class CursesCLI:
    """curses交互式界面"""
    
    def __init__(self, project_dir: Path = None):
        """
        初始化CLI
        
        Args:
            project_dir: 项目目录
        """
        self.project_dir = Path(project_dir) if project_dir else Path.cwd()
        self.manager = ReleaseManager(self.project_dir)
        self.current_screen = "main"
    
    def run(self):
        """运行主程序"""
        curses.wrapper(self._main)
    
    def _main(self, stdscr):
        """
        主循环
        
        Args:
            stdscr: curses标准屏幕
        """
        self.stdscr = stdscr
        init_colors()
        curses.curs_set(0)  # 隐藏光标
        
        self.current_screen = "main"
        
        while True:
            if self.current_screen == "main":
                self._main_screen()
            elif self.current_screen == "release":
                self._release_screen()
            elif self.current_screen == "history":
                self._history_screen()
            elif self.current_screen == "exit":
                break
    
    def _main_screen(self):
        """主菜单界面"""
        menu = Menu([
            "发布新版本",
            "查看历史版本",
            "退出"
        ], "Release App - 主菜单")
        
        while True:
            self.stdscr.clear()
            draw_border(self.stdscr, "Release App v1.0")
            
            # 显示Git信息
            self._show_git_info(3, 2)
            
            # 绘制菜单
            menu.draw(self.stdscr, 10, 4)
            
            # 底部提示
            hint = "使用↑↓选择，Enter确认，Esc退出"
            safe_addstr(self.stdscr, curses.LINES - 2, 2, hint)
            
            self.stdscr.refresh()
            
            key = self.stdscr.getch()
            result = menu.handle_input(key)
            
            if key == 27:  # ESC
                self.current_screen = "exit"
                break
            elif result == "发布新版本":
                self.current_screen = "release"
                break
            elif result == "查看历史版本":
                self.current_screen = "history"
                break
            elif result == "退出":
                self.current_screen = "exit"
                break
    
    def _release_screen(self):
        """发布界面"""
        # 步骤1: 选择发布类型
        release_type = self._select_release_type()
        if not release_type:
            self.current_screen = "main"
            return
        
        # 步骤2: 输入版本信息
        version_info = self._input_version_info()
        if not version_info:
            self.current_screen = "main"
            return
        
        # 步骤3: 确认并发布
        if self._confirm_release(release_type, version_info):
            self._do_release(release_type, version_info)
        
        self.current_screen = "main"
    
    def _select_release_type(self) -> Optional[str]:
        """选择发布类型"""
        menu = Menu([
            "仅二进制 (编译 + 打包)",
            "仅提交记录 (记录Git元数据)",
            "完整发布 (二进制 + 提交记录)"
        ], "选择发布类型")
        
        while True:
            self.stdscr.clear()
            draw_border(self.stdscr, "Release App")
            
            menu.draw(self.stdscr, 5, 4)
            
            hint = "↑↓选择，Enter确认，Esc返回"
            safe_addstr(self.stdscr, curses.LINES - 2, 2, hint)
            
            self.stdscr.refresh()
            
            key = self.stdscr.getch()
            result = menu.handle_input(key)
            
            if key == 27:
                return None
            elif result:
                type_map = {
                    "仅二进制 (编译 + 打包)": "binary",
                    "仅提交记录 (记录Git元数据)": "commit",
                    "完整发布 (二进制 + 提交记录)": "both"
                }
                return type_map.get(result)
    
    def _input_version_info(self) -> Optional[Dict]:
        """输入版本信息"""
        form = Form({
            'version': {
                'label': '版本号',
                'default': '1.0.0'
            },
            'notes': {
                'label': '发布说明',
                'default': ''
            },
            'binary_name': {
                'label': '二进制文件名 (可选)',
                'default': ''
            }
        }, "版本信息")
        
        while True:
            self.stdscr.clear()
            draw_border(self.stdscr, "版本信息")
            
            form.draw(self.stdscr, 5, 4)
            
            hint = "↑↓移动字段，输入内容，Enter完成，Esc取消"
            safe_addstr(self.stdscr, curses.LINES - 2, 2, hint)
            
            self.stdscr.refresh()
            
            key = self.stdscr.getch()
            result = form.handle_input(key)
            
            if key == 27:
                return None
            elif result:
                return form.get_values()
    
    def _confirm_release(self, release_type: str, version_info: Dict) -> bool:
        """确认发布"""
        self.stdscr.clear()
        draw_border(self.stdscr, "确认发布")
        
        y = 3
        
        # 显示发布摘要
        safe_addstr(self.stdscr, y, 4, "发布类型:", curses.A_BOLD)
        type_names = {
            'binary': '仅二进制',
            'commit': '仅提交',
            'both': '完整发布'
        }
        safe_addstr(self.stdscr, y, 18, type_names.get(release_type))
        y += 2
        
        safe_addstr(self.stdscr, y, 4, "版本号:", curses.A_BOLD)
        safe_addstr(self.stdscr, y, 18, version_info.get('version', ''))
        y += 2
        
        if version_info.get('notes'):
            safe_addstr(self.stdscr, y, 4, "发布说明:", curses.A_BOLD)
            safe_addstr(self.stdscr, y, 18, version_info['notes'])
            y += 2
        
        if version_info.get('binary_name'):
            safe_addstr(self.stdscr, y, 4, "二进制文件:", curses.A_BOLD)
            safe_addstr(self.stdscr, y, 18, version_info['binary_name'])
            y += 2
        
        y += 1
        safe_addstr(self.stdscr, y, 4, "确认发布？", curses.A_BOLD | curses.A_BLINK)
        y += 2
        
        safe_addstr(self.stdscr, y, 4, "[Y] 确认  [N] 取消")
        
        self.stdscr.refresh()
        
        while True:
            key = self.stdscr.getch()
            if key in (ord('y'), ord('Y')):
                return True
            elif key in (ord('n'), ord('N'), 27):
                return False
    
    def _do_release(self, release_type: str, version_info: Dict):
        """执行发布"""
        self.stdscr.clear()
        draw_border(self.stdscr, "发布中...")
        
        y = 5
        
        # 创建进度条
        progress = ProgressBar(100, 40)
        
        safe_addstr(self.stdscr, y, 4, "正在发布...")
        y += 3
        
        progress.draw(self.stdscr, y, 4)
        self.stdscr.refresh()
        
        try:
            version = version_info.get('version')
            notes = version_info.get('notes', '')
            binary_name = version_info.get('binary_name') or None
            
            # 模拟进度
            progress.update(10)
            progress.draw(self.stdscr, y, 4)
            self.stdscr.refresh()
            
            if release_type == 'binary':
                result = self.manager.release_binary(
                    version, binary_name, notes, clean_build=False
                )
            elif release_type == 'commit':
                result = self.manager.release_commit(
                    version, notes
                )
            else:  # both
                result = self.manager.release_both(
                    version, binary_name, notes, clean_build=False
                )
            
            progress.update(100)
            progress.draw(self.stdscr, y, 4)
            self.stdscr.refresh()
            
            # 显示结果
            curses.napms(500)  # 等待500ms
            
            self._show_result(result)
        
        except Exception as e:
            MessageBox.show(self.stdscr, f"发布失败: {str(e)}", "错误")
    
    def _show_result(self, result: Dict):
        """显示发布结果"""
        self.stdscr.clear()
        draw_border(self.stdscr, "发布结果")
        
        y = 3
        
        if result.get('status') == 'success':
            safe_addstr(self.stdscr, y, 4, "✓ 发布成功！", curses.color_pair(2))
            y += 2
            
            safe_addstr(self.stdscr, y, 4, "版本:", curses.A_BOLD)
            safe_addstr(self.stdscr, y, 18, result.get('version', ''))
            y += 2
            
            if result.get('binary_info'):
                info = result['binary_info']
                safe_addstr(self.stdscr, y, 4, "二进制:", curses.A_BOLD)
                safe_addstr(self.stdscr, y, 18, info.get('name', 'N/A'))
                y += 2
                safe_addstr(self.stdscr, y, 4, "大小:", curses.A_BOLD)
                safe_addstr(self.stdscr, y, 18, format_file_size(info.get('size', 0)))
                y += 2
                safe_addstr(self.stdscr, y, 4, "哈希:", curses.A_BOLD)
                hash_short = info.get('hash', '')[:30]
                safe_addstr(self.stdscr, y, 18, hash_short)
                y += 2
            
            if result.get('git_info'):
                info = result['git_info']
                safe_addstr(self.stdscr, y, 4, "Commit:", curses.A_BOLD)
                safe_addstr(self.stdscr, y, 18, info.get('commit_short', 'N/A'))
                y += 2
            
            safe_addstr(self.stdscr, y, 4, "版本文件:", curses.A_BOLD)
            version_file = result.get('version_file', '')
            safe_addstr(self.stdscr, y, 18, version_file[:40])
            y += 2
        else:
            safe_addstr(self.stdscr, y, 4, "✗ 发布失败", curses.color_pair(3))
            y += 2
            safe_addstr(self.stdscr, y, 4, result.get('message', '未知错误'))
            y += 2
        
        safe_addstr(self.stdscr, curses.LINES - 2, 4, "按任意键返回...")
        self.stdscr.refresh()
        self.stdscr.getch()
    
    def _history_screen(self):
        """历史版本界面"""
        versions = self.manager.version_tracker.list_versions()
        
        if not versions:
            MessageBox.show(self.stdscr, "暂无历史版本", "提示")
            self.current_screen = "main"
            return
        
        # 转换为菜单项
        menu_items = []
        for v in versions:
            item = f"{v['version']} - {v['created_at'][:19]}"
            menu_items.append(item)
        
        menu_items.append("返回")
        
        menu = Menu(menu_items, "历史版本")
        
        while True:
            self.stdscr.clear()
            draw_border(self.stdscr, "历史版本")
            
            menu.draw(self.stdscr, 3, 4)
            
            # 显示版本详情
            selected_idx = menu.selected
            if selected_idx < len(versions):
                version_data = self.manager.version_tracker.load_version_file(
                    versions[selected_idx]['version']
                )
                
                if version_data:
                    self._show_version_detail(version_data)
            
            hint = "↑↓选择，Enter查看详情，Esc返回"
            safe_addstr(self.stdscr, curses.LINES - 2, 2, hint)
            
            self.stdscr.refresh()
            
            key = self.stdscr.getch()
            result = menu.handle_input(key)
            
            if key == 27 or result == "返回":
                self.current_screen = "main"
                break
            elif result and result != "返回":
                # 显示详情
                idx = menu_items.index(result)
                version_data = self.manager.version_tracker.load_version_file(
                    versions[idx]['version']
                )
                self._show_version_detail_popup(version_data)
    
    def _show_version_detail(self, version_data: Dict):
        """显示版本详情（底部面板）"""
        detail_y = curses.LINES - 10
        
        safe_addstr(self.stdscr, detail_y, 2, "-" * (curses.COLS - 4))
        detail_y += 1
        
        type_name = {
            'binary': '二进制',
            'commit': '提交',
            'both': '完整'
        }.get(version_data.get('release_type', ''), '未知')
        
        safe_addstr(self.stdscr, detail_y, 4, f"类型: {type_name}")
        detail_y += 1
        
        notes = version_data.get('release_notes', '')
        if notes:
            safe_addstr(self.stdscr, detail_y, 4, f"说明: {notes[:40]}")
            detail_y += 1
    
    def _show_version_detail_popup(self, version_data: Dict):
        """弹出式版本详情"""
        message = f"版本: {version_data.get('version', 'N/A')}\n"
        message += f"时间: {version_data.get('created_at', 'N/A')}\n"
        message += f"类型: {version_data.get('release_type', 'N/A')}\n\n"
        
        if version_data.get('binary'):
            binary = version_data['binary']
            message += f"二进制: {binary.get('name', 'N/A')}\n"
            message += f"大小: {format_file_size(binary.get('size', 0))}\n\n"
        
        if version_data.get('git'):
            git = version_data['git']
            message += f"Commit: {git.get('commit_short', 'N/A')}\n"
            message += f"分支: {git.get('branch', 'N/A')}\n"
            message += f"作者: {git.get('author', 'N/A')}\n"
        
        MessageBox.show(self.stdscr, message, "版本详情")
    
    def _show_git_info(self, y: int, x: int):
        """显示Git信息"""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'binary_manager_v2' / 'core'))
            from git_integration import GitIntegration
            
            git = GitIntegration(str(self.project_dir))
            git_info = git.get_git_info()
            
            safe_addstr(self.stdscr, y, x, "Git状态:", curses.A_BOLD)
            safe_addstr(self.stdscr, y + 1, x, f"  分支: {git_info.get('branch', 'N/A')}")
            safe_addstr(self.stdscr, y + 2, x, f"  提交: {git_info.get('commit_short', 'N/A')}")
            safe_addstr(self.stdscr, y + 3, x, f"  作者: {git_info.get('author', 'N/A')}")
            safe_addstr(self.stdscr, y + 4, x, f"  状态: {'有未提交更改' if git_info.get('is_dirty') else '干净'}")
        except:
            safe_addstr(self.stdscr, y, x, "Git信息: 不可用")


def main_curses():
    """curses版本主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Release App - TUI版本')
    parser.add_argument('--project-dir', type=str, default='.', help='项目目录')
    
    args = parser.parse_args()
    
    try:
        cli = CursesCLI(Path(args.project_dir))
        cli.run()
    except Exception as e:
        curses.endwin()
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
