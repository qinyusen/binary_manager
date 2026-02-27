"""
curses UI组件
包含菜单、表单、进度条等基础组件
"""

import curses
from typing import List, Callable, Dict, Any, Optional


class Menu:
    """菜单组件"""
    
    def __init__(self, items: List[str], title: str = "Menu"):
        """
        初始化菜单
        
        Args:
            items: 菜单项列表
            title: 菜单标题
        """
        self.items = items
        self.title = title
        self.selected = 0
        self.start_y = 3
    
    def draw(self, stdscr, y: int, x: int):
        """
        绘制菜单
        
        Args:
            stdscr: curses窗口对象
            y: 起始Y坐标
            x: 起始X坐标
        """
        # 绘制标题
        stdscr.addstr(y, x, self.title, curses.A_BOLD)
        stdscr.addstr(y + 1, x, "=" * len(self.title))
        
        # 绘制菜单项
        for i, item in enumerate(self.items):
            menu_y = y + self.start_y + i
            prefix = "► " if i == self.selected else "  "
            
            if i == self.selected:
                stdscr.addstr(menu_y, x, prefix + item, curses.A_REVERSE)
            else:
                stdscr.addstr(menu_y, x, prefix + item)
        
        return len(self.items) + self.start_y + 1
    
    def handle_input(self, key: int) -> Optional[str]:
        """
        处理输入
        
        Args:
            key: 按键码
        
        Returns:
            如果是确认键返回选中的项，否则返回None
        """
        if key == curses.KEY_UP:
            self.selected = (self.selected - 1) % len(self.items)
        elif key == curses.KEY_DOWN:
            self.selected = (self.selected + 1) % len(self.items)
        elif key == ord('\n') or key == ord(' '):
            return self.items[self.selected]
        elif key >= ord('1') and key <= ord('9'):
            idx = key - ord('1')
            if idx < len(self.items):
                return self.items[idx]
        
        return None
    
    def get_selected(self) -> str:
        """获取当前选中的项"""
        return self.items[self.selected]


class Form:
    """表单组件"""
    
    def __init__(self, fields: Dict[str, Dict], title: str = "Form"):
        """
        初始化表单
        
        Args:
            fields: 字段字典，格式: {字段名: {label, default, validator}}
            title: 表单标题
        """
        self.fields = fields
        self.field_names = list(fields.keys())
        self.title = title
        self.current_field = 0
        self.values = {name: data.get('default', '') for name, data in fields.items()}
    
    def draw(self, stdscr, y: int, x: int):
        """
        绘制表单
        
        Args:
            stdscr: curses窗口对象
            y: 起始Y坐标
            x: 起始X坐标
        """
        # 绘制标题
        stdscr.addstr(y, x, self.title, curses.A_BOLD)
        stdscr.addstr(y + 1, x, "=" * len(self.title))
        
        # 绘制字段
        for i, name in enumerate(self.field_names):
            field_data = self.fields[name]
            label = field_data.get('label', name)
            value = self.values[name]
            
            field_y = y + 3 + i * 2
            prefix = "► " if i == self.current_field else "  "
            
            if i == self.current_field:
                attr = curses.A_REVERSE
            else:
                attr = curses.A_NORMAL
            
            stdscr.addstr(field_y, x, f"{prefix}{label}: ", attr)
            stdscr.addstr(field_y, x + len(prefix) + len(label) + 2, value, attr)
        
        return len(self.fields) * 2 + 4
    
    def handle_input(self, key: int) -> Optional[Dict[str, str]]:
        """
        处理输入
        
        Args:
            key: 按键码
        
        Returns:
            如果完成返回所有字段值，否则返回None
        """
        current_name = self.field_names[self.current_field]
        
        if key == curses.KEY_UP:
            self.current_field = (self.current_field - 1) % len(self.field_names)
        elif key == curses.KEY_DOWN:
            self.current_field = (self.current_field + 1) % len(self.field_names)
        elif key == ord('\n'):
            if self.current_field == len(self.field_names) - 1:
                return self.values
        elif key == curses.KEY_BACKSPACE or key == 127:
            self.values[current_name] = self.values[current_name][:-1]
        elif 32 <= key <= 126:  # 可打印字符
            self.values[current_name] += chr(key)
        
        return None
    
    def get_values(self) -> Dict[str, str]:
        """获取所有字段值"""
        return self.values


class ProgressBar:
    """进度条组件"""
    
    def __init__(self, total: int, width: int = 50):
        """
        初始化进度条
        
        Args:
            total: 总量
            width: 进度条宽度
        """
        self.total = total
        self.width = width
        self.current = 0
    
    def draw(self, stdscr, y: int, x: int, message: str = ""):
        """
        绘制进度条
        
        Args:
            stdscr: curses窗口对象
            y: 起始Y坐标
            x: 起始X坐标
            message: 附加消息
        """
        percent = self.current / self.total if self.total > 0 else 0
        filled = int(self.width * percent)
        
        bar = "█" * filled + "░" * (self.width - filled)
        
        if message:
            stdscr.addstr(y, x, message)
            stdscr.addstr(y + 1, x, f"[{bar}] {percent*100:.1f}%")
        else:
            stdscr.addstr(y, x, f"[{bar}] {percent*100:.1f}%")
        
        return 2
    
    def update(self, current: int):
        """更新当前进度"""
        self.current = min(current, self.total)
    
    def increment(self, amount: int = 1):
        """增加进度"""
        self.current = min(self.current + amount, self.total)


class MessageBox:
    """消息框组件"""
    
    @staticmethod
    def show(stdscr, message: str, title: str = "Message", 
             y: int = 5, x: int = 5, height: int = 10, width: int = 50):
        """
        显示消息框
        
        Args:
            stdscr: curses窗口对象
            message: 消息内容
            title: 标题
            y, x, height, width: 位置和大小
        """
        # 创建窗口
        win = curses.newwin(height, width, y, x)
        win.box()
        
        # 标题
        win.addstr(0, 2, f" {title} ")
        
        # 消息内容（自动换行）
        lines = []
        current_line = ""
        for word in message.split():
            if len(current_line) + len(word) + 1 > width - 4:
                lines.append(current_line)
                current_line = word
            else:
                if current_line:
                    current_line += " "
                current_line += word
        if current_line:
            lines.append(current_line)
        
        # 显示消息（最多显示height-4行）
        for i, line in enumerate(lines[:height-4]):
            win.addstr(i + 2, 2, line)
        
        # 提示
        win.addstr(height - 2, 2, "按任意键继续...")
        
        win.refresh()
        win.getch()
        del win


class ConfirmDialog:
    """确认对话框"""
    
    @staticmethod
    def show(stdscr, message: str, title: str = "Confirm") -> bool:
        """
        显示确认对话框
        
        Args:
            stdscr: curses窗口对象
            message: 确认消息
            title: 标题
        
        Returns:
            True确认，False取消
        """
        height, width = 8, 50
        y, x = 5, 5
        
        win = curses.newwin(height, width, y, x)
        win.box()
        win.addstr(0, 2, f" {title} ")
        
        # 消息
        lines = message.split('\n')
        for i, line in enumerate(lines[:3]):
            win.addstr(i + 2, 2, line)
        
        # 选项
        win.addstr(height - 3, 2, "[Y] Yes  [N] No")
        
        win.refresh()
        
        while True:
            key = win.getch()
            if key in (ord('y'), ord('Y')):
                del win
                return True
            elif key in (ord('n'), ord('N'), 27):  # 27是ESC
                del win
                return False
