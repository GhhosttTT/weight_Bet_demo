# iOS 网络层文档

## 概述

iOS 网络层基于 Alamofire 实现,提供完整的 API 接口定义、请求拦截、错误处理和请求重试机制。网络层采用 Repository 模式,将网络请求逻辑与业务逻辑分离。

## 架构

```
┌─────────────────────────────────────────────────────────────┐
│                        UI Layer                              │
│                    (ViewControllers)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Repository Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │AuthRepository│  │UserRepository│  │PlanRepository│ ...  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         └──────────────────┴──────────────────┘              │
│                    BaseRepository                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Network Layer                             │
│                     APIService                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │              Alamofire Session                   │       │
│  │  ┌────────────────┐  ┌────────────────┐         │       │
│  │  │AuthInterceptor │  │RetryInterceptor│         │       │
│  │  └────────────────┘  └────────────────┘         │       │
│  │  ┌────────────────┐                             │       │
│  │  │ErrorInterceptor│                             │       │
│  │  └────────────────┘                             │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. APIService

**位置**: `ios/WeightLossBetting/Data/Network/APIService.swift`

**职责**:
- 定义所有 API 端点
- 配置 Alamofire Session
- 处理请求和响应
- 统一错误处理

**主要功能**:

#### 认证 API
- `login(email:password:completion:)` - 用户登录
- `register(email:password:nickname:completion:)` - 用户注册
- `googleLogin(idToken:completion:)` - Google 第三方登录
- `refreshToken(refreshToken:completion:)` - 刷新访问令牌

#### 用户 API
- `getUserProfile(userId:completion:)` - 获取用户信息
- `updateUserProfile(userId:parameters:completion:)` - 更新用户信息
- `bindPaymentMethod(userId:parameters:completion:)` - 绑定支付方式
- `getBalance(userId:completion:)` - 获取账户余额
- `getTransactionHistory(userId:completion:)` - 获取交易历史

#### 对赌计划 API
- `createBettingPlan(parameters:completion:)` - 创建对赌计划
- `getBettingPlan(planId:completion:)` - 获取计划详情
- `getUserBettingPlans(userId:status:completion:)` - 获取用户计划列表
- `acceptBettingPlan(planId:parameters:completion:)` - 接受计划
- `rejectBettingPlan(planId:completion:)` - 拒绝计划
- `cancelBettingPlan(planId:completion:)` - 取消计划
- `inviteParticipant(planId:inviteeId:completion:)` - 邀请参与者

#### 打卡 API
- `createCheckIn(parameters:completion:)` - 创建打卡记录
- `getCheckInHistory(planId:userId:completion:)` - 获取打卡历史
- `getProgress(planId:userId:completion:)` - 获取进度统计
- `uploadCheckInPhoto(checkInId:imageData:completion:)` - 上传打卡照片
- `reviewCheckIn(checkInId:approved:comment:completion:)` - 审核打卡

#### 支付 API
- `charge(amount:paymentMethodId:completion:)` - 充值
- `withdraw(amount:completion:)` - 提现

#### 社交 API
- `getLeaderboard(type:limit:completion:)` - 获取排行榜
- `postComment(planId:content:completion:)` - 发表评论
- `getComments(planId:completion:)` - 获取评论列表
- `getUserBadges(userId:completion:)` - 获取用户勋章

#### 通知 API
- `registerDeviceToken(token:completion:)` - 注册设备令牌

### 2. AuthInterceptor

**位置**: `ios/WeightLossBetting/Data/Network/AuthInterceptor.swift`

**职责**:
- 自动添加 JWT 令牌到请求头
- 处理 401 未授权错误
- 自动刷新过期令牌
- 令牌刷新失败时清除本地令牌

**工作流程**:
```
1. 请求发送前 → 添加 Authorization 头
2. 收到 401 响应 → 尝试刷新令牌
3. 刷新成功 → 重试原请求
4. 刷新失败 → 清除令牌,返回错误
```

### 3. RetryInterceptor

**位置**: `ios/WeightLossBetting/Data/Network/RetryInterceptor.swift`

**职责**:
- 自动重试失败的网络请求
- 实现指数退避策略
- 只重试超时和服务器错误(5xx)

**配置**:
- 最大重试次数: 3
- 初始退避时间: 1 秒
- 退避策略: 线性增长 (1s, 2s, 3s)

**重试条件**:
- 请求超时 (URLError.timedOut)
- 服务器错误 (HTTP 500-599)

**不重试条件**:
- 客户端错误 (HTTP 400-499)
- 网络连接错误
- 其他非超时错误

### 4. ErrorInterceptor

**位置**: `ios/WeightLossBetting/Data/Network/ErrorInterceptor.swift`

**职责**:
- 监控网络请求错误
- 记录错误日志
- 便于调试和问题排查

### 5. TokenManager

**位置**: `ios/WeightLossBetting/Data/Network/TokenManager.swift`

**职责**:
- 安全存储 JWT 令牌 (使用 Keychain)
- 提供令牌读取和清除接口
- 检查令牌有效性

**API**:
- `saveTokens(accessToken:refreshToken:)` - 保存令牌
- `getAccessToken()` - 获取访问令牌
- `getRefreshToken()` - 获取刷新令牌
- `clearTokens()` - 清除所有令牌
- `hasValidToken()` - 检查是否有有效令牌

### 6. NetworkError

**位置**: `ios/WeightLossBetting/Data/Network/NetworkError.swift`

**错误类型**:
- `networkError(String)` - 网络连接错误
- `serverError(Int, String)` - 服务器错误 (5xx)
- `unauthorizedError(String)` - 未授权错误 (401)
- `validationError(String)` - 数据验证错误 (400, 422)
- `timeoutError(String)` - 请求超时
- `unknownError(String)` - 未知错误

### 7. NetworkResult

**位置**: `ios/WeightLossBetting/Data/Network/NetworkError.swift`

**状态**:
- `success(T)` - 请求成功,包含数据
- `failure(NetworkError)` - 请求失败,包含错误信息
- `loading` - 请求进行中

## Repository 层

### BaseRepository

**位置**: `ios/WeightLossBetting/Data/Repository/BaseRepository.swift`

**职责**:
- 提供通用的 API 调用封装
- 统一错误处理
- 将回调转换为 async/await

**核心方法**:
```swift
func safeApiCall<T>(_ apiCall: @escaping (@escaping (Result<T, Error>) -> Void) -> Void) async -> NetworkResult<T>
```

### 具体 Repository

1. **AuthRepository** - 认证相关操作
2. **UserRepository** - 用户信息管理
3. **BettingPlanRepository** - 对赌计划管理
4. **CheckInRepository** - 打卡管理
5. **PaymentRepository** - 支付操作
6. **SocialRepository** - 社交功能
7. **NotificationRepository** - 通知管理

## 使用示例

### 1. 用户登录

```swift
let authRepository = AuthRepository()

Task {
    let result = await authRepository.login(
        email: "user@example.com",
        password: "password123"
    )
    
    switch result {
    case .success(let authResponse):
        print("Login successful: \(authResponse.user.nickname)")
        // Token is automatically saved
    case .failure(let error):
        print("Login failed: \(error.localizedDescription)")
    case .loading:
        print("Loading...")
    }
}
```

### 2. 创建对赌计划

```swift
let planRepository = BettingPlanRepository()

let parameters: [String: Any] = [
    "bet_amount": 100.0,
    "start_date": "2024-01-01",
    "end_date": "2024-01-31",
    "initial_weight": 80.0,
    "target_weight": 75.0,
    "description": "30天减重5kg挑战"
]

Task {
    let result = await planRepository.createBettingPlan(parameters: parameters)
    
    switch result {
    case .success(let plan):
        print("Plan created: \(plan.id)")
    case .failure(let error):
        if error.isUnauthorized {
            // Handle unauthorized error (redirect to login)
        } else {
            print("Error: \(error.localizedDescription)")
        }
    case .loading:
        print("Creating plan...")
    }
}
```

### 3. 打卡并上传照片

```swift
let checkInRepository = CheckInRepository()

// 1. Create check-in
let checkInParams: [String: Any] = [
    "user_id": userId,
    "plan_id": planId,
    "weight": 78.5,
    "check_in_date": Date(),
    "note": "今天感觉很好!"
]

Task {
    let createResult = await checkInRepository.createCheckIn(parameters: checkInParams)
    
    switch createResult {
    case .success(let checkIn):
        // 2. Upload photo
        if let imageData = image.jpegData(compressionQuality: 0.8) {
            let uploadResult = await checkInRepository.uploadCheckInPhoto(
                checkInId: checkIn.id,
                imageData: imageData
            )
            
            switch uploadResult {
            case .success(let photoUrl):
                print("Photo uploaded: \(photoUrl)")
            case .failure(let error):
                print("Upload failed: \(error.localizedDescription)")
            case .loading:
                print("Uploading...")
            }
        }
    case .failure(let error):
        print("Check-in failed: \(error.localizedDescription)")
    case .loading:
        print("Creating check-in...")
    }
}
```

### 4. 错误处理

```swift
func handleNetworkError(_ error: NetworkError) {
    switch error {
    case .networkError(let message):
        showAlert(title: "网络错误", message: message)
    case .serverError(let code, let message):
        showAlert(title: "服务器错误 (\(code))", message: message)
    case .unauthorizedError(let message):
        // Redirect to login
        navigateToLogin()
    case .validationError(let message):
        showAlert(title: "数据验证失败", message: message)
    case .timeoutError(let message):
        showAlert(title: "请求超时", message: message)
    case .unknownError(let message):
        showAlert(title: "未知错误", message: message)
    }
}
```

## 配置

### 修改 Base URL

在 `APIService.swift` 中修改:

```swift
private let baseURL = "https://api.yourapp.com/api"
```

### 修改超时时间

在 `APIService.swift` 的 `init()` 方法中修改:

```swift
configuration.timeoutIntervalForRequest = 30  // 请求超时
configuration.timeoutIntervalForResource = 30 // 资源超时
```

### 修改重试配置

在 `RetryInterceptor.swift` 中修改:

```swift
private let maxRetryCount = 3              // 最大重试次数
private let initialBackoffMs: TimeInterval = 1.0  // 初始退避时间
```

## 测试

### 单元测试示例

```swift
import XCTest
@testable import WeightLossBetting

class APIServiceTests: XCTestCase {
    var apiService: APIService!
    
    override func setUp() {
        super.setUp()
        apiService = APIService.shared
    }
    
    func testLogin() async {
        let expectation = XCTestExpectation(description: "Login")
        
        apiService.login(email: "test@example.com", password: "password") { result in
            switch result {
            case .success(let authResponse):
                XCTAssertNotNil(authResponse.accessToken)
                XCTAssertNotNil(authResponse.user)
            case .failure(let error):
                XCTFail("Login failed: \(error)")
            }
            expectation.fulfill()
        }
        
        await fulfillment(of: [expectation], timeout: 10.0)
    }
}
```

## 最佳实践

1. **始终使用 Repository 层**: 不要直接在 UI 层调用 APIService
2. **错误处理**: 始终处理所有可能的错误类型
3. **令牌管理**: 使用 TokenManager 管理令牌,不要手动处理
4. **异步操作**: 使用 async/await 而不是回调
5. **网络状态检查**: 在发起请求前检查网络连接状态
6. **用户体验**: 显示加载状态和友好的错误提示

## 与 Android 对比

| 功能 | iOS | Android |
|------|-----|---------|
| 网络库 | Alamofire | Retrofit |
| 拦截器 | RequestInterceptor | OkHttp Interceptor |
| 令牌存储 | Keychain | SharedPreferences (Encrypted) |
| 异步处理 | async/await | Coroutines |
| 错误处理 | NetworkError enum | NetworkException sealed class |
| Repository | BaseRepository | BaseRepository |

## 故障排查

### 问题: 请求一直超时

**解决方案**:
1. 检查网络连接
2. 验证 Base URL 是否正确
3. 增加超时时间
4. 检查服务器是否正常运行

### 问题: 401 错误不断出现

**解决方案**:
1. 检查令牌是否正确保存
2. 验证令牌刷新逻辑
3. 检查服务器令牌验证逻辑
4. 清除本地令牌并重新登录

### 问题: 请求重试过多

**解决方案**:
1. 检查服务器稳定性
2. 减少最大重试次数
3. 增加退避时间
4. 检查网络质量

## 未来改进

1. **缓存策略**: 实现请求缓存机制
2. **离线支持**: 添加离线队列和同步机制
3. **请求优先级**: 实现请求优先级管理
4. **批量请求**: 支持批量 API 调用
5. **WebSocket**: 添加实时通信支持
6. **性能监控**: 集成网络性能监控工具

## 参考资料

- [Alamofire 文档](https://github.com/Alamofire/Alamofire)
- [Keychain Access 文档](https://github.com/kishikawakatsumi/KeychainAccess)
- [iOS 网络编程指南](https://developer.apple.com/documentation/foundation/url_loading_system)
- [Android 网络层实现](../android/app/src/main/java/com/weightloss/betting/data/remote/)
