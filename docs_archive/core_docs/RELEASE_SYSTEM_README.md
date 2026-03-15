# 地瓜机器人发布系统

基于洋葱架构的软件发布管理平台，支持 BSP、驱动和示例程序的发布与基于许可证的权限控制。

## 项目概述

本项目包含两个核心系统：

### 1. Binary Manager V2
通用的二进制包管理系统，提供包的发布、存储和下载功能。

### 2. Release Portal V3
基于 Binary Manager V2 构建的发布平台，添加了用户管理、许可证管理和权限控制功能。

## 核心特性

- ✅ **洋葱架构**：四层架构（Domain、Infrastructure、Application、Presentation）
- ✅ **账号系统与存储系统解耦**：通过接口层实现松耦合
- ✅ **基于许可证的权限控制**：支持 FULL_ACCESS 和 BINARY_ACCESS 两种级别
- ✅ **角色管理**：Admin、Publisher、Customer 三种角色
- ✅ **命令行界面**：完整的 CLI 工具
- ✅ **包管理**：支持源码、二进制和文档三种内容类型
- ✅ **资源分类**：支持 BSP、驱动、示例三种资源类型

## 快速开始

### 1. 安装依赖

```bash
# 安装 Binary Manager V2 依赖
pip install -r binary_manager_v2/requirements.txt

# 安装 Release Portal 依赖
pip install -r release_portal/requirements_v3.txt
```

### 2. 快速入门

```bash
# 运行快速入门示例
python examples/quick_start.py
```

这将自动：
- 初始化数据库
- 创建测试用户
- 创建许可证
- 发布示例资源
- 演示下载功能

### 3. 使用 CLI 工具

```bash
# 初始化数据库
release-portal init

# 创建用户
release-portal register admin admin@example.com admin123 --role Admin

# 登录
release-portal login admin

# 查看帮助
release-portal --help
```

## 文档

### 入门文档
- **[快速入门](QUICK_START.md)** - 5 分钟快速上手指南
- **[使用手册](USER_MANUAL.md)** - 完整的使用说明和 API 参考

### 设计文档
- **[架构设计](DECOUPLING_DESIGN.md)** - 账号系统与存储系统解耦设计
- **[系统设计](doc/design.md)** - 完整的系统设计文档（15章）
- **[实施总结](IMPLEMENTATION_SUMMARY.md)** - Phase 1 实施总结

### 项目文档
- **[Binary Manager V2](BINARY_MANAGER_V2.md)** - 二进制包管理系统
- **[Release Portal V3](release_portal/README.md)** - 发布平台

## 项目结构

```
release_system/
├── binary_manager_v2/          # 二进制包管理系统
│   ├── domain/                 # 领域层
│   ├── infrastructure/         # 基础设施层
│   ├── application/            # 应用层
│   └── presentation/           # 表现层
├── release_portal/             # 发布平台
│   ├── domain/                 # 领域层
│   │   ├── entities/           # User, Role, License, Release
│   │   ├── value_objects/      # ResourceType, ContentType, AccessLevel
│   │   ├── repositories/       # 仓储接口
│   │   └── services/           # IAuthorizationService, IStorageService
│   ├── infrastructure/         # 基础设施层
│   │   ├── database/           # SQLite 实现
│   │   └── auth/               # JWT Token 服务
│   ├── application/            # 应用层
│   │   ├── auth_service.py     # 认证服务
│   │   ├── authorization_service.py  # 授权服务
│   │   ├── license_service.py  # 许可证服务
│   │   ├── storage_service_adapter.py  # 存储适配器
│   │   ├── release_service.py  # 发布服务
│   │   └── download_service.py # 下载服务
│   └── presentation/           # 表现层
│       └── cli/                # 命令行界面
├── examples/                   # 示例脚本
│   ├── quick_start.py         # 快速入门示例
│   └── demo_portal.py         # 完整演示
├── doc/                       # 设计文档
├── data/                      # 数据目录
│   └── portal.db              # 默认数据库
├── test_portal.py             # 测试脚本
├── test_decoupling.py         # 解耦测试
├── QUICK_START.md             # 快速入门
├── USER_MANUAL.md             # 使用手册
├── DECOUPLING_DESIGN.md       # 架构设计
└── README.md                  # 本文件
```

## 架构设计

### 洋葱架构

```
┌─────────────────────────────────────────┐
│      Presentation Layer (CLI/Web)       │  ← 用户界面
├─────────────────────────────────────────┤
│       Application Layer (Services)      │  ← 业务逻辑
├─────────────────────────────────────────┤
│         Domain Layer (Entities)         │  ← 核心模型
├─────────────────────────────────────────┤
│      Infrastructure Layer (Database)    │  ← 数据持久化
└─────────────────────────────────────────┘
```

### 账号系统与存储系统解耦

```
┌──────────────────┐         ┌──────────────────┐
│   账号系统        │         │   存储系统        │
│  (Account)       │         │  (Storage)       │
│                  │         │                  │
│  - User          │         │  - Package       │
│  - Role          │         │  - Publisher     │
│  - License       │         │  - Downloader    │
│                  │         │                  │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         │ implements                 │ implements
         │                            │
         ↓                            ↓
┌──────────────────┐         ┌──────────────────┐
│AuthorizationSvc  │         │StorageSvcAdapter │
│                  │         │                  │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         │ uses                       │ uses
         └──────────┬─────────────────┘
                    ↓
         ┌──────────────────┐
         │  Business Svc    │
         │  (Release,       │
         │   Download)      │
         └──────────────────┘
```

## 角色

| 角色 | 发布 | 下载 | 用户管理 | 许可证管理 |
|------|-----|------|---------|-----------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Publisher | ✓ | ✓ | ✗ | ✗ |
| Customer | ✗ | * | ✗ | ✗ |

*Customer 的下载权限取决于其许可证

## 许可证级别

| 级别 | 源码 | 二进制 | 文档 |
|------|-----|-------|-----|
| FULL_ACCESS | ✓ | ✓ | ✓ |
| BINARY_ACCESS | ✗ | ✓ | ✓ |

## 包命名规范

格式：`{type}-diggo-{version}-{content}.tar.gz`

示例：
- `bsp-diggo-1-0-0-source.tar.gz`
- `bsp-diggo-1-0-0-binary.tar.gz`
- `bsp-diggo-1-0-0-document.tar.gz`

## 常用命令

```bash
# 初始化
release-portal init

# 用户管理
release-portal login <username>
release-portal logout
release-portal whoami
release-portal register <username> <email> <password> --role <role>

# 发布管理
release-portal publish create --type <BSP|DRIVER|EXAMPLES> --version <version>
release-portal publish add-package <release_id> --content-type <SOURCE|BINARY|DOCUMENT> --source <path>
release-portal publish publish <release_id>
release-portal list

# 下载管理
release-portal download list <release_id>
release-portal download download <release_id>

# 许可证管理
release-portal license create --organization <name> --level <FULL_ACCESS|BINARY_ACCESS> --types <types>
release-portal license list
release-portal license extend <license_id> --days <days>
```

## 测试

### 运行所有测试

```bash
python test_portal.py
```

### 运行解耦测试

```bash
python test_decoupling.py
```

### 运行示例

```bash
# 快速入门
python examples/quick_start.py

# 完整演示
python examples/demo_portal.py
```

## 配置

环境变量：

```bash
export RELEASE_PORTAL_DB="./data/portal.db"
export RELEASE_PORTAL_SECRET="your-secret-key"
export RELEASE_PORTAL_TOKEN_EXPIRY_HOURS=24
```

## 开发指南

### 使用服务容器

```python
from release_portal.initializer import create_container

container = create_container()

# 访问服务
auth_service = container.auth_service
authorization_service = container.authorization_service
release_service = container.release_service
download_service = container.download_service
license_service = container.license_service
```

### 创建发布

```python
from release_portal.domain.value_objects import ResourceType, ContentType

# 创建发布草稿
release = container.release_service.create_draft(
    resource_type=ResourceType.BSP,
    version="1.0.0",
    publisher_id=user.user_id,
    description="BSP v1.0.0"
)

# 添加包
package_id = container.release_service.add_package(
    release_id=release.release_id,
    content_type=ContentType.BINARY,
    source_dir="/path/to/source",
    user_id=user.user_id
)

# 发布版本
release = container.release_service.publish_release(
    release_id=release.release_id,
    user_id=user.user_id
)
```

### 下载包

```python
# 获取可下载的包
packages = container.download_service.get_available_packages(
    user_id=user.user_id,
    release_id="rel_xxx"
)

# 下载包
container.download_service.download_package(
    user_id=user.user_id,
    release_id="rel_xxx",
    content_type="BINARY",
    output_dir="/path/to/output"
)
```

## 故障排除

### Token 过期

```bash
release-portal logout
release-portal login <username>
```

### 权限错误

```bash
release-portal whoami
```

### 数据库问题

```bash
rm -f ./data/portal.db
release-portal init
```

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

[TODO: 添加许可证信息]

## 联系方式

- 项目负责人：[TODO]
- 技术支持：[TODO]

## 更新日志

### V3.0.0 (2024-01-15)
- ✅ 完成账号系统与存储系统解耦
- ✅ 实现用户、角色、许可证管理
- ✅ 实现发布和下载功能
- ✅ 实现 CLI 工具
- 🚧 Web 界面开发中

### V2.0.0
- Binary Manager V2 实现

### V1.0.0
- 初始版本

## 相关链接

- Binary Manager V2 文档：[BINARY_MANAGER_V2.md](BINARY_MANAGER_V2.md)
- Binary Manager 快速入门：[V2_QUICKSTART.md](V2_QUICKSTART.md)
