[Interface]
PrivateKey = QPZbp9aq49161YP2eWpk3PZAWXy7YV8wLCUGfIMOL1w=
Address = 172.16.0.2/32
DNS = 172.16.0.1
MTU = 1350
Table = off

# 策略路由设置
PostUp = ip rule add fwmark 51820 table 51820
PostUp = ip route add default dev wg0 table 51820
PostUp = ip rule add not fwmark 51820 table main
PostUp = iptables -t mangle -A OUTPUT -m owner --uid-owner 0 -j MARK --set-mark 51820

# 保留 SSH 公网 IP 的直连路由（重点）
PostUp = ip route add 45.78.63.195 via 45.78.63.1 dev eth0

PostDown = ip rule del fwmark 51820 table 51820
PostDown = ip rule del not fwmark 51820 table main
PostDown = iptables -t mangle -D OUTPUT -m owner --uid-owner 0 -j MARK --set-mark 51820
PostDown = ip route del 45.78.63.195 via 45.78.63.1 dev eth0

[Peer]
PublicKey = F9t+wSZzf5AoFw+fYUG948IeHiQ+QX5sw5Y7YBDz/1g=
Endpoint = it349.kookeey.info:26239
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
