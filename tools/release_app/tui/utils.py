"""
curses工具函数
包含颜色、布局等辅助功能
"""

import curses
from typing import Tuple


def init_colors():
    """初始化颜色对"""
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)    # 标题
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # 成功
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)     # 错误
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # 警告
    curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)    # 信息


def get_color_pair(color_type: str) -> int:
    """
    获取颜色对
    
    Args:
        color_type: 颜色类型 (title/success/error/warning/info)
    
    Returns:
        颜色对编号
    """
    colors = {
        'title': 1,
        'success': 2,
        'error': 3,
        'warning': 4,
        'info': 5
    }
    return curses.color_pair(colors.get(color_type, 0))


def center_window(height: int, width: int) -> Tuple[int, int]:
    """
    计算居中窗口的位置
    
    Args:
        height: 窗口高度
        width: 窗口宽度
    
    Returns:
        (y, x) 坐标
    """
    max_y, max_x = stdscr.getmaxyx()
    y = (max_y - height) // 2
    x = (max_x - width) // 2
    return y, x


def draw_border(stdscr, title: str = ""):
    """
    绘制窗口边框
    
    Args:
        stdscr: curses窗口对象
        title: 标题
    """
    max_y, max_x = stdscr.getmaxyx()
    stdscr.box()
    
    if title:
        title = f" {title} "
        if len(title) < max_x - 2:
            stdscr.addstr(0, 2, title)


def draw_horizontal_line(stdscr, y: int, x: int, length: int, char: str = "-"):
    """
    绘制水平线
    
    Args:
        stdscr: curses窗口对象
        y: Y坐标
        x: X坐标
        length: 长度
        char: 字符
    """
    stdscr.addstr(y, x, char * length)


def truncate_text(text: str, max_length: int) -> str:
    """
    截断文本
    
    Args:
        text: 原文本
        max_length: 最大长度
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def wrap_text(text: str, width: int) -> list:
    """
    文本换行
    
    Args:
        text: 原文本
        width: 宽度
    
    Returns:
        行列表
    """
    lines = []
    current_line = ""
    
    for word in text.split():
        if len(current_line) + len(word) + 1 > width:
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            if current_line:
                current_line += " "
            current_line += word
    
    if current_line:
        lines.append(current_line)
    
    return lines


class ScreenState:
    """屏幕状态管理"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.saved_states = []
    
    def save(self):
        """保存当前屏幕状态"""
        curses.def_prog_mode()
        self.saved_states.append(True)
    
    def restore(self):
        """恢复屏幕状态"""
        if self.saved_states:
            self.saved_states.pop()
        curses.reset_prog_mode()
    
    def clear(self):
        """清屏"""
        self.stdscr.clear()
        self.stdscr.refresh()


def safe_addstr(stdscr, y: int, x: int, text: str, attr = 0):
    """
    安全添加字符串（自动截断）
    
    Args:
        stdscr: curses窗口对象
        y: Y坐标
        x: X坐标
        text: 文本
        attr: 属性
    """
    max_y, max_x = stdscr.getmaxyx()
    
    if y >= max_y or x >= max_x:
        return
    
    available = max_x - x
    if len(text) > available:
        text = text[:available]
    
    try:
        stdscr.addstr(y, x, text, attr)
    except curses.error:
        pass
