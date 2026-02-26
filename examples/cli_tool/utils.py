#!/usr/bin/env python3
"""
工具函数
"""


def print_banner():
    """打印横幅"""
    banner = """
╔═══════════════════════════════════════════════════════╗
║          CLI Tool - 命令行工具示例                    ║
║          Binary Manager V2 示例应用                   ║
╚═══════════════════════════════════════════════════════╝
"""
    print(banner)


def print_error(message):
    """打印错误消息"""
    print(f"❌ {message}")


def print_success(message):
    """打印成功消息"""
    print(f"✅ {message}")


def print_warning(message):
    """打印警告消息"""
    print(f"⚠️  {message}")


def print_info(message):
    """打印信息消息"""
    print(f"ℹ️  {message}")


if __name__ == "__main__":
    print_banner()
    print_error("这是错误消息")
    print_success("这是成功消息")
    print_warning("这是警告消息")
    print_info("这是信息消息")
