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
│   └── Web UI (Flask API + 前端页面)             │
├─────────────────────────────────────────────────┤
│   Application Layer (NEW - Release Portal)      │
│   ├── ReleaseService (发布服务)                 │
│   ├── AuthService (认证服务)                    │
│   ├── DownloadService (下载服务)                │
│   └── LicenseService (许可证服务)               │
├─────────────────────────────────────────────────┤
│   Binary Manager V2 (现有层)                    │
│   ├── PublisherService (打包服务)               │
│   ├── DownloaderService (下载服务)              │
│   └── GroupService (分组服务)                   │
├─────────────────────────────────────────────────┤
│   Domain Layer (领域层)                         │
│   ├── User, Role, License (新增实体)            │
│   ├── Package, Version (现有实体)               │
│   └── Release (新增实体)                        │
├─────────────────────────────────────────────────┤
│   Infrastructure Layer (基础设施层)              │
│   ├── SQLite (用户、权限数据库)                 │
│   ├── Storage (S3/本地存储)                     │
│   └── Git (现有 Git 服务)                       │
└─────────────────────────────────────────────────┘
```

### 3.2 目录结构
```
release_portal/                  # 新的发布平台模块
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
│   │   └── license_repository.py # 许可证仓储接口
│   └── services/
│       └── auth_service.py     # 认证领域服务
├── infrastructure/
│   ├── database/
│   │   ├── sqlite_user_repository.py
│   │   ├── sqlite_role_repository.py
│   │   └── sqlite_license_repository.py
│   └── auth/
│       └── jwt_token_service.py # JWT Token 服务
├── application/
│   ├── release_service.py      # 发布服务（编排）
│   ├── auth_service.py         # 认证服务（编排）
│   ├── download_service.py     # 下载服务（权限过滤）
│   └── license_service.py      # 许可证管理服务
├── presentation/
│   ├── cli/
│   │   └── portal_cli.py       # 发布工具 CLI
│   └── web/
│       ├── app.py              # Flask 应用
│       ├── api/
│       │   ├── auth.py         # 认证 API
│       │   ├── releases.py     # 发布 API
│       │   └── download.py     # 下载 API
│       └── templates/          # 前端模板
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

### 9.1 页面结构

#### 登录页
- 用户名/密码输入
- "记住我"选项
- 登录按钮

#### 发布管理页（Publisher/Admin）
- 发布列表表格
  - 资源类型、版本、状态、发布时间
  - 操作按钮：查看、编辑、删除、发布/归档
- "新建发布"按钮

#### 新建发布页
- 表单字段：
  - 资源类型（下拉选择：BSP/Driver/Examples）
  - 版本号
  - 描述
  - 更新日志
- 文件上传区：
  - 源码文件（zip 或目录）
  - 二进制文件（zip 或目录）
  - 文档文件（zip 或目录）
- 保存草稿 / 立即发布 按钮

#### 发布详情页
- 发布信息展示
- 包列表（带下载链接）
- 权限视图（预览不同权限级别看到的包）

#### 许可证管理页（Admin）
- 许可证列表表格
  - 许可证 ID、组织、访问级别、资源类型、有效期
  - 操作按钮：查看、编辑、撤销
- "新建许可证"按钮

#### 客户下载页
- 发布列表（根据许可证过滤）
- 下载按钮（根据权限显示可下载的包）

### 9.2 UI 框架选择
推荐使用轻量级方案：
- **后端**：Flask + Jinja2 模板
- **前端**：Bootstrap 5 或 Tailwind CSS（通过 CDN 引入）
- **图标**：FontAwesome 或 Heroicons
- **文件上传**：Dropzone.js

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

### Phase 1：核心功能开发（4 周）
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

### Phase 2：Web 服务开发（3 周）
- Week 5：Flask API
  - 实现 REST API 端点
  - 权限中间件
- Week 6：Web UI
  - 实现登录、发布管理页面
  - 实现许可证管理页面
- Week 7：集成测试
  - 端到端测试
  - 性能测试

### Phase 3：文档和部署（2 周）
- Week 8：文档
  - 用户手册
  - API 文档
  - 部署指南
- Week 9：部署和上线
  - 生产环境部署
  - 监控和日志
  - 用户培训

---

## 13. 扩展性考虑

### 13.1 未来可能的功能
1. **多语言支持**：i18n 国际化
2. **通知系统**：发布通知、许可证过期提醒
3. **审计日志**：记录所有发布和下载操作
4. **版本比较**：可视化比较不同版本的差异
5. **自动化测试**：发布前自动运行测试套件
6. **CI/CD 集成**：与 Jenkins/GitLab CI 集成
7. **包签名**：GPG 签名验证
8. **多租户**：支持多个组织独立管理

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
✅ **双发布渠道**（CLI + Web）
✅ **权限分级下载**（FULL_ACCESS, BINARY_ACCESS）

系统采用分层架构，各层职责清晰，易于测试和维护。通过复用 Binary Manager V2 的打包和存储能力，减少了重复开发，提高了开发效率。

---

**文档版本**：v1.0  
**创建日期**：2026-03-01  
**最后更新**：2026-03-01
