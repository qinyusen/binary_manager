"""
测试修复的裸异常捕获功能
验证异常处理逻辑正确性
"""

import pytest
import json
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# 测试 sqlite_audit_log_repository 的异常处理
from release_portal.infrastructure.repositories.sqlite_audit_log_repository import (
    SQLiteAuditLogRepository,
)

# 测试 demo_tests 的异常处理
import demo_tests

# 测试 launcher 的异常处理
from tools.release_app.launcher import check_curses_support

# 测试 curses_cli 的异常处理
from tools.release_app.tui.curses_cli import CursesCLI


class TestExceptionHandling:
    """测试修复后的异常处理逻辑"""

    def test_audit_log_json_parse_exception(self):
        """测试审计日志JSON解析失败时的异常处理"""
        repo = SQLiteAuditLogRepository(":memory:")

        # 模拟数据库行，包含无效JSON
        invalid_row = {
            "id": 1,
            "action": "CREATE",
            "user_id": "user_123",
            "username": "testuser",
            "role": "Publisher",
            "ip_address": "127.0.0.1",
            "user_agent": "TestAgent",
            "resource_type": "BSP",
            "resource_id": "rel_123",
            "resource_name": "Test Release",
            "details": "invalid json {{{",
            "created_at": "2026-01-01 00:00:00",
        }

        # 应该不抛出异常，正常返回AuditLog对象
        audit_log = repo._row_to_audit_log(invalid_row)
        assert audit_log.id == 1
        assert audit_log.action.value == "CREATE"
        assert audit_log.details == {}  # 解析失败应该返回空字典

        # 测试有效JSON
        valid_row = invalid_row.copy()
        valid_row["details"] = '{"key": "value"}'
        audit_log = repo._row_to_audit_log(valid_row)
        assert audit_log.details == {"key": "value"}

    def test_demo_tests_listdir_exception(self, tmp_path):
        """测试目录遍历失败时的异常处理"""
        # 测试不存在的目录
        result = demo_tests.print_directory_tree(
            str(tmp_path / "nonexistent"), max_depth=2
        )
        assert result is None  # 异常处理应该正常返回

        # 测试存在的目录应该正常工作
        os.makedirs(tmp_path / "dir1" / "subdir1")
        os.makedirs(tmp_path / "dir2")
        (tmp_path / "file1.txt").write_text("test")

        # 应该不抛出异常
        result = demo_tests.print_directory_tree(str(tmp_path), max_depth=2)
        assert result is None  # 函数没有返回值，只要不抛异常就是成功

    def test_curses_support_exception(self):
        """测试curses支持检测的异常处理"""
        with patch("importlib.import_module") as mock_import:
            # 模拟导入失败
            mock_import.side_effect = ImportError("No module named curses")
            assert check_curses_support() is False

            # 模拟setupterm失败
            mock_import.side_effect = None
            mock_curses = Mock()
            mock_curses.setupterm.side_effect = Exception("setupterm failed")
            mock_import.return_value = mock_curses
            assert check_curses_support() is False

    def test_git_info_exception_handling(self):
        """测试Git信息显示的异常处理"""
        # 创建模拟的stdscr
        mock_stdscr = Mock()

        # 创建CLI实例
        cli = CursesCLI(mock_stdscr, project_dir="/nonexistent/path")

        # 应该不抛出异常，正常显示"Git信息: 不可用"
        cli._show_git_info(y=0, x=0)

        # 验证输出
        calls = mock_stdscr.addstr.call_args_list
        assert any("Git信息: 不可用" in str(call) for call in calls)
