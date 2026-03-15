# Release Portal V3 部署检查清单

## 📋 部署前检查

### 系统环境
- [ ] 操作系统版本（Ubuntu 20.04+ / CentOS 8+ / macOS 10.15+）
- [ ] Python 3.8+ 已安装
- [ ] pip 20.0+ 已安装
- [ ] 至少 2GB 内存可用
- [ ] 至少 20GB 磁盘空间可用
- [ ] 有 root 或 sudo 权限

### 网络配置
- [ ] 服务器有公网 IP 或可访问的内网 IP
- [ ] 防火墙已配置开放端口（80, 443, 22）
- [ ] DNS 配置正确（如使用域名）
- [ ] SSL 证书已准备（生产环境）

### 安全准备
- [ ] 已生成强随机密钥（`RELEASE_PORTAL_SECRET`）
- [ ] 已准备强密码策略
- [ ] 已配置 fail2ban（可选但推荐）

---

## 🚀 部署步骤检查

### 1. 安装依赖
```bash
# 检查 Python 版本
python3 --version  # 应该 >= 3.8

# 检查 pip 版本
pip3 --version  # 应该 >= 20.0

# 安装系统依赖
sudo apt install -y python3 python3-pip python3-venv git nginx sqlite3
```
- [ ] Python 版本检查通过
- [ ] 系统依赖安装成功

### 2. 创建应用用户
```bash
# 检查用户是否存在
id release-portal

# 如果不存在则创建
sudo useradd -r -s /bin/bash release-portal
```
- [ ] 应用用户已创建
- [ ] 用户目录 `/opt/release-portal` 已创建

### 3. 部署代码
```bash
# 克隆代码
git clone https://github.com/qinyusen/release_system.git /opt/release-portal/release_system

# 检查代码完整性
ls -la /opt/release-portal/release_system
```
- [ ] 代码已克隆
- [ ] 目录结构完整

### 4. 创建虚拟环境
```bash
# 创建虚拟环境
python3 -m venv /opt/release-portal/release_system/venv

# 激活虚拟环境
source /opt/release-portal/release_system/venv/bin/activate

# 升级 pip
pip install --upgrade pip
```
- [ ] 虚拟环境已创建
- [ ] pip 已升级到最新版本

### 5. 安装 Python 依赖
```bash
# 安装依赖
pip install -r release_portal/requirements_v3.txt
pip install -r requirements.txt
pip install gunicorn

# 验证安装
python3 -c "import flask; import release_portal; print('✅ 依赖安装成功')"
```
- [ ] 生产依赖安装成功
- [ ] 基础依赖安装成功
- [ ] 导入测试通过

### 6. 配置环境变量
```bash
# 生成密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 创建 .env 文件
cat > /opt/release-portal/release_system/.env << EOF
RELEASE_PORTAL_DB=/opt/release-portal/data/portal.db
RELEASE_PORTAL_SECRET=$SECRET_KEY
RELEASE_PORTAL_TOKEN_EXPIRY_HOURS=24
FLASK_ENV=production
FLASK_DEBUG=0
EOF

# 验证配置
cat /opt/release-portal/release_system/.env
```
- [ ] .env 文件已创建
- [ ] 密钥已生成（长度应该为 64 个字符）
- [ ] 配置项正确

### 7. 创建目录结构
```bash
# 创建目录
sudo -u release-portal mkdir -p /opt/release-portal/{data,storage,temp,logs,backups}

# 设置权限
sudo chmod 750 /opt/release-portal/{data,storage,logs,backups}

# 验证目录
ls -la /opt/release-portal/
```
- [ ] 所需目录已创建
- [ ] 权限设置正确

### 8. 初始化数据库
```bash
# 初始化数据库
python3 -c "from release_portal.initializer import DatabaseInitializer; DatabaseInitializer('/opt/release-portal/data/portal.db').initialize()"

# 验证数据库
sqlite3 /opt/release-portal/data/portal.db ".tables"
```
- [ ] 数据库文件已创建
- [ ] 数据库表已创建

### 9. 创建初始用户
```bash
# 创建管理员
python3 << EOF
from release_portal.initializer import create_container
container = create_container("/opt/release-portal/data/portal.db")
auth_service = container.auth_service
admin = auth_service.register(
    username="admin",
    email="admin@example.com",
    password="admin123",
    role_id="role_admin"
)
print(f"管理员创建成功: {admin.username}")
EOF
```
- [ ] 管理员账户已创建
- [ ] 发布者账户已创建（可选）
- [ ] 可以使用账户登录

### 10. 配置 systemd 服务
```bash
# 创建服务文件
sudo cat > /etc/systemd/system/release-portal.service << EOF
[Unit]
Description=Release Portal V3
After=network.target

[Service]
Type=notify
User=release-portal
WorkingDirectory=/opt/release-portal/release_system
Environment="PATH=/opt/release-portal/release_system/venv/bin"
EnvironmentFile=/opt/release-portal/release_system/.env
ExecStart=/opt/release-portal/release_system/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 120 \
    release_portal.presentation.web.app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 重新加载 systemd
sudo systemctl daemon-reload
```
- [ ] systemd 服务文件已创建
- [ ] 配置语法正确

### 11. 配置 Nginx（可选）
```bash
# 创建 Nginx 配置
sudo cat > /etc/nginx/sites-available/release-portal << EOF
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 500M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# 启用配置
sudo ln -s /etc/nginx/sites-available/release-portal /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t
```
- [ ] Nginx 配置已创建
- [ ] Nginx 配置测试通过

### 12. 配置 SSL 证书（生产环境）
```bash
# 使用 Let's Encrypt
sudo certbot --nginx -d your-domain.com

# 验证证书
sudo certbot certificates
```
- [ ] SSL 证书已安装
- [ ] HTTPS 可以访问

### 13. 启动服务
```bash
# 启动 Release Portal
sudo systemctl start release-portal

# 启动 Nginx（如果使用）
sudo systemctl start nginx

# 设置开机自启
sudo systemctl enable release-portal
sudo systemctl enable nginx
```
- [ ] Release Portal 服务已启动
- [ ] Nginx 服务已启动（如果使用）
- [ ] 服务已设置开机自启

---

## ✅ 部署后验证

### 1. 服务状态检查
```bash
# 检查服务状态
sudo systemctl status release-portal

# 检查端口监听
sudo netstat -tlnp | grep 5000

# 检查进程
ps aux | grep gunicorn
```
- [ ] 服务状态为 active (running)
- [ ] 端口 5000 正在监听
- [ ] 进程正常运行

### 2. 健康检查
```bash
# 健康检查端点
curl http://localhost:5000/health

# 预期输出:
# {"status":"healthy","version":"3.0.0","service":"Release Portal V3"}
```
- [ ] 健康检查返回 200
- [ ] 返回内容正确

### 3. Web 访问检查
```bash
# 访问 Web UI
curl -I http://localhost:5000/

# 预期输出:
# HTTP/1.1 200 OK
```
- [ ] Web 页面可以访问
- [ ] 页面显示正常

### 4. 登录测试
```
# 使用浏览器访问
http://your-domain.com

# 使用管理员账户登录
用户名: admin
密码: admin123
```
- [ ] 可以成功登录
- [ ] 界面显示正常

### 5. 功能测试
- [ ] 可以创建发布
- [ ] 可以上传文件
- [ ] 可以下载资源
- [ ] 可以管理许可证

### 6. 日志检查
```bash
# 查看应用日志
sudo journalctl -u release-portal -n 50

# 查看错误日志
sudo journalctl -u release-portal -p err -n 50

# 查看 Nginx 日志
sudo tail -f /var/log/nginx/release-portal-error.log
```
- [ ] 没有严重的错误日志
- [ ] 日志正常输出

### 7. 性能检查
```bash
# 检查资源使用
top -p $(pgrep -f gunicorn)

# 检查内存使用
free -h

# 检查磁盘使用
df -h
```
- [ ] CPU 使用率正常
- [ ] 内存使用正常
- [ ] 磁盘空间充足

---

## 🔒 安全检查

### 基本安全
- [ ] 已修改默认密码
- [ ] 密钥已更换为强随机值
- [ ] 防火墙已正确配置
- [ ] SSH 访问已限制

### SSL/TLS
- [ ] HTTPS 已启用
- [ ] SSL 证书有效
- [ ] 使用强加密协议
- [ ] HUC 已启用（可选）

### 备份策略
- [ ] 自动备份已配置
- [ ] 备份测试通过
- [ ] 恢复流程已验证
- [ ] 备份存储安全

### 监控告警
- [ ] 监控系统已配置
- [ ] 告警规则已设置
- [ ] 日志聚合已配置
- [ ] 性能监控已启用

---

## 📊 性能优化检查

### Gunicorn 配置
- [ ] Worker 数量根据 CPU 核心数调整
- [ ] 线程数已配置
- [ ] 超时时间合理
- [ ] 日志级别正确

### 数据库优化
- [ ] 索引已创建
- [ ] 定期 VACUUM 已配置
- [ ] 查询性能正常
- [ ] 数据库大小监控

### Nginx 优化
- [ ] Gzip 压缩已启用
- [ ] 静态文件缓存已配置
- [ ] 连接限制已设置
- [ ] 超时时间合理

---

## 📝 文档检查

- [ ] 部署文档已更新
- [ ] 配置文档已更新
- [ ] 运维手册已准备
- [ ] 故障排查指南已准备

---

## 🎯 上线前最终检查

### 关键项
- [ ] 所有测试通过
- [ ] 备份策略已验证
- [ ] 回滚方案已准备
- [ ] 监控告警已配置
- [ ] 安全审计已完成

### 业务验证
- [ ] 核心功能正常
- [ ] 数据迁移完成（如需要）
- [ ] 用户培训完成
- [ ] 支持流程已建立

---

## ⚠️ 常见问题排查

### 问题：服务无法启动
```bash
# 查看详细日志
sudo journalctl -u release-portal -n 100

# 检查配置
sudo systemctl daemon-reload
```

### 问题：无法访问 Web UI
```bash
# 检查防火墙
sudo ufw status

# 检查 Nginx 配置
sudo nginx -t

# 检查端口
sudo netstat -tlnp | grep 5000
```

### 问题：数据库错误
```bash
# 检查数据库文件
ls -la /opt/release-portal/data/

# 检查数据库完整性
sqlite3 /opt/release-portal/data/portal.db "PRAGMA integrity_check;"
```

---

## 📞 支持联系

- 📖 [完整部署指南](DEPLOYMENT_GUIDE.md)
- 📖 [快速开始](QUICKSTART_DEPLOYMENT.md)
- 📖 [Docker 部署](DOCKER_DEPLOYMENT.md)
- 🐛 [问题反馈](https://github.com/qinyusen/release_system/issues)

---

**检查清单版本**: 1.0  
**最后更新**: 2026-03-06  
**适用版本**: Release Portal V3.0.0
