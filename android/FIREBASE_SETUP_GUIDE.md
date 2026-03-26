# Firebase Cloud Messaging 配置指南

## 概述

本指南说明如何配置 Firebase Cloud Messaging (FCM) 以支持 Android 推送通知功能。

## 前置条件

- Google 账号
- Android 项目已创建

## 配置步骤

### 1. 创建 Firebase 项目

1. 访问 [Firebase Console](https://console.firebase.google.com/)
2. 点击"添加项目"
3. 输入项目名称: `weight-loss-betting-app`
4. 选择是否启用 Google Analytics(可选)
5. 点击"创建项目"

### 2. 添加 Android 应用

1. 在 Firebase 项目概览页面,点击"添加应用"
2. 选择 Android 图标
3. 填写应用信息:
   - **Android 包名**: `com.weightloss.betting`
   - **应用昵称**: Weight Loss Betting (可选)
   - **调试签名证书 SHA-1**: (可选,用于 Google 登录)
4. 点击"注册应用"

### 3. 下载配置文件

1. 下载 `google-services.json` 文件
2. 将文件放置到 `android/app/` 目录下
3. 确保文件路径为: `android/app/google-services.json`

### 4. 添加 Firebase SDK

**项目级 build.gradle** (`android/build.gradle`):

```gradle
buildscript {
    dependencies {
        // ... existing dependencies
        classpath 'com.google.gms:google-services:4.4.0'
    }
}
```

**应用级 build.gradle** (`android/app/build.gradle`):

已在代码中添加:
```gradle
plugins {
    // ... existing plugins
    id 'com.google.gms.google-services'
}

dependencies {
    // Firebase Cloud Messaging
    implementation platform('com.google.firebase:firebase-bom:32.7.0')
    implementation 'com.google.firebase:firebase-messaging-ktx'
}
```

### 5. 配置 FCM 服务

**AndroidManifest.xml**:

已在代码中添加:
```xml
<service
    android:name=".service.FCMService"
    android:exported="false">
    <intent-filter>
        <action android:name="com.google.firebase.MESSAGING_EVENT" />
    </intent-filter>
</service>
```

### 6. 获取 FCM 服务器密钥

1. 在 Firebase Console 中,进入项目设置
2. 选择"Cloud Messaging"选项卡
3. 找到"服务器密钥"(Server Key)
4. 复制服务器密钥
5. 将服务器密钥配置到后端服务器

**后端配置示例**:
```python
# backend/.env
FCM_SERVER_KEY=your_server_key_here
```

### 7. 测试 FCM 配置

#### 7.1 获取设备令牌

在应用启动时,FCM 会自动生成设备令牌:

```kotlin
// FCMService.kt
override fun onNewToken(token: String) {
    super.onNewToken(token)
    Log.d("FCM", "Device Token: $token")
    
    // 注册到后端服务器
    serviceScope.launch {
        notificationRepository.registerDeviceToken(token)
    }
}
```

#### 7.2 发送测试通知

在 Firebase Console 中:
1. 进入"Cloud Messaging"
2. 点击"发送第一条消息"
3. 输入通知标题和内容
4. 选择目标应用
5. 点击"发送测试消息"
6. 输入设备令牌
7. 点击"测试"

### 8. 通知类型配置

应用支持以下通知类型:

| 类型 | 说明 | 数据字段 |
|------|------|----------|
| `invite` | 邀请通知 | `type`, `relatedId` |
| `plan_active` | 计划生效通知 | `type`, `relatedId` |
| `settlement` | 结算通知 | `type`, `relatedId` |
| `check_in_reminder` | 打卡提醒 | `type`, `relatedId` |

**通知数据格式**:
```json
{
  "notification": {
    "title": "通知标题",
    "body": "通知内容"
  },
  "data": {
    "type": "invite",
    "relatedId": "plan_id_123"
  },
  "to": "device_token"
}
```

### 9. 后端发送通知示例

**Python (FastAPI) 示例**:

```python
import requests
import json

def send_fcm_notification(device_token: str, title: str, body: str, notification_type: str, related_id: str = None):
    """
    发送 FCM 通知
    """
    url = "https://fcm.googleapis.com/fcm/send"
    
    headers = {
        "Authorization": f"Bearer {FCM_SERVER_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "notification": {
            "title": title,
            "body": body
        },
        "data": {
            "type": notification_type,
            "relatedId": related_id or ""
        },
        "to": device_token
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.json()

# 使用示例
send_fcm_notification(
    device_token="user_device_token",
    title="计划邀请",
    body="用户 A 邀请你参与减肥对赌计划",
    notification_type="invite",
    related_id="plan_123"
)
```

### 10. 通知权限请求

**Android 13+ 需要请求通知权限**:

```kotlin
// 在适当的时机请求权限
if (!NotificationPermissionHelper.hasNotificationPermission(this)) {
    NotificationPermissionHelper.requestNotificationPermission(this)
}

// 处理权限结果
override fun onRequestPermissionsResult(
    requestCode: Int,
    permissions: Array<out String>,
    grantResults: IntArray
) {
    super.onRequestPermissionsResult(requestCode, permissions, grantResults)
    NotificationPermissionHelper.handlePermissionResult(
        requestCode,
        grantResults,
        onGranted = {
            // 权限已授予,注册 FCM 令牌
            registerFCMToken()
        },
        onDenied = {
            // 权限被拒绝,显示提示
            Toast.makeText(this, "需要通知权限才能接收提醒", Toast.LENGTH_LONG).show()
        }
    )
}
```

## 常见问题

### Q1: 收不到通知?

**检查清单**:
1. ✅ `google-services.json` 文件是否正确放置
2. ✅ 应用包名是否与 Firebase 配置一致
3. ✅ 设备令牌是否成功注册到后端
4. ✅ 通知权限是否已授予(Android 13+)
5. ✅ 应用是否在前台/后台运行
6. ✅ 设备网络连接是否正常

### Q2: 如何调试 FCM?

**启用日志**:
```kotlin
// 在 Application 类中
FirebaseMessaging.getInstance().isAutoInitEnabled = true

// 查看日志
adb logcat | grep FCM
```

### Q3: 前台和后台通知有什么区别?

- **前台**: 通知由 `FCMService.onMessageReceived()` 处理,可以自定义显示
- **后台**: 通知由系统自动显示,点击后启动应用

### Q4: 如何测试不同类型的通知?

使用 Firebase Console 的"发送测试消息"功能,在"其他选项"中添加自定义数据:
```json
{
  "type": "invite",
  "relatedId": "plan_123"
}
```

## 安全建议

1. **不要在客户端存储服务器密钥**: 服务器密钥应该只在后端使用
2. **验证通知来源**: 在后端验证通知请求的合法性
3. **限制通知频率**: 避免发送过多通知导致用户反感
4. **提供通知设置**: 允许用户自定义通知偏好

## 生产环境配置

### 1. 使用不同的 Firebase 项目

建议为开发、测试和生产环境创建不同的 Firebase 项目:
- `weight-loss-betting-dev`
- `weight-loss-betting-test`
- `weight-loss-betting-prod`

### 2. 配置构建变体

**build.gradle**:
```gradle
android {
    buildTypes {
        debug {
            applicationIdSuffix ".debug"
            // 使用开发环境的 google-services.json
        }
        release {
            // 使用生产环境的 google-services.json
        }
    }
}
```

### 3. 监控通知发送

在 Firebase Console 中监控:
- 通知发送成功率
- 设备令牌注册数量
- 通知打开率

## 参考资源

- [Firebase Cloud Messaging 官方文档](https://firebase.google.com/docs/cloud-messaging)
- [Android 通知最佳实践](https://developer.android.com/guide/topics/ui/notifiers/notifications)
- [FCM HTTP v1 API](https://firebase.google.com/docs/reference/fcm/rest/v1/projects.messages)

## 总结

完成以上步骤后,应用将能够:
- ✅ 接收推送通知
- ✅ 处理不同类型的通知
- ✅ 点击通知跳转到相应页面
- ✅ 在前台和后台都能正常工作

如有问题,请参考 Firebase Console 的日志和错误信息。
