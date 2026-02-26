# Embedded Linux BSP Package

一个完整的嵌入式Linux BSP（板级支持包）示例，展示Binary Manager在处理复杂嵌入式项目时的能力。

## BSP信息

- **板卡名称**: RV-Board-Dev1
- **架构**: ARM64 (aarch64)
- **SoC**: 虚构的RV-SOC-1000
- **内核版本**: Linux 6.1.x
- **Bootloader**: U-Boot 2023.01
- **根文件系统**: Buildroot 2023.02

## 目录结构

```
bsp_package/
├── README.md              # 本文件
├── board_info.json        # 板卡信息配置
├── bsp_manifest.json      # BSP清单文件
├── kernel/                # 内核相关文件
│   ├── Image              # 内核镜像
│   ├── modules/           # 内核模块
│   └── configs/           # 内核配置
├── bootloader/            # 引导加载程序
│   ├── u-boot.bin         # U-Boot二进制
│   └── spl/              # SPL文件
├── rootfs/               # 根文件系统
│   ├── rootfs.ext4       # ext4格式根文件系统
│   └── overlays/         # 设备树overlay
├── drivers/              # 板卡特定驱动
│   ├── gpio_driver.ko
│   └── spi_driver.ko
├── scripts/              # 构建和部署脚本
│   ├── flash.sh         # 烧写脚本
│   └── build.sh         # 构建脚本
├── configs/              # 配置文件
│   └── board.dts        # 设备树源文件
└── docs/                 # 文档
    ├── README.md        # 详细文档
    └── schematics.pdf   # 原理图（链接）
```

## 功能特性

### 硬件支持

- **CPU**: 四核 ARM Cortex-A53 @ 1.2GHz
- **内存**: 1GB DDR4
- **存储**: 8GB eMMC + SD卡槽
- **网络**: 千兆以太网
- **外设**:
  - 4x UART
  - 2x SPI
  - 2x I2C
  - 20x GPIO
  - USB 2.0 Host x 2
  - HDMI输出

### 软件特性

- **内核特性**:
  - 实时补丁 (PREEMPT_RT)
  - 设备树支持
  - 多种文件系统支持 (ext4, jffs2, squashfs)
  - 网络协议栈完整支持

- **Bootloader**:
  - U-Boot with SPL
  - 支持从eMMC/SD启动
  - 网络启动支持
  - UEFI支持（可选）

- **根文件系统**:
  - Buildroot构建
  - 包含常用工具和库
  - 支持Python开发
  - 包含SSH服务器

## 快速开始

### 1. 下载BSP包

```bash
python3 -m binary_manager_v2.cli.main download \
    --package-name rv_board_bsp \
    --version 1.0.0 \
    --output ./installed_bsps
```

### 2. 查看BSP信息

```bash
cd installed_bsps/rv_board_bsp_v1.0.0
cat board_info.json
```

### 3. 烧写到SD卡

```bash
# 插入SD卡
sudo ./scripts/flash.sh --device /dev/sdX --media sd
```

### 4. 烧写到eMMC

```bash
# 通过串口连接到板卡
# 进入U-Boot命令行
# 通过USB或网络烧写
sudo ./scripts/flash.sh --device /dev/ttyUSB0 --media emmc
```

## 发布新版本

### 开发环境准备

```bash
# 安装交叉编译工具链
sudo apt-get install gcc-aarch64-linux-gnu

# 安装依赖
sudo apt-get install build-essential git u-boot-tools device-tree-compiler
```

### 构建BSP

```bash
cd bsp_package
./scripts/build.sh --all
```

### 发布BSP包

```bash
python3 -m binary_manager_v2.cli.main publish \
    --source ./bsp_package \
    --package-name rv_board_bsp \
    --version 1.0.0 \
    --description "RV-Board-Dev1 BSP v1.0.0"
```

## 版本管理

### BSP版本规范

版本号格式: `MAJOR.MINOR.PATCH`

- **MAJOR**: 重大架构变更或不兼容更新
- **MINOR**: 新功能或重要改进
- **PATCH**: Bug修复或小改进

### 示例

- `1.0.0` - 初始发布版本
- `1.1.0` - 添加新驱动支持
- `1.1.1` - 修复内核崩溃bug
- `2.0.0` - 升级到Linux 6.x内核

## 配置说明

### 内核配置

```bash
cd kernel
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- menuconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc)
```

### U-Boot配置

```bash
cd bootloader
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- rv_board_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -j$(nproc)
```

### 根文件系统配置

```bash
cd rootfs
make rv_board_defconfig
make
```

## 驱动开发

### 添加新驱动

1. 在 `drivers/` 目录添加驱动源码
2. 更新 `kernel/configs/` 中的配置
3. 重新构建内核
4. 发布新版本BSP

### 示例驱动

```bash
# 编译GPIO驱动
make -C drivers M=$(pwd) modules

# 加载驱动
insmod drivers/gpio_driver.ko
```

## 故障排除

### 启动失败

1. 检查串口输出
2. 验证bootloader是否正确加载
3. 检查设备树配置

### 网络问题

1. 检查设备树中的网络配置
2. 验证PHY驱动是否加载
3. 检查引脚复用配置

### 性能优化

1. 启用CPU频率调节
2. 优化内存分配
3. 使用DMA传输

## 支持的板卡

- **RV-Board-Dev1** - 开发板（主要支持）
- **RV-Board-Pro** - 专业版（计划中）
- **RV-Board-Lite** - 精简版（计划中）

## 技术支持

- **文档**: `docs/README.md`
- **问题反馈**: 通过Git Issues提交
- **技术讨论**: 参考项目Wiki

## 许可证

本BSP包遵循GPL v2许可证。

## 更新日志

### v1.0.0 (2026-02-26)
- ✅ 初始发布
- ✅ Linux 6.1内核支持
- ✅ U-Boot 2023.01
- ✅ Buildroot 2023.02根文件系统
- ✅ 完整的外设驱动支持
- ✅ 烧写和部署脚本

## 贡献

欢迎提交改进和bug修复！

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 相关链接

- [Binary Manager文档](../../BINARY_MANAGER_V2.md)
- [快速开始指南](../../V2_QUICKSTART.md)
- [示例程序](../)
