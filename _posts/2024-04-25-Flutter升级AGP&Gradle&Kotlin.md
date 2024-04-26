---
layout: post
title: "Flutter升级AGP&Gradle&Kotlin"
date: 2024-04-25
description: "Flutter 跨平台开发，理清 Android Studio & AGP & Gradle & Kotlin 的关系，升级解决版本不匹配导致的编译问题。"
tag: Flutter
--- 

## AGP & Gradle & Kotlin 关系

跨平台扫盲，不熟悉这几样的同学了解一下。非 Android 开发出身，有总结错误的地方，谢谢指正。

1. Android Studio，开发 Android 的 SDK，大家都不陌生，对应 iOS 开发中 Xcode；
2. AGP(Android Gradle Plugin)，用于扩展 Gradle 功能的插件，以支持 Android 项目的构建；
3. Kotlin 开发语言，是一种与 Android 兼容的语言，类似 iOS 开发中的 Swift；
4. 不同版本 Android Studio 的 AGP 插件不同，AGP 对应 Gradle 版本不同；
5. Android Studio 升级时可能会升级 AGP，每个 AGP 版本都对应一个兼容的 Gradle 版本范围；
6. Android Studio 会捆绑一个 Kotlin 版本，一般为当前最新稳定版。

**具体对应关系可参考官方文档：**

* [Android Gradle 插件兼容列表](https://developer.android.google.cn/build/releases/gradle-plugin?hl=zh-cn)
* [Kotlin 版本所需的 D8 和 R8 编译器版本](https://developer.android.com/build/kotlin-support?hl=zh-cn)

## Flutter 编译 Android 报错

Flutter 升级至 3.19.6 后，编译 Android 报错`Failed to transform kotlin-stdlib-1.9.10.jar`，开始以为是 Flutter 的问题，调研发现是 Android Studio 升级导致。

**原因：** AGP(Android Gradle Plugin) & Gradle & Kotlin 之间版本有对应的关系，升级 Android Studio，导致 AGP 版本升高，对应兼容的最低 Gradle 版本和 Kotlin 版本也升高，如果项目设置的版本不匹配，就会编译报错。这对于不熟悉 Android 开发和 Gradle 的人来说，解决起来挺麻烦。

```groovy
FAILURE: Build failed with an exception.

* What went wrong:
Execution failed for task ':app:mergeExtDexDebug'.
> Could not resolve all files for configuration ':app:debugRuntimeClasspath'.
   > Failed to transform kotlin-stdlib-1.9.10.jar (org.jetbrains.kotlin:kotlin-stdlib:1.9.10) to match attributes {artifactType=android-dex, asm-transformed-variant=NONE, dexing-enable-desugaring=true, dexing-enable-jacoco-instrumentation=false, dexing-is-debuggable=true, dexing-min-sdk=19, org.gradle.category=library, org.gradle.libraryelements=jar, org.gradle.status=release, org.gradle.usage=java-runtime}.
      > Execution failed for DexingWithClasspathTransform: /Users/lifei/.gradle/caches/transforms-3/29afff73df66b7b192e6a6f531b855cf/transformed/jetified-kotlin-stdlib-1.9.10.jar.
         > Error while dexing.

* Try:
> Run with --stacktrace option to get the stack trace.
> Run with --info or --debug option to get more log output.
> Run with --scan to get full insights.

* Get more help at https://help.gradle.org

BUILD FAILED in 10m 15s

┌─ Flutter Fix ──────────────────────────────────────────────────────────────┐
│ [!] The shrinker may have failed to optimize the Java bytecode.            │
│ To disable the shrinker, pass the `--no-shrink` flag to this command.      │
│ To learn more, see: https://developer.android.com/studio/build/shrink-code │
└────────────────────────────────────────────────────────────────────────────┘
Error: Gradle task assembleDebug failed with exit code 1
```

## 升级项目 AGP

既然版本不匹配问题，除了降低 Android Studio 版本外，那就是利用 Android Studio 中 AGP 升级助手`AGP Upgrade Assistant...`快速升级 AGP。

1. 以 Android 模式打开 Flutter 项目（把项目的 Android 文件夹拖入 Android Studio），点击`Android Studio -> AGP Upgrade Assistant...`；
2. 出现一个弹窗，选择`Upgrade Android Gradle Plugin from version 7.4.2 to 8.3.2`，选择要升级的版本这里选择`8.3.2`；
3. 点击`Run selected steps`升级即可。

**一切顺利=草履虫教程，但可能会出现如下报错：**

![AGP升级报错](/images/posts/upgrade-agp/agp1.png)

```groovy
Namespace not specified. Specify a namespace in the module's build file. See https://d.android.com/r/tools/upgrade-assistant/set-namespace for information about setting the namespace.

If you've specified the package attribute in the source AndroidManifest.xml, you can use the AGP Upgrade Assistant to migrate to the namespace value in the build file. Refer to https://d.android.com/r/tools/upgrade-assistant/agp-upgrade-assistant for general information about using the AGP Upgrade Assistant.
```

**解决方案：**

这是由于 Android 主工程更新`Android Gradle Plugin 8.0`以后会强制要求在每一个 library 模块的 build.gradle 中标明命名空间namespace，如果没有标注会直接抛出异常。我的 Flutter 项目有一个自定义 OpenCV 插件，修改`/plugins/opencv_utils/android/build.gradle`添加版本即可。

```gradle
android {
    // 这里添加 namespace，和包名一致即可
    if (project.android.hasProperty("namespace")) {
        namespace 'com.lf.opencv.opencv_utils'
    }
    compileSdkVersion 33
    ......
}
```

**升级 AGP 插件版本至 8.3.2，通过 Git 我们检查更改如下(+号新增-号移除)：**

```diff
// android/build.gradle 修改了 gradle 插件版本
- classpath 'com.android.tools.build:gradle:7.4.2'
+ classpath 'com.android.tools.build:gradle:8.3.2'

// android/gradle.properties 新增如下内容
+ android.defaults.buildfeatures.buildconfig=true
+ android.nonTransitiveRClass=false
+ android.nonFinalResIds=false

// android/app/src/main/AndroidManifest.xml 移除了 package
- <manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.xx.yy">
+ <manifest xmlns:android="http://schemas.android.com/apk/res/android">

// android/gradle/wrapper/gradle-wrapper.properties 修改了 Gradle 版本
- distributionUrl=https\://services.gradle.org/distributions/gradle-7.5-all.zip
+ distributionUrl=https\://services.gradle.org/distributions/gradle-8.4-all.zip
```

## 升级 Kotlin 版本

升级完 AGP 后并没有结束，还需要升级 Kotlin 版本，因为不同的 Android Studio 捆绑 Kotlin 版本不同。

```diff
// 修改 android/build.gradle 文件中版本为 1.9.20
- ext.kotlin_version = '1.8.0'
+ ext.kotlin_version = '1.9.20'
```

修改文件`android/app/build.gradle`设置 **minSdkVersion、compileSdkVersion**。`com.xx.yy`修改为自己的包名。

```gradle
android {
    namespace "com.xx.yy"
    // 设置编译的 SDK 版本为 flutter.compileSdkVersion
    compileSdkVersion flutter.compileSdkVersion
......

defaultConfig {
    applicationId "com.xx.yy"
    // 设置最小兼容版本为 flutter.minSdkVersion
    minSdkVersion flutter.minSdkVersion
    targetSdkVersion flutter.targetSdkVersion
......
```

**如果想查看 Flutter 对应兼容版本。**

```gradle
// 修改文件`android/app/build.gradle`，打印 Gradle 和 Flutter 版本
println "gradle.gradleVersion: $gradle.gradleVersion"
println "android.buildToolsVersion: $android.buildToolsVersion"
println "flutter.compileSdkVersion: $flutter.compileSdkVersion"
println "flutter.targetSdkVersion: $flutter.targetSdkVersion"
println "flutter.minSdkVersion: $flutter.minSdkVersion"
println "flutter.ndkVersion: $flutter.ndkVersion"

android {
......
```

到这里问题解决，编译通过运行无警告🎉🎉

## 参考链接

* [android 添加 build 依赖项](https://developer.android.com/studio/build/dependencies?hl=zh-cn#groovy)
* [Flutter 升级 Gradle 和 Gradle Plugin](https://www.cnblogs.com/inexbot/p/17593347.html)
* [Failed to transform kotlin-stdlib-1.9.0.jar错误解决](https://github.com/juliansteenbakker/mobile_scanner/issues/729)
* [Android Studio Gradle 8.0升级记录](https://zhuanlan.zhihu.com/p/668428076)
* [Android Gradle 插件兼容列表](https://developer.android.google.cn/build/releases/gradle-plugin?hl=zh-cn)
* [Kotlin 版本所需的 D8 和 R8 编译器版本](https://developer.android.com/build/kotlin-support?hl=zh-cn)
