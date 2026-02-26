# Binary Manager

通过JSON配置文件管理二进制文件的发布和下载系统。

## 🎯 项目概述

Binary Manager是一个基于洋葱架构的二进制文件发布和下载管理系统，提供完整的包管理功能。

## ✨ 核心特性

### 🏗️ 洋葱架构设计
- **Domain层（领域层）** - 零外部依赖，纯粹的业务逻辑
- **Infrastructure层（基础设施层）** - 存储、Git、数据库实现
- **Application层（应用层）** - 业务服务协调
- **Presentation层（表示层）** - CLI命令行工具

### 📦 完整功能
- ✅ 发布管理（本地存储/S3云存储）
- ✅ 下载和安装
- ✅ 分组管理（Group）
- ✅ Git集成（commit追踪、branch、tag）
- ✅ SQLite数据库持久化
- ✅ SHA256哈希验证
- ✅ 依赖管理

### 🚀 高性能
- 依赖精简（总大小仅~6MB）
- 使用urllib3替代boto3实现S3支持
- Domain层完全零外部依赖

## 📁 项目结构

```
binary_manager_v2/
├── domain/                  # 领域层（零外部依赖）
│   ├── entities/           # 实体（Package, Version, Group等）
│   ├── value_objects/      # 值对象（PackageName, Hash, GitInfo等）
│   ├── services/           # 领域服务（FileScanner, HashCalculator等）
│   └── repositories/       # 仓储接口
├── infrastructure/         # 基础设施层
│   ├── storage/           # 存储服务（LocalStorage, S3Storage）
│   ├── git/              # Git服务
│   └── database/         # 数据库仓储实现（SQLite）
├── application/           # 应用层
│   ├── publisher_service.py    # 发布服务
│   ├── downloader_service.py   # 下载服务
│   └── group_service.py        # 分组服务
├── cli/                  # 表示层
│   └── main.py          # CLI工具
├── shared/              # 共享工具
│   ├── logger.py
│   ├── progress.py
│   └── config.py
└── config/              # 配置文件
    └── database_schema.sql
```

## 🔧 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 发布包

#### 发布到本地存储

```bash
python3 -m binary_manager_v2.cli.main publish \
  --source ./my_project \
  --package-name my_app \
  --version 1.0.0 \
  --description "My Application"
```

#### 发布到S3云存储

```bash
python3 -m binary_manager_v2.cli.main publish \
  --source ./my_project \
  --package-name my_app \
  --version 1.0.0 \
  --s3-bucket my-bucket
```

### 下载包

#### 通过配置文件下载

```bash
python3 -m binary_manager_v2.cli.main download \
  --config ./releases/my_app_v1.0.0.json \
  --output ./downloads
```

#### 通过名称和版本下载

```bash
python3 -m binary_manager_v2.cli.main download \
  --package-name my_app \
  --version 1.0.0 \
  --output ./downloads
```

#### 下载整个分组

```bash
python3 -m binary_manager_v2.cli.main download \
  --group-id 1 \
  --output ./downloads
```

### 分组管理

#### 创建分组

```bash
python3 -m binary_manager_v2.cli.main group create \
  --group-name dev_environment \
  --version 1.0.0 \
  --packages backend_api:1.0.0 frontend_web:2.0.0 \
  --description "Development Environment"
```

#### 列出所有分组

```bash
python3 -m binary_manager_v2.cli.main group list
```

#### 导出分组配置

```bash
python3 -m binary_manager_v2.cli.main group export \
  --group-id 1 \
  --output ./groups
```

#### 导入分组配置

```bash
python3 -m binary_manager_v2.cli.main group import \
  --config ./groups/dev_environment_v1.0.0.json
```

### 列出和管理

#### 列出所有包

```bash
python3 -m binary_manager_v2.cli.main list
```

#### 按名称过滤

```bash
python3 -m binary_manager_v2.cli.main list --package-name my_app
```

## 🧪 测试

运行完整测试套件：

```bash
python3 test_v2_complete.py
```

测试覆盖：
- ✅ Domain Layer（领域层测试）
- ✅ Infrastructure Layer（基础设施层测试）
- ✅ Database Layer（数据库层测试）
- ✅ Application Layer（应用层测试）
- ✅ CLI（命令行测试）
- ✅ Integration（集成测试）
- ✅ Edge Cases（边界情况测试）

## 📚 示例程序

项目包含完整的示例程序，展示Binary Manager的各种使用场景：

### 1. 简单应用（Simple App）
一个基本的计算器应用，适合入门学习：

```bash
# 发布示例应用
python3 -m binary_manager_v2.cli.main publish \
    --source ./examples/simple_app \
    --package-name simple_app \
    --version 1.0.0

# 下载并运行
python3 -m binary_manager_v2.cli.main download \
    --package-name simple_app \
    --version 1.0.0 \
    --output ./installed_apps

cd installed_apps/simple_app_v1.0.0
python3 main.py add 10 5
```

### 2. Web应用（Web App）
Web服务器应用示例：

```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./examples/web_app \
    --package-name web_app \
    --version 1.0.0

# 下载后运行
cd installed_apps/web_app_v1.0.0
python3 server.py
# 访问 http://localhost:8080
```

### 3. 命令行工具（CLI Tool）
功能丰富的CLI工具示例：

```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./examples/cli_tool \
    --package-name cli_tool \
    --version 1.0.0
```

### 4. 嵌入式Linux BSP（BSP Package）
完整的嵌入式Linux板级支持包示例：

```bash
# 发布BSP包
python3 -m binary_manager_v2.cli.main publish \
    --source ./examples/bsp_package \
    --package-name rv_board_bsp \
    --version 1.0.0 \
    --description "RV-Board-Dev1 Embedded Linux BSP"

# 下载BSP
python3 -m binary_manager_v2.cli.main download \
    --package-name rv_board_bsp \
    --version 1.0.0 \
    --output ./installed_bsps

# 查看BSP信息
cat installed_bsps/rv_board_bsp_v1.0.0/board_info.json

# 烧写到SD卡
cd installed_bsps/rv_board_bsp_v1.0.0
sudo ./scripts/flash.sh --device /dev/sdX --media sd
```

### 查看所有示例

```bash
# 查看示例目录
ls examples/

# 阅读示例文档
cat examples/README.md
cat examples/BSP_README.md

# 运行API使用示例
python3 examples_usage.py
```

详细文档：
- [示例程序总览](examples/README.md)
- [BSP使用指南](examples/BSP_README.md)
- [API使用示例](examples_usage.py)

## 📊 依赖

```
urllib3>=2.0.0    # HTTP和S3支持（~1MB）
requests>=2.31.0  # HTTP下载
```

**总依赖大小**: ~6MB

## 📚 详细文档

- [BINARY_MANAGER_V2.md](BINARY_MANAGER_V2.md) - 完整架构文档
- [V2_QUICKSTART.md](V2_QUICKSTART.md) - 5分钟快速入门
- [PROJECT_FILES.md](PROJECT_FILES.md) - 项目文件说明

## 🎯 使用场景

Binary Manager适用于以下场景：

- ✅ 需要管理多个二进制包的版本
- ✅ 需要追踪Git commit信息
- ✅ 需要管理包之间的依赖关系
- ✅ 需要云存储（S3）支持
- ✅ 需要分组部署多个相关包
- ✅ 需要SHA256哈希验证确保完整性

## 🔑 核心优势

### 1. 洋葱架构
- 清晰的层次分离
- Domain层零外部依赖
- 易于测试和维护

### 2. 完整功能
- Git集成自动提取commit信息
- 数据库持久化存储
- 分组管理批量部署
- S3云存储支持

### 3. 高性能
- 精简依赖（仅~6MB）
- 使用urllib3替代boto3
- 纯Python标准库的Domain层

### 4. 易用性
- 简单的CLI命令
- JSON配置文件
- 完整的测试覆盖

## 📝 许可

MIT License

## 🤝 贡献

欢迎贡献！请查看项目文档了解详细信息。

---

**GitHub**: https://github.com/qinyusen/binary_manager
