#!/bin/bash
#
# BSP Build Script for RV-Board-Dev1
# 用于构建BSP组件
#

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BSP_DIR="$(dirname "$SCRIPT_DIR")"
CROSS_COMPILE="${CROSS_COMPILE:-aarch64-linux-gnu-}"
ARCH="${ARCH:-arm64}"
JOBS="${JOBS:-$(nproc)}"

# 打印函数
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

# 检查工具链
check_toolchain() {
    info "检查交叉编译工具链..."
    
    if ! command -v ${CROSS_COMPILE}gcc &> /dev/null; then
        error "交叉编译器未找到: ${CROSS_COMPILE}gcc"
    fi
    
    local gcc_version=$(${CROSS_COMPILE}gcc --version | head -n1)
    info "使用工具链: $gcc_version"
}

# 构建内核
build_kernel() {
    info "构建内核..."
    
    cd "${BSP_DIR}/kernel"
    
    info "配置内核..."
    make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" rv_board_defconfig
    
    info "编译内核..."
    make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" -j"$JOBS"
    
    info "编译设备树..."
    make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" dtbs -j"$JOBS"
    
    info "内核构建完成"
    ls -lh Image arch/arm64/boot/dts/rv-board-dev1.dtb
}

# 构建U-Boot
build_uboot() {
    info "构建U-Boot..."
    
    cd "${BSP_DIR}/bootloader"
    
    info "配置U-Boot..."
    make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" rv_board_defconfig
    
    info "编译U-Boot..."
    make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" -j"$JOBS"
    
    info "编译SPL..."
    make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" spl/u-boot-spl.bin -j"$JOBS"
    
    info "U-Boot构建完成"
    ls -lh u-boot.bin spl/u-boot-spl.bin
}

# 构建根文件系统
build_rootfs() {
    info "构建根文件系统..."
    
    cd "${BSP_DIR}/rootfs"
    
    if [[ -f "build.sh" ]]; then
        info "执行构建脚本..."
        ./build.sh
    else
        warn "未找到构建脚本，使用预构建的rootfs"
    fi
    
    info "根文件系统构建完成"
    ls -lh rootfs.ext4
}

# 构建驱动
build_drivers() {
    info "构建驱动模块..."
    
    cd "${BSP_DIR}/drivers"
    
    for driver in *.c; do
        if [[ -f "$driver" ]]; then
            info "编译驱动: $driver"
            ${CROSS_COMPILE}gcc -c "$driver" -o "${driver%.c}.ko" \
                -I"${BSP_DIR}/kernel/include" \
                -I"${BSP_DIR}/kernel/arch/arm64/include"
        fi
    done
    
    info "驱动构建完成"
    ls -lh *.ko 2>/dev/null || warn "没有找到驱动文件"
}

# 创建SD卡镜像
create_sd_image() {
    info "创建SD卡镜像..."
    
    local image_file="${BSP_DIR}/sdcard_image.img"
    local image_size=2G  # 2GB
    
    info "创建镜像文件: $image_file (${image_size})"
    dd if=/dev/zero of="$image_file" bs=1 count=0 seek="$image_size"
    
    info "创建分区表..."
    parted -s "$image_file" mklabel gpt
    parted -s "$image_file" mkpart primary ext4 16MB 512MB
    parted -s "$image_file" mkpart primary ext4 512MB 100%
    
    info "设置loop设备..."
    local loop_dev=$(losetup -f)
    losetup -P "$loop_dev" "$image_file"
    
    info "格式化分区..."
    mkfs.ext4 -F "${loop_dev}p1"
    mkfs.ext4 -F "${loop_dev}p2"
    
    info "挂载分区..."
    local mount_point=$(mktemp -d)
    mount "${loop_dev}p1" "$mount_point"
    
    info "复制文件..."
    mkdir -p "$mount_point/boot"
    cp "${BSP_DIR}/kernel/Image" "$mount_point/boot/" 2>/dev/null || true
    cp "${BSP_DIR}/bootloader/u-boot.bin" "$mount_point/boot/" 2>/dev/null || true
    cp "${BSP_DIR}/configs/rv-board-dev1.dtb" "$mount_point/boot/" 2>/dev/null || true
    
    umount "$mount_point"
    losetup -d "$loop_dev"
    rm -rf "$mount_point"
    
    info "SD卡镜像创建完成: $image_file"
    ls -lh "$image_file"
}

# 生成清单
generate_manifest() {
    info "生成BSP清单..."
    
    cd "${BSP_DIR}"
    
    # 计算文件哈希
    cat > bsp_checksums.txt << EOF
# BSP文件校验和
# 生成时间: $(date)

EOF
    
    find . -type f \( -name "*.bin" -o -name "*.img" -o -name "*.ko" -o -name "*.dtb" \) \
        -exec sha256sum {} \; >> bsp_checksums.txt
    
    info "清单已生成: bsp_checksums.txt"
}

# 清理
clean() {
    info "清理构建文件..."
    
    cd "${BSP_DIR}/kernel"
    make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" clean
    
    cd "${BSP_DIR}/bootloader"
    make ARCH="$ARCH" CROSS_COMPILE="$CROSS_COMPILE" clean
    
    info "清理完成"
}

# 帮助信息
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    --all               构建所有组件 (默认)
    --kernel            仅构建内核
    --uboot             仅构建U-Boot
    --rootfs            仅构建根文件系统
    --drivers           仅构建驱动
    --image             创建SD卡镜像
    --manifest          生成清单
    --clean             清理构建文件
    --help              显示此帮助信息

Environment Variables:
    CROSS_COMPILE       交叉编译器前缀 (默认: aarch64-linux-gnu-)
    ARCH                架构 (默认: arm64)
    JOBS                并行编译任务数 (默认: nproc)

Examples:
    # 构建所有组件
    $0 --all

    # 仅构建内核
    $0 --kernel

    # 使用自定义工具链
    CROSS_COMPILE=aarch64-none-linux-gnu- $0 --all

EOF
    exit 0
}

# 主函数
main() {
    info "RV-Board-Dev1 BSP构建脚本"
    info "工具链: ${CROSS_COMPILE}"
    info "架构: $ARCH"
    info "并行任务: $JOBS"
    echo ""
    
    check_toolchain
    
    if [[ $# -eq 0 ]]; then
        set -- --all
    fi
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --all)
                build_kernel
                build_uboot
                build_rootfs
                build_drivers
                generate_manifest
                shift
                ;;
            --kernel)
                build_kernel
                shift
                ;;
            --uboot)
                build_uboot
                shift
                ;;
            --rootfs)
                build_rootfs
                shift
                ;;
            --drivers)
                build_drivers
                shift
                ;;
            --image)
                create_sd_image
                shift
                ;;
            --manifest)
                generate_manifest
                shift
                ;;
            --clean)
                clean
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
    
    info "构建完成！"
    info "查看 'bsp_checksums.txt' 获取文件校验和"
}

main "$@"
