# CLI Tool

一个功能丰富的命令行工具示例，展示Binary Manager的发布和下载功能。

## 功能

这个工具提供了多个实用命令，用于文件操作、文本处理和系统管理。

## 文件结构

```
cli_tool/
├── README.md           # 本文件
├── cli.py             # 命令行界面
├── commands/          # 命令模块
│   ├── __init__.py
│   ├── file_ops.py   # 文件操作命令
│   ├── text_ops.py   # 文本处理命令
│   └── sys_ops.py    # 系统操作命令
└── utils.py          # 工具函数
```

## 使用方法

### 安装

```bash
# 从本地安装
python3 -m binary_manager_v2.cli.main download \
    --package-name cli_tool \
    --version 1.0.0 \
    --output ./installed_apps
```

### 运行

```bash
cd cli_tool
python3 cli.py --help
```

## 可用命令

### 文件操作

#### 统计文件信息
```bash
python3 cli.py file stats /path/to/file
```

#### 查找重复文件
```bash
python3 cli.py file find-duplicates /path/to/directory
```

#### 批量重命名
```bash
python3 cli.py file rename /path/to/directory --pattern "*.txt" --prefix "new_"
```

### 文本处理

#### 统计文本
```bash
python3 cli.py text count /path/to/file.txt
```

#### 搜索替换
```bash
python.py cli.py text replace /path/to/file.txt --old "old_text" --new "new_text"
```

#### 格式化JSON
```bash
python3 cli.py text format-json /path/to/file.json
```

### 系统操作

#### 系统信息
```bash
python3 cli.py sys info
```

#### 磁盘使用
```bash
python3 cli.py sys disk
```

#### 进程列表
```bash
python3 cli.py sys processes
```

## 作为模块使用

```python
from commands.file_ops import get_file_stats
from commands.text_ops import count_text
from commands.sys_ops import get_system_info

# 获取文件统计信息
stats = get_file_stats("/path/to/file")
print(f"File size: {stats['size']} bytes")

# 统计文本
text_stats = count_text("Hello, World!")
print(f"Word count: {text_stats['words']}")

# 获取系统信息
sys_info = get_system_info()
print(f"OS: {sys_info['os']}")
```

## 发布

使用Binary Manager发布:

```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./cli_tool \
    --package-name cli_tool \
    --version 1.0.0
```

## 版本历史

- **1.0.0** - 初始版本
  - 文件操作命令（统计、查找重复、批量重命名）
  - 文本处理命令（统计、搜索替换、JSON格式化）
  - 系统操作命令（系统信息、磁盘使用、进程列表）
  - 彩色输出支持
  - 进度条显示
