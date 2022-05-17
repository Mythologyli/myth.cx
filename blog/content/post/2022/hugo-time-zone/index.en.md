---
title: Solve articles/pages not rendered problem caused by Hugo's default time zone
description: Oh no! Where is my new page!
date: 2022-05-17
slug: hugo-time-zone
image: 1.png
categories:
    - tech
tags:
    - Hugo
    - Time zone
---

## Problem

At 1:00 a.m. May 17th. I create a page like this:

```yaml {linenos=false}
title: Solve articles/pages not rendered problem in Hugo's default time zone
description: Oh no! Where is my new page!
date: 2022-05-17
```

However, nothing happened.

Then I looked at the console to see the output of `hugo -D server`:

```shell {linenos=false}
Change detected, rebuilding site.
2022-05-17 01:09:56.287 +0800
Source changed ".../index.md": WRITE
Total in 12 ms
```

It found my changes! So why the new page not rendered?

## Solution

It turns out that Hugo will not render future pages by default, nor will it output any prompts indicating that there are pages that have not been rendered because the time has not come. And Hugo considers my page according to UTC time, thinks my page is a future page, so there is no output.

To solve this, you can:

+ Add the time zone info in date field.
+ Configure Hugo to output future pages.

I chose the second way. In config.yaml I set:

```yaml {linenos=false}
buildFuture: true
```

So Hugo will render future pages.

## References

[Hugo Post Missing](https://jdhao.github.io/2020/01/11/hugo_post_missing/) Author: [jdhao](https://jdhao.github.io/)