# Release Portal V3

> 地瓜机器人软件发布管理平台 - 支持 BSP、驱动和示例程序的发布与权限控制

## 项目简介

Release Portal V3 是一个企业级软件发布管理平台，专为嵌入式系统开发场景设计。平台支持多资源类型（BSP、驱动、示例程序）的发布管理，并提供基于许可证的细粒度权限控制。

### 核心特性

- **多资源类型支持**：BSP（板级支持包）、DRIVER（驱动程序）、EXAMPLES（示例程序）
- **多内容类型**：SOURCE（源码）、BINARY（二进制）、DOCUMENT（文档）
- **许可证权限控制**：FULL_ACCESS（完全访问）vs BINARY_ACCESS（仅二进制）
- **角色管理**：Admin、Publisher、Customer 三级权限
- **双界面**：完整的 CLI 工具 + Web 管理界面
- **数据安全**：热备份 + 冷备份，支持 S3/SFTP/FTP 等多种存储后端
- **自动化测试**：发布前自动运行测试套件，确保质量

## 快速开始

### 环境要求

- Python 3.11+
- SQLite 3

### 安装

```bash
# 克隆项目
git clone https://github.com/qinyusen/release_system.git
cd release_system

# 安装依赖
pip install -r release_portal/requirements_v3.txt
```

### 初始化

```bash
# 初始化数据库
release-portal init

# 创建管理员账户
release-portal register admin admin@example.com admin123 --role Admin

# 登录
release-portal login admin

# 验证
release-portal whoami
```

### Docker 部署

```bash
# 构建并启动
docker-compose up -d

# 访问
# Web UI: http://localhost:5000
```

## 使用指南

### CLI 常用命令

```bash
# === 用户管理 ===
release-portal login <username>
release-portal logout
release-portal whoami
release-portal register <username> <email> <password> --role <role>

# === 发布管理 ===
release-portal publish create --type BSP --version 1.0.0 --description "描述"
release-portal publish add-package <release_id> --content-type SOURCE --source ./src
release-portal publish publish <release_id>
release-portal list

# === 下载管理 ===
release-portal download list <release_id>
release-portal download download <release_id>

# === 许可证管理 ===
release-portal license create --organization <name> --level FULL_ACCESS --types BSP,DRIVER
release-portal license list
release-portal license extend <license_id> --days 365
```

### Web 界面

```bash
# 启动 Web 服务
export FLASK_APP=release_portal.presentation.web.app
flask run --host 0.0.0.0 --port 5000

# 访问 http://localhost:5000
```

### API 接口

```bash
# 登录获取 Token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 创建发布
curl -X POST http://localhost:5000/api/releases \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"resource_type": "BSP", "version": "1.0.0", "description": "BSP v1.0.0"}'
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

### 目录结构

```
release_portal/
├── domain/              # 领域层
│   ├── entities/        # 实体：User, Role, License, Release
│   ├── value_objects/   # 值对象：ResourceType, ContentType, AccessLevel
│   ├── repositories/    # 仓储接口
│   └── services/        # 领域服务接口
├── infrastructure/      # 基础设施层
│   ├── database/        # SQLite 实现
│   └── auth/            # JWT Token 服务
├── application/         # 应用层
│   ├── auth_service.py          # 认证
│   ├── authorization_service.py # 授权
│   ├── release_service.py       # 发布
│   ├── download_service.py      # 下载
│   ├── license_service.py       # 许可证
│   ├── backup_service.py        # 热备份
│   └── cold_backup/             # 冷备份
├── presentation/        # 表现层
│   ├── cli/             # 命令行界面
│   └── web/             # Web 界面 + REST API
└── shared/              # 共享模块
```

## 权限模型

### 角色权限

| 角色 | 发布 | 下载 | 用户管理 | 许可证管理 |
|------|:----:|:----:|:--------:|:----------:|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Publisher | ✓ | ✓ | ✗ | ✗ |
| Customer | ✗ | * | ✗ | ✗ |

*Customer 的下载权限由许可证决定

### 许可证级别

| 级别 | 源码 | 二进制 | 文档 |
|------|:----:|:------:|:----:|
| FULL_ACCESS | ✓ | ✓ | ✓ |
| BINARY_ACCESS | ✗ | ✓ | ✓ |

## 功能模块

### 发布管理

- 支持三种资源类型：BSP、DRIVER、EXAMPLES
- 每个发布可包含多个包（源码/二进制/文档）
- 支持 Git commit 信息提取
- 发布状态管理：草稿 → 已发布 → 已归档

### 下载管理

- 基于许可证的权限控制
- 支持按内容类型下载
- 下载审计日志

### 备份恢复

- **热备份**：快速恢复，支持数据库 + 存储文件
- **冷备份**：长期归档，支持多种后端：
  - 本地文件系统
  - AWS S3 / Glacier
  - SFTP 服务器
  - FTP 服务器

### 自动化测试

发布前可选运行测试套件：

```bash
release-portal publish --type BSP --version 1.0.0 --test
release-portal publish --type BSP --version 1.0.0 --test --test-level all
```

测试级别：`critical`（默认）、`all`、`api`、`integration`

## 配置

### 环境变量

```bash
# 数据库
export RELEASE_PORTAL_DB="./data/portal.db"

# 安全配置
export RELEASE_PORTAL_SECRET="your-secret-key"
export RELEASE_PORTAL_TOKEN_EXPIRY_HOURS=24

# 存储配置
export RELEASE_PORTAL_STORAGE_DIR="./storage"
export RELEASE_PORTAL_MAX_UPLOAD_SIZE=500  # MB

# 备份配置
export RELEASE_PORTAL_BACKUP_DIR="./backups"
export RELEASE_PORTAL_BACKUP_RETENTION_DAYS=30
```

## 开发

### 运行测试

```bash
# 安装测试依赖
pip install -r requirements-test.txt

# 运行全部测试
python run_tests.sh

# 运行单元测试
pytest tests/unit -v

# 运行 API 测试
pytest tests/api -v

# 运行集成测试
pytest tests/integration -v
```

### 代码质量

```bash
# Lint
ruff check .

# Format
ruff format .
```

## 文档导航

### 快速入门

- [嵌入式工程师发布指南](docs/EMBEDDED_ENGINEER_GUIDE.md) - 完整使用指南
- [功能概览](docs/FEATURES.md) - 系统功能介绍

### 详细文档

| 文档 | 描述 |
|------|------|
| [使用手册](docs_archive/core_docs/USER_MANUAL.md) | 完整使用说明 |
| [部署指南](docs_archive/DEPLOYMENT_GUIDE.md) | 生产环境部署 |
| [Docker部署](docs_archive/DOCKER_DEPLOYMENT.md) | 容器化部署 |
| [解耦设计](docs_archive/DECOUPLING_DESIGN.md) | 系统架构设计 |

### 归档文档

- [核心文档](docs_archive/core_docs/) - 项目总览、快速入门、变更日志
- [开发文档](docs_archive/development_docs/) - 自动化测试、备份功能、代码改进
- [Binary Manager V2](docs_archive/binary_manager_docs/) - V2 版本文档

## 许可证

MIT License

## 联系方式

- **问题反馈**: https://github.com/qinyusen/release_system/issues
- **项目主页**: https://github.com/qinyusen/release_system

---

**版本**: 3.1.0 | **更新日期**: 2026-03-19 | **维护团队**: Release Platform Team
