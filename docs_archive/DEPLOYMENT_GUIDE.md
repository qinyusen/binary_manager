# Release Portal V3 部署指南

## 📋 目录

- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [详细安装步骤](#详细安装步骤)
- [配置说明](#配置说明)
- [数据库初始化](#数据库初始化)
- [启动服务](#启动服务)
- [生产环境配置](#生产环境配置)
- [反向代理配置](#反向代理配置)
- [系统服务配置](#系统服务配置)
- [监控和日志](#监控和日志)
- [备份策略](#备份策略)
- [故障排查](#故障排查)
- [安全检查清单](#安全检查清单)
- [性能优化](#性能优化)

---

## 环境要求

### 硬件要求

| 环境 | CPU | 内存 | 磁盘 |
|------|-----|------|------|
| **最小配置** | 2 核 | 2GB | 20GB |
| **推荐配置** | 4 核 | 4GB | 50GB |
| **生产环境** | 8+ 核 | 8GB+ | 100GB+ |

### 软件要求

#### 操作系统
- Linux（推荐 Ubuntu 20.04+ / CentOS 8+）
- macOS 10.15+
- Windows 10+（需要 WSL2）

#### Python 环境
- Python 3.8+
- pip 20.0+

#### 依赖服务
- SQLite 3（自带 Python）
- Nginx 1.18+（可选，用于生产环境）
- Supervisor / systemd（用于服务管理）

---

## 快速开始

### 5 分钟快速部署

```bash
# 1. 克隆仓库
git clone https://github.com/qinyusen/release_system.git
cd release_system

# 2. 安装依赖
pip install -r release_portal/requirements_v3.txt

# 3. 设置环境变量
export RELEASE_PORTAL_DB="./data/portal.db"
export RELEASE_PORTAL_SECRET="your-secret-key-change-in-production"

# 4. 初始化数据库
python3 -c "from release_portal.initializer import DatabaseInitializer; DatabaseInitializer().initialize()"

# 5. 启动服务
python3 -m release_portal.presentation.web.app
```

访问：http://localhost:5000

默认账户：
- 管理员：需要自行创建
- 或使用 CLI 创建：`release-portal register admin admin@example.com password --role Admin`

---

## 详细安装步骤

### 步骤 1: 系统准备

#### Ubuntu/Debian

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装系统依赖
sudo apt install -y python3 python3-pip python3-venv git nginx

# 安装测试依赖（可选）
sudo apt install -y sqlite3
```

#### CentOS/RHEL

```bash
# 更新系统
sudo yum update -y

# 安装系统依赖
sudo yum install -y python3 python3-pip git nginx

# 安装 EPEL 仓库
sudo yum install -y epel-release
```

#### macOS

```bash
# 安装 Homebrew（如果未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装依赖
brew install python3 git nginx
```

### 步骤 2: 创建应用用户

```bash
# 创建专用用户（推荐）
sudo useradd -r -s /bin/bash release-portal
sudo mkdir -p /opt/release-portal
sudo chown release-portal:release-portal /opt/release-portal
```

### 步骤 3: 下载代码

```bash
# 使用 release-portal 用户
sudo -u release-portal -i

# 克隆仓库
cd /opt
git clone https://github.com/qinyusen/release_system.git release-portal
cd release-portal

# 或使用压缩包
wget https://github.com/qinyusen/release_system/archive/main.zip
unzip main.zip
mv release_system-main release-portal
cd release-portal
```

### 步骤 4: 创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip
```

### 步骤 5: 安装依赖

```bash
# 安装生产依赖
pip install -r release_portal/requirements_v3.txt

# 安装基础依赖
pip install -r requirements.txt

# 安装测试依赖（开发环境）
pip install -r requirements-test.txt

# 验证安装
python3 -c "import flask; import release_portal; print('✅ 依赖安装成功')"
```

---

## 配置说明

### 环境变量配置

创建配置文件 `/opt/release-portal/.env`：

```bash
# 数据库配置
RELEASE_PORTAL_DB=/opt/release-portal/data/portal.db
RELEASE_PORTAL_SECRET=your-super-secret-key-change-this-in-production
RELEASE_PORTAL_TOKEN_EXPIRY_HOURS=24

# Web 服务配置
FLASK_APP=release_portal.presentation.web.app
FLASK_ENV=production
FLASK_DEBUG=0

# 存储配置
RELEASE_PORTAL_STORAGE_DIR=/opt/release-portal/storage
RELEASE_PORTAL_TEMP_DIR=/opt/release-portal/temp
RELEASE_PORTAL_MAX_UPLOAD_SIZE=500

# 日志配置
RELEASE_PORTAL_LOG_DIR=/opt/release-portal/logs
RELEASE_PORTAL_LOG_LEVEL=INFO

# 备份配置
RELEASE_PORTAL_BACKUP_DIR=/opt/release-portal/backups
RELEASE_PORTAL_BACKUP_RETENTION_DAYS=30
```

### 生成安全密钥

```bash
# 生成随机密钥
python3 -c "import secrets; print(secrets.token_hex(32))"
```

将生成的密钥设置到 `RELEASE_PORTAL_SECRET` 环境变量。

### 加载环境变量

在 `~/.bashrc` 或服务配置文件中添加：

```bash
# Release Portal 环境变量
export RELEASE_PORTAL_DB=/opt/release-portal/data/portal.db
export RELEASE_PORTAL_SECRET="your-secret-key"
export RELEASE_PORTAL_TOKEN_EXPIRY_HOURS=24
```

或使用 `python-dotenv`：

```bash
pip install python-dotenv
```

创建 `.env` 文件（推荐）：

```bash
cat > /opt/release-portal/.env << 'EOF'
RELEASE_PORTAL_DB=/opt/release-portal/data/portal.db
RELEASE_PORTAL_SECRET=your-secret-key
RELEASE_PORTAL_TOKEN_EXPIRY_HOURS=24
EOF
```

---

## 数据库初始化

### 方式 1: 使用 Python 脚本

```bash
# 确保数据目录存在
mkdir -p /opt/release-portal/data

# 初始化数据库
python3 << EOF
from release_portal.initializer import DatabaseInitializer

initializer = DatabaseInitializer("/opt/release-portal/data/portal.db")
initializer.initialize()
print("✅ 数据库初始化成功")
EOF
```

### 方式 2: 使用 CLI

```bash
# 设置环境变量
export RELEASE_PORTAL_DB="/opt/release-portal/data/portal.db"

# 初始化数据库
python3 -m release_portal.presentation.cli init
```

### 创建初始用户

```bash
# 创建管理员
python3 << EOF
from release_portal.initializer import create_container

container = create_container("/opt/release-portal/data/portal.db")

# 创建管理员
auth_service = container.auth_service
admin = auth_service.register(
    username="admin",
    email="admin@example.com",
    password="admin123",
    role_id="role_admin"
)
print(f"✅ 管理员创建成功: {admin.username}")
print(f"  用户ID: {admin.user_id}")

# 创建发布者
publisher = auth_service.register(
    username="publisher",
    email="publisher@example.com",
    password="pub123",
    role_id="role_publisher"
)
print(f"✅ 发布者创建成功: {publisher.username}")
EOF
```

---

## 启动服务

### 开发环境

```bash
# 激活虚拟环境
source venv/bin/activate

# 设置环境变量
export RELEASE_PORTAL_DB="./data/portal.db"
export RELEASE_PORTAL_SECRET="dev-secret-key"

# 启动开发服务器
flask run --host=0.0.0.0 --port=5000
```

### 生产环境

#### 方式 1: 使用 Gunicorn（推荐）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动服务
gunicorn \
  --bind 0.0.0.0:5000 \
  --workers 4 \
  --threads 2 \
  --timeout 120 \
  --access-logfile /opt/release-portal/logs/access.log \
  --error-logfile /opt/release-portal/logs/error.log \
  --log-level info \
  --env RELEASE_PORTAL_DB=/opt/release-portal/data/portal.db \
  --env RELEASE_PORTAL_SECRET=your-secret-key \
  release_portal.presentation.web.app:app
```

#### 方式 2: 使用 uWSGI

```bash
# 安装 uWSGI
pip install uwsgi

# 创建配置文件
cat > /opt/release-portal/uwsgi.ini << 'EOF'
[uwsgi]
module = release_portal.presentation.web.app:app
master = true
processes = 4
threads = 2
socket = /opt/release-portal/uwsgi.sock
chmod-socket = 660
vacuum = true
die-on-term = true
env = RELEASE_PORTAL_DB=/opt/release-portal/data/portal.db
env = RELEASE_PORTAL_SECRET=your-secret-key
EOF

# 启动服务
uwsgi --ini /opt/release-portal/uwsgi.ini
```

---

## 生产环境配置

### 创建必要目录

```bash
# 创建目录结构
sudo -u release-portal mkdir -p /opt/release-portal/{data,storage,temp,logs,backups}
sudo -u release-portal mkdir -p /opt/release-portal/logs/{access,error}

# 设置权限
chmod 750 /opt/release-portal/data
chmod 750 /opt/release-portal/storage
chmod 750 /opt/release-portal/logs
chmod 750 /opt/release-portal/backups
```

### 配置日志轮转

创建 `/etc/logrotate.d/release-portal`：

```
/opt/release-portal/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 release-portal release-portal
    sharedscripts
    postrotate
        systemctl reload release-portal > /dev/null 2>&1 || true
    endscript
}
```

---

## 反向代理配置

### Nginx 配置

创建 `/etc/nginx/sites-available/release-portal`：

```nginx
# Release Portal V3
upstream release_portal_backend {
    server unix:///opt/release-portal/uwsgi.sock;
    # 或使用 HTTP
    # server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name portal.example.com;

    # 重定向到 HTTPS（可选）
    # return 301 https://$server_name$request_uri;

    # 客户端最大请求体大小
    client_max_body_size 500M;

    # 访问日志
    access_log /var/log/nginx/release-portal-access.log;
    error_log /var/log/nginx/release-portal-error.log;

    # 静态文件
    location /static {
        alias /opt/release-portal/release_portal/presentation/web/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # API 端点
    location /api {
        include uwsgi_params;
        uwsgi_pass release_portal_backend;
        
        # 超时设置
        uwsgi_read_timeout 300s;
        uwsgi_connect_timeout 300s;
        uwsgi_send_timeout 300s;
    }

    # Web UI
    location / {
        include uwsgi_params;
        uwsgi_pass release_portal_backend;
    }

    # 健康检查
    location /health {
        include uwsgi_params;
        uwsgi_pass release_portal_backend;
        access_log off;
    }
}

# HTTPS 配置（使用 Let's Encrypt）
server {
    listen 443 ssl http2;
    server_name portal.example.com;

    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/portal.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/portal.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 其他配置同上...
    client_max_body_size 500M;

    location /static {
        alias /opt/release-portal/release_portal/presentation/web/static;
        expires 30d;
    }

    location /api {
        include uwsgi_params;
        uwsgi_pass release_portal_backend;
        uwsgi_read_timeout 300s;
    }

    location / {
        include uwsgi_params;
        uwsgi_pass release_portal_backend;
    }
}
```

启用配置：

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/release-portal /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 获取 SSL 证书（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d portal.example.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 系统服务配置

### Systemd 配置（推荐）

创建 `/etc/systemd/system/release-portal.service`：

```ini
[Unit]
Description=Release Portal V3
After=network.target

[Service]
Type=notify
User=release-portal
Group=release-portal
WorkingDirectory=/opt/release-portal
Environment="PATH=/opt/release-portal/venv/bin"
EnvironmentFile=/opt/release-portal/.env
ExecStart=/opt/release-portal/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile /opt/release-portal/logs/access.log \
    --error-logfile /opt/release-portal/logs/error.log \
    --log-level info \
    --capture-output \
    release_portal.presentation.web.app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=30
PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

管理服务：

```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start release-portal

# 设置开机自启
sudo systemctl enable release-portal

# 查看状态
sudo systemctl status release-portal

# 重启服务
sudo systemctl restart release-portal

# 查看日志
sudo journalctl -u release-portal -f
```

### Supervisor 配置

创建 `/etc/supervisor/conf.d/release-portal.conf`：

```ini
[program:release-portal]
command=/opt/release-portal/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile /opt/release-portal/logs/access.log \
    --error-logfile /opt/release-portal/logs/error.log \
    --log-level info \
    release_portal.presentation.web.app:app
directory=/opt/release-portal
user=release-portal
numprocs=1
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stdout_logfile=/opt/release-portal/logs/supervisor.log
stderr_logfile=/opt/release-portal/logs/supervisor_err.log
environment=RELEASE_PORTAL_DB="/opt/release-portal/data/portal.db",RELEASE_PORTAL_SECRET="your-secret-key"
```

管理服务：

```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 启动服务
sudo supervisorctl start release-portal

# 停止服务
sudo supervisorctl stop release-portal

# 重启服务
sudo supervisorctl restart release-portal

# 查看状态
sudo supervisorctl status
```

---

## 监控和日志

### 日志配置

#### 应用日志

```python
# 在应用中配置日志
import logging
from logging.handlers import RotatingFileHandler
import os

log_dir = os.environ.get('RELEASE_PORTAL_LOG_DIR', './logs')
os.makedirs(log_dir, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
```

#### 访问日志

Gunicorn 会自动记录访问日志到配置的文件中。

### 监控配置

#### 使用 systemd 监控

```bash
# 查看实时日志
sudo journalctl -u release-portal -f

# 查看最近的错误
sudo journalctl -u release-portal -p err -n 50
```

#### 使用 Prometheus 监控（可选）

```bash
# 安装 exporter
pip install prometheus-flask-exporter

# 修改应用
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
PrometheusMetrics(app)
```

---

## 备份策略

### 自动备份脚本

创建 `/opt/release-portal/scripts/backup.sh`：

```bash
#!/bin/bash
# Release Portal 自动备份脚本

# 配置
BACKUP_DIR="/opt/release-portal/backups"
DB_PATH="/opt/release-portal/data/portal.db"
STORAGE_DIR="/opt/release-portal/storage"
RETENTION_DAYS=30

# 创建备份目录
mkdir -p "$BACKUP_DIR"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_$DATE"

echo "[$(date)] 开始备份..."

# 1. 备份数据库
echo "备份数据库..."
sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/${BACKUP_NAME}.db'"

# 2. 备份存储文件（如果使用本地存储）
if [ -d "$STORAGE_DIR" ]; then
    echo "备份存储文件..."
    tar -czf "$BACKUP_DIR/${BACKUP_NAME}_storage.tar.gz" -C "$STORAGE_DIR" .
fi

# 3. 清理旧备份
echo "清理旧备份..."
find "$BACKUP_DIR" -name "backup_*.db" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "backup_*_storage.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] 备份完成: $BACKUP_NAME"
```

设置定时任务：

```bash
# 添加到 crontab
crontab -e

# 每天凌晨 2 点备份
0 2 * * * /opt/release-portal/scripts/backup.sh >> /opt/release-portal/logs/backup.log 2>&1
```

### 使用内置备份功能

```bash
# 使用 CLI 备份
python3 << EOF
from release_portal.initializer import create_container

container = create_container()
backup_service = container.backup_service

# 创建备份
backup = backup_service.create_backup(
    name="daily_backup",
    include_storage=True
)
print(f"✅ 备份成功: {backup['filename']}")

# 恢复备份
# backup_service.restore_backup("backup_20260306.tar.gz")
EOF
```

---

## 故障排查

### 常见问题

#### 1. 服务无法启动

**症状**: 服务启动失败

**排查**:
```bash
# 检查日志
sudo journalctl -u release-portal -n 50

# 检查端口占用
sudo netstat -tlnp | grep 5000

# 检查权限
ls -la /opt/release-portal/data/
```

**解决**:
```bash
# 修复权限
sudo chown -R release-portal:release-portal /opt/release-portal
sudo chmod 750 /opt/release-portal/data

# 释放端口
sudo lsof -ti:5000 | xargs kill -9
```

#### 2. 数据库锁定

**症状**: `database is locked`

**排查**:
```bash
# 检查数据库文件
ls -la /opt/release-portal/data/

# 检查数据库锁
sqlite3 /opt/release-portal/data/portal.db "PRAGMA database_list;"
```

**解决**:
```bash
# 停止服务
sudo systemctl stop release-portal

# 检查并修复数据库
sqlite3 /opt/release-portal/data/portal.db "PRAGMA integrity_check;"

# 重启服务
sudo systemctl start release-portal
```

#### 3. 权限错误

**症状**: `Permission denied`

**排查**:
```bash
# 检查用户
whoami
groups release-portal

# 检查目录权限
ls -la /opt/release-portal/
```

**解决**:
```bash
# 修复所有权
sudo chown -R release-portal:release-portal /opt/release-portal

# 设置正确的权限
sudo chmod 750 /opt/release-portal/data
sudo chmod 750 /opt/release-portal/storage
sudo chmod 755 /opt/release-portal/release_portal
```

#### 4. 内存不足

**症状**: `Cannot allocate memory`

**排查**:
```bash
# 检查内存
free -h

# 检查进程内存
ps aux | grep gunicorn
```

**解决**:
```bash
# 减少 worker 数量
# 修改服务配置中的 --workers 参数
sudo systemctl edit release-portal

# 或增加 swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 安全检查清单

### 部署前检查

- [ ] **更改默认密钥**：生成并设置强随机密钥
- [ ] **创建管理员账户**：使用强密码
- [ ] **配置 HTTPS**：使用有效的 SSL 证书
- [ ] **设置防火墙**：只开放必要端口（80, 443, 22）
- [ ] **限制文件上传**：设置合理的文件大小限制
- [ ] **配置日志**：启用访问和错误日志
- [ ] **设置备份**：配置自动备份策略
- [ ] **监控服务**：配置服务监控和告警
- [ ] **定期更新**：设置系统和依赖更新计划

### 生产环境加固

```bash
# 1. 配置防火墙
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 2. 限制 SSH 访问
sudo sed -i 's/#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# 3. 配置 fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 4. 定期安全更新
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 性能优化

### Gunicorn 配置优化

```bash
# 根据 CPU 核心数调整 worker 数量
# 公式：workers = (2 × CPU核心数) + 1

# 4 核 CPU 示例
gunicorn \
  --workers 9 \
  --threads 2 \
  --worker-class=gthread \
  --worker-connections 1000 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --timeout 120 \
  --keepalive 5 \
  release_portal.presentation.web.app:app
```

### 数据库优化

```sql
-- 创建索引
sqlite3 /opt/release-portal/data/portal.db << EOF
CREATE INDEX IF NOT EXISTS idx_releases_type ON releases(resource_type);
CREATE INDEX IF NOT EXISTS idx_releases_status ON releases(status);
CREATE INDEX IF NOT EXISTS idx_packages_release ON packages(release_id);
CREATE INDEX IF NOT EXISTS idx_licenses_org ON licenses(organization_name);
EOF

-- 定期 VACUUM
sqlite3 /opt/release-portal/data/portal.db "VACUUM;"
```

### Nginx 优化

```nginx
# 启用 gzip 压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript;

# 启用缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=portal_cache:10m max_size=1g inactive=60m;

location /static {
    proxy_cache portal_cache;
    proxy_cache_valid 200 30d;
    proxy_cache_use_stale error timeout invalid_header updating;
}
```

---

## 更新和维护

### 更新应用

```bash
# 停止服务
sudo systemctl stop release-portal

# 备份当前版本
cp -r /opt/release-portal /opt/release-portal.backup

# 更新代码
cd /opt/release-portal
git pull origin main

# 更新依赖
source venv/bin/activate
pip install --upgrade -r release_portal/requirements_v3.txt

# 数据库迁移（如有）
# python3 scripts/migrate.py

# 重启服务
sudo systemctl start release-portal

# 验证
curl http://localhost:5000/health
```

### 健康检查

创建健康检查脚本 `/opt/release-portal/scripts/healthcheck.sh`：

```bash
#!/bin/bash
# 健康检查脚本

HEALTH_URL="http://localhost:5000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
    echo "✅ 服务正常"
    exit 0
else
    echo "❌ 服务异常 (HTTP $RESPONSE)"
    exit 1
fi
```

---

## 附录

### A. 端口说明

| 端口 | 用途 | 说明 |
|------|------|------|
| 5000 | Flask 应用 | 默认端口 |
| 80 | HTTP | Nginx 反向代理 |
| 443 | HTTPS | Nginx 反向代理 |
| 22 | SSH | 服务器管理 |

### B. 目录结构

```
/opt/release-portal/
├── data/               # 数据库文件
├── storage/            # 存储的包文件
├── temp/               # 临时文件
├── logs/               # 日志文件
├── backups/            # 备份文件
├── venv/               # 虚拟环境
├── scripts/            # 自定义脚本
├── release_portal/     # 应用代码
├── binary_manager_v2/  # 二进制管理器
└── .env                # 环境变量
```

### C. 常用命令

```bash
# 查看服务状态
sudo systemctl status release-portal

# 查看实时日志
sudo journalctl -u release-portal -f

# 重启服务
sudo systemctl restart release-portal

# 手动备份
python3 -c "from release_portal.initializer import create_container; \
            container = create_container(); \
            backup = container.backup_service.create_backup('manual_backup', True); \
            print(f'备份成功: {backup[\"filename\"]}')"

# 数据库维护
sqlite3 /opt/release-portal/data/portal.db "VACUUM; ANALYZE;"

# 清理日志
journalctl --vacuum-time=7d
```

---

## 联系支持

- **文档**: [项目 README](README.md)
- **问题反馈**: [GitHub Issues](https://github.com/qinyusen/release_system/issues)
- **邮件**: support@example.com

---

**文档版本**: 1.0  
**最后更新**: 2026-03-06  
**维护者**: Release Portal Team
