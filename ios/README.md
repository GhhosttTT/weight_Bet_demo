# Weight Loss Betting iOS App

iOS 客户端采用 Swift + MVVM + Alamofire + Core Data 架构开发。

## 项目结构

```
ios/
├── Podfile                          # CocoaPods 依赖配置
├── WeightLossBetting/
│   ├── AppDelegate.swift            # 应用入口,配置 Firebase
│   ├── SceneDelegate.swift          # 场景管理,处理登录状态
│   ├── Info.plist                   # 应用配置文件
│   │
│   ├── Data/                        # 数据层
│   │   ├── Model/                   # 数据模型
│   │   │   └── Models.swift         # 所有数据模型定义
│   │   │
│   │   ├── Network/                 # 网络层
│   │   │   ├── APIService.swift     # API 服务,封装所有网络请求
│   │   │   ├── AuthInterceptor.swift # 请求拦截器,自动添加 JWT token
│   │   │   └── TokenManager.swift   # Token 管理,使用 Keychain 安全存储
│   │   │
│   │   ├── Local/                   # 本地存储
│   │   │   └── CoreDataManager.swift # Core Data 管理器
│   │   │
│   │   └── Repository/              # 仓储层
│   │       ├── AuthRepository.swift         # 认证仓储
│   │       ├── BettingPlanRepository.swift  # 对赌计划仓储
│   │       └── CheckInRepository.swift      # 打卡仓储
│   │
│   ├── UI/                          # UI 层
│   │   ├── Auth/                    # 认证相关界面
│   │   │   ├── LoginViewController.swift
│   │   │   ├── LoginViewModel.swift
│   │   │   ├── RegisterViewController.swift
│   │   │   └── RegisterViewModel.swift
│   │   │
│   │   ├── Main/                    # 主界面
│   │   │   ├── MainTabBarController.swift
│   │   │   └── HomeViewController.swift
│   │   │
│   │   ├── Plans/                   # 计划相关界面
│   │   │   └── PlansViewController.swift
│   │   │
│   │   ├── CheckIn/                 # 打卡相关界面
│   │   │   └── CheckInViewController.swift
│   │   │
│   │   └── Profile/                 # 个人资料界面
│   │       └── ProfileViewController.swift
│   │
│   └── WeightLossBetting.xcdatamodeld/  # Core Data 模型文件
│
└── README.md                        # 本文件
```

## 技术栈

### 核心框架
- **Swift 5.9+**: 开发语言
- **UIKit**: UI 框架
- **MVVM**: 架构模式

### 网络层
- **Alamofire 5.8**: HTTP 网络请求库
- **JWT**: 身份认证

### 本地存储
- **Core Data**: 本地数据库,用于缓存和离线支持
- **KeychainAccess**: 安全存储 Token

### 第三方服务
- **Firebase Cloud Messaging**: 推送通知
- **Stripe SDK**: 支付集成
- **Kingfisher**: 图片加载和缓存
- **Charts**: 进度图表展示

## 架构设计

### MVVM 架构

```
View (ViewController) ←→ ViewModel ←→ Repository ←→ API/Database
```

- **View**: UIViewController,负责 UI 展示和用户交互
- **ViewModel**: 业务逻辑处理,数据转换
- **Repository**: 数据源管理,统一网络和本地数据访问
- **APIService**: 网络请求封装
- **CoreDataManager**: 本地数据库管理

### 数据流

1. **网络请求流程**:
   ```
   ViewController → ViewModel → Repository → APIService → Backend API
   ```

2. **数据缓存流程**:
   ```
   APIService → Repository → CoreDataManager → Core Data
   ```

3. **离线支持流程**:
   ```
   ViewController → Repository → CoreDataManager (保存到离线队列)
   网络恢复 → Repository → 同步离线数据到服务器
   ```

## 核心功能

### 1. 认证功能
- ✅ 用户登录 (邮箱/密码)
- ✅ 用户注册
- ✅ JWT Token 管理
- ✅ 自动 Token 刷新
- ⏳ Google 第三方登录 (待实现)

### 2. 对赌计划
- ✅ 创建对赌计划
- ✅ 查看计划列表
- ✅ 查看计划详情
- ✅ 接受对赌计划
- ✅ 邀请功能
- ⏳ 取消/拒绝计划 (待实现)

### 3. 打卡功能
- ✅ 创建打卡记录
- ✅ 查看打卡历史
- ✅ 查看进度统计
- ✅ 离线打卡支持
- ⏳ 照片上传 (待实现)
- ⏳ 进度图表展示 (待实现)

### 4. 支付功能
- ✅ 查看账户余额
- ✅ 查看交易历史
- ⏳ 充值功能 (待实现)
- ⏳ 提现功能 (待实现)

### 5. 通知功能
- ✅ Firebase Cloud Messaging 集成
- ⏳ 推送通知处理 (待实现)
- ⏳ 通知权限请求 (待实现)

## 安装和运行

### 前置要求
- Xcode 15.0+
- iOS 14.0+
- CocoaPods 1.12+

### 安装步骤

1. **安装 CocoaPods** (如果尚未安装):
   ```bash
   sudo gem install cocoapods
   ```

2. **安装依赖**:
   ```bash
   cd ios
   pod install
   ```

3. **打开项目**:
   ```bash
   open WeightLossBetting.xcworkspace
   ```
   
   ⚠️ **注意**: 必须打开 `.xcworkspace` 文件,而不是 `.xcodeproj` 文件

4. **配置 Firebase**:
   - 在 Firebase Console 创建 iOS 应用
   - 下载 `GoogleService-Info.plist` 文件
   - 将文件添加到 Xcode 项目中

5. **配置后端 API 地址**:
   - 打开 `Data/Network/APIService.swift`
   - 修改 `baseURL` 为实际的后端 API 地址

6. **运行项目**:
   - 选择目标设备或模拟器
   - 点击 Run 按钮或按 `Cmd + R`

## 配置说明

### API 配置
在 `APIService.swift` 中配置后端 API 地址:
```swift
private let baseURL = "https://your-api-domain.com/api"
```

### Firebase 配置
1. 将 `GoogleService-Info.plist` 添加到项目
2. 在 `AppDelegate.swift` 中已配置 Firebase 初始化

### Stripe 配置
在实现支付功能时,需要配置 Stripe 的 Publishable Key

## 开发指南

### 添加新功能

1. **创建数据模型** (如果需要):
   ```swift
   // 在 Data/Model/Models.swift 中添加
   struct NewModel: Codable {
       let id: String
       let name: String
   }
   ```

2. **添加 API 接口**:
   ```swift
   // 在 Data/Network/APIService.swift 中添加
   func getNewData(completion: @escaping (Result<NewModel, Error>) -> Void) {
       session.request("\(baseURL)/new-endpoint", method: .get)
           .validate()
           .responseDecodable(of: APIResponse<NewModel>.self) { response in
               self.handleResponse(response, completion: completion)
           }
   }
   ```

3. **创建 Repository**:
   ```swift
   // 创建 Data/Repository/NewRepository.swift
   class NewRepository {
       static let shared = NewRepository()
       private let apiService = APIService.shared
       
       func fetchData(completion: @escaping (Result<NewModel, Error>) -> Void) {
           apiService.getNewData(completion: completion)
       }
   }
   ```

4. **创建 ViewModel**:
   ```swift
   // 创建 UI/New/NewViewModel.swift
   class NewViewModel {
       private let repository = NewRepository.shared
       
       func loadData(completion: @escaping (Result<NewModel, Error>) -> Void) {
           repository.fetchData(completion: completion)
       }
   }
   ```

5. **创建 ViewController**:
   ```swift
   // 创建 UI/New/NewViewController.swift
   class NewViewController: UIViewController {
       private let viewModel = NewViewModel()
       
       override func viewDidLoad() {
           super.viewDidLoad()
           loadData()
       }
       
       private func loadData() {
           viewModel.loadData { result in
               // 处理结果
           }
       }
   }
   ```

### 代码规范

- 使用 Swift 命名规范
- 类名使用大驼峰 (PascalCase)
- 变量和函数名使用小驼峰 (camelCase)
- 使用 `// MARK: -` 组织代码
- 添加必要的注释

### Git 提交规范

- `feat`: 新功能
- `fix`: 修复 bug
- `refactor`: 重构代码
- `style`: 代码格式调整
- `docs`: 文档更新
- `test`: 测试相关

## 待实现功能

### 高优先级
- [ ] Google 第三方登录
- [ ] 照片上传功能
- [ ] 进度图表展示
- [ ] 充值和提现功能
- [ ] 推送通知完整实现

### 中优先级
- [ ] 计划邀请功能
- [ ] 评论和社交功能
- [ ] 排行榜
- [ ] 勋章系统

### 低优先级
- [ ] 深色模式支持
- [ ] 多语言支持
- [ ] 动画效果优化
- [ ] 单元测试
- [ ] UI 测试

## 与 Android 客户端对比

| 功能 | Android (Kotlin) | iOS (Swift) |
|------|-----------------|-------------|
| 架构模式 | MVVM | MVVM |
| 网络库 | Retrofit | Alamofire |
| 本地数据库 | Room | Core Data |
| 依赖注入 | Hilt | 手动注入 |
| 图片加载 | Coil | Kingfisher |
| 图表库 | MPAndroidChart | Charts |
| 推送通知 | FCM | FCM + APNs |

## 常见问题

### Q: 为什么要使用 Core Data 而不是 Realm?
A: Core Data 是 Apple 官方框架,与 iOS 系统深度集成,稳定性好,适合本项目的缓存和离线需求。

### Q: 为什么选择 Alamofire 而不是原生 URLSession?
A: Alamofire 提供了更简洁的 API,内置请求拦截器、自动重试等功能,开发效率更高。

### Q: 如何处理 Token 过期?
A: 使用 `AuthInterceptor` 自动检测 401 错误,调用刷新 Token API,然后重试原请求。

### Q: 离线数据如何同步?
A: 离线时数据保存到 Core Data 的离线队列,网络恢复后自动调用 `syncOfflineCheckIns` 同步到服务器。

## 参考资料

- [Swift 官方文档](https://swift.org/documentation/)
- [Alamofire 文档](https://github.com/Alamofire/Alamofire)
- [Core Data 编程指南](https://developer.apple.com/documentation/coredata)
- [Firebase iOS SDK](https://firebase.google.com/docs/ios/setup)
- [Stripe iOS SDK](https://stripe.com/docs/mobile/ios)

## 联系方式

如有问题,请联系开发团队或提交 Issue。
