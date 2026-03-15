# 数据备份功能 - 完整文档

## 📋 功能概述

数据备份功能为 Release Portal V3 提供完整的数据备份和恢复解决方案，确保数据安全和业务连续性。

### 核心功能

✅ **数据库备份** - 备份 SQLite 数据库
✅ **存储文件备份** - 备份发布的包文件
✅ **压缩存储** - 使用 gzip 压缩减小存储空间
✅ **元数据管理** - 记录备份时间、大小、校验和
✅ **备份列表** - 查看所有备份及其详细信息
✅ **一键恢复** - 快速恢复到任意备份点
✅ **备份下载** - 下载备份文件到本地
✅ **权限控制** - 仅管理员可操作

### 技术特点

- **原子操作** - 备份过程不会影响系统运行
- **增量备份** - 支持选择性备份（仅数据库或包含存储）
- **校验和验证** - SHA256 校验确保数据完整性
- **自动清理** - 临时文件自动清理
- **Web UI** - 直观的备份管理界面
- **REST API** - 完整的 API 接口

## 🏗️ 架构设计

### 组件结构

```
┌─────────────────────────────────────────┐
│           Web UI (backup.html)           │
│  - 备份列表展示                           │
│  - 创建/恢复/删除操作                     │
│  - 备份下载                              │
└─────────────────┬───────────────────────┘
                  │ HTTP/JSON
                  ▼
┌─────────────────────────────────────────┐
│       Backup REST API (backup.py)       │
│  - POST /api/backup/create              │
│  - GET  /api/backup                     │
│  - GET  /api/backup/<filename>          │
│  - POST /api/backup/restore             │
│  - GET  /api/backup/<filename>/download  │
│  - DELETE /api/backup/<filename>        │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│      BackupService (backup_service.py)  │
│  - create_backup()                      │
│  - restore_backup()                     │
│  - list_backups()                       │
│  - delete_backup()                      │
│  - get_backup_info()                    │
└─────────────────────────────────────────┘
```

### 数据流程

#### 创建备份流程

```
用户请求
    │
    ▼
[1] 验证权限（Admin）
    │
    ▼
[2] 创建临时目录
    │
    ▼
[3] 复制数据库文件
    │
    ▼
[4] 复制存储文件（可选）
    │
    ▼
[5] 创建元数据（JSON）
    │
    ▼
[6] 打包为 tar.gz
    │
    ▼
[7] 计算校验和（SHA256）
    │
    ▼
[8] 保存到备份目录
    │
    ▼
[9] 返回备份信息
```

#### 恢复备份流程

```
用户请求
    │
    ▼
[1] 验证权限（Admin）
    │
    ▼
[2] 验证备份文件存在
    │
    ▼
[3] 备份当前数据
    │
    ▼
[4] 解压备份文件
    │
    ▼
[5] 读取元数据
    │
    ▼
[6] 恢复数据库
    │
    ▼
[7] 恢复存储文件（如包含）
    │
    ▼
[8] 验证恢复成功
    │
    ▼
[9] 返回结果
```

## 🔌 API 端点

### 1. 列出所有备份

```http
GET /api/backup
```

**Query Parameters:**
- `db_path` (可选) - 数据库路径，默认 `./data/portal.db`
- `storage_path` (可选) - 存储路径，默认 `./releases`
- `backup_dir` (可选) - 备份目录，默认 `./backups`

**Response:**
```json
{
  "backups": [
    {
      "filename": "backup_20240302_120000.tar.gz",
      "size": 1024000,
      "created_at": "2024-03-02T12:00:00",
      "checksum": "abc123...",
      "metadata": {
        "name": "backup_20240302_120000",
        "created_at": "2024-03-02T12:00:00",
        "database_size": 102400,
        "includes_storage": true
      }
    }
  ],
  "count": 1
}
```

### 2. 创建备份

```http
POST /api/backup/create
```

**Request Body:**
```json
{
  "name": "my_backup",           // 可选
  "include_storage": true,       // 可选，默认 true
  "db_path": "./data/portal.db",
  "storage_path": "./releases",
  "backup_dir": "./backups"
}
```

**Response:**
```json
{
  "backup_id": "backup_20240302_120000",
  "filename": "backup_20240302_120000.tar.gz",
  "path": "./backups/backup_20240302_120000.tar.gz",
  "size": 1024000,
  "checksum": "abc123...",
  "created_at": "2024-03-02T12:00:00",
  "includes_storage": true
}
```

### 3. 获取备份详情

```http
GET /api/backup/<filename>
```

**Response:**
```json
{
  "filename": "backup_20240302_120000.tar.gz",
  "size": 1024000,
  "created_at": "2024-03-02T12:00:00",
  "checksum": "abc123...",
  "metadata": {
    "name": "backup_20240302_120000",
    "database_size": 102400,
    "includes_storage": true
  }
}
```

### 4. 下载备份

```http
GET /api/backup/<filename>/download
```

**Response:** Binary file stream

### 5. 恢复备份

```http
POST /api/backup/restore
```

**Request Body:**
```json
{
  "backup_filename": "backup_20240302_120000.tar.gz",
  "target_db_path": "./data/portal.db",       // 可选
  "target_storage_path": "./releases",        // 可选
  "db_path": "./data/portal.db",
  "storage_path": "./releases",
  "backup_dir": "./backups"
}
```

**Response:**
```json
{
  "success": true,
  "backup_filename": "backup_20240302_120000.tar.gz",
  "restored_at": "2024-03-02T12:30:00",
  "metadata": {...}
}
```

### 6. 删除备份

```http
DELETE /api/backup/<filename>
```

**Response:**
```json
{
  "success": true,
  "message": "Backup deleted successfully"
}
```

## 💻 使用示例

### Python 代码示例

```python
from release_portal.application.backup_service import BackupService

# 初始化备份服务
backup_service = BackupService(
    db_path='./data/portal.db',
    storage_path='./releases',
    backup_dir='./backups'
)

# 创建备份
backup_info = backup_service.create_backup(
    name='production_backup',
    include_storage=True
)
print(f"备份创建成功: {backup_info['filename']}")

# 列出备份
backups = backup_service.list_backups()
for backup in backups:
    print(f"{backup['filename']} - {backup['size']} bytes")

# 恢复备份
restore_info = backup_service.restore_backup(
    backup_filename='backup_20240302_120000.tar.gz'
)
print(f"备份恢复成功: {restore_info['restored_at']}")

# 删除备份
success = backup_service.delete_backup('backup_20240302_120000.tar.gz')
print(f"删除{'成功' if success else '失败'}")
```

### cURL 示例

```bash
# 创建备份
curl -X POST http://localhost:5000/api/backup/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_backup",
    "include_storage": true
  }'

# 列出备份
curl -X GET http://localhost:5000/api/backup \
  -H "Authorization: Bearer <token>"

# 下载备份
curl -X GET http://localhost:5000/api/backup/backup_20240302_120000.tar.gz/download \
  -H "Authorization: Bearer <token>" \
  -o backup.tar.gz

# 恢复备份
curl -X POST http://localhost:5000/api/backup/restore \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "backup_filename": "backup_20240302_120000.tar.gz"
  }'

# 删除备份
curl -X DELETE http://localhost:5000/api/backup/backup_20240302_120000.tar.gz \
  -H "Authorization: Bearer <token>"
```

### Web UI 使用

1. **访问备份页面**
   - 登录系统（管理员账户）
   - 点击侧边栏"数据备份"

2. **创建备份**
   - 点击"创建备份"按钮
   - 输入备份名称（可选）
   - 选择是否包含存储文件
   - 点击"创建"

3. **恢复备份**
   - 找到要恢复的备份
   - 点击"恢复"按钮
   - 确认恢复操作

4. **下载备份**
   - 找到要下载的备份
   - 点击"下载"按钮
   - 文件将保存到本地

5. **删除备份**
   - 找到要删除的备份
   - 点击"删除"按钮
   - 确认删除操作

## 📊 备份文件格式

### 目录结构

```
backup_20240302_120000.tar.gz
└── backup_20240302_120000/
    ├── portal.db           # SQLite 数据库文件
    ├── storage/            # 存储文件目录（可选）
    │   ├── pkg1.tar.gz
    │   └── pkg2.tar.gz
    └── metadata.json       # 备份元数据
```

### 元数据格式

```json
{
  "name": "backup_20240302_120000",
  "created_at": "2024-03-02T12:00:00",
  "database_size": 102400,
  "includes_storage": true,
  "storage_size": 10240000,
  "db_path": "./data/portal.db",
  "storage_path": "./releases"
}
```

## 🔒 安全考虑

### 权限控制

- ✅ **仅管理员可操作** - 所有备份 API 需要管理员权限
- ✅ **认证要求** - 所有请求需要有效的 JWT token
- ✅ **操作审计** - 建议添加操作日志记录

### 数据完整性

- ✅ **SHA256 校验和** - 验证备份文件完整性
- ✅ **原子操作** - 备份过程不会损坏原数据
- ✅ **自动备份** - 恢复前自动备份当前数据

### 存储安全

- ✅ **临时文件清理** - 自动清理临时文件
- ✅ **路径验证** - 防止目录遍历攻击
- ✅ **错误处理** - 完善的异常处理机制

## 🚀 性能优化

### 存储优化

- **gzip 压缩** - 减小备份文件大小
- **可选存储** - 选择性备份存储文件
- **增量备份** - 未来可添加增量备份支持

### 操作优化

- **异步备份** - 大文件可考虑异步处理
- **进度显示** - 添加备份进度反馈
- **并行处理** - 数据库和存储可并行备份

## 📝 最佳实践

### 备份策略

1. **定期备份** - 建议每天自动备份
2. **多地存储** - 备份文件应存储在不同位置
3. **备份验证** - 定期测试备份恢复
4. **保留策略** - 保留最近 N 个备份

### 操作建议

1. **恢复前备份** - 恢复前先创建当前备份
2. **测试恢复** - 在测试环境验证备份
3. **监控空间** - 监控备份目录磁盘空间
4. **定期清理** - 删除过期的备份文件

## 🧪 测试

### 测试覆盖

```bash
# 运行备份 API 测试
pytest tests/api/test_backup_api.py -v
```

### 测试用例

- ✅ 创建备份（仅数据库）
- ✅ 创建备份（包含存储）
- ✅ 列出备份
- ✅ 获取备份详情
- ✅ 下载备份
- ✅ 恢复备份
- ✅ 删除备份
- ✅ 权限验证

## 🔧 配置

### 默认配置

```python
# 备份目录
BACKUP_DIR = './backups'

# 数据库路径
DB_PATH = './data/portal.db'

# 存储路径
STORAGE_PATH = './releases'
```

### 环境变量

```bash
# 可通过环境变量配置
export PORTAL_BACKUP_DIR=/var/backups/portal
export PORTAL_DB_PATH=/var/lib/portal/portal.db
export PORTAL_STORAGE_PATH=/var/lib/portal/storage
```

## 📚 相关文档

- [系统架构文档](../doc/design.md)
- [API 文档](../README.md)
- [部署指南](../doc/deployment.md)

## 🐛 故障排查

### 常见问题

**1. 备份失败：权限不足**
```
解决方案：确保应用有读写备份目录的权限
```

**2. 恢复失败：数据库被占用**
```
解决方案：停止应用服务后再恢复
```

**3. 磁盘空间不足**
```
解决方案：清理旧备份文件或增加磁盘空间
```

### 调试模式

```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 未来改进

- [ ] 自动定时备份
- [ ] 增量备份支持
- [ ] 备份加密
- [ ] 云存储集成（S3, OSS）
- [ ] 备份压缩比例优化
- [ ] 备份验证工具
- [ ] 备份导出/导入
- [ ] 备份计划任务

## 📞 支持

如有问题或建议，请：
- 查看文档
- 提交 Issue
- 联系技术支持

---

**版本**: 1.0.0  
**最后更新**: 2024-03-02  
**维护者**: Release Portal Team
