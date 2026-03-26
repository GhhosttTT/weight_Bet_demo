# iOS 项目架构说明

## 架构概览

本项目采用 **MVVM (Model-View-ViewModel)** 架构模式,结合 **Repository Pattern** 实现数据层抽象。

```
┌─────────────────────────────────────────────────────────┐
│                     Presentation Layer                   │
│  ┌──────────────┐         ┌──────────────┐             │
│  │ViewController│ ◄─────► │  ViewModel   │             │
│  └──────────────┘         └──────────────┘             │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                      Domain Layer                        │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  Repository  │ ◄─────► │    Models    │             │
│  └──────────────┘         └──────────────┘             │
└─────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│      Data Layer          │  │    Local Storage         │
│  ┌──────────────┐        │  │  ┌──────────────┐       │
│  │  APIService  │        │  │  │ CoreDataMgr  │       │
│  └──────────────┘        │  │  └──────────────┘       │
│         │                │  │         │                │
│         ▼                │  │         ▼                │
│  ┌──────────────┐        │  │  ┌──────────────┐       │
│  │   Backend    │        │  │  │  Core Data   │       │
│  │     API      │        │  │  │   Database   │       │
│  └──────────────┘        │  │  └──────────────┘       │
└──────────────────────────┘  └──────────────────────────┘
```

## 目录结构详解

### 1. Data Layer (数据层)

#### 1.1 Model (数据模型)
**位置**: `Data/Model/Models.swift`

**职责**:
- 定义所有数据结构
- 实现 Codable 协议用于 JSON 序列化
- 与后端 API 数据格式保持一致

**主要模型**:
```swift
- User              // 用户信息
- BettingPlan       // 对赌计划
- CheckIn           // 打卡记录
- ProgressStats     // 进度统计
- Balance           // 账户余额
- Transaction       // 交易记录
- AuthResponse      // 认证响应
```

#### 1.2 Network (网络层)
**位置**: `Data/Network/`

**组件**:

1. **APIService.swift**
   - 封装所有 HTTP 请求
   - 使用 Alamofire 进行网络通信
   - 统一错误处理
   - 自动 JSON 解析

2. **AuthInterceptor.swift**
   - 请求拦截器
   - 自动添加 JWT Token 到请求头
   - 检测 401 错误并自动刷新 Token
   - 实现无感知的 Token 续期

3. **TokenManager.swift**
   - Token 安全存储 (使用 Keychain)
   - Token 读取和清除
   - Token 有效性检查

**数据流**:
```
ViewController → ViewModel → Repository → APIService → Backend
                                                ↓
                                         AuthInterceptor
                                         (添加 Token)
```

#### 1.3 Local (本地存储)
**位置**: `Data/Local/CoreDataManager.swift`

**职责**:
- Core Data 数据库管理
- 数据缓存策略
- 离线数据队列管理
- 数据同步逻辑

**功能**:
```swift
- cacheUser()              // 缓存用户信息
- cacheBettingPlan()       // 缓存对赌计划
- saveOfflineCheckIn()     // 保存离线打卡
- getOfflineCheckIns()     // 获取待同步数据
- markCheckInAsSynced()    // 标记已同步
- clearAllCache()          // 清除所有缓存
```

#### 1.4 Repository (仓储层)
**位置**: `Data/Repository/`

**职责**:
- 统一数据访问接口
- 协调网络和本地数据源
- 实现缓存策略
- 处理离线场景

**仓储类**:

1. **AuthRepository**
   ```swift
   - login()          // 登录
   - register()       // 注册
   - logout()         // 登出
   - isLoggedIn()     // 检查登录状态
   ```

2. **BettingPlanRepository**
   ```swift
   - createBettingPlan()      // 创建计划
   - getBettingPlan()         // 获取计划详情
   - getUserBettingPlans()    // 获取用户计划列表
   - acceptBettingPlan()      // 接受计划
   ```

3. **CheckInRepository**
   ```swift
   - createCheckIn()          // 创建打卡
   - getCheckInHistory()      // 获取打卡历史
   - getProgress()            // 获取进度统计
   - syncOfflineCheckIns()    // 同步离线数据
   ```

### 2. UI Layer (界面层)

#### 2.1 Auth (认证模块)
**位置**: `UI/Auth/`

**组件**:
- `LoginViewController` + `LoginViewModel`: 登录界面
- `RegisterViewController` + `RegisterViewModel`: 注册界面

**功能**:
- 用户登录
- 用户注册
- 表单验证
- 错误提示

#### 2.2 Main (主界面模块)
**位置**: `UI/Main/`

**组件**:
- `MainTabBarController`: 主标签栏控制器
- `HomeViewController`: 首页

**功能**:
- 底部导航栏
- 页面切换
- 首页展示

#### 2.3 Plans (计划模块)
**位置**: `UI/Plans/`

**组件**:
- `PlansViewController`: 计划列表界面

**功能**:
- 显示用户的所有计划
- 按状态筛选
- 创建新计划
- 查看计划详情

#### 2.4 CheckIn (打卡模块)
**位置**: `UI/CheckIn/`

**组件**:
- `CheckInViewController`: 打卡界面

**功能**:
- 输入体重数据
- 上传照片
- 查看打卡历史
- 显示进度图表

#### 2.5 Profile (个人资料模块)
**位置**: `UI/Profile/`

**组件**:
- `ProfileViewController`: 个人资料界面

**功能**:
- 显示用户信息
- 编辑个人资料
- 查看账户余额
- 设置和登出

### 3. Core Data Model (数据模型)
**位置**: `WeightLossBetting.xcdatamodeld/`

**Entities**:

1. **UserEntity**
   - 缓存用户基本信息
   - 支持离线查看

2. **BettingPlanEntity**
   - 缓存对赌计划
   - 支持离线浏览

3. **CheckInEntity**
   - 缓存打卡记录
   - 用于进度计算

4. **OfflineCheckInEntity**
   - 离线打卡队列
   - 网络恢复后自动同步

## 数据流详解

### 1. 登录流程

```
用户输入 → LoginViewController
              ↓
         LoginViewModel.login()
              ↓
         AuthRepository.login()
              ↓
         APIService.login()
              ↓
         Backend API
              ↓
         AuthResponse (含 Token)
              ↓
         TokenManager.saveTokens()
              ↓
         CoreDataManager.cacheUser()
              ↓
         导航到主界面
```

### 2. 创建对赌计划流程

```
用户填写表单 → CreatePlanViewController
                  ↓
             CreatePlanViewModel.create()
                  ↓
             BettingPlanRepository.createBettingPlan()
                  ↓
             APIService.createBettingPlan()
                  ↓ (AuthInterceptor 自动添加 Token)
             Backend API
                  ↓
             BettingPlan 对象
                  ↓
             CoreDataManager.cacheBettingPlan()
                  ↓
             更新 UI
```

### 3. 打卡流程 (在线)

```
用户输入体重 → CheckInViewController
                  ↓
             CheckInViewModel.checkIn()
                  ↓
             CheckInRepository.createCheckIn()
                  ↓
             APIService.createCheckIn()
                  ↓
             Backend API
                  ↓
             CheckIn 对象
                  ↓
             更新 UI
```

### 4. 打卡流程 (离线)

```
用户输入体重 → CheckInViewController
                  ↓
             CheckInViewModel.checkIn()
                  ↓
             CheckInRepository.createCheckIn()
                  ↓
             APIService.createCheckIn() [失败]
                  ↓
             CoreDataManager.saveOfflineCheckIn()
                  ↓
             显示"已保存,将在网络恢复后同步"
                  
网络恢复 → CheckInRepository.syncOfflineCheckIns()
              ↓
         遍历离线队列
              ↓
         APIService.createCheckIn() [成功]
              ↓
         CoreDataManager.markCheckInAsSynced()
```

### 5. Token 刷新流程

```
API 请求 → AuthInterceptor.adapt()
              ↓
         添加 Token 到请求头
              ↓
         发送请求
              ↓
         收到 401 响应
              ↓
         AuthInterceptor.retry()
              ↓
         APIService.refreshToken()
              ↓
         Backend API
              ↓
         新的 Token
              ↓
         TokenManager.saveTokens()
              ↓
         重试原请求 (带新 Token)
```

## 设计模式

### 1. MVVM (Model-View-ViewModel)

**优点**:
- 分离 UI 和业务逻辑
- 便于单元测试
- 代码可维护性高

**实现**:
```swift
// View
class LoginViewController: UIViewController {
    private let viewModel = LoginViewModel()
    
    func loginButtonTapped() {
        viewModel.login(email: email, password: password) { result in
            // 更新 UI
        }
    }
}

// ViewModel
class LoginViewModel {
    private let repository = AuthRepository.shared
    
    func login(email: String, password: String, completion: @escaping (Result<User, Error>) -> Void) {
        repository.login(email: email, password: password, completion: completion)
    }
}
```

### 2. Repository Pattern

**优点**:
- 抽象数据源
- 统一数据访问接口
- 便于切换数据源 (网络/本地)

**实现**:
```swift
class BettingPlanRepository {
    func getUserBettingPlans(userId: String, completion: @escaping (Result<[BettingPlan], Error>) -> Void) {
        // 先尝试从网络获取
        apiService.getUserBettingPlans(userId: userId) { result in
            switch result {
            case .success(let plans):
                // 缓存到本地
                plans.forEach { self.coreDataManager.cacheBettingPlan($0) }
                completion(.success(plans))
            case .failure:
                // 网络失败,返回缓存数据
                let cachedPlans = self.coreDataManager.getCachedBettingPlans(userId: userId)
                completion(.success(cachedPlans))
            }
        }
    }
}
```

### 3. Singleton Pattern

**使用场景**:
- APIService
- TokenManager
- CoreDataManager
- Repository 类

**实现**:
```swift
class APIService {
    static let shared = APIService()
    private init() {}
}
```

### 4. Interceptor Pattern

**使用场景**:
- 请求拦截 (添加 Token)
- 响应拦截 (处理 401)
- 自动重试

**实现**:
```swift
class AuthInterceptor: RequestInterceptor {
    func adapt(_ urlRequest: URLRequest, for session: Session, completion: @escaping (Result<URLRequest, Error>) -> Void) {
        // 添加 Token
    }
    
    func retry(_ request: Request, for session: Session, dueTo error: Error, completion: @escaping (RetryResult) -> Void) {
        // 处理 401,刷新 Token
    }
}
```

## 依赖管理

### CocoaPods 依赖

```ruby
# 网络
pod 'Alamofire', '~> 5.8'

# 图片
pod 'Kingfisher', '~> 7.10'

# 支付
pod 'StripePaymentSheet', '~> 23.0'

# 推送
pod 'Firebase/Messaging', '~> 10.20'

# 图表
pod 'Charts', '~> 5.0'

# 安全存储
pod 'KeychainAccess', '~> 4.2'
```

### 依赖关系图

```
AppDelegate
    ├── Firebase
    └── UNUserNotificationCenter

SceneDelegate
    ├── TokenManager
    └── MainTabBarController / LoginViewController

ViewController
    └── ViewModel
        └── Repository
            ├── APIService
            │   ├── Alamofire
            │   └── AuthInterceptor
            │       └── TokenManager (Keychain)
            └── CoreDataManager
                └── Core Data
```

## 性能优化

### 1. 网络层优化
- 使用 Alamofire 的请求缓存
- 实现请求去重
- 合并相似请求

### 2. 本地存储优化
- 使用 Core Data 的批量操作
- 实现分页加载
- 定期清理过期缓存

### 3. UI 优化
- 使用 Kingfisher 的图片缓存
- 实现列表的懒加载
- 避免主线程阻塞

### 4. 内存优化
- 使用弱引用避免循环引用
- 及时释放大对象
- 使用 Instruments 检测内存泄漏

## 安全考虑

### 1. Token 安全
- 使用 Keychain 存储 Token
- Token 自动刷新机制
- 登出时清除 Token

### 2. 网络安全
- 强制使用 HTTPS
- 实现证书固定 (可选)
- 验证服务器证书

### 3. 数据安全
- Core Data 加密 (可选)
- 敏感数据不缓存
- 定期清理缓存

## 测试策略

### 1. 单元测试
- ViewModel 逻辑测试
- Repository 测试
- 数据模型测试

### 2. 集成测试
- API 集成测试
- Core Data 集成测试
- 离线同步测试

### 3. UI 测试
- 登录流程测试
- 创建计划流程测试
- 打卡流程测试

## 扩展性

### 添加新功能的步骤

1. **定义数据模型** (Models.swift)
2. **添加 API 接口** (APIService.swift)
3. **创建 Repository** (新建 Repository 文件)
4. **创建 ViewModel** (新建 ViewModel 文件)
5. **创建 ViewController** (新建 ViewController 文件)
6. **添加导航** (更新 TabBar 或 Navigation)

### 模块化建议

未来可以考虑将各个模块拆分为独立的 Framework:
- AuthModule
- BettingPlanModule
- CheckInModule
- PaymentModule

## 与 Android 对比

| 方面 | iOS (Swift) | Android (Kotlin) |
|------|-------------|------------------|
| 架构 | MVVM | MVVM |
| 网络 | Alamofire | Retrofit |
| 数据库 | Core Data | Room |
| 依赖注入 | 手动 | Hilt |
| 异步 | Completion Handler | Coroutines |
| UI | UIKit | Jetpack Compose / XML |
| 导航 | UINavigationController | Navigation Component |

## 总结

本项目采用清晰的分层架构,遵循 SOLID 原则,具有良好的可维护性和可扩展性。通过 Repository Pattern 实现了数据源的抽象,支持离线功能。使用 MVVM 模式分离了 UI 和业务逻辑,便于测试和维护。
