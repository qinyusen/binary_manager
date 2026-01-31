# Binary Manager v2 - 快速开始指南

## 🎯 5分钟快速开始

### 步骤1：安装和初始化

```bash
# 安装依赖
pip3 install boto3 requests jsonschema tqdm

# 初始化数据库
cd binary_manager_v2
python3 -c "
import sys
sys.path.insert(0, '.')
from core.database_manager import DatabaseManager

with DatabaseManager() as db:
    db.init_database()
    print(f'✓ 数据库初始化完成')
    print(f'Publisher ID: {db.publisher_id}')
"
```

### 步骤2：发布包（自动提取Git信息）

```bash
# 确保你的项目在Git仓库中
cd /path/to/your/git/project

# 发布包
python3 binary_manager_v2/core/publisher_v2.py . 1.0.0 my_app
```

自动记录：
- ✅ Git commit哈希
- ✅ 分支名称
- ✅ Tag标签
- ✅ 作者信息
- ✅ 提交时间
- ✅ 主机名
- ✅ 发布者ID

### 步骤3：查看发布记录

```python
from binary_manager_v2.core.database_manager import DatabaseManager

with DatabaseManager() as db:
    packages = db.query_packages()
    
    for pkg in packages:
        print(f"\n{pkg['package_name']} v{pkg['version']}")
        print(f"  Git: {pkg['git_commit_short']}")
        print(f"  Branch: {pkg['git_branch']}")
        print(f"  Tag: {pkg['git_tag']}")
        print(f"  Publisher: {pkg['publisher_id']}")
        print(f"  Created: {pkg['created_at']}")
```

### 步骤4：创建Group（可选）

```python
from binary_manager_v2.group.group_manager import create_group

packages = [
    {
        'package_name': 'backend_api',
        'version': '1.0.0',
        'install_order': 1
    },
    {
        'package_name': 'frontend_web',
        'version': '2.0.0',
        'install_order': 2
    }
]

env_config = {
    'database_url': 'postgresql://localhost:5432/dev',
    'api_port': 8080,
    'debug': True
}

result = create_group(
    group_name='dev_environment',
    version='1.0.0',
    packages=packages,
    environment_config=env_config
)

print(f"✓ Group创建成功，ID: {result['group_id']}")
```

## 📋 常见任务

### 查询特定包

```python
with DatabaseManager() as db:
    packages = db.query_packages({
        'package_name': 'my_app',
        'version': '1.0.0'
    })
    print(packages)
```

### 查询所有版本

```python
with DatabaseManager() as db:
    packages = db.query_packages({'package_name': 'my_app'})
    for pkg in packages:
        print(f"v{pkg['version']} - Git: {pkg['git_commit_short']}")
```

### 按Git commit查询

```python
with DatabaseManager() as db:
    packages = db.query_packages({'git_commit': 'abc123...'})
    for pkg in packages:
        print(f"{pkg['package_name']} v{pkg['version']}")
```

### 列出所有Groups

```bash
python3 binary_manager_v2/group/group_manager.py list
```

### 导出Group JSON

```bash
# 假设Group ID是1
python3 binary_manager_v2/group/group_manager.py export 1 ./groups
```

## 🔧 配置AWS S3（可选）

### 方法1：配置文件

编辑 `binary_manager_v2/config/config.json`：

```json
{
  "s3": {
    "enabled": true,
    "bucket": "your-bucket-name",
    "access_key": "AKIA...",
    "secret_key": "secret...",
    "region": "us-east-1"
  }
}
```

### 方法2：环境变量

```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
export AWS_S3_BUCKET=your-bucket
```

### 方法3：代码中配置

```python
s3_config = {
    'enabled': True,
    'bucket': 'your-bucket',
    'access_key': 'AKIA...',
    'secret_key': 'secret...'
}

from binary_manager_v2.core.publisher_v2 import publish_package

publish_package(
    source_dir='.',
    output_dir='./releases',
    package_name='my_app',
    version='1.0.0',
    upload=True,
    s3_config=s3_config
)
```

## 📊 数据库查询示例

### 统计信息

```python
with DatabaseManager() as db:
    stats = db.get_statistics()
    print(f"Total packages: {stats['total_packages']}")
    print(f"Total groups: {stats['total_groups']}")
    print(f"Total publishers: {stats['total_publishers']}")
    print(f"Total storage: {stats['total_storage_bytes']} bytes")
```

### 查询特定发布者的包

```python
with DatabaseManager() as db:
    packages = db.query_packages({'publisher_id': 'user@hostname'})
    print(f"Published {len(packages)} packages")
```

### 按时间查询

```python
with DatabaseManager() as db:
    # 查询所有包，然后按时间过滤
    all_packages = db.query_packages()
    recent = [p for p in all_packages 
               if p['created_at'] > '2026-01-01']
    print(f"Recent packages: {len(recent)}")
```

## 🐛 故障排除

### 问题：Git集成失败

**原因**：不在Git仓库中或没有commit

**解决**：
```bash
git init
git add .
git commit -m "Initial commit"
```

### 问题：数据库初始化失败

**原因**：权限问题或路径错误

**解决**：
```bash
# 删除旧数据库
rm -f binary_manager_v2/database/binary_manager.db

# 手动初始化
python3 -c "
from binary_manager_v2.core.database_manager import DatabaseManager
DatabaseManager().init_database()
"
```

### 问题：S3上传失败

**原因**：凭证无效或权限不足

**解决**：
```bash
# 检查凭证
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret

# 测试连接
python3 -c "
import boto3
s3 = boto3.client('s3')
print(s3.list_buckets())
"
```

## 🎯 实际使用场景

### 场景1：团队协作发布

```bash
# 开发者A（电脑1）
cd /project/backend
python3 binary_manager_v2/core/publisher_v2.py . 1.0.0 backend

# 开发者B（电脑2）
cd /project/frontend
python3 binary_manager_v2/core/publisher_v2.py . 1.0.0 frontend

# 组建Group
python3 -c "
from binary_manager_v2.group.group_manager import create_group
create_group(
    group_name='full_app',
    version='1.0.0',
    packages=[
        {'package_name': 'backend', 'version': '1.0.0', 'install_order': 1},
        {'package_name': 'frontend', 'version': '1.0.0', 'install_order': 2}
    ]
)
"
```

### 场景2：多版本管理

```bash
# 发布v1.0.0
git tag v1.0.0
python3 binary_manager_v2/core/publisher_v2.py . 1.0.0 my_app

# 更新代码，发布v1.1.0
git tag v1.1.0
python3 binary_manager_v2/core/publisher_v2.py . 1.1.0 my_app

# 查看所有版本
python3 -c "
from binary_manager_v2.core.database_manager import DatabaseManager
db = DatabaseManager()
for p in db.query_packages({'package_name': 'my_app'}):
    print(f\"v{p['version']} - Git: {p['git_commit_short']} - {p['created_at']}\")
"
```

### 场景3：环境配置管理

```python
# 开发环境
dev_config = {
    'database_url': 'postgresql://localhost:5432/dev',
    'redis_url': 'redis://localhost:6379',
    'debug': True,
    'log_level': 'DEBUG'
}

# 测试环境
test_config = {
    'database_url': 'postgresql://test-db:5432/app',
    'redis_url': 'redis://test-redis:6379',
    'debug': False,
    'log_level': 'INFO'
}

# 生产环境
prod_config = {
    'database_url': 'postgresql://prod-db:5432/app',
    'redis_url': 'redis://prod-redis:6379',
    'debug': False,
    'log_level': 'WARNING'
}

create_group('dev_env', '1.0.0', packages, environment_config=dev_config)
create_group('test_env', '1.0.0', packages, environment_config=test_config)
create_group('prod_env', '1.0.0', packages, environment_config=prod_config)
```

## 📚 下一步

1. 阅读 [BINARY_MANAGER_V2.md](BINARY_MANAGER_V2.md) 了解完整功能
2. 阅读 [UPGRADE_DESIGN.md](UPGRADE_DESIGN.md) 了解设计细节
3. 查看 [EXAMPLES.md](EXAMPLES.md) 学习更多示例
4. 探索API文档和代码注释

## 💡 提示

- ✅ 确保在Git仓库中发布包
- ✅ 使用有意义的Tag和版本号
- ✅ 在Group中明确安装顺序
- ✅ 定期同步数据库到S3
- ✅ 使用环境变量管理敏感信息
