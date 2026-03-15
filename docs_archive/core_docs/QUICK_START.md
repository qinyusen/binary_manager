# 地瓜机器人发布平台 V3 - 快速入门

## 5 分钟快速上手

### 1. 安装和初始化

```bash
# 安装依赖
pip install -r release_portal/requirements_v3.txt

# 初始化数据库
release-portal init
```

### 2. 创建测试用户

```bash
# 创建发布者
release-portal register publisher publisher@example.com pub123 --role Publisher

# 创建客户
release-portal register customer customer@example.com cust123 --role Customer
```

### 3. 登录

```bash
release-portal login publisher
```

### 4. 发布资源

```bash
# 创建发布草稿
release-portal publish create --type BSP --version 1.0.0

# 添加包（假设你有源代码目录）
release-portal publish add-package rel_xxx --content-type BINARY --source /path/to/source

# 发布版本
release-portal publish publish rel_xxx
```

### 5. 下载资源

```bash
# 登录为客户
release-portal logout
release-portal login customer

# 查看可下载的包
release-portal download list rel_xxx

# 下载包
release-portal download download rel_xxx
```

## 常用命令

### 用户管理

```bash
# 登录
release-portal login <username>

# 登出
release-portal logout

# 查看当前用户
release-portal whoami

# 注册新用户（需要管理员权限）
release-portal register <username> <email> <password> --role <Admin|Publisher|Customer>
```

### 发布管理

```bash
# 创建发布草稿
release-portal publish create --type <BSP|DRIVER|EXAMPLES> --version <version>

# 添加包
release-portal publish add-package <release_id> --content-type <SOURCE|BINARY|DOCUMENT> --source <path>

# 发布版本
release-portal publish publish <release_id>

# 查看发布列表
release-portal list
```

### 下载管理

```bash
# 查看可下载的包
release-portal download list <release_id>

# 下载包
release-portal download download <release_id> [--content-type <SOURCE|BINARY|DOCUMENT>]
```

### 许可证管理

```bash
# 创建许可证
release-portal license create --organization <name> --level <FULL_ACCESS|BINARY_ACCESS> --types <BSP,DRIVER,EXAMPLES> --days <days>

# 查看许可证列表
release-portal license list

# 延期许可证
release-portal license extend <license_id> --days <days>
```

## 快速示例脚本

运行快速入门示例：

```bash
python examples/quick_start.py
```

这将创建测试数据库、用户、许可证和发布，让你快速了解系统功能。

## 完整文档

- **使用手册**：`USER_MANUAL.md`
- **架构设计**：`DECOUPLING_DESIGN.md`
- **设计文档**：`doc/design.md`

## 系统架构

系统采用洋葱架构，分为四层：

```
┌─────────────────────────────────────────┐
│      Presentation Layer (CLI/Web)       │  ← 用户界面
├─────────────────────────────────────────┤
│       Application Layer (Services)      │  ← 业务逻辑
├─────────────────────────────────────────┤
│         Domain Layer (Entities)         │  ← 核心模型
├─────────────────────────────────────────┤
│      Infrastructure Layer (Database)    │  ← 数据持久化
└─────────────────────────────────────────┘
```

### 核心概念

#### 三种资源类型
- **BSP**：板级支持包
- **DRIVER**：驱动程序
- **EXAMPLES**：示例程序

#### 三种内容类型
- **SOURCE**：源代码
- **BINARY**：二进制文件
- **DOCUMENT**：文档

#### 两种许可证级别
- **FULL_ACCESS**：可下载源码、二进制和文档
- **BINARY_ACCESS**：只能下载二进制和文档

#### 三种用户角色
- **Admin**：管理员，拥有所有权限
- **Publisher**：发布者，可以发布和下载
- **Customer**：客户，根据许可证下载

## 下一步

1. 阅读 `USER_MANUAL.md` 了解详细使用方法
2. 阅读 `DECOUPLING_DESIGN.md` 了解系统架构
3. 运行 `examples/demo_portal.py` 查看完整示例
4. 开始使用 CLI 工具管理你的发布

## 常见问题

### Q: 如何查看用户权限？
A: 使用 `release-portal whoami` 查看当前用户的角色。

### Q: Token 过期怎么办？
A: 重新登录：`release-portal login <username>`

### Q: 如何备份数据库？
A: 复制 `data/portal.db` 文件即可。

### Q: 如何重置密码？
A: 目前需要通过数据库操作，或创建新用户。

## 联系方式

如有问题，请查看文档或提交 Issue。
