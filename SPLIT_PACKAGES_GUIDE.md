# 分包发布指南

## 概述

Binary Manager V2 **完全支持**将一个项目的不同部分（二进制、头文件、文档等）分开发布，同时保持版本号关联，并支持独立下载。这是嵌入式项目常见的发布模式。

## 使用场景

在嵌入式项目中，通常需要将软件包分成多个部分：

- **二进制文件（Binaries）**: 编译好的库和可执行文件
- **头文件（Headers）**: 开发所需的头文件和接口定义
- **文档（Documentation）**: API手册、用户指南、示例代码等

这些部分通常：
- 有相同的版本号
- 需要独立发布（更新其中一个不影响其他）
- 需要独立下载（用户按需获取）
- 需要保持版本一致性

## 解决方案

Binary Manager V2 提供了两种主要方案来支持这种需求：

### 方案1: 使用不同的 package_name（推荐）

这是最清晰和推荐的方式。

#### 发布示例

```python
# 发布二进制包
publisher.publish(
    source_dir="./my_project-bin",
    package_name="my_project-bin",
    version="1.0.0",
    description="My Project v1.0.0 - Binaries"
)

# 发布头文件包
publisher.publish(
    source_dir="./my_project-headers",
    package_name="my_project-headers",
    version="1.0.0",
    description="My Project v1.0.0 - Headers"
)

# 发布文档包
publisher.publish(
    source_dir="./my_project-docs",
    package_name="my_project-docs",
    version="1.0.0",
    description="My Project v1.0.0 - Documentation"
)
```

#### 命名规范

推荐使用以下命名规范：
- `{project_name}-bin` 或 `{project_name}-binaries`
- `{project_name}-headers` 或 `{project_name}-dev`
- `{project_name}-docs` 或 `{project_name}-documentation`

#### 下载示例

```python
# 只下载二进制（生产环境）
downloader.download_by_name_version(
    package_name="my_project-bin",
    version="1.0.0",
    output_dir="./production/binaries"
)

# 下载二进制+头文件（开发环境）
downloader.download_by_name_version(
    package_name="my_project-bin",
    version="1.0.0",
    output_dir="./dev/bin"
)
downloader.download_by_name_version(
    package_name="my_project-headers",
    version="1.0.0",
    output_dir="./dev/include"
)
```

#### 优势

- ✅ 清晰明确：通过包名就能知道内容
- ✅ 易于管理：每个包独立管理
- ✅ 灵活下载：可以按需下载特定部分
- ✅ 版本独立：可以单独升级某个部分

### 方案2: 使用元数据标记

使用相同的 package_name，通过 metadata 区分。

#### 发布示例

```python
# 发布二进制包
publisher.publish(
    source_dir="./my_project",
    package_name="my_project",
    version="1.0.0",
    metadata={"type": "binary", "component": "runtime"}
)

# 发布头文件包
publisher.publish(
    source_dir="./my_project",
    package_name="my_project",
    version="1.0.0",
    metadata={"type": "headers", "component": "development"}
)
```

**注意**: 这个方案需要修改数据库schema以支持相同的package_name+version组合，当前版本推荐使用方案1。

## 使用 Group 管理版本匹配

Group 是管理多个相关包的最佳方式。

### 创建不同环境组合

```python
# 完整开发环境（包含所有部分）
group_service.create_group(
    group_name="my_project_full",
    version="1.0.0",
    packages=[
        {"package_name": "my_project-bin", "version": "1.0.0"},
        {"package_name": "my_project-headers", "version": "1.0.0"},
        {"package_name": "my_project-docs", "version": "1.0.0"}
    ]
)

# 运行时环境（仅二进制）
group_service.create_group(
    group_name="my_project_runtime",
    version="1.0.0",
    packages=[
        {"package_name": "my_project-bin", "version": "1.0.0"}
    ]
)

# 开发环境（二进制+头文件）
group_service.create_group(
    group_name="my_project_dev",
    version="1.0.0",
    packages=[
        {"package_name": "my_project-bin", "version": "1.0.0"},
        {"package_name": "my_project-headers", "version": "1.0.0"}
    ]
)
```

### 下载整个组

```python
# 下载完整开发环境
downloader.download_group(
    group_id=1,
    output_dir="./full_installation"
)

# 下载运行时环境
downloader.download_group(
    group_id=2,
    output_dir="./production"
)
```

### 导出/导入组配置

```python
# 导出组配置
group_service.export_group(
    group_id=1,
    output_path="./my_project_full_v1.0.0.json"
)

# 在其他环境导入
group_service.import_group(
    config_path="./my_project_full_v1.0.0.json"
)
```

## 版本管理策略

### 统一版本发布

所有部分使用相同版本号：

```
my_project-bin:1.0.0
my_project-headers:1.0.0
my_project-docs:1.0.0
```

**优点**: 版本一致，易于理解

### 部分升级

只更新某个部分：

```
my_project-bin:1.0.0      (未变化)
my_project-headers:1.0.1  (新增API)
my_project-docs:1.0.0     (未变化)
```

**优点**: 灵活，减少不必要的更新

### 版本查询

查找特定版本的所有相关包：

```python
packages = package_repo.find_all()
version_1_0_0_packages = [
    p for p in packages 
    if str(p.package_name).startswith("my_project-") 
    and p.version.value == "1.0.0"
]
```

## 实际使用示例

### 场景1: 生产部署

只需要运行时二进制文件：

```bash
# 方式1: 直接下载二进制包
python3 -m binary_manager_v2.cli.main download \
    --package-name my_project-bin \
    --version 1.0.0 \
    --output /opt/myapp

# 方式2: 下载运行时组
python3 -m binary_manager_v2.cli.main download \
    --group-id 2 \
    --output /opt/myapp
```

### 场景2: 开发环境

需要二进制和头文件：

```bash
# 下载开发组
python3 -m binary_manager_v2.cli.main download \
    --group-id 3 \
    --output /home/developer/myproject
```

### 场景3: CI/CD集成

```bash
# 发布新版本的所有部分
python3 -m binary_manager_v2.cli.main publish \
    --source ./build/binaries \
    --package-name my_project-bin \
    --version ${CI_COMMIT_TAG}

python3 -m binary_manager_v2.cli.main publish \
    --source ./build/headers \
    --package-name my_project-headers \
    --version ${CI_COMMIT_TAG}

python3 -m binary_manager_v2.cli.main publish \
    --source ./docs \
    --package-name my_project-docs \
    --version ${CI_COMMIT_TAG}

# 创建开发环境组
python3 -m binary_manager_v2.cli.main group create \
    --group-name my_project_dev \
    --version ${CI_COMMIT_TAG} \
    --packages my_project-bin:${CI_COMMIT_TAG},my_project-headers:${CI_COMMIT_TAG}
```

## 最佳实践

### 1. 命名规范

使用清晰的后缀标识包类型：

```bash
# 二进制包
myapp-bin
myapp-runtime
myapp-binaries

# 头文件包
myapp-headers
myapp-dev
myapp-devel

# 文档包
myapp-docs
myapp-documentation
myapp-manual
```

### 2. 版本策略

- **同步版本**: 主要版本保持一致
- **独立版本**: 补丁版本可以独立
- **版本匹配**: 使用 Group 确保兼容性

### 3. 依赖管理

在 metadata 中记录依赖关系：

```python
publisher.publish(
    source_dir="./my_project-headers",
    package_name="my_project-headers",
    version="1.0.1",
    metadata={
        "type": "headers",
        "requires": "my_project-bin>=1.0.0"
    }
)
```

### 4. 文档说明

在每个包中包含 README 说明：

```
my_project-bin/README.md:
  # My Project Binaries
  ## Version: 1.0.0
  ## Components: Library, Executable
  ## Requires: None
  ## Compatible Headers: my_project-headers:1.0.0

my_project-headers/README.md:
  # My Project Headers
  ## Version: 1.0.0
  ## Compatible Binaries: my_project-bin:1.0.0
  ## API Version: 2.0
```

## 完整示例

查看 `examples_split_packages.py` 获取完整的示例代码，包含：

1. ✅ 分包发布（二进制、头文件、文档）
2. ✅ 独立下载（按需下载）
3. ✅ Group 管理（版本匹配）
4. ✅ 版本查询（查找相关包）
5. ✅ 部分升级（独立更新）
6. ✅ 元数据标记（类型分类）

运行示例：

```bash
python3 examples_split_packages.py
```

## 总结

Binary Manager V2 **完全支持**分包发布场景：

✅ **独立发布** - 每个部分可以独立发布
✅ **版本关联** - 通过版本号保持一致性
✅ **独立下载** - 按需下载特定部分
✅ **Group管理** - 统一管理相关包
✅ **灵活升级** - 支持部分升级
✅ **易于使用** - 清晰的API和CLI

**推荐方案**: 使用不同的 package_name + 相同的 version + Group 管理

这种模式完全满足嵌入式项目的分包发布需求！
