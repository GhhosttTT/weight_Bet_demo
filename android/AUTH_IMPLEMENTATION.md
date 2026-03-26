# Android 认证功能实现总结

## 任务概述

实现了 Android 客户端的完整认证功能,包括登录界面、注册界面、令牌管理和自动刷新机制。

## 已完成的功能

### 任务 20.1: 创建登录界面 ✅

#### LoginViewModel
- 处理登录逻辑
- 验证邮箱格式和密码
- 调用 AuthRepository 进行登录
- 管理登录状态 (Loading, Success, Error)
- 支持 Google 登录 (预留接口)

#### LoginActivity
- 邮箱/密码输入界面
- 登录按钮和 Google 登录按钮
- 显示加载状态
- 错误提示
- 登录成功后跳转到主页
- 跳转到注册页面

#### 功能特点
- 输入验证 (邮箱格式、密码非空)
- 友好的错误提示 (根据不同错误类型显示不同消息)
- 加载状态显示
- 自动保存 JWT 令牌到 SharedPreferences (通过 DataStore)

### 任务 20.2: 创建注册界面 ✅

#### RegisterViewModel
- 处理注册逻辑
- 完整的输入验证:
  - 邮箱格式验证
  - 密码长度验证 (至少 6 位)
  - 密码确认验证
  - 昵称长度验证 (2-20 字符)
  - 年龄范围验证 (13-120)
  - 身高范围验证 (100-250 cm)
  - 体重范围验证 (30-300 kg)
- 调用 AuthRepository 进行注册
- 管理注册状态 (Loading, Success, Error)

#### RegisterActivity
- 完整的注册表单:
  - 邮箱输入
  - 密码输入
  - 确认密码输入
  - 昵称输入
  - 性别选择 (Spinner)
  - 年龄输入
  - 身高输入
  - 当前体重输入
- 注册按钮
- 返回登录链接
- 显示加载状态
- 错误提示
- 注册成功后跳转到主页

#### 功能特点
- 完整的客户端验证
- 友好的错误提示
- 自动保存 JWT 令牌
- 注册成功后自动登录

### 任务 20.3: 实现 Google 登录 (部分完成) ⚠️

#### 已实现
- LoginViewModel 中的 `googleLogin()` 方法
- AuthRepository 中的 `googleLogin()` 方法
- LoginActivity 中的 Google 登录按钮

#### 待完成
- 集成 Google Sign-In SDK
- 配置 Google OAuth 客户端 ID
- 实现 Google 登录回调处理

#### 使用说明
Google 登录功能的框架已经搭建完成,需要:
1. 在 `build.gradle` 中添加 Google Sign-In 依赖
2. 在 Google Cloud Console 配置 OAuth 客户端
3. 在 LoginActivity 中实现 Google Sign-In 流程
4. 获取 ID Token 后调用 `viewModel.googleLogin(idToken)`

### 任务 20.4: 实现令牌刷新机制 ✅

#### TokenRefreshManager
- 检查令牌有效性
- 自动刷新令牌
- 刷新失败时清除令牌

#### 功能特点
- 提供 `ensureValidToken()` 方法检查令牌
- 提供 `refreshToken()` 方法刷新令牌
- 刷新失败时自动清除令牌,强制用户重新登录

#### 使用方式
```kotlin
// 在需要确保令牌有效的地方调用
val isValid = tokenRefreshManager.ensureValidToken()
if (!isValid) {
    // 跳转到登录页
}
```

#### 注意事项
- 当前实现简化了令牌过期检查
- 生产环境应该解析 JWT 的 `exp` 字段判断过期时间
- 可以在 AuthInterceptor 中集成自动刷新逻辑

### 额外功能: SplashActivity ✅

#### 功能
- 应用启动时检查登录状态
- 如果已登录,直接跳转到主页
- 如果未登录,跳转到登录页

#### 实现
- 使用 TokenManager 检查是否存在访问令牌
- 使用协程异步检查
- 自动导航到相应页面

## 文件结构

```
android/app/src/main/java/com/weightloss/betting/
├── ui/
│   └── auth/
│       ├── LoginViewModel.kt           # 登录 ViewModel
│       ├── LoginActivity.kt            # 登录界面
│       ├── RegisterViewModel.kt        # 注册 ViewModel
│       ├── RegisterActivity.kt         # 注册界面
│       └── SplashActivity.kt           # 启动页
├── data/
│   └── remote/
│       └── TokenRefreshManager.kt      # 令牌刷新管理器
└── res/
    └── layout/
        ├── activity_login.xml          # 登录界面布局
        └── activity_register.xml       # 注册界面布局
```

## 技术特点

1. **MVVM 架构**: 使用 ViewModel 分离业务逻辑和 UI
2. **LiveData**: 响应式数据更新
3. **Hilt 依赖注入**: 自动管理依赖
4. **协程**: 异步处理网络请求
5. **DataStore**: 安全存储令牌
6. **Material Design**: 使用 Material Components 构建 UI
7. **ViewBinding**: 类型安全的视图绑定

## 使用示例

### 登录流程

```kotlin
// 用户输入邮箱和密码
val email = "user@example.com"
val password = "password123"

// ViewModel 处理登录
viewModel.login(email, password)

// 观察登录状态
viewModel.loginState.observe(this) { state ->
    when (state) {
        is LoginState.Loading -> {
            // 显示加载状态
        }
        is LoginState.Success -> {
            // 登录成功,跳转到主页
            navigateToMain()
        }
        is LoginState.Error -> {
            // 显示错误信息
            Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
        }
    }
}
```

### 注册流程

```kotlin
// 用户填写注册表单
viewModel.register(
    email = "user@example.com",
    password = "password123",
    confirmPassword = "password123",
    nickname = "张三",
    gender = "male",
    age = 25,
    height = 175.0,
    currentWeight = 70.0
)

// 观察注册状态
viewModel.registerState.observe(this) { state ->
    when (state) {
        is RegisterState.Loading -> {
            // 显示加载状态
        }
        is RegisterState.Success -> {
            // 注册成功,跳转到主页
            navigateToMain()
        }
        is RegisterState.Error -> {
            // 显示错误信息
            Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
        }
    }
}
```

### 令牌刷新

```kotlin
// 检查令牌有效性
lifecycleScope.launch {
    val isValid = tokenRefreshManager.ensureValidToken()
    if (!isValid) {
        // 令牌无效,跳转到登录页
        navigateToLogin()
    }
}
```

## 错误处理

### 登录错误
- **邮箱或密码错误** (401): "邮箱或密码错误"
- **网络连接失败**: "网络连接失败,请检查网络"
- **请求超时**: "请求超时,请重试"
- **其他错误**: 显示服务器返回的错误信息

### 注册错误
- **邮箱已注册** (ValidationError): 显示服务器返回的错误信息
- **数据验证失败**: 显示具体的验证错误
- **网络连接失败**: "网络连接失败,请检查网络"
- **请求超时**: "请求超时,请重试"

## 安全性

1. **密码不明文存储**: 密码仅在传输时使用,不在客户端存储
2. **令牌安全存储**: 使用 DataStore 加密存储令牌
3. **HTTPS 通信**: 所有网络请求使用 HTTPS
4. **输入验证**: 客户端和服务器双重验证

## 待完成的工作

### Google 登录集成
1. 添加 Google Sign-In SDK 依赖:
```gradle
implementation 'com.google.android.gms:play-services-auth:20.7.0'
```

2. 配置 Google OAuth 客户端 ID

3. 实现 Google Sign-In 流程:
```kotlin
// 在 LoginActivity 中
private fun setupGoogleSignIn() {
    val gso = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
        .requestIdToken(getString(R.string.default_web_client_id))
        .requestEmail()
        .build()
    
    val googleSignInClient = GoogleSignIn.getClient(this, gso)
    
    binding.btnGoogleLogin.setOnClickListener {
        val signInIntent = googleSignInClient.signInIntent
        startActivityForResult(signInIntent, RC_SIGN_IN)
    }
}

override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
    super.onActivityResult(requestCode, resultCode, data)
    
    if (requestCode == RC_SIGN_IN) {
        val task = GoogleSignIn.getSignedInAccountFromIntent(data)
        try {
            val account = task.getResult(ApiException::class.java)
            val idToken = account.idToken
            if (idToken != null) {
                viewModel.googleLogin(idToken)
            }
        } catch (e: ApiException) {
            Toast.makeText(this, "Google 登录失败", Toast.LENGTH_SHORT).show()
        }
    }
}
```

### 令牌自动刷新
在 AuthInterceptor 中集成自动刷新逻辑:
```kotlin
override fun intercept(chain: Interceptor.Chain): Response {
    val originalRequest = chain.request()
    
    // 确保令牌有效
    if (!tokenRefreshManager.ensureValidTokenSync()) {
        // 令牌无效,返回 401 错误
        return Response.Builder()
            .request(originalRequest)
            .protocol(Protocol.HTTP_1_1)
            .code(401)
            .message("Unauthorized")
            .body(ResponseBody.create(null, ""))
            .build()
    }
    
    // 继续正常流程
    // ...
}
```

### JWT 过期时间解析
实现 JWT 解析以准确判断令牌是否过期:
```kotlin
private fun isTokenExpiringSoon(token: String): Boolean {
    try {
        val parts = token.split(".")
        if (parts.size != 3) return true
        
        val payload = String(Base64.decode(parts[1], Base64.URL_SAFE))
        val json = JSONObject(payload)
        val exp = json.getLong("exp")
        val now = System.currentTimeMillis() / 1000
        
        // 如果令牌在 5 分钟内过期,返回 true
        return (exp - now) < 300
    } catch (e: Exception) {
        return true
    }
}
```

## 测试建议

### 单元测试
- 测试 ViewModel 的输入验证逻辑
- 测试登录/注册成功和失败场景
- 测试令牌刷新逻辑

### UI 测试
- 测试登录界面交互
- 测试注册界面交互
- 测试错误提示显示
- 测试页面跳转

### 集成测试
- 测试完整的登录流程
- 测试完整的注册流程
- 测试令牌自动刷新
- 测试登录状态持久化

## 总结

Android 认证功能已基本完成,包括:
- ✅ 登录界面和逻辑
- ✅ 注册界面和逻辑
- ⚠️ Google 登录 (框架已搭建,需要集成 SDK)
- ✅ 令牌刷新机制
- ✅ 启动页和登录状态检查

认证功能提供了完整的用户体验,包括输入验证、错误处理、加载状态显示和自动登录。为后续的功能开发奠定了坚实的基础。
