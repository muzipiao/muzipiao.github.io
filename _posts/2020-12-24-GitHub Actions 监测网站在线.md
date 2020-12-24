---
layout: post
title: "GitHub Actions 监测网站在线"
date: 2020-12-24
description: "通过 GitHub Actions 监测网站/Blog是否在线"
tag: GitHub
--- 


## GitHub Actions

GitHub Actions 是 GitHub 的持续集成服务，如果接触过 Jenkins 或 Travis CI，那么对持续集成不会陌生。我们经常使用的功能，在 push 代码到仓库时触发或定时触发抓取代码、自动打包、自动部署到服务器、自动化测试等，都属于持续集成类。GitHub Actions 功能更强大，不仅可以自己添加脚本，而且允许开发者分享自己的脚本到[应用市场](https://github.com/marketplace?type=actions)，其他人使用时直接引用即可。

例如下方所示工作流程，引用应用市场他人脚本`dawidd6/action-send-mail@v2` 可实现 push 代码到仓库时，使用谷歌邮箱自动发送一封 Email 到指定邮箱，内容为 README.md 文本内容。其中 `{% raw %}${{secrets.MAIL_USERNAME}}{% endraw %}` 和 `{% raw %}${{secrets.MAIL_PASSWORD}}{% endraw %}` 分别为邮箱账号和授权码，注意一定**不要在代码中直接使用密码**，密钥类要配置在当前仓库的`Settings/Secrets`目录下，使用`{% raw %}${{secrets.变量名称}}{% endraw %}`引用，具体配置方法，稍后具体说明。

```yml
name: CI 
on:
  push:
    branches: [ master ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Send mail
        uses: dawidd6/action-send-mail@v2
        with:
          server_address: smtp.gmail.com
          server_port: 465
          username: {% raw %}${{secrets.MAIL_USERNAME}}{% endraw %}
          password: {% raw %}${{secrets.MAIL_PASSWORD}}{% endraw %}
          subject: Github Actions job result
          body: file://README.md
          to: obiwan@tatooine.com,yoda@dagobah.com
          from: Luke Skywalker
```

## 监测网站

自建的网站/博客经常会出现 HTTPS 证书过期，服务器宕机等各种情况，这时候需要另外一台服务器定时监测网站是否在线。GitHub Actions 完全可以满足这个需求，通过定时执行脚本，来检测网站是否在线，而且是稳定免费的。

实现思路：

1. 添加一个工作流程 (workflow)，并设置定时触发（每隔 15 分钟）此工作流程；
2. 在工作流程中使用 curl 命令检查 cocoafei.top 的 HTTP 请求状态码；
3. 使用 python 脚本判断状态码，如果不是 200 或 301 就发送邮件通知，是的话忽略。

流程图：

![actions流程图](/images/posts/github_actions/flow_chart.png)

## curl 查询网站状态

curl 功能很强大，我们判断网站是否在线，只需要使用 curl 查询请求网站，获取网站 HTTP 状态码，200/301 时表示网站正常。

* -I 仅测试HTTP头
* -m 15 表示最多查询15s
* -o /dev/null 屏蔽原有输出信息
* -s silent 模式，不输出任何东西
* -w %{http_code} 控制额外输出

```shell
# 这里表示静默获取网站 cocoafei.top 的 HTTP 请求状态码，最多查询 15s
curl -I -m 15 -s -w "%{http_code}\n" -o /dev/null  cocoafei.top
```

![curl 查询结果](/images/posts/github_actions/curl_result.png)

## python 发送 Email

由于需要判断网站状态，网站不在线时再发送邮件，在线时忽略，市场上发送邮件的 Action 不符合需求。

使用 Python 脚本实现判断状态码和发邮件功能，需要传入三个参数，分别是发送邮件的邮箱名称，邮箱授权码和 curl 网站获取的网络状态码。

**警告[FBI WARNING]**⚠️：不要把邮箱授权码写在代码里面，会造成邮箱被盗。

```python
#!/usr/bin/env python
# coding=UTF-8

import os, sys
import smtplib
from email.mime.text import MIMEText

"""
参数 1 SMTP 服务器的用户名，发送邮箱名称
参数 2 SMTP 服务器的密码，发送邮箱授权码（注意非邮箱原密码）
参数 3 curl 网站返回的状态码，如 200
"""
if len(sys.argv) != 4:
    print("参数个数错误" + str(len(sys.argv)))
    sys.exit(0)

# SMTP 服务器名称
mail_host = "smtp.qq.com"
# SMTP 服务器的用户名
mail_user = str(sys.argv[1])
# SMTP 服务器的密码
mail_pass = str(sys.argv[2])
# curl 网站返回的状态码
status_code = int(sys.argv[3])

# cocoafei.top 使用重定向域名，因此会返回 301，表示网站正常，不用发送邮件
if status_code == 301 or status_code == 200:
    print("网站状态正常" + str(status_code))
    sys.exit(0)

# 发送邮箱，这里自己给自己发送一封邮件
sender = mail_user
# 接收邮箱，多个邮箱使用逗号隔开，eg. [1234@qq.com, 5678@126.com]
receivers = [mail_user]
# 邮件正文文字
message = MIMEText('curl cocoafei.top 状态码:' + str(status_code), 'plain', 'utf-8')
# 发件人名称，eg. 发件人：GithubActions <actions@github.com>
message['From'] = "GithubActions <actions@github.com>"
# 收件人名称，eg. 收件人：lifei
message['To'] = "lifei<cocoafei.top>"
# 邮件标题
message['Subject'] = 'cocoafei.top 网络故障'

try:
    smtpObj = smtplib.SMTP()
    # 链接 SMTP 服务器，QQ 发送邮件服务器：smtp.qq.com，使用SSL，端口号465或587
    smtpObj.connect(mail_host, 587)
    # 登录 SMTP 服务器
    smtpObj.login(mail_user,mail_pass)
    # 发送邮件
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功，网站状态码：" + str(status_code))
except smtplib.SMTPException:
    print("无法发送邮件，失败原因：\n" + str(smtplib.Exception))
```

## 添加 Actions

(1) 选择当前仓库，点击 Actions 标签：

![选择 Actions 标签](/images/posts/github_actions/create_action1.png)

(2) 选择自定义工作流程：

![自定义工作流程](/images/posts/github_actions/create_action2.png)

(3) 重命名 yml 文件名称，名称无限制，yml 配置文件基本格式如下：

![yml 文件](/images/posts/github_actions/create_action3.png)

## yml 文件格式

GitHub 只要发现 `.github/workflows` 目录里面有.yml文件，就会自动运行该文件，主要格式：

1. workflow（工作流程）：可简单理解为一个 yml 文件就是一个 workflow。

2. job（任务）：一个 workflow 由一个或多个 jobs 构成，一次可以完成多个任务。

3. step（步骤）：每个 job 由多个 step 构成，一步一步逐个完成。

4. action（动作）：每个 step 可以依次执行一个或多个命令（action）。

如本次定时检查网站是否在线的 yml 文件，不用监听 push/pull 请求触发，定时触发，每 15 分钟执行一次 curl 命令，并将返回的 HTTP 状态码存储在变量 status_code，将发送邮件的邮箱账号、密码和status_code 的值传入 python 脚本中，如果不是 200/301 就发送通知邮件。

```shell
# 获取 cocoafei.top 的 HTTP 状态码，并将返回的 HTTP 状态码存储在变量 status_code
export status_code=$(curl -I -m 15 -s -w "%{http_code}\n" -o /dev/null  cocoafei.top)
# 将发送邮件的邮箱账号、密码和status_code 传入 Python 脚本，判断是否需要发送邮件
python ./email_status.py {% raw %}${{secrets.MAIL_USERNAME}}{% endraw %} {% raw %}${{secrets.MAIL_PASSWORD}}{% endraw %} $status_code
```

监测网站的完整 yml 文件如下，可参考下方注释理解。

```yml
# 工作流程 (workflow) 名称
name: cocoafei.top

# 触发条件
on:
  # 每天每 15 分钟运行一次此工作流
  schedule:
    - cron: '*/15 * * * *'

# 任务，一个工作流程由一个或多个任务 (job) 构成
jobs:
  # build 任务，这个工作流程包含一个名称为 "build" 的任务 (job)
  build:
    # 任务 (job) 运行的环境类型，运行在虚拟机环境 ubuntu-latest
    runs-on: ubuntu-latest

    # 步骤 (step) 表示将作为任务 (job) 一部分执行的一系列任务
    steps:
      # 第一步是获取源码，引用现成的检出 action，将代码检出到虚拟机上
      - uses: actions/checkout@v2
      
      # 运行一组 shell 名称，获取 cocoafei.top 的网站状态，并判断是否需要发送邮件
      - name: Get cocoafei.top response status code.
        run: |
          export status_code=$(curl -I -m 15 -s -w "%{http_code}\n" -o /dev/null  cocoafei.top)
          python ./email_status.py {% raw %}${{secrets.MAIL_USERNAME}}{% endraw %} {% raw %}${{secrets.MAIL_PASSWORD}}{% endraw %} $status_code

```

## on 触发条件

可以通过 push 或 pull 请求事件触发工作流，或定时触发工作流，并可指定分支。

```yml
name: cocoafei.top
# 此工作流程的触发条件
on:
  # push 或 pull 请求事件触发工作流，且仅针对 master 分支
  push:
    branches: [ master ]
  pull_request:
    branches: [ master ]
  # 每天每 15 分钟运行一次此工作流
  schedule:
    - cron: '*/15 * * * *'
```

schedule 计划任务语法有五个字段，中间用空格分隔，每个字段代表一个时间单位。

```yml
# 计划任务语法有五个字段，中间用空格分隔，每个字段代表一个时间单位。
on:
  schedule:
    # 每 15 分钟运行一次此工作流
    - cron: '*/15 * * * *'
    # 每 5 分支运行一次此工作流
    - cron: '*/15 * * * *'
    # 每天在国际标准时间 20 点（北京时间早上 4 点）运行一次此工作流
    - cron: '0 20 * * *'
    # 每周一在国际时间下午 1 点（北京时间下午 9 点）运行一次此工作流
    - cron: '0 13 * * 1'
    # 每天国际时间 0 点（北京时间上午 8 点）运行一次此工作流
    - cron: '0 0 * * *'
    
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12 or JAN-DEC)
│ │ │ │ ┌───────────── day of the week (0 - 6 or SUN-SAT)
│ │ │ │ │                                   
│ │ │ │ │
│ │ │ │ │
* * * * *
```

您可在这五个字段中使用以下运算符：

| 运算符 |	描述 | 示例 |
| --- | --- | --- |
| * |	任意值 |	* * * * * 在每天的每分钟运行。|
| , |	值列表分隔符 |	2,10 4,5 * * * 在每天第 4 和第 5 小时的第 2 和第 10 分钟运行。|
| - |	值的范围 |	0 4-6 * * * 在第 4、5、6 小时的第 0 分钟运行。|
| / |	步骤值 |	20/15 * * * * 从第 20 分钟到第 59 分钟每隔 15 分钟运行（第 20、35 和 50 分钟）。|

## 配置 Secrets 变量

由于 Python 脚本使用 QQ 邮箱发送 Email，QQ 邮箱不允许直接使用密码，需要提前获取 QQ 邮箱授权码，具体获取方法，先登录 QQ 邮箱，在路径`设置-账户-POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务`，根据提示，查看说明开启获取授权码即可，其他邮箱操作类似。

(1) 选择当前仓库的 Setting 目录，在 `Settings/Secrets`，可看到如下界面：

![选择 Secrets](/images/posts/github_actions/add_secrets1.png)

(2) 选择 `New repository secret` 按钮，看到如下画面，填入变量名称（如 MAIL_PASSWORD）和变量值（如获取的邮箱授权码），点击 `Add secret` 保存。

![添加 Secret](/images/posts/github_actions/add_secrets2.png)

(3) 通过 `{% raw %}${{secrets.变量名称}}{% endraw %}` 使用变量值（例如 `{% raw %}${{secrets.MAIL_PASSWORD}}{% endraw %}`）。

## 自动执行效果

![执行效果](/images/posts/github_actions/run_result1.png)

![执行效果](/images/posts/github_actions/run_result2.png)

![执行效果](/images/posts/github_actions/run_result3.png)

![执行效果](/images/posts/github_actions/run_result4.png)

## 参考

[官方文档-触发工作流程的事件](https://docs.github.com/cn/free-pro-team@latest/actions/reference/events-that-trigger-workflows)

[示例-定时发送天气](http://www.ruanyifeng.com/blog/2019/12/github_actions.html)

[示例-GitHub Actions](http://www.ruanyifeng.com/blog/2019/09/getting-started-with-github-actions.html)
