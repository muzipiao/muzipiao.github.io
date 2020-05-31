---
layout: post
title: "iOS 集成 OpenCV"
date: 2017-07-12 
description: "iOS 项目集成 OpenCV 及踩过的坑"
tag: iOS 
---   

## CocoaPods方式集成

编辑 Podfile 文件，添加 `pod 'OpenCV2'`，保存执行 `pod install` 即可。

也许你会问，为什么不是 `pod 'OpenCV'`？OpenCV 版本于2006年面世，主要基于C语言；2009年发布 OpenCV2，主要基于C++，目前最新版本是基于 OpenCV2 的。使用 CocoaPods 集成 OpenCV1.0 有头文件重复等问题，但集成 OpenCV2 是没有问题了，所以推荐使用 CocoaPods 集成 OpenCV2。

### 改为 Objective-C 与 C++ 混编

导入 OpenCV 头文件使用即可。注意的是，凡是导入 OpenCV 头文件的类，都需要把相应类后缀名 .m 改为 .mm。

```objc
#import <opencv2/opencv.hpp>
#import <opencv2/imgproc/types_c.h>
#import <opencv2/imgcodecs/ios.h>
```

## 直接下载 Framework 集成

直接集成 OpenCV 亦很简单，从[OpenCV 官网](http://opencv.org)下载框架，拖入 Xcode 项目。然后导入 OpenCV 依赖的系统库。

导入路径：选择项目 Targets—>General—>Linked Frameworks and Libraies，点击”+”添加下方依赖库。

> * libc++.tbd 
> * AVFoundation.framework 
> * CoreImage.framework 
> * CoreGraphics.framework 
> * QuartzCore.framework 
> * Accelerate.framework 
> * CoreVideo.framework 
> * CoreMedia.framework 
> * AssetsLibrary.framework

## 已经踩过的`深坑`

### 导入头文件的深坑

导入`#import <opencv2/opencv.hpp>`报 Expected identitier 的错误。这是由于 opencv 的 import 要写在`#import <UIKit/UIKit.h>、#import <Foundation/Foundation.h>`这些系统库 `前面`，否则会出现重命名的冲突。

![导入头文件错误](/images/posts/opencv/OpenCVSetError/OpenCVSetError1.png)

### Objective-C 和 C++ 的混编的深坑

OpenCV 框架提供是 C++ 的 API 接口，凡是使用 OpenCV 的地方，类的文件类型必须由 .m 类型改为 .mm 类型，这时候编译器按照 OC 与 C++ 混编进行编译。

假设你使用 OpenCV 的类为 A.mm，那如果你在 Objective-C 的类 B.m 中导入使用，此时编译器会认为此时 A.mm 也按照 Objective-C 类型编译，你必须把 B.m 类型更改为 B.mm 类型才不会报错，以此类推，你在 C.m 中使用 B.mm，那 C 也必须更改为 C.mm 类型......；有人比喻这样蔓延的有点像森林大火，一个接一个，很形象。

**解决办法**：在导入 OpenCV 头文件的时候，`#import <opencv2/opencv.hpp>`前面加上`#ifdef __cplusplus`，指明编译器只有使用了 OpenCV 的 .mm 类型文件，才按照 C++ 类型编译。如下即可解决:

```objc
#ifdef __cplusplus
#import <opencv2/opencv.hpp>
#import <opencv2/imgproc/types_c.h>
#import <opencv2/imgcodecs/ios.h>
#endif
```

### 编译警告

导入 OpenCV 使用时，Xcode8 或 Xcode9 可能会有一堆类似`warning: empty paragraph passed to '@param' command [-Wdocumentation]`的文档警告，Xcode10 已经没有没有此文档警告。

![文档警告](/images/posts/opencv/OpenCVSetError/OpenCVSetError2.png)

如果编译器报文档警告，有强迫症的小伙伴不能忍。解决办法：导入头文件的时候，忽略文档警告即可；同时只在需要的地方导入 C++ 类，则加上编译器忽略文档警告即可，解决办法如下：

```objc
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wdocumentation"

#ifdef __cplusplus
#import <opencv2/opencv.hpp>
#import <opencv2/imgproc/types_c.h>
#import <opencv2/imgcodecs/ios.h>
#endif

#pragma clang pop
```

### UIImage 与 cv::Mat 转换报错。

读取视频帧，转换为 UIImage 时报 `_CMSampleBufferGetImageBuffer", referenced from:` 的错误，是由于缺少 `CoreMedia.framework` 框架，在 `Targets—>General—>Linked Frameworks and Libraies` 导入 `CoreMedia.framework` 框架即可。

-----------------------------------------

如果您觉得有所帮助，请在[GitHub OOB](https://github.com/muzipiao/OOB)上赏个Star ⭐️，您的鼓励是我前进的动力
