#!/bin/bash

# VMess住宅IP代理配置验证脚本
# 版本: 1.0
# 作者: AI Assistant
# 功能: 验证VMess住宅IP代理配置是否正确

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查ShadowsocksR Plus+配置
check_ssr_config() {
    log_info "检查ShadowsocksR Plus+配置..."
    
    # 检查是否安装
    if ! opkg list-installed | grep -q shadowsocksr; then
        log_error "ShadowsocksR Plus+未安装"
        return 1
    fi
    
    # 检查配置文件
    if [ ! -f "/etc/config/shadowsocksr" ]; then
        log_error "ShadowsocksR配置文件不存在"
        return 1
    fi
    
    log_success "ShadowsocksR Plus+已安装"
    return 0
}

# 检查VMess节点配置
check_vmess_node() {
    log_info "检查VMess住宅IP节点配置..."
    
    # 查找VMess节点
    local vmess_found=false
    local node_count=$(uci show shadowsocksr | grep "@servers\[" | wc -l)
    
    for i in $(seq 0 $((node_count-1))); do
        local server=$(uci get shadowsocksr.@servers[$i].server 2>/dev/null)
        local type=$(uci get shadowsocksr.@servers[$i].type 2>/dev/null)
        local protocol=$(uci get shadowsocksr.@servers[$i].v2ray_protocol 2>/dev/null)
        
        if [ "$server" = "92.112.248.210" ] && [ "$type" = "v2ray" ] && [ "$protocol" = "vmess" ]; then
            vmess_found=true
            log_success "找到VMess住宅IP节点: $server"
            
            # 检查详细配置
            local port=$(uci get shadowsocksr.@servers[$i].server_port 2>/dev/null)
            local uuid=$(uci get shadowsocksr.@servers[$i].vmess_id 2>/dev/null)
            local alter_id=$(uci get shadowsocksr.@servers[$i].alter_id 2>/dev/null)
            local security=$(uci get shadowsocksr.@servers[$i].security 2>/dev/null)
            local network=$(uci get shadowsocksr.@servers[$i].network 2>/dev/null)
            local tls=$(uci get shadowsocksr.@servers[$i].tls 2>/dev/null)
            local proxy=$(uci get shadowsocksr.@servers[$i].proxy 2>/dev/null)
            
            echo "  端口: $port"
            echo "  UUID: $uuid"
            echo "  额外ID: $alter_id"
            echo "  加密: $security"
            echo "  传输: $network"
            echo "  TLS: $tls"
            echo "  上级代理: $proxy"
            
            # 验证关键参数
            if [ "$port" = "111111" ] && [ "$uuid" = "a48314c6-f8d0-d56e-0000-000000000000" ]; then
                log_success "VMess节点配置正确"
            else
                log_warning "VMess节点配置可能有误"
            fi
            
            break
        fi
    done
    
    if [ "$vmess_found" = false ]; then
        log_error "未找到VMess住宅IP节点"
        return 1
    fi
    
    return 0
}

# 检查代理链配置
check_proxy_chain() {
    log_info "检查代理链配置..."
    
    local main_server=$(uci get shadowsocksr.@global[0].global_server 2>/dev/null)
    if [ -z "$main_server" ]; then
        log_error "未设置主服务器"
        return 1
    fi
    
    log_success "主服务器索引: $main_server"
    
    # 检查主服务器配置
    local main_alias=$(uci get shadowsocksr.@servers[$main_server].alias 2>/dev/null)
    local main_ip=$(uci get shadowsocksr.@servers[$main_server].server 2>/dev/null)
    
    echo "  主服务器: $main_alias ($main_ip)"
    
    return 0
}

# 检查服务状态
check_service_status() {
    log_info "检查服务状态..."
    
    # 检查ShadowsocksR服务
    if /etc/init.d/shadowsocksr status | grep -q "running"; then
        log_success "ShadowsocksR服务运行中"
    else
        log_warning "ShadowsocksR服务未运行"
    fi
    
    # 检查进程
    if pgrep -f "ss-redir" > /dev/null; then
        log_success "ss-redir进程运行中"
    else
        log_warning "ss-redir进程未运行"
    fi
    
    if pgrep -f "v2ray" > /dev/null; then
        log_success "v2ray进程运行中"
    else
        log_warning "v2ray进程未运行"
    fi
}

# 网络连接测试
test_connectivity() {
    log_info "测试网络连接..."
    
    # 测试本地连接
    if ping -c 1 -W 3 8.8.8.8 > /dev/null 2>&1; then
        log_success "本地网络连接正常"
    else
        log_error "本地网络连接失败"
        return 1
    fi
    
    # 测试代理连接（通过curl测试IP）
    log_info "测试代理IP地址..."
    local proxy_ip=$(curl -s --connect-timeout 10 --socks5 127.0.0.1:1080 http://ipinfo.io/ip 2>/dev/null)
    
    if [ -n "$proxy_ip" ]; then
        log_success "代理IP: $proxy_ip"
        
        # 检查是否为住宅IP
        local ip_info=$(curl -s --connect-timeout 10 --socks5 127.0.0.1:1080 "http://ipinfo.io/$proxy_ip/json" 2>/dev/null)
        if echo "$ip_info" | grep -q "92.112.248.210"; then
            log_success "成功使用住宅IP代理"
        else
            log_warning "当前使用的不是住宅IP代理"
            echo "IP信息: $ip_info"
        fi
    else
        log_error "无法获取代理IP"
    fi
}

# 显示配置摘要
show_config_summary() {
    log_info "配置摘要:"
    echo "=========================================="
    echo "住宅IP地址: 92.112.248.210"
    echo "端口: 111111"
    echo "协议: VMess"
    echo "UUID: a48314c6-f8d0-d56e-0000-000000000000"
    echo "=========================================="
}

# 主函数
main() {
    echo "VMess住宅IP代理配置验证"
    echo "======================================"
    
    show_config_summary
    echo
    
    check_ssr_config || exit 1
    echo
    
    check_vmess_node || exit 1
    echo
    
    check_proxy_chain
    echo
    
    check_service_status
    echo
    
    test_connectivity
    echo
    
    log_success "验证完成！"
}

# 执行主函数
main "$@"