---
layout: post
title: "cocoapods 发布库"
date: 2018-07-09 
description: "cocoapods 发布自己的库。"
tag: iOS 
---   

## 安装 cocoapods

首次安装 cocoapods 建议升级 Ruby，防止 Ruby 版本过低出现的一些错误。

```ruby
# 查看当前 Ruby 版本
ruby -v
# 联网升级为 Ruby 最新稳定版本，需要几分钟时间
curl -L get.rvm.io | bash -s stable 
# 激活环境变量
source ~/.bashrc
source ~/.bash_profile
# 查看升级后的 Ruby 版本
ruby -v
```

更换安装源，Ruby 官方库 https://rubygems.org/ 为国外源，速度慢且可能被墙，更换为国内源。

```ruby
# 查看当前 Ruby 源，预计显示 https://rubygems.org/
gem sources -l
# 删除源
gem sources --remove https://rubygems.org/
# 添加源
gem sources --add https://gems.ruby-china.com/
# 查看更改后 Ruby 源
gem sources -l
```

安装 cocoapods，Mac 新版系统，例如 Mojave，由于目录权限改变，必须安装到用户目录`/usr/local/bin`下，旧的安装方法`sudo gem install cocoapods`在新系统上会报错。

```ruby
# 将 cocoapods 安装到 /usr/local/bin 目录下
sudo gem install -n /usr/local/bin cocoapods
# 安装成功后，查看 cocoapods 
pod --version
```

## 使用 cocoapods

创建 Podfile 文件，编辑填入需要集成的依赖库。

```ruby
# 创建 Podfile（切换到工程目录下,没有后缀）
$ touch Podfile
# 搜索需要的框架，里面会有集成方法，例如 pod 'AFNetworking', '~> 3.2.1'
$ pod search AFNetworking
```

Podfile 文件示例如下：

```ruby
# 使用 Swift 或将下方依赖编译动态库
use_frameworks!
# 设置 iOS 最低兼容版本
platform :ios, '8.0'
# 当前项目 Scheme
target 'MyScheme' do
# 依赖 AFNetworking 最新版本，pod update会更新
pod 'AFNetworking'
# 指定 MBProgressHUD 的 1.1.0 版本，pod update不更新
pod 'MBProgressHUD', '1.1.0'
# 依赖 SDWebImage 的 5.0 以上兼容版本，一般表示是以 5 开头版本，pod update会更新
pod 'SDWebImage', '~> 5.0'
# 依赖 FMDB 的 2.7.5 以上兼容版本，若有警告，隐藏警告
pod 'FMDB', '~> 2.7.5', inhibit_warnings: true
# 依赖 YYText 的 1.0.7 以上兼容版本，不隐藏警告
pod 'YYText', '~> 1.0.7', inhibit_warnings: false
end
```

编辑完成 Podfile 完成后，`pod install`即可，`pod update`会升级已安装的库。

```ruby
# 安装依赖库
$ pod install
# 升级安装依赖库（update包含install）
$ pod update
```

## 创建 cocoapods 发布项目

推荐使用 cocoapods 模板创建，快速标准。完整命令如下，有选项的命令会在后面解释。

```ruby
# 基于模板工程，创建一个名称叫 TestProj 的项目，会要求输入一些选项
pod lib create TestProj
# 基于模板工程，已经生成了 .podspec 文件，其他项目可用此命令创建
pod spec create TestProj
# .podspec 文件及项目编辑完成后，本地验证，可标记使用静态库和忽略警告
pod lib lint
# 本地验证，若项目依赖了静态库，必须加上--use-libraries
pod lib lint --use-libraries
# 本地验证，有警告导致验证不通过，可使用--allow-warnings使验证通过
pod lib lint --use-libraries --allow-warnings
# 创建 tag，注意 tag 必须和 podspec 文件中 s.version = '0.1.2' 一致
git tag '0.1.2'
# 推送至 GitHub，若此命令报错，使用 sourcetree 或其他工具推送接口
git push
# 远程验证，可标记使用静态库和忽略警告
pod spec lint
# 远程验证，若项目依赖了静态库，必须加上--use-libraries
pod spec lint --use-libraries
# 远程验证，有警告导致验证不通过，可使用--allow-warnings使验证通过
pod spec lint --use-libraries --allow-warnings
# 验证无错误，发布项目至 cocoapods
pod trunk push TestProj.podspec --use-libraries
# 如果想删除已发布库，可使用 delete
pod trunk delete {podname} {version}
```

### 基于模板创建项目

命令`pod lib create TestProj`会创建一个名称为 TestProj 的项目，一般名称和你待发布库的名称相同，此项目基于 cocoapods 项目模板，方便快捷发布库。执行此命令需要输入一些选项。

```ruby
# 准备应用到什么平台
What platform do you want to use?? [ iOS / macOS ]
> iOS
# 准备使用什么语言
What language do you want to use?? [ Swift / ObjC ]
> ObjC
# 是否需要为你的库包含一个 Demo 项目
Would you like to include a demo application with your library? [ Yes / No ]
> Yes
# 你想选择哪一个测试框架
Which testing frameworks will you use? [ Specta / Kiwi / None ]
> None
# 你想要做视图单元测试吗
Would you like to do view based testing? [ Yes / No ]
> No
# 你的类前缀是什么，自定义，输入空表示没有前缀
What is your class prefix?
> TP
```

创建成功，自动打开项目，编辑项目最低兼容版本，证书等配置，编译项目通过。最主要的文件是 .podspec 的文件的编辑，列举必须常用的项。

```ruby
Pod::Spec.new do |spec|
# 库名称，必须和 TestProj.podspec 名称一致
spec.name         = "TestProj"
# 待发布库的版本，首次随意，后面依次递增，注意和 tag 名称相同 git tag '0.1.2'
spec.version      = "0.1.2"
# 库的简介
spec.summary      = "这里写库 TestProj 的简单介绍。"
# 库的详细介绍，注意，这里文本长度大于 spec.summary，否则验证报错
spec.description  = <<-DESC
TestProj 是一个简单的库，使用 TestProj 可快速实现什么功能。
DESC
# 库的主页pod search TestProj会展示Homepage: https://github.com/muzipiao/GMObjC
spec.homepage     = "https://github.com/muzipiao/TestProj"
# 开源协议，指向.podspec 文件同级目录下的 LICENSE 文件，注意无后缀
spec.license      = { :type => "MIT", :file => "LICENSE" }
# 库的作者及邮箱
spec.author             = { "lifei" => "lifei_zdjl@126.com" }
# 库兼容的最低版本
spec.platform     = :ios, "8.0"
# 如果依赖了静态库 framework 或 .a 文件，此项必须
spec.static_framework = true
# 指向的 Github 地址及版本
spec.source       = { :git => "https://github.com/muzipiao/TestProj.git", :tag => "#{spec.version}" }
# 源码位置，注意 podspec 文件中路径必须为子路径，不能向上遍历父路径，例如 ../ 等写法
spec.source_files  = "TestProj/Classes/**/*.{h,m}"
# 头文件位置，注意 podspec 文件中路径必须为子路径，不能向上遍历父路径，例如 ../ 等写法
spec.public_header_files = "TestProj/Classes/**/*.h"
# 依赖的系统库，依赖单个用 .framework，多个用.frameworks，逗号隔开
spec.framework  = "Foundation"
# 若依赖多个系统库，使用 .frameworks，库之间逗号隔开
spec.frameworks = 'Foundation', 'UIKit', 'AVFoundation'
# 库是否依赖 ARC
spec.requires_arc = true
# 库依赖的其他三方库
spec.dependency "AFNetworking"
# 依赖本地 framework
spec.vendored_frameworks = 'Libs/MBProgressHUD.framework'
# 配置头文件搜索路径
spec.xcconfig = { 'HEADER_SEARCH_PATHS' => '$(PROJECT_DIR)/Libs/MBProgressHUD.framework/Headers' }
end
```

特别注意：podspec 文件中路径必须为子路径，不能向上遍历父路径。

## 常见错误

### use_frameworks!

使用 Swift 库的同学必须加上`use_frameworks!`，这个标记是会将 Pod 管理的依赖全部编译为动态库，需注意项目最低兼容版本需要在 iOS8 以上。

### 依赖静态库的错误

如果库依赖静态库，必须在 .podspec 的文件中配置`spec.static_framework = true`，否则会报如下错误

```ruby
-> TestProj (0.1.2)
- WARN  | summary: The summary is not meaningful.
- ERROR | [iOS] unknown: Encountered an unknown error (The 'Pods-App' target has transitive dependencies that include static binaries: (/private/var/folders/pg/nbtf_x71135bgsk9844np9hr0000gn/T/CocoaPods-Lint-20190308-57050-lhnm7v-TestProj/Pods/Libs/MBProgressHUD.framework)) during validation.
[!] TestProj did not pass validation, due to 1 error and 1 warning.
You can use the `--no-clean` option to inspect any issue.
```

###  pod search 总是失败

安装 CocoaPods 后，可以正常使用，但发现执行`pod search`来搜索类库信息时，却总是出现类似错误`[!] Unable to find a pod with name, author, summary, or descriptionmatching '······'`，可尝试下面的方法。

* 删除 CocoaPods 目录`~/Library/Caches/CocoaPods/Pods/Release`的缓存；
* 删除`~/Library/Caches/CocoaPods`目录下的 search_index.json 文件；
* 执行`pod setup`命令，会自动下载本地库，有时速度较慢。
* 执行`pod search AFNetworking`，搜索任意库，会重新创建索引，速度较慢。
