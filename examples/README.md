# Examples

本目录包含使用 Binary Manager V2 的示例应用程序。

## 示例应用程序

### 1. simple_app
一个简单的计算器应用程序，演示基本的发布和下载功能。

**功能**：
- 基本数学运算（加、减、乘、除）
- 命令行界面
- 配置文件支持

**运行**：
```bash
cd examples/simple_app
python3 main.py add 10 5
python3 main.py sub 10 5
python3 main.py mul 10 5
python3 main.py div 10 5
```

**发布**：
```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./examples/simple_app \
    --package-name simple_app \
    --version 1.0.0
```

**下载**：
```bash
python3 -m binary_manager_v2.cli.main download \
    --package-name simple_app \
    --version 1.0.0 \
    --output ./installed_apps
```

### 2. web_app
一个简单的Web服务器，演示如何发布和运行Web应用程序。

**功能**：
- HTTP服务器
- 静态文件服务
- RESTful API端点
- 健康检查

**运行**：
```bash
cd examples/web_app
python3 server.py
# 访问 http://localhost:8080
```

**发布**：
```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./examples/web_app \
    --package-name web_app \
    --version 1.0.0
```

**下载**：
```bash
python3 -m binary_manager_v2.cli.main download \
    --package-name web_app \
    --version 1.0.0 \
    --output ./installed_apps
```

### 3. cli_tool
一个功能丰富的命令行工具，展示如何构建复杂的CLI应用程序。

**功能**：
- 文件操作（统计、查找重复、批量重命名）
- 文本处理（统计、搜索替换、JSON格式化）
- 系统操作（系统信息、磁盘使用、进程列表）

**运行**：
```bash
cd examples/cli_tool
python3 cli.py --help
python3 cli.py file stats cli.py
python3 cli.py text count cli.py
python3 cli.py sys info
```

**发布**：
```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./examples/cli_tool \
    --package-name cli_tool \
    --version 1.0.0
```

**下载**：
```bash
python3 -m binary_manager_v2.cli.main download \
    --package-name cli_tool \
    --version 1.0.0 \
    --output ./installed_apps
```

## 使用示例脚本

项目根目录下的 `examples_usage.py` 提供了如何使用 Binary Manager V2 API 的完整示例：

```bash
python3 examples_usage.py
```

该脚本演示了：
- 如何发布应用程序
- 如何列出所有包
- 如何下载包
- 如何创建包组
- 如何搜索包

## 快速开始

1. **发布示例应用**：
```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./examples/simple_app \
    --package-name simple_app \
    --version 1.0.0
```

2. **列出已发布的包**：
```bash
python3 -m binary_manager_v2.cli.main list
```

3. **下载并运行应用**：
```bash
python3 -m binary_manager_v2.cli.main download \
    --package-name simple_app \
    --version 1.0.0 \
    --output ./installed_apps

cd installed_apps/simple_app_v1.0.0
python3 main.py add 10 5
```

## 包组管理

创建包含多个应用的包组：

```bash
python3 -m binary_manager_v2.cli.main group create \
    --group-name dev_environment \
    --version 1.0.0 \
    --packages simple_app:1.0.0,web_app:1.0.0
```

导出包组配置：

```bash
python3 -m binary_manager_v2.cli.main group export \
    --group-name dev_environment \
    --version 1.0.0 \
    --output ./exports
```

导入包组配置：

```bash
python3 -m binary_manager_v2.cli.main group import \
    --input ./exports/dev_environment_v1.0.0.json
```

## 开发自己的应用

要创建自己的应用并使用 Binary Manager 发布：

1. 创建应用目录结构：
```
my_app/
├── main.py           # 主程序
├── config.json       # 配置文件
└── README.md         # 文档
```

2. 发布应用：
```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./my_app \
    --package-name my_app \
    --version 1.0.0 \
    --description "My Application"
```

3. 分发给其他用户：
```bash
# 其他用户下载你的应用
python3 -m binary_manager_v2.cli.main download \
    --package-name my_app \
    --version 1.0.0 \
    --output ./installed_apps
```

## 版本管理

Binary Manager 支持完整的版本管理：

```bash
# 发布新版本
python3 -m binary_manager_v2.cli.main publish \
    --source ./examples/simple_app \
    --package-name simple_app \
    --version 1.1.0

# 列出所有版本
python3 -m binary_manager_v2.cli.main list --package-name simple_app

# 下载特定版本
python3 -m binary_manager_v2.cli.main download \
    --package-name simple_app \
    --version 1.0.0 \
    --output ./installed_apps
```

## Git集成

如果你的应用在Git仓库中，Binary Manager会自动提取Git信息：

- Commit hash
- Branch name
- Tag
- Author信息
- Commit message
- Remote repositories

这些信息会保存在包的元数据中，方便追踪。

## 故障排除

### 问题：发布失败
- 检查源目录是否存在
- 确保有写入权限
- 查看日志输出

### 问题：下载失败
- 确认包已发布
- 检查版本号是否正确
- 验证存储路径是否可访问

### 问题：运行下载的应用失败
- 检查依赖是否安装
- 验证文件完整性
- 查看应用的README文档

## 更多信息

- [Binary Manager V2 文档](../BINARY_MANAGER_V2.md)
- [快速开始指南](../V2_QUICKSTART.md)
- [完整测试套件](../test_v2_complete.py)
