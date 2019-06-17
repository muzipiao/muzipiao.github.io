---
layout: post
title: "iOS集成OpenCV"
date: 2017-07-12 
description: "iOS项目集成OpenCV及踩过的坑"
tag: iOS 
---   

## iOS项目集成OpenCV及踩过的坑

### 一、直接下载Framework集成

#### 1.1、下载OpenCV的Framework

从[OpenCV官网](http://opencv.org)下载框架，拖入Xcode项目。

#### 1.2、导入OpenCV依赖的库

导入路径：选择项目—>Targets—>General—>Linked Frameworks and Libraies，点击”+”添加下方依赖库。

> * libc++.tbd 
> * AVFoundation.framework 
> * CoreImage.framework 
> * CoreGraphics.framework 
> * QuartzCore.framework 
> * Accelerate.framework 
> * CoreVideo.framework 
> * CoreMedia.framework 
> * AssetsLibrary.framework

#### 1.3、改为Objective-C与C++混编

凡是导入OpenCV头文件的类，都需要把相应类后缀名.m改为.mm。

```Objective-C++
#import <opencv2/opencv.hpp>
#import <opencv2/imgproc/types_c.h>
#import <opencv2/imgcodecs/ios.h>
```

### 二、~~CocoaPods方式集成~~(不推荐)

#### 2.1 CocoaPods文件配置

在项目Pod文件中配置**pod ‘OpenCV’**，然后**pod update**；同理，使用时导入OpenCV相应的头文件，并把类后缀名.m改为.mm。

#### 2.2 使用CocoaPods集成OpenCV说明

使用CocoaPods虽然配置简单，但自动配置的不正确，存在名称重复等大量的问题。例如:

> Warning: Multiple build commands for output file /Users/P85755/Library/Developer/Xcode/DerivedData/PracticeProject-bgmxispyljyrbfdimchwaxacraaa/Build/Products/Debug-iphoneos/OpenCV/calib3d.hpp
Warning: Multiple build commands for output file /Users/P85755/Library/Developer/Xcode/DerivedData/PracticeProject-bgmxispyljyrbfdimchwaxacraaa/Build/Products/Debug-iphoneos/OpenCV/core.hpp
。。。。。。。。。等等
是由于CocoaPods自动配置时，生成了相同名称的.h配置文件，虽然在不同路径，Xcode仍旧认为是同一个文件。

### 三、已经踩过的`深坑`

#### 3.1、导入头文件的深坑

导入**#import <opencv2/opencv.hpp>**报Expected identitier的错误。这是由于opencv 的 import 要写在**#import <UIKit/UIKit.h>、#import <Foundation/Foundation.h>**这些系统自带的 framework `前面`，否则会出现重命名的冲突。

![导入头文件错误](https://raw.githubusercontent.com/muzipiao/GitHubImages/master/OpenCVImg/OpenCVSetError/OpenCVSetError1.png)

#### 3.2、Objective-C和C++的混编的深坑

OpenCV框架提供是C++的API接口，凡是使用OpenCV的地方，类的文件类型必须由.m类型改为.mm类型，这时候编译器按照OC与C++混编进行编译。

假设你使用OpenCV的类为A.mm，那如果你在Objective-C的类B.m中导入使用，此时编译器会认为此时A.mm也按照Objective-C类型编译，你必须把B.m类型更改为B.mm类型才不会报错，以此类推，你在C.m中使用B.mm，那C也必须更改为C.mm类型。。。有人比喻这样蔓延的有点像森林大火，一个接一个，很形象。

`解决办法：`在导入OpenCV头文件的时候，**#import <opencv2/opencv.hpp>**前面加上**#ifdef __cplusplus**，指明编译器只有使用了OpenCV的.mm类型文件，才按照C++类型编译。如下即可解决:

```Objective-C++
#ifdef __cplusplus
#import <opencv2/opencv.hpp>
#import <opencv2/imgproc/types_c.h>
#import <opencv2/imgcodecs/ios.h>
#endif
```

#### 3.3、编译警告

导入OpenCV使用时，Xcode8会有一堆类似`warning: empty paragraph passed to '@param' command [-Wdocumentation]`的文档警告。

![导入头文件错误](https://raw.githubusercontent.com/muzipiao/GitHubImages/master/OpenCVImg/OpenCVSetError/OpenCVSetError2.png)

虽然项目目前不报错了，但对于有强迫症的小伙伴来说，还是不能忍。解决办法：导入头文件的时候，忽略文档警告即可；同时只在需要的地方导入C++类，则加上编译器忽略文档警告即可，解决办法如下：

```Objective-C++
#pragma clang diagnostic push
#pragma clang diagnostic ignored "-Wdocumentation"

#ifdef __cplusplus
#import <opencv2/opencv.hpp>
#import <opencv2/imgproc/types_c.h>
#import <opencv2/imgcodecs/ios.h>
#endif

#pragma clang pop
```

#### 3.4、UIImage与cv::Mat转换报错。

读取视频帧，转换为UIImage时报**_CMSampleBufferGetImageBuffer", referenced from:**的错误，是由于缺少**CoreMedia.framework**框架，在**Targets—>General—>Linked Frameworks and Libraies**导入**CoreMedia.framework**框架即可。

-----------------------------------------

如果您觉得有所帮助，请在[GitHub OpenCVDemo](https://github.com/muzipiao/OpenCVDemo)上赏个Star ⭐️，您的鼓励是我前进的动力