---
title: 解决 Hugo 默认时区造成文章/页面不渲染的问题
description: Hugo 坏啦！为什么无视我新增的页面？
date: 2022-05-17
slug: hugo-time-zone
image: 1.png
categories:
    - tech
tags:
    - Hugo
    - 时区
---

## 问题

现在是凌晨1点，已经是5月17日了。像下面这样，我创建了一个页面，将时间设置为5月17日：

{{< highlight yaml >}}
title: 解决 Hugo 默认时区造成文章/页面不渲染的问题
description: Hugo 坏啦！为什么无视我新增的页面？
date: 2022-05-17
{{< /highlight >}}

然而，浏览器什么变化都没有。

赶快回到终端，查看 `hugo -D server` 的输出：

{{< highlight shell >}}
Change detected, rebuilding site.
2022-05-17 01:09:56.287 +0800
Source changed ".../index.md": WRITE
Total in 12 ms
{{< /highlight >}}

诶诶，这不是识别出页面变化了吗？可是为什么不渲染新的页面呢？

## 解决方案

苦苦 Google 一番，终于在[这里](https://jdhao.github.io/2020/01/11/hugo_post_missing/)找到了答案。

原来，Hugo 默认不会渲染将来的页面，也不会输出任何提示，说明有页面因为时间未到而未渲染。而 Hugo 按照 UTC 时间考虑我的页面，认为我的页面是将来的页面，自然就没有输出了。

找到了问题，方法就很简单了。你可以：

+ 为自己文章/页面的 date 加上时区
+ 配置 Hugo 使其输出将来的页面

我直接采用了简单粗暴的第二种方式。在 config.yaml 中添加：

{{< highlight yaml >}}
buildFuture: true
{{< /highlight >}}

这样就会将将来的页面也一起渲染。