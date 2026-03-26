# Android 网络层实现总结

## 任务概述

实现了 Android 客户端的完整网络层,包括 API 接口定义、Retrofit 配置、JWT 令牌拦截器、错误处理拦截器和 Repository 层。

## 已完成的功能

### 1. API 接口定义 (ApiService.kt)

定义了所有后端 API 端点接口:
- **认证 API**: 注册、登录、刷新令牌、Google 登录
- **用户 API**: 获取/更新用户信息、查询余额、交易历史
- **对赌计划 API**: 创建、查询、接受、拒绝、取消计划
- **打卡 API**: 创建打卡、查询历史、获取进度
- **支付 API**: 充值、提现
- **社交 API**: 排行榜、评论、勋章

### 2. 网络拦截器

#### AuthInterceptor (认证拦截器)
- 自动添加 JWT 令牌到请求头
- 使用 `Authorization: Bearer <token>` 格式
- 跳过登录/注册等认证请求
- 集成 TokenManager 管理令牌

#### ErrorInterceptor (错误处理拦截器)
- 统一处理 HTTP 错误响应
- 解析服务器返回的错误信息
- 将 HTTP 状态码转换为自定义异常类型:
  - 401 → UnauthorizedError
  - 400/422 → ValidationError
  - 5xx → ServerError
  - 其他 → UnknownError

#### RetryInterceptor (请求重试拦截器)
- 自动重试失败的网络请求
- 最多重试 3 次
- 使用指数退避策略 (1s, 2s, 3s)
- 仅对超时和服务器错误 (5xx) 重试
- 客户端错误 (4xx) 不重试

### 3. 网络结果封装

#### NetworkResult
统一的网络请求结果类型:
```kotlin
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val exception: NetworkException) : NetworkResult<Nothing>()
    object Loading : NetworkResult<Nothing>()
}
```

#### NetworkException
自定义网络异常类型:
- `NetworkError` - 网络连接失败
- `ServerError` - 服务器错误 (5xx)
- `UnauthorizedError` - 未授权 (401)
- `ValidationError` - 数据验证失败 (400, 422)
- `TimeoutError` - 请求超时
- `UnknownError` - 未知错误

#### ErrorResponse
API 错误响应模型,用于解析服务器返回的错误信息。

### 4. Repository 层

#### BaseRepository
提供通用的网络请求处理逻辑:
- `safeApiCall()` 方法封装网络请求
- 自动捕获和转换异常
- 返回 NetworkResult 类型
- 在 IO 线程执行请求

#### 具体 Repository

1. **AuthRepository** - 认证相关操作
   - 注册、登录、Google 登录
   - 刷新令牌、登出
   - 自动保存令牌到 TokenManager

2. **UserRepository** - 用户信息管理
   - 获取/更新用户信息
   - 查询账户余额
   - 获取交易历史

3. **BettingPlanRepository** - 对赌计划管理
   - 创建、查询计划
   - 接受、拒绝、取消计划
   - 获取用户的所有计划

4. **CheckInRepository** - 打卡记录管理
   - 创建打卡记录
   - 查询打卡历史
   - 获取进度统计

5. **PaymentRepository** - 支付操作
   - 充值
   - 提现

6. **SocialRepository** - 社交功能
   - 获取排行榜
   - 发表/查询评论
   - 获取用户勋章

### 5. 依赖注入配置

#### NetworkModule
提供网络相关依赖:
- Gson 配置
- OkHttpClient 配置 (包含所有拦截器)
- Retrofit 配置
- ApiService 实例

#### RepositoryModule
提供所有 Repository 实例:
- AuthRepository
- UserRepository
- BettingPlanRepository
- CheckInRepository
- PaymentRepository
- SocialRepository

### 6. 令牌管理

#### TokenManager
使用 DataStore 安全存储令牌:
- 保存访问令牌和刷新令牌
- 提供获取令牌的方法
- 提供清除令牌的方法 (登出时使用)

## 技术特点

1. **类型安全**: 使用 Kotlin 协程和 sealed class 确保类型安全
2. **错误处理**: 统一的错误处理机制,易于在 UI 层展示错误信息
3. **自动重试**: 智能重试机制提高请求成功率
4. **令牌管理**: 自动添加令牌,简化 API 调用
5. **依赖注入**: 使用 Hilt 管理依赖,易于测试和维护
6. **协程支持**: 所有网络请求使用 suspend 函数,支持协程

## 使用示例

### 登录示例

```kotlin
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    fun login(email: String, password: String) {
        viewModelScope.launch {
            val request = LoginRequest(email, password)
            
            when (val result = authRepository.login(request)) {
                is NetworkResult.Success -> {
                    // 登录成功
                    val user = result.data.user
                    // 导航到主页
                }
                is NetworkResult.Error -> {
                    // 登录失败
                    when (result.exception) {
                        is NetworkException.UnauthorizedError -> {
                            // 显示"用户名或密码错误"
                        }
                        is NetworkException.NetworkError -> {
                            // 显示"网络连接失败"
                        }
                        else -> {
                            // 显示通用错误信息
                        }
                    }
                }
                is NetworkResult.Loading -> {
                    // 显示加载状态
                }
            }
        }
    }
}
```

### 创建对赌计划示例

```kotlin
class CreatePlanViewModel @Inject constructor(
    private val bettingPlanRepository: BettingPlanRepository
) : ViewModel() {
    
    fun createPlan(
        betAmount: Double,
        startDate: String,
        endDate: String,
        initialWeight: Double,
        targetWeight: Double
    ) {
        viewModelScope.launch {
            val request = CreatePlanRequest(
                betAmount = betAmount,
                startDate = startDate,
                endDate = endDate,
                initialWeight = initialWeight,
                targetWeight = targetWeight,
                description = null
            )
            
            when (val result = bettingPlanRepository.createPlan(request)) {
                is NetworkResult.Success -> {
                    // 创建成功
                    val plan = result.data
                    // 导航到计划详情页
                }
                is NetworkResult.Error -> {
                    // 创建失败
                    when (result.exception) {
                        is NetworkException.ValidationError -> {
                            // 显示验证错误信息
                        }
                        else -> {
                            // 显示通用错误信息
                        }
                    }
                }
                is NetworkResult.Loading -> {
                    // 显示加载状态
                }
            }
        }
    }
}
```

## 文件结构

```
android/app/src/main/java/com/weightloss/betting/
├── data/
│   ├── model/
│   │   └── Models.kt                    # 数据模型
│   ├── remote/
│   │   ├── ApiService.kt                # API 接口定义
│   │   ├── AuthInterceptor.kt           # 认证拦截器
│   │   ├── ErrorInterceptor.kt          # 错误处理拦截器
│   │   ├── RetryInterceptor.kt          # 请求重试拦截器
│   │   ├── TokenManager.kt              # 令牌管理器
│   │   ├── NetworkResult.kt             # 网络结果封装
│   │   └── ErrorResponse.kt             # 错误响应模型
│   └── repository/
│       ├── BaseRepository.kt            # Repository 基类
│       ├── AuthRepository.kt            # 认证 Repository
│       ├── UserRepository.kt            # 用户 Repository
│       ├── BettingPlanRepository.kt     # 对赌计划 Repository
│       ├── CheckInRepository.kt         # 打卡 Repository
│       ├── PaymentRepository.kt         # 支付 Repository
│       └── SocialRepository.kt          # 社交 Repository
└── di/
    ├── NetworkModule.kt                 # 网络模块
    └── RepositoryModule.kt              # Repository 模块
```

## 下一步工作

网络层已完成,接下来可以:
1. 实现 ViewModel 层
2. 实现 UI 层 (Activity/Fragment/Compose)
3. 实现本地数据库缓存
4. 实现离线支持
5. 编写单元测试

## 注意事项

1. **BASE_URL 配置**: 当前配置为 `http://10.0.2.2:8000/`,这是 Android 模拟器访问本机的地址。真机测试时需要修改为实际的服务器 IP 地址。

2. **令牌刷新**: 当前实现需要手动调用 `refreshToken()`,建议在后续实现自动刷新机制 (在 AuthInterceptor 中检测 401 错误并自动刷新)。

3. **日志记录**: LoggingInterceptor 在生产环境应该禁用,避免泄露敏感信息。

4. **超时配置**: 当前超时时间为 30 秒,可根据实际需求调整。

5. **错误信息**: 错误信息应该本地化,支持多语言。

## 总结

Android 网络层已完整实现,包括:
- ✅ API 接口定义
- ✅ Retrofit 配置
- ✅ JWT 令牌拦截器
- ✅ 错误处理拦截器
- ✅ 请求重试拦截器
- ✅ Repository 层
- ✅ 网络结果封装
- ✅ 依赖注入配置

网络层提供了类型安全、易于使用的 API,为后续的 UI 层开发奠定了坚实的基础。
