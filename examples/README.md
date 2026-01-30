# Binary Manager - 示例项目

本目录包含完整的示例项目，演示如何使用Binary Manager进行项目发布和下载。

## 📁 目录结构

```
examples/
├── simple_app/          # 简单计算器
│   ├── calculator.py    # 计算器主程序
│   └── README.md        # 文档
├── web_app/             # Web应用
│   ├── server.py        # Python HTTP服务器
│   ├── index.html       # 前端页面
│   └── README.md        # 文档
└── cli_tool/            # CLI工具
    ├── file_tool.py     # 文件处理工具
    └── README.md        # 文档
```

## 🚀 快速使用

### 1. 发布所有示例

```bash
bash publish_examples.sh
```

这将发布三个示例项目到 `releases/` 目录。

### 2. 下载所有示例

```bash
bash download_examples.sh
```

这将下载并安装所有示例到 `installed_apps/` 目录。

### 3. 运行示例

**简单计算器：**
```bash
python3 installed_apps/simple_calculator/simple_calculator/calculator.py
```

**Web应用：**
```bash
python3 installed_apps/web_app/web_app_demo/server.py
# 然后在浏览器打开 http://localhost:8000
```

**文件工具：**
```bash
# 查看帮助
python3 installed_apps/file_tool/file_tool/file_tool.py --help

# 统计文件
python3 installed_apps/file_tool/file_tool/file_tool.py . --count

# 列出Python文件
python3 installed_apps/file_tool/file_tool/file_tool.py . --list --pattern "*.py"
```

## 📖 详细教程

查看 [TUTORIAL.md](../TUTORIAL.md) 获取详细的分步教程。

## 🎯 示例说明

### 1. Simple Calculator

**功能：** 基本数学运算（加减乘除）

**特点：**
- 简单易懂的Python类
- 完整的错误处理
- 清晰的输出

**适用场景：** 学习、演示、测试

**发布：**
```bash
python3 binary_manager/publisher/main.py \
  --source examples/simple_app \
  --output releases \
  --version 1.0.0 \
  --name simple_calculator
```

### 2. Web Application

**功能：** Python HTTP服务器 + HTML前端

**特点：**
- 完整的前后端分离
- 响应式设计
- 简单的RESTful接口

**适用场景：** Web开发、API开发

**发布：**
```bash
python3 binary_manager/publisher/main.py \
  --source examples/web_app \
  --output releases \
  --version 1.0.0 \
  --name web_app_demo
```

### 3. File Tool

**功能：** 文件统计和列表操作

**特点：**
- 命令行接口
- 多种输出格式
- 灵活的过滤选项

**适用场景：** 文件管理、开发工具

**发布：**
```bash
python3 binary_manager/publisher/main.py \
  --source examples/cli_tool \
  --output releases \
  --version 1.0.0 \
  --name file_tool
```

## 📊 发布包信息

| 项目 | 版本 | 文件数 | 原始大小 | 压缩大小 |
|------|------|--------|----------|----------|
| Simple Calculator | 1.0.0 | 2 | 838 bytes | 674 bytes |
| Web Application | 1.0.0 | 3 | 2,946 bytes | 1,662 bytes |
| File Tool | 1.0.0 | 2 | 2,934 bytes | 1,298 bytes |

## 🔧 手动操作

如果不想使用自动化脚本，可以手动操作：

### 发布单个示例

```bash
# 发布简单计算器
python3 binary_manager/publisher/main.py \
  --source examples/simple_app \
  --output releases \
  --version 1.0.0 \
  --name simple_calculator

# 发布Web应用
python3 binary_manager/publisher/main.py \
  --source examples/web_app \
  --output releases \
  --version 1.0.0 \
  --name web_app_demo

# 发布文件工具
python3 binary_manager/publisher/main.py \
  --source examples/cli_tool \
  --output releases \
  --version 1.0.0 \
  --name file_tool
```

### 下载单个示例

```bash
# 下载简单计算器
python3 binary_manager/downloader/main.py \
  --config releases/simple_calculator_v1.0.0.json \
  --output installed_apps

# 下载Web应用
python3 binary_manager/downloader/main.py \
  --config releases/web_app_demo_v1.0.0.json \
  --output installed_apps

# 下载文件工具
python3 binary_manager/downloader/main.py \
  --config releases/file_tool_v1.0.0.json \
  --output installed_apps
```

## ✨ 高级用法

### 忽略特定文件

```bash
python3 binary_manager/publisher/main.py \
  --source examples/web_app \
  --output releases \
  --version 1.0.0 \
  --name web_app_demo \
  --ignore "*.pyc" \
  --ignore ".DS_Store"
```

### 指定下载URL

```bash
python3 binary_manager/publisher/main.py \
  --source examples/simple_app \
  --output releases \
  --version 1.0.0 \
  --name simple_calculator \
  --url "http://example.com/packages/simple_calculator_v1.0.0.zip"
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
  --output extracted_app
```

## 🎓 学习路径

1. **初学者**
   - 阅读 Simple Calculator 代码
   - 运行并理解输出
   - 修改代码并重新发布

2. **进阶**
   - 学习 Web Application 的前后端分离
   - 了解 File Tool 的CLI设计
   - 尝试发布自己的项目

3. **高级**
   - 探索高级用法
   - 集成到CI/CD
   - 搭建软件分发系统

## 📚 相关文档

- [TUTORIAL.md](../TUTORIAL.md) - 详细教程
- [EXAMPLES.md](../EXAMPLES.md) - 使用示例
- [QUICKSTART.md](../QUICKSTART.md) - 快速开始
- [README.md](../README.md) - 完整文档

## 🛠️ 故障排除

### 问题：找不到binary_manager模块

**解决方案：**
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 问题：权限错误

**解决方案：**
```bash
chmod +x publish_examples.sh
chmod +x download_examples.sh
```

### 问题：哈希验证失败

**解决方案：**
检查文件是否完整，重新下载：
```bash
bash publish_examples.sh
bash download_examples.sh
```

## 📝 贡献

欢迎贡献新的示例！请遵循以下步骤：

1. 在 `examples/` 下创建新目录
2. 编写清晰、简洁的代码
3. 添加 README.md 说明文档
4. 更新本文档

## 📄 许可

MIT License
