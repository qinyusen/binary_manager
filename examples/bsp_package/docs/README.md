# RV-Board-Dev1 BSP 详细文档

## 目录

1. [概述](#概述)
2. [硬件规格](#硬件规格)
3. [软件架构](#软件架构)
4. [开发指南](#开发指南)
5. [部署指南](#部署指南)
6. [故障排除](#故障排除)
7. [高级配置](#高级配置)

## 概述

RV-Board-Dev1是一款基于ARM Cortex-A53的嵌入式开发板BSP包，提供了完整的Linux运行环境。

### 主要特性

- **高性能**: 4核ARM Cortex-A53 @ 1.2GHz
- **丰富的外设**: UART, SPI, I2C, GPIO, USB, 以太网
- **完整支持**: 内核、Bootloader、根文件系统、驱动
- **易于使用**: 提供完整的构建和部署脚本
- **开源**: 遵循GPL v2许可证

## 硬件规格

### SoC信息

| 项目 | 规格 |
|------|------|
| 型号 | RV-SOC-1000 |
| 架构 | ARM64 (aarch64) |
| CPU | 4x Cortex-A53 |
| 频率 | 1.2GHz |
| GPU | Mali-450 (可选) |

### 内存规格

| 项目 | 规格 |
|------|------|
| 类型 | DDR4 |
| 容量 | 1GB |
| 频率 | 1600MHz |
| 带宽 | 12.8GB/s |

### 存储规格

| 类型 | 容量 | 接口 |
|------|------|------|
| eMMC | 8GB | HS200 |
| SD卡槽 | 支持 | SD 3.0 |
| SPI NOR | 16MB | (可选) |

### 外设接口

#### UART (4个)
- UART0: 调试串口 (115200 8N1)
- UART1-3: 通用串口

#### SPI (2个)
- SPI0: 主模式，最高50MHz
- SPI1: 主/从模式

#### I2C (2个)
- I2C0: 100kHz / 400kHz
- I2C1: 100kHz / 400kHz

#### GPIO (20个)
- 可配置输入/输出
- 中断支持
- 复用功能

#### USB
- 2x USB 2.0 Host
- 1x USB 2.0 OTG (可选)

#### 网络
- 千兆以太网 (RGMII)
- 支持WAKE-ON-LAN

#### 显示
- HDMI 1.4
- 最大分辨率: 1920x1080 @ 60Hz

### 扩展接口

- 40针GPIO扩展头 (兼容Raspberry Pi)
- M.2接口 (WiFi/BT模块)
- CAN接口 (1路)

## 软件架构

### 系统架构图

```
┌─────────────────────────────────────────────┐
│          用户空间应用程序                   │
├─────────────────────────────────────────────┤
│          根文件系统 (Buildroot)             │
├─────────────────────────────────────────────┤
│          Linux内核 6.1.x                    │
├─────────────────────────────────────────────┤
│    设备驱动 | GPIO | SPI | I2C | UART ...  │
├─────────────────────────────────────────────┤
│          U-Boot 2023.01                    │
├─────────────────────────────────────────────┤
│          SPL (Secondary Program Loader)     │
├─────────────────────────────────────────────┤
│          硬件 (RV-SOC-1000)                │
└─────────────────────────────────────────────┘
```

### 组件版本

| 组件 | 版本 | 说明 |
|------|------|------|
| Linux内核 | 6.1.0 | 主线内核 + RT补丁 |
| U-Boot | 2023.01 | 支持SPL |
| Buildroot | 2023.02 | 根文件系统 |
| GCC | 11.3.0 | 交叉编译工具链 |

## 开发指南

### 开发环境搭建

#### 安装依赖

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    git \
    device-tree-compiler \
    u-boot-tools \
    gcc-aarch64-linux-gnu \
    qemu-user-static \
    binfmt-support
```

Fedora/RHEL:
```bash
sudo dnf install -y \
    gcc-c++ \
    git \
    dtc \
    uboot-tools \
    aarch64-linux-gnu-gcc \
    qemu-user-static
```

#### 克隆源码

```bash
git clone https://example.com/bsp/rv-board.git
cd rv-board
```

### 内核开发

#### 修改内核配置

```bash
cd kernel
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- rv_board_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- menuconfig
```

#### 常见配置选项

```
# 启用实时补丁
CONFIG_PREEMPT_RT=y

# 启用特定驱动
CONFIG_GPIO_SYSFS=y
CONFIG_SPI=y
CONFIG_I2C=y

# 网络配置
CONFIG_NET=y
CONFIG_NETWORK_FILESYSTEMS=y
```

#### 添加内核驱动

1. 在 `drivers/` 添加驱动源码
2. 创建 `Kconfig` 和 `Makefile`
3. 更新父目录的 `Kconfig` 和 `Makefile`
4. 启用驱动配置
5. 重新编译内核

### U-Boot开发

#### 修改U-Boot配置

```bash
cd bootloader
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- rv_board_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- menuconfig
```

#### 添加U-Boot命令

```c
// common/cmd_mycommand.c

#include <common.h>
#include <command.h>

static int do_mycommand(struct cmd_tbl *cmdtp, int flag, int argc,
                       char *const argv[])
{
    printf("My custom command\n");
    return 0;
}

U_BOOT_CMD(
    mycommand, 1, 1, do_mycommand,
    "My custom command",
    ""
);
```

### 根文件系统定制

#### 添加包

在 `rootfs/configs/` 修改配置:

```
# 添加Python支持
BR2_PACKAGE_PYTHON3=y

# 添加SSH服务器
BR2_PACKAGE_DROPBEAR=y

# 添加编辑器
BR2_PACKAGE_VIM=y
```

#### 添加自定义脚本

```bash
# 创建overlay目录
mkdir -p rootfs/overlay/usr/local/bin

# 添加脚本
cat > rootfs/overlay/usr/local/bin/my-script.sh << 'EOF'
#!/bin/sh
echo "Hello from RV-Board!"
EOF

chmod +x rootfs/overlay/usr/local/bin/my-script.sh
```

## 部署指南

### SD卡部署

#### 创建SD卡

1. 下载或构建BSP
2. 插入SD卡 (>=4GB)
3. 运行烧写脚本:

```bash
sudo ./scripts/flash.sh --device /dev/sdX --media sd
```

4. 将SD卡插入板卡
5. 上电启动

#### SD卡分区布局

| 分区 | 大小 | 类型 | 说明 |
|------|------|------|------|
| - | 16MB | RAW | SPL |
| - | 2MB | RAW | U-Boot |
| boot | 496MB | ext4 | 内核+设备树 |
| root | 剩余 | ext4 | 根文件系统 |

### eMMC部署

#### 通过U-Boot烧写

1. 进入U-Boot命令行
2. 配置网络:
```
setenv ipaddr 192.168.1.100
setenv serverip 192.168.1.1
```

3. 下载并烧写:
```
tftp 0x80000000 spl.bin
mmc write 0x80000000 0 100

tftp 0x80000000 u-boot.bin
mmc write 0x80000000 200 800
```

### 网络启动

#### 配置TFTP服务器

```bash
# 安装tftpd-hpa
sudo apt-get install tftpd-hpa

# 复制文件到TFTP根目录
sudo cp kernel/Image /var/lib/tftpboot/
sudo cp configs/rv-board-dev1.dtb /var/lib/tftpboot/
```

#### U-Boot网络启动命令

```bash
setenv serverip 192.168.1.1
setenv ipaddr 192.168.1.100
dhcp
tftp 0x80080000 Image
tftp 0x84000000 rv-board-dev1.dtb
booti 0x80080000 - 0x84000000
```

## 故障排除

### 启动问题

#### 串口无输出

- 检查串口连接 (TX/RX/GND)
- 确认波特率设置 (115200)
- 检查串口驱动

#### 内核启动失败

- 检查load address (应该为0x80080000)
- 验证设备树配置
- 查看内核日志 (dmesg)
- 确认bootargs参数

### 性能问题

#### CPU频率不提升

```bash
# 检查频率调节器
cat /sys/devices/system/cpu/cpufreq/policy0/scaling_governor

# 设置性能模式
echo performance > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
```

#### 内存占用过高

```bash
# 查看内存使用
free -h

# 查看进程内存占用
top
```

### 网络问题

#### 以太网不工作

- 检查网线连接
- 验证设备树PHY配置
- 查看网络状态:
```bash
ip link show
ip addr show
```

#### WiFi不工作

- 确认USB WiFi驱动加载
- 扫描网络:
```bash
iwlist wlan0 scan
```

## 高级配置

### 实时系统配置

#### 启用PREEMPT_RT

已包含在BSP中，验证实时性:

```bash
# 查看补丁状态
uname -v

# 测试延迟
cyclictest -p 80 -n -i 10000 -l 10000
```

### 安全启动

#### 配置安全启动

```bash
# 生成密钥
openssl genrsa -out private_key.pem 2048
openssl rsa -in private_key.pem -out public_key.pem -pubout

# 签名FIT镜像
./tools/mkimage -f kernel.its -k private_key.pem kernel.itb
```

### 性能优化

#### CPU性能模式

```bash
# 设置所有CPU为性能模式
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > $cpu
done
```

#### 网络优化

```bash
# 调整TCP缓冲区
echo "4096 87380 16777216" > /proc/sys/net/ipv4/tcp_rmem
echo "4096 65536 16777216" > /proc/sys/net/ipv4/tcp_wmem
```

## 技术支持

- 邮件列表: bsp@example.com
- 问题追踪: https://github.com/example/rv-board/issues
- Wiki: https://github.com/example/rv-board/wiki

## 许可证

本BSP遵循GPL v2许可证。详见 COPYING 文件。

## 更新日志

### v1.0.0 (2026-02-26)
- 初始发布
- Linux 6.1内核
- U-Boot 2023.01
- Buildroot 2023.02
- 完整驱动支持
