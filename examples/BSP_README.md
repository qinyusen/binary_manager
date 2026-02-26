# Embedded Linux BSP Examples

本目录包含嵌入式Linux BSP（板级支持包）的发布示例。

## BSP包结构

```
bsp_package/
├── README.md                # 主文档
├── board_info.json          # 板卡信息
├── bsp_manifest.json        # BSP清单
├── kernel/                  # 内核文件
│   ├── README.md
│   ├── Image                # 内核镜像
│   └── configs/             # 内核配置
├── bootloader/              # Bootloader
│   ├── README.md
│   ├── u-boot.bin           # U-Boot二进制
│   └── spl/                 # SPL文件
├── rootfs/                  # 根文件系统
│   └── rootfs.ext4          # ext4格式
├── drivers/                 # 驱动模块
│   ├── gpio_driver.ko
│   └── spi_driver.ko
├── scripts/                 # 脚本
│   ├── flash.sh             # 烧写脚本
│   └── build.sh             # 构建脚本
├── configs/                 # 配置文件
│   └── rv-board-dev1.dts    # 设备树
└── docs/                    # 文档
    └── README.md            # 详细文档
```

## 快速开始

### 1. 发布BSP包

```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./examples/bsp_package \
    --package-name rv_board_bsp \
    --version 1.0.0 \
    --description "RV-Board-Dev1 Embedded Linux BSP"
```

### 2. 下载BSP包

```bash
python3 -m binary_manager_v2.cli.main download \
    --package-name rv_board_bsp \
    --version 1.0.0 \
    --output ./installed_bsps
```

### 3. 烧写到SD卡

```bash
cd installed_bsps/rv_board_bsp_v1.0.0
sudo ./scripts/flash.sh --device /dev/sdX --media sd
```

### 4. 查看BSP信息

```bash
cat board_info.json
cat bsp_manifest.json
```

## BSP特性

### 硬件支持

- **SoC**: RV-SOC-1000 (ARM Cortex-A53, 4核@1.2GHz)
- **内存**: 1GB DDR4
- **存储**: 8GB eMMC + SD卡槽
- **网络**: 千兆以太网
- **外设**: 4xUART, 2xSPI, 2xI2C, 20xGPIO, USB 2.0, HDMI

### 软件组件

- **内核**: Linux 6.1 with PREEMPT_RT
- **Bootloader**: U-Boot 2023.01 with SPL
- **根文件系统**: Buildroot 2023.02
- **驱动**: GPIO, SPI, I2C, UART, Ethernet等

## 构建BSP

### 准备开发环境

```bash
# 安装交叉编译工具链
sudo apt-get install gcc-aarch64-linux-gnu

# 安装其他依赖
sudo apt-get install build-essential git u-boot-tools device-tree-compiler
```

### 构建所有组件

```bash
cd bsp_package
./scripts/build.sh --all
```

### 构建单个组件

```bash
# 仅构建内核
./scripts/build.sh --kernel

# 仅构建U-Boot
./scripts/build.sh --uboot

# 仅构建根文件系统
./scripts/build.sh --rootfs
```

## 部署选项

### SD卡部署

适用于开发和原型验证:

```bash
# 烧写到SD卡
sudo ./scripts/flash.sh --device /dev/sdX --media sd

# 插入SD卡到板卡
# 上电启动
```

### eMMC部署

适用于生产环境:

```bash
# 通过串口连接
# 进入U-Boot命令行
# 执行烧写命令
sudo ./scripts/flash.sh --device /dev/ttyUSB0 --media emmc
```

### 网络启动

适用于批量部署:

```bash
# 配置TFTP服务器
# 在U-Boot中执行网络启动
sudo ./scripts/flash.sh --device /dev/ttyUSB0 --media network
```

## 版本管理

### 版本号规范

```
MAJOR.MINOR.PATCH

MAJOR    - 重大架构变更
MINOR    - 新功能或重要改进
PATCH    - Bug修复或小改进
```

### 示例

- `1.0.0` - 初始发布
- `1.1.0` - 添加新驱动
- `1.1.1` - 修复内核bug
- `2.0.0` - 内核大版本升级

## 使用场景

### 1. 嵌入式系统开发

```bash
# 下载BSP
python3 -m binary_manager_v2.cli.main download \
    --package-name rv_board_bsp --version 1.0.0

# 烧写到SD卡进行开发
sudo ./scripts/flash.sh --device /dev/sdX --media sd

# 连接串口进行调试
picocom -b 115200 /dev/ttyUSB0
```

### 2. 产品批量部署

```bash
# 创建包组
python3 -m binary_manager_v2.cli.main group create \
    --group-name production_environment \
    --version 1.0.0 \
    --packages "rv_board_bsp:1.0.0,application_firmware:2.0.0"

# 导出配置
python3 -m binary_manager_v2.cli.main group export \
    --group-name production_environment \
    --version 1.0.0 \
    --output ./production

# 在生产线上使用配置部署
```

### 3. CI/CD集成

```bash
# 在CI流程中发布新版本
./scripts/build.sh --all

python3 -m binary_manager_v2.cli.main publish \
    --source ./bsp_package \
    --package-name rv_board_bsp \
    --version ${CI_COMMIT_TAG}

# 自动化测试
python3 -m binary_manager_v2.cli.main download \
    --package-name rv_board_bsp \
    --version ${CI_COMMIT_TAG}
```

## 自定义BSP

### 添加自定义驱动

1. 在 `drivers/` 添加驱动源码
2. 更新 `bsp_manifest.json`
3. 重新构建: `./scripts/build.sh --drivers`
4. 发布新版本

### 修改内核配置

1. 编辑 `kernel/configs/rv_board_defconfig`
2. 重新构建: `./scripts/build.sh --kernel`
3. 测试验证
4. 发布新版本

### 更新根文件系统

1. 在 `rootfs/` 添加文件或修改配置
2. 重新构建: `./scripts/build.sh --rootfs`
3. 验证功能
4. 发布新版本

## 故障排除

### 发布失败

- 检查目录结构
- 验证manifest文件格式
- 确认文件权限

### 烧写失败

- 检查设备权限
- 验证设备路径
- 确认文件完整性

### 启动失败

- 检查串口输出
- 验证bootloader
- 查看内核日志
- 检查设备树

## 相关资源

- [BSP详细文档](docs/README.md)
- [内核文档](kernel/README.md)
- [Bootloader文档](bootloader/README.md)
- [烧写脚本使用](scripts/README.md)
- [Binary Manager文档](../../BINARY_MANAGER_V2.md)

## 许可证

本BSP示例遵循GPL v2许可证。

## 贡献

欢迎提交改进和Bug修复！

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 创建Pull Request
