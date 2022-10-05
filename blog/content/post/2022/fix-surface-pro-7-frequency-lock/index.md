---
title: 修正 Surface Pro 7 低电量锁频问题
description: 解决 Surface Pro 7 在低电量下的严重卡顿
date: '2022-10-05'
slug: fix-surface-pro-7-frequency-lock
image: 1.png
categories:
    - tech
tags:
    - Surface
    - 锁频
    - 卡顿
    - 低电量
---

## 故障

笔者有一台 i5 款 Surface Pro 7，平常拿来进行远程桌面、手写等轻量任务。不知从何时起，这台 Surface 出现了卡顿的现象：在电量低于 40% 左右时，整个系统异常卡顿。窗口缩放都在掉帧，只开一个远程桌面都卡成 PPT。但此时电脑并未开启省电模式。若接上电源，系统立刻恢复如初。

## 解决

由于在高电量和接通电源时不存在卡顿，故极有可能是 CPU 锁频导致。打开任务管理器，果然，CPU 频率被限制在在 1.0 GHz 左右，不卡才怪。

大概 3 个月前给电脑装了 22H2 版的 Windows 11，因此一开始怀疑是 Windows 11 的锅。但是，搜索了一下似乎也不是这方面的问题。

在别的 Windows 设备上也没有遇到相同故障，所以还是把矛头对准了 Surface。Google 上一番搜索后，在 reddit 的 Surface 社区找到了这个，解决了问题：

[Throttling on battery from Intel Dynamic Tuning? Here's the fix!](https://www.reddit.com/r/Surface/comments/fqwyrk/throttling_on_battery_from_intel_dynamic_tuning/)

总而言之，问题是由 Intel Dynamic Tuning 引起的。它会在低电量时限制 CPU 以节省电量，但却造成了严重的卡顿。所以解决方法是：**禁用 Intel Dynamic Tuning 服务**。

## 分析

实际上，是 Intel 的 DTT 技术导致的降频，Intel 对它的介绍是：

> 英特尔® Dynamic Tuning Technology （英特尔® DTT） 是 英特尔 Adaptix ™ 技术的一 部分。
> 
> DTT 是系统软件制造商（也称为 OEM）配置的系统软件驱动程序，用于动态优化系统性能、电池续航时间和散热性能。
> 
> DTT 包含基于人工智能和机器学习的高级算法，以支持这些优化以获得性能、散热和电池续航时间。OEM 为其系统专门配置软件。DTT 并非旨在成为基于最终用户的软件，因为更改系统制造商设置可能会导致系统运行的风险。
> 
> 以下是 DTT 中包含的一些技术。OEM 决定它们将如何使用 DTT 的功能以及如何配置 DTT。
> 
> DTT 技术：
> + 英特尔 Power Share 技术自动并动态地在英特尔处理器和英特尔®独立显卡之间分配电源，以优化性能并改善电池续航时间。
> + 散热管理：监控功率和温度，并管理 SOC 和系统设备以在 OEM 定义的散热限制和规格内维护系统。
> + 自适应性能：允许 OEM 根据系统事件（如交流或电池模式、翻盖型或笔记本电脑使用、OEM 性能模式等）配置 DTT 设置。
> + 英特尔® DTT提供以下权益：
> + 改进了电源和散热系统约束下的 CPU 和 GPU 性能
> + 改进了 CPU 和独立 GPU 电源共享，通过将电源预算转移到 CPU 或 GPU 来提高性能，同时保持系统散热和电源预算。
> + 智能混合工作负载功率平衡
> + 监视和管理整体系统散热，以保持组件和系统规格。
> + 将散热和性能策略智能动态更改作为系统配置和使用的功能。

Intel 声称 DTT “包含基于人工智能和机器学习的高级算法”，但看来这些算法也不怎么聪明，以致于我的 Surface 直接变得无法使用。从另一方面讲，说不定是 Microsoft 或者 Intel 为了让续航数据变得更好看而搞的损害用户体验的把戏。

关闭 DTT 可能导致一些副作用，但我也没有别的选择。希望 Microsoft 早日修复这个问题。