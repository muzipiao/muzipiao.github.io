---
layout: post
title: "iOS 钥匙串 Keychain 安全机制"
date: 2017-05-08 
description: "iOS 钥匙串的通俗描述"
tag: iOS 
---  


## iOS钥匙串Keychain安全机制

### **一、Keychain简介：**


* iOS的钥匙串Keychain是苹果的一种安全机制，可理解为苹果系统的`保险柜`，我们可以将重要的东西保存在里面，例如用户名，密码，VPN凭证等等。
* Keychain的实质是一个安全的数据库，Keychain里面的所有数据都是加密的。

### **二、Keychain保存特性：**

* QQ是我们经常用的App，当我们卸载QQ又重新安装后，惊奇的发现，用户名和密码还在，自动填充到了输入框里面。这就是利用了Keychain的特性，Keychain里保存的信息不会因App被删除而丢失，所以在重装App后，Keychain里的数据还能使用。
* 注意，恢复出厂设置可清空钥匙串里面的信息。

### **三、Keychain安全性：**

* 我们知道，iOS系统下每个应用都有自己对应的沙盒，每个沙盒之间都是相互独立的，互不能访问（没有越狱的情况下），正因为这样的沙盒机制让iOS的系统变得更安全。
* 同理，不同App之间Keychain是不能相互访问的，除非是同一供应商开发的App(例如腾讯公司开发的“QQ”和“微信”属于同一供应商)，经过设置后可访问设置共有钥匙串部分信息。简单来说就是自己公司开发的App能访问自己的钥匙串，别的公司是无法访问你的App的钥匙串的。
* 钥匙串Keychain的安全性依赖于苹果提供的安全，尽管苹果系统是安全的，苹果系统里面的加密的Keychain更加安全，但出于高安全的考虑，我们尽量避免明文储存密码等敏感信息，一般都是加密后存储在Keychain里面，增加安全系数。
* 同一公司开发的App可设置共享部分。如图：

3.1、未对应用APP的进行配置时，会默认存储在自身BundleID的条目下，不能相互访问。

![ ](/images/posts/keychain/appKeychain1.png)

3.2、对APP的进行配置后，APP具有对某个条目的访问权限。

![ ](/images/posts/keychain/appKeychain2.png)

### **四、App使用的钥匙串Keychain与iPhone中的的钥匙串的区别**

4.1、iPhone中的钥匙串功能：保存各种密码、WiFi、appleID、网站密码等等。

![ ](/images/posts/keychain/iosKeychainSw.png)

4.2、App中的钥匙串Keychain主要是保存App的用户名密码等重要信息。

![ ](/images/posts/keychain/keychainSw.png)

### **五、App的Keychain清除条件**

|操作条件|更换Apple ID|还原所有设置|抹掉所有内容和设置|还原网络设置|还原键盘字典|还原主屏幕布局|还原位置与隐私|
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
|是否清除Keychain数据|否|否|是|否|否|否|否|

> - 更换Apple ID，不会抹去应用App和Keychain内容。这一点我开始有点主观臆断，以为Apple ID和Windows用户一样，不同用户间互不干扰。更换Apple ID后，App仍旧能读取存储在Keychain的内容。更换Apple ID只会抹除照片图库，通讯录，Safari的账户信息等。
> - 还原所有设置，不能删除App，也不能删除Keychain。
> - 抹掉所有内容和设置会清空手机，并清空Keychain里面的内容。
> - 还原网络设置，将删除所有的网络设置，将WiFi，4G等网络设置还原为出厂设置。
> - 还原键盘字典，将删除键盘上键入的所有自定义字，并将键盘字典恢复为出厂设置。
> - 还原主屏幕布局，将主屏幕还原为厂家默认的布局。
> - 还原位置与隐私，会将手机的位置和隐私设置还原为厂家默认值。


