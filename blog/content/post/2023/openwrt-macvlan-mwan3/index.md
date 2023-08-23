---
title: OpenWrt 路由器 MacVLAN+MWAN3 校园网多拨超详细指南
description: 利用 MacVLAN 实现浙大校园网网页认证多拨
date: '2023-04-10'
slug: openwrt-macvlan-mwan3
image: 1.png
categories:
    - tech
tags:
    - OpenWrt
    - 多拨
    - 校园网
    - MacVLAN
    - MWAN3
---

在校园网上网的过程中，许多同学都会有一些多线程下载需求。例如：公网 PT/BT 种子下载、Steam 游戏下载等等。这时，大家都希望能提高自己的网速，节省下载时间。

对于这类多线程的下载需求，如果采用多拨，在配置得当的情况下，系统会将流量分流至多个网络接口，实现网络带宽叠加的效果。

在介绍 OpenWrt 有线多拨方式前，先对校园网认证方式和现有的几种多拨方法作简要总结。不感兴趣的同学可以跳过这些部分。

## 校园网认证方式

### 网页认证方式

网页登录认证常用于 ZJUWLAN/ZJUWLAN-NEW 无线网。**目前大多数宿舍区的有线网也支持此方式**。接入 ZJUWLAN 或支持此方式的有线网，使用浏览器访问任意公网站点（如百度），会被重定向到认证网页。在认证网页输入账号密码，登录后即可访问公网。

认证的详细过程如下：设备接入无线或受支持的有线网后，DHCP 服务器向设备分配 IP 地址。在网页认证过程中，设备提交自己的 IP，服务端将 IP 在 DHCP 表中比对，如找不到 IP 则无法完成认证。这也是在不支持网页认证的有线网中强行认证会提示“IP 不在 DHCP 表中”的原因。具体的请求细节可以参考[田发呆](https://www.cc98.org/user/id/600145)同学的[网页认证登录脚本](https://www.cc98.org/topic/4898875)。

值得注意的是，在连接网络但未认证的情况下，经实测，ZJUWLAN/ZJUWLAN-NEW 不能访问包括 CC98 服务器在内的大部分内网主机。以下是在 ZJUWLAN-NEW 上的一些测试：

```
$ ping 10.10.98.98 -n 1

Pinging 10.10.98.98 with 32 bytes of data:
Request timed out.

$ ping 10.10.0.21 -n 1

Pinging 10.10.0.21 with 32 bytes of data:
Reply from 10.10.0.21: bytes=32 time=11ms TTL=250

$ ping lns.zju.edu.cn -n 1

Pinging lns.zju.edu.cn [10.0.2.3] with 32 bytes of data:
Reply from 10.0.2.3: bytes=32 time=2ms TTL=61

$ ping ee.zju.edu.cn -n 1

Pinging ee.zju.edu.cn [10.203.4.85] with 32 bytes of data:
Request timed out.

$ ping net.zju.edu.cn -n 1

Pinging net.zju.edu.cn [10.50.200.245] with 32 bytes of data:
Reply from 10.50.200.245: bytes=32 time=2ms TTL=60

$ ping speedtest.zju.edu.cn -n 1

Pinging speedtest.zju.edu.cn [10.202.41.81] with 32 bytes of data:
Reply from 10.202.41.81: bytes=32 time=7ms TTL=59
```

有线网则可在未认证的情况下访问几乎整个 10.0.0.0/8 段（未仔细验证）。

在登录认证后，公网流量会被正确路由，限速规则也在此时生效。不好的一点是，登录认证同样会对内网流量施加限速，导致在访问内网主机时无法达到链路速度。与后面介绍的 L2TP 认证方式不同，限速是在上级网关配置的，这导致我们原本的接口被限速，无法将 10.0.0.0/8 的流量分流到不限速的接口。对于使用 NexusHD、期望内网高速上传/下载的同学来说是重大弊端。

相比下面介绍的 L2TP 方式，网页认证的优点是支持同时登录多个设备，而 L2TP 只支持登录 1 个设备。*参考信息技术中心[说明](https://itc.zju.edu.cn/_t2014/2020/0414/c49794a2058046/page.psp)*。并且，由于网页认证无需在设备上进行加解密，对设备性能的要求较低。

*注：性能需求在单账号时影响不显著，但在多拨情况下有较大影响。大多数路由器在同时运行数个 L2TP 客户端、满带宽运行时会出现显著的性能问题。*

### L2TP 认证方式

L2TP 认证方式常用于有线网。在实际的使用中常有两种方式：有线 VPN 客户端和自建 L2TP 客户端。其中，信息技术中心提供的有线 VPN 客户端易于使用，但可能在 Windows 10/11 上导致一些网络问题，并且与科学上网工具的兼容性不佳。自建 L2TP 客户端的常见方式包括：Windows 自带的 VPN 功能、Linux 环境下的 xl2tpd/[zjunet](https://github.com/QSCTech/zjunet)。

L2TP 认证方式重要优点为：在拨号后可以在本机设置[静态路由](https://www.cc98.org/topic/5055830)，让 10.0.0.0/8 的流量通过原本的接口（未被限速）而非 L2TP 接口（被限速），对使用 NexusHD 的同学相当有用。缺点为设置方法复杂，并且只能一次登录一个设备。

### 802.1X 认证方式

用于 ZJUWLAN-Secure 无线网。本文主要聚焦于有线网，故不再赘述。

## 现有多拨方式

目前常见的多拨方式有：

- 有线 L2TP 多拨
- 有线 L2TP 叠加 ZJUWLAN 无线

*注：2021 年前可实现单账号 L2TP 多拨，目前漏洞已修复，只能进行多账号 L2TP 多拨。*

我们分两种情况介绍：

### 不借助路由器

不借助路由器直接在 Windows PC 上多拨，需要使用 Connectify Dispatch 软件。详细介绍可以看我的[这篇帖子](https://www.cc98.org/topic/5055830)。然而，Connectify Dispatch 软件需要破解，并且实测多拨的稳定性很差，故非常不推荐。

*注：直接在 Windows 上拨几个 L2TP 账号并不会使带宽叠加，因为 Windows 不会进行负载均衡。同时登录无线和有线，迅雷之类的软件可能会使用全部可用的网络接口，使带宽叠加。*

### 借助路由器多拨

这种情况下一般采用 L2TP 多拨，大多数路由器原装系统并不支持，需要安装第三方固件：

#### OpenWrt

可以借助 xl2tpd+MWAN3 实现多拨。但实测 OpenWrt 对 L2TP 的支持不太好，容易出现断连的情况（我这里测试的结果是这样，存疑）。

#### 高恪、爱快、ROS 等流控系统

这类系统具有强大的流控功能，可以很好的进行负载均衡。ROS（RouterOS，不是 Robot Operating System） 多拨可以参考 [hzdrro](https://www.cc98.org/user/id/504443) 同学的[这篇帖子](https://www.cc98.org/topic/5123534)。高恪、爱快等系统的设置也较为容易。

我之前一直使用刷写了高恪固件的新三路由器进行 L2TP 多拨。这类方法也存在一定缺点：

- L2TP 多拨需要多个账号
- L2TP 对设备性能的要求较高，多个 L2TP 客户端对一般的路由器过于吃力，可能需要 x86 软路由
- ROS、爱快均不支持常见的 MT7621 芯片路由器，需要 x86 软路由。高恪支持一些 MT7621 路由器，但高恪系统无 IPv6 支持，需要另想办法

下面开始这篇指南的主要内容：基于网页认证的多拨。

---

## OpenWrt+网页认证实现多拨

这一方案具有如下优点：

+ OpenWrt 适用于大多数路由器，无需购买软路由
+ 网页认证支持单账号多拨，无需使用多个账号
+ 网页认证方式对设备性能要求低
+ 通过 MacVLAN，可以绕过网页认证后的内网限速

在开始教程前，首先说明以下几点：

1. 多拨的上限受账号并发数和链路速度的限制。其中，链路速度主要和宿舍的交换机有关。将网线插入电脑，适配器属性中会显示 100Mbps 或 1000Mbps，这个即为多拨的上限（此处假设电脑网卡支持 1000Mbps）。

   *注：不要傻乎乎地以为把宿舍交换机换了就可以实现百兆到千兆的飞跃：先把宿舍交换机到上级的那根网线接自己电脑上试一下，如果还是显示 100Mbps——别折腾了，认了吧，双拨够了。这在玉泉很常见。*

2. 多拨并不能加速单个连接。因此，在测速时需要进行多连接测试。可以使用 [speedtest.net](https://www.speedtest.net/zh-Hans)，或者直接进行 BT 下载。

### 安装 OpenWrt 及相关依赖

#### 刷入 OpenWrt 固件

首先，确保你的路由器支持刷写 OpenWrt 固件。可以在[此列表](https://openwrt.org/toh/views/toh_fwdownload)中查找你的路由器。

*注1：大多数市售路由器需要先刷 breed 这个第三方 BootLoader 再刷写系统。可以直接在 breed [支持列表](https://www.right.com.cn/forum/thread-161906-1-1.html)中看看有没有自己的路由器，有的话可以在[恩山论坛](https://www.right.com.cn/)搜索对应路由器刷 breed 的教程。*

*注2：建议使用最新的原版 OpenWrt 而非 Lean 的 LEDE 版本。这些版本来源不一，有的会遇到 IPv6 支持问题和 MWAN3 版本问题，不推荐使用。*

找到自己的路由器后，从 	Firmware OpenWrt Install URL 下载最新稳定版固件，并利用 breed 刷入固件。之后，登入 OpenWrt 的 LuCI Web 界面并修改密码。

#### 安装依赖

由于[浙大镜像源](https://mirrors.zju.edu.cn/)支持 OpenWrt，安装依赖的过程只需内网连接，相当简单。

1. 确保路由器的 WAN 口已连接，网络-接口的 WAN 处已获取到校园网 10.0.0.0/8 端的内网 IP。

2. SSH 连接路由器：

   `ssh root@192.168.1.1`

3. 替换镜像源为浙大源：

   `sed -i 's_https\?://downloads.openwrt.org_http://mirrors.zju.edu.cn/openwrt_' /etc/opkg/distfeeds.conf`

4. 安装依赖：

   `opkg update && opkg install nano kmod-macvlan	mwan3	luci-app-mwan3	luci-i18n-mwan3-zh-cn python3 python3-pip`

5. 重启路由器：

   `reboot`

### 配置 MacVLAN 接口

默认情况下，网络-接口中有 LAN、WAN、WAN6 三个接口。关于 IPv6 配置的部分不再展开，有需要的同学可以在论坛自行搜索。

根据上面介绍的网页认证的实现方式可知：单个接口具有一个 MAC，可以通过 DHCP 获取一个 IPv4 地址，完成此接口的网页认证。如果需要多拨，则需要多个网络接口，此时仅仅一个 WAN 是不够的。

一种简单的想法是将 br-lan 网桥中用做 LAN 的接口拿出，配置为新的 WAN 口，从而拿到更多 IP 地址。问题在于这需要从上级交换机连接多根网线，非常不便。何况路由器的网卡是有限的，可能不够使用。

利用 MacVLAN 技术，可以很方便的解决这个问题。关于 MacVLAN 的详细介绍可以参考[这篇文章](https://icloudnative.io/posts/netwnetwork-virtualization-macvlan/)。简单地讲，MacVLAN 技术可以在单个物理网卡上虚拟出多个 MAC 地址不同的虚拟网卡。当物理网卡收到数据包后，会根据目的 MAC 地址判断这个包属于哪一个虚拟网卡。因此，创建多个 MacVLAN 虚拟网卡，即可从 DHCP 服务器获取多个 IP 地址。具体的配置方法如下：

1. 点击网络-接口，查看 WAN 对应的网卡名称，如 eth0。

2. 点击设备选项卡，根据想要多拨的次数添加 MacVLAN 设备。例如，想要双拨，则添加两个 MacVLAN 设备。

   添加设备时，设备类型选 MAC VLAN，基设备填 WAN 对应的设备（本例中为 eth0），模式 VEPA，MAC 地址填写一个不与原设备重复的 MAC 地址（可以简单地修改最后一位）。其他不填即可。

   全部添加完成后，点击保存并应用。确保原设备 eth0 与新添加的所有 MacVLAN 设备的 MAC 地址互不重复。

3. 回到接口选项卡，添加新接口，个数与刚刚添加的 MacVLAN 数相同。

   名称可填 WAN22/WAN33/WAN44 等等，确保不重复即可。协议选择 DHCP 客户端，设备选择刚刚添加的 MacVLAN 设备。

   注意：每个接口都需要填写跃点数。在编辑-高级设备-使用网关跃点中填写。这个值无所谓，互不重复即可。可以填名称中的数字：22/33/44。

   所有接口创建完成后，点击保存并应用。之后检查每个接口的状态。每个接口都应获取到互不重复的 IPv4 地址。

### 配置 MWAN3

MWAN3 可以实现负载均衡，配置方法如下：

1. 点击网络-MultiWAN 管理器-接口。首先删除所有原有的接口。然后在下方输入刚刚添加的 MacVLAN 接口的名称，点击添加。在弹出的窗口中勾选已启用，跟踪的主机或 IP 地址填百度的 IP 地址 `110.242.68.66`，其他默认既可。点击保存。重复此过程，直到所有的 MacVLAN 接口都已添加。

2. 点击成员选项卡。首先删除所有原有的成员，然后在下方输入 web1/web2/web3 之类的名称，点击添加。接口选择上一步中的接口，跃点数和 Weight 都填 1（除非每个接口的带宽不同，此时按比例填写 Weight）。点击保存。重复此过程，直到所有的口都已添加。

3. 点击策略选项卡，删除原有策略，只保留 balanced 策略。将 balanced 策略的成员选择为上一步中添加的成员。点击保存。

4. 点击规则选项卡，删除原有规则，只保留 default_rule_v4 和 default_rule_v6。将 default_rule_v4 的策略选择为 balanced，default_rule_v6 的策略选择为 default。点击保存并应用。

### 配置网页认证脚本

虽然 MWAN3 配置完成，但此时一定无法访问公网，因为还未进行网页认证。由于此时的 IPv4 流量会被随机分配给某个 MacVLAN 接口，我们只能不断设置到 `net.zju.edu.cn` 的静态路由，手动完成网页认证，过于麻烦。因此，需要编写一个脚本，自动完成网页认证。

MWAN3 的通知功能可以在接口失败时运行用户自定义的脚本。因此，可以利用这个功能，当某个接口连网失败时，自动在这个接口进行网页认证。登录脚本由[田发呆](https://www.cc98.org/user/id/600145)同学的[新ZJUWLAN登录脚本](https://www.cc98.org/topic/4898875)修改得来。

[下载地址](https://cloud.akashic.cc/#s/9KX_YAbA)，访问密码：cc98

配置方法如下：

1. 更换 Python3 源：

   `pip config set global.index-url https://mirrors.zju.edu.cn/pypi/web/simple
`

1. 安装 requests 模块：

   `pip install requests`

2. 修改脚本：

   脚本中此处需要进行修改：

   ```python
   if __name__ == '__main__':
      if action == "disconnected" and device.find("eth0mac") != -1:
         global username, password

         username = "xxxxxxxxxx"
         password = "xxxxxxxxxx"
   ```

   将 `eth0mac` 修改为刚刚添加的所有 MacVLAN 设备名称的共同部分。将 username 和 password 修改为自己的账号密码。

   如果有多个账号，可以多添加一些逻辑，根据 device 名称使用不同的账号密码。

3. 将脚本复制到 /root 路径下：

   `cd /root && nano mwan3.py`

   之后粘贴脚本内容，然后 Ctrl+O，回车保存。

4. 测试是否能利用脚本完成认证：

   `python3 mwan3.py wan1 eth0mac0 disconnected`

   如显示成功，则说明脚本配置无误。修改 eth0mac0，完成所有 MacVLAN 接口的网页认证。

5. 点击网络-MultiWAN 管理器-通知。在输入框最后一行添加：

   `/usr/bin/python3 /root/mwan3.py $INTERFACE $DEVICE $ACTION`

   之后保存并应用。

此后，断开连接后会 MWAN3 会自动运行脚本，重新完成网页认证。

### 配置静态路由分流内网流量

完成上述步骤后，所有的 IPv4 流量都会被分配给 MacVLAN 接口，而这些接口已被限速。因此，访问内网的单连接速度也随之降低。

不过，原接口 WAN 未完成网页认证，未被限速。通过静态路由将 10.0.0.0/8 的流量分配给 WAN，即可避免访问内网时被限速。

*注：静态路由规则优先级高于 MWAN3。*

配置方法如下：

1. 点击状态-概览，找到 WAN 对应设备的网关地址。

2. 点击网络-路由-静态 IPv4 路由。点击添加，接口选择 WAN，目标填写 `10.0.0.0/8`，网关填写刚刚记录的网关。保存并应用。

---

指南到此结束。

![](1.png)