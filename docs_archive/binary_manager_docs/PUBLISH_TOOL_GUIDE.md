# 交互式发布工具使用指南

## 概述

`publish_tool.py` 是一个友好的命令行交互式发布工具，简化了Binary Manager的发布流程。

## 特性

- ✅ **交互式引导** - 步骤化完成发布流程
- ✅ **智能默认值** - 自动填充常见选项
- ✅ **输入验证** - 实时验证输入的正确性
- ✅ **彩色输出** - 清晰的信息展示
- ✅ **快速发布** - 支持命令行参数快速发布
- ✅ **错误处理** - 友好的错误提示

## 使用方式

### 1. 交互式发布模式（推荐）

通过问答式交互完成发布：

```bash
python3 publish_tool.py
```

**流程示例**：

```
============================================================
     Binary Manager V2 - 交互式发布工具
============================================================

[1/7] 指定源目录
ℹ️  请输入要发布的源目录路径
➜ 源目录 [.]: ./examples/simple_app
✅ 源目录: /path/to/examples/simple_app

[2/7] 扫描文件
ℹ️  正在扫描文件...
✅ 扫描完成，找到 4 个文件

✓ 找到 4 个文件:
  .py 文件 (2):
    - main.py (1234 bytes)
    - calculator.py (5678 bytes)
  .json 文件 (1):
    - config.json (234 bytes)
  .md 文件 (1):
    - README.md (3456 bytes)

⚠️  是否继续发布? [Y/n]: y

[3/7] 设置包信息
➜ 包名 [simple_app]: 
➜ 版本号 [1.0.0]: 
➜ 描述 []: Simple Calculator Application

[4/7] 选择存储位置
存储位置:
  → 1. 本地存储
    2. S3云存储

➜ 请选择 [1-2]: 1
➜ 存储路径 [./releases]: 

[5/7] 确认发布信息

发布信息摘要:
  源目录:   /path/to/examples/simple_app
  包名:     simple_app
  版本:     1.0.0
  描述:     Simple Calculator Application
  文件数:   4
  总大小:   10602 bytes
  存储:     本地 (./releases)

➜ 确认发布? [Y/n]: y

============================================================
开始发布...
============================================================

✅ 发布成功!
============================================================

  包名:        simple_app
  版本:        1.0.0
  包ID:        1
  存档文件:    ./releases/simple_app_v1.0.0.zip
  配置文件:    ./releases/simple_app_v1.0.0.json

  Git信息:
    分支:    main
    提交:    abc1234

============================================================
         🎉 发布完成！
============================================================
```

### 2. 快速发布模式

使用命令行参数直接发布：

```bash
python3 publish_tool.py --quick ./examples/simple_app simple_app
```

指定版本号：

```bash
python3 publish_tool.py --quick ./examples/simple_app simple_app --version 2.0.0
```

**快速发布示例**：

```bash
$ python3 publish_tool.py --quick ./examples/web_app web_app

ℹ️  快速发布: web_app 1.0.0
  源目录: /path/to/examples/web_app

✅ 发布成功: web_app v1.0.0
  包ID: 2
```

## 命令行参数

```bash
python3 publish_tool.py [OPTIONS]

选项:
  --quick SOURCE NAME    快速发布模式（源目录 包名）
  --version VERSION      版本号（默认: 1.0.0）
  --help                 显示帮助信息
```

## 交互步骤详解

### 步骤1: 指定源目录

- **提示**: 输入要发布的源目录路径
- **默认值**: 当前目录（.）
- **验证**: 检查目录是否存在
- **示例**: 
  ```
  ➜ 源目录 [.]: ./my_project
  ```

### 步骤2: 扫描文件

- **自动扫描**: 自动扫描目录中的所有文件
- **显示文件**: 按文件类型分组显示
- **统计信息**: 显示文件数量和总大小
- **确认**: 询问是否继续

### 步骤3: 设置包信息

- **包名**: 建议使用小写字母、数字、下划线
- **版本号**: 建议使用语义化版本（如 1.0.0）
- **描述**: 可选的项目描述

**命名规范**：
```
good_name          # 推荐
my-project          # 推荐
my_project          # 推荐
My-Project          # 不推荐（包含大写）
my project          # 不推荐（包含空格）
```

**版本号格式**：
```
1.0.0               # 标准
2.1.3               # 标准
0.0.1-alpha         # 预发布版本
```

### 步骤4: 选择存储位置

**选项1: 本地存储**
- 存储到本地文件系统
- 默认路径: `./releases/`
- 适合: 开发、测试

**选项2: S3云存储**
- 存储到AWS S3
- 需要: Bucket名称、Access Key、Secret Key
- 适合: 生产、分发

### 步骤5: 确认发布

显示完整信息摘要：
- 源目录路径
- 包名和版本
- 文件统计
- 存储位置
- Git信息（如果有）

## 输出说明

### 颜色含义

- 🔵 **蓝色** - 信息提示
- 🟢 **绿色** - 成功消息
- 🟡 **黄色** - 警告提示
- 🔴 **红色** - 错误消息
- 🟣 **紫色** - 步骤标题

### 图标说明

- `ℹ️`  - 信息
- `✅`  - 成功
- `⚠️`  - 警告
- `❌`  - 错误
- `➜`  - 输入提示
- `🎉`  - 完成

## 使用场景

### 场景1: 初次发布

适合不熟悉命令行的用户：

```bash
python3 publish_tool.py
```

按照提示一步步完成发布。

### 场景2: 重复发布

对于频繁发布的项目，使用快速模式：

```bash
python3 publish_tool.py --quick ./build/my_app my_app
```

### 场景3: 批量发布

创建脚本批量发布多个组件：

```bash
#!/bin/bash
# 发布所有组件

python3 publish_tool.py --quick ./build/binaries myapp-bin
python3 publish_tool.py --quick ./build/headers myapp-headers
python3 publish_tool.py --quick ./docs myapp-docs

echo "所有组件发布完成！"
```

### 场景4: CI/CD集成

在CI/CD流程中使用快速发布：

```yaml
# .gitlab-ci.yml
publish:
  stage: deploy
  script:
    - python3 publish_tool.py --quick ./build myapp $CI_COMMIT_TAG
  only:
    - tags
```

## 常见问题

### Q1: 如何取消发布？

**A**: 在确认步骤输入 `n` 或按 `Ctrl+C`

```
➜ 确认发布? [Y/n]: n
⚠️  发布已取消
```

### Q2: 如何修改默认存储路径？

**A**: 在交互式发布时输入新路径

```
➜ 存储路径 [./releases]: /opt/releases
```

### Q3: 发布失败怎么办？

**A**: 查看错误信息，检查：
- 源目录是否存在
- 包名是否有效
- 版本号格式是否正确
- 存储路径是否有写权限

### Q4: 如何发布到S3？

**A**: 选择 "S3云存储"，填写必要信息：

```
➜ 请选择 [1-2]: 2
➜ S3 Bucket名称: my-bucket
➜ AWS区域 [us-east-1]: 
➜ Access Key ID: AKIAIOSFODNN7EXAMPLE
➜ Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### Q5: 可以发布包含Git信息的包吗？

**A**: 可以！如果源目录是Git仓库，工具会自动提取：
- Commit hash
- Branch名称
- Tag信息
- Author信息
- Commit消息

## 高级技巧

### 技巧1: 使用配置文件

创建配置文件避免重复输入：

```json
{
  "package_name": "myapp",
  "version": "1.0.0",
  "description": "My Application",
  "storage_path": "./releases"
}
```

### 技巧2: 预先准备源目录

确保源目录结构合理：

```
my_project/
├── README.md          # 项目说明
├── LICENSE            # 许可证
├── bin/              # 可执行文件
├── lib/              # 库文件
├── include/          # 头文件
└── docs/             # 文档
```

### 技巧3: 使用通配符忽略不需要的文件

创建 `.bmignore` 文件：

```
*.pyc
__pycache__/
*.log
.git/
.vscode/
```

### 技巧4: 脚本化发布流程

创建发布脚本：

```bash
#!/bin/bash
# release.sh

VERSION=$1

if [ -z "$VERSION" ]; then
    echo "用法: ./release.sh <version>"
    exit 1
fi

echo "发布版本 $VERSION..."

# 构建项目
./build.sh

# 发布二进制
python3 publish_tool.py --quick ./dist/bin myapp-bin --version $VERSION

# 发布头文件
python3 publish_tool.py --quick ./dist/headers myapp-headers --version $VERSION

echo "发布完成！"
```

使用：

```bash
./release.sh 1.0.0
```

## 故障排除

### 问题1: 权限错误

```
❌ 错误: Permission denied
```

**解决**:
```bash
chmod +x publish_tool.py
sudo python3 publish_tool.py
```

### 问题2: 模块导入错误

```
❌ 错误: No module named 'binary_manager_v2'
```

**解决**:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python3 publish_tool.py
```

### 问题3: 数据库错误

```
❌ 错误: Database is locked
```

**解决**: 确保没有其他进程正在访问数据库

### 问题4: 存储空间不足

```
❌ 错误: No space left on device
```

**解决**: 清理旧发布包或更改存储路径

## 对比：交互式 vs CLI

| 特性 | 交互式工具 | 标准CLI |
|------|-----------|---------|
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 灵活性 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 速度 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 学习曲线 | 低 | 中 |
| 适合场景 | 新手、偶尔发布 | 专家、频繁发布 |

## 最佳实践

### 1. 首次使用交互式工具

熟悉发布流程和各个选项。

### 2. 验证发布结果

发布后检查：

```bash
# 查看已发布的包
python3 -m binary_manager_v2.cli.main list

# 下载测试
python3 -m binary_manager_v2.cli.main download \
    --package-name myapp \
    --version 1.0.0 \
    --output ./test
```

### 3. 保留发布记录

维护 CHANGELOG.md 记录每次发布的内容。

### 4. 版本策略

使用语义化版本：

- `MAJOR.MINOR.PATCH`
- 主版本.次版本.修订号
- 示例: `1.0.0`, `1.2.3`, `2.0.0`

### 5. 测试发布

先发布测试版本：

```bash
python3 publish_tool.py --quick ./build myapp --version 1.0.0-rc1
```

## 总结

`publish_tool.py` 提供了：

✅ **简单** - 交互式引导，无需记忆命令
✅ **快速** - 快速模式，一键发布
✅ **友好** - 彩色输出，清晰的提示
✅ **灵活** - 支持本地和S3存储
✅ **可靠** - 输入验证，错误处理

开始使用：

```bash
python3 publish_tool.py
```
