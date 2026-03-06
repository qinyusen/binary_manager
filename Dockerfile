# Release Portal V3 Docker 镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY release_portal/requirements_v3.txt .
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r release_portal/requirements_v3.txt && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p data storage logs backups temp && \
    chmod 755 data storage logs backups

# 初始化数据库
RUN python3 -c "from release_portal.initializer import DatabaseInitializer; DatabaseInitializer('/app/data/portal.db').initialize()"

# 暴露端口
EXPOSE 5000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# 启动命令
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--threads", "2", \
     "--timeout", "120", \
     "--access-logfile", "/app/logs/access.log", \
     "--error-logfile", "/app/logs/error.log", \
     "--log-level", "info", \
     "release_portal.presentation.web.app:app"]
