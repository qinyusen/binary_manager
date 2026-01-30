# Binary Manager

通过JSON配置文件管理二进制文件的发布和下载系统。

## 功能特点

- **发布器** - 扫描文件、打包zip、生成JSON配置
- **下载器** - 解析JSON、下载zip、校验解压
- **安全校验** - SHA256哈希验证
- **完整记录** - 详细的文件清单和元信息

## 目录结构

```
binary_manager/
├── publisher/                  # 发布器模块
│   ├── scanner.py             # 文件扫描和哈希计算
│   ├── packager.py            # 打包和JSON生成
│   └── main.py                # 发布器CLI入口
├── downloader/                # 下载器模块
│   ├── downloader.py          # HTTP下载
│   ├── verifier.py            # 校验功能
│   └── main.py                # 下载器CLI入口
├── examples/                   # 示例测试目录
│   └── my_app/                # 示例应用
└── config/                     # 配置文件
    └── schema.json            # JSON Schema验证规则

install_dependencies.sh         # Ubuntu依赖安装脚本
requirements.txt                # Python依赖列表
```

## 安装

### Ubuntu系统

运行依赖安装脚本（需要root权限）：

```bash
sudo ./install_dependencies.sh
```

### 其他系统

安装Python依赖：

```bash
pip install -r requirements.txt
```

## 使用说明

### 发布器 - 打包文件

```bash
python3 binary_manager/publisher/main.py \
  --source ./binary_manager/examples/my_app \
  --output ./releases \
  --version 1.0.0 \
  --name my_app
```

**参数说明：**
- `--source, -s`: 源目录（必需）
- `--output, -o`: 输出目录（默认：./releases）
- `--version, -v`: 版本号（默认：1.0.0）
- `--name, -n`: 包名称（默认：basedir名）
- `--url, -u`: 下载URL（可选）
- `--ignore, -i`: 忽略模式（可多次指定）

**输出：**
- `my_app_v1.0.0.zip` - 打包的zip文件
- `my_app_v1.0.0.json` - JSON配置文件

### 下载器 - 下载安装

```bash
python3 binary_manager/downloader/main.py \
  --config ./releases/my_app_v1.0.0.json \
  --output ./downloads
```

**参数说明：**
- `--config, -c`: JSON配置URL或路径（必需）
- `--output, -o`: 下载目录（默认：./downloads）
- `--verify-only`: 仅验证配置不下载
- `--extract-only`: 提取现有zip文件

### JSON配置文件示例

```json
{
  "package_name": "my_app",
  "version": "1.0.0",
  "created_at": "2026-01-30T10:00:00Z",
  "file_info": {
    "archive_name": "my_app_v1.0.0.zip",
    "size": 5242880,
    "file_count": 4,
    "hash": "sha256:abc123..."
  },
  "files": [
    {
      "path": "src/main.py",
      "size": 1024,
      "hash": "sha256:def456..."
    }
  ],
  "download_url": "http://example.com/packages/my_app_v1.0.0.zip"
}
```

## 测试

### 测试发布器

```bash
python3 binary_manager/publisher/main.py \
  -s ./binary_manager/examples/my_app \
  -o ./test_releases \
  -v 1.0.0 \
  -n test_app
```

### 测试下载器

```bash
python3 binary_manager/downloader/main.py \
  -c ./test_releases/test_app_v1.0.0.json \
  -o ./test_downloads
```

## 依赖

- Python 3.6+
- requests>=2.31.0
- jsonschema>=4.20.0
- tqdm>=4.66.0

## 许可

MIT License
