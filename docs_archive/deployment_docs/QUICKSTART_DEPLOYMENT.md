# 快速开始：5分钟部署 Release Portal

这是一个简化版的部署指南，帮助你在 5 分钟内快速启动 Release Portal。

## 前置条件

- Python 3.8+
- pip
- 2GB 内存
- 20GB 磁盘空间

## 快速部署

### 1. 克隆代码（30秒）

```bash
git clone https://github.com/qinyusen/release_system.git
cd release_system
```

### 2. 安装依赖（1分钟）

```bash
pip install -r release_portal/requirements_v3.txt
pip install -r requirements.txt
```

### 3. 配置环境（30秒）

```bash
# 生成密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 设置环境变量
export RELEASE_PORTAL_DB="./data/portal.db"
export RELEASE_PORTAL_SECRET="$SECRET_KEY"
export RELEASE_PORTAL_TOKEN_EXPIRY_HOURS=24

# 创建必要目录
mkdir -p data storage temp logs backups
```

### 4. 初始化数据库（1分钟）

```bash
python3 << 'EOF'
from release_portal.initializer import DatabaseInitializer, create_container

# 初始化数据库
print("正在初始化数据库...")
initializer = DatabaseInitializer("./data/portal.db")
initializer.initialize()
print("✅ 数据库初始化成功")

# 创建管理员账户
print("\n正在创建管理员账户...")
container = create_container("./data/portal.db")
auth_service = container.auth_service

admin = auth_service.register(
    username="admin",
    email="admin@example.com",
    password="admin123",
    role_id="role_admin"
)
print(f"✅ 管理员账户创建成功")
print(f"   用户名: {admin.username}")
print(f"   密码: admin123")
print(f"   ⚠️  请在生产环境中立即修改密码！")

# 创建发布者账户
publisher = auth_service.register(
    username="publisher",
    email="publisher@example.com",
    password="pub123",
    role_id="role_publisher"
)
print(f"\n✅ 发布者账户创建成功")
print(f"   用户名: {publisher.username}")
print(f"   密码: pub123")
EOF
```

### 5. 启动服务（30秒）

```bash
# 方式 1: 开发服务器（快速测试）
python3 -m release_portal.presentation.web.app

# 方式 2: 生产服务器（推荐）
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 release_portal.presentation.web.app:app
```

### 6. 访问系统（10秒）

打开浏览器访问：

```
http://localhost:5000
```

使用管理员账户登录：
- 用户名: `admin`
- 密码: `admin123`

## 验证部署

```bash
# 健康检查
curl http://localhost:5000/health

# 预期输出:
# {
#   "status": "healthy",
#   "version": "3.0.0",
#   "service": "Release Portal V3"
# }
```

## 下一步

### 生产环境部署

对于生产环境，请参考完整的[部署指南](DEPLOYMENT_GUIDE.md)，包括：

1. ✅ 使用反向代理（Nginx）
2. ✅ 配置 HTTPS（Let's Encrypt）
3. ✅ 设置系统服务（systemd）
4. ✅ 配置自动备份
5. ✅ 设置监控和日志
6. ✅ 使用强密码和安全密钥

### 常用命令

```bash
# 创建新用户
python3 << EOF
from release_portal.initializer import create_container
container = create_container()
user = container.auth_service.register(
    username="newuser",
    email="user@example.com",
    password="password123",
    role_id="role_publisher"
)
print(f"用户创建成功: {user.username}")
EOF

# 创建许可证
python3 << EOF
from release_portal.initializer import create_container
from release_portal.domain.value_objects import AccessLevel, ResourceType

container = create_container()
license_service = container.license_service
license = license_service.create_license(
    organization_name="客户公司",
    access_level=AccessLevel.FULL_ACCESS,
    resource_types={ResourceType.BSP}
)
print(f"许可证创建成功: {license.license_id}")
print(f"许可证密钥: {license.license_key}")
EOF

# 备份数据
python3 << EOF
from release_portal.initializer import create_container
container = create_container()
backup = container.backup_service.create_backup(
    name="manual_backup",
    include_storage=True
)
print(f"备份成功: {backup['filename']}")
EOF
```

### 系统服务（可选）

创建 systemd 服务文件：

```bash
sudo cat > /etc/systemd/system/release-portal.service << 'EOF'
[Unit]
Description=Release Portal V3
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
EnvironmentFile=$(pwd)/.env
ExecStart=$(which gunicorn) \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 120 \
    release_portal.presentation.web.app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable release-portal
sudo systemctl start release-portal
```

## 故障排查

### 问题 1: 端口已被占用

```bash
# 查找占用进程
lsof -ti:5000

# 杀死进程
lsof -ti:5000 | xargs kill -9
```

### 问题 2: 权限错误

```bash
# 修复权限
chmod 755 data storage temp logs backups
```

### 问题 3: 依赖安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 使用虚拟环境
python3 -m venv venv
source venv/bin/activate
pip install -r release_portal/requirements_v3.txt
```

### 问题 4: 数据库错误

```bash
# 删除旧数据库重新初始化
rm -f data/portal.db
python3 -c "from release_portal.initializer import DatabaseInitializer; DatabaseInitializer('./data/portal.db').initialize()"
```

## 安全提醒

⚠️ **在生产环境中，请务必：**

1. 修改默认密码
2. 使用强随机密钥（`RELEASE_PORTAL_SECRET`）
3. 配置 HTTPS
4. 启用防火墙
5. 设置自动备份
6. 定期更新系统和依赖

## 获取帮助

- 📖 [完整部署指南](DEPLOYMENT_GUIDE.md)
- 📖 [用户手册](USER_MANUAL.md)
- 📖 [API 文档](doc/design.md)
- 🐛 [问题反馈](https://github.com/qinyusen/release_system/issues)

---

**快速开始完成！** 🎉

你现在可以：
- 访问 http://localhost:5000
- 登录管理后台
- 创建发布
- 管理许可证
- 开始使用 Release Portal
