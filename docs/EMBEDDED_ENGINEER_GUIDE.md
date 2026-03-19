# 嵌入式工程师发布指南

> 本指南帮助嵌入式工程师使用发布平台管理项目，支持 **源码+文档** 和 **二进制+源码** 两种发布模式。

---

## 📋 目录

- [系统概述](#系统概述)
- [快速开始](#快速开始)
- [发布模式一：源码+文档](#发布模式一源码文档)
- [发布模式二：二进制+源码](#发布模式二二进制源码)
- [Web 界面使用](#web-界面使用)
- [自动化测试功能](#自动化测试功能)
- [数据备份与恢复](#数据备份与恢复)
- [API 接口使用](#api-接口使用)
- [权限与许可证](#权限与许可证)
- [常见场景](#常见场景)
- [故障排除](#故障排除)

---

## 系统概述

### 核心概念

```
┌─────────────────────────────────────────────────────────────┐
│                      发布平台架构                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│   │   SOURCE    │    │   BINARY    │    │  DOCUMENT   │   │
│   │   源码包    │    │   二进制包   │    │   文档包    │   │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘   │
│          │                  │                  │          │
│          └──────────────────┼──────────────────┘          │
│                             ▼                             │
│                    ┌─────────────────┐                    │
│                    │     Release     │                    │
│                    │     发布版本     │                    │
│                    └────────┬────────┘                    │
│                             │                             │
│              ┌──────────────┼──────────────┐              │
│              ▼              ▼              ▼              │
│         ┌─────────┐   ┌─────────┐   ┌─────────┐          │
│         │   BSP   │   │ DRIVER  │   │EXAMPLES │          │
│         │板级支持包│   │ 驱动程序 │   │ 示例程序 │          │
│         └─────────┘   └─────────┘   └─────────┘          │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

### 资源类型说明

| 资源类型 | 说明 | 典型内容 |
|---------|------|---------|
| **BSP** | 板级支持包 | Bootloader、Kernel、根文件系统、设备树 |
| **DRIVER** | 驱动程序 | 驱动源码、KO文件、配置脚本 |
| **EXAMPLES** | 示例程序 | Demo应用、测试程序、使用示例 |

### 内容类型说明

| 内容类型 | 说明 | 包格式 |
|---------|------|--------|
| **SOURCE** | 源代码 | `.tar.gz` 压缩包 |
| **BINARY** | 编译产物 | `.tar.gz` 压缩包 |
| **DOCUMENT** | 技术文档 | `.tar.gz` 压缩包 |

---

## 快速开始

### 1️⃣ 安装与初始化

```bash
# 安装依赖
pip install -r release_portal/requirements_v3.txt

# 初始化数据库
release-portal init

# 创建管理员账户
release-portal register admin admin@example.com admin123 --role Admin

# 登录系统
release-portal login admin
```

### 2️⃣ 验证安装

```bash
release-portal whoami
```

输出示例：
```
User ID: user_xxx
Username: admin
Email: admin@example.com
Role: Admin
```

---

## 发布模式一：源码+文档

> 适用于：开源项目、需要用户自行编译的场景

### 📊 流程图

```
┌────────────────────────────────────────────────────────────────┐
│                    源码+文档 发布流程                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌─────────┐ │
│  │ 准备源码  │───▶│ 准备文档  │───▶│ 创建发布  │───▶│ 添加包  │ │
│  └──────────┘    └──────────┘    └──────────┘    └─────────┘ │
│       │                                                   │    │
│       ▼                                                   ▼    │
│  ┌──────────────┐                                  ┌──────────┐ │
│  │ my_bsp/      │                                  │ 发布版本  │ │
│  │ ├── src/     │                                  └──────────┘ │
│  │ ├── include/ │                                       │       │
│  │ └── Makefile │                                       ▼       │
│  └──────────────┘                                  ┌──────────┐ │
│       │                                            │ 完成！    │ │
│       ▼                                            └──────────┘ │
│  ┌──────────────┐                                             │
│  │ docs/        │                                             │
│  │ ├── api.md   │                                             │
│  │ ├── port.md  │                                             │
│  │ └── quick.md │                                             │
│  └──────────────┘                                             │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 📝 详细步骤

#### Step 1: 准备项目目录结构

```
my_bsp_project/
├── source/                    # 源码目录
│   ├── bootloader/
│   │   └── u-boot/
│   ├── kernel/
│   │   └── linux-5.15/
│   ├── rootfs/
│   │   └── buildroot/
│   └── Makefile
├── document/                  # 文档目录
│   ├── README.md
│   ├── API_Reference.md
│   ├── Porting_Guide.md
│   └── Quick_Start.md
└── scripts/
    └── build.sh
```

#### Step 2: 创建发布草稿

```bash
release-portal publish create \
  --type BSP \
  --version 1.0.0 \
  --description "RV-Board BSP v1.0.0 - 支持完整Linux系统" \
  --changelog "初始版本发布

- 支持 U-Boot 2023.04
- 支持 Linux Kernel 5.15
- 包含完整根文件系统
- 提供 SD卡烧写脚本"
```

输出：
```
✓ Created draft release: rel_abc123
```

#### Step 3: 添加源码包

```bash
release-portal publish add-package rel_abc123 \
  --content-type SOURCE \
  --source ./my_bsp_project/source \
  --extract-git
```

> 💡 **提示**：`--extract-git` 会自动提取 Git commit 信息并记录到发布中

#### Step 4: 添加文档包

```bash
release-portal publish add-package rel_abc123 \
  --content-type DOCUMENT \
  --source ./my_bsp_project/document
```

#### Step 5: 发布版本

```bash
release-portal publish publish rel_abc123
```

输出：
```
✓ Release published successfully
  Release ID: rel_abc123
  Version: 1.0.0
  Packages: 2 (SOURCE, DOCUMENT)
```

### 🎯 用户下载流程

```
┌─────────────────────────────────────────────────────────────┐
│                   用户下载流程                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户登录 ──▶ 查看发布 ──▶ 选择包 ──▶ 下载 ──▶ 编译使用     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

```bash
# 客户端操作
release-portal login customer
release-portal list --type BSP
release-portal download download rel_abc123 --content-type SOURCE
release-portal download download rel_abc123 --content-type DOCUMENT

# 编译使用
cd downloads/rel_abc123/source
make all
```

---

## 发布模式二：二进制+源码

> 适用于：需要快速部署、同时提供源码支持的场景

### 📊 流程图

```
┌────────────────────────────────────────────────────────────────┐
│                   二进制+源码 发布流程                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐                 │
│  │ 编译构建  │───▶│ 准备源码  │───▶│ 创建发布  │                 │
│  └──────────┘    └──────────┘    └──────────┘                 │
│       │                                               │        │
│       ▼                                               ▼        │
│  ┌──────────────────┐                         ┌─────────────┐  │
│  │ build/output/    │                         │ 添加包      │  │
│  │ ├── u-boot.bin   │                         │             │  │
│  │ ├── zImage       │                         │  ┌───────┐  │  │
│  │ ├── rootfs.tar   │                         │  │BINARY │  │  │
│  │ └── sdcard.img   │                         │  └───────┘  │  │
│  └──────────────────┘                         │  ┌───────┐  │  │
│                                               │  │SOURCE │  │  │
│                                               │  └───────┘  │  │
│                                               └──────┬──────┘  │
│                                                      │         │
│                                                      ▼         │
│                                               ┌─────────────┐  │
│                                               │ 发布版本    │  │
│                                               └─────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 📝 详细步骤

#### Step 1: 编译构建项目

```bash
# 编译 Bootloader
cd bootloader/u-boot
make distclean
make rv_board_defconfig
make -j$(nproc)
cp u-boot.bin ../../build/output/

# 编译 Kernel
cd kernel/linux-5.15
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- rv_board_defconfig
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -j$(nproc)
cp arch/arm/boot/zImage ../../build/output/
cp arch/arm/boot/dts/rv-board.dtb ../../build/output/

# 构建根文件系统
cd rootfs/buildroot
make rv_board_defconfig
make
cp output/images/rootfs.tar ../../build/output/

# 生成 SD 卡镜像
cd build
./create_sdcard_img.sh
```

构建后的目录结构：
```
build/output/
├── u-boot.bin           # Bootloader 二进制
├── zImage               # Kernel 镜像
├── rv-board.dtb         # 设备树
├── rootfs.tar           # 根文件系统
├── sdcard.img           # 完整 SD 卡镜像
└── flash.sh             # 烧写脚本
```

#### Step 2: 创建发布

```bash
release-portal publish create \
  --type BSP \
  --version 2.0.0 \
  --description "RV-Board BSP v2.0.0 - 生产就绪版本" \
  --changelog "生产环境就绪

- 预编译完整系统镜像
- 支持 SD 卡直接烧写
- 包含完整源码
- 优化启动速度"
```

#### Step 3: 添加二进制包

```bash
release-portal publish add-package rel_def456 \
  --content-type BINARY \
  --source ./build/output
```

#### Step 4: 添加源码包

```bash
release-portal publish add-package rel_def456 \
  --content-type SOURCE \
  --source ./source \
  --extract-git
```

#### Step 5: 添加文档包（可选）

```bash
release-portal publish add-package rel_def456 \
  --content-type DOCUMENT \
  --source ./document
```

#### Step 6: 发布版本

```bash
release-portal publish publish rel_def456
```

输出：
```
✓ Release published successfully
  Release ID: rel_def456
  Version: 2.0.0
  Packages: 3 (BINARY, SOURCE, DOCUMENT)
```

### 🎯 用户下载流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    用户下载流程                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐         ┌─────────────┐                      │
│   │FULL_ACCESS  │         │BINARY_ACCESS│                      │
│   │  完全访问   │         │  二进制访问  │                      │
│   └──────┬──────┘         └──────┬──────┘                      │
│          │                       │                              │
│          ▼                       ▼                              │
│   ┌─────────────┐         ┌─────────────┐                      │
│   │• BINARY ✓   │         │• BINARY ✓   │                      │
│   │• SOURCE ✓   │         │• SOURCE ✗   │                      │
│   │• DOCUMENT ✓ │         │• DOCUMENT ✓ │                      │
│   └─────────────┘         └─────────────┘                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### FULL_ACCESS 用户（可下载源码）

```bash
release-portal login vip_customer
release-portal download download rel_def456
# 下载: BINARY + SOURCE + DOCUMENT

# 或按需下载
release-portal download download rel_def456 --content-type BINARY
release-portal download download rel_def456 --content-type SOURCE
```

#### BINARY_ACCESS 用户（仅二进制）

```bash
release-portal login regular_customer
release-portal download download rel_def456
# 下载: BINARY + DOCUMENT（源码包不可见）

# 直接烧写使用
cd downloads/rel_def456/binary
sudo ./flash.sh --device /dev/sdX
```

---

## Web 界面使用

> 发布平台提供友好的 Web 管理界面，支持图形化的发布、下载和许可证管理操作。

### 启动 Web 服务

```bash
# 设置环境变量
export FLASK_APP=release_portal.presentation.web.app

# 启动开发服务器
flask run --host 0.0.0.0 --port 5000

# 或使用 Python 直接运行
python -m release_portal.presentation.web.app
```

### 访问界面

```
浏览器访问: http://localhost:5000
```

### 界面功能概览

```
┌─────────────────────────────────────────────────────────────────┐
│                     Web 界面功能架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   仪表板    │  │  发布管理   │  │  下载中心   │             │
│  │  Dashboard  │  │  Releases   │  │  Downloads  │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │ 许可证管理  │  │  数据备份   │  │  审计日志   │             │
│  │  Licenses   │  │   Backup    │  │   Audit     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 主要页面功能

#### 1. 仪表板 (Dashboard)

```
┌────────────────────────────────────────────────────────────────┐
│  📊 统计概览                                                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 总发布数  │  │ 已发布   │  │  草稿    │  │ 许可证数 │       │
│  │    12    │  │    8     │  │    4     │  │    15    │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  快速操作                                                │  │
│  │  ┌─────────────────┐    ┌─────────────────┐             │  │
│  │  │  📦 创建新发布   │    │  📥 下载资源    │             │  │
│  │  └─────────────────┘    └─────────────────┘             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**功能**：
- 查看系统统计数据
- 快速创建发布
- 快速下载资源

#### 2. 发布管理 (Releases)

```
┌────────────────────────────────────────────────────────────────┐
│  发布管理                                    [+ 创建发布] [刷新] │
├────────────────────────────────────────────────────────────────┤
│  筛选: [所有类型 ▼]  [所有状态 ▼]                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ BSP - 2.0.0          [BSP] [PUBLISHED]                   │ │
│  │ RV-Board BSP v2.0.0 - 生产就绪版本                        │ │
│  │ 👤 admin | 📅 2026-03-19                                 │ │
│  │                                    [发布] [归档]          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ DRIVER - 1.2.0      [DRIVER] [DRAFT]                     │ │
│  │ WiFi驱动 v1.2.0                                           │ │
│  │ 👤 engineer | 📅 2026-03-18                               │ │
│  │                                    [发布] [归档]          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**功能**：
- 创建新发布（填写类型、版本、描述、更新日志）
- 上传包文件
- 发布/归档操作
- 按类型和状态筛选

#### 3. 下载中心 (Downloads)

```
┌────────────────────────────────────────────────────────────────┐
│  下载中心                                                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  选择发布: [rel_abc123 - BSP v2.0.0 ▼]                        │
│                                                                │
│  可用包:                                                       │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 📦 BINARY  bsp-diggo-2-0-0-binary.tar.gz    (15.2 MB)   │ │
│  │ 📄 DOCUMENT bsp-diggo-2-0-0-document.tar.gz (2.3 MB)    │ │
│  │ 💻 SOURCE  bsp-diggo-2-0-0-source.tar.gz   (45.8 MB)   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  [📥 下载全部]  [📥 下载选中]                                   │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**功能**：
- 选择发布的版本
- 查看可下载的包（根据许可证权限）
- 批量下载或单独下载

#### 4. 许可证管理 (Licenses)

```
┌────────────────────────────────────────────────────────────────┐
│  许可证管理                              [+ 创建许可证]         │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 许可证: lic_001                                           │ │
│  │ 组织: 战略合作伙伴A                                       │ │
│  │ 级别: FULL_ACCESS                                         │ │
│  │ 资源类型: BSP, DRIVER, EXAMPLES                          │ │
│  │ 过期时间: 2027-03-19                                      │ │
│  │ 状态: ✅ 有效                                             │ │
│  │                                    [延期] [吊销]          │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

**功能**：
- 创建新许可证
- 查看许可证列表
- 延期/吊销许可证
- 分配许可证给用户

### Web 界面发布流程

#### 创建发布

```
┌─────────────────────────────────────────┐
│  创建新发布                              │
├─────────────────────────────────────────┤
│                                         │
│  资源类型: [BSP (板级支持包) ▼]         │
│                                         │
│  版本:     [1.0.0          ]            │
│                                         │
│  描述:     [                    ]       │
│            [                    ]       │
│                                         │
│  更新日志: [                    ]       │
│            [                    ]       │
│                                         │
│  上传包文件:                             │
│  [选择文件...]  支持 .tar.gz, .zip      │
│                                         │
│  [取消]              [创建]             │
└─────────────────────────────────────────┘
```

---

## 自动化测试功能

> 发布平台支持发布前自动运行测试套件，确保发布的版本通过质量验证。

### 启用自动测试

```bash
# 安装测试依赖
pip install pytest pytest-cov pytest-flask

# 发布时启用测试
release-portal publish \
  --type BSP \
  --version 1.0.0 \
  --binary-dir ./build/output \
  --test
```

### 测试级别说明

```
┌─────────────────────────────────────────────────────────────────┐
│                      测试级别对比                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  级别          测试内容          耗时        适用场景            │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  critical     关键功能测试       ~30秒       日常开发发布        │
│  (默认)       • 用户认证                     快速迭代            │
│               • 创建发布                                         │
│               • 发布流程                                         │
│                                                                 │
│  all          所有测试           ~2分钟      重要版本发布        │
│               • 全部 API 测试                 生产环境部署       │
│               • 集成测试                                          │
│               • 单元测试                                          │
│                                                                 │
│  api          API 端点测试       ~1分钟      API 变更后         │
│               • 认证 API                       接口验证          │
│               • 发布 API                                          │
│               • 下载 API                                          │
│                                                                 │
│  integration  集成测试           ~1分钟      业务流程验证        │
│               • 端到端工作流                       跨模块测试     │
│               • 许可证管理                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 使用示例

#### CLI 命令行

```bash
# 关键测试（默认）
release-portal publish \
  --type BSP \
  --version 1.0.0 \
  --binary-dir ./build \
  --test

# 完整测试
release-portal publish \
  --type BSP \
  --version 1.0.0 \
  --binary-dir ./build \
  --test \
  --test-level all

# API 测试
release-portal publish \
  --type BSP \
  --version 1.0.0 \
  --binary-dir ./build \
  --test \
  --test-level api
```

#### 发布流程（带测试）

```
发布流程
    │
    ▼
创建发布草稿
    │
    ▼
添加包文件
    │
    ▼
发布（带测试）
    │
    ▼
┌─────────────────────┐
│  自动运行测试        │
│  • 检查测试环境      │
│  • 运行测试套件      │
│  • 收集测试结果      │
└─────────┬───────────┘
          │
          ▼
    ┌─────────────┐
    │ 测试通过？  │
    └─────┬───────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼
  是           否
    │           │
    ▼           ▼
发布成功 ✅  发布被阻止 ❌
```

#### 测试输出示例

```
============================================================
🧪 发布前验证 - Release ID: rel_abc123
📋 测试级别: critical
============================================================

✅ 测试环境检查通过
   - pytest: 已安装
   - 测试文件: 54 个

🔍 运行关键测试...

============================================================
✅ 测试通过！
📊 测试统计:
   - 总计: 10 个
   - 通过: 10 个
   - 失败: 0 个
   - 跳过: 0 个
   - 耗时: 28.45 秒
============================================================

✅ 测试验证通过，继续发布...
✓ 发布成功!
```

### 最佳实践

```
┌─────────────────────────────────────────────────────────────────┐
│                      测试使用建议                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  场景                    推荐级别        原因                    │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  日常开发迭代            critical       快速反馈，不影响效率     │
│  API 接口变更            api            针对性验证               │
│  重要版本发布            all            完整覆盖，确保质量       │
│  CI/CD 自动化           all            自动化全量验证           │
│  紧急修复                (跳过测试)     仅限紧急情况             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 数据备份与恢复

> 发布平台提供热备份和冷备份两种方案，保障数据安全。

### 备份类型对比

```
┌─────────────────────────────────────────────────────────────────┐
│                      备份类型对比                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  特性            热备份              冷备份                     │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  存储位置        本地快速存储        异地/低成本存储             │
│  恢复时间        秒级到分钟级        小时级到天级                │
│  存储成本        较高                较低                        │
│  保留期限        短期（天/周）       长期（月/年）               │
│  访问频率        频繁                极少                        │
│  用途            日常恢复            灾难恢复                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 热备份

热备份用于日常数据恢复，支持快速恢复到最近的状态。

#### 通过 Web UI

```
┌────────────────────────────────────────────────────────────────┐
│  数据备份                                                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  备份类型: ○ 仅数据库  ● 数据库 + 存储文件                     │
│                                                                │
│  备份名称: [daily_backup_20260319        ]                    │
│                                                                │
│  描述:     [每日自动备份                  ]                    │
│                                                                │
│                          [创建备份]                             │
│                                                                │
├────────────────────────────────────────────────────────────────┤
│  备份历史:                                                     │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │ 📦 backup_20260319_001.db    2026-03-19 10:30   [下载]   │ │
│  │ 📦 backup_20260318_001.db    2026-03-18 10:30   [下载]   │ │
│  │ 📦 backup_20260317_001.db    2026-03-17 10:30   [下载]   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

#### 通过 API

```bash
# 创建备份
curl -X POST http://localhost:5000/api/backup/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "backup_name": "daily_backup",
    "include_storage": true
  }'

# 列出备份
curl http://localhost:5000/api/backup \
  -H "Authorization: Bearer <token>"

# 恢复备份
curl -X POST http://localhost:5000/api/backup/backup_001/restore \
  -H "Authorization: Bearer <token>"
```

### 冷备份

冷备份用于长期归档和灾难恢复，支持多种存储后端。

#### 支持的存储后端

```
┌─────────────────────────────────────────────────────────────────┐
│                      冷备份存储后端                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  本地文件   │  │   AWS S3    │  │    SFTP     │             │
│  │   系统     │  │  /Glacier   │  │   服务器    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────┐                                               │
│  │    FTP      │                                               │
│  │   服务器    │                                               │
│  └─────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### 成本对比（AWS S3）

| 存储类型 | 价格/GB/月 | 检索时间 | 适用场景 |
|---------|-----------|---------|---------|
| STANDARD | $0.023 | 即时 | 热备份 |
| GLACIER | $0.004 | 3-5 小时 | 冷备份（季度/年度） |
| DEEP_ARCHIVE | $0.00099 | 12 小时 | 冷备份（多年归档） |

**成本节省**：
- Glacier vs Standard: **83% 节省**
- Deep Archive vs Standard: **96% 节省**

#### 创建冷备份

##### 本地文件系统

```bash
curl -X POST http://localhost:5000/api/cold-backup/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "backup_name": "monthly_archive",
    "include_storage": true,
    "storage_type": "local",
    "storage_config": {
      "storage_path": "./cold_storage",
      "retention_days": 365
    }
  }'
```

##### AWS S3 Glacier

```bash
curl -X POST http://localhost:5000/api/cold-backup/create \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "backup_name": "disaster_recovery",
    "include_storage": true,
    "storage_type": "s3",
    "storage_config": {
      "bucket": "my-backup-bucket",
      "prefix": "cold_backups/",
      "storage_class": "GLACIER",
      "region": "us-east-1"
    }
  }'
```

### 备份策略建议

```
┌─────────────────────────────────────────────────────────────────┐
│                 3-2-1 备份原则                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  3 份副本   ───▶  原始数据 + 2 份备份                           │
│  2 种介质   ───▶  本地存储 + 云存储                              │
│  1 份异地   ───▶  异地备份确保灾难恢复                           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  推荐保留策略:                                                  │
│  ─────────────────────────────────────────────────────────────  │
│  • 每日备份: 保留 7 天                                          │
│  • 每周备份: 保留 4 周                                          │
│  • 每月备份: 保留 12 个月                                       │
│  • 每年备份: 保留 7 年                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## API 接口使用

> 发布平台提供完整的 REST API，方便集成到 CI/CD 流程。

### API 认证

```bash
# 登录获取 Token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'

# 返回
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "user_xxx",
    "username": "admin",
    "role": "Admin"
  }
}
```

### 主要 API 端点

```
┌─────────────────────────────────────────────────────────────────┐
│                      API 端点一览                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  认证 API (/api/auth)                                           │
│  ├── POST /login           # 登录                               │
│  ├── POST /logout          # 登出                               │
│  └── GET  /verify          # 验证 Token                         │
│                                                                 │
│  发布 API (/api/releases)                                       │
│  ├── GET  /                # 列出发布                           │
│  ├── POST /                # 创建发布                           │
│  ├── GET  /:id             # 获取详情                           │
│  ├── POST /:id/publish     # 发布版本                           │
│  ├── POST /:id/archive     # 归档版本                           │
│  └── POST /:id/packages    # 添加包                             │
│                                                                 │
│  下载 API (/api/downloads)                                      │
│  ├── GET  /:id             # 获取可用包                         │
│  └── POST /:id/download    # 下载包                             │
│                                                                 │
│  许可证 API (/api/licenses)                                      │
│  ├── GET  /                # 列出许可证                         │
│  ├── POST /                # 创建许可证                         │
│  ├── POST /:id/extend      # 延期许可证                         │
│  └── POST /:id/revoke      # 吊销许可证                         │
│                                                                 │
│  备份 API (/api/backup)                                         │
│  ├── GET  /                # 列出备份                           │
│  ├── POST /create          # 创建备份                           │
│  └── POST /:id/restore     # 恢复备份                           │
│                                                                 │
│  冷备份 API (/api/cold-backup)                                  │
│  ├── GET  /                # 列出归档                           │
│  ├── POST /create          # 创建冷备份                         │
│  ├── POST /:id/retrieve    # 检索归档                           │
│  └── DELETE /:id           # 删除归档                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 完整发布示例（API）

```python
import requests

BASE_URL = "http://localhost:5000/api"

# 1. 登录
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "publisher",
    "password": "password123"
})
token = response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. 创建发布
response = requests.post(f"{BASE_URL}/releases", 
    headers=headers,
    json={
        "resource_type": "BSP",
        "version": "1.0.0",
        "description": "BSP v1.0.0",
        "changelog": "初始版本"
    }
)
release_id = response.json()["release_id"]

# 3. 添加包（需要 multipart/form-data）
with open("./build/output.tar.gz", "rb") as f:
    files = {"package_file": f}
    data = {"content_type": "BINARY"}
    requests.post(
        f"{BASE_URL}/releases/{release_id}/packages",
        headers=headers,
        files=files,
        data=data
    )

# 4. 发布（带测试）
response = requests.post(
    f"{BASE_URL}/releases/{release_id}/publish",
    headers=headers,
    json={
        "run_tests": True,
        "test_level": "critical"
    }
)

if response.status_code == 200:
    print("✅ 发布成功!")
else:
    print(f"❌ 发布失败: {response.json()['message']}")
```

### CI/CD 集成示例

```yaml
# .github/workflows/publish.yml
name: Publish Release

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build
        run: |
          make all
          tar -czf build.tar.gz build/output/
      
      - name: Login
        run: |
          TOKEN=$(curl -s -X POST ${{ secrets.PORTAL_URL }}/api/auth/login \
            -H "Content-Type: application/json" \
            -d '{"username":"${{ secrets.PORTAL_USER }}","password":"${{ secrets.PORTAL_PASS }}"}' \
            | jq -r '.token')
          echo "PORTAL_TOKEN=$TOKEN" >> $GITHUB_ENV
      
      - name: Create Release
        run: |
          curl -X POST ${{ secrets.PORTAL_URL }}/api/releases \
            -H "Authorization: Bearer $PORTAL_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{
              "resource_type": "BSP",
              "version": "${{ github.ref_name }}",
              "description": "Automated release from CI"
            }'
      
      - name: Publish with Tests
        run: |
          curl -X POST ${{ secrets.PORTAL_URL }}/api/releases/$RELEASE_ID/publish \
            -H "Authorization: Bearer $PORTAL_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"run_tests": true, "test_level": "all"}'
```

---

## 权限与许可证

### 许可证级别对比

```
┌────────────────────────────────────────────────────────────┐
│                    许可证权限矩阵                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  内容类型        FULL_ACCESS        BINARY_ACCESS         │
│  ─────────────────────────────────────────────────────    │
│                                                            │
│  SOURCE (源码)      ✓ 可下载            ✗ 不可下载         │
│                                                            │
│  BINARY (二进制)    ✓ 可下载            ✓ 可下载           │
│                                                            │
│  DOCUMENT (文档)    ✓ 可下载            ✓ 可下载           │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### 创建许可证

#### FULL_ACCESS 许可证（合作伙伴/核心客户）

```bash
release-portal license create \
  --organization "战略合作伙伴A" \
  --level FULL_ACCESS \
  --types BSP,DRIVER,EXAMPLES \
  --days 365 \
  --notes "战略合作协议编号: XXX-2024-001"
```

输出：
```
✓ License created successfully
  License ID: lic_full_001
  Organization: 战略合作伙伴A
  Access Level: FULL_ACCESS
  Resource Types: BSP, DRIVER, EXAMPLES
  Expires At: 2025-03-19
```

#### BINARY_ACCESS 许可证（普通客户）

```bash
release-portal license create \
  --organization "普通客户B" \
  --level BINARY_ACCESS \
  --types BSP \
  --days 180 \
  --notes "试用许可证"
```

输出：
```
✓ License created successfully
  License ID: lic_binary_001
  Organization: 普通客户B
  Access Level: BINARY_ACCESS
  Resource Types: BSP
  Expires At: 2025-09-19
```

### 分配许可证给用户

```python
from release_portal.initializer import create_container

container = create_container()

# 为用户分配许可证
container.auth_service.assign_license_to_user(
    user_id='user_xxx',
    license_id='lic_full_001'
)
```

---

## 常见场景

### 场景 1：发布新版本 BSP

```bash
# 完整发布流程脚本
#!/bin/bash
set -e

VERSION="2.1.0"
RELEASE_ID=""

# 1. 创建发布草稿
RELEASE_ID=$(release-portal publish create \
  --type BSP \
  --version $VERSION \
  --description "RV-Board BSP v$VERSION" \
  --changelog "$(cat CHANGELOG.md)" | grep "Release ID:" | awk '{print $3}')

# 2. 添加二进制包
release-portal publish add-package $RELEASE_ID \
  --content-type BINARY \
  --source ./build/output

# 3. 添加源码包
release-portal publish add-package $RELEASE_ID \
  --content-type SOURCE \
  --source ./source \
  --extract-git

# 4. 添加文档包
release-portal publish add-package $RELEASE_ID \
  --content-type DOCUMENT \
  --source ./document

# 5. 发布
release-portal publish publish $RELEASE_ID

echo "✓ BSP v$VERSION 发布成功!"
```

### 场景 2：驱动程序发布

```bash
# 驱动程序通常只需要二进制+源码
release-portal publish create \
  --type DRIVER \
  --version 1.2.0 \
  --description "WiFi驱动 v1.2.0"

# 添加预编译的 KO 文件
release-portal publish add-package rel_driver_001 \
  --content-type BINARY \
  --source ./driver/build

# 添加源码
release-portal publish add-package rel_driver_001 \
  --content-type SOURCE \
  --source ./driver/src \
  --extract-git

# 发布
release-portal publish publish rel_driver_001
```

### 场景 3：示例程序发布

```bash
# 示例程序通常源码+文档即可
release-portal publish create \
  --type EXAMPLES \
  --version 1.0.0 \
  --description "GPIO控制示例"

release-portal publish add-package rel_example_001 \
  --content-type SOURCE \
  --source ./examples/gpio

release-portal publish add-package rel_example_001 \
  --content-type DOCUMENT \
  --source ./examples/gpio/docs

release-portal publish publish rel_example_001
```

### 场景 4：版本更新

```bash
# 查看当前发布列表
release-portal list --type BSP

# 发布新版本
release-portal publish create \
  --type BSP \
  --version 2.1.1 \
  --description "RV-Board BSP v2.1.1 - Bug修复版本" \
  --changelog "修复:
- 修复 SPI 驱动偶发崩溃问题
- 优化内存占用
- 更新文档说明"

# ... 添加包并发布
```

---

## 包命名规范

### 自动命名规则

```
{type}-diggo-{version}-{content}.tar.gz

├── type: bsp, driver, examples
├── version: 1-0-0 (点号转连字符)
└── content: source, binary, document
```

### 示例

```
bsp-diggo-2-0-0-source.tar.gz     # BSP v2.0.0 源码包
bsp-diggo-2-0-0-binary.tar.gz     # BSP v2.0.0 二进制包
bsp-diggo-2-0-0-document.tar.gz   # BSP v2.0.0 文档包

driver-diggo-1-2-0-source.tar.gz  # 驱动 v1.2.0 源码包
driver-diggo-1-2-0-binary.tar.gz  # 驱动 v1.2.0 二进制包
```

---

## 命令速查表

### 发布管理

| 命令 | 说明 |
|-----|------|
| `release-portal publish create --type <TYPE> --version <VER>` | 创建发布草稿 |
| `release-portal publish add-package <ID> --content-type <TYPE> --source <PATH>` | 添加包 |
| `release-portal publish publish <ID>` | 发布版本 |
| `release-portal publish archive <ID>` | 归档版本 |
| `release-portal list --type <TYPE>` | 查看发布列表 |

### 下载管理

| 命令 | 说明 |
|-----|------|
| `release-portal download list <ID>` | 查看可下载的包 |
| `release-portal download download <ID>` | 下载所有可用包 |
| `release-portal download download <ID> --content-type <TYPE>` | 下载指定类型 |

### 许可证管理

| 命令 | 说明 |
|-----|------|
| `release-portal license create --organization <NAME> --level <LEVEL>` | 创建许可证 |
| `release-portal license list` | 查看许可证列表 |
| `release-portal license extend <ID> --days <DAYS>` | 延期许可证 |

---

## 故障排除

### 问题 1：权限不足

```
错误: ValueError: User does not have permission to publish BSP
```

**解决方案**：
```bash
# 检查当前用户角色
release-portal whoami

# 如果角色不是 Admin 或 Publisher，需要管理员更新
# 管理员操作：
release-portal login admin
release-portal register engineer engineer@example.com password --role Publisher
```

### 问题 2：许可证过期

```
错误: ValueError: License is inactive or expired
```

**解决方案**：
```bash
# 管理员延期许可证
release-portal license extend lic_xxx --days 90
```

### 问题 3：Token 过期

```
错误: Invalid or expired token
```

**解决方案**：
```bash
release-portal logout
release-portal login <username>
```

### 问题 4：找不到源码包

```
Note: SOURCE package is not available with your license level.
```

**说明**：这是正常提示，表示当前许可证级别（BINARY_ACCESS）不允许下载源码包。

**解决方案**：
- 联系管理员升级许可证为 FULL_ACCESS
- 或只下载 BINARY 和 DOCUMENT 包

---

## 最佳实践

### 1. 发布前检查清单

- [ ] 版本号符合语义化版本规范（如 v1.2.3）
- [ ] 源码已提交到 Git 仓库
- [ ] 编译产物已测试验证
- [ ] 文档已更新
- [ ] CHANGELOG.md 已更新

### 2. 目录结构建议

```
project/
├── source/           # 源码（用于 SOURCE 包）
├── build/            # 编译脚本
│   └── output/       # 编译产物（用于 BINARY 包）
├── document/         # 文档（用于 DOCUMENT 包）
├── scripts/          # 辅助脚本
├── CHANGELOG.md      # 变更日志
└── README.md         # 项目说明
```

### 3. 版本管理建议

```
主版本.次版本.修订版本

1.0.0  → 初始稳定版本
1.1.0  → 新增功能
1.1.1  → Bug 修复
2.0.0  → 重大更新（不兼容旧版本）
```

### 4. 安全建议

- 定期更新用户密码
- 为不同客户创建不同许可证
- 敏感项目使用 BINARY_ACCESS 许可证
- 定期审查许可证状态

---

## 附录

### 项目结构总览

```
release_portal/
├── domain/              # 领域层
│   ├── entities/       # 实体：User, Role, License, Release
│   └── value_objects/  # 值对象：ResourceType, ContentType
├── infrastructure/      # 基础设施层
│   ├── database/       # SQLite 数据库
│   └── auth/           # JWT 认证
├── application/         # 应用层
│   ├── release_service.py    # 发布服务
│   ├── download_service.py   # 下载服务
│   └── license_service.py    # 许可证服务
└── presentation/        # 表示层
    └── cli/            # 命令行工具
```

### 环境变量配置

```bash
# 数据库路径
export RELEASE_PORTAL_DB="./data/portal.db"

# JWT 密钥
export RELEASE_PORTAL_SECRET="your-secret-key"

# Token 过期时间（小时）
export RELEASE_PORTAL_TOKEN_EXPIRY_HOURS=24
```

---

**文档版本**：2.0  
**最后更新**：2026-03-19  
**适用平台版本**：Release Portal V3

## 📚 相关文档

| 文档 | 说明 |
|-----|------|
| [用户手册](../docs_archive/core_docs/USER_MANUAL.md) | 完整使用手册 |
| [快速入门](../docs_archive/core_docs/QUICK_START.md) | 5分钟快速上手 |
| [API 文档](http://localhost:5000/api/docs) | 在线 API 文档 |
| [自动化测试](../docs_archive/development_docs/AUTO_TESTS_FEATURE.md) | 测试功能详解 |
| [冷备份功能](../docs_archive/development_docs/COLD_BACKUP_FEATURE_COMPLETE.md) | 备份功能详解 |
