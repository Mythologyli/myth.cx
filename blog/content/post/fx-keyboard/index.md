---
title: fxKeyboard | 把你的计算器当做电脑键鼠！
description: 既然每天带着计算器上课，何不将计算器作为键盘？
date: 2021-04-28
slug: fx-keyboard
image: 2.png
categories:
    - tech
tags:
    - 计算器
---

## 前言

**警告：本程序可能损害您的计算器或电脑！务必在阅读说明后谨慎操作。本人不对任何损坏负责！**

Surface 的键盘在竞品中算是手感不错的，可没有数字区同样令人抓狂。既然每天带着计算器上课，何不将计算器作为键盘？

## 功能

+ 数字、字母输入
+ 连续字符输入。如按下 sin 输入 sin
+ 电脑截屏。CAPTURE 映射 PrintScreen
+ 方向键、鼠标控制模式切换
+ ...

## 使用方法

1. 使用 FA-124 软件将 Add-in 复制到您的计算器
2. 使用计算器菜单中的 LINK 将计算器连接到计算机
3. 在执行此步骤之前，请先阅读注意事项！从这里下载 Zadig。打开 Zadig，单击 Options - List All Device，选择 CESG502，然后将原始驱动程序替换为 WinUSB
4. 在您的计算器中打开 Add-in。它将自动连接到您的计算机。 如果您没有插入 USB 线缆，则不久后 Add-in 将提示退出
5. 打开计算机中的 fxKeyboardLink.exe。现在，您可以将计算器用作计算机的键盘！
6. 特殊映射：

    | Calculator Key | Computer |
    | ---- | ---- |
    | OPTN | Switch between arrow mode and cursor mode |
    | Arrow keys | Arrow keys in arrow mode and cursor controller in cursor mode |
    | θ | Text: theta |
    | EXIT | ESC |
    | QUIT | ESC |
    | ∠ | < |
    | sin-1 | Text: arcsin |
    | ab/c | / |
    | CAPTURE | PrintScreen |
    | CLIP | Ctrl + C |
    | PASTE | Ctrl + V |
    | DEL | Backspace |
    | INS | Insert |
    | ÷ | / |
    | π | Text: pi |
    | EXE | Enter in arrow mode and click in cursor mode |
    | EXE with SHIFT | Enter with Shift pressed. This is convenient for using Mathmetica |

## 注意事项

+ fxKeyboardLink.exe 将自动打开 NumLock
+ 一旦使用 Zadig 替换了原始驱动程序，您将无法使用 FA-124 连接！如果您想返回原始驱动程序，请仔细阅读[此处](https://github.com/pbatard/libwdi/wiki/FAQ#Help_Zadig_replaced_the_driver_for_the_wrong_device_How_do_I_restore_it)的 Zadig FAQ。您需要知道USB设备为 CESG502
+ 如果一通操作后，您无法以任何方式将计算器连接到计算机，请尝试通过后面的按钮重新启动计算器

## 截图
![](https://download.akashic.cc/fxkeyboard/1.png)

![](https://download.akashic.cc/fxkeyboard/2.png)

### 已知问题

+ 连续按下计算器键将与计算机键盘实际行为不匹配。 原因是我只用了 GetKey 函数（原因是懒）
+ 在光标模式下，光标以恒定的速度缓慢移动（原因还是是懒）

## 开源地址

https://github.com/Mythologyli/fxKeyboard

如果你喜欢本程序的话，欢迎去点一个 Star 哦！

## 下载地址

https://cloud.akashic.cc/#s/6EcqHrhQ