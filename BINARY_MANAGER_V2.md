# Binary Manager v2 - 升级版

Binary Manager v2 是原有系统的重大升级，支持多用户、Git集成、数据库同步和Group概念。

## 🚀 新功能

### 1. 多用户多设备支持
- ✅ 每台设备自动生成唯一Publisher ID
- ✅ 记录主机名和活跃时间
- ✅ 统一的数据库管理所有发布

### 2. Git集成
- ✅ 自动提取Git commit哈希
- ✅ 记录分支名称、Tag标签
- ✅ 记录作者信息和提交时间
- ✅ 二进制与Git commit精确映射

### 3. 数据库系统
- ✅ SQLite本地数据库
- ✅ AWS S3云端备份
- ✅ 自动同步机制
- ✅ 完整的发布历史记录

### 4. Group概念
- ✅ 组合多个包为一个Group
- ✅ 版本依赖管理
- ✅ 环境配置支持
- ✅ 按顺序安装

## 📁 目录结构

```
binary_manager_v2/
├── core/                       # 核心模块
│   ├── git_integration.py      # Git集成工具
│   ├── database_manager.py     # 数据库管理器
│   ├── sync_manager.py         # S3同步管理
│   └── publisher_v2.py        # 升级版发布器
├── group/                      # Group管理
│   ├── __init__.py
│   └── group_manager.py        # Group管理器
├── downloader_v2/             # 下载器（待实现）
├── config/                     # 配置文件
│   ├── config.json            # 主配置
│   └── database_schema.sql     # 数据库结构
├── database/                   # 数据库文件
│   └── binary_manager.db      # SQLite数据库
├── cache/                      # 本地缓存
│   ├── packages/               # 包缓存
│   └── groups/                 # Group缓存
├── requirements_v2.txt          # 依赖列表
└── scripts/                    # 辅助脚本
    └── init_v2.sh            # 初始化脚本
```

## 🔧 快速开始

### 1. 初始化

```bash
# 运行初始化脚本
bash init_v2.sh
```

这将：
- 安装Python依赖
- 初始化SQLite数据库
- 生成Publisher ID

### 2. 配置

编辑 `binary_manager_v2/config/config.json`：

```json
{
  "database": {
    "path": "./database/binary_manager.db"
  },
  "s3": {
    "enabled": false,
    "bucket": "your-bucket-name",
    "access_key": "",
    "secret_key": "",
    "region": "us-east-1"
  }
}
```

### 3. 发布包（带Git信息）

```bash
cd binary_manager_v2
python3 core/publisher_v2.py /path/to/your/project 1.0.0 my_app
```

自动提取：
- Git commit哈希
- 分支名称
- Tag标签
- 作者信息
- 提交时间

### 4. 创建Group

```python
from binary_manager_v2.group.group_manager import create_group

packages = [
    {
        'package_name': 'backend_api',
        'version': '1.0.0',
        'install_order': 1,
        'required': True
    },
    {
        'package_name': 'frontend_web',
        'version': '2.0.0',
        'install_order': 2,
        'required': True
    }
]

env_config = {
    'database_url': 'postgresql://localhost:5432/dev',
    'api_port': 8080
}

result = create_group(
    group_name='dev_environment',
    version='1.0.0',
    packages=packages,
    environment_config=env_config
)

print(f"Group ID: {result['group_id']}")
```

## 📊 数据库结构

### 主要表

- **publishers** - 发布者信息
- **packages** - 包信息（含Git信息）
- **groups** - Group信息
- **group_packages** - Group和包的关联
- **dependencies** - 依赖关系
- **cache_status** - 缓存状态
- **sync_history** - 同步历史

## 🔐 安全特性

### Git信息验证
- 验证commit哈希完整性
- 验证分支和tag有效性
- 检测未提交的更改

### 数据完整性
- SHA256哈希校验
- 数据库校验和
- 文件完整性验证

### 访问控制
- 发布者ID认证
- Group访问权限（待实现）

## 📦 使用示例

### 示例1：发布Python项目

```bash
# 假设在Git仓库目录中
cd /path/to/my_git_project
python3 binary_manager_v2/core/publisher_v2.py . 1.0.0 my_project
```

自动记录：
- 当前commit: abc123...
- 分支: main
- Tag: v1.0.0（如果有）
- 作者: John Doe

### 示例2：查询包信息

```python
from binary_manager_v2.core.database_manager import DatabaseManager

with DatabaseManager() as db:
    # 查询特定包
    packages = db.query_packages({
        'package_name': 'my_app',
        'version': '1.0.0'
    })
    
    for pkg in packages:
        print(f"Package: {pkg['package_name']} v{pkg['version']}")
        print(f"Git Commit: {pkg['git_commit_short']}")
        print(f"Publisher: {pkg['publisher_id']}")
        print(f"Created: {pkg['created_at']}")
```

### 示例3：列出所有Groups

```bash
python3 binary_manager_v2/group/group_manager.py list
```

### 示例4：导出Group JSON

```bash
# 导出Group ID 1
python3 binary_manager_v2/group/group_manager.py export 1 ./groups
```

## 🔗 与v1对比

| 功能 | v1 | v2 |
|------|----|----|
| 基本发布/下载 | ✅ | ✅ |
| Git集成 | ❌ | ✅ |
| 数据库支持 | ❌ | ✅ |
| 多用户支持 | ❌ | ✅ |
| Group概念 | ❌ | ✅ |
| 依赖管理 | ❌ | ✅ |
| 环境配置 | ❌ | ✅ |
| 云端同步 | ❌ | ✅ |
| 发布历史 | ❌ | ✅ |

## 🚧 待完成功能

- [ ] 下载器v2实现
- [ ] Group下载功能
- [ ] 依赖解析和验证
- [ ] Web UI
- [ ] 权限管理
- [ ] API接口

## 📝 依赖

```bash
pip install -r binary_manager_v2/requirements_v2.txt
```

- boto3>=1.26.0 - AWS S3
- requests>=2.31.0 - HTTP下载
- jsonschema>=4.20.0 - JSON验证
- tqdm>=4.66.0 - 进度显示

## 🔧 配置说明

### Git配置

```json
{
  "git": {
    "enabled": true,
    "require_clean_repo": false
  }
}
```

- `enabled`: 是否启用Git集成
- `require_clean_repo`: 是否要求干净的Git仓库

### S3配置

```json
{
  "s3": {
    "enabled": true,
    "bucket": "your-bucket",
    "access_key": "AKIA...",
    "secret_key": "secret...",
    "region": "us-east-1"
  }
}
```

或使用环境变量：
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `AWS_S3_BUCKET`

## 📖 API文档

### DatabaseManager

```python
class DatabaseManager:
    def save_package(self, package_info: Dict, git_info: Dict) -> Optional[int]:
        """保存包信息"""
    
    def create_group(self, group_info: Dict) -> Optional[int]:
        """创建Group"""
    
    def query_packages(self, filters: Dict = None) -> List[Dict]:
        """查询包"""
    
    def query_groups(self, filters: Dict = None) -> List[Dict]:
        """查询Group"""
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
```

### GroupManager

```python
class GroupManager:
    def create_group(self, group_name: str, version: str, 
                    packages: List[Dict], ...) -> Dict:
        """创建Group"""
    
    def export_group(self, group_id: int, output_dir: str) -> str:
        """导出Group为JSON"""
    
    def import_group(self, group_json_path: str) -> int:
        """从JSON导入Group"""
```

## 🎯 使用场景

### 场景1：开发团队协作

1. 开发者在各自的电脑上发布代码
2. 系统自动记录Git commit信息
3. 创建包含所有组件的Group
4. 团队成员下载Group一次性安装

### 场景2：多环境配置

```python
# 创建开发环境Group
dev_group = create_group(
    group_name='dev_environment',
    version='1.0.0',
    packages=[...],
    environment_config={
        'database_url': 'postgresql://localhost:5432/dev',
        'debug': True
    }
)

# 创建生产环境Group
prod_group = create_group(
    group_name='prod_environment',
    version='1.0.0',
    packages=[...],
    environment_config={
        'database_url': 'postgresql://prod-db:5432/app',
        'debug': False
    }
)
```

### 场景3：版本回滚

```python
with DatabaseManager() as db:
    # 查询特定包的所有版本
    packages = db.query_packages({'package_name': 'my_app'})
    
    for pkg in packages:
        print(f"Version: {pkg['version']}, Git: {pkg['git_commit_short']}")
```

## 🐛 故障排除

### Git集成失败

```bash
# 确保在Git仓库中
git status

# 确保有commit
git log --oneline
```

### 数据库错误

```bash
# 重新初始化数据库
rm binary_manager_v2/database/binary_manager.db
python3 -c "from binary_manager_v2.core.database_manager import DatabaseManager; DatabaseManager().init_database()"
```

### S3上传失败

```bash
# 检查AWS凭证
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# 测试连接
python3 -c "import boto3; print(boto3.client('s3').list_buckets())"
```

## 📚 更多文档

- [UPGRADE_DESIGN.md](../UPGRADE_DESIGN.md) - 详细设计文档
- [EXAMPLES.md](../EXAMPLES.md) - 使用示例
- [README.md](../README.md) - v1版本文档

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

---

## ✅ 升级总结

Binary Manager v2已实现：

- ✅ Git集成（commit、分支、tag、作者）
- ✅ SQLite数据库（完整结构）
- ✅ AWS S3同步（上传/下载）
- ✅ Group管理（创建、导出）
- ✅ 发布器v2（带Git信息）
- ✅ 配置系统
- ✅ 初始化脚本

下一步：
- 下载器v2实现
- Group下载功能
- 依赖解析
