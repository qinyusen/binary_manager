# Binary Manager

通过JSON配置文件管理二进制文件的发布和下载系统。

## 🎯 项目概述

Binary Manager提供两个版本：

- **V1** - 基础版本（已稳定）
- **V2** - 洋葱架构版本（推荐，功能更强大）

---

## 📦 V2 版本（推荐）

### ✨ 特性

- **🏗️ 洋葱架构** - 清晰的四层分离设计
  - Domain层（领域层）- 零外部依赖
  - Infrastructure层（基础设施层）- 存储、Git、数据库
  - Application层（应用层）- 业务服务
  - Presentation层（表示层）- CLI工具

- **📦 完整功能**
  - 发布管理（本地/S3）
  - 下载和安装
  - 分组管理（Group）
  - Git集成
  - SQLite数据库
  - SHA256哈希验证

- **🚀 高性能**
  - 依赖减少94%（~99MB → ~6MB）
  - 使用urllib3替代boto3
  - 纯Python标准库的Domain层

### 📁 V2目录结构

```
binary_manager_v2/
├── domain/                  # 领域层（零外部依赖）
│   ├── entities/           # 实体
│   ├── value_objects/      # 值对象
│   ├── services/           # 领域服务
│   └── repositories/       # 仓储接口
├── infrastructure/         # 基础设施层
│   ├── storage/           # 存储服务（Local/S3）
│   ├── git/              # Git服务
│   └── database/         # 数据库仓储（SQLite）
├── application/           # 应用层
│   ├── publisher_service.py
│   ├── downloader_service.py
│   └── group_service.py
├── cli/                  # 表示层
│   └── main.py          # CLI工具
├── shared/              # 共享工具
│   ├── logger.py
│   ├── progress.py
│   └── config.py
└── config/              # 配置文件
    └── database_schema.sql
```

### 🔧 V2 快速开始

#### 安装

```bash
pip install -r requirements.txt
```

#### 发布包

```bash
# 发布到本地
python3 binary_manager_v2/cli/main.py publish \
  --source ./my_project \
  --package-name my_app \
  --version 1.0.0

# 发布到S3
python3 binary_manager_v2/cli/main.py publish \
  --source ./my_project \
  --package-name my_app \
  --version 1.0.0 \
  --s3-bucket my-bucket
```

#### 下载包

```bash
# 通过配置文件下载
python3 binary_manager_v2/cli/main.py download \
  --config ./releases/my_app_v1.0.0.json \
  --output ./downloads

# 通过名称和版本下载
python3 binary_manager_v2/cli/main.py download \
  --package-name my_app \
  --version 1.0.0 \
  --output ./downloads

# 下载整个分组
python3 binary_manager_v2/cli/main.py download \
  --group-id 1 \
  --output ./downloads
```

#### 分组管理

```bash
# 创建分组
python3 binary_manager_v2/cli/main.py group create \
  --group-name dev_environment \
  --version 1.0.0 \
  --packages backend_api:1.0.0 frontend_web:2.0.0

# 列出所有分组
python3 binary_manager_v2/cli/main.py group list

# 导出分组
python3 binary_manager_v2/cli/main.py group export \
  --group-id 1 \
  --output ./groups
```

#### 列出包

```bash
# 列出所有包
python3 binary_manager_v2/cli/main.py list

# 按名称过滤
python3 binary_manager_v2/cli/main.py list --package-name my_app
```

### 🧪 V2 测试

```bash
python3 test_v2_complete.py
```

### 📊 V2 依赖

```
urllib3>=2.0.0    # HTTP和S3（~1MB）
requests>=2.31.0  # HTTP下载
```

**总依赖大小**: ~6MB（比V1减少94%）

---

## 📦 V1 版本（基础版）

### 特性

- 发布器 - 扫描文件、打包zip、生成JSON配置
- 下载器 - 解析JSON、下载zip、校验解压
- SHA256哈希验证
- 详细的文件清单和元信息

### V1 快速开始

#### 发布包

```bash
python3 binary_manager/publisher/main.py \
  --source ./binary_manager/examples/my_app \
  --output ./releases \
  --version 1.0.0 \
  --name my_app
```

#### 下载包

```bash
python3 binary_manager/downloader/main.py \
  --config ./releases/my_app_v1.0.0.json \
  --output ./downloads
```

### V1 依赖

```
requests>=2.31.0
jsonschema>=4.20.0
tqdm>=4.66.0
```

---

## 📚 文档

- [README.md](README.md) - 本文档
- [BINARY_MANAGER_V2.md](BINARY_MANAGER_V2.md) - V2详细文档
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - 重构总结
- [V2_QUICKSTART.md](V2_QUICKSTART.md) - V2快速入门
- [TUTORIAL.md](TUTORIAL.md) - 使用教程

## 🏗️ 架构对比

| 特性 | V1 | V2 |
|------|----|----|
| 基本发布/下载 | ✅ | ✅ |
| Git集成 | ❌ | ✅ |
| 数据库支持 | ❌ | ✅ |
| 分组管理 | ❌ | ✅ |
| 依赖管理 | ❌ | ✅ |
| S3存储 | ❌ | ✅（使用urllib3）|
| 依赖大小 | ~105MB | ~6MB |
| 架构 | 单体 | 洋葱架构 |

## 🚀 推荐使用场景

### 使用V1如果您：
- 只需要基本的发布/下载功能
- 不需要数据库存储
- 不需要Git集成

### 使用V2如果您：
- 需要完整的包管理功能
- 需要Git commit追踪
- 需要管理多个包的依赖关系
- 需要S3云存储
- 关注依赖大小和性能

## 📝 许可

MIT License

## 🤝 贡献

欢迎贡献！请查看项目文档了解详细信息。

---

**GitHub**: https://github.com/qinyusen/binary_manager
