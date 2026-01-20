---
title: Asterisk + EC20 实现短信收发+语音通话+网络代理
description: 无需 FreePBX，在 Ubuntu 24 实现短信转发和来电通知
date: '2026-01-20'
slug: asterisk-ec20
image: 1.png
categories:
    - tech
tags:
    - Asterisk
    - EC20
    - 移远
    - SIP
    - VoIP
    - 代理
---

## 起因

笔者有一张新加坡 [eight](https://www.eight.com.sg/) 的电话卡，带有一些中国大陆漫游流量，也支持在国内语音漫游和接收短信。之前一直使用备用 Android 机 + [SmsForwarder](https://github.com/pppscn/SmsForwarder) 来接收短信通知，体验还是不错的。不过，想要远程接打电话不太可能，并且想利用这张卡的漫游流量也不太容易。于是，笔者决定研究一下 4G 模块的方案。

## 购买 Quectel EC20 模块

笔者从闲鱼购买了 `EC20CEFAG-512-SGNS` 模块 + USB 转接板 + 天线，总共花费 60 左右，还是很合算的。美中不足的是配套的天线太弱，导致网速很慢，笔者后来又新购了较长的天线。购买时需要注意，EC20 有多个版本，因为我们希望支持通话和短信，建议直接购买全功能的 `EC20CEFAG` 版本。另外，购买时最好让商家检查一下模块固件版本，确保是 `EC20CEFAGR06AXXM4G` 或者 `EC20CEFAGR08AXXM4G`，具体原因下面会说明。

## 更新固件

刚刚到手时，EC20 模块的固件版本是 `EC20CEFAGR06A10M4G`。笔者测试了 eight 电话卡，功能正常，但笔者的中国电信卡却无法进行短信收发和语音通话。经过一番查找，发现 R06 基线的固件较老，对新版中国电信卡的支持不好，需要升级到新的 R08 基线固件。

EC20 的固件获取比较麻烦，因为移远没有把固件放在官网上。许多人是通过在[论坛](https://forumschinese.quectel.com/)发帖的方式获得固件的，不过论坛上的技术支持回复往往较慢。笔者由于在淘宝上的移远旗舰店购买过一些东西，所以直接联系客服获取了最新的 R08 固件。另外闲鱼上也有一些卖家出售固件。截止笔者写作时（2026/01/20），最新的 EC20 固件版本是 `EC20CEFAGR08A03M4G`。

获取固件之后，从[官网](https://www.quectel.com.cn/download-zone)下载 Quectel QFlash 工具，按照 PDF 里的说明更新固件即可。

## 配置模块

笔者使用的系统为 Ubuntu 24。下面的测试均使用中国电信卡进行。

### 连接到串口

首先在 Ubuntu 上安装 `minicom`：

```bash
sudo apt install minicom
```

然后插入模块，检查 `/dev/` 下新增的设备，会出现四个 `/dev/ttyUSB*` 设备：

```bash
/dev/ttyUSB0  /dev/ttyUSB1  /dev/ttyUSB2  /dev/ttyUSB3
```

其中，`/dev/ttyUSB2` 是 AT 命令端口，使用 `minicom` 连接：

```bash
sudo minicom -D /dev/ttyUSB2
```

### 重置模块

输入 `AT+QPRTPARA=3` 重置模块，避免之前的配置影响测试。之后输入 `AT+CFUN=1,1` 重启模块。

### AT 命令测试

首先查看下模块信息。输入 `ATI`：

```
Quectel
EC20F
Revision: EC20CEFAGR08A03M4G

OK
```

固件版本已经是最新的 R08 基线。接下来输入 `AT+COPS?`，查看注册状态：

```
+COPS: 0,0,"CHN-CT",7

OK
```

可以看到，已经成功注册到中国电信网络了。

### 配置 VoLTE（可选）

VoLTE 有助于提高语音通话质量，并且类似 eight 这样的国外卡在国内必须使用 VoLTE 才能进行语音通话。输入 `AT+QCFG="ims",1` 启用 VoLTE。

之后，使用 `AT+QCFG="ims"` 检查当前 VoLTE 状态，如果显示 `"ims",1,1` 则表示成功激活。

### 配置 UAC 数字音频（可选）

UAC 数字音频也有助于提高通话质量。输入 `AT+QCFG="usbcfg",0x2C7C,0x0125,1,1,1,1,1,0,1`。之后在 Ubuntu 终端运行 `aplay -L`，可以看到新增了音频设备：

```bash
hw:CARD=Android,DEV=0
    Android, USB Audio
    Direct hardware device without any conversions
```

### 配置网络

为了方便之后配置代理，现在可以修改好模块的网络模式。输入 `AT+QCFG="usbnet",1`，将 USB 网络模式设置为 ECM 模式。之后输入 `AT+CFUN=1,1` 重启模块。重启后，Ubuntu 会自动识别出一个新的网络接口 `enx...`。

### 退出 minicom

按下 `Ctrl-A`，然后按 `X`，选择 `Yes` 退出 minicom。

## 安装 Asterisk

笔者此处和其他教程的区别是没有使用 FreePBX，而是直接使用 Asterisk 进行配置。可以将 FreePBX 看作是 Asterisk 的一个图形化管理界面，由于我们的使用场景较为简单，可以直接手动配置 Asterisk，免去了安装 FreePBX 的麻烦。

### 安装 Asterisk 和依赖

```bash
sudo apt install asterisk asterisk-dev adb git autoconf automake libsqlite3-dev build-essential libasound2-dev alsa-utils
```

### 编译安装 asterisk-chan-quectel 模块

```bash
git clone https://github.com/IchthysMaranatha/asterisk-chan-quectel
cd asterisk-chan-quectel
```

笔者这里按照[另一篇文章](https://blog.wsl.moe/2023/03/%E5%AE%89%E8%A3%85%E5%9F%BA%E4%BA%8E-quectel-ec20-%E6%A8%A1%E5%9D%97%E7%9A%84%E7%9F%AD%E4%BF%A1%E5%8F%8A%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%8F%91%E6%9C%8D%E5%8A%A1/)的说明，修改了 `pdu.c` 文件中 663 行左右的代码：

```c
int i = 0;
int sca_digits = (pdu[i++] - 1) * 2;
int field_len = pdu_parse_number(pdu + i, pdu_length - i, sca_digits, sca, sca_len);
```

修改为：

```c
int i = 0;
int sca_digits = (pdu[i++] - 1) * 2;
if (pdu[i-1] == 0) {
    return i;
}
int field_len = pdu_parse_number(pdu + i, pdu_length - i, sca_digits, sca, sca_len);
```

之后运行 `asterisk -V`，查看 Asterisk 版本号：

```
Asterisk 20.6.0~dfsg+~cs6.13.40431414-2build5
```

然后以下命令，编译安装 asterisk-chan-quectel 模块：

```bash
./bootstrap
./configure DESTDIR=/usr/lib/x86_64-linux-gnu/asterisk/modules --with-astversion=20.6.0
make
sudo make install
```

之后，将 `quectel.conf` 复制到 `/etc/asterisk/` 目录下。如果你之前激活了 UAC 数字音频，将配置文件末尾部分中的两行取消注释：

```ini
[quectel0]
audio=/dev/ttyUSB1		         ; tty port for Audio, set as ttyUSB4 for Simcom if no other dev present
data=/dev/ttyUSB2		         ; tty port for AT commands; 		no default value
quec_uac=1                              ; Uncomment line if using UAC mode
alsadev=hw:CARD=Android,DEV=0           ; Uncomment if using UAC, set device name or index as reqd
```

最后，运行 `sudo systemctl restart asterisk` 重启 Asterisk 服务。

### 设置权限

Ubuntu 安装的 Asterisk 默认使用 `asterisk` 用户运行，该用户无权访问 `/dev/ttyUSB` 设备。需要将该用户添加到 `dialout` 组：

```bash
sudo usermod -aG dialout asterisk
```

另外，Ubuntu 上默认安装的 modemmanager 也会干扰 EC20 模块的使用，将其禁用：

```bash
sudo systemctl stop ModemManager
sudo systemctl disable ModemManager
```

之后重启系统。

### 检查 EC20 模块状态

重启后，运行 `sudo asterisk -rvvv` 进入 Asterisk CLI，输入 `quectel show device state quectel0` 检查模块状态：

```
-------------- Status -------------
  Device                  : quectel0
  State                   : Free
  Audio                   : /dev/ttyUSB1
  Data                    : /dev/ttyUSB2
  Voice                   : Yes
  SMS                     : Yes
  Manufacturer            : Quectel
  Model                   : EC20F
  Firmware                : EC20CEFAGR08A03M4G
  IMEI                    : XXXXXX
  IMSI                    : XXXXXX
  GSM Registration Status : Registered, home network
  RSSI                    : 27, -59 dBm
  Mode                    : No Service
  Submode                 : No service
  Provider Name           : CHN-CT
  Location area code      : XXXXXX
  Cell ID                 : XXXXXX
  Subscriber Number       : Unknown
  SMS Service Center      : XXXXXX
  Use UCS-2 encoding      : Yes
  Tasks in queue          : 0
  Commands in queue       : 0
  Call Waiting            : Disabled
  Current device state    : start
  Desired device state    : start
  When change state       : now
  Calls/Channels          : 0
    Active                : 0
    Held                  : 0
    Dialing               : 0
    Alerting              : 0
    Incoming              : 0
    Waiting               : 0
    Releasing             : 0
    Initializing          : 0
```

以上内容说明已经成功注册到中国电信网络，并且 Asterisk 能够正常访问 EC20 模块。由于是电信卡，我们可以向 10000 发送一条免费短信进行测试：

```
quectel sms quectel0 10000 "cxll"
```

看到 `Successfully sent SMS message` 即表示发送成功。如果不出意外，几秒钟后可以在终端里看到运营商的回复短信。

## 配置短信转发和语音通话

### 配置 SIP 账号

首先编辑 `/etc/asterisk/pjsip.conf`，在文件末尾添加以下内容：

```ini
[transport-udp]
type=transport
protocol=udp
bind=0.0.0.0

[1001]
type=endpoint
context=from-internal
disallow=all
allow=ulaw,alaw,g722,gsm
auth=auth1001
aors=1001
rewrite_contact=yes
rtp_symmetric=yes

[auth1001]
type=auth
auth_type=userpass
username=1001
password=YourStrongPassword ; 请修改为强密码

[1001]
type=aor
max_contacts=1
```

这里我们创建了一个 SIP 账号，后续我们将把 EC20 模块的来电转发到该账号，并将该账号拨出的电话通过 EC20 模块拨出。

### 禁用 chan_sip 模块

由于我们使用了 `chan_pjsip`，需要禁用默认的 `chan_sip` 模块，否则会产生冲突。编辑 `/etc/asterisk/modules.conf`：

```ini
[modules]
autoload=yes

; Do not load the chan_sip since we are using chan_pjsip
noload => chan_sip.so
```

### 配置 extensions_custom.conf

现在我们来配置短信转发和语音通话。新建 `/etc/asterisk/extensions_custom.conf`，添加以下内容：

```ini
[from-internal]
exten => _[+0-9].,1,NoOp(Calling out via EC20: ${EXTEN})
same => n,Dial(Quectel/quectel0/${EXTEN})
same => n,Hangup()

[incoming-mobile]
; --- 短信处理 ---
exten => sms,1,Verbose(Incoming SMS from ${CALLERID(num)})
; 运行短信通知脚本
same => n,System(/usr/bin/python3 /etc/asterisk/scripts/sms_notify.py "${CALLERID(num)}" "${SMS_BASE64}" &)
; 保存短信内容到本地
same => n,System(echo '${STRFTIME(${EPOCH},,%Y-%m-%d %H:%M:%S)} - ${QUECTELNAME} - ${CALLERID(num)}: ${BASE64_DECODE(${SMS_BASE64})}' >> /var/log/asterisk/sms.txt)
same => n,Hangup()

; --- USSD 处理 ---
exten => ussd,1,Verbose(Incoming USSD: ${BASE64_DECODE(${USSD_BASE64})})
same => n,System(echo '${STRFTIME(${EPOCH},,%Y-%m-%d %H:%M:%S)} - ${QUECTELNAME}: ${BASE64_DECODE(${USSD_BASE64})}' >> /var/log/asterisk/ussd.txt)
same => n,Hangup()

; --- 语音来电处理 ---
exten => s,1,NoOp(Incoming call from ${CALLERID(num)})
same => n,Set(CALLERID(all)="${CALLERID(num)}" <${CALLERID(num)}>)
; 运行来电通知脚本
same => n,System(/usr/bin/python3 /etc/asterisk/scripts/call_notify.py "${CALLERID(num)}" &)
; 保存来电记录到本地
same => n,System(echo '${STRFTIME(${EPOCH},,%Y-%m-%d %H:%M:%S)} - ${QUECTELNAME} - Incoming call from ${CALLERID(num)}' >> /var/log/asterisk/calls.txt)

; 设置循环参数
same => n,Set(MAX_RETRIES=8) ; 每 5 秒检查一次，共等待 40 秒
same => n,Set(COUNTER=0)

; 循环检查点
same => n(check_reg),NoOp(Checking if 1001 is online... Attempt ${COUNTER})
; 检查 PJSIP 1001 是否上线
same => n,Set(CONTACTS=${PJSIP_DIAL_CONTACTS(1001)})

; 如果有地址，跳转到拨号
same => n,GotoIf($[ "${CONTACTS}" != "" ]?dial_now)

; 如果无地址，判断是否超时
same => n,Set(COUNTER=$[${COUNTER} + 1])
same => n,GotoIf($[${COUNTER} >= ${MAX_RETRIES}]?timeout)

; 未超时则等待 5 秒重试
same => n,Ringing() ; 向主叫方播放回铃音
same => n,Wait(5)
same => n,Goto(check_reg)

; 拨号分支
same => n(dial_now),NoOp(1001 is online, dialing...)
same => n,Dial(PJSIP/1001,30)
same => n,Hangup()

; 超时分支
same => n(timeout),NoOp(1001 did not register in time. Hanging up.)
same => n,Hangup()
```

这里我们创建了两个拨号计划：`from-internal` 用于处理从 SIP 账号拨出的电话，`incoming-mobile` 用于处理来自 EC20 模块的短信和来电。相比与其他教程中的配置，该配置有如下特点：

+ 支持拨国际号码（以 `+` 开头的号码）
+ 短信、UUSD 和来电会被储存到本地文件中。同时，在收到短信和来电时，会调用 `/etc/asterisk/scripts` 中的外部 Python 脚本进行通知。如果你不需要脚本功能，可以将相关行删除
+ 一般来说，SIP 客户端需要保持在线，才能接听到来电。但这要求手机上的客户端一直与服务端连接，一是耗电，二是容易被手机系统杀进程，很不稳定。如果客户端不在线，按照其他教程中的设置，来电会被直接挂断。这里我们设置了一个循环检查机制，来电时如果客户端不在线，则会每 5 秒检查一次 SIP 客户端是否在线，最多等待 40 秒。由于来电时 Python 脚本将通知发送到微信，用户看到通知后会立即去打开 SIP 客户端。如果在 40 秒内客户端上线，则来电可以接通；如果超时，则 Asterisk 会挂断来电

Python 脚本可以按照如下框架编写：

```python3
# sms_notify.py

import sys
import requests
import base64

caller_id = sys.argv[1]
msg_base64 = sys.argv[2]

def send_notification(cid, b64_content):
    try:
        content = base64.b64decode(b64_content).decode('utf-8')
    except:
        content = "Decode Error"

    # ...

if __name__ == "__main__":
    send_notification(caller_id, msg_base64)
```

```python3
# call_notify.py

import sys
import requests

caller_id = sys.argv[1]

def send_notification(cid):
    # ...

if __name__ == "__main__":
    send_notification(caller_id)
```

配置完 `extensions_custom.conf` 后，需要在 `/etc/asterisk/extensions.conf` 中包含该文件。在 `/etc/asterisk/extensions.conf` 末尾添加：

```ini
#include extensions_custom.conf
```

最后，重启 Asterisk 服务：

```bash
sudo systemctl restart asterisk
```

## SIP 客户端设置

笔者使用 [Groundwire](https://play.google.com/store/apps/details?id=cz.acrobits.softphone.aliengroundwire) 作为 Android 系统上的 SIP 客户端。

配置时，新建 SIP 账号，用户名填写 `1001`，密码填写之前在 `pjsip.conf` 中设置的密码，域名填写 Asterisk 所在机器的 IP 地址或者域名。

配置完成后，可以拨打 10000 进行测试。也可以顺便测试一下短信接收的通知脚本是否工作正常。

如果你想测试接听电话，可以先完全关闭 Groundwire，然后用另一个手机拨打 EC20 模块的号码。此时主叫手机会听到 5 秒一次的回铃音。重新打开 Groundwire，等待片刻，即可收到来电，接听后双方可以正常通话。

## 网络代理

待更新。

## 参考资料及致谢

+ [IchthysMaranatha/asterisk-chan-quectel](https://github.com/IchthysMaranatha/asterisk-chan-quectel)

本文大量参考了以下两篇文章：

+ [安装基于 Quectel EC20 模块的短信及语音转发服务](https://blog.wsl.moe/2023/03/%E5%AE%89%E8%A3%85%E5%9F%BA%E4%BA%8E-quectel-ec20-%E6%A8%A1%E5%9D%97%E7%9A%84%E7%9F%AD%E4%BF%A1%E5%8F%8A%E8%AF%AD%E9%9F%B3%E8%BD%AC%E5%8F%91%E6%9C%8D%E5%8A%A1/)
+ [使用 EC20 模块配合 Asterisk 及 FreePBX 实现短信转发和网络电话](https://blog.sparktour.me/posts/2022/10/08/quectel-ec20-asterisk-freepbx-gsm-gateway/)

以及，感谢 Google Gemini 的帮助。

