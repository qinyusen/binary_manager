# Release Portal V3 Docker 部署指南

## 快速开始

### 1. 使用 Docker Compose（推荐）

```bash
# 生成安全密钥
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 创建 .env 文件
cat > .env << EOF
RELEASE_PORTAL_SECRET=$SECRET_KEY
EOF

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 初始化管理员账户
docker-compose exec web python3 << EOF
from release_portal.initializer import create_container
container = create_container()
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

访问：http://localhost:5000

### 2. 使用 Docker 命令

```bash
# 构建镜像
docker build -t release-portal:v3 .

# 运行容器
docker run -d \
  --name release-portal \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/storage:/app/storage \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/backups:/app/backups \
  -e RELEASE_PORTAL_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))") \
  release-portal:v3

# 查看日志
docker logs -f release-portal

# 进入容器
docker exec -it release-portal bash
```

### 3. 使用 Nginx 反向代理

```bash
# 启动服务（包含 Nginx）
docker-compose --profile with-nginx up -d

# 配置 SSL 证书
mkdir -p nginx/ssl
# 将证书文件复制到 nginx/ssl/ 目录
# 修改 nginx/nginx.conf 中的 SSL 配置
```

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `RELEASE_PORTAL_DB` | `/app/data/portal.db` | 数据库路径 |
| `RELEASE_PORTAL_SECRET` | - | JWT 密钥（必须设置） |
| `RELEASE_PORTAL_TOKEN_EXPIRY_HOURS` | `24` | Token 过期时间 |
| `FLASK_ENV` | `production` | Flask 环境 |
| `RELEASE_PORTAL_STORAGE_DIR` | `/app/storage` | 存储目录 |
| `RELEASE_PORTAL_MAX_UPLOAD_SIZE` | `500` | 最大上传大小（MB） |
| `RELEASE_PORTAL_LOG_LEVEL` | `INFO` | 日志级别 |

## 数据持久化

使用 Docker Volume 或绑定挂载：

```yaml
volumes:
  # 方式 1: Docker Volume
  - data:/app/data
  
  # 方式 2: 绑定挂载
  - ./data:/app/data
```

## 备份和恢复

### 备份

```bash
# 备份数据库
docker exec release-portal \
  sqlite3 /app/data/portal.db ".backup '/app/backups/backup_$(date +%Y%m%d).db'"

# 备份存储文件
docker exec release-portal \
  tar -czf /app/backups/storage_$(date +%Y%m%d).tar.gz -C /app/storage .
```

### 恢复

```bash
# 恢复数据库
docker cp backup.db release-portal:/app/data/portal.db

# 重启容器
docker-compose restart
```

## 监控和日志

### 查看日志

```bash
# 查看所有日志
docker-compose logs

# 查看特定服务日志
docker-compose logs web

# 实时查看日志
docker-compose logs -f

# 查看应用日志
docker exec release-portal tail -f /app/logs/app.log
```

### 健康检查

```bash
# 检查容器健康状态
docker ps
docker inspect release-portal | grep -A 5 Health

# 手动健康检查
curl http://localhost:5000/health
```

## 性能优化

### 调整 Worker 数量

```dockerfile
CMD ["gunicorn", \
     "--workers", "8", \
     "--threads", "2", \
     ...]
```

公式：`workers = (2 × CPU核心数) + 1`

### 使用多阶段构建

```dockerfile
# 构建阶段
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements*.txt .
RUN pip install --user -r requirements.txt

# 运行阶段
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["gunicorn", ...]
```

## 安全加固

### 1. 使用非 root 用户

```dockerfile
RUN useradd -r -s /bin/false portal
USER portal
```

### 2. 只读文件系统

```yaml
services:
  web:
    read_only: true
    tmpfs:
      - /tmp
```

### 3. 资源限制

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 故障排查

### 容器无法启动

```bash
# 查看详细日志
docker-compose logs web

# 检查容器状态
docker ps -a

# 进入容器调试
docker-compose run --rm web bash
```

### 数据库锁定

```bash
# 停止容器
docker-compose down

# 检查数据库
docker-compose run --rm web \
  sqlite3 /app/data/portal.db "PRAGMA integrity_check;"

# 重启容器
docker-compose up -d
```

### 性能问题

```bash
# 查看容器资源使用
docker stats release-portal

# 调整资源配置
docker-compose up -d --scale web=3
```

## 更新和维护

### 更新应用

```bash
# 停止容器
docker-compose down

# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 启动容器
docker-compose up -d
```

### 清理旧镜像

```bash
# 删除未使用的镜像
docker image prune -a

# 删除未使用的容器
docker container prune

# 删除未使用的卷
docker volume prune
```

## 生产环境建议

1. **使用多节点部署**：使用 Docker Swarm 或 Kubernetes
2. **配置监控**：使用 Prometheus + Grafana
3. **日志聚合**：使用 ELK Stack 或 Loki
4. **自动备份**：配置定时任务
5. **使用 HTTPS**：配置 SSL 证书
6. **限制资源**：设置 CPU 和内存限制
7. **安全扫描**：定期扫描镜像漏洞

## 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Gunicorn 文档](https://docs.gunicorn.org/)
- [Flask 部署指南](https://flask.palletsprojects.com/en/latest/deploying/)

---

**问题反馈**: [GitHub Issues](https://github.com/qinyusen/release_system/issues)
