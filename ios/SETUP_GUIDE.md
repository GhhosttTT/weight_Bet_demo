# iOS 项目设置指南

本指南将帮助你完成 iOS 项目的初始设置和配置。

## 📋 前置要求

- macOS 13.0 (Ventura) 或更高版本
- Xcode 15.0 或更高版本
- CocoaPods 1.12 或更高版本
- iOS 14.0+ 目标设备或模拟器

## 🚀 快速开始

### 1. 安装 CocoaPods

如果你还没有安装 CocoaPods,运行以下命令:

```bash
sudo gem install cocoapods
```

验证安装:
```bash
pod --version
```

### 2. 安装项目依赖

```bash
cd ios
pod install
```

这将安装以下依赖:
- Alamofire (网络请求)
- Kingfisher (图片加载)
- StripePaymentSheet (支付)
- Firebase/Messaging (推送通知)
- Charts (图表)
- KeychainAccess (安全存储)

### 3. 创建 Xcode 项目

由于 Git 不包含 `.xcodeproj` 文件,你需要创建一个新的 Xcode 项目:

1. 打开 Xcode
2. 选择 "Create a new Xcode project"
3. 选择 "iOS" → "App"
4. 填写项目信息:
   - Product Name: `WeightLossBetting`
   - Team: 选择你的开发团队
   - Organization Identifier: `com.weightloss.betting`
   - Interface: `Storyboard`
   - Language: `Swift`
5. 保存到 `ios/` 目录

### 4. 配置项目设置

在 Xcode 中:

1. **General 设置**:
   - Deployment Target: iOS 14.0
   - Bundle Identifier: `com.weightloss.betting`

2. **Signing & Capabilities**:
   - 添加你的开发团队
   - 启用 "Push Notifications"
   - 启用 "Background Modes" → 选择 "Remote notifications"

3. **Build Settings**:
   - Swift Language Version: Swift 5

### 5. 添加源文件到项目

将以下目录拖拽到 Xcode 项目中:
- `WeightLossBetting/Data/`
- `WeightLossBetting/UI/`
- `WeightLossBetting/AppDelegate.swift`
- `WeightLossBetting/SceneDelegate.swift`

确保选择 "Copy items if needed" 和 "Create groups"。

### 6. 配置 Firebase

#### 6.1 创建 Firebase 项目

1. 访问 [Firebase Console](https://console.firebase.google.com/)
2. 创建新项目或选择现有项目
3. 添加 iOS 应用:
   - iOS bundle ID: `com.weightloss.betting`
   - App nickname: `Weight Loss Betting iOS`

#### 6.2 下载配置文件

1. 下载 `GoogleService-Info.plist`
2. 将文件拖拽到 Xcode 项目根目录
3. 确保 "Copy items if needed" 被选中
4. 确保 "Add to targets" 选中了 WeightLossBetting

#### 6.3 配置 FCM

1. 在 Firebase Console 中,进入 "Project Settings" → "Cloud Messaging"
2. 上传 APNs 认证密钥或证书
3. 记录 Server Key (后端需要使用)

### 7. 配置后端 API

打开 `Data/Network/APIService.swift`,修改 `baseURL`:

```swift
private let baseURL = "https://your-backend-api.com/api"
```

开发环境可以使用:
```swift
private let baseURL = "http://localhost:8000/api"
```

### 8. 配置 Stripe

#### 8.1 获取 Stripe Keys

1. 访问 [Stripe Dashboard](https://dashboard.stripe.com/)
2. 获取 Publishable Key (测试模式)

#### 8.2 配置 Stripe SDK

在实现支付功能时,在 `AppDelegate.swift` 中添加:

```swift
import StripePaymentSheet

func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    StripeAPI.defaultPublishableKey = "pk_test_your_key_here"
    // ... 其他配置
}
```

### 9. 配置 Core Data

Core Data 模型文件已创建在 `WeightLossBetting.xcdatamodeld/`。

需要添加以下 Entities:

#### UserEntity
- id: String
- email: String
- nickname: String
- gender: String
- age: Int16
- height: Double
- currentWeight: Double
- targetWeight: Double
- updatedAt: Date

#### BettingPlanEntity
- id: String
- creatorId: String
- participantId: String (Optional)
- status: String
- betAmount: Double
- startDate: Date
- endDate: Date
- planDescription: String (Optional)
- updatedAt: Date

#### CheckInEntity
- id: String
- userId: String
- planId: String
- weight: Double
- checkInDate: Date
- photoUrl: String (Optional)
- note: String (Optional)
- createdAt: Date

#### OfflineCheckInEntity
- id: String
- planId: String
- weight: Double
- note: String (Optional)
- photoUrl: String (Optional)
- createdAt: Date
- synced: Boolean

### 10. 运行项目

1. 确保已运行 `pod install`
2. 打开 `WeightLossBetting.xcworkspace` (不是 .xcodeproj)
3. 选择目标设备或模拟器
4. 点击 Run (Cmd + R)

## 🔧 常见问题解决

### 问题 1: "No such module 'Alamofire'"

**解决方案**:
1. 确保运行了 `pod install`
2. 确保打开的是 `.xcworkspace` 而不是 `.xcodeproj`
3. Clean Build Folder (Cmd + Shift + K)
4. 重新构建项目

### 问题 2: Firebase 初始化失败

**解决方案**:
1. 确保 `GoogleService-Info.plist` 在项目中
2. 确保文件被添加到 Target
3. 检查 Bundle Identifier 是否匹配

### 问题 3: Core Data 错误

**解决方案**:
1. 确保 `.xcdatamodeld` 文件在项目中
2. 检查 Entity 名称是否正确
3. 清除模拟器数据: Device → Erase All Content and Settings

### 问题 4: 推送通知不工作

**解决方案**:
1. 确保在真机上测试 (模拟器不支持推送)
2. 确保启用了 Push Notifications capability
3. 确保上传了 APNs 证书到 Firebase
4. 检查通知权限是否被授予

### 问题 5: Keychain 访问错误

**解决方案**:
1. 在模拟器上,重置模拟器
2. 在真机上,检查 Keychain Sharing capability
3. 确保 Bundle Identifier 正确

## 📱 测试指南

### 单元测试

创建测试文件在 `WeightLossBettingTests/`:

```swift
import XCTest
@testable import WeightLossBetting

class AuthRepositoryTests: XCTestCase {
    func testLogin() {
        // 测试登录功能
    }
}
```

运行测试: Cmd + U

### UI 测试

创建 UI 测试在 `WeightLossBettingUITests/`:

```swift
import XCTest

class LoginUITests: XCTestCase {
    func testLoginFlow() {
        let app = XCUIApplication()
        app.launch()
        // 测试登录流程
    }
}
```

### 手动测试清单

- [ ] 用户注册
- [ ] 用户登录
- [ ] 创建对赌计划
- [ ] 接受对赌计划
- [ ] 每日打卡
- [ ] 查看进度
- [ ] 离线打卡
- [ ] 网络恢复后同步
- [ ] 推送通知接收
- [ ] 查看账户余额

## 🔐 安全配置

### 1. API Keys 管理

不要将 API Keys 硬编码在代码中。使用配置文件:

创建 `Config.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>API_BASE_URL</key>
    <string>https://your-api.com</string>
    <key>STRIPE_PUBLISHABLE_KEY</key>
    <string>pk_test_...</string>
</dict>
</plist>
```

读取配置:
```swift
guard let path = Bundle.main.path(forResource: "Config", ofType: "plist"),
      let config = NSDictionary(contentsOfFile: path) else {
    fatalError("Config.plist not found")
}

let apiBaseURL = config["API_BASE_URL"] as! String
```

### 2. 证书 Pinning (可选)

在 `APIService.swift` 中添加证书固定以增强安全性。

### 3. 混淆和加密

对于生产环境,考虑:
- 启用 Bitcode
- 使用 ProGuard 混淆
- 加密敏感数据

## 📦 发布准备

### 1. 更新版本号

在 Xcode 中:
- General → Version: 1.0.0
- General → Build: 1

### 2. 配置 App Icon

1. 准备不同尺寸的图标
2. 添加到 `Assets.xcassets/AppIcon.appiconset/`

### 3. 配置 Launch Screen

编辑 `LaunchScreen.storyboard`

### 4. 生产环境配置

- 切换到生产 API URL
- 使用生产 Stripe Keys
- 使用生产 Firebase 配置

### 5. Archive 和上传

1. Product → Archive
2. Distribute App
3. 选择 App Store Connect
4. 上传到 TestFlight

## 🔄 持续集成 (可选)

### 使用 Fastlane

安装 Fastlane:
```bash
sudo gem install fastlane
```

初始化:
```bash
cd ios
fastlane init
```

配置 `Fastfile` 进行自动化构建和部署。

## 📚 额外资源

- [iOS 开发文档](https://developer.apple.com/documentation/)
- [Swift 编程指南](https://docs.swift.org/swift-book/)
- [CocoaPods 指南](https://guides.cocoapods.org/)
- [Firebase iOS 文档](https://firebase.google.com/docs/ios/setup)
- [Alamofire 文档](https://github.com/Alamofire/Alamofire/blob/master/Documentation/Usage.md)

## 💡 开发技巧

1. **使用 SwiftLint** 保持代码风格一致
2. **使用 Git Hooks** 在提交前运行测试
3. **定期更新依赖** 保持安全性
4. **使用 Instruments** 进行性能分析
5. **启用 Crash Reporting** (如 Firebase Crashlytics)

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。
