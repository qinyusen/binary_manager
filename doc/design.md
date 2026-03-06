# 这里是整个项目的设计文档

## 项目概要
项目是服务于一个芯片团队的BSP团队，还有嵌入式应用软件团队

这些团队主要以C和C++为主，有部分python

---

# 地瓜机器人发布平台 V3 设计文档

## 1. 系统概述

### 1.1 目标
构建一个基于 Binary Manager V2 的软件发布平台，用于发布地瓜机器人的 BSP（Board Support Package）、驱动程序和示例程序，实现基于权限的受控下载。

### 1.2 核心特性
- ✅ **多类型资源发布**：支持 BSP、驱动、示例程序三种资源类型
- ✅ **分类打包**：源码、二进制、文档分别打包，便于权限控制
- ✅ **混合鉴权模式**：结合角色（RBAC）和许可证的灵活权限控制
- ✅ **双发布渠道**：支持 CLI 和 Web 两种发布方式
- ✅ **权限分级下载**：
  - 完全访问：源码 + 二进制 + 文档
  - 受限访问：二进制 + 文档

### 1.3 技术栈
- **核心框架**：Binary Manager V2（洋葱架构）
- **数据库**：SQLite（扩展现有 schema）
- **Web 框架**：Flask
- **依赖管理**：基于现有 requirements_v2.txt，新增 Flask 相关
- **存储**：本地存储 / S3（复用 Binary Manager V2）

---

## 2. 核心概念和术语

### 2.1 资源类型（Resource Type）
- **BSP**：板级支持包，包含硬件抽象层、启动代码等
- **Driver**：驱动程序，包含外设驱动、传感器驱动等
- **Examples**：示例程序，包含演示代码、教程等

### 2.2 内容类型（Content Type）
- **Source**：源代码（如 .c, .h, .py, .cpp）
- **Binary**：二进制库（如 .so, .a, .bin, .elf）
- **Document**：文档（如 .pdf, .md, .html, .txt）

### 2.3 包命名规范
采用 `类型-产品-版本` 格式：
```
bsp-diggo-v1.0.0-source.tar.gz
bsp-diggo-v1.0.0-binary.tar.gz
bsp-diggo-v1.0.0-doc.tar.gz

driver-diggo-v2.1.0-source.tar.gz
driver-diggo-v2.1.0-binary.tar.gz
driver-diggo-v2.1.0-doc.tar.gz

examples-diggo-v1.5.0-source.tar.gz
examples-diggo-v1.5.0-doc.tar.gz
```

### 2.4 权限层级
- **FULL_ACCESS**：可下载源码 + 二进制 + 文档
- **BINARY_ACCESS**：可下载二进制 + 文档

### 2.5 角色（Role）
- **Admin**：管理员，可发布、管理所有资源
- **Publisher**：发布者，可发布指定类型的资源
- **Customer**：客户，根据权限下载资源

### 2.6 许可证（License）
- 授权给特定客户或组织的访问凭证
- 包含权限层级、有效期、允许访问的资源类型等信息

---

## 3. 架构设计

### 3.1 整体架构
基于 Binary Manager V2 的洋葱架构，在其之上添加一个新的应用层：

```
┌─────────────────────────────────────────────────┐
│   Presentation Layer                            │
│   ├── CLI (发布工具)                            │
│   ├── Web UI (Flask API + 前端页面)             │
│   └── TUI (终端界面)                            │ ✅ 新增
├─────────────────────────────────────────────────┤
│   Application Layer (Release Portal)            │
│   ├── ReleaseService (发布服务)                 │
│   ├── AuthService (认证服务)                    │
│   ├── DownloadService (下载服务)                │
│   ├── LicenseService (许可证服务)               │
│   ├── AuditService (审计服务)                   │ ✅ 新增
│   ├── BackupService (备份服务)                  │ ✅ 新增
│   └── TestRunner (测试运行器)                   │ ✅ 新增
├─────────────────────────────────────────────────┤
│   Binary Manager V2                             │
│   ├── PublisherService (打包服务)               │
│   ├── DownloaderService (下载服务)              │
│   └── GroupService (分组服务)                   │
├─────────────────────────────────────────────────┤
│   Domain Layer (领域层)                         │
│   ├── User, Role, License (实体)                │
│   ├── Package, Version (实体)                   │
│   ├── Release (实体)                            │
│   ├── AuditLog (实体)                           │ ✅ 新增
│   ├── Backup (实体)                             │ ✅ 新增
│   └── ColdBackup (实体)                         │ ✅ 新增
├─────────────────────────────────────────────────┤
│   Infrastructure Layer (基础设施层)              │
│   ├── SQLite (数据库)                           │
│   ├── Storage (S3/本地存储)                     │
│   ├── Git (Git 服务)                            │
│   └── Auth (JWT Token 服务)                     │
└─────────────────────────────────────────────────┘
```

### 3.2 目录结构
```
release_portal/                  # 发布平台模块
├── domain/                      # 领域层
│   ├── entities/
│   │   ├── user.py             # 用户实体
│   │   ├── role.py             # 角色实体
│   │   ├── license.py          # 许可证实体
│   │   ├── release.py          # 发布记录实体
│   │   └── permission.py       # 权限值对象
│   ├── repositories/
│   │   ├── user_repository.py  # 用户仓储接口
│   │   ├── role_repository.py  # 角色仓储接口
│   │   ├── license_repository.py # 许可证仓储接口
│   │   └── release_repository.py # 发布仓储接口
│   └── services/
│       └── auth_service.py     # 认证领域服务
├── infrastructure/
│   ├── database/
│   │   ├── sqlite_user_repository.py
│   │   ├── sqlite_role_repository.py
│   │   ├── sqlite_license_repository.py
│   │   └── sqlite_release_repository.py
│   └── auth/
│       └── token_service.py    # JWT Token 服务
├── application/
│   ├── release_service.py      # 发布服务（编排）
│   ├── auth_service.py         # 认证服务（编排）
│   ├── download_service.py     # 下载服务（权限过滤）
│   ├── license_service.py      # 许可证管理服务
│   ├── audit_service.py        # 审计服务 ✅ 新增
│   ├── backup_service.py       # 备份服务 ✅ 新增
│   └── test_runner.py          # 测试运行器 ✅ 新增
├── presentation/
│   ├── cli/
│   │   └── portal_cli.py       # 发布工具 CLI
│   ├── web/
│   │   ├── app.py              # Flask 应用
│   │   ├── api/
│   │   │   ├── auth.py         # 认证 API
│   │   │   ├── releases.py     # 发布 API
│   │   │   ├── downloads.py    # 下载 API
│   │   │   ├── licenses.py     # 许可证 API
│   │   │   ├── audit.py        # 审计 API ✅ 新增
│   │   │   ├── backup.py       # 备份 API ✅ 新增
│   │   │   └── cold_backup.py  # 冷备份 API ✅ 新增
│   │   └── templates/          # 前端模板
│   │       ├── login.html      # 登录页
│   │       ├── dashboard.html  # 仪表盘 ✅ 新增
│   │       ├── releases.html   # 发布管理
│   │       ├── downloads.html  # 下载中心
│   │       ├── licenses.html   # 许可证管理
│   │       ├── backup.html     # 备份管理 ✅ 新增
│   │       ├── cold_backup.html # 冷备份管理 ✅ 新增
│   │       └── audit.html      # 审计日志 ✅ 新增
│   └── tui/                    # 终端界面 ✅ 新增
│       └── curses_cli.py
├── shared/
│   ├── config.py               # 配置管理
│   └── exceptions.py           # 异常定义
└── requirements_v3.txt         # 依赖清单
```

---

## 4. 数据模型设计

### 4.1 用户（User）
```python
class User:
    user_id: str              # 用户唯一标识
    username: str             # 用户名
    email: str                # 邮箱
    password_hash: str        # 密码哈希
    role: Role                # 角色
    license_id: Optional[str] # 关联的许可证（客户）
    created_at: datetime
    is_active: bool
```

### 4.2 角色（Role）
```python
class Role:
    role_id: str
    name: str                 # Admin, Publisher, Customer
    permissions: List[Permission]
    description: str
```

### 4.3 许可证（License）
```python
class License:
    license_id: str           # 许可证唯一标识（如 UUID）
    organization: str         # 组织/客户名称
    access_level: AccessLevel # FULL_ACCESS or BINARY_ACCESS
    allowed_resource_types: List[ResourceType] # [BSP, Driver, Examples]
    expires_at: Optional[datetime]
    created_at: datetime
    is_active: bool
    metadata: Dict            # 额外信息（如联系方式、备注）
```

### 4.4 发布记录（Release）
```python
class Release:
    release_id: str           # 发布唯一标识
    resource_type: ResourceType # BSP, Driver, Examples
    version: str              # 版本号
    content_packages: Dict[ContentType, PackageId] # {Source: pkg_id, Binary: pkg_id, Doc: pkg_id}
    publisher_id: str         # 发布者用户 ID
    status: ReleaseStatus     # DRAFT, PUBLISHED, ARCHIVED
    created_at: datetime
    published_at: Optional[datetime]
    description: str
    changelog: str
```

### 4.5 权限（Permission）- 值对象
```python
class Permission:
    resource: str             # 资源操作：publish, download, manage_users
    resource_types: List[ResourceType] # 可操作的资源类型
```

### 4.6 数据库 Schema（SQLite 扩展）

```sql
-- 用户表
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id TEXT NOT NULL,
    license_id TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id),
    FOREIGN KEY (license_id) REFERENCES licenses(license_id)
);

-- 角色表
CREATE TABLE roles (
    role_id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- 角色权限关联表
CREATE TABLE role_permissions (
    role_id TEXT,
    permission TEXT,
    resource_type TEXT,
    PRIMARY KEY (role_id, permission, resource_type),
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

-- 许可证表
CREATE TABLE licenses (
    license_id TEXT PRIMARY KEY,
    organization TEXT NOT NULL,
    access_level TEXT NOT NULL, -- 'FULL_ACCESS' or 'BINARY_ACCESS'
    expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT -- JSON 格式
);

-- 许可证资源类型关联表
CREATE TABLE license_resource_types (
    license_id TEXT,
    resource_type TEXT, -- 'BSP', 'DRIVER', 'EXAMPLES'
    PRIMARY KEY (license_id, resource_type),
    FOREIGN KEY (license_id) REFERENCES licenses(license_id)
);

-- 发布记录表
CREATE TABLE releases (
    release_id TEXT PRIMARY KEY,
    resource_type TEXT NOT NULL, -- 'BSP', 'DRIVER', 'EXAMPLES'
    version TEXT NOT NULL,
    source_package_id TEXT,
    binary_package_id TEXT,
    doc_package_id TEXT,
    publisher_id TEXT NOT NULL,
    status TEXT DEFAULT 'DRAFT', -- 'DRAFT', 'PUBLISHED', 'ARCHIVED'
    description TEXT,
    changelog TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP,
    FOREIGN KEY (publisher_id) REFERENCES users(user_id),
    FOREIGN KEY (source_package_id) REFERENCES packages(id),
    FOREIGN KEY (binary_package_id) REFERENCES packages(id),
    FOREIGN KEY (doc_package_id) REFERENCES packages(id)
);

-- 审计日志表 ✅ 新增
CREATE TABLE audit_logs (
    log_id TEXT PRIMARY KEY,
    user_id TEXT,
    username TEXT,
    action TEXT NOT NULL,          -- 'login', 'publish', 'download', etc.
    resource_type TEXT,
    resource_id TEXT,
    details TEXT,                  -- JSON 格式
    ip_address TEXT,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- 备份表 ✅ 新增
CREATE TABLE backups (
    backup_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    filename TEXT NOT NULL,
    size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    includes_storage BOOLEAN DEFAULT 0,
    metadata TEXT,                 -- JSON 格式
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- 冷备份表 ✅ 新增
CREATE TABLE cold_backups (
    backup_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    filename TEXT NOT NULL,
    size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    storage_location TEXT,         -- 'local', 's3', 'azure', etc.
    checksum TEXT,
    metadata TEXT                  -- JSON 格式
);
```

### 4.7 审计日志（AuditLog）✅ 新增

```python
class AuditLog:
    log_id: str
    user_id: str
    username: str
    action: str              # login, publish, download, etc.
    resource_type: str
    resource_id: str
    details: Dict
    ip_address: str
    user_agent: str
    timestamp: datetime
```

### 4.8 备份（Backup）✅ 新增

```python
class Backup:
    backup_id: str
    name: str
    filename: str
    size: int
    created_at: datetime
    created_by: str
    includes_storage: bool
    metadata: Dict
```

### 4.9 冷备份（ColdBackup）✅ 新增

```python
class ColdBackup:
    backup_id: str
    name: str
    filename: str
    size: int
    created_at: datetime
    storage_location: str    # local/s3/azure
    checksum: str
    metadata: Dict
```

---

## 5. 权限控制设计

### 5.1 权限矩阵

| 角色 | 发布资源 | 下载源码 | 下载二进制 | 下载文档 | 管理用户 | 管理许可证 |
|------|---------|---------|-----------|---------|---------|-----------|
| Admin | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Publisher | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Customer (FULL) | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| Customer (BINARY) | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ |

### 5.2 认证流程

#### CLI 方式
```bash
# 登录获取 Token
release-portal login --username engineer --password-stdin

# Token 存储在 ~/.release-portal/config.json
{
  "user_id": "user_123",
  "username": "engineer",
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "expires_at": "2026-03-02T10:00:00Z"
}

# 发布时自动附带 Token
release-portal publish \
  --type bsp \
  --version v1.0.0 \
  --source ./bsp-source \
  --binary ./bsp-binary \
  --doc ./bsp-doc
```

#### Web 方式
```bash
# 登录获取 Token
POST /api/auth/login
{
  "username": "engineer",
  "password": "password"
}

# 返回
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "user_id": "user_123",
    "username": "engineer",
    "role": "Publisher"
  }
}

# 后续请求在 Header 中携带 Token
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### 5.3 下载权限过滤

```python
class DownloadService:
    def get_available_packages(self, user: User, release_id: str) -> List[PackageInfo]:
        license = self.license_service.get_user_license(user)
        release = self.release_repository.find_by_id(release_id)
        
        available_packages = []
        
        # 根据权限级别过滤可下载的包
        if license.access_level == AccessLevel.FULL_ACCESS:
            # 可下载源码 + 二进制 + 文档
            if release.source_package_id:
                available_packages.append(self.get_package(release.source_package_id))
            if release.binary_package_id:
                available_packages.append(self.get_package(release.binary_package_id))
            if release.doc_package_id:
                available_packages.append(self.get_package(release.doc_package_id))
        
        elif license.access_level == AccessLevel.BINARY_ACCESS:
            # 只能下载二进制 + 文档
            if release.binary_package_id:
                available_packages.append(self.get_package(release.binary_package_id))
            if release.doc_package_id:
                available_packages.append(self.get_package(release.doc_package_id))
        
        return available_packages
```

---

## 6. API 设计

### 6.1 CLI 命令

#### 认证命令
```bash
# 登录
release-portal login --username <username> --password-stdin

# 登出
release-portal logout

# 查看当前用户
release-portal whoami
```

#### 发布命令
```bash
# 发布（自动打包源码、二进制、文档）
release-portal publish \
  --type <bsp|driver|examples> \
  --version <version> \
  --source-dir <path> \
  --binary-dir <path> \
  --doc-dir <path> \
  --description <text> \
  --changelog <text>

# 发布草稿
release-portal publish \
  --type bsp \
  --version v1.0.0 \
  --source-dir ./bsp/source \
  --binary-dir ./bsp/build \
  --doc-dir ./bsp/doc \
  --draft

# 从草稿发布
release-portal publish --release-id <release-id> --publish
```

#### 查询命令
```bash
# 列出所有发布
release-portal list --type <bsp|driver|examples>

# 查看发布详情
release-portal info --release-id <release-id>

# 搜索发布
release-portal search --query <keyword>
```

#### 下载命令
```bash
# 下载（根据权限自动过滤）
release-portal download \
  --release-id <release-id> \
  --output <path>

# 下载指定内容类型
release-portal download \
  --release-id <release-id> \
  --content-type <source|binary|doc> \
  --output <path>
```

#### 许可证管理（管理员）
```bash
# 创建许可证
release-portal license create \
  --organization <name> \
  --access-level <full|binary> \
  --resource-types <bsp,driver,examples> \
  --expires-at <date>

# 列出许可证
release-portal license list

# 撤销许可证
release-portal license revoke --license-id <license-id>
```

### 6.2 REST API

#### 认证 API
```python
# 登录
POST /api/auth/login
Request: {"username": "user", "password": "pass"}
Response: {"token": "jwt_token", "user": {...}}

# 登出
POST /api/auth/logout
Headers: Authorization: Bearer <token>

# 验证 Token
GET /api/auth/verify
Headers: Authorization: Bearer <token>
Response: {"valid": true, "user": {...}}
```

#### 发布 API
```python
# 创建发布草稿
POST /api/releases
Headers: Authorization: Bearer <token>
Request: {
  "resource_type": "BSP",
  "version": "v1.0.0",
  "description": "Initial release",
  "changelog": "First version"
}
Response: {"release_id": "rel_123", "status": "DRAFT"}

# 上传包文件
POST /api/releases/{release_id}/packages
Headers: Authorization: Bearer <token>
Request: Multipart/form-data
  - source_file: (file)
  - binary_file: (file)
  - doc_file: (file)
Response: {"package_ids": {...}}

# 发布
POST /api/releases/{release_id}/publish
Headers: Authorization: Bearer <token>

# 列出发布
GET /api/releases?type=BSP&status=PUBLISHED
Response: {"releases": [...]}

# 获取发布详情
GET /api/releases/{release_id}
Response: {"release": {...}}
```

#### 下载 API
```python
# 获取可下载包列表（根据权限过滤）
GET /api/releases/{release_id}/packages
Headers: Authorization: Bearer <token>
Response: {
  "packages": [
    {"content_type": "binary", "package_id": "pkg_123", "size": 1024},
    {"content_type": "doc", "package_id": "pkg_124", "size": 512}
  ]
}

# 下载包
GET /api/releases/{release_id}/download/{content_type}
Headers: Authorization: Bearer <token>
Response: Binary file stream
```

#### 许可证管理 API（管理员）
```python
# 创建许可证
POST /api/licenses
Headers: Authorization: Bearer <token> (Admin only)
Request: {
  "organization": "Company ABC",
  "access_level": "BINARY_ACCESS",
  "allowed_resource_types": ["BSP", "DRIVER"],
  "expires_at": "2027-01-01T00:00:00Z"
}
Response: {"license_id": "lic_123"}

# 列出许可证
GET /api/licenses
Response: {"licenses": [...]}

# 撤销许可证
DELETE /api/licenses/{license_id}
```

### 6.3 审计 API ✅ 新增

```python
# 获取审计日志
GET /api/audit/logs
Query Parameters:
  - start_date: 开始日期 (ISO 8601)
  - end_date: 结束日期 (ISO 8601)
  - user_id: 用户ID (可选)
  - action: 操作类型 (可选，如 login, publish, download)
  - resource_type: 资源类型 (可选)
  - page: 页码 (默认 1)
  - per_page: 每页数量 (默认 50)
Headers: Authorization: Bearer <token>
Response: {
  "logs": [
    {
      "log_id": "log_123",
      "user_id": "user_456",
      "username": "admin",
      "action": "publish",
      "resource_type": "BSP",
      "resource_id": "rel_789",
      "details": {...},
      "ip_address": "192.168.1.100",
      "timestamp": "2026-03-06T10:30:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 50
}

# 导出审计日志
GET /api/audit/logs/export
Query Parameters:
  - start_date: 开始日期
  - end_date: 结束日期
  - format: 导出格式 (csv, xlsx, json)
Headers: Authorization: Bearer <token>
Response: File download (CSV/Excel/JSON)

# 获取审计统计
GET /api/audit/stats
Query Parameters:
  - start_date: 开始日期
  - end_date: 结束日期
Headers: Authorization: Bearer <token>
Response: {
  "total_actions": 1000,
  "unique_users": 50,
  "actions_by_type": {
    "login": 200,
    "publish": 50,
    "download": 750
  },
  "actions_by_resource": {
    "BSP": 300,
    "DRIVER": 400,
    "EXAMPLES": 300
  }
}
```

### 6.4 备份 API ✅ 新增

```python
# 创建备份
POST /api/backup/create
Headers: Authorization: Bearer <token> (Admin/Publisher)
Request: {
  "name": "daily_backup",
  "include_storage": true
}
Response: {
  "backup_id": "backup_123",
  "filename": "backup_20260306.tar.gz",
  "size": 1073741824,
  "created_at": "2026-03-06T10:00:00Z"
}

# 列出备份
GET /api/backup/list
Headers: Authorization: Bearer <token>
Response: {
  "backups": [
    {
      "backup_id": "backup_123",
      "name": "daily_backup",
      "filename": "backup_20260306.tar.gz",
      "size": 1073741824,
      "created_at": "2026-03-06T10:00:00Z"
    }
  ]
}

# 恢复备份
POST /api/backup/restore
Headers: Authorization: Bearer <token> (Admin only)
Request: {
  "backup_filename": "backup_20260306.tar.gz",
  "restore_storage": true
}
Response: {
  "message": "Backup restored successfully",
  "restored_at": "2026-03-06T11:00:00Z"
}

# 下载备份
GET /api/backup/{backup_id}/download
Headers: Authorization: Bearer <token> (Admin/Publisher)
Response: Binary file stream

# 删除备份
DELETE /api/backup/{backup_id}
Headers: Authorization: Bearer <token> (Admin only)
Response: {"message": "Backup deleted successfully"}
```

### 6.5 冷备份 API ✅ 新增

```python
# 创建冷备份
POST /api/cold-backup/create
Headers: Authorization: Bearer <token> (Admin only)
Request: {
  "name": "monthly_archive",
  "storage_location": "s3",  # or "local", "azure"
  "metadata": {
    "description": "Monthly cold backup for compliance",
    "retention_years": 7
  }
}
Response: {
  "backup_id": "cold_backup_456",
  "name": "monthly_archive",
  "filename": "cold_backup_20260306.tar.gz",
  "size": 5368709120,
  "checksum": "sha256:abc123...",
  "created_at": "2026-03-06T10:00:00Z"
}

# 列出冷备份
GET /api/cold-backup/list
Headers: Authorization: Bearer <token>
Response: {
  "backups": [
    {
      "backup_id": "cold_backup_456",
      "name": "monthly_archive",
      "filename": "cold_backup_20260306.tar.gz",
      "size": 5368709120,
      "storage_location": "s3",
      "created_at": "2026-03-06T10:00:00Z"
    }
  ]
}

# 上传外部冷备份
POST /api/cold-backup/upload
Headers: Authorization: Bearer <token> (Admin only)
Request: Multipart/form-data
  - backup_file: (file)
  - name: "external_backup_20260306"
  - metadata: JSON string
Response: {
  "backup_id": "cold_backup_789",
  "message": "Cold backup uploaded successfully"
}

# 从冷备份恢复
POST /api/cold-backup/restore
Headers: Authorization: Bearer <token> (Admin only)
Request: {
  "backup_id": "cold_backup_456"
}
Response: {
  "message": "Cold backup restored successfully",
  "restored_at": "2026-03-06T11:00:00Z"
}

# 删除冷备份
DELETE /api/cold-backup/{backup_id}
Headers: Authorization: Bearer <token> (Admin only)
Response: {"message": "Cold backup deleted successfully"}
```

---

## 7. 发布流程设计

### 7.1 CLI 发布流程

```mermaid
sequenceDiagram
    participant Engineer
    participant CLI
    participant Portal Service
    participant Binary Manager V2
    participant Storage

    Engineer->>CLI: 执行 publish 命令
    CLI->>CLI: 读取 Token 配置
    CLI->>Portal Service: 创建发布草稿
    Portal Service-->>CLI: 返回 release_id
    
    CLI->>CLI: 扫描源码目录
    CLI->>Binary Manager V2: 打包源码 (PublisherService)
    Binary Manager V2->>Storage: 上传源码包
    Binary Manager V2-->>CLI: 返回 package_id
    
    CLI->>CLI: 扫描二进制目录
    CLI->>Binary Manager V2: 打包二进制 (PublisherService)
    Binary Manager V2->>Storage: 上传二进制包
    Binary Manager V2-->>CLI: 返回 package_id
    
    CLI->>CLI: 扫描文档目录
    CLI->>Binary Manager V2: 打包文档 (PublisherService)
    Binary Manager V2->>Storage: 上传文档包
    Binary Manager V2-->>CLI: 返回 package_id
    
    CLI->>Portal Service: 关联 package_id 到 release
    CLI->>Portal Service: 发布 release
    Portal Service-->>Engineer: 发布成功
```

### 7.2 Web 发布流程

```mermaid
sequenceDiagram
    participant Publisher
    participant Web UI
    participant Portal Service
    participant Binary Manager V2
    participant Storage

    Publisher->>Web UI: 登录
    Web UI->>Portal Service: POST /auth/login
    Portal Service-->>Web UI: 返回 Token
    Web UI-->>Publisher: 显示发布页面

    Publisher->>Web UI: 填写发布信息
    Publisher->>Web UI: 上传文件（拖拽）
    Web UI->>Portal Service: POST /releases (创建草稿)
    
    Publisher->>Web UI: 上传源码 zip
    Web UI->>Portal Service: POST /releases/{id}/packages
    Portal Service->>Binary Manager V2: 保存并记录 package
    Binary Manager V2->>Storage: 上传源码包
    
    Publisher->>Web UI: 上传二进制 zip
    Web UI->>Portal Service: POST /releases/{id}/packages
    Portal Service->>Binary Manager V2: 保存并记录 package
    Binary Manager V2->>Storage: 上传二进制包
    
    Publisher->>Web UI: 上传文档 zip
    Web UI->>Portal Service: POST /releases/{id}/packages
    Portal Service->>Binary Manager V2: 保存并记录 package
    Binary Manager V2->>Storage: 上传文档包
    
    Publisher->>Web UI: 点击"发布"按钮
    Web UI->>Portal Service: POST /releases/{id}/publish
    Portal Service-->>Publisher: 发布成功
```

---

## 8. 下载流程设计

### 8.1 客户端下载流程

```mermaid
sequenceDiagram
    participant Customer
    participant CLI/Web
    participant Portal Service
    participant License Service
    participant Storage

    Customer->>CLI/Web: 登录（提供许可证）
    CLI/Web->>Portal Service: 验证许可证
    Portal Service->>License Service: 查询许可证
    License Service-->>Portal Service: 返回权限信息
    Portal Service-->>CLI/Web: 返回 Token

    Customer->>CLI/Web: 浏览可用发布
    CLI/Web->>Portal Service: GET /releases
    Portal Service-->>CLI/Web: 返回发布列表

    Customer->>CLI/Web: 选择发布并下载
    CLI/Web->>Portal Service: GET /releases/{id}/packages
    Portal Service->>License Service: 检查下载权限
    License Service-->>Portal Service: 返回可下载内容类型
    Portal Service-->>CLI/Web: 返回可下载包列表

    Customer->>CLI/Web: 下载包
    CLI/Web->>Storage: 下载文件
    Storage-->>Customer: 返回文件流
```

### 8.2 权限检查逻辑

```python
def check_download_permission(user: User, release: Release, content_type: ContentType) -> bool:
    """
    检查用户是否有权限下载指定内容类型
    """
    # 1. 获取用户的许可证
    license = license_repository.find_by_id(user.license_id)
    if not license or not license.is_active:
        return False
    
    # 2. 检查许可证是否过期
    if license.expires_at and license.expires_at < datetime.utcnow():
        return False
    
    # 3. 检查许可证是否允许访问该资源类型
    if release.resource_type not in license.allowed_resource_types:
        return False
    
    # 4. 根据访问级别检查内容类型
    if license.access_level == AccessLevel.FULL_ACCESS:
        return True  # 可下载所有类型
    
    elif license.access_level == AccessLevel.BINARY_ACCESS:
        # 只能下载二进制和文档
        return content_type in [ContentType.BINARY, ContentType.DOC]
    
    return False
```

---

## 9. Web UI 设计

### 9.1 实际实现的页面 ✅ 已更新

#### 登录页 (`login.html`)
- 用户名/密码输入
- "记住我"选项
- 登录按钮
- 错误提示
- 响应式设计

#### 仪表盘 (`dashboard.html`) ✅ 新增
- 系统概览统计卡片
  - 总发布数
  - 总用户数
  - 总许可证数
  - 最近活动
- 最近发布列表（前5条）
- 最近下载记录（前10条）
- 系统健康状态
  - 数据库状态
  - 存储空间使用
  - 服务运行时间

#### 发布管理页 (`releases.html`)
- 发布列表表格
  - 资源类型、版本、状态、发布时间、发布者
  - 操作按钮：查看、编辑、发布、归档、删除
- 筛选功能（按类型、状态）
- "新建发布"按钮
- 分页和搜索
- 创建发布模态框
  - 资源类型选择（BSP/Driver/Examples）
  - 版本号输入
  - 描述和更新日志
  - 文件上传（支持拖拽）
  - 保存草稿/立即发布

#### 下载中心 (`downloads.html`)
- 可下载资源列表（根据许可证过滤）
- 资源类型标签
- 权限说明（FULL_ACCESS / BINARY_ACCESS）
- 一键下载按钮
- 下载历史记录
- 搜索和筛选

#### 许可证管理页 (`licenses.html`) - Admin 专用
- 许可证列表表格
  - 许可证 ID、组织、访问级别、资源类型、有效期、状态
  - 操作按钮：查看、编辑、延期、撤销
- "新建许可证"按钮
- 许可证创建模态框
  - 组织名称
  - 访问级别选择
  - 资源类型多选
  - 有效期设置
- 延期功能

#### 备份管理页 (`backup.html`) ✅ 新增
- 备份列表表格
  - 备份名称、文件名、大小、创建时间、创建者
  - 操作按钮：下载、恢复、删除
- "创建备份"按钮
- 创建备份模态框
  - 备份名称
  - 是否包含存储
- 备份统计信息
  - 备份总数
  - 总存储占用
  - 最近备份时间

#### 冷备份管理页 (`cold_backup.html`) ✅ 新增
- 冷备份列表表格
  - 备份名称、文件名、大小、存储位置、创建时间
  - 操作按钮：下载、恢复、删除
- "创建冷备份"按钮
- "上传外部备份"按钮
- 存储位置配置
- 冷备份归档策略

#### 审计日志页 (`audit.html`) ✅ 新增
- 操作日志列表
  - 时间、用户、操作类型、资源、详情
- 高级筛选
  - 时间范围
  - 用户筛选
  - 操作类型筛选
  - 资源类型筛选
- 日志详情查看
- 日志导出功能（CSV/Excel）
- 操作统计图表
  - 操作趋势
  - 用户活跃度
  - 资源访问统计

### 9.2 UI 设计特点

#### 视觉设计
- **色彩方案**：紫色渐变主题 (#667eea → #764ba2)
- **卡片式布局**：圆角阴影设计
- **状态徽章**：彩色标识不同状态（草稿/已发布/已归档）
- **响应式设计**：适配桌面、平板、手机

#### 交互设计
- **模态框**：用于创建和编辑操作
- **实时搜索**：列表页即时筛选
- **拖拽上传**：文件上传支持拖拽
- **加载动画**：操作反馈
- **Toast 通知**：操作成功/失败提示

### 9.3 UI 技术栈

#### 实际使用的技术
- **后端**：Flask + Jinja2 模板引擎
- **前端框架**：Bootstrap 5.3
- **图标库**：Bootstrap Icons
- **JavaScript**：Vanilla JS（无额外框架依赖）
- **AJAX**：Fetch API
- **文件上传**：Dropzone.js 集成
- **图表**：Chart.js（用于审计统计）

#### 特性
- **无依赖前端**：不需要 npm/webpack
- **CDN 加速**：静态资源通过 CDN 加载
- **客户端存储**：sessionStorage 存储 Token
- **异步加载**：动态加载内容

---

## 10. 扩展功能 ✅ 新增章节

### 10.1 审计日志系统

#### 功能概述
记录系统中所有关键操作，提供完整的操作追踪和审计能力。

#### 记录的操作类型
- **用户操作**
  - 登录/登出
  - 密码修改
  - 用户创建/删除
- **发布操作**
  - 创建发布草稿
  - 上传包文件
  - 发布版本
  - 归档版本
- **许可证操作**
  - 创建许可证
  - 撤销许可证
  - 延期许可证
- **下载操作**
  - 下载包文件
  - 查看发布详情
- **系统操作**
  - 数据库备份
  - 配置变更
  - 系统启动/停止

#### 审计数据字段
```python
{
    "log_id": "uuid",
    "user_id": "user_123",
    "username": "admin",
    "action": "publish",
    "resource_type": "BSP",
    "resource_id": "rel_456",
    "details": {
        "version": "v1.0.0",
        "packages": ["source", "binary", "doc"]
    },
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "timestamp": "2026-03-06T10:30:00Z"
}
```

#### 查询和导出
- 按时间范围查询
- 按用户筛选
- 按操作类型筛选
- 按资源类型筛选
- 导出为 CSV/Excel/JSON
- 实时统计和图表

### 10.2 备份管理系统

#### 功能概述
提供完整的数据库和存储备份能力，支持手动和自动备份。

#### 备份类型
- **完整备份**：数据库 + 存储文件
- **数据库备份**：仅数据库
- **增量备份**：仅备份变更部分

#### 备份策略
```python
{
    "backup_name": "daily_backup",
    "include_storage": True,
    "retention_days": 30,
    "schedule": {
        "type": "cron",
        "expression": "0 2 * * *"  # 每天凌晨2点
    }
}
```

#### 备份操作
- 创建备份（手动/自动）
- 列出备份
- 下载备份文件
- 恢复备份
- 删除旧备份
- 备份验证（checksum）

#### 备份存储
- 本地存储
- S3 云存储
- Azure Blob Storage
- Google Cloud Storage

### 10.3 冷备份系统

#### 功能概述
长期归档备份，用于合规性和灾难恢复。

#### 冷备份特点
- **长期保存**：保留 7 年或更久
- **只读存储**：防止修改和删除
- **离线存储**：可存储到离线介质
- **加密存储**：支持加密归档

#### 冷备份流程
```
1. 创建备份快照
2. 压缩和加密
3. 计算校验和
4. 上传到长期存储（S3 Glacier/Azure Archive）
5. 记录元数据
```

#### 冷备份操作
- 创建冷备份
- 上传外部备份
- 列出冷备份
- 从冷备份恢复
- 删除冷备份（需要特殊权限）
- 验证备份完整性

### 10.4 自动化测试系统

#### 功能概述
在发布前自动运行测试套件，确保发布的版本质量。

#### 测试级别
- **Critical（关键测试）**
  - 测试内容：核心功能验证
  - 耗时：约 30 秒
  - 用途：日常发布
  - 测试用例：约 10 个

- **All（完整测试）**
  - 测试内容：所有测试
  - 耗时：约 2 分钟
  - 用途：重要版本
  - 测试用例：约 54 个

- **API（API 测试）**
  - 测试内容：API 端点
  - 耗时：约 1 分钟
  - 用途：API 验证
  - 测试用例：约 31 个

- **Integration（集成测试）**
  - 测试内容：端到端流程
  - 耗时：约 1 分钟
  - 用途：流程验证
  - 测试用例：约 15 个

#### 测试流程
```mermaid
graph LR
    A[发布请求] --> B{启用测试?}
    B -->|否| C[直接发布]
    B -->|是| D[运行测试]
    D --> E{测试通过?}
    E -->|是| C
    E -->|否| F[阻止发布]
    F --> G[返回错误]
```

#### 测试结果
```python
{
    "passed": True,
    "total_tests": 10,
    "passed_tests": 10,
    "failed_tests": 0,
    "skipped_tests": 0,
    "duration": 28.45,
    "errors": []
}
```

#### CLI 集成
```bash
# 发布时运行测试
release-portal publish \
  --type bsp \
  --version v1.0.0 \
  --test \
  --test-level critical

# 发布时跳过测试（开发环境）
release-portal publish \
  --type bsp \
  --version v1.0.0 \
  --skip-test
```

#### API 集成
```python
POST /api/releases/{release_id}/publish
Headers: Authorization: Bearer <token>
Request: {
    "run_tests": True,
    "test_level": "critical"
}
```

---

## 10. 安全设计

### 10.1 认证和授权
- **密码存储**：使用 bcrypt 或 Argon2 哈希
- **Token**：JWT（JSON Web Token），有效期 24 小时
- **Token 存储**：
  - CLI：存储在 `~/.release-portal/config.json`
  - Web：存储在 HttpOnly Cookie

### 10.2 HTTPS 和传输安全
- 生产环境强制 HTTPS
- API 请求使用 TLS 加密

### 10.3 许可证安全
- 许可证 ID 使用 UUID v4（随机生成，难以猜测）
- 支持许可证撤销
- 许可证过期自动失效

### 10.4 文件安全
- 上传文件大小限制（如 500MB）
- 文件类型白名单
- 上传文件病毒扫描（可选，使用 ClamAV）

---

## 11. 部署方案

### 11.1 开发环境
```bash
# 安装依赖
pip install -r release_portal/requirements_v3.txt

# 初始化数据库
release-portal init --db ./dev.db

# 启动 Web 服务（开发模式）
export FLASK_APP=release_portal/presentation/web/app.py
export FLASK_ENV=development
flask run --host 0.0.0.0 --port 5000

# CLI 使用
release-portal --config ./dev-config.json publish --type bsp --version v1.0.0 ...
```

### 11.2 生产环境
```bash
# 使用 Gunicorn 部署 Flask
gunicorn -w 4 -b 0.0.0.0:5000 \
  release_portal.presentation.web.app:app

# 使用 systemd 管理
# /etc/systemd/system/release-portal.service
[Unit]
Description=Release Portal
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/release-portal
Environment="FLASK_ENV=production"
ExecStart=/usr/local/bin/gunicorn -w 4 -b 0.0.0.0:5000 \
  release_portal.presentation.web.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 11.3 Docker 部署
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY release_portal/requirements_v3.txt .
RUN pip install --no-cache-dir -r requirements_v3.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", \
     "release_portal.presentation.web.app:app"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./config:/app/config
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///data/portal.db
    restart: always
```

---

## 12. 实施计划

### Phase 1：核心功能开发（4 周）✅ 已完成
- Week 1-2：领域层和基础设施层
  - 实现 User, Role, License, Release 实体
  - 实现 SQLite 仓储
  - 实现认证服务（JWT）
- Week 3：应用层
  - 实现 ReleaseService, AuthService, DownloadService
  - 集成 Binary Manager V2 的 PublisherService
- Week 4：CLI 实现
  - 实现认证、发布、下载命令
  - 测试完整发布流程

### Phase 2：Web 服务开发（3 周）✅ 已完成
- Week 5：Flask API
  - 实现 REST API 端点
  - 权限中间件
- Week 6：Web UI
  - 实现登录、发布管理页面
  - 实现许可证管理页面
- Week 7：集成测试
  - 端到端测试
  - 性能测试

### Phase 3：扩展功能开发（3 周）✅ 已完成
- Week 8：审计和备份功能
  - 实现审计日志系统
  - 实现备份管理
  - 实现冷备份系统
- Week 9：自动化测试和 TUI
  - 实现发布前自动化测试
  - 实现终端用户界面（TUI）
- Week 10：完整测试和优化
  - 端到端测试
  - 性能优化
  - 安全加固

### Phase 4：文档和部署（2 周）✅ 已完成
- Week 11：文档编写
  - 用户手册
  - API 文档
  - 部署指南（DEPLOYMENT_GUIDE.md）
  - 快速开始（QUICKSTART_DEPLOYMENT.md）
  - Docker 部署（DOCKER_DEPLOYMENT.md）
  - 部署检查清单（DEPLOYMENT_CHECKLIST.md）
- Week 12：部署和上线
  - 生产环境部署
  - 监控和日志
  - 用户培训

**当前状态**: ✅ 所有核心功能和扩展功能已完成（2026-03-06）

---

## 13. 扩展性考虑

### 13.1 未来可能的功能
1. **多语言支持** - i18n 国际化
2. **通知系统** - 发布通知、许可证过期提醒
3. ~~审计日志~~ ✅ **已完成**
4. 版本比较 - 可视化比较不同版本的差异
5. ~~自动化测试~~ ✅ **已完成**
6. CI/CD 集成 - 与 Jenkins/GitLab CI 集成
7. 包签名 - GPG 签名验证
8. 多租户 - 支持多个组织独立管理
9. ~~备份功能~~ ✅ **已完成**
10. 实时监控 - Prometheus/Grafana 集成
11. API 限流 - 防止滥用
12. 高可用部署 - 集群部署、负载均衡
13. 消息队列 - 异步任务处理
14. 全文搜索 - ElasticSearch 集成
15. 移动端 APP - iOS/Android 客户端

### 13.2 性能优化
1. **缓存**：使用 Redis 缓存许可证和发布信息
2. **CDN**：静态文件和下载包使用 CDN 加速
3. **数据库优化**：添加索引，查询优化
4. **异步处理**：文件上传使用异步任务队列（Celery）

### 13.3 可扩展架构
- **仓储抽象**：未来可从 SQLite 迁移到 PostgreSQL
- **存储抽象**：未来可添加更多存储后端（Azure Blob, Google Cloud Storage）
- **认证扩展**：未来可支持 OAuth2、LDAP

---

## 14. 风险和挑战

### 14.1 技术风险
- **并发访问**：SQLite 在高并发下性能受限
  - 缓解：使用连接池，或迁移到 PostgreSQL
- **大文件上传**：网络不稳定可能导致上传失败
  - 缓解：实现分片上传和断点续传

### 14.2 业务风险
- **许可证泄露**：客户可能分享许可证文件
  - 缓解：限制同时登录数，监控异常下载行为
- **权限控制复杂度**：多种权限组合可能导致逻辑错误
  - 缓解：完善的单元测试和集成测试

---

## 15. 总结

本设计文档基于 Binary Manager V2 的洋葱架构，构建了一个完整的软件发布平台，实现了：

✅ **多类型资源发布**（BSP、Driver、Examples）
✅ **分类打包**（Source、Binary、Doc）
✅ **混合鉴权**（角色 + 许可证）
✅ **多发布渠道**（CLI + Web + TUI）
✅ **权限分级下载**（FULL_ACCESS, BINARY_ACCESS）
✅ **审计日志系统**（完整的操作追踪）
✅ **备份管理**（手动 + 自动备份）
✅ **冷备份系统**（长期归档）
✅ **自动化测试**（发布前质量保证）

系统采用分层架构，各层职责清晰，易于测试和维护。通过复用 Binary Manager V2 的打包和存储能力，减少了重复开发，提高了开发效率。

**核心优势**:
- 🎯 **架构清晰** - 洋葱架构，依赖方向正确
- 🔒 **安全可靠** - JWT 认证 + 许可证控制
- 📊 **可追溯性** - 完整的审计日志
- 💾 **数据安全** - 多重备份策略
- ✅ **质量保证** - 自动化测试集成
- 🚀 **易于部署** - 完善的部署指南和脚本

---

**文档版本**：v2.0  
**创建日期**：2026-03-01  
**最后更新**：2026-03-06  
**更新内容**：
- 新增审计日志系统设计
- 新增备份管理系统设计
- 新增冷备份系统设计
- 新增自动化测试系统设计
- 更新架构图和目录结构
- 更新 API 端点列表
- 更新 Web UI 页面列表
- 更新实施计划状态
- 更新扩展性考虑
