# 地瓜机器人发布平台 V3 - 使用手册

## 目录

1. [系统概述](#系统概述)
2. [安装和初始化](#安装和初始化)
3. [用户管理](#用户管理)
4. [发布管理](#发布管理)
5. [下载管理](#下载管理)
6. [许可证管理](#许可证管理)
7. [完整工作流示例](#完整工作流示例)
8. [常见问题](#常见问题)
9. [API 参考](#api-参考)

---

## 系统概述

地瓜机器人发布平台 V3 是一个软件发布管理系统，支持：

- **三种资源类型**：BSP、驱动程序（DRIVER）、示例程序（EXAMPLES）
- **三种内容类型**：源代码（SOURCE）、二进制（BINARY）、文档（DOCUMENT）
- **基于许可证的权限控制**：
  - `FULL_ACCESS`：可下载源码、二进制和文档
  - `BINARY_ACCESS`：只能下载二进制和文档
- **两种使用方式**：命令行（CLI）和 Web 界面（开发中）

---

## 安装和初始化

### 1. 安装依赖

```bash
# 安装 Binary Manager V2 依赖
pip install -r binary_manager_v2/requirements.txt

# 安装 Release Portal 依赖
pip install release_portal/requirements_v3.txt
```

### 2. 初始化数据库

```bash
# 使用默认路径初始化
release-portal init

# 指定数据库路径
release-portal init --db ./data/my_portal.db
```

初始化后会创建三个默认角色：

- **Admin**：管理员，拥有所有权限
- **Publisher**：发布者，可以发布和下载资源
- **Customer**：客户，只能根据许可证下载资源

---

## 用户管理

### 用户注册

只有管理员可以注册新用户。

```bash
# 注册管理员用户
release-portal register admin admin123 admin@example.com --role Admin

# 注册发布者用户
release-portal register engineer engineer123 engineer@example.com --role Publisher

# 注册客户用户
release-portal register customer customer123 customer@example.com --role Customer
```

### 用户登录

```bash
release-portal login admin
# 输入密码：admin123

release-portal login engineer
# 输入密码：engineer123
```

登录成功后，Token 会保存在 `~/.release-portal/config.json`。

### 查看当前用户

```bash
release-portal whoami
```

输出示例：
```
User ID: user_admin123
Username: admin
Email: admin@example.com
Role: Admin
```

### 用户登出

```bash
release-portal logout
```

---

## 发布管理

### 创建发布草稿

```bash
release-portal publish create \
  --type BSP \
  --version 1.0.0 \
  --description "地瓜机器人 BSP v1.0.0" \
  --changelog "初始版本发布"
```

输出示例：
```
✓ 发布草稿创建成功
Release ID: rel_abc123
Resource Type: BSP
Version: 1.0.0
Status: DRAFT
```

### 添加包到发布

支持三种内容类型：SOURCE（源码）、BINARY（二进制）、DOCUMENT（文档）。

#### 添加二进制包

```bash
release-portal publish add-package rel_abc123 \
  --content-type BINARY \
  --source /path/to/binary/build
```

#### 添加源码包

```bash
release-portal publish add-package rel_abc123 \
  --content-type SOURCE \
  --source /path/to/source/code \
  --extract-git
```

#### 添加文档包

```bash
release-portal publish add-package rel_abc123 \
  --content-type DOCUMENT \
  --source /path/to/documentation
```

### 发布版本

```bash
release-portal publish publish rel_abc123
```

注意：发布前必须至少添加一个二进制包。

### 归档版本

```bash
release-portal publish archive rel_abc123
```

### 查看发布列表

```bash
# 查看所有发布
release-portal list

# 按资源类型筛选
release-portal list --type BSP

# 按状态筛选
release-portal list --status PUBLISHED
```

输出示例：
```
Available Releases:
Release ID          Resource Type    Version       Status       Published At
rel_abc123          BSP              1.0.0         PUBLISHED    2024-01-15 10:30:00
rel_def456          DRIVER           2.0.0         DRAFT        -
```

---

## 下载管理

### 查看可下载的包

```bash
release-portal download list rel_abc123
```

输出示例：
```
Available packages for release rel_abc123:
  - BINARY: bsp-diggo-1-0-0-binary v1.0.0 (1024000 bytes)
  - DOCUMENT: bsp-diggo-1-0-0-document v1.0.0 (51200 bytes)

Note: SOURCE package is not available with your license level.
```

### 下载包

#### 下载所有可用的包

```bash
release-portal download download rel_abc123
```

默认下载到 `./downloads/<release_id>/`。

#### 下载特定类型的包

```bash
# 下载二进制包
release-portal download download rel_abc123 --content-type BINARY

# 下载文档包
release-portal download download rel_abc123 --content-type DOCUMENT

# 下载源码包（需要 FULL_ACCESS 许可证）
release-portal download download rel_abc123 --content-type SOURCE
```

#### 指定输出目录

```bash
release-portal download download rel_abc123 \
  --content-type BINARY \
  --output /path/to/output
```

---

## 许可证管理

### 创建许可证

```bash
# 创建完全访问许可证
release-portal license create \
  --organization "客户A公司" \
  --level FULL_ACCESS \
  --types BSP,DRIVER,EXAMPLES \
  --days 365

# 创建二进制访问许可证
release-portal license create \
  --organization "客户B公司" \
  --level BINARY_ACCESS \
  --types BSP \
  --days 180
```

输出示例：
```
✓ 许可证创建成功
License ID: lic_xyz789
Organization: 客户A公司
Access Level: FULL_ACCESS
Resource Types: BSP, DRIVER, EXAMPLES
Expires At: 2025-01-15 00:00:00
```

### 查看许可证列表

```bash
release-portal license list
```

输出示例：
```
Licenses:
License ID: lic_xyz789
Organization: 客户A公司
Access Level: FULL_ACCESS
Resource Types: BSP, DRIVER, EXAMPLES
Expires At: 2025-01-15 00:00:00
Status: Active

License ID: lic_def123
Organization: 客户B公司
Access Level: BINARY_ACCESS
Resource Types: BSP
Expires At: 2024-07-15 00:00:00
Status: Active
```

### 延期许可证

```bash
# 延期 30 天
release-portal license extend lic_xyz789 --days 30

# 延期到指定日期
release-portal license extend lic_xyz789 --date 2025-12-31
```

### 吊销许可证

```bash
release-portal license revoke lic_xyz789
```

### 激活许可证

```bash
release-portal license activate lic_xyz789
```

### 为用户分配许可证

目前需要通过数据库直接分配，未来会提供 CLI 命令。

```python
from release_portal.initializer import create_container

container = create_container()
container.auth_service.assign_license_to_user('user_id', 'license_id')
```

---

## 完整工作流示例

### 场景 1：发布 BSP 新版本

```bash
# 1. 登录为发布者
release-portal login engineer

# 2. 创建发布草稿
release-portal publish create \
  --type BSP \
  --version 2.0.0 \
  --description "地瓜机器人 BSP v2.0.0" \
  --changelog "- 新增 UART 驱动支持
- 优化 GPIO 性能
- 修复已知问题"

# 3. 添加源码包
release-portal publish add-package rel_new_bsp \
  --content-type SOURCE \
  --source /path/to/bsp/source \
  --extract-git

# 4. 添加二进制包
release-portal publish add-package rel_new_bsp \
  --content-type BINARY \
  --source /path/to/bsp/build

# 5. 添加文档包
release-portal publish add-package rel_new_bsp \
  --content-type DOCUMENT \
  --source /path/to/bsp/docs

# 6. 发布版本
release-portal publish publish rel_new_bsp
```

### 场景 2：客户下载资源

```bash
# 1. 登录为客户
release-portal login customer

# 2. 查看可下载的发布
release-portal list --status PUBLISHED

# 3. 查看特定发布的可用包
release-portal download list rel_new_bsp

# 4. 下载二进制包和文档（BINARY_ACCESS 许可证）
release-portal download download rel_new_bsp

# 或下载特定类型
release-portal download download rel_new_bsp --content-type BINARY
```

### 场景 3：许可证管理

```bash
# 1. 登录为管理员
release-portal login admin

# 2. 为新客户创建许可证
release-portal license create \
  --organization "新客户公司" \
  --level FULL_ACCESS \
  --types BSP,DRIVER \
  --days 365

# 3. 查看许可证状态
release-portal license list

# 4. 续期许可证
release-portal license extend lic_new_license --days 90

# 5. （如需要）吊销许可证
release-portal license revoke lic_old_license
```

---

## 常见问题

### Q1: 如何重置用户密码？

目前需要通过数据库直接操作，未来会提供 CLI 命令。

```python
from release_portal.initializer import create_container

container = create_container()
user = container.auth_service.get_user_from_token(token)
# 需要实现密码重置功能
```

### Q2: 如何删除发布？

目前不支持删除，但可以归档。

```bash
release-portal publish archive rel_old_release
```

### Q3: 许可证过期后如何处理？

许可证过期后，用户将无法下载任何资源。管理员可以：

1. 延期许可证：`release-portal license extend <license_id> --days 30`
2. 创建新许可证并分配给用户

### Q4: 如何查看用户权限？

```bash
release-portal whoami
```

这将显示用户的角色，角色决定了用户的权限。

### Q5: Token 过期怎么办？

Token 有效期为 24 小时。过期后需要重新登录：

```bash
release-portal logout
release-portal login <username>
```

### Q6: 如何备份和恢复数据库？

```bash
# 备份数据库
cp data/portal.db data/portal_backup_$(date +%Y%m%d).db

# 恢复数据库
cp data/portal_backup_20240115.db data/portal.db
```

---

## API 参考

### CLI 命令参考

#### 初始化命令

```bash
release-portal init [--db DB_PATH]
```

- `--db`：指定数据库路径（可选，默认为 `./data/portal.db`）

#### 用户管理命令

```bash
# 登录
release-portal login USERNAME

# 登出
release-portal logout

# 查看当前用户
release-portal whoami

# 注册新用户（需要管理员权限）
release-portal register USERNAME EMAIL PASSWORD --role ROLE
```

- `ROLE`：Admin、Publisher、Customer

#### 发布管理命令

```bash
# 创建发布草稿
release-portal publish create \
  --type {BSP,DRIVER,EXAMPLES} \
  --version VERSION \
  [--description DESCRIPTION] \
  [--changelog CHANGELOG]

# 添加包
release-portal publish add-package RELEASE_ID \
  --content-type {SOURCE,BINARY,DOCUMENT} \
  --source SOURCE_DIR \
  [--extract-git] \
  [--no-extract-git]

# 发布版本
release-portal publish publish RELEASE_ID

# 归档版本
release-portal publish archive RELEASE_ID
```

#### 查询命令

```bash
# 列出发布
release-portal list [--type {BSP,DRIVER,EXAMPLES}] [--status {DRAFT,PUBLISHED,ARCHIVED}]

# 列出可下载的包
release-portal download list RELEASE_ID
```

#### 下载命令

```bash
# 下载包
release-portal download download RELEASE_ID \
  [--content-type {SOURCE,BINARY,DOCUMENT}] \
  [--output OUTPUT_DIR]
```

#### 许可证管理命令

```bash
# 创建许可证
release-portal license create \
  --organization ORGANIZATION \
  --level {FULL_ACCESS,BINARY_ACCESS} \
  --types TYPE1,TYPE2,TYPE3 \
  [--days DAYS] \
  [--date YYYY-MM-DD]

# 列出许可证
release-portal license list

# 延期许可证
release-portal license extend LICENSE_ID \
  [--days DAYS] \
  [--date YYYY-MM-DD]

# 吊销许可证
release-portal license revoke LICENSE_ID

# 激活许可证
release-portal license activate LICENSE_ID
```

### Python API 参考

#### 创建服务容器

```python
from release_portal.initializer import create_container

container = create_container("./data/portal.db")
```

#### 用户认证

```python
# 注册用户
user = container.auth_service.register(
    username="john",
    email="john@example.com",
    password="password123",
    role_id="role_customer"
)

# 登录
token = container.auth_service.login("john", "password123")

# 从 Token 获取用户
user = container.auth_service.get_user_from_token(token)
```

#### 发布管理

```python
from release_portal.domain.value_objects import ResourceType, ContentType

# 创建发布草稿
release = container.release_service.create_draft(
    resource_type=ResourceType.BSP,
    version="1.0.0",
    publisher_id=user.user_id,
    description="BSP v1.0.0",
    changelog="Initial release"
)

# 添加包
package_id = container.release_service.add_package(
    release_id=release.release_id,
    content_type=ContentType.BINARY,
    source_dir="/path/to/source",
    extract_git=False,
    user_id=user.user_id
)

# 发布版本
release = container.release_service.publish_release(
    release_id=release.release_id,
    user_id=user.user_id
)
```

#### 下载管理

```python
# 获取可下载的包
packages = container.download_service.get_available_packages(
    user_id=user.user_id,
    release_id="rel_abc123"
)

# 下载包
container.download_service.download_package(
    user_id=user.user_id,
    release_id="rel_abc123",
    content_type="BINARY",
    output_dir="/path/to/output"
)
```

#### 许可证管理

```python
from release_portal.domain.value_objects import AccessLevel, ResourceType
from datetime import datetime, timedelta

# 创建许可证
license = container.license_service.create_license(
    organization="客户公司",
    access_level=AccessLevel.FULL_ACCESS,
    allowed_resource_types=[ResourceType.BSP, ResourceType.DRIVER],
    expires_at=datetime.now() + timedelta(days=365)
)

# 为用户分配许可证
container.auth_service.assign_license_to_user(
    user_id=user.user_id,
    license_id=license.license_id
)

# 延期许可证
license = container.license_service.extend_license(
    license_id=license.license_id,
    days=30
)
```

---

## 系统架构

### 洋葱架构

系统采用四层洋葱架构：

```
┌─────────────────────────────────────────┐
│      Presentation Layer (CLI/Web)       │
├─────────────────────────────────────────┤
│       Application Layer (Services)      │
├─────────────────────────────────────────┤
│         Domain Layer (Entities)         │
├─────────────────────────────────────────┤
│      Infrastructure Layer (Database)    │
└─────────────────────────────────────────┘
```

### 依赖关系

- **Domain Layer**：无外部依赖，只使用 Python 标准库
- **Application Layer**：依赖 Domain Layer
- **Infrastructure Layer**：依赖 Domain Layer
- **Presentation Layer**：依赖 Application Layer

### 账号系统与存储系统解耦

系统通过接口层实现了账号系统和存储系统的解耦：

- **IAuthorizationService**：授权服务接口
- **IStorageService**：存储服务接口

这样设计的好处：
1. 账号系统可以独立运行
2. 存储系统可以独立运行
3. 可以轻松替换实现
4. 易于测试和维护

详细设计请参考 `DECOUPLING_DESIGN.md`。

---

## 配置文件

### Token 存储位置

Token 保存在用户主目录：

```
~/.release-portal/config.json
```

格式：
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "username": "john"
}
```

### 数据库配置

默认数据库路径：`./data/portal.db`

可以通过环境变量或命令行参数修改：

```bash
export RELEASE_PORTAL_DB_PATH=/custom/path/portal.db
release-portal init --db /custom/path/portal.db
```

---

## 故障排除

### 问题 1：Token 无效

**错误信息**：`Error: Invalid or expired token. Please login again.`

**解决方案**：
```bash
release-portal logout
release-portal login <username>
```

### 问题 2：权限不足

**错误信息**：`ValueError: User does not have permission to publish BSP`

**解决方案**：
- 确认用户角色是否正确
- 确认角色是否具有相应权限
- 联系管理员分配正确的角色

### 问题 3：许可证过期

**错误信息**：`ValueError: License is inactive or expired`

**解决方案**：
- 联系管理员延期许可证
- 或请求分配新的许可证

### 问题 4：包名无效

**错误信息**：`InvalidPackageNameError: Invalid package name: xxx`

**解决方案**：
- 包名只能包含字母、数字、下划线和连字符
- 版本号中的点号会自动转换为连字符

### 问题 5：数据库锁定

**错误信息**：`sqlite3.OperationalError: database is locked`

**解决方案**：
- 确保只有一个进程在访问数据库
- 关闭所有数据库连接后重试

---

## 附录

### 默认角色权限

| 角色 | 发布权限 | 下载权限 | 用户管理 | 许可证管理 |
|------|---------|---------|---------|-----------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Publisher | ✓ | ✓ | ✗ | ✗ |
| Customer | ✗ | * | ✗ | ✗ |

*Customer 的下载权限取决于其许可证

### 许可证级别说明

| 级别 | 源码 | 二进制 | 文档 |
|------|-----|-------|-----|
| FULL_ACCESS | ✓ | ✓ | ✓ |
| BINARY_ACCESS | ✗ | ✓ | ✓ |

### 资源类型说明

- **BSP**：板级支持包（Board Support Package）
- **DRIVER**：驱动程序
- **EXAMPLES**：示例程序

### 内容类型说明

- **SOURCE**：源代码包（.tar.gz 格式）
- **BINARY**：二进制包（.tar.gz 格式）
- **DOCUMENT**：文档包（.tar.gz 格式）

---

## 联系方式

如有问题或建议，请联系：

- 项目负责人：[TODO: 添加联系方式]
- 技术支持：[TODO: 添加联系方式]
- 问题反馈：[TODO: 添加 GitHub Issues 链接]

---

**文档版本**：1.0  
**最后更新**：2024-01-15  
**适用系统版本**：Release Portal V3
