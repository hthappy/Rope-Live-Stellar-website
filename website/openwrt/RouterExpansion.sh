#!/bin/sh

# OpenWRT Extroot 自动扩容脚本
# 适用于已格式化的ext4 USB设备

USB_DEVICE="/dev/sda"
USB_PARTITION="/dev/sda1"
TEMP_MOUNT="/mnt/usb_setup"

log() {
    echo "[$(date '+%H:%M:%S')] $1"
}

error_exit() {
    echo "错误: $1" >&2
    exit 1
}

# 检查root权限
check_root() {
    [ "$(id -u)" = "0" ] || error_exit "需要root权限运行此脚本"
}

# 卸载现有分区
unmount_partitions() {
    log "卸载现有分区..."
    
    for part in "${USB_DEVICE}"*; do
        if [ -b "$part" ] && [ "$part" != "$USB_DEVICE" ]; then
            if mount | grep -q "$part"; then
                log "卸载: $part"
                umount "$part" 2>/dev/null || true
            fi
        fi
    done
}

# 准备overlay结构
prepare_overlay() {
    log "准备overlay结构..."
    
    mkdir -p "$TEMP_MOUNT"
    
    mount "$USB_PARTITION" "$TEMP_MOUNT" || error_exit "挂载失败"
    
    if [ -d "/overlay/upper" ] && [ -d "/overlay/work" ]; then
        log "复制现有overlay内容..."
        cp -r /overlay/* "$TEMP_MOUNT/" 2>/dev/null || {
            mkdir -p "$TEMP_MOUNT/upper" "$TEMP_MOUNT/work"
        }
    else
        mkdir -p "$TEMP_MOUNT/upper" "$TEMP_MOUNT/work"
    fi
    
    umount "$TEMP_MOUNT"
    rmdir "$TEMP_MOUNT"
    
    log "overlay结构准备完成"
}

# 配置fstab
configure_fstab() {
    log "配置fstab..."
    
    if [ -f "/etc/config/fstab" ]; then
        cp "/etc/config/fstab" "/etc/config/fstab.backup"
    fi
    
    cat > "/etc/config/fstab" << FSTAB_EOF
config global
	option anon_swap '0'
	option anon_mount '0'
	option auto_swap '1'
	option auto_mount '1'
	option delay_root '5'
	option check_fs '0'

config mount
	option target '/overlay'
	option device '$USB_PARTITION'
	option fstype 'ext4'
	option options 'rw,relatime'
	option enabled '1'
	option is_rootfs '1'
FSTAB_EOF
    
    log "fstab配置完成"
}

# 显示结果
show_result() {
    echo
    echo "=== 扩容配置完成 ==="
    echo "USB设备: $USB_DEVICE"
    echo "分区: $USB_PARTITION"
    echo "文件系统: ext4"
    echo
    echo "请重启路由器以激活extroot:"
    echo "  reboot"
    echo
    echo "重启后检查结果:"
    echo "  df -h"
    echo
}

# 主程序
main() {
    echo "OpenWRT Extroot 自动扩容脚本"
    echo "=============================="
    # 更新软件包
    opkg update
    # 安装必要软件包
    opkg install kmod-usb-storage block-mount kmod-fs-ext4 e2fsprogs
    check_root
    
    log "开始扩容过程..."
    
    unmount_partitions
    prepare_overlay
    configure_fstab
    
    show_result
}

main