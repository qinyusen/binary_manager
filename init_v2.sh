#!/bin/bash
# Binary Manager v2 初始化脚本

echo "========================================"
echo "Binary Manager v2 - 初始化"
echo "========================================"

# 查找项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -d "$SCRIPT_DIR/binary_manager_v2" ]; then
    cd "$SCRIPT_DIR/binary_manager_v2"
elif [ -f "$SCRIPT_DIR/database/binary_manager.db" ]; then
    cd "$SCRIPT_DIR"
else
    echo "错误: 无法找到Binary Manager v2项目目录"
    exit 1
fi

echo "工作目录: $(pwd)"
echo ""

# 安装依赖
echo "========================================"
echo "安装Python依赖"
echo "========================================"

pip3 install -r requirements_v2.txt

if [ $? -ne 0 ]; then
    echo "错误: 依赖安装失败"
    exit 1
fi

echo "✓ 依赖安装完成"
echo ""

# 初始化数据库
echo "========================================"
echo "初始化数据库"
echo "========================================"

python3 -c "
import sys
sys.path.insert(0, '.')
from core.database_manager import DatabaseManager

with DatabaseManager() as db:
    db.init_database()
    print('✓ 数据库初始化完成')
    print(f'Publisher ID: {db.publisher_id}')
    print(f'Database: {db.db_path}')
    stats = db.get_statistics()
    print(f'Statistics: {stats}')
"

if [ $? -ne 0 ]; then
    echo "错误: 数据库初始化失败"
    exit 1
fi

echo ""
echo "========================================"
echo "初始化完成！"
echo "========================================"
echo ""
echo "配置文件: config/config.json"
echo "数据库: database/binary_manager.db"
echo ""
echo "下一步："
echo "  1. 编辑 config/config.json 配置AWS S3（可选）"
echo "  2. 发布包: python3 core/publisher_v2.py <source_dir> [version] [name]"
echo "  3. 创建Group: python3 group/group_manager.py list"
