---
title: 在 Windows 上实现阿里云 DNS 动态解析
description: 利用 AliyunDdnsCSharp 在 Windows 上实现阿里云 DNS 动态解析服务
date: 2020-09-13
slug: aliyun-ddns
categories:
    - tech
tags:
    - 阿里云
    - DNS
    - DDNS
    - Windows
    - 域名
---

由于学校校园网 Wi-Fi 最近支持了 IPv6/IPv4 双栈连接，笔记本终于可以离开网线接入 IPv6 网络了。因为我有在阿里云购买的域名，所以做了 AAAA 解析记录，可以愉快地用域名远程连接笔记本，再也不需要通过服务器中转 RDP。可是学校分配的 IPv6 时不时会发生改变，而一遍遍在阿里云控制台更改太麻烦，于是想到能不能在 Windows 上实现阿里云 DNS 动态解析服务。

在一番搜索后，在 Github 上找到了 [AliyunDdnsCSharp](https://github.com/xuchao1213/AliyunDdnsCSharp) 这个项目，完美地解决了我的问题。感谢项目作者 [xuchao1213]((https://github.com/xuchao1213)！

下面是个人实践的安装方法：

1. 点击链接，在阿里云申请 AccessKey ID 和 AccessKey Secret。通过 AccessKey 可以调用阿里云域名解析相关的 API，从而实现对域名解析记录的更改。

2. 在 Github 下载该程序。将压缩包 AliyunDdnsCSharp.zip 在任意目录解压（目录以后不可变动）。执行 Install.bat 安装服务。

3. 在 conf 目录下放置配置文件。支持多个配置文件，每个文件一条记录。
   
   例如，以下配置表示：刷新间隔10 min；解析域名为 test.example.com；记录类型为 AAAA (IPv6)；线路为默认线路；TTL 为600；获取 IPv6 地址的方式为 ipconfig（默认）。

{{< highlight json >}}
{
    "Interval": "10",
    "AccessKeyId": "xxxxxx",
    "AccessKeySecret": "xxxxxx",
    "DomainName": "example.com",
    "SubDomainName": "test",
    "Type": "AAAA",
    "Line": "default",
    "TTL": "600",
    "GetIpUrls": []
}
{{< /highlight >}}

4. 执行 Start.bat，DDNS服务应该可以正常运行。