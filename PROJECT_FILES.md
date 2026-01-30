# Binary Manager - 项目文件清单

## 项目结构

```
.
├── binary_manager/              # 主目录
│   ├── publisher/              # 发布器模块
│   │   ├── __init__.py         # 模块初始化
│   │   ├── scanner.py          # 文件扫描器
│   │   ├── packager.py         # 打包器
│   │   └── main.py             # 发布器CLI
│   ├── downloader/            # 下载器模块
│   │   ├── __init__.py         # 模块初始化
│   │   ├── downloader.py       # 下载器
│   │   ├── verifier.py         # 校验器
│   │   └── main.py             # 下载器CLI
│   ├── examples/               # 示例项目
│   │   └── my_app/
│   │       ├── src/            # 源代码
│   │       │   └── main.py
│   │       ├── lib/            # 库文件
│   │       │   └── utils.py
│   │       ├── data/           # 数据文件
│   │       │   └── config.json
│   │       └── README.md       # 示例文档
│   └── config/                 # 配置文件
│       └── schema.json         # JSON Schema
├── install_dependencies.sh      # Ubuntu依赖安装脚本
├── requirements.txt             # Python依赖列表
├── test.py                     # 自动化测试脚本
├── README.md                   # 项目文档
└── QUICKSTART.md               # 快速开始指南

测试生成目录 (运行test.py后):
├── test_releases/              # 测试发布的包
│   ├── test_app_v1.0.0.zip
│   └── test_app_v1.0.0.json
└── test_downloads/             # 测试下载的包
    └── test_app/
        └── test_app/           # 解压后的文件
```

## 文件说明

### 核心模块

#### 发布器

- **scanner.py** (150行)
  - 递归扫描目录
  - 计算文件SHA256哈希
  - 支持忽略模式
  - 生成文件清单

- **packager.py** (105行)
  - 创建zip压缩包
  - 计算zip包哈希
  - 生成JSON配置
  - 保存配置文件

- **main.py** (72行)
  - 命令行接口
  - 参数解析
  - 错误处理

#### 下载器

- **downloader.py** (82行)
  - HTTP下载功能
  - 进度显示
  - 重试机制
  - 文件信息获取

- **verifier.py** (125行)
  - SHA256哈希验证
  - zip解压
  - JSON配置验证
  - 文件完整性检查

- **main.py** (159行)
  - 命令行接口
  - 下载流程控制
  - 本地文件支持
  - 错误处理

### 配置文件

- **schema.json** - JSON Schema验证规则
- **config.json** - 示例数据配置

### 脚本文件

- **install_dependencies.sh** - Ubuntu依赖安装
  - 检查root权限
  - 验证Python3
  - 安装pip3
  - 安装Python包

- **test.py** - 自动化测试脚本
  - 清理测试文件
  - 测试发布器
  - 测试下载器
  - 验证完整性

### 文档文件

- **README.md** - 完整项目文档
- **QUICKSTART.md** - 快速开始指南
- **PROJECT_FILES.md** - 本文件

### 依赖文件

- **requirements.txt** - Python依赖包列表

## 文件统计

| 类型 | 数量 |
|------|------|
| Python模块 | 10 |
| 示例文件 | 4 |
| 脚本文件 | 2 |
| 配置文件 | 2 |
| 文档文件 | 3 |
| **总计** | **21** |

## 功能特性

### 发布器功能

- ✓ 递归扫描文件目录
- ✓ 计算SHA256哈希值
- ✓ 支持忽略模式（.git, __pycache__等）
- ✓ 创建zip压缩包
- ✓ 生成JSON配置文件
- ✓ 记录文件清单和元信息
- ✓ 命令行接口

### 下载器功能

- ✓ HTTP下载zip包
- ✓ 支持本地文件
- ✓ 进度条显示
- ✓ SHA256哈希验证
- ✓ zip解压
- ✓ 文件完整性验证
- ✓ 命令行接口

### 安全特性

- ✓ SHA256哈希校验
- ✓ JSON Schema验证
- ✓ 文件完整性检查
- ✓ 错误处理和重试

## 使用示例

### 发布包
```bash
python3 binary_manager/publisher/main.py \
  --source ./binary_manager/examples/my_app \
  --output ./releases \
  --version 1.0.0 \
  --name my_app
```

### 下载包
```bash
python3 binary_manager/downloader/main.py \
  --config ./releases/my_app_v1.0.0.json \
  --output ./downloads
```

### 运行测试
```bash
python3 test.py
```

## 技术栈

- **Python 3.6+**
- **requests** - HTTP下载
- **jsonschema** - JSON验证
- **tqdm** - 进度显示
- **内置库** - zipfile, hashlib, json, pathlib

## 许可证

MIT License
