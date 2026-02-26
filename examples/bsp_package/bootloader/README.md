# U-Boot Bootloader for RV-Board-Dev1

## Bootloader信息
- **名称**: U-Boot
- **版本**: 2023.01
- **架构**: ARM64 (aarch64)
- **配置文件**: configs/rv_board_defconfig
- **SPL**: 支持

## U-Boot特性

### 启动流程
1. **SPL (Secondary Program Loader)**
   - 初始化DDR内存
   - 加载主U-Boot
   - 最小的初始化代码 (~40KB)

2. **U-Boot Proper**
   - 完整的硬件初始化
   - 设备树解析
   - 启动内核
   - 提供命令行界面

### 支持的启动介质
- eMMC (默认)
- SD卡
- 网络启动 (TFTP/NFS)
- USB启动
- SPI NOR Flash

### 网络功能
- TFTP - 下载文件
- NFS - 网络根文件系统
- HTTP - 通过HTTP下载
- DHCP - 自动IP配置

### 安全特性
- FIT镜像签名验证
- 安全启动支持 (可选)
- TrustZone支持

## 配置选项

### 默认配置
```bash
cat configs/rv_board_defconfig
```

### 关键配置项
```
CONFIG_ARM64=y
CONFIG_TARGET_RV_BOARD=y
CONFIG_SPL=y
CONFIG_SPL_BUILD=y
CONFIG_NR_DRAM_BANKS=1
CONFIG_DM=y
CONFIG_DM_SERIAL=y
CONFIG_DM_GPIO=y
CONFIG_OF_CONTROL=y
CONFIG_OF_SEPARATE=y
CONFIG_ENV_IS_IN_MMC=y
CONFIG_BOOTDELAY=3
```

## 编译U-Boot

### 准备工作
```bash
# 安装工具链
sudo apt-get install gcc-aarch64-linux-gnu device-tree-compiler

# 设置环境变量
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
```

### 编译步骤
```bash
# 配置U-Boot
make rv_board_defconfig

# 编译
make -j$(nproc)

# 编译SPL
make spl/u-boot-spl.bin
```

### 输出文件
- `u-boot.bin` - 主U-Boot二进制
- `spl/u-boot-spl.bin` - SPL二进制
- `u-boot.dtb` - U-Boot设备树
- `u-boot.map` - 符号表

## U-Boot命令

### 常用命令

#### 环境变量
```bash
printenv              # 打印所有环境变量
setenv bootargs '...' # 设置环境变量
saveenv              # 保存环境变量
```

#### 启动相关
```bash
boot                   # 启动内核
bootm <addr>          # 从指定地址启动
bootz <addr>          # 启动zImage内核
```

#### 文件操作
```bash
fatls mmc 0:1 /       # 列出FAT文件
fatload mmc 0:1 <addr> <file>  # 加载文件
```

#### 网络操作
```bash
dhcp                  # 获取IP地址
tftp <addr> <file>    # 通过TFTP下载文件
ping <addr>           # 测试网络连接
```

#### 硬件信息
```bash
bdinfo               # 板卡信息
mtest <start> <end>  # 内存测试
```

### 环境变量配置

#### 默认启动命令
```bash
setenv bootcmd 'mmc dev 0; fatload mmc 0:1 0x80080000 Image; fatload mmc 0:1 0x84000000 rv-board-dev1.dtb; booti 0x80080000 - 0x84000000'
saveenv
```

#### 网络启动
```bash
setenv bootcmd 'dhcp; tftp 0x80080000 Image; tftp 0x84000000 rv-board-dev1.dtb; booti 0x80080000 - 0x84000000'
saveenv
```

#### 内核参数
```bash
setenv bootargs 'console=ttyS0,115200 root=/dev/mmcblk0p2 rootfstype=ext4 rootwait'
saveenv
```

## 启动流程详解

### eMMC启动流程
1. ROM代码加载SPL
2. SPL初始化DDR并加载U-Boot
3. U-Boot初始化硬件
4. U-Boot加载设备树
5. U-Boot加载内核镜像
6. U-Boot跳转到内核

### SD卡启动流程
1. ROM代码从SD卡加载SPL
2. SPL初始化DDR并加载U-Boot
3. 后续流程同eMMC

### 网络启动流程
1. ROM代码从eMMC启动
2. U-Boot通过DHCP获取IP
3. U-Boot通过TFTP下载内核
4. 后续流程同eMMC

## 设备树

### U-Boot设备树
- `configs/rv-board-dev1-u-boot.dts` - U-Boot专用设备树
- 包含U-Boot特定的配置
- 节点: chosen, memory, uart, gpio等

### 设备树编译
```bash
dtc -I dts -O dtb -o rv-board-dev1-u-boot.dtb configs/rv-board-dev1-u-boot.dts
```

## 脚本支持

### 自动化脚本
详见 `scripts/flash.sh`

```bash
# 烧写到SD卡
./scripts/flash.sh --device /dev/sdX --media sd

# 烧写到eMMC
./scripts/flash.sh --device /dev/ttyUSB0 --media emmc
```

## 调试

### 串口调试
- 波特率: 115200
- 数据位: 8
- 停止位: 1
- 校验位: None

### 常见调试命令
```bash
# 打印调试信息
printenv

# 查看内存映射
bdinfo

# 测试内存
mtest 0x80000000 0x84000000

# 启动时的详细输出
setenv debug 1
```

## 常见问题

### U-Boot无法启动
1. 检查串口连接
2. 验证二进制文件完整性
3. 检查load address设置
4. 查看SPL输出

### 无法加载内核
1. 检查分区表
2. 验证内核镜像存在
3. 检查文件系统类型
4. 查看加载地址

### 网络启动失败
1. 检查网线连接
2. 验证DHCP服务器
3. 检查TFTP服务器配置
4. 验证IP地址

## 性能优化

### 启动速度优化
1. 减少bootdelay
2. 禁用不必要的驱动
3. 使用优化的设备树

### 内存优化
1. 调整malloc pool大小
2. 优化栈大小
3. 使用LTO编译

## 相关链接
- [U-Boot官方文档](https://www.denx.de/wiki/U-Boot)
- [U-Boot命令参考](https://www.denx.de/wiki/U-Boot/Documentation)
