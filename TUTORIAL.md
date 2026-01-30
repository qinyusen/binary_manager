# Binary Manager - 示例教程

本教程提供完整的示例，帮助你理解如何使用Binary Manager进行项目发布和下载。

## 📚 示例项目概览

### 1. Simple Calculator（简单计算器）
- **类型**: Python 应用
- **文件**: 2个
- **大小**: 838 bytes
- **功能**: 基本数学运算（加减乘除）

### 2. Web Application（Web应用）
- **类型**: Web 应用（前后端分离）
- **文件**: 3个
- **大小**: 2,946 bytes
- **功能**: Python HTTP服务器 + HTML前端

### 3. File Tool（文件工具）
- **类型**: CLI工具
- **文件**: 2个
- **大小**: 2,934 bytes
- **功能**: 文件统计和列表操作

---

## 🚀 快速开始

### 方法1：使用自动化脚本

**发布所有示例：**
```bash
bash publish_examples.sh
```

**下载所有示例：**
```bash
bash download_examples.sh
```

### 方法2：手动操作

**发布单个示例：**
```bash
python3 binary_manager/publisher/main.py \
  --source examples/simple_app \
  --output releases \
  --version 1.0.0 \
  --name simple_calculator
```

**下载单个示例：**
```bash
python3 binary_manager/downloader/main.py \
  --config releases/simple_calculator_v1.0.0.json \
  --output installed_apps
```

---

## 📖 详细教程

### 教程1：发布你的第一个项目

#### 步骤1：准备项目
```bash
cd test
ls examples/simple_app/
```

**输出：**
```
calculator.py
README.md
```

#### 步骤2：发布项目
```bash
python3 binary_manager/publisher/main.py \
  --source examples/simple_app \
  --output releases \
  --version 1.0.0 \
  --name simple_calculator
```

**输出：**
```
========================================
Binary Manager - Publisher
========================================
Package: simple_calculator
Version: 1.0.0
Source: examples/simple_app
Output: releases
========================================

Scanning files...
Found 2 files (838 bytes)

Creating package...
Created: simple_calculator_v1.0.0.zip (674 bytes)
Created: releases/simple_calculator_v1.0.0.json

========================================
Package created successfully!
========================================
```

#### 步骤3：查看生成的文件
```bash
ls -lh releases/
```

**输出：**
```
-rw-r--r-- 1 user  staff  608B simple_calculator_v1.0.0.json
-rw-r--r-- 1 user  staff  674B simple_calculator_v1.0.0.zip
```

#### 步骤4：查看JSON配置
```bash
cat releases/simple_calculator_v1.0.0.json
```

**输出：**
```json
{
  "package_name": "simple_calculator",
  "version": "1.0.0",
  "created_at": "2026-01-30T23:21:00.000000Z",
  "file_info": {
    "archive_name": "simple_calculator_v1.0.0.zip",
    "size": 674,
    "file_count": 2,
    "hash": "sha256:dfcf373bc98606439ebec65818b4a9a154997b19a3d20f35e7f81a05cda5e01e"
  },
  "files": [
    {
      "path": "README.md",
      "size": 192,
      "hash": "sha256:..."
    },
    {
      "path": "calculator.py",
      "size": 646,
      "hash": "sha256:..."
    }
  ]
}
```

---

### 教程2：下载和运行项目

#### 步骤1：下载项目
```bash
python3 binary_manager/downloader/main.py \
  --config releases/simple_calculator_v1.0.0.json \
  --output installed_apps
```

**输出：**
```
========================================
Binary Manager - Downloader
========================================
Config: releases/simple_calculator_v1.0.0.json
Output: installed_apps
========================================

Loading config from local path...

Package: simple_calculator
Version: 1.0.0
Files: 2
Size: 674 bytes

Locating package...
Found package in config directory: releases/simple_calculator_v1.0.0.zip

Verifying package...
Package verified successfully!

Extracting package...
Package extracted successfully!

Verifying extracted files...
All files verified successfully!

========================================
Package installation complete!
========================================
Location: installed_apps/simple_calculator/simple_calculator
```

#### 步骤2：查看安装的文件
```bash
ls -la installed_apps/simple_calculator/simple_calculator/
```

**输出：**
```
total 16
drwxr-xr-x  4 user  staff   128 Jan 30 23:21 .
drwxr-xr-x  3 user  staff    96 Jan 30 23:21 ..
-rw-r--r--  1 user  staff  192 Jan 30 23:21 README.md
-rw-r--r--  1 user  staff  646 Jan 30 23:21 calculator.py
```

#### 步骤3：运行应用
```bash
python3 installed_apps/simple_calculator/simple_calculator/calculator.py
```

**输出：**
```
Simple Calculator
5 + 3 = 8
10 - 4 = 6
6 * 7 = 42
15 / 3 = 5.0
```

---

### 教程3：发布Web应用

#### 发布Web应用
```bash
python3 binary_manager/publisher/main.py \
  --source examples/web_app \
  --output releases \
  --version 1.0.0 \
  --name web_app_demo
```

#### 下载并运行Web应用
```bash
# 下载
python3 binary_manager/downloader/main.py \
  --config releases/web_app_demo_v1.0.0.json \
  --output installed_apps

# 启动服务器
python3 installed_apps/web_app/web_app_demo/server.py
```

**输出：**
```
Server running at http://localhost:8000
Press Ctrl+C to stop
```

**在浏览器中打开：** http://localhost:8000

---

### 教程4：使用CLI工具

#### 发布CLI工具
```bash
python3 binary_manager/publisher/main.py \
  --source examples/cli_tool \
  --output releases \
  --version 1.0.0 \
  --name file_tool
```

#### 下载并使用CLI工具
```bash
# 下载
python3 binary_manager/downloader/main.py \
  --config releases/file_tool_v1.0.0.json \
  --output installed_apps

# 查看帮助
python3 installed_apps/file_tool/file_tool/file_tool.py --help

# 统计文件
python3 installed_apps/file_tool/file_tool/file_tool.py . --count

# 列出Python文件
python3 installed_apps/file_tool/file_tool/file_tool.py . --list --pattern "*.py"

# JSON输出
python3 installed_apps/file_tool/file_tool/file_tool.py . --count --json
```

**输出示例：**
```
# --count
Files: 2
Directories: 0
Total: 2

# --list
calculator.py
README.md

# --count --json
{
  "files": 2,
  "directories": 0,
  "total": 2
}
```

---

## 🔧 高级用法

### 忽略特定文件

```bash
python3 binary_manager/publisher/main.py \
  --source my_project \
  --output releases \
  --version 1.0.0 \
  --name my_app \
  --ignore "*.pyc" \
  --ignore "*_test.py" \
  --ignore "*.log" \
  --ignore ".git"
```

### 仅验证配置

```bash
python3 binary_manager/downloader/main.py \
  --config releases/simple_calculator_v1.0.0.json \
  --verify-only
```

### 仅解压zip

```bash
python3 binary_manager/downloader/main.py \
  --extract-only releases/simple_calculator_v1.0.0.zip \
  --output extracted
```

### 指定下载URL

发布时指定URL：
```bash
python3 binary_manager/publisher/main.py \
  --source examples/simple_app \
  --output releases \
  --version 1.0.0 \
  --name simple_calculator \
  --url "http://example.com/packages/simple_calculator_v1.0.0.zip"
```

从URL下载：
```bash
python3 binary_manager/downloader/main.py \
  --config http://example.com/packages/simple_calculator_v1.0.0.json \
  --output installed_apps
```

---

## 📊 示例对比

| 特性 | Simple Calculator | Web Application | File Tool |
|------|------------------|-----------------|-----------|
| 文件数 | 2 | 3 | 2 |
| 大小 | 838 bytes | 2,946 bytes | 2,934 bytes |
| 压缩后 | 674 bytes | 1,662 bytes | 1,298 bytes |
| 复杂度 | 简单 | 中等 | 中等 |
| 适用场景 | 学习、演示 | Web开发 | 文件管理 |

---

## 🎯 实际应用场景

### 场景1：团队内部工具分发

1. 开发者创建工具（如file_tool）
2. 使用发布器打包
3. 将JSON配置和zip包上传到内部服务器
4. 团队成员使用下载器安装

### 场景2：多版本管理

```bash
# 发布版本 1.0.0
python3 binary_manager/publisher/main.py --source my_app --output releases --version 1.0.0 --name my_app

# 更新后发布 1.1.0
python3 binary_manager/publisher/main.py --source my_app --output releases --version 1.1.0 --name my_app

# 发布 2.0.0
python3 binary_manager/publisher/main.py --source my_app --output releases --version 2.0.0 --name my_app
```

### 场景3：自动化部署

结合CI/CD工具：
```bash
# CI脚本中自动发布
python3 binary_manager/publisher/main.py \
  --source $PROJECT_DIR \
  --output $RELEASE_DIR \
  --version $CI_COMMIT_TAG \
  --name $PROJECT_NAME \
  --url $DOWNLOAD_URL
```

---

## 🛠️ 故障排除

### 问题1：找不到模块
```bash
pip install requests jsonschema tqdm
```

### 问题2：权限错误
```bash
chmod +x publish_examples.sh
chmod +x download_examples.sh
```

### 问题3：哈希验证失败
检查下载是否完整，重新下载：
```bash
rm -f releases/simple_calculator_v1.0.0.zip
python3 binary_manager/publisher/main.py --source examples/simple_app --output releases --version 1.0.0 --name simple_calculator
```

---

## 📚 更多资源

- [README.md](README.md) - 完整文档
- [QUICKSTART.md](QUICKSTART.md) - 快速开始
- [EXAMPLES.md](EXAMPLES.md) - 使用示例
- [PROJECT_FILES.md](PROJECT_FILES.md) - 文件说明

---

## ✅ 下一步

1. 运行 `python3 demo.py` 查看交互式演示
2. 尝试发布你自己的项目
3. 探索高级功能和自定义配置
4. 集成到你的开发流程中
