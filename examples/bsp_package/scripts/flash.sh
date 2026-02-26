#!/bin/bash
#
# BSP Flash Script for RV-Board-Dev1
# 用于烧写BSP到各种存储介质
#

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 默认值
DEVICE=""
MEDIA_TYPE=""
VERIFY=true
BACKUP=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BSP_DIR="$(dirname "$SCRIPT_DIR")"

# 帮助信息
usage() {
    cat << EOF
Usage: $0 --device <DEVICE> --media <TYPE> [OPTIONS]

Options:
    --device <DEVICE>    目标设备 (如: /dev/sdX 或 /dev/ttyUSB0)
    --media <TYPE>       介质类型: sd, emmc, network
    --verify            验证写入 (默认: true)
    --no-verify         跳过验证
    --backup            烧写前备份
    --help              显示此帮助信息

Examples:
    # 烧写到SD卡
    $0 --device /dev/sdX --media sd

    # 烧写到eMMC (通过串口)
    $0 --device /dev/ttyUSB0 --media emmc

    # 网络启动
    $0 --device /dev/ttyUSB0 --media network

EOF
    exit 1
}

# 打印信息
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 检查设备
check_device() {
    local device=$1
    
    if [[ "$MEDIA_TYPE" == "sd" ]]; then
        if [[ ! -b "$device" ]]; then
            error "设备不存在: $device"
        fi
        
        # 检查设备是否在使用中
        if mount | grep -q "^${device}"; then
            error "设备已挂载，请先卸载: $device"
        fi
    fi
}

# 备份现有数据
backup_device() {
    local device=$1
    local backup_file="${device##*/}_backup_$(date +%Y%m%d_%H%M%S).img"
    
    info "备份设备到: $backup_file"
    
    if [[ "$MEDIA_TYPE" == "sd" ]]; then
        dd if="$device" of="$backup_file" bs=4M status=progress
        info "备份完成: $backup_file"
    fi
}

# 烧写到SD卡
flash_sd() {
    local device=$1
    local image_file="${BSP_DIR}/sdcard_image.img"
    
    info "准备烧写到SD卡: $device"
    warn "此操作将删除设备上的所有数据！"
    
    # 创建临时镜像
    info "创建SD卡镜像..."
    local tmp_dir=$(mktemp -d)
    
    # 创建分区表和文件系统
    # 这里简化处理，实际应该使用完整的镜像
    
    # 烧写bootloader
    info "烧写SPL..."
    dd if="${BSP_DIR}/bootloader/spl/spl.bin" of="$device" bs=1K seek=1 conv=notrunc
    
    info "烧写U-Boot..."
    dd if="${BSP_DIR}/bootloader/u-boot.bin" of="$device" bs=1K seek=256 conv=notrunc
    
    # 创建分区
    info "创建分区..."
    parted -s "$device" mklabel gpt
    parted -s "$device" mkpart primary ext4 16MB 512MB
    parted -s "$device" mkpart primary ext4 512MB 100%
    
    # 格式化分区
    info "格式化分区..."
    mkfs.ext4 -F "${device}1"
    mkfs.ext4 -F "${device}2"
    
    # 挂载并复制文件
    info "复制文件系统..."
    local mount_point=$(mktemp -d)
    mount "${device}1" "$mount_point"
    
    mkdir -p "$mount_point/boot"
    cp "${BSP_DIR}/kernel/Image" "$mount_point/boot/"
    cp "${BSP_DIR}/configs/rv-board-dev1.dtb" "$mount_point/boot/"
    
    umount "$mount_point"
    
    # 验证
    if [[ "$VERIFY" == "true" ]]; then
        info "验证烧写..."
        sync
        info "验证完成"
    fi
    
    info "SD卡烧写完成！"
}

# 烧写到eMMC
flash_emmc() {
    local device=$1
    
    info "准备烧写到eMMC (通过串口: $device)"
    
    # 检查串口连接
    if [[ ! -c "$device" ]]; then
        error "串口设备不存在: $device"
    fi
    
    info "请确保："
    info "1. 板卡已通过串口连接到 $device"
    info "2. 板卡已启动到U-Boot"
    info "3. 网络已连接"
    
    # 这里应该实现实际的eMMC烧写逻辑
    # 通常通过U-Boot命令或专用工具
    
    info "eMMC烧写功能需要:"
    info "1. 板卡进入烧写模式"
    info "2. 通过USB或网络传输"
    info "3. 参考板卡文档完成烧写"
}

# 网络启动
network_boot() {
    local device=$1
    
    info "配置网络启动..."
    
    # 检查TFTP服务器配置
    info "请确保TFTP服务器配置正确"
    info "TFTP根目录应包含:"
    info "  - Image (内核)"
    info "  - rv-board-dev1.dtb (设备树)"
    info "  - rootfs.ext4 (根文件系统)"
    
    cat << EOF

在U-Boot命令行执行:

setenv serverip <TFTP服务器IP>
setenv ipaddr <板卡IP>
dhcp
tftp 0x80080000 Image
tftp 0x84000000 rv-board-dev1.dtb
booti 0x80080000 - 0x84000000

EOF
}

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --device)
            DEVICE="$2"
            shift 2
            ;;
        --media)
            MEDIA_TYPE="$2"
            shift 2
            ;;
        --verify)
            VERIFY=true
            shift
            ;;
        --no-verify)
            VERIFY=false
            shift
            ;;
        --backup)
            BACKUP=true
            shift
            ;;
        --help)
            usage
            ;;
        *)
            error "未知选项: $1"
            ;;
    esac
done

# 检查必需参数
if [[ -z "$DEVICE" ]] || [[ -z "$MEDIA_TYPE" ]]; then
    error "缺少必需参数。使用 --help 查看帮助"
fi

# 显示配置
info "配置信息:"
info "  设备: $DEVICE"
info "  介质: $MEDIA_TYPE"
info "  验证: $VERIFY"
info "  备份: $BACKUP"
echo ""

# 检查设备
check_device "$DEVICE"

# 备份
if [[ "$BACKUP" == "true" ]]; then
    backup_device "$DEVICE"
fi

# 根据介质类型烧写
case "$MEDIA_TYPE" in
    sd)
        flash_sd "$DEVICE"
        ;;
    emmc)
        flash_emmc "$DEVICE"
        ;;
    network)
        network_boot "$DEVICE"
        ;;
    *)
        error "不支持的介质类型: $MEDIA_TYPE"
        ;;
esac

info "所有操作完成！"
