# Binary Manager V2 - 洋葱架构实现

Binary Manager V2 采用**洋葱架构（Onion Architecture）**设计，提供清晰、可维护、可测试的二进制文件管理系统。

## 🎯 设计原则

### 洋葱架构层次

```
┌─────────────────────────────────────────┐
│   Presentation Layer (CLI)             │ ← 外层
├─────────────────────────────────────────┤
│   Application Layer (Services)         │
├─────────────────────────────────────────┤
│   Infrastructure Layer (DB, Storage)    │
├─────────────────────────────────────────┤
│   Domain Layer (Core Business)         │ ← 内层（零依赖）
└─────────────────────────────────────────┘
```

### 核心优势

- **Domain层零外部依赖** - 只使用Python标准库
- **依赖倒置** - 内层定义接口，外层实现
- **易于测试** - 每层可独立测试
- **高度解耦** - 层与层之间通过接口通信

---

## 📦 目录结构

### Domain层（领域层）- 核心

```
domain/
├── entities/                    # 实体
│   ├── package.py              # 包实体
│   ├── version.py              # 版本实体
│   ├── group.py                # 分组实体
│   ├── file_info.py            # 文件信息实体
│   └── publisher.py            # 发布者实体
├── value_objects/              # 值对象
│   ├── package_name.py         # 包名称（不可变）
│   ├── hash.py                 # 哈希值
│   ├── git_info.py             # Git信息
│   └── storage_location.py     # 存储位置
├── services/                   # 领域服务
│   ├── file_scanner.py         # 文件扫描
│   ├── hash_calculator.py      # 哈希计算
│   └── packager.py             # 打包服务
└── repositories/               # 仓储接口
    ├── package_repository.py   # 包仓储接口
    ├── group_repository.py     # 分组仓储接口
    └── storage_repository.py   # 存储仓储接口
```

**特点**:
- ✅ 零外部依赖
- ✅ 纯业务逻辑
- ✅ 不可变的值对象
- ✅ 富领域模型

### Infrastructure层（基础设施层）

```
infrastructure/
├── storage/                    # 存储服务
│   ├── local_storage.py        # 本地文件存储
│   └── s3_storage.py          # AWS S3存储（urllib3）
├── git/                       # Git服务
│   └── git_service.py         # Git信息提取
└── database/                  # 数据库仓储
    ├── sqlite_package_repository.py  # 包仓储实现
    └── sqlite_group_repository.py    # 分组仓储实现
```

**职责**:
- ✅ 实现Domain层定义的接口
- ✅ 处理外部系统交互
- ✅ 提供技术能力（存储、数据库、Git）

### Application层（应用层）

```
application/
├── publisher_service.py       # 发布服务
├── downloader_service.py      # 下载服务
└── group_service.py          # 分组服务
```

**职责**:
- ✅ 编排业务流程
- ✅ 协调Domain和Infrastructure
- ✅ 事务管理
- ✅ 用例实现

### Presentation层（表示层）

```
cli/
└── main.py                   # 命令行接口
```

**职责**:
- ✅ 用户交互
- ✅ 参数验证
- ✅ 调用Application层

---

## 🚀 快速开始

### 安装依赖

```bash
pip install -r binary_manager_v2/requirements_v2.txt
```

### 发布包

```bash
# 本地发布
python3 -m binary_manager_v2.cli.main publish \
  --source ./my_project \
  --package-name my_app \
  --version 1.0.0 \
  --output ./releases

# 发布到S3
python3 -m binary_manager_v2.cli.main publish \
  --source ./my_project \
  --package-name my_app \
  --version 1.0.0 \
  --s3-bucket my-bucket \
  --s3-region us-east-1
```

### 下载包

```bash
# 通过配置文件
python3 -m binary_manager_v2.cli.main download \
  --config ./releases/my_app_v1.0.0.json \
  --output ./downloads

# 通过名称和版本
python3 -m binary_manager_v2.cli.main download \
  --package-name my_app \
  --version 1.0.0 \
  --output ./downloads
```

### 分组管理

```bash
# 创建分组
python3 -m binary_manager_v2.cli.main group create \
  --group-name dev_environment \
  --version 1.0.0 \
  --packages backend_api:1.0.0 frontend_web:2.0.0

# 列出分组
python3 -m binary_manager_v2.cli.main group list

# 导出分组
python3 -m binary_manager_v2.cli.main group export \
  --group-id 1 \
  --output ./groups
```

---

## 🏗️ 架构详解

### Domain层示例

#### 值对象（不可变）

```python
from binary_manager_v2.domain.value_objects import PackageName, Hash

# 创建包名称
name = PackageName("my_app")
print(name.value)  # "my_app"

# 创建哈希
hash_obj = Hash.from_string("sha256:abc123...")
print(hash_obj.algorithm)  # "sha256"
```

#### 实体

```python
from binary_manager_v2.domain.entities import Package
from binary_manager_v2.domain.value_objects import PackageName, Hash

package = Package(
    package_name=PackageName("my_app"),
    version="1.0.0",
    archive_hash=Hash.from_string("sha256:abc123..."),
    archive_size=1024000,
    file_count=10
)
```

#### 领域服务

```python
from binary_manager_v2.domain.services import FileScanner

scanner = FileScanner()
files, scan_info = scanner.scan_directory("./my_project")
print(f"扫描了 {scan_info['total_files']} 个文件")
```

### Infrastructure层示例

#### 存储服务

```python
from binary_manager_v2.infrastructure.storage import LocalStorage, S3Storage

# 本地存储
local_storage = LocalStorage("./releases")
local_storage.upload_file("./my_app.zip", "my_app_v1.0.0.zip")

# S3存储
s3_storage = S3Storage(
    bucket_name="my-bucket",
    access_key="xxx",
    secret_key="xxx"
)
s3_storage.upload_file("./my_app.zip", "packages/my_app_v1.0.0.zip")
```

#### 数据库仓储

```python
from binary_manager_v2.infrastructure.database import SQLitePackageRepository

repo = SQLitePackageRepository()
packages = repo.find_by_name("my_app")
```

### Application层示例

```python
from binary_manager_v2.application import PublisherService

publisher = PublisherService()
result = publisher.publish(
    source_dir="./my_project",
    package_name="my_app",
    version="1.0.0",
    extract_git=True
)
```

---

## 📊 依赖优化

### 依赖对比

| 版本 | 依赖 | 大小 |
|------|------|------|
| V1旧架构 | boto3, jsonschema, requests, tqdm | ~105MB |
| V2新架构 | urllib3, requests | ~6MB |

**减少94%依赖体积** ✅

### 实现方式

- 移除boto3 → 使用urllib3实现S3
- 移除jsonschema → 未使用，直接删除
- tqdm变为可选 → 使用ConsoleProgress作为fallback

---

## 🧪 测试

```bash
# 运行完整测试套件
python3 test_v2_complete.py
```

测试覆盖：
- ✅ Domain层 - 实体、值对象、领域服务
- ✅ Infrastructure层 - 存储、Git、数据库
- ✅ Application层 - 发布、下载、分组服务
- ✅ CLI - 命令行接口
- ✅ 集成测试 - 端到端流程

---

## 🔧 配置

### 数据库配置

```sql
-- binary_manager_v2/config/database_schema.sql
-- 包含完整的数据库结构
-- 支持包、分组、依赖、发布者等表
```

### 日志配置

```python
from binary_manager_v2.shared.logger import Logger

Logger.set_level("INFO")
```

---

## 📚 API文档

### CLI命令

```bash
# 查看帮助
python3 -m binary_manager_v2.cli.main --help

# 发布帮助
python3 -m binary_manager_v2.cli.main publish --help

# 下载帮助
python3 -m binary_manager_v2.cli.main download --help

# 分组帮助
python3 -m binary_manager_v2.cli.main group --help
```

### Python API

```python
# 发布服务
from binary_manager_v2.application import PublisherService
publisher = PublisherService()
result = publisher.publish(...)

# 下载服务
from binary_manager_v2.application import DownloaderService
downloader = DownloaderService()
result = downloader.download_by_id(package_id, output_dir)

# 分组服务
from binary_manager_v2.application import GroupService
group_service = GroupService()
result = group_service.create_group(...)
```

---

## 🎯 设计优势

### 1. 可测试性

每层可独立测试：

```python
# Domain层测试（无需mock）
from binary_manager_v2.domain.value_objects import PackageName
name = PackageName("my_app")
assert name.value == "my_app"

# Infrastructure层测试（使用真实SQLite）
from binary_manager_v2.infrastructure.database import SQLitePackageRepository
repo = SQLitePackageRepository(":memory:")
```

### 2. 可维护性

- 清晰的层次结构
- 单一职责原则
- 依赖方向明确（外层依赖内层）

### 3. 可扩展性

添加新功能：
1. 在Domain层添加接口
2. 在Infrastructure层实现
3. 在Application层编排
4. 在CLI层暴露

### 4. 性能优化

- Domain层零依赖 → 快速导入
- 按需加载Infrastructure层
- 依赖体积减少94%

---

## 📝 相关文档

- [README.md](README.md) - 项目总览
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - 重构总结
- [V2_QUICKSTART.md](V2_QUICKSTART.md) - 快速入门
- [TUTORIAL.md](TUTORIAL.md) - 使用教程

---

**GitHub**: https://github.com/qinyusen/binary_manager
