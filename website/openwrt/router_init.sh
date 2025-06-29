#!/bin/sh

# OpenWRT 23.05 路由器初始化脚本
# 作者: QiDianLab
# 版本: 2.0
# 日期: 2025年
# 功能: 自动配置主题、DNS防泄露、系统优化等

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
declare -A DOWNLOAD_FILES=(
    ["logo"]="$BASE_URL/logo.png:/www/luci-static/argon/img/logo.png"
    ["footer"]="$BASE_URL/footer.htm:/usr/lib/lua/luci/view/themes/argon/footer.htm"
    ["footer_login"]="$BASE_URL/footer_login.htm:/usr/lib/lua/luci/view/themes/argon/footer_login.htm"
    ["sysauth"]="$BASE_URL/sysauth.htm:/usr/lib/lua/luci/view/themes/argon/sysauth.htm"
    ["header"]="$BASE_URL/header.htm:/usr/lib/lua/luci/view/themes/argon/header.htm"
    ["shadowsocksr_lua"]="$BASE_URL/shadowsocksr.lua:/usr/lib/lua/luci/controller/shadowsocksr.lua"
    ["shadowsocksr_js"]="$BASE_URL/shadowsocksr-control.js:/www/luci-static/argon/js/shadowsocksr-control.js"
    ["shadowsocksr_css"]="$BASE_URL/shadowsocksr-hide.css:/www/luci-static/argon/css/shadowsocksr-hide.css"
)

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

# 创建备份
create_backup() {
    log_info "创建配置备份..."
    mkdir -p "$BACKUP_DIR"
    
    # 备份重要配置文件
    local config_files=(
        "/etc/config/system"
        "/etc/config/network"
        "/etc/config/wireless"
        "/etc/config/dhcp"
        "/etc/config/firewall"
        "/etc/config/smartdns"
        "/etc/config/shadowsocksr"
        "/etc/banner"
    )
    
    for file in "${config_files[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/" 2>/dev/null || log_warning "备份 $file 失败"
        fi
    done
    
    log_success "配置已备份到: $BACKUP_DIR"
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
            retries=$((retries + 1))
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
    
    # 下载所有文件
    local failed_downloads=0
    for name in "${!DOWNLOAD_FILES[@]}"; do
        local url_path="${DOWNLOAD_FILES[$name]}"
        local url="${url_path%:*}"
        local path="${url_path#*:}"
        
        if ! download_with_retry "$url" "$path"; then
            failed_downloads=$((failed_downloads + 1))
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
    
cat > /etc/banner <<'EOF'
   ____  _ _____  _             _           _     
  / __ \(_)  __ \(_)           | |         | |    
 | |  | |_| |  | |_  __ _ _ __ | |     __ _| |__  
 | |  | | | |  | | |/ _` | '_ \| |    / _` | '_ \ 
 | |__| | | |__| | | (_| | | | | |___| (_| | |_) |
  \___\_\_|_____/|_|\__,_|_| |_|______\__,_|_.__/ 
网站: https://www.qidianlab.com | Telegram: @QiDianLab



   
EOF
    
    log_success "系统banner设置完成"
}

# 检查必要的软件包
check_packages() {
    log_info "检查必要的软件包..."
    
    local packages="smartdns shadowsocksr ipset"
    local missing_packages=""
    
    for pkg in $packages; do
        if ! opkg list-installed | grep -q "^$pkg "; then
            missing_packages="$missing_packages $pkg"
        fi
    done
    
    if [ -n "$missing_packages" ]; then
        log_warning "缺少软件包:$missing_packages"
        log_info "请先安装: opkg update && opkg install$missing_packages"
        return 1
    fi
    
    log_success "所有必要软件包已安装"
    return 0
}

# 配置SmartDNS
configure_smartdns() {
    log_info "配置SmartDNS..."
    
    # 基础配置
    uci set smartdns.@smartdns[0].enabled='1'
    uci set smartdns.@smartdns[0].server_name='smartdns'
    uci set smartdns.@smartdns[0].port='5335'
    uci set smartdns.@smartdns[0].auto_set_dnsmasq='1'
    uci set smartdns.@smartdns[0].tcp_server='1'
    uci set smartdns.@smartdns[0].ipv6_server='1'
    uci set smartdns.@smartdns[0].bind_device='1'
    uci set smartdns.@smartdns[0].dualstack_ip_selection='1'
    uci set smartdns.@smartdns[0].serve_expired='1'
    uci set smartdns.@smartdns[0].cache_persist='1'
    uci set smartdns.@smartdns[0].resolve_local_hostnames='1'
    uci set smartdns.@smartdns[0].force_https_soa='1'
    uci set smartdns.@smartdns[0].rr_ttl_min='600'
    
    # 辅助DNS配置
    uci set smartdns.@smartdns[0].seconddns_port='6553'
    uci set smartdns.@smartdns[0].seconddns_tcp_server='1'
    uci set smartdns.@smartdns[0].seconddns_enabled='1'
    uci set smartdns.@smartdns[0].seconddns_server_group='us'
    uci set smartdns.@smartdns[0].seconddns_no_speed_check='1'
    
    # 删除现有服务器配置
    while uci -q delete smartdns.@server[0]; do :; done
    
    # 添加国内DNS服务器
    uci add smartdns server
    uci set smartdns.@server[-1].enabled='1'
    uci set smartdns.@server[-1].name='114DNS'
    uci set smartdns.@server[-1].ip='114.114.114.114'
    uci set smartdns.@server[-1].server_group='cn'
    
    uci add smartdns server
    uci set smartdns.@server[-1].enabled='1'
    uci set smartdns.@server[-1].name='AliDNS'
    uci set smartdns.@server[-1].ip='223.5.5.5'
    uci set smartdns.@server[-1].server_group='cn'
    
    # 添加国外DNS服务器（通过SOCKS5代理）
    uci add smartdns server
    uci set smartdns.@server[-1].enabled='1'
    uci set smartdns.@server[-1].name='GoogleDNS'
    uci set smartdns.@server[-1].ip='8.8.8.8'
    uci set smartdns.@server[-1].server_group='us'
    uci set smartdns.@server[-1].type='tcp'
    uci set smartdns.@server[-1].proxy='socks5://123456:123456@127.0.0.1:1080'
    
    uci add smartdns server
    uci set smartdns.@server[-1].enabled='1'
    uci set smartdns.@server[-1].name='CloudflareDNS'
    uci set smartdns.@server[-1].ip='1.1.1.1'
    uci set smartdns.@server[-1].server_group='us'
    uci set smartdns.@server[-1].type='tcp'
    uci set smartdns.@server[-1].proxy='socks5://123456:123456@127.0.0.1:1080'
    
    # 删除现有域名规则
    while uci -q delete smartdns.@domain-rule[0]; do :; done
    
    # 添加GFWList规则
    uci add smartdns domain-rule
    uci set smartdns.@domain-rule[-1].enabled='1'
    uci set smartdns.@domain-rule[-1].name='foreign_domains'
    uci set smartdns.@domain-rule[-1].domain='#gfwlist'
    uci set smartdns.@domain-rule[-1].server_group='us'
    
    uci commit smartdns
    log_success "SmartDNS配置完成"
}

# 创建域名列表
create_domain_lists() {
    log_info "创建域名列表..."
    
    ensure_directory "/etc/smartdns"
    ensure_directory "/etc/smartdns/domain-set"
    
    # 创建域名转发列表
    cat > "/etc/smartdns/domain-forwarding.list" << 'EOF'
# 国外域名转发列表
# Google服务
google.com
googleapis.com
gstatic.com
youtube.com
ytimg.com
googlevideo.com
googleusercontent.com

# 社交媒体
facebook.com
fbcdn.net
twitter.com
instagram.com
whatsapp.com
telegram.org
discord.com
reddit.com
pinterest.com
tumblr.com
linkedin.com

# 技术网站
github.com
stackoverflow.com
wikipedia.org
cloudflare.com
amazon.com
aws.amazon.com
microsoft.com
office.com
outlook.com

# 流媒体
netflix.com
spotify.com
twitch.tv
vimeo.com
soundcloud.com

# 工具网站
dropbox.com
zoom.us
slack.com

# DNS测试网站
dnsleaktest.com
whoer.com
ipleak.net
whatismyipaddress.com
ip-api.com
EOF
    
    # 创建GFWList配置
    cat > "/etc/smartdns/domain-set/gfwlist.conf" << 'EOF'
# 常见国外域名列表
google.com
googleapis.com
gstatic.com
youtube.com
ytimg.com
facebook.com
twitter.com
instagram.com
whatsapp.com
telegram.org
discord.com
reddit.com
wikipedia.org
github.com
stackoverflow.com
cloudflare.com
amazon.com
aws.amazon.com
microsoft.com
office.com
outlook.com
linkedin.com
netflix.com
spotify.com
dropbox.com
zoom.us
slack.com
twitch.tv
pinterest.com
tumblr.com
vimeo.com
soundcloud.com
dnsleaktest.com
whoer.com
ipleak.net
EOF
    
    log_success "域名列表创建完成"
}

# 配置ShadowSocksR Plus+
configure_shadowsocksr() {
    log_info "配置ShadowSocksR Plus+..."
    
    # DNS配置
    uci set shadowsocksr.@global[0].dns_mode='dns2socks'
    uci set shadowsocksr.@global[0].shunt_dns='1'
    uci set shadowsocksr.@global[0].pdnsd_enable='0'
    
    # SOCKS5代理配置
    if ! uci -q get shadowsocksr.@socks5_proxy[0] >/dev/null 2>&1; then
        uci add shadowsocksr socks5_proxy
    fi
    
    uci set shadowsocksr.@socks5_proxy[0].enabled='1'
    uci set shadowsocksr.@socks5_proxy[0].local_port='1080'
    uci set shadowsocksr.@socks5_proxy[0].socks5_auth='password'
    uci set shadowsocksr.@socks5_proxy[0].socks5_user='123456'
    uci set shadowsocksr.@socks5_proxy[0].socks5_pass='123456'
    uci set shadowsocksr.@socks5_proxy[0].socks5_mixed='1'
    
    uci commit shadowsocksr
    log_success "ShadowSocksR Plus+配置完成"
}

# 配置dnsmasq
configure_dnsmasq() {
    log_info "配置dnsmasq..."
    
    # 设置上游DNS服务器
    uci set dhcp.@dnsmasq[0].server='127.0.0.1#5335'
    
    # 配置IP集合分流（如果支持）
    if ipset list china >/dev/null 2>&1; then
        uci set dhcp.@dnsmasq[0].ipset='/cn/china'
        log_success "已配置基于IP集合的自动分流"
    else
        log_warning "未找到china IP集合，跳过IP分流配置"
    fi
    
    uci commit dhcp
    log_success "dnsmasq配置完成"
}

# 重启服务
restart_services() {
    log_info "重启相关服务..."
    
    local services=("smartdns" "shadowsocksr" "dnsmasq")
    
    for service in "${services[@]}"; do
        if /etc/init.d/$service restart; then
            log_success "$service 服务重启成功"
        else
            log_warning "$service 服务重启失败"
        fi
        sleep 2
    done
    
    log_success "服务重启完成"
}

# 验证配置
verify_config() {
    log_info "验证配置..."
    
    local errors=0
    
    # 检查服务状态
    if ! pgrep smartdns >/dev/null; then
        log_error "SmartDNS服务未运行"
        errors=$((errors + 1))
    fi
    
    if ! pgrep v2ray >/dev/null && ! pgrep xray >/dev/null; then
        log_warning "代理服务可能未运行"
    fi
    
    # 检查端口监听
    if ! netstat -tulpn 2>/dev/null | grep -q ':5335'; then
        log_error "SmartDNS端口5335未监听"
        errors=$((errors + 1))
    fi
    
    if ! netstat -tulpn 2>/dev/null | grep -q ':6553'; then
        log_error "SmartDNS辅助端口6553未监听"
        errors=$((errors + 1))
    fi
    
    # 测试DNS解析
    if command -v nslookup >/dev/null; then
        if nslookup baidu.com 127.0.0.1 >/dev/null 2>&1; then
            log_success "国内DNS解析正常"
        else
            log_error "国内DNS解析失败"
            errors=$((errors + 1))
        fi
        
        if nslookup google.com 127.0.0.1 >/dev/null 2>&1; then
            log_success "国外DNS解析正常"
        else
            log_error "国外DNS解析失败"
            errors=$((errors + 1))
        fi
    else
        log_warning "nslookup命令不可用，跳过DNS解析测试"
    fi
    
    if [ $errors -eq 0 ]; then
        log_success "配置验证通过"
        return 0
    else
        log_error "配置验证失败，发现 $errors 个错误"
        return 1
    fi
}

# 显示测试信息
show_test_info() {
    echo
    echo -e "${GREEN}=== OpenWRT 路由器初始化完成 ===${NC}"
    echo
    echo "配置信息:"
    echo "  主机名: QiDianLab"
    echo "  SmartDNS端口: 5335, 6553"
    echo "  SOCKS5代理端口: 1080"
    echo "  配置备份: $BACKUP_DIR"
    echo "  日志文件: $LOG_FILE"
    echo
    echo "测试建议:"
    echo "1. DNS解析测试:"
    echo "   nslookup baidu.com 127.0.0.1"
    echo "   nslookup google.com 127.0.0.1"
    echo
    echo "2. 在线测试:"
    echo "   https://dnsleaktest.com/"
    echo "   https://whoer.com/"
    echo
    echo "3. 服务状态检查:"
    echo "   ps | grep smartdns"
    echo "   netstat -tulpn | grep -E '(5335|6553|1080)'"
    echo
    echo "4. 日志查看:"
    echo "   logread | grep smartdns"
    echo "   cat $LOG_FILE"
    echo
    echo -e "${YELLOW}注意：如果DNS泄露测试仍显示中国DNS，请检查代理服务器连接状态${NC}"
    echo
}

# 显示帮助信息
show_help() {
    echo "OpenWRT 路由器初始化脚本 v$SCRIPT_VERSION"
    echo
    echo "用法: $0 [选项]"
    echo
    echo "选项:"
    echo "  -h, --help         显示此帮助信息"
    echo "  --verify-only      仅验证当前配置"
    echo "  --backup-only      仅备份当前配置"
    echo "  --theme-only       仅下载主题文件"
    echo "  --dns-only         仅配置DNS防泄露"
    echo "  --no-download      跳过文件下载"
    echo "  --no-verify        跳过配置验证"
    echo
    echo "功能:"
    echo "  - 自动下载并配置Argon主题"
    echo "  - 配置SmartDNS进行DNS分流"
    echo "  - 配置ShadowSocksR Plus+的DNS代理"
    echo "  - 设置国外域名通过SOCKS5代理查询DNS"
    echo "  - 创建域名转发列表和GFWList"
    echo "  - 验证配置并提供测试建议"
    echo
}

# 主函数
main() {
    echo -e "${BLUE}OpenWRT 路由器初始化脚本 v$SCRIPT_VERSION${NC}"
    echo "=========================================="
    echo
    
    # 初始化日志
    echo "脚本开始时间: $(date)" > "$LOG_FILE"
    
    # 检查root权限
    check_root
    
    # 创建配置备份
    create_backup
    
    # 系统基础配置
    configure_system_basic
    
    # 下载主题文件（如果网络可用）
    if [ "$SKIP_DOWNLOAD" != "1" ]; then
        download_theme_files
    fi
    
    # 设置系统banner
    setup_banner
    
    # DNS防泄露配置
    if [ "$DNS_ONLY" = "1" ] || [ "$THEME_ONLY" != "1" ]; then
        if check_packages; then
            configure_smartdns
            create_domain_lists
            configure_shadowsocksr
            configure_dnsmasq
            restart_services
        else
            log_warning "跳过DNS配置，因为缺少必要软件包"
        fi
    fi
    
    # 验证配置
    if [ "$SKIP_VERIFY" != "1" ]; then
        if verify_config; then
            show_test_info
            log_success "路由器初始化完成！"
        else
            log_error "配置验证失败，请检查日志: $LOG_FILE"
            exit 1
        fi
    fi
}

# 解析命令行参数
while [ $# -gt 0 ]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        --verify-only)
            check_root
            verify_config
            exit $?
            ;;
        --backup-only)
            check_root
            create_backup
            exit 0
            ;;
        --theme-only)
            THEME_ONLY=1
            ;;
        --dns-only)
            DNS_ONLY=1
            ;;
        --no-download)
            SKIP_DOWNLOAD=1
            ;;
        --no-verify)
            SKIP_VERIFY=1
            ;;
        *)
            echo "未知选项: $1"
            echo "使用 --help 查看帮助信息"
            exit 1
            ;;
    esac
    shift
done

# 执行主函数
main