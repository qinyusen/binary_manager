# 地瓜机器人发布平台 V3

基于 Binary Manager V2 构建的软件发布管理平台，支持 BSP、驱动和示例程序的发布与基于许可证的权限控制。

## 快速开始

### 1. 安装依赖

```bash
pip install -r release_portal/requirements_v3.txt
```

### 2. 初始化数据库

```bash
release-portal init
```

### 3. 创建用户并登录

```bash
# 创建发布者
release-portal register publisher publisher@example.com pub123 --role Publisher

# 登录
release-portal login publisher
```

### 4. 发布资源

```bash
# 创建发布草稿
release-portal publish create --type BSP --version 1.0.0

# 添加包
release-portal publish add-package rel_xxx --content-type BINARY --source /path/to/source

# 发布版本
release-portal publish publish rel_xxx
```

## 核心功能

- ✅ **三种资源类型**：BSP、驱动程序（DRIVER）、示例程序（EXAMPLES）
- ✅ **三种内容类型**：源代码（SOURCE）、二进制（BINARY）、文档（DOCUMENT）
- ✅ **基于许可证的权限控制**：FULL_ACCESS vs BINARY_ACCESS
- ✅ **角色管理**：Admin、Publisher、Customer
- ✅ **命令行界面**：完整的 CLI 工具
- 🚧 **Web 界面**：开发中

## 包命名规范

包名格式：`{type}-diggo-{version}-{content}.tar.gz`

例如：
- `bsp-diggo-1-0-0-source.tar.gz`
- `bsp-diggo-1-0-0-binary.tar.gz`
- `bsp-diggo-1-0-0-document.tar.gz`

## 常用命令

```bash
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

## 文档

- **[快速入门](../QUICK_START.md)** - 5 分钟快速上手
- **[使用手册](../USER_MANUAL.md)** - 完整的使用说明和 API 参考
- **[架构设计](../DECOUPLING_DESIGN.md)** - 账号系统与存储系统解耦设计
- **[设计文档](../doc/design.md)** - 系统设计文档

## 示例

运行快速入门示例：

```bash
python examples/quick_start.py
```

运行完整演示：

```bash
python examples/demo_portal.py
```

## 配置

环境变量：

```bash
export RELEASE_PORTAL_DB="./data/portal.db"
export RELEASE_PORTAL_SECRET="your-secret-key"
export RELEASE_PORTAL_TOKEN_EXPIRY_HOURS=24
```

## 项目结构

```
release_portal/
├── domain/              # 领域层（实体、值对象、仓储接口）
│   ├── entities/        # User, Role, License, Release
│   ├── value_objects/   # ResourceType, ContentType, AccessLevel, Permission
│   ├── repositories/    # 仓储接口
│   └── services/        # IAuthorizationService, IStorageService
├── infrastructure/      # 基础设施层（数据库实现）
│   ├── database/        # SQLite 实现
│   └── auth/            # JWT Token 服务
├── application/         # 应用层（服务编排）
│   ├── auth_service.py          # 认证服务
│   ├── authorization_service.py # 授权服务
│   ├── license_service.py       # 许可证服务
│   ├── storage_service_adapter.py # 存储服务适配器
│   ├── release_service.py       # 发布服务
│   └── download_service.py      # 下载服务
├── presentation/        # 表现层（CLI、Web）
│   └── cli/             # 命令行界面
├── shared/             # 共享配置和异常
└── __init__.py
```

## 架构特点

### 洋葱架构

系统采用四层洋葱架构，确保依赖方向正确：

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

通过接口层实现了账号系统和存储系统的解耦：

- **IAuthorizationService**：授权服务接口
- **IStorageService**：存储服务接口
- **AuthorizationService**：账号系统实现
- **StorageServiceAdapter**：存储系统适配器

这样设计的好处：
1. 账号系统可以独立运行和测试
2. 存储系统可以独立运行和测试
3. 可以轻松替换实现
4. 易于维护和扩展

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

## 开发

### 运行测试

```bash
python test_portal.py
```

### 数据库初始化

```python
from release_portal.initializer import DatabaseInitializer

initializer = DatabaseInitializer('./test.db')
initializer.initialize()
```

### 使用服务容器

```python
from release_portal.initializer import create_container

container = create_container()

# 访问服务
auth_service = container.auth_service
release_service = container.release_service
download_service = container.download_service
license_service = container.license_service
```

## 故障排除

### Token 过期

```bash
release-portal logout
release-portal login <username>
```

### 权限错误

确认用户角色和许可证是否正确：
```bash
release-portal whoami
```

### 数据库问题

重新初始化数据库：
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
