#!/usr/bin/env python
# coding=UTF-8

import os, sys
import smtplib
from email.mime.text import MIMEText

sys.argv
if len(sys.argv) != 4:
    print("参数个数错误" + str(len(sys.argv)))
    sys.exit(0)

mail_host = "smtp.qq.com"
mail_user = str(sys.argv[1])
mail_pass = str(sys.argv[2])
status_code = int(sys.argv[3])

user_name = os.popen("echo $username").read()
print("用户名：" + str(user_name))

if status_code == 301 or status_code == 200:
    print("网站状态正常" + str(status_code))
    sys.exit(0)

sender = mail_user
receivers = [mail_user]
message = MIMEText('curl cocoafei.top 状态码:' + str(status_code), 'plain', 'utf-8')
message['From'] = "GithubActions <actions@github.com>"
message['To'] = "lifei<cocoafei.top>"
message['Subject'] = 'cocoafei.top 网络故障'

try:
    smtpObj = smtplib.SMTP() 
    smtpObj.connect(mail_host, 587)
    smtpObj.login(mail_user,mail_pass)
    smtpObj.sendmail(sender, receivers, message.as_string())
    print("邮件发送成功")
except smtplib.SMTPException:
    print("无法发送邮件，原因：\n" + str(smtplib.Exception))
