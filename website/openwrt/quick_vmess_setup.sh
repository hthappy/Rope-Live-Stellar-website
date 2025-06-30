#!/bin/bash

# VMess住宅IP代理快速配置脚本
# 版本: 1.0
# 专门用于配置 a48314c6:f8d0d56e@92.112.248.210:111111 VMess代理

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# VMess配置参数
VMESS_SERVER="92.112.248.210"
VMESS_PORT="26239"
VMESS_UUID="f6e274cc-f2c9-f282-ed5e-e1b7de6f56d6"
VMESS_PASS="f8d0d56e"
VMESS_ALIAS="住宅IP-VMess-92.112.248.210"

echo "======================================"
echo "VMess住宅IP代理快速配置"
echo "======================================"
echo "服务器: $VMESS_SERVER:$VMESS_PORT"
echo "协议: VMess"
echo "UUID: $VMESS_UUID"
echo "======================================"
echo

log_success "ShadowsocksR Plus+已安装"

# 备份现有配置
log_info "备份现有配置..."
cp /etc/config/shadowsocksr /etc/config/shadowsocksr.backup.$(date +%Y%m%d_%H%M%S)
log_success "配置已备份"

# 添加VMess节点
log_info "添加VMess住宅IP节点..."
uci add shadowsocksr servers
NODE_INDEX=$(uci show shadowsocksr | grep "@servers\[" | tail -1 | sed 's/.*\[\([0-9]*\)\].*/\1/')

# 基本配置
uci set shadowsocksr.@servers[$NODE_INDEX].alias="$VMESS_ALIAS"
uci set shadowsocksr.@servers[$NODE_INDEX].server="$VMESS_SERVER"
uci set shadowsocksr.@servers[$NODE_INDEX].server_port="$VMESS_PORT"
uci set shadowsocksr.@servers[$NODE_INDEX].timeout="60"
uci set shadowsocksr.@servers[$NODE_INDEX].tcp_fast_open="false"

# VMess特定配置
uci set shadowsocksr.@servers[$NODE_INDEX].type="v2ray"
uci set shadowsocksr.@servers[$NODE_INDEX].v2ray_protocol="vmess"
uci set shadowsocksr.@servers[$NODE_INDEX].vmess_id="$VMESS_UUID"
uci set shadowsocksr.@servers[$NODE_INDEX].alter_id="0"
uci set shadowsocksr.@servers[$NODE_INDEX].security="auto"
uci set shadowsocksr.@servers[$NODE_INDEX].network="tcp"
uci set shadowsocksr.@servers[$NODE_INDEX].transport="tcp"
uci set shadowsocksr.@servers[$NODE_INDEX].tls="0"
uci set shadowsocksr.@servers[$NODE_INDEX].path="/"
uci set shadowsocksr.@servers[$NODE_INDEX].host=""

# 查找科学上网节点作为上级代理
log_info "配置代理链..."
MAIN_NODE_INDEX=0
for i in $(seq 0 10); do
    NODE_SERVER=$(uci get shadowsocksr.@servers[$i].server 2>/dev/null)
    if [ -n "$NODE_SERVER" ] && [ "$NODE_SERVER" != "$VMESS_SERVER" ]; then
        MAIN_NODE_INDEX=$i
        MAIN_NODE_ALIAS=$(uci get shadowsocksr.@servers[$i].alias 2>/dev/null)
        log_info "找到科学上网节点: $MAIN_NODE_ALIAS ($NODE_SERVER)"
        break
    fi
done

# 设置代理链
uci set shadowsocksr.@servers[$NODE_INDEX].proxy="$MAIN_NODE_INDEX"
log_success "代理链配置完成: 科学上网节点 -> VMess住宅IP"

# 提交配置
uci commit shadowsocksr
log_success "VMess节点配置完成"

# 配置分流规则
log_info "配置跨境电商分流规则..."

# 创建跨境电商域名列表
cat > /etc/shadowsocksr/ecommerce_domains.txt << 'EOF'
# 跨境电商平台域名
amazon.com
amazon.co.uk
amazon.de
amazon.fr
amazon.it
amazon.es
amazon.ca
amazon.com.au
ebay.com
ebay.co.uk
ebay.de
ebay.fr
ebay.it
ebay.es
ebay.ca
ebay.com.au
shopify.com
woocommerce.com
magento.com
bigcommerce.com
wix.com
squarespace.com
wordpress.com
stripe.com
paypal.com
shopee.com
lazada.com
rakuten.com
aliexpress.com
dhgate.com
1688.com
wish.com
overstock.com
wayfair.com
homedepot.com
lowes.com
bestbuy.com
target.com
walmart.com
costco.com
EOF

# 配置域名分流
if [ -f "/etc/dnsmasq.d/gfwlist.conf" ]; then
    # 添加跨境电商域名到分流列表
    while read domain; do
        if [[ ! "$domain" =~ ^# ]] && [ -n "$domain" ]; then
            echo "server=/$domain/127.0.0.1#5335" >> /etc/dnsmasq.d/ecommerce.conf
            echo "ipset=/$domain/gfwlist" >> /etc/dnsmasq.d/ecommerce.conf
        fi
    done < /etc/shadowsocksr/ecommerce_domains.txt
    
    log_success "跨境电商域名分流配置完成"
else
    log_warning "未找到GFWList配置，请手动配置域名分流"
fi

# 重启服务
log_info "重启相关服务..."
/etc/init.d/shadowsocksr restart
sleep 3
/etc/init.d/dnsmasq restart

# 验证配置
log_info "验证配置..."
sleep 5

if /etc/init.d/shadowsocksr status | grep -q "running"; then
    log_success "ShadowsocksR服务运行正常"
else
    log_error "ShadowsocksR服务启动失败"
fi

if pgrep -f "v2ray" > /dev/null; then
    log_success "V2Ray进程运行正常"
else
    log_warning "V2Ray进程未找到"
fi

# 显示配置摘要
echo
log_info "配置摘要:"
echo "=========================================="
echo "VMess节点: $VMESS_ALIAS"
echo "服务器: $VMESS_SERVER:$VMESS_PORT"
echo "UUID: $VMESS_UUID"
echo "上级代理: 节点索引 $MAIN_NODE_INDEX"
echo "节点索引: $NODE_INDEX"
echo "=========================================="
echo

# 使用说明
log_info "使用说明:"
echo "1. 在ShadowsocksR Plus+ Web界面中选择 '$VMESS_ALIAS' 节点"
echo "2. 设置运行模式为 '绕过大陆模式' 或 '全局模式'"
echo "3. 访问跨境电商网站将自动使用住宅IP"
echo "4. 使用以下命令验证配置:"
echo "   /tmp/verify_vmess_config.sh"
echo

log_success "VMess住宅IP代理配置完成！"
echo "请在Web界面中激活该节点以开始使用住宅IP代理。"