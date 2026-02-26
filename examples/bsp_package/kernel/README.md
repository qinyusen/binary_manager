# RV-Board-Dev1 Linux Kernel

## 内核信息
- **版本**: 6.1.0
- **架构**: ARM64 (aarch64)
- **配置文件**: configs/rv_board_defconfig
- **镜像**: Image (压缩的内核镜像)

## 内核特性

### CPU支持
- SMP (对称多处理) - 4核
- CPU频率调节
- CPU空闲管理
- CPU热插拔（实验性）

### 内存管理
- 1GB DDR4支持
- 内存热插拔（实验性）
- 内存压缩（zRAM）

### 设备支持
- GPIO驱动
- SPI控制器驱动
- I2C控制器驱动
- UART驱动（4个串口）
- USB 2.0 Host控制器
- 以太网PHY驱动
- HDMI显示驱动

### 文件系统
- ext4 (主文件系统)
- jffs2 (MTD设备)
- squashfs (只读压缩)
- tmpfs (临时文件系统)
- proc/sysfs/debugfs (虚拟文件系统)

### 网络协议栈
- TCP/IP完整支持
- IPv6支持
- WiFi (通过USB dongle)
- 蓝牙 (可选)

### 实时特性
- PREEMPT_RT补丁
- 高精度定时器
- RT调度器支持

## 配置选项

### 默认配置
```bash
# 查看当前配置
cat configs/rv_board_defconfig
```

### 重新配置内核
```bash
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- rv_board_defconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- menuconfig
make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- savedefconfig
```

## 编译内核

### 准备工作
```bash
# 安装交叉编译工具
sudo apt-get install gcc-aarch64-linux-gnu

# 设置环境变量
export ARCH=arm64
export CROSS_COMPILE=aarch64-linux-gnu-
```

### 编译步骤
```bash
# 配置内核
make rv_board_defconfig

# 编译内核
make -j$(nproc)

# 编译设备树
make dtbs

# 编译模块
make modules
```

### 输出文件
- `Image` - 内核镜像
- `System.map` - 符号表
- `vmlinux` - 未压缩的ELF内核
- `.config` - 当前配置
- `arch/arm64/boot/dts/*.dtb` - 设备树二进制文件

## 内核模块

### 查看已加载模块
```bash
lsmod
```

### 加载模块
```bash
insmod gpio_driver.ko
modprobe spi_driver
```

### 卸载模块
```bash
rmmod gpio_driver
```

### 模块配置
模块配置文件位置: `/etc/modules-load.d/`

## 设备树

### 主设备树
- `configs/rv-board-dev1.dts` - 主板卡设备树

### Overlay设备树
- `configs/rv-board-dev1-lcd.dtbo` - LCD显示overlay
- `configs/rv-board-dev1-wifi.dtbo` - WiFi模块overlay

### 编译设备树
```bash
dtc -I dts -O dtb -o rv-board-dev1.dtb configs/rv-board-dev1.dts
```

## 性能优化

### CPU频率调节
```bash
# 查看可用的频率调节器
cat /sys/devices/system/cpu/cpufreq/policy0/scaling_available_governors

# 设置性能模式
echo performance > /sys/devices/system/cpu/cpufreq/policy0/scaling_governor
```

### 内存优化
```bash
# 启用zRAM
echo zram > /etc/modules-load.d/zram.conf
```

## 调试

### 内核日志
```bash
dmesg
dmesg | grep -i error
dmesg | tail -100  # 查看最近的日志
```

### 串口调试
- 波特率: 115200
- 数据位: 8
- 停止位: 1
- 校验位: None

### 性能分析
```bash
# CPU性能
perf top

# 延迟分析
cyclictest -p 80 -n -i 10000 -l 10000
```

## 常见问题

### 内核启动失败
1. 检查内核镜像完整性
2. 验证设备树配置
3. 查看串口输出
4. 检查load address设置

### 驱动加载失败
1. 检查内核配置
2. 验证模块版本匹配
3. 查看dmesg日志
4. 确认设备树节点配置

### 性能问题
1. 检查CPU频率调节器设置
2. 启用性能模式
3. 检查中断负载
4. 使用perf工具分析

## 相关链接
- [Linux内核文档](https://www.kernel.org/doc/html/latest/)
- [设备树规范](https://www.devicetree.org/)
- [ARM64内核文档](https://www.kernel.org/doc/html/latest/arch/arm64/)
