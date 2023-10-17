---
title: 为移动魔百盒 GITV 生成 Kodi 可用的 M3U 源和 EPG 节目表
description: 移动魔百盒 OTT 盒子 GITV 抓包实战
date: '2023-01-28'
slug: gitv-ott-m3u-epg
image: 1.png
categories:
    - tech
tags:
    - 移动魔百盒
    - 银河互联网电视
    - GITV
    - OTT
    - M3U
    - EPG
    - Kodi
---

笔者在陕西移动办理宽带时，移动公司赠送了一个魔百盒 OTT 盒子。移动魔百盒可以通过 GITV（银河互联网电视）观看电视直播，虽比起 IPTV 延迟较高，但也有一定价值。最近在折腾 Kodi，于是想通过抓包的方式得到 GITV 的 M3U 源，以便在 Kodi 和其他设备上观看。

## 抓包

抓包采用 Wireshark 进行。具体方法为：在电脑上开热点，让魔百盒连接热点，再使用 Wireshark 抓包相应的网卡。

开始抓包后，在魔百盒上打开节目点播，得到节目列表（不需要开始播放）后停止抓包。

通过分析抓包结果，我们筛选出两个重要的 URL：

+ `channel_info_url`: [http://111.20.43.97:29010/chnInfos/SAXYD_ZX/0.json](http://111.20.43.97:29010/chnInfos/SAXYD_ZX/0.json)
+ `epg_list_url`: [http://111.20.43.97:29010/tagNewestEpgList/SAXYD_ZX/1/100/0.json](http://111.20.43.97:29010/tagNewestEpgList/SAXYD_ZX/1/100/0.json)

其中，`channel_info_url` 的内容如下：

```json
{
    "timestamp": "20230122220712",
    "data": [
        {
            "bigIconWidth": 220,
            "width": 88,
            "chnDefinition": "200",
            "chnIcon": "http:\/\/live.pic.gitv.tv\/images\/sx_icon\/CCTV-1.png",
            "nodeChn_status": "1",
            "playIcon": "",
            "height": 22,
            "bigIconHeight": 90,
            "forbidReplay": "1",
            "chns": [
                {
                    "codeRate": "default",
                    "playUrl": "http:\/\/saxyd-livod.dispatcher.gitv.tv\/gitv_live\/CCTV-1-HD\/CCTV-1-HD.m3u8?p=GITV&area=SAXYD_ZX",
                    "num": 3,
                    "definition": "清晰度自适应"
                },
                {
                    "codeRate": "3M",
                    "playUrl": "http:\/\/saxyd-livod.dispatcher.gitv.tv\/gitv_live\/CCTV-1-HD\/CCTV-1-HD.m3u8?p=GITV&area=SAXYD_ZX",
                    "num": 3,
                    "definition": "高清"
                }
            ],
            "newIcon": "http:\/\/live.pic.gitv.tv\/images\/sx_icon\/cctv-1_B.png",
            "chnName": "CCTV-1高清",
            "chn_status": "1",
            "bigChnIcon": "http:\/\/live.pic.gitv.tv\/\/images\/livod_icon\/20191224\/CCTV-1.png",
            "subTags": [
                {
                    "tagId": 0,
                    "subTagId": 1,
                    "tagType": 0
                }
            ],
            "guidWidth": null,
            "playIconWidth": null,
            "showLive": "1",
            "chnCode": "CCTV-1-HD",
            "guideHeight": null,
            "guideIcon": "",
            "playIconHeight": null
        },
        ...
    ]
}
```

从中我们可以获取到：

+ `bigChnIcon`: 高清台标
+ `chnName`: 频道名称
+ `chnCode`: 频道代码

`epg_list_url` 的内容如下：

```json
{
    "timestamp": "20230121093506",
    "data": [
        {
            "backgroundImg": null,
            "chnunCode": "cctv1",
            "packageCode": "5889b41f35db5e5d3c8e9a10_CCTV-1-HD",
            "chnDefinition": 200,
            "isShift": 1,
            "isBroadcastChn": 0,
            "packageCover": "http:\/\/live.pic.gitv.tv\/\/images\/2023\/1\/154\/5f841190a0294f32b102dfc8c283130c.jpg",
            "backPoster": "http:\/\/saxyd-livod.dispatcher.gitv.tv\/gitv_live\/CCTV-1-HD\/images?p=GITV&area=SAXYD_ZX",
            "tag": "综艺",
            "purchaseOwn": 0,
            "defHis": 0,
            "chnNum": 1,
            "title": "喜气洋洋合家欢-2023东西南北贺新春1",
            "packageCoverH": "http:\/\/live.pic.gitv.tv\/\/images\/2023\/1\/154\/612692009ef24f108a7dbed55e60c7a8.jpg",
            "packageName": null,
            "startTime": 1674261840000,
            "epgPoster": "http:\/\/saxyd-livod.dispatcher.gitv.tv\/gitv_live\/CCTV-1-HD\/live.jpg?p=GITV&area=SAXYD_ZX",
            "createTime": 1674197129000,
            "id": null,
            "chnOrder": 5,
            "restrictLv": null,
            "playUrl": "http:\/\/saxyd-livod.dispatcher.gitv.tv\/gitv_live\/CCTV-1-HD\/CCTV-1-HD.m3u8?p=GITV&area=SAXYD_ZX",
            "playOrder": 20230121,
            "chnName": "CCTV-1高清",
            "fkOrder": 9999,
            "endTime": 1674272280000,
            "superscriptPic": "http:\/\/live.pic.gitv.tv\/images\/livod_icon\/superscript\/hd.png",
            "chnTypeId": 1,
            "epgStatus": 1,
            "chnCode": "CCTV-1-HD",
            "showLive": 1,
            "onlineCount": 53046,
            "backPlayUrl": "http:\/\/saxyd-livod.dispatcher.gitv.tv\/gitv_live\/CCTV-1-HD\/history.m3u8?p=GITV&area=SAXYD_ZX",
            "updateTime": 1674197131000,
            "superscriptType": 1
        },
        ...
    ]
}
```

从中我们可以获取到：

+ `title`: 节目标题
+ `startTime`: 节目开始时间
+ `endTime`: 节目结束时间
+ `chnName`: 频道名称
+ `chnCode`: 频道代码
+ `playUrl`: 播放地址

需要注意的是，`playUrl` 并不是直接的播放地址。访问此地址得到：

```json
{
    "t": 1674914975,
    "o": "live",
    "u": "http:\/\/zteres.sn.chinamobile.com:6060\/yinhe\/2\/ch00000090990000001068?virtualDomain=yinhe.live_hls.zte.com",
    "c": "zhongxing",
    "isBlackUser": "false"
}
```

其中 `u` 才是真正的播放地址。

## 生成 M3U 源和 EPG 节目表

根据以上这些信息，我们可以编写一个 Python 脚本来定时生成 M3U 源和 EPG 节目表。

```python
import sys
import json
from urllib.request import urlopen
from datetime import datetime
from threading import Thread
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

import m3u
import xmltv


config = json.load(open("config.json"))


class UpdateFilesThread(Thread):
    def __init__(self, threadID, name, delay):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay

    def run(self):
        while True:
            try:
                print("更新频道...")

                channel_info_data = json.loads(
                    urlopen(config["channel_info_url"]).read().decode("utf-8")
                )["data"]
                epg_list_data = json.loads(
                    urlopen(config["epg_list_url"]).read().decode("utf-8")
                )["data"]

                try:
                    channel_cache = json.load(open("cache.json"))
                except FileNotFoundError:
                    channel_cache = {}

                # 获取频道图标
                channel_icon = {}
                for channel in channel_info_data:
                    channel_icon[channel["chnCode"]] = channel["bigChnIcon"]

                # 获取频道信息
                m3u_channel_list: list[m3u.Channel] = []
                xmltv_channel_list: list[xmltv.Channel] = []

                for channel in epg_list_data:
                    tvg_logo = channel_icon[channel["chnCode"]]

                    if channel["chnCode"] in channel_cache:
                        m3u8 = channel_cache[channel["chnCode"]]["m3u8"]
                    else:
                        m3u8 = json.loads(
                            urlopen(channel["playUrl"]).read().decode("utf-8")
                        )["u"]
                        channel_cache[channel["chnCode"]] = {
                            "m3u8": m3u8
                        }

                    m3u_channel = m3u.Channel(
                        tvg_id=channel["chnCode"],
                        tvg_name=channel["chnName"],
                        tvg_logo=tvg_logo,
                        group_title="GITV",
                        m3u8=m3u8
                    )

                    m3u_channel_list.append(m3u_channel)

                    programme_title = channel["title"]
                    programme_start = datetime.fromtimestamp(
                        channel["startTime"] / 1000)
                    programme_stop = datetime.fromtimestamp(
                        channel["endTime"] / 1000)

                    xmltv_channel = xmltv.Channel(
                        channel_id=channel["chnCode"],
                        display_name=channel["chnName"],
                        programme_title=programme_title,
                        programme_start=programme_start,
                        programme_stop=programme_stop
                    )

                    xmltv_channel_list.append(xmltv_channel)

                    print(f"频道：{channel['chnName']}")

                # 保存 M3U 文件
                with open("gitv.m3u", "w", encoding="utf-8") as f:
                    f.write(m3u.M3u(m3u_channel_list).generate_text())

                # 保存 XMLTV 文件
                with open("gitv.xml", "w", encoding="utf-8") as f:
                    f.write(xmltv.Xmltv(xmltv_channel_list).generate_text())

                # 保存缓存
                json.dump(channel_cache, open("cache.json", "w"))

                print("更新完成！")

                time.sleep(config["update_interval"])

            except KeyboardInterrupt:
                sys.exit()

            except Exception as e:
                print(e)


class HttpServerThread(Thread):
    def __init__(self, threadID, name, delay):
        Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.delay = delay

    def run(self):
        server = HTTPServer(
            (config["listen_address"], config["listen_port"]),
            SimpleHTTPRequestHandler
        )
        server.serve_forever()


def main():
    update_files_thread = UpdateFilesThread(1, "UpdateFilesThread", 1)
    http_server_thread = HttpServerThread(2, "HttpServerThread", 2)

    update_files_thread.start()
    http_server_thread.start()

    update_files_thread.join()
    http_server_thread.join()


if __name__ == '__main__':
    main()
```