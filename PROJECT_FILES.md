# Binary Manager - 项目文件清单

## 项目结构

```
.
├── binary_manager/              # V1 - 基础版本
│   ├── publisher/              # 发布器模块
│   ├── downloader/            # 下载器模块
│   └── examples/              # 示例项目
│
├── binary_manager_v2/          # V2 - 洋葱架构版本（推荐）
│   ├── domain/                # Domain层（零外部依赖）
│   │   ├── entities/          # 实体
│   │   ├── value_objects/     # 值对象
│   │   ├── services/          # 领域服务
│   │   └── repositories/      # 仓储接口
│   │
│   ├── infrastructure/        # Infrastructure层
│   │   ├── storage/          # 存储服务（Local/S3）
│   │   ├── git/             # Git服务
│   │   └── database/         # 数据库仓储（SQLite）
│   │
│   ├── application/          # Application层
│   │   ├── publisher_service.py
│   │   ├── downloader_service.py
│   │   └── group_service.py
│   │
│   ├── cli/                 # Presentation层
│   │   └── main.py          # CLI工具
│   │
│   ├── shared/              # 共享工具
│   │   ├── logger.py
│   │   ├── progress.py
│   │   └── config.py
│   │
│   ├── config/              # 配置文件
│   │   ├── config.json
│   │   └── database_schema.sql
│   │
│   ├── database/            # 数据库文件
│   │   └── binary_manager.db
│   │
│   └── requirements_v2.txt  # V2依赖列表
│
├── examples/                # 示例项目
│   ├── simple_app/
│   ├── cli_tool/
│   ├── cpp_demo/
│   └── web_app/
│
├── tools/                   # 工具
│   └── release_app/         # Release App工具
│
├── install_dependencies.sh  # Ubuntu依赖安装脚本（支持V1/V2）
├── requirements.txt         # Python依赖列表（V2）
├── test.py                 # V1自动化测试脚本
├── test_v2_complete.py    # V2完整测试套件
│
└── 文档/
    ├── README.md                   # 项目总览
    ├── QUICKSTART.md               # V1快速开始（已删除）
    ├── V2_QUICKSTART.md            # V2快速开始
    ├── BINARY_MANAGER_V2.md        # V2详细文档
    ├── REFACTORING_SUMMARY.md      # 重构总结
    ├── TUTORIAL.md                 # 使用教程
    └── ...
```

## V2 架构层次

### Domain层（领域层）
**目录**: `binary_manager_v2/domain/`

**特点**: 零外部依赖，纯Python标准库

| 文件 | 说明 | 行数 |
|------|------|------|
| `entities/package.py` | 包实体 | ~140 |
| `entities/version.py` | 版本实体 | ~50 |
| `entities/group.py` | 分组实体 | ~80 |
| `entities/file_info.py` | 文件信息实体 | ~60 |
| `value_objects/package_name.py` | 包名称值对象 | ~30 |
| `value_objects/hash.py` | 哈希值对象 | ~40 |
| `value_objects/git_info.py` | Git信息值对象 | ~95 |
| `value_objects/storage_location.py` | 存储位置值对象 | ~50 |
| `services/file_scanner.py` | 文件扫描服务 | ~95 |
| `services/hash_calculator.py` | 哈希计算服务 | ~40 |
| `services/packager.py` | 打包服务 | ~65 |
| `repositories/package_repository.py` | 包仓储接口 | ~45 |
| `repositories/group_repository.py` | 分组仓储接口 | ~55 |
| `repositories/storage_repository.py` | 存储仓储接口 | ~40 |

### Infrastructure层（基础设施层）
**目录**: `binary_manager_v2/infrastructure/`

| 文件 | 说明 | 行数 |
|------|------|------|
| `storage/local_storage.py` | 本地存储实现 | ~130 |
| `storage/s3_storage.py` | S3存储实现（urllib3） | ~180 |
| `git/git_service.py` | Git服务实现 | ~145 |
| `database/sqlite_package_repository.py` | 包仓储实现 | ~210 |
| `database/sqlite_group_repository.py` | 分组仓储实现 | ~190 |

### Application层（应用层）
**目录**: `binary_manager_v2/application/`

| 文件 | 说明 | 行数 |
|------|------|------|
| `publisher_service.py` | 发布服务 | ~190 |
| `downloader_service.py` | 下载服务 | ~200 |
| `group_service.py` | 分组服务 | ~180 |

### Presentation层（表示层）
**目录**: `binary_manager_v2/cli/`

| 文件 | 说明 | 行数 |
|------|------|------|
| `main.py` | CLI工具 | ~300 |

### 共享层
**目录**: `binary_manager_v2/shared/`

| 文件 | 说明 | 行数 |
|------|------|------|
| `logger.py` | 日志工具 | ~60 |
| `progress.py` | 进度条工具 | ~120 |
| `config.py` | 配置管理 | ~50 |

## V1 模块

### 发布器
**目录**: `binary_manager/publisher/`

| 文件 | 说明 | 行数 |
|------|------|------|
| `scanner.py` | 文件扫描器 | ~150 |
| `packager.py` | 打包器 | ~120 |
| `main.py` | 发布器CLI | ~200 |

### 下载器
**目录**: `binary_manager/downloader/`

| 文件 | 说明 | 行数 |
|------|------|------|
| `downloader.py` | 下载器 | ~100 |
| `verifier.py` | 校验器 | ~80 |
| `main.py` | 下载器CLI | ~150 |

## 配置文件

| 文件 | 用途 |
|------|------|
| `binary_manager/config/schema.json` | JSON Schema验证规则 |
| `binary_manager_v2/config/config.json` | V2主配置文件 |
| `binary_manager_v2/config/database_schema.sql` | 数据库结构 |

## 测试文件

| 文件 | 说明 | 覆盖范围 |
|------|------|----------|
| `test.py` | V1自动化测试 | 发布、下载、验证 |
| `test_v2_complete.py` | V2完整测试套件 | 所有层次 |
| `test_architecture.py` | 架构测试 | Domain层 |

## 依赖对比

### V1 依赖
```
requests>=2.31.0
jsonschema>=4.20.0
tqdm>=4.66.0
```
**总大小**: ~105MB

### V2 依赖
```
urllib3>=2.0.0
requests>=2.31.0
```
**总大小**: ~6MB

**减少**: 94%

## 工具和脚本

| 文件 | 用途 |
|------|------|
| `install_dependencies.sh` | Ubuntu依赖安装（支持V1/V2） |
| `tools/release_app/` | Release App交互式发布管理工具 |

## 文档

| 文件 | 说明 |
|------|------|
| `README.md` | 项目总览和快速开始 |
| `QUICKSTART.md` | V1快速开始（已删除） |
| `V2_QUICKSTART.md` | V2快速开始 |
| `BINARY_MANAGER_V2.md` | V2详细文档 |
| `REFACTORING_SUMMARY.md` | 重构总结 |
| `REFACTORING_SUMMARY_CN.md` | 中文重构总结 |
| `TUTORIAL.md` | 使用教程 |
| `UPGRADE_DESIGN.md` | 升级设计文档 |
| `RELEASE_APP_GUIDE.md` | Release App指南 |
| `V2_TEST_REPORT.md` | V2测试报告 |

## 代码统计

### V2 代码量

| 层次 | 文件数 | 代码行数（估算） |
|------|--------|------------------|
| Domain层 | 14 | ~900 |
| Infrastructure层 | 5 | ~850 |
| Application层 | 3 | ~570 |
| Presentation层 | 1 | ~300 |
| Shared层 | 3 | ~230 |
| **总计** | **26** | **~2850** |

### V1 代码量

| 模块 | 文件数 | 代码行数（估算） |
|------|--------|------------------|
| Publisher | 3 | ~470 |
| Downloader | 3 | ~330 |
| **总计** | **6** | **~800** |

## 特性对比

| 特性 | V1 | V2 |
|------|----|----|
| 基本发布/下载 | ✅ | ✅ |
| SHA256哈希验证 | ✅ | ✅ |
| Git集成 | ❌ | ✅ |
| SQLite数据库 | ❌ | ✅ |
| 分组管理 | ❌ | ✅ |
| S3存储 | ❌ | ✅（urllib3）|
| 依赖大小 | ~105MB | ~6MB |
| 架构 | 单体 | 洋葱架构 |

## 使用建议

### 选择V1如果：
- 只需要基本的发布/下载功能
- 不需要数据库存储
- 不需要Git集成
- 关注简单性

### 选择V2如果：
- 需要完整的包管理功能
- 需要Git commit追踪
- 需要管理多个包的依赖关系
- 需要S3云存储
- 关注依赖大小和性能
- 需要可测试和可维护的架构

---

**更新日期**: 2026-02-26  
**版本**: V2（洋葱架构）
