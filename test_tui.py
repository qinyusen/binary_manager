#!/usr/bin/env python3
"""
TUI界面测试脚本
不实际编译，只测试UI组件
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Release App TUI - 组件测试")
print("=" * 60)
print()

# 测试1: 导入检查
print("测试 1: 导入TUI模块")
try:
    from tools.release_app.tui.widgets import Menu, Form, ProgressBar
    from tools.release_app.tui.utils import init_colors
    print("✅ 导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 测试2: curses支持检查
print()
print("测试 2: 检查curses支持")
try:
    import curses
    curses.setupterm()
    print("✅ curses支持正常")
except Exception as e:
    print(f"⚠️  curses不支持: {e}")
    print("   TUI模式将不可用，请使用CLI模式")

# 测试3: 组件创建测试
print()
print("测试 3: 创建UI组件")

menu = Menu(["选项1", "选项2", "选项3"], "测试菜单")
print(f"✅ Menu创建成功，{len(menu.items)}个选项")

form = Form({
    'version': {'label': '版本号', 'default': '1.0.0'},
    'notes': {'label': '说明', 'default': ''}
}, "测试表单")
print(f"✅ Form创建成功，{len(form.fields)}个字段")

progress = ProgressBar(100, 50)
print(f"✅ ProgressBar创建成功，总量{progress.total}")

print()
print("=" * 60)
print("测试完成！")
print("=" * 60)
print()

print("运行TUI版本:")
print("  python3 -m tools.release_app --tui")
print()
print("或使用启动器:")
print("  python3 tools/release_app/launcher.py")
print()

# 询问是否启动TUI
answer = input("是否现在启动TUI界面？ [y/N]: ")
if answer.lower() == 'y':
    try:
        from tools.release_app.tui.curses_cli import main_curses
        print("\n启动TUI界面...")
        sys.argv = ['test', '--project-dir', '.']
        main_curses()
    except KeyboardInterrupt:
        print("\n\n用户取消")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
else:
    print("跳过TUI启动")
