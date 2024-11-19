#!/usr/bin/env python
# coding=UTF-8

import os, sys
import smtplib
from email.mime.text import MIMEText


"""
参数 0 脚本文件名称
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

# muzipiao.github.io/ 使用重定向域名，因此会返回 301，表示网站正常，不用发送邮件
if status_code == 301 or status_code == 200:
    print("网站状态正常" + str(status_code))
    sys.exit(0)

# 发送邮箱，这里自己给自己发送一封邮件
sender = mail_user
# 接收邮箱，多个邮箱使用逗号隔开，eg. [1234@qq.com, 5678@126.com]
receivers = [mail_user]
# 邮件正文文字
message = MIMEText("curl muzipiao.github.io/ 状态码:" + str(status_code), "plain", "utf-8")
# 发件人名称，eg. 发件人：GithubActions <actions@github.com>
message["From"] = "GithubActions <actions@github.com>"
# 收件人名称，eg. 收件人：lifei
message["To"] = "lifei<muzipiao.github.io/>"
# 邮件标题
message["Subject"] = "muzipiao.github.io/ 网络故障"

try:
    smtpObj = smtplib.SMTP()
    # 链接 SMTP 服务器，QQ 发送邮件服务器：smtp.qq.com，使用SSL，端口号465或587
    smtpObj.connect(mail_host, 587)
    # 登录 SMTP 服务器
    smtpObj.login(mail_user, mail_pass)
    # 发送邮件
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功，网站状态码：" + str(status_code))
except smtplib.SMTPException:
    print("无法发送邮件，失败原因：\n" + str(smtplib.Exception))
