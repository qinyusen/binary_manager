# Binary Manager - 快速开始指南

## 系统要求

- Python 3.6 或更高版本
- Ubuntu（使用install_dependencies.sh）或其他操作系统

## 快速安装

### Ubuntu系统

```bash
sudo ./install_dependencies.sh
```

### 其他系统

```bash
pip install -r requirements.txt
```

## 快速开始

### 1. 测试功能

运行自动化测试脚本：

```bash
python3 test.py
```

测试脚本会自动：
- 清理旧的测试文件
- 测试发布器功能
- 测试下载器功能
- 验证文件完整性

### 2. 发布你的第一个包

```bash
python3 binary_manager/publisher/main.py \
  --source ./binary_manager/examples/my_app \
  --output ./my_releases \
  --version 1.0.0 \
  --name my_first_package
```

这将生成：
- `my_releases/my_first_package_v1.0.0.zip` - 打包的文件
- `my_releases/my_first_package_v1.0.0.json` - JSON配置文件

### 3. 安装包

```bash
python3 binary_manager/downloader/main.py \
  --config ./my_releases/my_first_package_v1.0.0.json \
  --output ./installed_packages
```

这将会：
- 读取JSON配置
- 验证zip文件哈希
- 解压文件到指定目录
- 验证每个文件的哈希

## 工作流程

```
你的项目 → 发布器 → zip + JSON配置 → 下载器 → 安装后的项目
```

## 常见用法

### 忽略某些文件

```bash
python3 binary_manager/publisher/main.py \
  --source ./my_project \
  --ignore '*.log' \
  --ignore '.git' \
  --ignore 'node_modules'
```

### 仅验证配置

```bash
python3 binary_manager/downloader/main.py \
  --config ./package.json \
  --verify-only
```

### 仅解压现有zip

```bash
python3 binary_manager/downloader/main.py \
  --extract-only ./my_package.zip \
  --output ./extracted
```

## 生成的JSON配置

```json
{
  "package_name": "my_app",
  "version": "1.0.0",
  "created_at": "2026-01-30T10:00:00Z",
  "file_info": {
    "archive_name": "my_app_v1.0.0.zip",
    "size": 947,
    "file_count": 4,
    "hash": "sha256:ab458da3b12ac36bbbc8c0d42c1dbd70a173c9e1a27af45c243e9cd3c04fd965"
  },
  "files": [
    {
      "path": "README.md",
      "size": 209,
      "hash": "sha256:38ca6447075919224d3a6a40f7657bc950851c2edcc9d4c7b734f6c05495ef0a"
    }
  ]
}
```

## 故障排除

### 权限错误

```bash
chmod +x install_dependencies.sh
chmod +x test.py
chmod +x binary_manager/publisher/main.py
chmod +x binary_manager/downloader/main.py
```

### 依赖安装失败

```bash
pip3 install --upgrade pip
pip3 install requests jsonschema tqdm
```

### Python版本不兼容

确保使用Python 3.6+：

```bash
python3 --version
```

## 下一步

- 阅读完整的 [README.md](README.md) 了解详细文档
- 查看 `binary_manager/examples/my_app/` 了解示例项目结构
- 根据需要修改 `binary_manager/publisher/scanner.py` 中的忽略模式

## 获取帮助

```bash
# 发布器帮助
python3 binary_manager/publisher/main.py --help

# 下载器帮助
python3 binary_manager/downloader/main.py --help
```
