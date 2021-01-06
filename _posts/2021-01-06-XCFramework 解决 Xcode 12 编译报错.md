---
layout: post
title: "XCFramework 解决 Xcode 12 编译报错"
date: 2021-01-06
description: "XCFramework 解决 Xcode 12 编译报错"
tag: iOS
--- 

我们先看一个 Xcode 12 编译时的常见错误，GMObjC.framework 同时包含 `x86_64 arm64` 架构，在 Xcode 12 之前的版本，编译时并不会报错，但现在却报错如下：

```text
# 当在真机运行时，编译报错
xx.xcodeproj Building for iOS, but the linked and embedded framework 'GMObjC.framework' was built for iOS + iOS Simulator.
# 当在模拟器运行时，编译报错
xx.xcodeproj Building for iOS Simulator, but the linked and embedded framework 'GMObjC.framework' was built for iOS + iOS Simulator.
```

很明显，新版本 Xcode 在使用包含多架构的库时会报错。从 stackoverflow 很容易找到解决方案，在工程的 `Build Settings -> Excluded Architectures` 依次添加编译对应架构时，需要排除的架构。

以包含 `x86_64 arm64` 架构的 GMObjC.framework 为例，在编译模拟器时，需要移除 arm64 架构；同理编译真机时，需要移除 x86_64 架构。选择 `Excluded Architectures`，点击加号”➕“，依次添加`Any iOS Simulator` 值为 arm64，`Any iOS` 值为 x86_64，再次编译即可通过。

![Xcode 12 报错解决](/images/posts/xcframework/xcframework1.png)

那 Xcode 为什么会编译报错呢，而之前不会。和 UIWebView、UIAlertView 类似，苹果在督促我们开发者放弃旧类型，使用新类型 XCFramework。

## XCFramework 是什么

首先回顾一下 iOS 开发中的静态库和动态库。

* 静态库(.a/.framework)：链接时完整地拷贝至可执行文件中，被多次使用就有多份冗余拷贝；
* 动态库(.dylib/.tbd/.framework)：程序运行时由系统动态加载到内存，系统动态库可被多个程序共享。

XCFramework 是苹果新出的库类型，在 Xcode 11 及 cocoapods 1.9 以上版本被支持，与普通动态库/静态库最大的区别是将**多个平台**的二进制库，捆绑到一个可分发的`.xcframework`捆绑包中，支持所有的苹果平台和架构。

这里的关键词是**多个平台**（iOS, macOS, tvOS, watchOS, iPadOS, carPlayOS），我们使用的普通动态库/静态库属于`fat file`，仅仅是包含多个架构，如`armv7 armv7s arm64 arm64e x86_64`等，而 XCFramework 可以包含 iOS 设备，iOS 模拟器和 Mac Catalyst 等多个平台的二进制库。

苹果引入 XCFramework 支持所有苹果平台，以支持苹果想实现**大一统**的规划，而且 XCFramework 编译的 Swift 库，使用者不再需要使用相同 Xcode 版本编译器（使用 Swift 库实现组件化的开发者应该深有感触），对比使用 .framework 格式，使用 .xcframework 格式 APP 包大小和启动速度都有提升。

## 制作 XCFramework

制作 XCFramework 很简单，通过`xcodebuild -create-xcframework`命令即可完成，我通过合并 GMObjC 库的模拟器和真机版本来演示。

当前文件夹下有编译好的 GMObjC.framework 分别是真机版本和模拟器版本。

```text
.
├── Release-iphoneos
│   ├── 0CD1FB8D-9D63-3092-B68B-2E579A306D3F.bcsymbolmap
│   ├── GMObjC.framework
│   └── GMObjC.framework.dSYM
└── Release-iphonesimulator
    ├── GMObjC.framework
    └── GMObjC.framework.dSYM
```

通过`xcodebuild -create-xcframework`命令来合并为 XCFramework。

```shell 
# 创建合并包 GMObjC.xcframework
xcodebuild -create-xcframework -framework Release-iphoneos/GMObjC.framework -framework Release-iphonesimulator/GMObjC.framework -output GMObjC.xcframework
# 或者换行展示更清晰
xcodebuild -create-xcframework \
          -framework Release-iphoneos/GMObjC.framework \
          -framework Release-iphonesimulator/GMObjC.framework \
          -output GMObjC.xcframework
```

合并后的 GMObjC.xcframework 目录结构如下，包含 arm64 和 x86_64 版本，这和 lipo 操作类似，合并其他平台时操作类似。

```text
GMObjC.xcframework
├── Info.plist
├── ios-arm64
│   └── GMObjC.framework
└── ios-x86_64-simulator
    └── GMObjC.framework
```

如果是静态库 .a 文件，则需要用`-library`和`-headers`来指定静态库和头文件。

```shell
xcodebuild -create-xcframework \
          -library Release-iphoneos/GMObjC.a \
          -headers Release-iphoneos/include/GMObjC \
          -library Release-iphonesimulator/GMObjC.a \
          -headers Release-iphonesimulator/include/GMObjC \
          -output GMObjC.xcframework
```

## 使用 XCFramework

如何使用 .xcframework 文件，选择当前工程 Target，选择 General 目录下的 `Frameworks,Libraries,and Embedded Content` 拖入 .xcframework 文件即可，和使用 .framework 文件几乎一样。

![XCFramework 配置](/images/posts/xcframework/xcframework2.png)

## 一键编译 XCFramework

编译 XCFramework 需要使用命令 `xcodebuild -create-xcframework`，写成 shell 文件更方便，放在 .xcodeproj 文件同级目录下，填入 scheme 名称，拖入终端回车即可生成。

脚本只写了 iPhone 真机和模拟器的合并，其他平台类似，自行添加修改即可，查看示例在 [GMObjCFramework](https://github.com/muzipiao/GMObjC) 文件夹中，下载后脚本拖入终端运行，可看到生成的 GMObjC.xcframework 在 build 目录下。

```shell
#!/bin/sh
# 放在与 .xcodeproj 文件同级目录下，生成结果在 build 目录下

# 需要编译的 scheme
scheme="GMObjCFramework"

if [ -z "$scheme" ] || [ "$scheme" = "" ]; then
     echo "请填入 scheme 名称"
fi

echo "scheme: $scheme"
cd "$(dirname "$0")" || exit 0

xcodebuild archive \
    -scheme "$scheme" \
    -sdk iphoneos \
    -archivePath "archives/ios_devices.xcarchive" \
    BUILD_LIBRARY_FOR_DISTRIBUTION=YES \
    SKIP_INSTALL=NO

xcodebuild archive \
    -scheme "$scheme" \
    -sdk iphonesimulator \
    -archivePath "archives/ios_simulators.xcarchive" \
    BUILD_LIBRARY_FOR_DISTRIBUTION=YES \
    SKIP_INSTALL=NO

# 优先从 archive 文件夹下读取
product_list=$(ls archives/ios_devices.xcarchive/Products/Library/Frameworks)
for file_name in $product_list
do
    full_product_name=$file_name
    break
done

# 读取不到就从 showBuildSettings 读取
if [ -z "$full_product_name" ] || [ "$full_product_name" = "" ]; then
    name_dict=$(xcodebuild -showBuildSettings | grep FULL_PRODUCT_NAME)
    full_product_name=${name_dict#*= }
fi

product_name=${full_product_name%.*}

xcodebuild -create-xcframework \
    -framework archives/ios_devices.xcarchive/Products/Library/Frameworks/"$full_product_name" \
    -framework archives/ios_simulators.xcarchive/Products/Library/Frameworks/"$full_product_name" \
    -output build/"$product_name".xcframework
```
