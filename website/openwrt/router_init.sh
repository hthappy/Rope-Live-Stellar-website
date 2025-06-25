# 初始化脚本# 定义下载链接和目标目录
URL1="https://stellar.ai-yy.com/openwrt/footer.htm"
URL2="https://stellar.ai-yy.com/openwrt/footer_login.htm"
URL3="https://stellar.ai-yy.com/openwrt/sysauth.htm"
URL4="https://stellar.ai-yy.com/openwrt/header.htm"
URL5="https://stellar.ai-yy.com/openwrt/shadowsocksr.lua"
URL6="https://stellar.ai-yy.com/openwrt/shadowsocksr-control.js"
URL7="https://stellar.ai-yy.com/openwrt/shadowsocksr-hide.css"
LOGO="https://stellar.ai-yy.com/openwrt/logo.png"
TARGET_DIR="/usr/lib/lua/luci/view/themes/argon/"

# 检查目标目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo "错误：目标目录 $TARGET_DIR 不存在！"
    exit 1
fi

# 下载logo
echo "正在下载 logo.png..."
wget -q --no-check-certificate "$LOGO" -O "/www/luci-static/argon/img/logo.png"
if [ $? -ne 0 ]; then
    echo "下载 logo.png 失败！"
    exit 1
fi

# 下载文件并覆盖
echo "正在下载 footer.htm..."
wget -q --no-check-certificate "$URL1" -O "$TARGET_DIR/footer.htm"
if [ $? -ne 0 ]; then
    echo "下载 footer.htm 失败！"
    exit 1
fi

echo "正在下载 footer_login.htm..."
wget -q --no-check-certificate "$URL2" -O "$TARGET_DIR/footer_login.htm"
if [ $? -ne 0 ]; then
    echo "下载 footer_login.htm 失败！"
    exit 1
fi

echo "正在下载 sysauth.htm..."
wget -q --no-check-certificate "$URL3" -O "$TARGET_DIR/sysauth.htm"
if [ $? -ne 0 ]; then
    echo "下载 sysauth.htm 失败！"
    exit 1
fi



/etc/init.d/uhttpd restart

# 修改/etc/banner
cat > /etc/banner <<'EOF'
   ____  _ _____  _             _           _     
  / __ \(_)  __ \(_)           | |         | |    
 | |  | |_| |  | |_  __ _ _ __ | |     __ _| |__  
 | |  | | | |  | | |/ _` | '_ \| |    / _` | '_ \ 
 | |__| | | |__| | | (_| | | | | |___| (_| | |_) |
  \___\_\_|_____/|_|\__,_|_| |_|______\__,_|_.__/ 
   网站: https://www.qidianlab.com  |  Telegram: @QiDianLab



   
EOF