#!/bin/bash
# Release Portal V3 一键部署脚本
# 适用于 Ubuntu 20.04+ / Debian 11+

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -eq 0 ]; then 
        log_warning "不建议使用 root 用户运行此脚本"
        read -p "是否继续? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# 检测操作系统
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$NAME
        VERSION=$VERSION_ID
    else
        log_error "无法检测操作系统"
        exit 1
    fi
    log_info "检测到操作系统: $OS $VERSION"
}

# 安装系统依赖
install_system_dependencies() {
    log_info "安装系统依赖..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv git nginx sqlite3
    elif command -v yum &> /dev/null; then
        sudo yum update -y
        sudo yum install -y python3 python3-pip git nginx sqlite
    else
        log_error "不支持的包管理器"
        exit 1
    fi
    
    log_success "系统依赖安装完成"
}

# 创建应用用户
create_app_user() {
    log_info "创建应用用户..."
    
    if id "release-portal" &>/dev/null; then
        log_warning "用户 release-portal 已存在"
    else
        sudo useradd -r -s /bin/bash -d /opt/release-portal release-portal
        log_success "用户 release-portal 创建成功"
    fi
    
    sudo mkdir -p /opt/release-portal
    sudo chown release-portal:release-portal /opt/release-portal
}

# 克隆代码
clone_repository() {
    log_info "克隆代码仓库..."
    
    if [ -d "/opt/release-portal/release_system" ]; then
        log_warning "代码目录已存在"
        read -p "是否更新代码? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            cd /opt/release-portal/release_system
            sudo -u release-portal git pull
        fi
    else
        sudo -u release-portal git clone https://github.com/qinyusen/release_system.git /opt/release-portal/release_system
    fi
    
    cd /opt/release-portal/release_system
    log_success "代码准备完成"
}

# 创建虚拟环境
create_virtualenv() {
    log_info "创建虚拟环境..."
    
    if [ -d "/opt/release-portal/release_system/venv" ]; then
        log_warning "虚拟环境已存在"
    else
        sudo -u release-portal python3 -m venv /opt/release-portal/release_system/venv
    fi
    
    log_success "虚拟环境创建完成"
}

# 安装 Python 依赖
install_python_dependencies() {
    log_info "安装 Python 依赖..."
    
    sudo -u release-portal /opt/release-portal/release_system/venv/bin/pip install --upgrade pip
    sudo -u release-portal /opt/release-portal/release_system/venv/bin/pip install \
        -r /opt/release-portal/release_system/release_portal/requirements_v3.txt \
        -r /opt/release-portal/release_system/requirements.txt \
        gunicorn
    
    log_success "Python 依赖安装完成"
}

# 配置环境变量
configure_environment() {
    log_info "配置环境变量..."
    
    # 生成密钥
    SECRET_KEY=$(sudo -u release-portal python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # 创建 .env 文件
    cat > /opt/release-portal/release_system/.env << EOF
RELEASE_PORTAL_DB=/opt/release-portal/data/portal.db
RELEASE_PORTAL_SECRET=$SECRET_KEY
RELEASE_PORTAL_TOKEN_EXPIRY_HOURS=24
FLASK_ENV=production
FLASK_DEBUG=0
RELEASE_PORTAL_STORAGE_DIR=/opt/release-portal/storage
RELEASE_PORTAL_TEMP_DIR=/opt/release-portal/temp
RELEASE_PORTAL_LOG_DIR=/opt/release-portal/logs
RELEASE_PORTAL_BACKUP_DIR=/opt/release-portal/backups
RELEASE_PORTAL_MAX_UPLOAD_SIZE=500
EOF
    
    log_success "环境变量配置完成"
}

# 创建目录结构
create_directories() {
    log_info "创建目录结构..."
    
    sudo -u release-portal mkdir -p /opt/release-portal/{data,storage,temp,logs,backups}
    sudo chmod 750 /opt/release-portal/{data,storage,logs,backups}
    
    log_success "目录结构创建完成"
}

# 初始化数据库
initialize_database() {
    log_info "初始化数据库..."
    
    if [ -f "/opt/release-portal/data/portal.db" ]; then
        log_warning "数据库已存在"
        read -p "是否重新初始化数据库? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo rm -f /opt/release-portal/data/portal.db
        else
            log_info "跳过数据库初始化"
            return
        fi
    fi
    
    sudo -u release-portal /opt/release-portal/release_system/venv/bin/python3 << EOF
import sys
sys.path.insert(0, '/opt/release-portal/release_system')

from release_portal.initializer import DatabaseInitializer, create_container

# 初始化数据库
initializer = DatabaseInitializer("/opt/release-portal/data/portal.db")
initializer.initialize()
print("✅ 数据库初始化成功")

# 创建管理员账户
container = create_container("/opt/release-portal/data/portal.db")
auth_service = container.auth_service

admin = auth_service.register(
    username="admin",
    email="admin@example.com",
    password="admin123",
    role_id="role_admin"
)
print(f"✅ 管理员账户创建成功")
print(f"   用户名: admin")
print(f"   密码: admin123")
print(f"   ⚠️  请登录后立即修改密码！")

publisher = auth_service.register(
    username="publisher",
    email="publisher@example.com",
    password="pub123",
    role_id="role_publisher"
)
print(f"✅ 发布者账户创建成功")
print(f"   用户名: publisher")
print(f"   密码: pub123")
EOF
    
    log_success "数据库初始化完成"
}

# 配置 systemd 服务
configure_systemd_service() {
    log_info "配置 systemd 服务..."
    
    sudo cat > /etc/systemd/system/release-portal.service << EOF
[Unit]
Description=Release Portal V3
After=network.target

[Service]
Type=notify
User=release-portal
Group=release-portal
WorkingDirectory=/opt/release-portal/release_system
Environment="PATH=/opt/release-portal/release_system/venv/bin"
EnvironmentFile=/opt/release-portal/release_system/.env
ExecStart=/opt/release-portal/release_system/venv/bin/gunicorn \\
    --bind 0.0.0.0:5000 \\
    --workers 4 \\
    --threads 2 \\
    --timeout 120 \\
    --access-logfile /opt/release-portal/logs/access.log \\
    --error-logfile /opt/release-portal/logs/error.log \\
    --log-level info \\
    --capture-output \\
    release_portal.presentation.web.app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=30
PrivateTmp=true
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable release-portal
    
    log_success "systemd 服务配置完成"
}

# 配置 Nginx
configure_nginx() {
    log_info "配置 Nginx..."
    
    read -p "是否配置 Nginx 反向代理? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "跳过 Nginx 配置"
        return
    fi
    
    read -p "输入域名 (例如: portal.example.com): " DOMAIN_NAME
    
    sudo cat > /etc/nginx/sites-available/release-portal << EOF
server {
    listen 80;
    server_name $DOMAIN_NAME;

    client_max_body_size 500M;

    access_log /var/log/nginx/release-portal-access.log;
    error_log /var/log/nginx/release-portal-error.log;

    location /static {
        alias /opt/release-portal/release_system/release_portal/presentation/web/static;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
    }

    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }

    location /health {
        proxy_pass http://127.0.0.1:5000;
        access_log off;
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/release-portal /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    
    log_success "Nginx 配置完成"
    log_info "请访问: http://$DOMAIN_NAME"
}

# 配置防火墙
configure_firewall() {
    log_info "配置防火墙..."
    
    if command -v ufw &> /dev/null; then
        read -p "是否配置防火墙 (ufw)? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo ufw allow 22/tcp
            sudo ufw allow 80/tcp
            sudo ufw allow 443/tcp
            sudo ufw --force enable
            log_success "防火墙配置完成"
        fi
    fi
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    sudo systemctl start release-portal
    sleep 3
    
    if sudo systemctl is-active --quiet release-portal; then
        log_success "Release Portal 服务启动成功"
    else
        log_error "Release Portal 服务启动失败"
        sudo journalctl -u release-portal -n 50
        exit 1
    fi
}

# 配置自动备份
configure_backup() {
    log_info "配置自动备份..."
    
    read -p "是否配置自动备份? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "跳过自动备份配置"
        return
    fi
    
    # 创建备份脚本
    sudo cat > /opt/release-portal/scripts/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/release-portal/backups"
DB_PATH="/opt/release-portal/data/portal.db"
STORAGE_DIR="/opt/release-portal/storage"
RETENTION_DAYS=30

mkdir -p "$BACKUP_DIR"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="backup_$DATE"

echo "[$(date)] 开始备份..."
sqlite3 "$DB_PATH" ".backup '$BACKUP_DIR/${BACKUP_NAME}.db'"

if [ -d "$STORAGE_DIR" ]; then
    tar -czf "$BACKUP_DIR/${BACKUP_NAME}_storage.tar.gz" -C "$STORAGE_DIR" . 2>/dev/null
fi

find "$BACKUP_DIR" -name "backup_*.db" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "backup_*_storage.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] 备份完成: $BACKUP_NAME"
EOF
    
    sudo chmod +x /opt/release-portal/scripts/backup.sh
    sudo chown release-portal:release-portal /opt/release-portal/scripts/backup.sh
    
    # 添加到 crontab
    (sudo crontab -l 2>/dev/null; echo "0 2 * * * /opt/release-portal/scripts/backup.sh >> /opt/release-portal/logs/backup.log 2>&1") | sudo crontab -
    
    log_success "自动备份配置完成（每天凌晨 2 点）"
}

# 显示部署信息
show_deployment_info() {
    echo ""
    echo "=========================================="
    log_success "Release Portal V3 部署完成！"
    echo "=========================================="
    echo ""
    echo "服务信息："
    echo "  服务状态: $(systemctl is-active release-portal)"
    echo "  服务地址: http://localhost:5000"
    echo ""
    echo "默认账户："
    echo "  管理员: admin / admin123"
    echo "  发布者: publisher / pub123"
    echo ""
    echo "⚠️  重要提示："
    echo "  1. 请登录后立即修改默认密码"
    echo "  2. 请检查防火墙配置"
    echo "  3. 建议配置 HTTPS（使用 Let's Encrypt）"
    echo ""
    echo "常用命令："
    echo "  查看状态: sudo systemctl status release-portal"
    echo "  查看日志: sudo journalctl -u release-portal -f"
    echo "  重启服务: sudo systemctl restart release-portal"
    echo ""
    echo "文档："
    echo "  完整部署指南: DEPLOYMENT_GUIDE.md"
    echo "  用户手册: USER_MANUAL.md"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "  Release Portal V3 一键部署脚本"
    echo "=========================================="
    echo ""
    
    check_root
    detect_os
    install_system_dependencies
    create_app_user
    clone_repository
    create_virtualenv
    install_python_dependencies
    configure_environment
    create_directories
    initialize_database
    configure_systemd_service
    configure_nginx
    configure_firewall
    start_services
    configure_backup
    show_deployment_info
}

# 运行主函数
main
