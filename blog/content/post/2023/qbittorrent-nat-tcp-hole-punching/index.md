---
title: 通过 NAT TCP 打洞使 qBittorrent 获得公网 IPv4 的连接性体验
description: 利用 NATMap 实现 TCP 打洞帮助 BT 做种
date: '2023-01-15'
slug: qbittorrent-nat-tcp-hole-punching
image: 1.png
categories:
    - tech
tags:
    - NAT
    - 打洞
    - qBittorrent
    - BT
    - PT
---

## 网络环境分析

目前在国内，许多用户无法从运营商那里获取公网 IPv4 地址（点名中国移动）。对于 PT 玩家而言，这意味着他们在 IPv4 下的可连接性很差，无法获取很多上传量。在这种现状下，TCP 打洞是一种很好的解决方案。

为了更好地理解 TCP 打洞帮助做种的原理，我们先来看看客户端和 Tracker 通信的过程。简单地讲，qBittorrent 之类的客户端将自己的 IP 地址和监听端口上报给 Tracker，Tracker 再将其发送给其他需要下载的 Peer 客户端。之后，Peer 客户端连接至相应的 IP 地址和端口，开始下载。需要注意的是，**实际上，客户端往往不需要上报自己的 IPv4 地址，因为 Tracker 采用的是从 TCP 报文中获取到的 IPv4 地址**。

这一过程是很清晰的，但实际网络环境不会这么理想。我们考虑国内宽带的常见情况：通过 PPPoE 拨号获得 IP 地址，网络设备有光猫、路由器和一个子网下的做种设备。为了避免光猫拨号造成的麻烦，我们只讨论光猫为桥接模式的情况。

### 能获取到公网 IPv4 地址

首先，考虑路由器 PPPoE 拨号能获取到公网 IPv4 地址的情况。不难发现，如果 BT 客户端运行在路由器上，就可以轻松地被其他客户端连接，因为客户端监听在公网地址和端口上。假设 BT 客户端上报的监听端口为 `23456`，Tracker 从 TCP 报文中获得的 IPv4 地址为公网地址 `1.1.1.1`。这样，其他客户端连接到 `1.1.1.1:23456` 即可进行下载。

但如果 BT 客户端运行在路由器子网下的设备上，情况则稍稍复杂。我们假设路由器获得的公网地址为 `1.1.1.1`，路由器在子网的地址为 `192.168.1.1`，客户端设备的地址为 `192.168.1.2`。此时，BT 客户端监听在 `192.168.1.2` 的 `23456` 端口上。BT 客户端上报的端口也为 `23456`，而 Tracker 获得的 IPv4 地址则为公网地址 `1.1.1.1`。其他客户端会尝试连接 `1.1.1.1:23456`，这显然会失败，因为拥有公网地址的路由器并没有在监听此端口，更不会把此端口收到的数据转发到 `192.168.1.2:23456`。

这时，有几种常见的解决方案：

1. 在路由器上设置 `192.168.1.2` 为 DMZ 主机。此时，发往 `1.1.1.1:23456` 的数据会被自动转发到 `192.168.1.2:23456`。

2. 在路由器上设置端口转发，将 `23456` 端口转发到 `192.168.1.2:23456`。

3. 打开路由器和 BT 客户端的 UPnP 功能。这实际上可以理解为一个自动的端口转发协议。

可以看出，路由器上有一层 NAT（网络地址转换），但由于路由器对我们而言是完全可控的设备，我们可以轻松配置转发穿越这一层 NAT，使其他客户端可以连接到我们的 BT 客户端。

### 不能获取到公网 IPv4 地址

不能获取到公网 IPv4 地址的情况则令人绝望。这意味着只有运营商设备拥有公网地址，路由器获取到的则是一个私有地址，其本身就在通过 NAT 连接互联网。

我们假设运营商设备的公网地址为 `1.1.1.1`，路由器获取到的地址为 `10.0.0.2`。我们在路由器上配置好上一节的内容，使得 `10.0.0.2:23456` 上存在一个 BT 客户端监听服务。此时，客户端向 Tracker 上报端口 `23456`，Tracker 获得的 IPv4 地址为公网地址 `1.1.1.1`。其他客户端会尝试连接 `1.1.1.1:23456`，这显然会失败。并且，我们无法通过在运营商 NAT 设备上配置 DMZ 主机或端口转发来解决，因为运营商设备对我们来说不可控。

## NAT 类型分析

为了设法穿越运营商 NAT，我们先了解一下常见的 NAT 类型。以下内容摘抄、修改自互联网：

### 完全圆锥形 NAT/Full Cone NAT

完全圆锥型 NAT 将一个来自内部 IP 地址和端口的所有请求，始终映射到相同的公网 IP 地址和端口；同时，任意外部主机向映射的公网 IP 地址和端口发送报文，都可以实现和内网主机进行通信，就像一个向外开口的圆锥形一样，故得名。

这种模式很宽松，限制小，只要内网主机的 IP 地址和端口与公网 IP 地址和端口建立映射关系，所有互联网上的主机都可以访问该 NAT 之后的内网主机。

### 地址限制式圆锥形 NAT/Address Restricted Cone NAT

地址限制式圆锥形 NAT 同样将一个来自内部 IP 地址和端口的所有请求，始终映射到相同的公网 IP 地址和端口；与完全圆锥型 NAT 不同的是，当内网主机向某公网主机发送过报文后，只有该公网主机才能向内网主机发送报文，故得名。

相比完全圆锥形 NAT，地址限制式圆锥形 NAT 增加了地址限制，也就是 IP 受限，而端口不受限。

### 端口限制式圆锥形 NAT/Port Restricted Cone NAT

端口限制式圆锥形 NAT 更加严格，在上述条件下，只有该公网主机该端口才能向内网主机发送报文，故得名。

相比地址限制式圆锥形 NAT，端口限制式圆锥形 NAT 又增加了端口限制，也就是说 IP、端口都受限。

### 对称式 NAT/Symmetric NAT

对称式 NAT 将内网 IP 和端口到相同目的地址和端口的所有请求，都映射到同一个公网地址和端口；同一个内网主机，用相同的内网 IP 和端口向另外一个目的地址发送报文，则会用不同的映射（比如映射到不同的端口）。

和端口限制式 NAT 不同的是，端口限制式 NAT 是所有请求映射到相同的公网 IP 地址和端口，而对称式 NAT 是为不同的请求建立不同的映射。它具有端口受限锥型的受限特性，内部地址每一次请求一个特定的外部地址，都可能会绑定到一个新的端口号。也就是请求不同的外部地址映射的端口号是可能不同的。

了解了四种 NAT 类型，我们不难发现，对于 BT 这种使用模式，只有完全圆锥形 NAT/Full Cone NAT 可以尝试穿越。不同 Peer 客户端的 IP 不同，如果限制 IP 地址，Peer 就无法进行连接。

## NAT TCP 打洞

我们已经知道，在完全圆锥形 NAT 下，当映射关系建立后，任意外部主机向映射的公网 IP 地址和端口发送报文，都可以实现和内网主机进行通信。因此，只要内网主机通过某个端口向外发出请求，NAT 映射关系就会建立。

不过，NAT 映射关系建立后，还面临着如何长时间保持的问题。我们可以利用 [Natter](https://github.com/MikeWang000000/Natter) 或 [NATMap](https://github.com/heiher/natmap) 来实现对 NAT 映射关系的保持。具体原理如下：

1. 由本地端口 A 向外发起 TCP 长连接，以维持 NAT 端口映射关系。

2. 通过 STUN 服务器，获取对应的公网 IP 和端口。

3. 利用端口重用特性，同时监听端口 A，对外提供服务。

## qBittorrent 场景下的应用方法

我们再来考虑 TCP 打洞在 BT 中的应用。公网 IPv4 地址不用担心，Tracker 可以从 TCP 报文中直接获得。关键是需要上报给 Tracker 正确的端口。

对于 qBittorrent 而言，其上报的端口必然是其本地监听端口。如果要实现灵活地修改上报端口，需要修改 qBittorrent 源码，不符合大多数 PT 站的要求。因此，需要采取比较迂回的策略。

我们假设做种设备的内网 IP 为 `192.168.1.2`，路由器内网 IP 为 `192.168.1.1`。路由器通过拨号获取到私网 IP `10.0.0.2`。运营商 NAT 设备的公网 IP 为 `1.1.1.1`。其中，做种设备已被设置为 DMZ 主机，意味着监听 `192.168.1.2:xxxx` 等价于监听 `10.0.0.2:xxxx`。

我们使用 NATMap，通过本地端口 `12345` 向外发起 TCP 连接，从而获取一组 NAT 映射关系，并且 `12345` 端口可以用于提供服务。假设 `1.1.1.1:34567` 被映射到 `10.0.0.2:12345`，进而通过 DMZ 主机设置来到 `192.168.1.2:12345`。理想情况下，直接让 qBittorrent 上报 `34567` 并监听 `12345` 即可。然而，由于 qBittorrent 只能上报本地监听端口，我们只能让 qBittorrent 监听 `192.168.1.2:34567`。因此，需要 iptables 规则将本地的 `12345` 端口转发至 `34567` 端口。

我们以 NATMap 为例。建立 NAT 映射关系或映射关系改变时，NATMap 可以触发脚本执行自定义操作。传入参数为：

+ $1: Public address (IPv4/IPv6)
+ $2: Public port
+ $3: IP4P
+ $4: Bind port (private port)
+ $5: Protocol (TCP/UDP)

对于 BT 的应用场景，我们只需要关注参数 2 公网端口和参数 4 内网端口。我们的脚本需要将 qBittorrent 的监听端口设置为参数 2 公网端口，然后用 iptables 将本地的参数 4 内网端口转发至本地的参数 2 公网端口。具体实现如下：

```bash
#!/bin/sh

# Natter/NATMap
private_port=$4 # Natter: $3; NATMap: $4
public_port=$2 # Natter: $5; NATMap: $2

# qBittorrent.
qb_web_port="8080"
qb_username="admin"
qb_password="adminadmin"

echo "Update qBittorrent listen port to $public_port..."

# Update qBittorrent listen port.
qb_cookie=$(curl -s -i --header "Referer: http://localhost:$qb_web_port" --data "username=$qb_username&password=$qb_password" http://localhost:$qb_web_port/api/v2/auth/login | grep -i set-cookie | cut -c13-48)
curl -X POST -b "$qb_cookie" -d 'json={"listen_port":"'$public_port'"}' "http://localhost:$qb_web_port/api/v2/app/setPreferences"

echo "Update iptables..."

# Use iptables to forward traffic.
LINE_NUMBER=$(iptables -t nat -nvL --line-number | grep ${private_port} | head -n 1 | grep -o '^[0-9]+')
iptables -t nat -D PREROUTING $LINE_NUMBER
iptables -t nat -I PREROUTING -p tcp --dport $private_port -j REDIRECT --to-port $public_port

echo "Done."
```

详细使用说明和脚本下载请前往我的 Github 仓库 [qBittorrent NAT TCP Hole Punching](https://github.com/Mythologyli/qBittorrent-NAT-TCP-Hole-Punching/blob/master/README.zh.md)。欢迎 Star。

如果运行 NATMap 的设备与运行 qBittorrent 的设备不同，则需要修改脚本中 iptables 转发的部分和 qBittorrent API 中的 `localhost`。

## 参考内容

+ [Natter](https://github.com/MikeWang000000/Natter)

+ [NATMap](https://github.com/heiher/natmap)