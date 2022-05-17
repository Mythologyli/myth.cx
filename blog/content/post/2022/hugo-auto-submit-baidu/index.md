---
title: 利用 Github Actions 自动提交 Hugo 站内链接到百度搜索资源平台
description: Hugo + Github Actions + 百度搜索资源平台
date: '2022-05-17T21:39:00'
slug: hugo-auto-submit-baidu
image: 1.png
categories:
    - tech
tags:
    - Hugo
    - 百度搜索
    - sitemap
    - Github Actions
---

## 前言

如果你希望你的网站尽快被百度搜索收录，你一定在百度搜索资源平台添加了你的站点，并通过普通收录功能向百度提交了你的站内链接。

百度的普通收录有以下三种方式：

| 方式 | 收录速度 | 收录完整性 |
| ---- | ---- | ---- |
| API 提交 | 最为快速 | 取决于推送程序 |
| sitemap | 慢于 API | sitemap 完整则完整 |
| 手动提交 | 未知 | 正经人谁手动啊 |

考虑到大多数人的 Hugo 站点都在利用 Git 进行管理，使用 Github 上的仓库，我们可以利用 Github Actions，在 Push 时自动提交链接到百度搜索资源平台。

## 细节

我的 Hugo 仓库目录结构如下：

```shell {linenos=false}
myth.cx (repo)
  -- ...
  -- blog (hugo)
     -- ...
     -- public
        -- ...
        -- sitemap.xml
  -- scripts
     -- ...
     -- baidu.py
```

在每次利用 `hugo` 命令生成静态页面后，public 目录下都会自动产生 sitemap.xml 文件，从这个文件中我们可以获取所有站内链接，并通过 Python 脚本向百度搜索资源平台提交。

首先，我们需要在 Github Action Ubuntu 环境中配置 Hugo。利用 [actions-hugo](https://github.com/peaceiris/actions-hugo) 配置 Hugo 环境：

```yml {linenos=false}
- name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
          extended: true
```

这样，我们就可以在 Actions 中使用 `hugo` 命令：

```yml {linenos=false}
- name: Build
        run: cd blog && hugo
```

这一步后，Hugo 已经为我们生成了 sitemap.xml 文件。利用如下 Python 脚本可以向百度提交链接：

```python
import sys
import requests
import lxml.etree


def submit_to_baidu(api_url, urls):
    """
    Submit the url to baidu
    """

    headers = {
        'User-Agent': 'curl/7.12.1',
        'Host': 'data.zz.baidu.com',
        'Content-Type': 'text/plain',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Content-Length': str(len(urls))
    }

    res = requests.post(api_url, headers=headers, data=urls)
    return res.text


def get_urls(sitemap_path):
    """
    Get the urls from sitemap
    """

    tree = lxml.etree.parse(sitemap_path)

    namespaces = {
        'sitemapindex': 'http://www.sitemaps.org/schemas/sitemap/0.9',
    }

    urls = ''
    for url in tree.xpath("//sitemapindex:loc/text()", namespaces=namespaces):
        urls += url + '\n'

    return urls


if __name__ == '__main__':
    urls = get_urls(sys.argv[1])

    print(urls)

    print(submit_to_baidu(sys.argv[2], urls))
```

该脚本接收两个参数，第一个参数是 sitemap.xml 的路径，第二个参数是百度搜索资源平台的 API 提交地址。对于第一个参数，我们可以直接写在 Github Actions 的 yml 文件中，而第二个参数涉及隐私，使用 Secret 的方式配置。

```yml {linenos=false}
- name: Submit
        run: cp blog/public/sitemap.xml scripts && cd scripts && pip3 install lxml && python3 baidu.py sitemap.xml "${{ secrets.BAIDU_API_URL }}"
```

新建 Secert BAIDU_API_URL，设置为百度搜索资源平台的 API 提交地址，形如 `https://data.zz.baidu.com/urls?site=xxxx&token=xxxx`。最终的完整 yml 文件为：

```yml {linenos=false}
name: Submit to Baidu

on: [ push ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          submodules: true
          fetch-depth: 0

      - name: Setup Hugo
        uses: peaceiris/actions-hugo@v2
        with:
          hugo-version: 'latest'
          extended: true

      - name: Build
        run: cd blog && hugo

      - name: Submit
        run: cp blog/public/sitemap.xml scripts && cd scripts && pip3 install lxml && python3 baidu.py sitemap.xml "${{ secrets.BAIDU_API_URL }}"
```

## 开源地址

可以参考[我的博客仓库](https://github.com/Mythologyli/myth.cx)

## 参考资料

[如何使用 API 推送功能](https://ziyuan.baidu.com/college/courseinfo?id=267&page=3#h2_article_title14)