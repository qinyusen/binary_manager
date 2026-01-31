# Binary Manager v2.0 - 升级设计文档

## 📋 升级概述

### 新增核心功能

1. **多用户多设备支持**
   - 支持多台电脑发布
   - 统一的数据库管理
   - 云端同步

2. **Git集成**
   - 自动提取Git commit信息
   - 记录分支、Tag、作者和时间
   - 二进制与Git commit映射

3. **数据库系统**
   - SQLite本地数据库
   - AWS S3云端备份
   - 自动同步机制

4. **Group概念**
   - 组合多个包为一个Group
   - 版本依赖管理
   - 环境配置支持

---

## 🗄️ 数据库设计

### 表结构

#### 1. packages 表
```sql
CREATE TABLE packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT NOT NULL,
    version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    publisher_id TEXT NOT NULL,
    publisher_hostname TEXT NOT NULL,
    
    -- Git信息
    git_commit_hash TEXT NOT NULL,
    git_branch TEXT,
    git_tag TEXT,
    git_author TEXT,
    git_commit_time TEXT,
    
    -- 文件信息
    archive_name TEXT NOT NULL,
    archive_size INTEGER NOT NULL,
    archive_hash TEXT NOT NULL,
    file_count INTEGER NOT NULL,
    
    -- 存储信息
    storage_type TEXT NOT NULL,  -- 'local' or 's3'
    storage_path TEXT NOT NULL,
    
    -- 元数据
    description TEXT,
    metadata TEXT,  -- JSON格式
    
    UNIQUE(package_name, version, git_commit_hash)
);
```

#### 2. groups 表
```sql
CREATE TABLE groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL UNIQUE,
    version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    description TEXT,
    environment_config TEXT,  -- JSON格式
    metadata TEXT  -- JSON格式
);
```

#### 3. group_packages 表
```sql
CREATE TABLE group_packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    package_id INTEGER NOT NULL,
    install_order INTEGER DEFAULT 0,
    required INTEGER DEFAULT 1,  -- 是否必需
    
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (package_id) REFERENCES packages(id),
    UNIQUE(group_id, package_id)
);
```

#### 4. dependencies 表
```sql
CREATE TABLE dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    depends_on_group_id INTEGER,
    depends_on_package_id INTEGER,
    constraint_type TEXT NOT NULL,  -- 'exact', 'minimum', 'range'
    version_constraint TEXT,
    
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (depends_on_group_id) REFERENCES groups(id),
    FOREIGN KEY (depends_on_package_id) REFERENCES packages(id)
);
```

#### 5. cache_status 表
```sql
CREATE TABLE cache_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    last_synced_at TEXT NOT NULL,
    last_sync_status TEXT NOT NULL,  -- 'success', 'failed', 'pending'
    record_count INTEGER NOT NULL,
    checksum TEXT NOT NULL
);
```

#### 6. publishers 表
```sql
CREATE TABLE publishers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    publisher_id TEXT NOT NULL UNIQUE,
    hostname TEXT NOT NULL,
    first_seen_at TEXT NOT NULL,
    last_active_at TEXT,
    metadata TEXT  -- JSON格式
);
```

---

## 📁 新的目录结构

```
binary_manager_v2/
├── core/                        # 核心模块
│   ├── __init__.py
│   ├── git_integration.py      # Git集成
│   ├── database_manager.py     # 数据库管理
│   ├── sync_manager.py         # 云端同步（S3）
│   └── publisher_v2.py        # 升级版发布器
├── group/                       # Group管理
│   ├── __init__.py
│   ├── group_manager.py        # Group管理器
│   ├── group_builder.py        # Group构建器
│   └── group_downloader.py     # Group下载器
├── downloader_v2/              # 升级版下载器
│   ├── __init__.py
│   ├── downloader.py
│   ├── verifier.py
│   ├── dependency_resolver.py  # 依赖解析
│   └── main.py
├── config/                      # 配置
│   ├── config.json             # 主配置文件
│   ├── schema_v2.json          # JSON Schema v2
│   └── database_schema.sql     # 数据库结构
├── database/                    # 数据库文件
│   └── binary_manager.db        # SQLite数据库
├── cache/                       # 本地缓存
│   ├── packages/               # 包缓存
│   └── groups/                 # Group缓存
├── examples_v2/                 # 升级版示例
│   └── ...
└── scripts/                     # 辅助脚本
    ├── init_db.sh              # 初始化数据库
    ├── sync_to_s3.sh           # 同步到S3
    └── create_group.sh         # 创建Group
```

---

## 🔧 核心功能设计

### 1. Git集成 (git_integration.py)

```python
class GitIntegration:
    def get_git_info(self, repo_path: str) -> Dict:
        """
        获取Git仓库信息
        
        返回：
        {
            'commit_hash': 'abc123...',
            'branch': 'main',
            'tag': 'v1.0.0',
            'author': 'John Doe',
            'commit_time': '2026-01-30T10:00:00Z',
            'short_hash': 'abc123',
            'is_dirty': False
        }
        """
        pass
    
    def get_changed_files(self, repo_path: str, commit: str) -> List[str]:
        """
        获取指定commit修改的文件
        """
        pass
```

### 2. 数据库管理 (database_manager.py)

```python
class DatabaseManager:
    def __init__(self, db_path: str, s3_config: Dict = None):
        pass
    
    def register_publisher(self, publisher_id: str, hostname: str) -> int:
        """注册发布者"""
        pass
    
    def save_package(self, package_info: Dict, git_info: Dict) -> int:
        """保存包信息"""
        pass
    
    def create_group(self, group_info: Dict) -> int:
        """创建Group"""
        pass
    
    def add_package_to_group(self, group_id: int, package_id: int, 
                            install_order: int = 0) -> None:
        """添加包到Group"""
        pass
    
    def query_packages(self, filters: Dict) -> List[Dict]:
        """查询包"""
        pass
    
    def query_groups(self, filters: Dict) -> List[Dict]:
        """查询Group"""
        pass
    
    def sync_to_s3(self) -> bool:
        """同步到S3"""
        pass
    
    def sync_from_s3(self) -> bool:
        """从S3同步"""
        pass
```

### 3. Group管理 (group_manager.py)

```python
class GroupManager:
    def create_group(self, name: str, version: str, 
                    packages: List[Dict]) -> str:
        """
        创建Group
        
        packages: [
            {
                'package_name': 'my_app',
                'version': '1.0.0',
                'git_commit': 'abc123',
                'install_order': 1
            },
            ...
        ]
        """
        pass
    
    def export_group(self, group_id: int) -> Dict:
        """
        导出Group为JSON
        
        {
            'group_name': 'dev_environment',
            'version': '1.0.0',
            'packages': [...],
            'dependencies': [...],
            'environment_config': {...}
        }
        """
        pass
    
    def import_group(self, group_json: Dict) -> int:
        """从JSON导入Group"""
        pass
    
    def resolve_dependencies(self, group_id: int) -> List[Dict]:
        """解析依赖关系"""
        pass
```

---

## 📦 新的JSON格式

### Package JSON v2

```json
{
  "package_name": "my_app",
  "version": "1.0.0",
  "created_at": "2026-01-30T10:00:00Z",
  
  "publisher": {
    "publisher_id": "user@desktop-001",
    "hostname": "desktop-001.local"
  },
  
  "git_info": {
    "commit_hash": "abc123def456...",
    "branch": "main",
    "tag": "v1.0.0",
    "author": "John Doe <john@example.com>",
    "commit_time": "2026-01-30T09:00:00Z",
    "short_hash": "abc123"
  },
  
  "file_info": {
    "archive_name": "my_app_v1.0.0.zip",
    "size": 947,
    "file_count": 4,
    "hash": "sha256:..."
  },
  
  "files": [...],
  
  "storage": {
    "type": "s3",
    "bucket": "my-bucket",
    "path": "packages/my_app_v1.0.0.zip"
  }
}
```

### Group JSON

```json
{
  "group_name": "dev_environment",
  "version": "1.0.0",
  "created_at": "2026-01-30T10:00:00Z",
  "created_by": "user@desktop-001",
  "description": "开发环境完整配置",
  
  "packages": [
    {
      "package_name": "backend_api",
      "version": "1.0.0",
      "git_commit": "abc123...",
      "install_order": 1,
      "required": true
    },
    {
      "package_name": "frontend_web",
      "version": "2.1.0",
      "git_commit": "def456...",
      "install_order": 2,
      "required": true
    },
    {
      "package_name": "utils_lib",
      "version": "1.5.0",
      "git_commit": "ghi789...",
      "install_order": 0,
      "required": true
    }
  ],
  
  "dependencies": [
    {
      "package": "frontend_web",
      "depends_on": "backend_api",
      "type": "minimum",
      "version": ">=1.0.0"
    }
  ],
  
  "environment_config": {
    "database_url": "postgresql://localhost:5432/dev",
    "redis_url": "redis://localhost:6379",
    "api_port": 8080,
    "debug_mode": true
  },
  
  "install_order": ["utils_lib", "backend_api", "frontend_web"]
}
```

---

## 🔄 工作流程

### 发布流程（升级版）

```
1. 扫描目录
2. 提取Git信息（commit、分支、tag、作者）
3. 生成UUID作为publisher_id
4. 获取主机名
5. 注册发布者
6. 打包zip
7. 计算哈希
8. 保存到数据库（包含Git信息）
9. 上传到S3（可选）
10. 同步数据库到S3
11. 生成JSON配置（v2格式）
```

### Group创建流程

```
1. 选择要包含的包
2. 定义安装顺序
3. 配置环境变量
4. 定义依赖关系
5. 创建Group记录
6. 生成Group JSON
7. 导出为可下载的文件
```

### 下载Group流程

```
1. 下载Group JSON
2. 解析Group配置
3. 解析依赖关系
4. 按顺序下载包
5. 验证每个包的Git信息
6. 应用环境配置
7. 验证完整性
```

---

## 🚀 使用示例

### 1. 发布包（带Git信息）

```bash
python3 binary_manager_v2/core/publisher_v2.py \
  --source ./my_app \
  --output ./releases \
  --version 1.0.0 \
  --name my_app
```

自动提取Git信息并保存到数据库。

### 2. 创建Group

```bash
python3 binary_manager_v2/group/create_group.py \
  --name dev_environment \
  --version 1.0.0 \
  --packages backend_api,frontend_web,utils_lib \
  --env config/dev_env.json
```

### 3. 下载Group

```bash
python3 binary_manager_v2/downloader_v2/main.py \
  --group-json dev_environment_v1.0.0.json \
  --output ./installed
```

自动解析依赖并按顺序安装所有包。

---

## 📊 数据同步策略

### 本地数据库
- SQLite文件存储
- 快速查询和更新
- 支持离线操作

### S3备份
- 定期上传数据库快照
- 存储JSON配置文件
- 存储包文件

### 同步策略
- **自动同步**: 发布/下载后自动同步
- **定时同步**: 每小时自动同步
- **手动同步**: 使用命令手动触发

---

## 🔐 安全性

1. **Git信息验证**
   - 验证commit哈希完整性
   - 验证分支和tag的有效性

2. **数据库加密**
   - SQLite文件可加密
   - S3使用IAM权限

3. **访问控制**
   - 发布者认证
   - Group访问权限

---

## 📝 实施计划

### 阶段1：数据库和Git集成（核心）
1. 创建数据库结构
2. 实现Git集成模块
3. 实现数据库管理器
4. 升级发布器支持Git

### 阶段2：Group功能（核心）
1. 实现Group管理器
2. 实现Group构建器
3. 设计Group JSON格式
4. 实现依赖解析

### 阶段3：云端同步（核心）
1. 实现S3同步管理
2. 实现缓存管理
3. 实现自动同步策略

### 阶段4：下载器升级
1. 升级下载器支持Group
2. 实现依赖解析
3. 实现环境配置应用

### 阶段5：测试和文档
1. 创建测试用例
2. 编写用户文档
3. 创建示例项目
