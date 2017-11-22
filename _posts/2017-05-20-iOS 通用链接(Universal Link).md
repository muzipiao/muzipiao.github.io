
---
layout: post
title: " iOS 通用链接(Universal Link)"
date: 2017-05-20
description: " iOS通过Universal Link打开App功能"
tag: iOS
---

## iOS 通用链接(Universal Link)

> **Apple通用链接：**一种能够方便的通过传统 `HTTP` 链接来启动 APP, 使用相同的网址打开网站和APP。
> 
> 通过唯一的网址, 不需要特别的schema就可以链接一个特定的视图到APP里面 。
> 
> **比如：**在微信中使用了**通用链接**, 那么用户在Safari、UIWebView或者 WKWebView点击一个链接, iOS设备上的微信app怎会在微信里面**自动打开这个页面**, 如果**没有安装**则在Safrai中**打开响应链接**。

### 一、系统要求：

**iOS 9及以上**系统，iOS 9以下仍旧用**URL Scheme**实现跳转。

### 二、使用方法：

1. 在**苹果开发者网站**中打开需要使用`Universal Link`功能的App中的`Associated Domains`。
2. 创建一个json格式的`apple-app-site-associatio`,上传`apple-app-site-association`到服务器根目录下。
3. 在**AppDelegate**中实现相应的方法。

### 三、对比URL Scheme

1. 由`其他应用`跳转到App或App对应界面，或跳转到其他App`仍旧使用URL Scheme`。
2. `Universal Link`适用于`App跳转功能`，且待跳转功能配置文件存储在服务器，更加灵活。
3. App已经安装的前提下：直接`启动App`然后现实链接内容。
4. App没有安装的前提下：Web上`继续显示`链接内容。

### 四、参数以及安全性

1. 由于路径完全是**自定义**的，自由度很高，可以通过拼接路径的方式**带参数**；例如/path/x/parameter。
2. 未安装App会直接在浏览器中继续打开链接，因此不能够带**敏感信息**。

### 五、注意点

1. 首先你的**服务器**必须得**支持SSL**，必须支持**HTTPS**；我们只需要把配置好的json文件上传到服务器中该域名的根目录下，言下之意，我们可以用**GET请求**可以获取到https://www.example.com/apple-app-association；当我们的App在设备上第一次运行时，如果支持**Associated Domains**功能，那么iOS会**自动**去GET定义的Domain下的apple-app-site-association文件。
2. **服务器上apple-app-site-association的更新不会让iOS本地的apple-app-site-association`同步更新`，即iOS只会在App第一次启动时`请求一次`，以后除非App更新或重新安装，否则不会在每次打开时请求apple-app-site-association。**
3. `非系统原生App`不一定能支持直接点击URL跳转，例如在微信中点击URL会首先在微信内的WebView打开，如果要跳转只能再通过Safari打开。
4. 从9.3.X改版之后，通用链接不支持`域内跳转`了，跳转前后的两个domain必须是不同的，否则只会safari打开。跨域问题：假设当前网页的地址为 yoursite.com/a/\*，如果要跳转的链接也是 yoursite.com/a/\* 这个域下的，系统将不会进行拉起应用的操作，必须要跳转不同的子域，例如 yoursite.com/b/\* 时，系统才会根据关联文件去判断是否要拉起应用。
