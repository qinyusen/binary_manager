# Release Portal V3 - Web UI 页面和文件上传功能

## 已完成的功能

### 1. Web UI 页面

#### ✅ 发布管理页面 (`templates/releases.html`)
- 显示所有发布记录（支持按类型和状态筛选）
- 创建新发布（填写资源类型、版本、描述、更新日志）
- 上传包文件（支持 .tar.gz, .tar, .zip 格式）
- 发布和归档功能
- 美观的渐变侧边栏设计

#### ✅ 下载中心页面 (`templates/downloads.html`)
- 显示可下载的发布列表
- 按发布展示可用的资源包
- 实时下载功能（点击下载按钮直接下载）
- 显示用户许可证状态
- 统计信息展示

#### ✅ 许可证管理页面 (`templates/licenses.html`)
- 显示所有许可证列表
- 创建新许可证（组织名称、访问级别、资源类型、有效期）
- 延期许可证功能
- 激活/撤销许可证
- 仅管理员可见管理按钮

### 2. 文件上传功能

#### ✅ 新增 API 端点
```
POST /api/releases/<release_id>/packages
```

**功能：**
- 接受上传的包文件（multipart/form-data）
- 自动解压 .tar.gz, .tar, .zip 格式
- 调用 ReleaseService.add_package() 添加到发布
- 支持的内容类型：SOURCE, BINARY, DOCUMENT
- 文件大小限制：500MB
- 临时文件自动清理

**请求示例：**
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -F "package_file=@bsp.tar.gz" \
  -F "content_type=BINARY" \
  http://localhost:5000/api/releases/<release_id>/packages
```

**响应示例：**
```json
{
  "package_id": "pkg_123456",
  "message": "Package uploaded successfully"
}
```

#### ✅ 支持的文件格式
- `.tar.gz` - gzip 压缩的 tar 包
- `.tar` - 未压缩的 tar 包
- `.zip` - ZIP 压缩包

#### ✅ 文件处理流程
1. 验证文件扩展名
2. 保存到临时目录
3. 根据格式解压文件
4. 调用 add_package() 添加到发布
5. 自动清理临时文件

## 使用指南

### 启动 Web 服务器

```bash
# 设置环境变量
export FLASK_APP=release_portal.presentation.web.app
export FLASK_ENV=development

# 启动服务器
flask run --port 5000

# 或者使用 python
python3 -m release_portal.presentation.web.app
```

### 访问 Web UI

1. 打开浏览器访问：http://localhost:5000
2. 使用测试账户登录：
   - 管理员：admin / admin123
   - 发布者：publisher / pub123
   - 客户：customer / cust123

### 发布管理流程

1. **创建发布**
   - 点击"创建发布"按钮
   - 填写资源类型（BSP/驱动/示例）
   - 填写版本号（使用语义化版本，如 1.0.0）
   - 填写描述和更新日志
   - 选择包文件上传

2. **上传包文件**
   - 支持 .tar.gz, .tar, .zip 格式
   - 自动解压和处理
   - 实时反馈上传进度

3. **发布版本**
   - 点击"发布"按钮
   - 状态从 DRAFT 变为 PUBLISHED
   - 用户即可在下载中心看到

4. **归档版本**
   - 点击"归档"按钮
   - 状态变为 ARCHIVED
   - 从下载列表中移除

### 下载资源

1. 访问下载中心
2. 查看可用的发布
3. 点击资源包的"下载"按钮
4. 文件自动下载到本地

### 许可证管理（仅管理员）

1. 访问许可证管理页面
2. 点击"创建许可证"
3. 填写组织信息、访问级别、允许的资源类型
4. 设置有效期（天数）
5. 创建后可延期、激活或撤销

## 设计特点

### UI 设计
- **渐变色侧边栏**：紫色渐变 (#667eea → #764ba2)
- **卡片式布局**：圆角阴影设计
- **状态徽章**：彩色标识不同状态
- **响应式设计**：适配不同屏幕尺寸
- **Bootstrap 5**：现代化 UI 框架
- **Bootstrap Icons**：丰富的图标库

### 技术特点
- **JWT 认证**：无状态身份验证
- **sessionStorage**：客户端 token 存储
- **异步 API 调用**：fetch API
- **实时数据更新**：动态加载内容
- **错误处理**：友好的错误提示
- **安全上传**：文件类型和大小验证

## API 端点总览

### 认证 API (`/api/auth`)
- `POST /login` - 用户登录
- `POST /logout` - 用户登出
- `POST /register` - 注册用户（仅管理员）
- `GET /verify` - 验证 token

### 发布 API (`/api/releases`)
- `GET /releases` - 列出发布
- `GET /releases/<id>` - 获取发布详情
- `POST /releases` - 创建发布
- `POST /releases/<id>/publish` - 发布版本
- `POST /releases/<id>/archive` - 归档版本
- `POST /releases/<id>/packages` - **上传包文件**（新增）

### 下载 API (`/api/downloads`)
- `GET /downloads/releases` - 列出可下载发布
- `GET /downloads/<id>/packages` - 获取可下载包列表
- `GET /downloads/<id>/download/<type>` - 下载包
- `GET /downloads/license` - 获取用户许可证信息

### 许可证 API (`/api/licenses`)
- `GET /licenses` - 列出许可证
- `GET /licenses/<id>` - 获取许可证详情
- `POST /licenses` - 创建许可证（仅管理员）
- `POST /licenses/<id>/revoke` - 撤销许可证
- `POST /licenses/<id>/activate` - 激活许可证
- `POST /licenses/<id>/extend` - 延期许可证

## 测试

运行测试脚本：

```bash
python3 test_ui_pages.py
```

测试内容：
- ✅ Web UI 页面可访问性
- ✅ 认证要求验证
- ✅ 文件上传功能
- ✅ API 端点响应

## 已知问题

### 导入路径问题
某些模块使用相对导入，在特定环境下可能出现问题。已在 `api/__init__.py` 中添加 sys.path 设置。

### 临时文件清理
使用 atexit.register() 确保临时文件在程序结束时清理，但在异常情况下可能需要手动清理。

### 文件大小限制
默认限制为 500MB，可在 `app.py` 中调整 `MAX_CONTENT_LENGTH` 配置。

## 下一步改进建议

1. **进度条显示**：为文件上传添加进度条
2. **拖拽上传**：支持拖拽文件上传
3. **批量操作**：支持批量发布/归档
4. **版本对比**：显示不同版本间的差异
5. **操作日志**：记录所有管理操作
6. **通知系统**：发布新版本时发送通知
7. **数据导出**：导出发布列表和统计信息
8. **搜索功能**：在列表中添加搜索和排序
9. **权限细化**：更细粒度的权限控制
10. **国际化**：支持多语言

## 文件清单

### 新增文件
- `release_portal/presentation/web/templates/releases.html` (383 行)
- `release_portal/presentation/web/templates/downloads.html` (310 行)
- `release_portal/presentation/web/templates/licenses.html` (440 行)
- `test_ui_pages.py` (测试脚本)

### 修改文件
- `release_portal/presentation/web/api/releases.py` (添加文件上传端点)
- `release_portal/presentation/web/api/__init__.py` (添加路径设置)
- `release_portal/presentation/web/app.py` (修复导入路径)
- `release_portal/presentation/web/api/auth.py` (修复导入路径)

## 总结

本次开发完成了 Release Portal V3 Phase 2 的核心 Web UI 页面和文件上传功能：

✅ **3 个完整的 Web UI 页面** - 发布管理、下载中心、许可证管理
✅ **文件上传 API 端点** - 支持压缩包上传和解压
✅ **统一的 UI 设计风格** - 渐变色侧边栏、卡片式布局
✅ **完整的用户交互** - 创建、上传、发布、下载、管理
✅ **测试脚本** - 验证所有功能正常工作

Web UI 已经可以投入使用，用户可以通过浏览器完成所有发布管理操作！
