#!/bin/sh

# OpenWRT 23.05 路由器初始化脚本
# 作者: QiDianLab
# 版本: 2.0
# 日期: 2025年
# 功能: 自动配置主题

# 脚本配置
SCRIPT_VERSION="2.0"
LOG_FILE="/tmp/router_init.log"
BACKUP_DIR="/tmp/config_backup_$(date +%Y%m%d_%H%M%S)"
MAX_RETRIES=3
RETRY_DELAY=2

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 下载链接配置
BASE_URL="https://stellar.qidianlab.com/openwrt"

# 下载文件配置（sh兼容方式）
get_download_url() {
    case "$1" in
        "logo") echo "$BASE_URL/logo.png" ;;
        "footer") echo "$BASE_URL/footer.htm" ;;
        "footer_login") echo "$BASE_URL/footer_login.htm" ;;
        "sysauth") echo "$BASE_URL/sysauth.htm" ;;
        "header") echo "$BASE_URL/header.htm" ;;
        "shadowsocksr_lua") echo "$BASE_URL/shadowsocksr.lua" ;;
        "shadowsocksr_js") echo "$BASE_URL/shadowsocksr-control.js" ;;
        "shadowsocksr_css") echo "$BASE_URL/shadowsocksr-hide.css" ;;
        "banner") echo "$BASE_URL/banner.txt" ;;
        *) echo "" ;;
    esac
}

get_download_path() {
    case "$1" in
        "logo") echo "/www/luci-static/argon/img/logo.png" ;;
        "footer") echo "/usr/lib/lua/luci/view/themes/argon/footer.htm" ;;
        "footer_login") echo "/usr/lib/lua/luci/view/themes/argon/footer_login.htm" ;;
        "sysauth") echo "/usr/lib/lua/luci/view/themes/argon/sysauth.htm" ;;
        "header") echo "/usr/lib/lua/luci/view/themes/argon/header.htm" ;;
        "shadowsocksr_lua") echo "/usr/lib/lua/luci/controller/shadowsocksr.lua" ;;
        "shadowsocksr_js") echo "/www/luci-static/argon/js/shadowsocksr-control.js" ;;
        "shadowsocksr_css") echo "/www/luci-static/argon/css/shadowsocksr-hide.css" ;;
        "banner") echo "/etc/banner" ;;
        *) echo "" ;;
    esac
}

# 所有下载文件的名称列表
DOWNLOAD_FILES_LIST="logo footer footer_login sysauth header shadowsocksr_lua shadowsocksr_js shadowsocksr_css banner"

# 日志函数
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
    log "INFO" "$*"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*"
    log "SUCCESS" "$*"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*"
    log "WARNING" "$*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*"
    log "ERROR" "$*"
}

# 错误处理函数
error_exit() {
    log_error "$1"
    cleanup_on_error
    exit 1
}

# 清理函数
cleanup_on_error() {
    log_warning "脚本执行失败，正在清理临时文件..."
    # 这里可以添加清理逻辑
}

# 检查root权限
check_root() {
    [ "$(id -u)" = "0" ] || error_exit "需要root权限运行此脚本"
}

# 检查网络连接
check_network() {
    log_info "检查网络连接..."
    if ! ping -c 1 -W 5 8.8.8.8 >/dev/null 2>&1; then
        log_warning "网络连接检查失败，某些功能可能无法正常工作"
        return 1
    fi
    log_success "网络连接正常"
    return 0
}


# 带重试的下载函数
download_with_retry() {
    local url="$1"
    local output="$2"
    local retries=0
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if wget -q --no-check-certificate --timeout=30 "$url" -O "$output"; then
            log_success "下载成功: $(basename "$output")"
            return 0
        else
            retries=$(expr $retries + 1)
            log_warning "下载失败 (尝试 $retries/$MAX_RETRIES): $(basename "$output")"
            [ $retries -lt $MAX_RETRIES ] && sleep $RETRY_DELAY
        fi
    done
    
    log_error "下载失败: $(basename "$output")"
    return 1
}

# 检查目录并创建
ensure_directory() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir" || error_exit "无法创建目录: $dir"
    fi
}

# 设置系统基础配置
configure_system_basic() {
    log_info "配置系统基础设置..."
    
    # 设置主机名
    uci set system.@system[0].hostname='QiDianLab'
    
    # 设置时区
    uci set system.@system[0].timezone='CST-8'
    uci set system.@system[0].zonename='Asia/Shanghai'
    
    # 提交系统配置
    uci commit system
    
    log_success "系统基础配置完成"
}

# 下载主题文件
download_theme_files() {
    log_info "下载主题文件..."
    
    # 检查网络连接
    if ! check_network; then
        log_warning "跳过主题文件下载"
        return 1
    fi
    
    # 检查并创建目标目录
    ensure_directory "/usr/lib/lua/luci/view/themes/argon"
    ensure_directory "/www/luci-static/argon/img"
    ensure_directory "/www/luci-static/argon/js"
    ensure_directory "/www/luci-static/argon/css"
    ensure_directory "/usr/lib/lua/luci/controller"
    
    # 下载所有文件，下载前备份原文件
    log_info "备份原主题文件..."
    for name in $DOWNLOAD_FILES_LIST; do
        local path=$(get_download_path "$name")
        if [ -f "$path" ]; then
            cp "$path" "$path.bak" 2>/dev/null || log_warning "备份 $path 失败"
        fi
    done

    local failed_downloads=0
    for name in $DOWNLOAD_FILES_LIST; do
        local url=$(get_download_url "$name")
        local path=$(get_download_path "$name")
        
        if [ -n "$url" ] && [ -n "$path" ]; then
            if ! download_with_retry "$url" "$path"; then
                failed_downloads=$(expr $failed_downloads + 1)
            fi
        fi
    done
    
    if [ $failed_downloads -eq 0 ]; then
        log_success "所有主题文件下载完成"
        # 重启web服务
        /etc/init.d/uhttpd restart
    else
        log_warning "$failed_downloads 个文件下载失败"
    fi
}

# 设置系统banner
setup_banner() {
    log_info "设置系统banner..."
    
    # 尝试下载banner文件
    local url=$(get_download_url "banner")
    local output=$(get_download_path "banner")
    if [ -n "$url" ] && [ -n "$output" ]; then
        
        if download_with_retry "$url" "$output"; then
            log_success "Banner文件下载成功"
        else
            log_warning "Banner文件下载失败，使用默认设置"
            # 如果下载失败，使用简单的banner
            echo "OpenWRT Router - QiDianLab" > /etc/banner
            echo "网站: https://www.qidianlab.com | Telegram: @QiDianLab" >> /etc/banner
        fi
    else
        log_warning "未配置banner下载链接，使用默认设置"
        echo "OpenWRT Router - QiDianLab" > /etc/banner
        echo "网站: https://www.qidianlab.com | Telegram: @QiDianLab" >> /etc/banner
    fi
    
    log_success "系统banner设置完成"
}


# 主函数
main() {
    echo -e "${BLUE}QiDianLab 路由器初始化脚本 v$SCRIPT_VERSION${NC}"
    echo "=========================================="
    echo
    
    # 初始化日志
    echo "脚本开始时间: $(date)" > "$LOG_FILE"
    
    # 检查root权限
    check_root
    
    # 系统基础配置
    configure_system_basic
    
    # 下载主题文件（如果网络可用）
    if [ "$SKIP_DOWNLOAD" != "1" ]; then
        download_theme_files
    fi
    
    # 设置系统banner
    setup_banner
}

# 执行主函数
main