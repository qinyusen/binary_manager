# Binary Manager V2 快速入门

这个指南将帮助你在5分钟内开始使用Binary Manager V2。

## 📦 前置要求

- Python 3.6+
- pip

## 🚀 安装

```bash
# 克隆仓库
git clone https://github.com/qinyusen/binary_manager.git
cd binary_manager

# 安装依赖
pip install -r requirements.txt
```

**依赖大小**: 仅~6MB（比V1减少94%）

---

## 📝 基础使用

### 1️⃣ 发布你的第一个包

```bash
python3 -m binary_manager_v2.cli.main publish \
  --source ./examples/simple_app \
  --package-name simple_calculator \
  --version 1.0.0 \
  --output ./releases
```

**输出**:
- ✅ `simple_calculator_v1.0.0.zip` - 压缩包
- ✅ `simple_calculator_v1.0.0.json` - 配置文件
- ✅ 数据库记录 - 自动保存到SQLite

### 2️⃣ 下载包

```bash
python3 -m binary_manager_v2.cli.main download \
  --config ./releases/simple_calculator_v1.0.0.json \
  --output ./downloads
```

**输出**:
- ✅ 自动验证SHA256哈希
- ✅ 解压到指定目录
- ✅ 完整的文件清单

### 3️⃣ 创建分组

分组允许你将多个包组合在一起，方便批量安装。

```bash
python3 -m binary_manager_v2.cli.main group create \
  --group-name my_environment \
  --version 1.0.0 \
  --packages simple_calculator:1.0.0
```

### 4️⃣ 查看所有包

```bash
python3 -m binary_manager_v2.cli.main list
```

---

## 🔥 进阶功能

### Git集成

如果你的项目在Git仓库中，V2会自动提取Git信息：

```bash
cd your_git_project
python3 -m binary_manager_v2.cli.main publish \
  --source . \
  --package-name my_project \
  --version 1.0.0
```

**自动记录**:
- Git commit哈希
- 分支名称
- Tag标签
- 作者信息
- 提交时间

### 发布到S3

```bash
python3 -m binary_manager_v2.cli.main publish \
  --source ./my_project \
  --package-name my_project \
  --version 1.0.0 \
  --s3-bucket my-bucket \
  --s3-region us-east-1
```

**环境变量**:
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_S3_BUCKET=my-bucket
```

### 下载分组

```bash
# 下载整个分组的所有包
python3 -m binary_manager_v2.cli.main download \
  --group-id 1 \
  --output ./install
```

---

## 📂 常用命令

### 发布命令

```bash
# 完整命令
python3 -m binary_manager_v2.cli.main publish \
  --source ./my_project \
  --package-name my_app \
  --version 1.0.0 \
  --description "My awesome application" \
  --output ./releases \
  --ignore "*.pyc,__pycache__"

# 最简命令
python3 -m binary_manager_v2.cli.main publish \
  -s ./my_project \
  -n my_app \
  -v 1.0.0
```

### 下载命令

```bash
# 通过配置文件
python3 -m binary_manager_v2.cli.main download \
  --config ./releases/my_app_v1.0.0.json \
  --output ./downloads

# 通过包ID
python3 -m binary_manager_v2.cli.main download \
  --package-id 1 \
  --output ./downloads

# 通过名称和版本
python3 -m binary_manager_v2.cli.main download \
  --package-name my_app \
  --version 1.0.0 \
  --output ./downloads

# 下载分组
python3 -m binary_manager_v2.cli.main download \
  --group-id 1 \
  --output ./install
```

### 分组命令

```bash
# 创建分组
python3 -m binary_manager_v2.cli.main group create \
  --group-name dev_environment \
  --version 1.0.0 \
  --packages backend:1.0.0 frontend:2.0.0 \
  --description "Development environment"

# 列出分组
python3 -m binary_manager_v2.cli.main group list

# 导出分组
python3 -m binary_manager_v2.cli.main group export \
  --group-id 1 \
  --output ./groups

# 导入分组
python3 -m binary_manager_v2.cli.main group import \
  --config ./groups/dev_environment_v1.0.0.json

# 删除分组
python3 -m binary_manager_v2.cli.main group delete \
  --group-id 1
```

### 列出命令

```bash
# 列出所有包
python3 -m binary_manager_v2.cli.main list

# 按名称过滤
python3 -m binary_manager_v2.cli.main list --package-name my_app
```

---

## 🏗️ 架构概览

```
binary_manager_v2/
├── domain/           # 领域层（核心逻辑，零依赖）
├── infrastructure/   # 基础设施层（存储、数据库、Git）
├── application/      # 应用层（业务服务）
└── cli/             # CLI工具（用户界面）
```

**洋葱架构**:
- Domain层 ← 零外部依赖，纯Python标准库
- Infrastructure层 ← 实现Domain接口
- Application层 ← 编排业务流程
- CLI ← 用户交互

---

## 🧪 测试

运行测试套件验证安装：

```bash
python3 test_v2_complete.py
```

**测试覆盖**:
- ✅ Domain层 - 实体、值对象、服务
- ✅ Infrastructure层 - 存储、Git、数据库
- ✅ Application层 - 发布、下载、分组
- ✅ CLI - 命令行接口
- ✅ 集成测试

---

## 💡 使用技巧

### 1. 忽略文件

发布时忽略特定文件：

```bash
python3 -m binary_manager_v2.cli.main publish \
  --source ./my_project \
  --package-name my_app \
  --version 1.0.0 \
  --ignore "*.pyc,__pycache__,.git,node_modules"
```

### 2. 不提取Git信息

如果不需要Git信息：

```bash
python3 -m binary_manager_v2.cli.main publish \
  --source ./my_project \
  --package-name my_app \
  --version 1.0.0 \
  --no-git
```

### 3. 添加元数据

```bash
python3 -m binary_manager_v2.cli.main publish \
  --source ./my_project \
  --package-name my_app \
  --version 1.0.0 \
  --description "My application" \
  --metadata '{"author":"John Doe","license":"MIT"}'
```

---

## 📖 配置文件示例

### package.json（生成）

```json
{
  "package_name": "my_app",
  "version": "1.0.0",
  "created_at": "2026-02-26T15:00:00Z",
  "file_info": {
    "archive_name": "my_app_v1.0.0.zip",
    "size": 1024000,
    "file_count": 10,
    "hash": "sha256:abc123..."
  },
  "files": [
    {
      "path": "src/main.py",
      "size": 1024,
      "hash": "sha256:def456..."
    }
  ],
  "git_info": {
    "commit_hash": "abc123...",
    "commit_short": "abc123",
    "branch": "main",
    "author": "John Doe"
  }
}
```

---

## ❓ 常见问题

### Q: 如何查看已发布的包？

```bash
python3 -m binary_manager_v2.cli.main list
```

### Q: 如何删除包？

```bash
# 使用SQLite直接删除
sqlite3 binary_manager_v2/database/binary_manager.db
DELETE FROM packages WHERE id = 1;
```

### Q: 如何更新包？

发布新版本即可：

```bash
python3 -m binary_manager_v2.cli.main publish \
  --source ./my_project \
  --package-name my_app \
  --version 1.1.0
```

### Q: 数据库在哪里？

`binary_manager_v2/database/binary_manager.db`

---

## 📚 下一步

- 阅读完整文档：[BINARY_MANAGER_V2.md](BINARY_MANAGER_V2.md)
- 了解架构设计：[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
- 查看API文档：[README.md](README.md)

---

## 🤝 获取帮助

```bash
# 查看所有命令
python3 -m binary_manager_v2.cli.main --help

# 查看特定命令帮助
python3 -m binary_manager_v2.cli.main publish --help
python3 -m binary_manager_v2.cli.main download --help
python3 -m binary_manager_v2.cli.main group --help
```

---

**GitHub**: https://github.com/qinyusen/binary_manager
