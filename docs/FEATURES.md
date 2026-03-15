# Release Portal V3 功能文档

## 概述

Release Portal V3 是地瓜机器人软件发布管理平台，支持 BSP、驱动和示例程序的发布与基于许可证的权限控制。

## 核心功能

### 1. 包管理

支持三种资源类型：
- **BSP** - 板级支持包
- **DRIVER** - 驱动程序
- **EXAMPLES** - 示例程序

### 2. 用户权限管理

| 角色 | 发布 | 下载 | 用户管理 | 许可证管理 |
|------|-----|------|---------|-----------|
| Admin | ✓ | ✓ | ✓ | ✓ |
| Publisher | ✓ | ✓ | ✗ | ✗ |
| Customer | ✗ | * | ✗ | ✗ |

*Customer 的下载权限取决于其许可证

### 3. 许可证级别

| 级别 | 源码 | 二进制 | 文档 |
|------|-----|-------|-----|
| FULL_ACCESS | ✓ | ✓ | ✓ |
| BINARY_ACCESS | ✗ | ✓ | ✓ |

---

## 冷备份存储后端

### 支持的存储类型

Release Portal 支持四种冷备份存储后端：

| 存储类型 | 描述 | 适用场景 |
|---------|------|---------|
| `local` | 本地文件系统 | 开发测试、小规模部署 |
| `s3` | AWS S3/Glacier | 云端大规模存储 |
| `sftp` | SFTP 服务器 | SSH 访问的云端服务器 |
| `ftp` | FTP/FTPS 服务器 | 传统 FTP 服务器 |

### 使用方式

#### 本地存储 (local)

```python
from release_portal.application.cold_backup import ColdBackupManager

manager = ColdBackupManager()
manager.initialize(
    backup_dir="/data/backups",
    storage_type="local",
    storage_config={
        "path": "/data/cold_backups"
    }
)
```

#### S3 存储 (s3)

```python
manager.initialize(
    backup_dir="/tmp/backups",
    storage_type="s3",
    storage_config={
        "bucket": "my-backup-bucket",
        "access_key": "AKIAIOSFODNN7EXAMPLE",
        "secret_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "region": "us-east-1",
        "storage_class": "GLACIER"  # STANDARD | GLACIER | DEEP_ARCHIVE
    }
)
```

#### SFTP 存储 (sftp)

```python
manager.initialize(
    backup_dir="/tmp/backups",
    storage_type="sftp",
    storage_config={
        "host": "sftp.example.com",
        "port": 22,
        "username": "backup_user",
        "password": "your_password",      # 与 key_path 二选一
        # "key_path": "/path/to/key",     # 私钥认证
        "remote_path": "/backups/cold",
        "timeout": 30
    }
)
```

**SFTP 配置参数**：

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| host | string | ✓ | - | SFTP 服务器地址 |
| port | int | - | 22 | SFTP 端口 |
| username | string | ✓ | - | 用户名 |
| password | string | - | - | 密码认证 |
| key_path | string | - | - | 私钥路径（与密码二选一） |
| remote_path | string | - | /cold_backups | 远程存储路径 |
| timeout | int | - | 30 | 连接超时（秒） |

#### FTP 存储 (ftp)

```python
manager.initialize(
    backup_dir="/tmp/backups",
    storage_type="ftp",
    storage_config={
        "host": "ftp.example.com",
        "port": 21,
        "username": "backup_user",
        "password": "your_password",
        "use_tls": True,           # 使用 FTPS
        "passive_mode": True,      # 被动模式
        "remote_path": "/backups/cold",
        "timeout": 30
    }
)
```

**FTP 配置参数**：

| 参数 | 类型 | 必需 | 默认值 | 描述 |
|------|------|------|--------|------|
| host | string | ✓ | - | FTP 服务器地址 |
| port | int | - | 21 | FTP 端口 |
| username | string | - | anonymous | 用户名 |
| password | string | - | "" | 密码 |
| use_tls | bool | - | True | 是否使用 FTPS |
| passive_mode | bool | - | True | 被动模式 |
| remote_path | string | - | /cold_backups | 远程存储路径 |
| timeout | int | - | 30 | 连接超时（秒） |

---

## REST API

### API 文档访问

启动服务后访问：
- **Swagger UI**: `http://localhost:5000/api/docs`
- **OpenAPI JSON**: `http://localhost:5000/api/openapi.json`

### 主要端点

| 模块 | 端点前缀 | 描述 |
|------|---------|------|
| 认证 | `/api/auth` | 登录、注册、Token 验证 |
| 发布管理 | `/api/releases` | 创建、发布、归档版本 |
| 下载管理 | `/api/downloads` | 获取包列表、下载文件 |
| 许可证管理 | `/api/licenses` | 创建、激活、撤销许可证 |
| 备份管理 | `/api/backup` | 数据库备份与恢复 |
| 冷备份管理 | `/api/cold-backup` | 长期归档存储 |
| 审计日志 | `/api/audit` | 操作日志查询 |

### 认证方式

大多数 API 需要 JWT Token 认证：

```bash
# 登录获取 Token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}'

# 使用 Token 访问 API
curl http://localhost:5000/api/releases \
  -H "Authorization: Bearer <your_jwt_token>"
```

---

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t release-portal .

# 运行容器
docker run -d \
  -p 5000:5000 \
  -v /data/storage:/app/storage \
  -v /data/db:/app/data \
  -e RELEASE_PORTAL_SECRET=your-secret-key \
  release-portal
```

### Docker Compose 部署

```bash
docker-compose up -d
```

### 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| RELEASE_PORTAL_DB | ./data/portal.db | 数据库路径 |
| RELEASE_PORTAL_STORAGE | ./storage | 存储目录 |
| RELEASE_PORTAL_SECRET | default-secret-key | JWT 密钥 |

---

## 依赖

### 核心依赖

```
Flask==3.0.0
Werkzeug==3.0.1
Flask-CORS==4.0.0
PyYAML==6.0.1
paramiko==3.3.1
```

### 可选依赖

- `boto3` - S3 存储后端
- `schedule` - 定时备份调度

---

## 更新日志

### v3.1.0

- 新增 SFTP 冷备份存储后端
- 新增 FTP/FTPS 冷备份存储后端
- 新增 OpenAPI 文档 (Swagger UI)
- 修复 4 处裸异常捕获问题
- ReleaseService 代码精简 71%
- DownloadService 代码精简 53%
