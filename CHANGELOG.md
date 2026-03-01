# 变更日志

本文档记录了地瓜机器人发布系统的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [3.0.0] - 2024-01-15

### 新增
- ✨ 实现账号系统与存储系统的完全解耦
- ✨ 添加用户管理功能（注册、登录、认证）
- ✨ 添加角色管理（Admin、Publisher、Customer）
- ✨ 添加许可证管理系统
- ✨ 实现基于许可证的权限控制（FULL_ACCESS、BINARY_ACCESS）
- ✨ 实现发布管理功能（草稿、发布、归档）
- ✨ 实现受控下载功能（基于权限过滤）
- ✨ 添加完整的 CLI 命令行工具
- ✨ 添加 JWT Token 认证机制
- ✨ 创建核心接口：IAuthorizationService、IStorageService
- ✨ 实现 AuthorizationService（授权服务）
- ✨ 实现 StorageServiceAdapter（存储服务适配器）
- ✨ 重构 ReleaseService 和 DownloadService 使用接口
- ✨ 添加 AuthService.assign_license_to_user 方法

### 改进
- 🔧 优化 Permission.allows 方法支持全局权限（空resource_types）
- 🔧 修复 AuthorizationService.can_publish 方法的权限验证逻辑
- 🔧 修改包命名格式，将版本号中的点号转换为连字符
- 🔧 更新 Container 以包含 authorization_service

### 文档
- 📝 添加完整的使用手册（USER_MANUAL.md）
- 📝 添加快速入门指南（QUICK_START.md）
- 📝 添加账号系统与存储系统解耦设计文档（DECOUPLING_DESIGN.md）
- 📝 添加 Release Portal V3 实施总结（IMPLEMENTATION_SUMMARY.md）
- 📝 添加地瓜机器人发布系统总览（RELEASE_SYSTEM_README.md）
- 📝 更新 release_portal/README.md
- 📝 添加快速入门示例脚本（examples/quick_start.py）
- 📝 更新演示脚本（examples/demo_portal.py）

### 测试
- ✅ 添加解耦测试脚本（test_decoupling.py）
- ✅ 添加完整功能测试脚本（test_portal.py）
- ✅ 所有测试通过

### 架构
- 🏗️ 实现四层洋葱架构（Domain、Infrastructure、Application、Presentation）
- 🏗️ 账号系统独立于存储系统运行
- 🏗️ 存储系统独立于账号系统运行
- 🏗️ 通过接口层实现松耦合

## [2.0.0] - 2024-01-10

### 新增
- ✨ 实现 Binary Manager V2
- ✨ 完整的包管理功能
- ✨ 支持本地存储和 S3 云存储
- ✨ Git 集成（commit 追踪、branch、tag）
- ✨ SQLite 数据库持久化
- ✨ SHA256 哈希验证
- ✨ 分组管理功能
- ✨ CLI 命令行工具
- ✨ 交互式发布工具

### 文档
- 📝 添加 Binary Manager V2 完整文档
- 📝 添加快速入门指南
- 📝 添加示例程序和文档

## [1.0.0] - 2024-01-05

### 新增
- 🎉 初始版本发布
- ✨ 基础包管理功能
- ✨ 简单的发布和下载功能

---

## 版本说明

### [3.0.0] - Release Portal V3
地瓜机器人发布平台，基于 Binary Manager V2 构建，添加了：
- 用户管理和认证
- 许可证管理
- 基于权限的受控下载
- 完整的 CLI 工具

### [2.0.0] - Binary Manager V2
通用的二进制包管理系统，提供：
- 包的发布和下载
- 本地和云存储支持
- Git 集成
- 分组管理

### [1.0.0] - Initial Release
初始版本

---

## 下一步计划

### [3.1.0] - 计划中
- [ ] Web 用户界面
- [ ] 用户自助密码重置
- [ ] 许可证到期提醒
- [ ] 更详细的审计日志

### [3.2.0] - 规划中
- [ ] SSO 单点登录支持
- [ ] OAuth 集成
- [ ] 更丰富的许可证策略
- [ ] 包依赖关系管理

### [4.0.0] - 未来版本
- [ ] 多语言支持
- [ ] 插件系统
- [ ] 自动化测试和部署
- [ ] 性能优化和缓存
