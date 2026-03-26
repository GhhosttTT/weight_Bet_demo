# 减肥对赌 APP - Android 客户端

## 项目概述

这是减肥对赌 APP 的 Android 原生客户端,使用 Kotlin 开发,采用 MVVM 架构模式。

## 技术栈

- **语言**: Kotlin
- **架构**: MVVM (Model-View-ViewModel)
- **依赖注入**: Hilt
- **网络请求**: Retrofit + OkHttp
- **本地数据库**: Room
- **异步处理**: Kotlin Coroutines + Flow
- **UI**: Material Design Components

## 项目结构

```
app/src/main/java/com/weightloss/betting/
├── data/                      # 数据层
│   ├── local/                 # 本地数据源
│   │   ├── dao/              # Room DAO
│   │   ├── entity/           # Room 实体
│   │   └── AppDatabase.kt    # 数据库配置
│   ├── remote/               # 远程数据源
│   │   ├── ApiService.kt     # API 接口定义
│   │   ├── AuthInterceptor.kt # 认证拦截器
│   │   └── TokenManager.kt   # 令牌管理
│   └── model/                # 数据模型
├── di/                       # 依赖注入模块
│   ├── NetworkModule.kt      # 网络模块
│   └── DatabaseModule.kt     # 数据库模块
├── ui/                       # UI 层
│   └── MainActivity.kt       # 主 Activity
└── WeightLossBettingApp.kt   # Application 类

```

## 主要功能

### 已实现的基础架构

1. **网络层配置**
   - Retrofit 配置
   - OkHttp 拦截器
   - JWT 令牌自动添加 (AuthInterceptor)
   - 错误处理拦截器 (ErrorInterceptor)
   - 请求重试拦截器 (RetryInterceptor)
   - API 接口定义

2. **Repository 层**
   - BaseRepository - 提供统一的错误处理
   - AuthRepository - 认证相关操作
   - UserRepository - 用户信息管理
   - BettingPlanRepository - 对赌计划管理
   - CheckInRepository - 打卡记录管理
   - PaymentRepository - 支付操作
   - SocialRepository - 社交功能

3. **网络结果封装**
   - NetworkResult - 统一的网络请求结果类型
   - NetworkException - 自定义网络异常类型
   - ErrorResponse - API 错误响应模型

4. **本地数据库配置**
   - Room 数据库
   - 用户、计划、打卡实体
   - DAO 接口

5. **依赖注入**
   - Hilt 配置
   - 网络模块 (NetworkModule)
   - Repository 模块 (RepositoryModule)
   - 数据库模块 (DatabaseModule)

6. **数据模型**
   - 认证相关模型
   - 用户相关模型
   - 对赌计划模型
   - 打卡记录模型
   - 支付相关模型
   - 社交功能模型

## 构建和运行

### 前置要求

- Android Studio Hedgehog | 2023.1.1 或更高版本
- JDK 17
- Android SDK (API 24-34)
- Gradle 8.2+

### 构建步骤

1. 克隆项目
```bash
git clone <repository-url>
cd android
```

2. 在 Android Studio 中打开项目

3. 同步 Gradle 依赖

4. 配置后端 API 地址
   - 编辑 `app/src/main/java/com/weightloss/betting/di/NetworkModule.kt`
   - 修改 `BASE_URL` 为你的后端服务器地址

5. 运行项目
   - 连接 Android 设备或启动模拟器
   - 点击 Run 按钮

## API 配置

默认 API 地址为 `http://10.0.2.2:8000/`,这是 Android 模拟器访问本机的地址。

如果使用真机测试,需要修改为实际的服务器 IP 地址。

## 下一步开发计划

1. 实现认证功能 UI
2. 实现用户信息管理 UI
3. 实现对赌计划功能 UI
4. 实现打卡功能 UI
5. 实现支付功能 UI
6. 实现社交功能 UI

## 注意事项

- 确保后端 API 服务已启动
- 模拟器需要配置网络代理才能访问外网
- 真机测试时需要确保设备和服务器在同一网络

## 许可证

MIT License


## 网络层架构说明

### 拦截器链

网络请求按以下顺序经过拦截器处理:

1. **RetryInterceptor** - 请求重试
   - 自动重试失败的请求(最多3次)
   - 使用指数退避策略
   - 仅对超时和服务器错误重试

2. **AuthInterceptor** - 认证
   - 自动添加 JWT 令牌到请求头
   - 跳过登录/注册等认证请求

3. **ErrorInterceptor** - 错误处理
   - 统一处理 HTTP 错误响应
   - 将错误码转换为自定义异常类型
   - 解析服务器返回的错误信息

4. **LoggingInterceptor** - 日志记录
   - 记录请求和响应详情
   - 仅在 Debug 模式下启用

### Repository 层设计

Repository 层负责:
- 封装网络请求逻辑
- 统一错误处理
- 提供类型安全的 API
- 管理令牌存储

所有 Repository 继承自 `BaseRepository`,使用 `safeApiCall` 方法执行网络请求:

```kotlin
suspend fun getUserProfile(userId: String): NetworkResult<User> {
    return safeApiCall { apiService.getUserProfile(userId) }
}
```

### 错误处理

网络请求的错误通过 `NetworkException` 类型表示:

- `NetworkError` - 网络连接失败
- `ServerError` - 服务器错误 (5xx)
- `UnauthorizedError` - 未授权 (401)
- `ValidationError` - 数据验证失败 (400, 422)
- `TimeoutError` - 请求超时
- `UnknownError` - 未知错误

使用示例:

```kotlin
when (val result = authRepository.login(request)) {
    is NetworkResult.Success -> {
        // 处理成功
        val user = result.data.user
    }
    is NetworkResult.Error -> {
        // 处理错误
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
```

### 请求重试机制

RetryInterceptor 实现了自动重试机制:
- 最多重试 3 次
- 初始退避时间 1 秒
- 每次重试时间翻倍 (1s, 2s, 3s)
- 仅对超时和服务器错误 (5xx) 重试
- 客户端错误 (4xx) 不重试

### 令牌管理

TokenManager 使用 DataStore 安全存储令牌:
- 访问令牌 (Access Token)
- 刷新令牌 (Refresh Token)

当访问令牌过期时,应用应调用 `AuthRepository.refreshToken()` 获取新令牌。

