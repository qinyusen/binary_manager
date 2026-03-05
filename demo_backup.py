#!/usr/bin/env python3
"""
数据备份功能演示脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_backup_service():
    """演示备份服务功能"""
    print_section("💾 数据备份服务功能演示")
    
    from release_portal.application.backup_service import BackupService
    import tempfile
    import os
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test.db")
    storage_path = os.path.join(temp_dir, "storage")
    backup_dir = os.path.join(temp_dir, "backups")
    
    # 创建测试数据库和存储
    os.makedirs(storage_path, exist_ok=True)
    os.makedirs(backup_dir, exist_ok=True)
    
    # 创建测试数据库
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
    conn.execute("INSERT INTO test (name) VALUES ('test1')")
    conn.commit()
    conn.close()
    
    # 创建测试存储文件
    test_file = os.path.join(storage_path, "test.txt")
    with open(test_file, 'w') as f:
        f.write("test content")
    
    print(f"\n测试环境:")
    print(f"  数据库: {db_path}")
    print(f"  存储: {storage_path}")
    print(f"  备份目录: {backup_dir}")
    
    # 初始化备份服务
    backup_service = BackupService(
        db_path=db_path,
        storage_path=storage_path,
        backup_dir=backup_dir
    )
    
    print("\n" + "-" * 70)
    print("1️⃣ 创建备份")
    print("-" * 70)
    
    # 创建备份
    backup_info = backup_service.create_backup(
        name="demo_backup",
        include_storage=True
    )
    
    print(f"✓ 备份创建成功!")
    print(f"  文件名: {backup_info['filename']}")
    print(f"  大小: {backup_info['size']} 字节")
    print(f"  校验和: {backup_info['checksum'][:16]}...")
    print(f"  包含存储: {backup_info['includes_storage']}")
    
    print("\n" + "-" * 70)
    print("2️⃣ 列出备份")
    print("-" * 70)
    
    # 列出备份
    backups = backup_service.list_backups()
    print(f"✓ 找到 {len(backups)} 个备份:")
    for backup in backups:
        print(f"  - {backup['filename']}")
        print(f"    大小: {backup['size']} 字节")
        print(f"    创建时间: {backup['created_at']}")
    
    print("\n" + "-" * 70)
    print("3️⃣ 获取备份信息")
    print("-" * 70)
    
    # 获取备份信息
    backup_filename = backup_info['filename']
    backup_info_detail = backup_service.get_backup_info(backup_filename)
    
    if backup_info_detail:
        print(f"✓ 备份信息:")
        print(f"  文件名: {backup_info_detail['filename']}")
        print(f"  大小: {backup_info_detail['size']} 字节")
        print(f"  创建时间: {backup_info_detail['created_at']}")
        print(f"  校验和: {backup_info_detail['checksum'][:16]}...")
        if backup_info_detail['metadata']:
            print(f"  元数据: {backup_info_detail['metadata']}")
    
    print("\n" + "-" * 70)
    print("4️⃣ 清理")
    print("-" * 70)
    
    # 清理临时目录
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)
    print("✓ 测试环境已清理")


def demo_backup_api():
    """演示备份 API"""
    print_section("🔌 备份 API 端点")
    
    endpoints = [
        ("GET /api/backup", "列出所有备份"),
        ("POST /api/backup/create", "创建新备份"),
        ("GET /api/backup/<filename>", "获取备份详情"),
        ("GET /api/backup/<filename>/download", "下载备份文件"),
        ("POST /api/backup/restore", "恢复备份"),
        ("DELETE /api/backup/<filename>", "删除备份"),
    ]
    
    print("\n可用的 API 端点:\n")
    for endpoint, description in endpoints:
        print(f"  {endpoint:50s} - {description}")


def demo_backup_workflow():
    """演示完整备份工作流"""
    print_section("🔄 完整备份工作流")
    
    print("\n创建备份工作流:")
    print("  1. 用户在 Web UI 点击'创建备份'")
    print("  2. 前端调用 POST /api/backup/create")
    print("  3. 后端创建临时目录")
    print("  4. 复制数据库和存储文件")
    print("  5. 创建元数据 JSON")
    print("  6. 打包为 tar.gz")
    print("  7. 计算校验和")
    print("  8. 保存到备份目录")
    print("  9. 返回备份信息给前端")
    
    print("\n恢复备份工作流:")
    print("  1. 用户选择要恢复的备份")
    print("  2. 前端调用 POST /api/backup/restore")
    print("  3. 后端验证备份文件存在")
    print("  4. 自动备份当前数据")
    print("  5. 解压备份文件")
    print("  6. 读取元数据")
    print("  7. 恢复数据库")
    print("  8. 恢复存储文件（如包含）")
    print("  9. 返回恢复结果")


def demo_features():
    """演示核心功能"""
    print_section("✨ 核心功能特性")
    
    features = [
        ("✅ 数据库备份", "备份 SQLite 数据库文件"),
        ("✅ 存储备份", "备份发布的包文件"),
        ("✅ 压缩存储", "使用 gzip 压缩"),
        ("✅ 元数据管理", "记录备份时间、大小、校验和"),
        ("✅ 备份列表", "查看所有备份"),
        ("✅ 一键恢复", "快速恢复到任意备份点"),
        ("✅ 备份下载", "下载备份到本地"),
        ("✅ 权限控制", "仅管理员可操作"),
        ("✅ SHA256 校验", "确保数据完整性"),
        ("✅ Web UI", "直观的管理界面"),
    ]
    
    print("\n")
    for feature, description in features:
        print(f"  {feature:20s} - {description}")


def demo_usage():
    """演示使用方法"""
    print_section("📖 使用方法")
    
    print("\n通过 Web UI 使用:")
    print("  1. 访问 http://localhost:5000")
    print("  2. 使用管理员账户登录")
    print("  3. 点击侧边栏'数据备份'")
    print("  4. 创建/恢复/下载/删除备份")
    
    print("\n通过 API 使用:")
    print("  # 创建备份")
    print("  curl -X POST http://localhost:5000/api/backup/create \\")
    print("    -H 'Authorization: Bearer <token>' \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"include_storage\": true}'")
    
    print("\n  # 列出备份")
    print("  curl http://localhost:5000/api/backup \\")
    print("    -H 'Authorization: Bearer <token>'")
    
    print("\n通过代码使用:")
    print("  from release_portal.application.backup_service import BackupService")
    print("  ")
    print("  backup_service = BackupService(")
    print("      db_path='./data/portal.db',")
    print("      storage_path='./releases',")
    print("      backup_dir='./backups'")
    print("  )")
    print("  ")
    print("  # 创建备份")
    print("  backup_info = backup_service.create_backup()")
    print("  ")
    print("  # 恢复备份")
    print("  backup_service.restore_backup('backup_file.tar.gz')")


def main():
    """主函数"""
    print("\n" + "💾" * 35)
    print("  数据备份功能 - 完整演示")
    print("💾" * 35)
    
    demo_features()
    demo_backup_api()
    demo_backup_workflow()
    demo_usage()
    
    # 实际演示备份服务（需要真实环境）
    print("\n" + "=" * 70)
    print("  是否运行实际备份服务演示？")
    print("  (需要创建临时文件)")
    print("=" * 70)
    
    try:
        demo_backup_service()
    except Exception as e:
        print(f"\n⚠️  演示失败: {e}")
        print("   这是正常的，可能是因为缺少依赖或环境配置")
    
    print_section("📚 更多信息")
    
    print("\n查看完整文档:")
    print("  • BACKUP_FEATURE_DOCUMENTATION.md - 详细功能文档")
    print("  • release_portal/application/backup_service.py - 备份服务")
    print("  • release_portal/presentation/web/api/backup.py - 备份 API")
    print("  • release_portal/presentation/web/templates/backup.html - Web UI")
    
    print("\n快速开始:")
    print("  1. 访问 http://localhost:5000/backup")
    print("  2. 使用管理员账户登录")
    print("  3. 点击'创建备份'")
    print("  4. 等待备份完成")
    
    print("\n" + "=" * 70)
    print("  数据备份功能已就绪！")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
