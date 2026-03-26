# 剩余工作指南

## 概述

本文档列出了 Android 任务 25-27 中尚未完成的工作项,并提供实现建议。

## 待完成工作清单

### 1. 评论功能 UI (任务 26.2) ⏳

**优先级**: 高

**需要创建的文件**:
- `res/layout/dialog_comment.xml` - 评论对话框布局
- `res/layout/item_comment.xml` - 评论列表项布局
- `ui/social/CommentViewModel.kt` - 评论 ViewModel
- `ui/social/CommentAdapter.kt` - 评论适配器

**实现建议**:

#### 1.1 创建评论对话框布局

```xml
<!-- res/layout/dialog_comment.xml -->
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:padding="16dp">

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="发表评论"
        android:textSize="18sp"
        android:textStyle="bold"
        android:layout_marginBottom="16dp" />

    <com.google.android.material.textfield.TextInputLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:hint="输入评论内容 (最多500字)">

        <com.google.android.material.textfield.TextInputEditText
            android:id="@+id/etComment"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:inputType="textMultiLine"
            android:lines="4"
            android:maxLength="500" />

    </com.google.android.material.textfield.TextInputLayout>

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        android:layout_marginTop="16dp">

        <Button
            android:id="@+id/btnCancel"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="取消"
            android:layout_marginEnd="8dp"
            style="@style/Widget.Material3.Button.OutlinedButton" />

        <Button
            android:id="@+id/btnSubmit"
            android:layout_width="0dp"
            android:layout_height="wrap_content"
            android:layout_weight="1"
            android:text="发表"
            android:layout_marginStart="8dp" />

    </LinearLayout>

</LinearLayout>
```

#### 1.2 在 PlanDetailActivity 中添加评论功能

```kotlin
// 在 PlanDetailActivity 中添加
private fun showCommentDialog() {
    val dialogView = layoutInflater.inflate(R.layout.dialog_comment, null)
    val etComment = dialogView.findViewById<TextInputEditText>(R.id.etComment)
    val btnCancel = dialogView.findViewById<Button>(R.id.btnCancel)
    val btnSubmit = dialogView.findViewById<Button>(R.id.btnSubmit)
    
    val dialog = MaterialAlertDialogBuilder(this)
        .setView(dialogView)
        .create()
    
    btnCancel.setOnClickListener {
        dialog.dismiss()
    }
    
    btnSubmit.setOnClickListener {
        val content = etComment.text.toString().trim()
        if (content.isEmpty()) {
            Toast.makeText(this, "请输入评论内容", Toast.LENGTH_SHORT).show()
            return@setOnClickListener
        }
        
        if (content.length > 500) {
            Toast.makeText(this, "评论内容不能超过500字", Toast.LENGTH_SHORT).show()
            return@setOnClickListener
        }
        
        // 调用 ViewModel 发表评论
        viewModel.postComment(planId, content)
        dialog.dismiss()
    }
    
    dialog.show()
}
```

### 2. 鼓励功能 (任务 26.3) ⏳

**优先级**: 中

**需要添加的 API**:

```kotlin
// ApiService.kt
@POST("api/social/users/{userId}/encourage")
suspend fun encourageUser(
    @Path("userId") userId: String,
    @Body request: Map<String, String>
): Response<Unit>
```

**实现建议**:

在用户信息页面或计划详情页面添加鼓励按钮:

```kotlin
// ProfileActivity.kt 或 PlanDetailActivity.kt
binding.btnEncourage.setOnClickListener {
    viewModel.encourageUser(targetUserId)
}

// ViewModel
fun encourageUser(targetUserId: String) {
    viewModelScope.launch {
        when (val result = socialRepository.encourageUser(targetUserId)) {
            is NetworkResult.Success -> {
                _encourageState.value = EncourageState.Success("鼓励成功!")
            }
            is NetworkResult.Error -> {
                _encourageState.value = EncourageState.Error(
                    result.exception.message ?: "鼓励失败"
                )
            }
            is NetworkResult.Loading -> {
                // Already handled
            }
        }
    }
}
```

### 3. Firebase 配置文件 (任务 25.1) ⏳

**优先级**: 高

**步骤**:
1. 访问 [Firebase Console](https://console.firebase.google.com/)
2. 创建项目或使用现有项目
3. 添加 Android 应用(包名: `com.weightloss.betting`)
4. 下载 `google-services.json`
5. 将文件放置到 `android/app/` 目录

**详细说明**: 参考 `FIREBASE_SETUP_GUIDE.md`

### 4. 自定义主题颜色 (任务 27.3) ⏳

**优先级**: 中

**实现建议**:

创建或修改 `res/values/themes.xml`:

```xml
<resources>
    <style name="Theme.WeightLossBetting" parent="Theme.Material3.Light.NoActionBar">
        <!-- Primary brand color -->
        <item name="colorPrimary">@color/primary</item>
        <item name="colorPrimaryVariant">@color/primary_dark</item>
        <item name="colorOnPrimary">@android:color/white</item>
        
        <!-- Secondary brand color -->
        <item name="colorSecondary">@color/secondary</item>
        <item name="colorSecondaryVariant">@color/secondary_dark</item>
        <item name="colorOnSecondary">@android:color/white</item>
        
        <!-- Status bar color -->
        <item name="android:statusBarColor">?attr/colorPrimaryVariant</item>
    </style>
</resources>
```

创建 `res/values/colors.xml`:

```xml
<resources>
    <!-- Primary colors -->
    <color name="primary">#FF6200EE</color>
    <color name="primary_dark">#FF3700B3</color>
    
    <!-- Secondary colors -->
    <color name="secondary">#FF03DAC5</color>
    <color name="secondary_dark">#FF018786</color>
    
    <!-- Background colors -->
    <color name="background">#FFFFFFFF</color>
    <color name="surface">#FFFFFFFF</color>
    
    <!-- Text colors -->
    <color name="text_primary">#FF000000</color>
    <color name="text_secondary">#FF757575</color>
</resources>
```

### 5. 深色模式支持 (任务 27.3) ⏳

**优先级**: 低

**实现建议**:

创建 `res/values-night/themes.xml`:

```xml
<resources>
    <style name="Theme.WeightLossBetting" parent="Theme.Material3.Dark.NoActionBar">
        <!-- Primary brand color -->
        <item name="colorPrimary">@color/primary_night</item>
        <item name="colorPrimaryVariant">@color/primary_dark_night</item>
        <item name="colorOnPrimary">@android:color/black</item>
        
        <!-- Secondary brand color -->
        <item name="colorSecondary">@color/secondary_night</item>
        <item name="colorSecondaryVariant">@color/secondary_dark_night</item>
        <item name="colorOnSecondary">@android:color/black</item>
        
        <!-- Status bar color -->
        <item name="android:statusBarColor">?attr/colorPrimaryVariant</item>
    </style>
</resources>
```

创建 `res/values-night/colors.xml`:

```xml
<resources>
    <!-- Primary colors for dark mode -->
    <color name="primary_night">#FFBB86FC</color>
    <color name="primary_dark_night">#FF6200EE</color>
    
    <!-- Secondary colors for dark mode -->
    <color name="secondary_night">#FF03DAC6</color>
    <color name="secondary_dark_night">#FF03DAC6</color>
    
    <!-- Background colors for dark mode -->
    <color name="background">#FF121212</color>
    <color name="surface">#FF121212</color>
    
    <!-- Text colors for dark mode -->
    <color name="text_primary">#FFFFFFFF</color>
    <color name="text_secondary">#FFB0B0B0</color>
</resources>
```

### 6. 用户 ID 管理 (所有任务) ⏳

**优先级**: 高

**问题**: 当前代码中使用硬编码的 `userId = "current_user_id"`

**解决方案**:

创建 `util/SessionManager.kt`:

```kotlin
package com.weightloss.betting.util

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "session")

@Singleton
class SessionManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val USER_ID_KEY = stringPreferencesKey("user_id")
    
    val userId: Flow<String?> = context.dataStore.data.map { preferences ->
        preferences[USER_ID_KEY]
    }
    
    suspend fun saveUserId(userId: String) {
        context.dataStore.edit { preferences ->
            preferences[USER_ID_KEY] = userId
        }
    }
    
    suspend fun clearSession() {
        context.dataStore.edit { preferences ->
            preferences.clear()
        }
    }
}
```

**使用示例**:

```kotlin
@AndroidEntryPoint
class ProfileActivity : AppCompatActivity() {
    
    @Inject
    lateinit var sessionManager: SessionManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        lifecycleScope.launch {
            sessionManager.userId.collect { userId ->
                userId?.let {
                    viewModel.loadUserProfile(it)
                }
            }
        }
    }
}
```

### 7. 自定义通知图标 (任务 25.2) ⏳

**优先级**: 低

**步骤**:
1. 创建通知图标(24x24 dp, 白色, 透明背景)
2. 放置到 `res/drawable/ic_notification.xml`
3. 更新 FCMService 中的图标引用

**图标示例** (`res/drawable/ic_notification.xml`):

```xml
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFFFF"
        android:pathData="M12,2C6.48,2 2,6.48 2,12s4.48,10 10,10 10,-4.48 10,-10S17.52,2 12,2zM13,17h-2v-2h2v2zM13,13h-2L11,7h2v6z"/>
</vector>
```

### 8. 单元测试 (所有任务) ⏳

**优先级**: 中

**需要测试的组件**:
- ViewModel 测试
- Repository 测试
- Adapter 测试

**示例测试**:

```kotlin
// LeaderboardViewModelTest.kt
@ExperimentalCoroutinesApi
class LeaderboardViewModelTest {
    
    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()
    
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()
    
    private lateinit var viewModel: LeaderboardViewModel
    private lateinit var socialRepository: SocialRepository
    
    @Before
    fun setup() {
        socialRepository = mockk()
        viewModel = LeaderboardViewModel(socialRepository)
    }
    
    @Test
    fun `loadLeaderboard success should update state`() = runTest {
        // Given
        val entries = listOf(
            LeaderboardEntry("1", "User1", 10.5, 1),
            LeaderboardEntry("2", "User2", 8.0, 2)
        )
        coEvery { socialRepository.getLeaderboard(any()) } returns NetworkResult.Success(entries)
        
        // When
        viewModel.loadLeaderboard("weight-loss")
        
        // Then
        val state = viewModel.leaderboardState.getOrAwaitValue()
        assertTrue(state is LeaderboardState.Success)
        assertEquals(2, (state as LeaderboardState.Success).entries.size)
    }
}
```

## 实现优先级建议

### 第一阶段 (必须完成):
1. ✅ Firebase 配置文件
2. ✅ 用户 ID 管理
3. ✅ 评论功能 UI

### 第二阶段 (建议完成):
4. ✅ 鼓励功能
5. ✅ 自定义主题颜色
6. ✅ 单元测试

### 第三阶段 (可选):
7. ✅ 深色模式支持
8. ✅ 自定义通知图标
9. ✅ 动画效果

## 测试清单

完成实现后,请测试以下功能:

### 通知功能:
- [ ] FCM 令牌注册成功
- [ ] 接收邀请通知
- [ ] 接收计划生效通知
- [ ] 接收结算通知
- [ ] 接收打卡提醒
- [ ] 点击通知跳转正确
- [ ] 通知权限请求正常

### 社交功能:
- [ ] 排行榜数据加载正确
- [ ] 三种排行榜类型切换正常
- [ ] 勋章列表显示正确
- [ ] 评论发表成功
- [ ] 评论列表显示正确
- [ ] 鼓励功能正常

### UI/UX:
- [ ] 底部导航切换流畅
- [ ] 加载状态显示正确
- [ ] 错误提示清晰
- [ ] 网络超时处理正确
- [ ] 主题颜色统一
- [ ] 深色模式正常(如果实现)

## 参考资源

- [Android 开发文档](https://developer.android.com/)
- [Material Design 指南](https://material.io/design)
- [Firebase 文档](https://firebase.google.com/docs)
- [Kotlin 协程指南](https://kotlinlang.org/docs/coroutines-guide.html)
- [Hilt 依赖注入](https://developer.android.com/training/dependency-injection/hilt-android)

## 总结

完成以上工作后,Android 客户端将具备完整的功能:
- ✅ 通知系统
- ✅ 社交功能
- ✅ 现代化 UI/UX
- ✅ 完善的错误处理
- ✅ 良好的用户体验

预计完成时间: 2-3 天(取决于优先级选择)
