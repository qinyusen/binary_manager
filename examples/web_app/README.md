# Web App

一个简单的Web服务器示例，用于演示Binary Manager的发布和下载功能。

## 功能

这个应用提供了一个简单的HTTP服务器，可以提供静态文件服务和基本的API端点。

## 文件结构

```
web_app/
├── README.md           # 本文件
├── server.py          # Web服务器
├── index.html         # 示例HTML页面
└── api.py            # API模块
```

## 使用方法

### 安装

```bash
# 从本地安装
python3 -m binary_manager_v2.cli.main download \
    --package-name web_app \
    --version 1.0.0 \
    --output ./installed_apps
```

### 运行

```bash
cd web_app
python3 server.py
```

服务器将在 `http://localhost:8080` 启动

### 访问

- 主页: http://localhost:8080/
- API示例: http://localhost:8080/api/info
- 健康检查: http://localhost:8080/api/health

## API端点

### GET /api/health
健康检查端点

返回:
```json
{"status": "healthy", "version": "1.0.0"}
```

### GET /api/info
服务器信息端点

返回:
```json
{
  "name": "Web App",
  "version": "1.0.0",
  "description": "简单的Web服务器示例"
}
```

## 发布

使用Binary Manager发布:

```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./web_app \
    --package-name web_app \
    --version 1.0.0
```

## 版本历史

- **1.0.0** - 初始版本
  - 基本HTTP服务器
  - 静态文件服务
  - RESTful API端点
  - 健康检查
