---
layout: post
title: "RSA使用NSString格式公钥加密"
date: 2016-12-11 
description: "iOS使用NSString格式公钥私钥进行加密解密"
tag: RSA 
---   

#### 前言：

> RSA加密在iOS中经常用到，麻烦的方法是使用openssl生成所需秘钥文件，
> 需要用到.der和.p12后缀格式的文件，其中.der格式的文件存放的是公钥（Public key）用于加密，
> .p12格式的文件存放的是私钥（Private key）用于解密。
> 

然而，有没有简单的方法，仅仅通过NSString字符串格式的公钥和私钥就可以进行方便的加密解密？答案是肯定的。

**`warning:`** 使用此封装类，需要用到iOS`keychain sharin`，所以一定要打开项目的钥匙串keychain🔑开关。

**`路径:`**Xcode8 中选中targets -> capabilities -> keychain sharing 将这个开关打开

**项目钥匙串开关**

![RSA序列图](https://raw.githubusercontent.com/muzipiao/GitHubImages/master/RSAImage/RSAImg0.png)


#### 常见使用场景(客户端加密交易密码发送给服务器)：

客户端向服务器请求`RSA公钥`----->`服务器`----->返给客户端一个`NSString`格式的RSA公钥----->客户端用`RSA公钥字符串`加密`密码`发送给服务器----->服务器用RSA私钥解密并核对`密码`----->核对结果(Y/N)返回给客户端

**RSA加密序列图**

![RSA序列图](https://raw.githubusercontent.com/muzipiao/GitHubImages/master/RSAImage/RSAImg1.png)

**RSA加密关系图**

![RSA序列图](https://raw.githubusercontent.com/muzipiao/GitHubImages/master/RSAImage/RSAImg2.png)


#### 注意：

例如：这是一串服务器生成的RSA公钥

> MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDTbZ6cNH9
> PgdF60aQKveLz3FTalyzHQwbp601y77SzmGHX3F5NoVUZbd
> K7UMdoCLK4FBziTewYD9DWvAErXZo9BFuI96bAop8wfl1Vk
> ZyyHTcznxNJFGSQd/B70/ExMgMBpEwkAAdyUqIjIdVGh1FQ
> K/4acwS39YXwbS+IlHsPSQIDAQAB
>

但由于含有`/+=\n`等特殊字符串，网络传输过程中导致转义，进而导致加密解密不成功，解决办法是进行URL特殊符号编码解码(百分号转义)；具体示例，在Demo中有示例，文章最下方有`链接`。

#### RSA用NSString加密解密示例，非常简单

```Objective-C
    //----------------------RSA加密示例------------------------
    //原始数据，要加密的字符串
    NSString *originalString = @"这是一段将要使用'秘钥字符串'进行加密的字符串!";
    
    //使用字符串格式的公钥私钥加密解密, RSAPublickKey为公钥字符串(NSString格式)
    NSString *encryptStr = [RSAEncryptor encryptString:originalString publicKey:RSAPublickKey];
    
    NSLog(@"加密前:%@", originalString);
    NSLog(@"加密后:%@", encryptStr);
    //用私钥解密，RSAPrivateKey为私钥字符串(NSString格式)
    NSString *decryptString = [RSAEncryptor decryptString:encryptStr privateKey:RSAPrivateKey];
    
    NSLog(@"解密后:%@",decryptString);
```

#### RSA用NSString加解密的封装，拖入项目导入即可用

**`头文件预览`**

```Objective-C
// RSA加密封装类
//注意：如果使用，需要打开钥匙串；因为iOS不支持直接使用字符串格式的公钥进行加密，转换为文件后可使用

#import <Foundation/Foundation.h>

@interface RSAEncryptor : NSObject

/**
 *  加密方法
 *
 *  @param str   需要加密的字符串
 *  @param path  '.der'格式的公钥文件路径
 */
+ (NSString *)encryptString:(NSString *)str publicKeyWithContentsOfFile:(NSString *)path;

/**
 *  解密方法
 *
 *  @param str       需要解密的字符串
 *  @param path      '.p12'格式的私钥文件路径
 *  @param password  私钥文件密码
 */
+ (NSString *)decryptString:(NSString *)str privateKeyWithContentsOfFile:(NSString *)path password:(NSString *)password;

/**
 *  加密方法
 *
 *  @param str    需要加密的字符串
 *  @param pubKey 公钥字符串
 */
+ (NSString *)encryptString:(NSString *)str publicKey:(NSString *)pubKey;

/**
 *  解密方法
 *
 *  @param str     需要解密的字符串
 *  @param privKey 私钥字符串
 */
+ (NSString *)decryptString:(NSString *)str privateKey:(NSString *)privKey;

@end
```
如果您觉得有所帮助，请在[GitHub](https://github.com/muzipiao/RSAEncrypt)上赏个Star ⭐️，您的鼓励是我前进的动力
[点击下载RSA加密解密Demo](https://github.com/muzipiao/RSAEncrypt.git)
https://github.com/muzipiao/RSAEncrypt.git
