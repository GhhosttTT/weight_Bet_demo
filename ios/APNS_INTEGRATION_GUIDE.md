# Apple Push Notification Service (APNs) Integration Guide

## Overview

This guide explains the APNs integration for the Weight Loss Betting iOS app. The implementation follows Apple's best practices and integrates with the backend notification system.

## Architecture

### Components

1. **NotificationService** (`Data/Service/NotificationService.swift`)
   - Singleton service managing all notification operations
   - Handles device token registration with backend
   - Processes incoming notifications
   - Manages notification permissions
   - Handles notification navigation

2. **AppDelegate** (`AppDelegate.swift`)
   - Configures APNs on app launch
   - Implements `UNUserNotificationCenterDelegate`
   - Handles device token registration
   - Processes notifications in different app states

3. **NotificationRepository** (`Data/Repository/NotificationRepository.swift`)
   - Communicates with backend API
   - Registers device tokens
   - Handles network errors and retries

4. **NotificationPermissionHelper** (`UI/Common/NotificationPermissionHelper.swift`)
   - UI helper for requesting permissions
   - Shows settings alerts when needed
   - Provides user-friendly permission explanations

## Setup Requirements

### 1. Apple Developer Account Configuration

Before APNs can work, you need to configure your Apple Developer account:

1. **Enable Push Notifications Capability**
   - Open Xcode project
   - Select target → Signing & Capabilities
   - Click "+ Capability"
   - Add "Push Notifications"

2. **Create APNs Certificate or Key**
   
   **Option A: APNs Authentication Key (Recommended)**
   - Go to Apple Developer Portal
   - Certificates, Identifiers & Profiles → Keys
   - Create new key with "Apple Push Notifications service (APNs)" enabled
   - Download the .p8 key file
   - Note the Key ID and Team ID
   - Upload to Firebase Console (if using FCM) or your backend

   **Option B: APNs Certificate**
   - Go to Apple Developer Portal
   - Certificates, Identifiers & Profiles → Certificates
   - Create new certificate for "Apple Push Notification service SSL"
   - Download and install in Keychain
   - Export as .p12 file
   - Upload to your backend

3. **Configure App ID**
   - Ensure your App ID has Push Notifications enabled
   - Bundle ID must match: `com.weightloss.betting` (or your configured ID)

### 2. Xcode Project Configuration

The following configurations are already set up in the project:

1. **Info.plist**
   - `NSUserNotificationsUsageDescription` - Explains why notifications are needed

2. **Capabilities**
   - Push Notifications capability must be enabled
   - Background Modes → Remote notifications (if needed)

3. **Entitlements**
   - APNs environment (development/production) is automatically configured

### 3. Backend Configuration

Ensure your backend is configured to send APNs notifications:

1. **Device Token Registration Endpoint**
   ```
   POST /api/notifications/register
   {
     "device_token": "string",
     "platform": "ios"
   }
   ```

2. **Notification Payload Format**
   ```json
   {
     "aps": {
       "alert": {
         "title": "Notification Title",
         "body": "Notification Body"
       },
       "badge": 1,
       "sound": "default"
     },
     "type": "invite|plan_active|settlement|check_in_reminder",
     "relatedId": "plan_id_or_settlement_id"
   }
   ```

## Implementation Details

### Device Token Registration Flow

1. App launches → `AppDelegate.application(_:didFinishLaunchingWithOptions:)`
2. Request notification permissions → `NotificationService.requestNotificationPermissions()`
3. User grants permission → `UIApplication.shared.registerForRemoteNotifications()`
4. System generates device token → `AppDelegate.application(_:didRegisterForRemoteNotificationsWithDeviceToken:)`
5. Token sent to backend → `NotificationService.setDeviceToken()` → `NotificationRepository.registerDeviceToken()`
6. Backend stores token for future notifications

### Notification Handling Flow

**When App is in Foreground:**
1. Notification arrives → `userNotificationCenter(_:willPresent:withCompletionHandler:)`
2. `NotificationService.handleNotification()` processes the notification
3. Notification banner is shown with sound and badge
4. App can update UI based on notification data

**When App is in Background:**
1. Notification arrives → System shows notification banner
2. User taps notification → `userNotificationCenter(_:didReceive:withCompletionHandler:)`
3. `NotificationService.handleNotificationResponse()` processes the tap
4. App navigates to relevant screen based on notification type

**When App is Not Running:**
1. User taps notification → App launches
2. `AppDelegate.application(_:didFinishLaunchingWithOptions:)` receives notification data
3. After 1 second delay, notification is processed
4. App navigates to relevant screen

### Notification Types

The app handles the following notification types:

1. **invite** - Plan invitation from another user
   - Navigates to plan invitation screen
   - Shows plan details and accept/reject options

2. **plan_active** - Plan has been accepted and is now active
   - Navigates to active plan details
   - Shows plan progress and check-in options

3. **settlement** - Plan has been settled
   - Navigates to settlement results
   - Shows final results and payout information

4. **check_in_reminder** - Daily reminder to check in
   - Navigates to check-in screen
   - Shows current plan and weight input

### Error Handling

**Device Token Registration Failures:**
- Token is stored locally in UserDefaults
- Retry attempted on next app launch
- Retry attempted when user logs in
- Manual retry available via `NotificationService.retryPendingTokenRegistration()`

**Permission Denied:**
- User is shown alert to enable in Settings
- App continues to function without notifications
- Permission can be requested again later

**Network Errors:**
- Token registration failures are logged
- Automatic retry on next successful network request
- No user-facing error (silent failure)

## Usage Examples

### Request Notification Permission

```swift
// In your view controller (e.g., after login)
NotificationPermissionHelper.requestPermissionIfNeeded(from: self) { granted in
    if granted {
        print("Notifications enabled")
    } else {
        print("Notifications disabled")
    }
}
```

### Show Permission Explanation First

```swift
// Show explanation before requesting permission
NotificationPermissionHelper.showPermissionExplanation(from: self) {
    NotificationService.shared.requestNotificationPermissions { granted in
        print("Permission granted: \(granted)")
    }
}
```

### Handle Notification in Your View Controller

```swift
override func viewDidLoad() {
    super.viewDidLoad()
    
    // Observe notification events
    NotificationCenter.default.addObserver(
        self,
        selector: #selector(handleNotificationTap(_:)),
        name: .didTapNotification,
        object: nil
    )
}

@objc private func handleNotificationTap(_ notification: Notification) {
    guard let userInfo = notification.userInfo,
          let type = userInfo["type"] as? String,
          let relatedId = userInfo["relatedId"] as? String else {
        return
    }
    
    // Navigate based on notification type
    switch type {
    case "invite":
        navigateToPlanInvitation(planId: relatedId)
    case "plan_active":
        navigateToActivePlan(planId: relatedId)
    case "settlement":
        navigateToSettlement(settlementId: relatedId)
    case "check_in_reminder":
        navigateToCheckIn(planId: relatedId)
    default:
        break
    }
}
```

### Update Badge Count

```swift
// Update badge count
NotificationService.shared.updateBadgeCount(5)

// Clear badge
NotificationService.shared.clearBadge()
```

### Check Permission Status

```swift
NotificationService.shared.checkNotificationPermissionStatus { status in
    switch status {
    case .authorized:
        print("Notifications are enabled")
    case .denied:
        print("Notifications are disabled")
    case .notDetermined:
        print("Permission not requested yet")
    default:
        break
    }
}
```

## Testing

### Testing on Simulator

**Note:** APNs does not work on iOS Simulator. You must test on a physical device.

However, you can test local notifications on simulator:

```swift
// Test local notification
let content = UNMutableNotificationContent()
content.title = "Test Notification"
content.body = "This is a test"
content.sound = .default
content.userInfo = ["type": "invite", "relatedId": "test_plan_id"]

let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
let request = UNNotificationRequest(identifier: UUID().uuidString, content: content, trigger: trigger)

UNUserNotificationCenter.current().add(request)
```

### Testing on Physical Device

1. **Build and Run on Device**
   - Connect iPhone/iPad via USB
   - Select device in Xcode
   - Build and run (Cmd+R)

2. **Grant Notification Permission**
   - App will request permission on first launch
   - Grant permission in the system dialog

3. **Verify Device Token Registration**
   - Check Xcode console for: "✅ Successfully registered for remote notifications"
   - Check for: "✅ Device token registered successfully with backend"

4. **Send Test Notification from Backend**
   - Use your backend's notification sending endpoint
   - Or use Firebase Console (if using FCM)
   - Or use APNs testing tools

5. **Test Different App States**
   - Foreground: Notification banner should appear
   - Background: Tap notification to open app
   - Not running: Tap notification to launch app

### Testing with Firebase Console

If using Firebase Cloud Messaging:

1. Go to Firebase Console → Cloud Messaging
2. Click "Send your first message"
3. Enter notification title and text
4. Select your iOS app
5. Add custom data:
   - Key: `type`, Value: `invite`
   - Key: `relatedId`, Value: `test_plan_123`
6. Send test message to your device token

## Troubleshooting

### Device Token Not Received

**Symptoms:** `didRegisterForRemoteNotificationsWithDeviceToken` not called

**Solutions:**
1. Ensure Push Notifications capability is enabled
2. Check that you're testing on a physical device (not simulator)
3. Verify Apple Developer account has valid certificates/keys
4. Check device has internet connection
5. Try deleting app and reinstalling

### Notifications Not Appearing

**Symptoms:** Notifications sent but not displayed

**Solutions:**
1. Check notification permissions: Settings → App → Notifications
2. Verify device token is correctly registered with backend
3. Check notification payload format matches APNs requirements
4. Verify APNs certificate/key is valid and not expired
5. Check backend logs for sending errors

### Backend Registration Fails

**Symptoms:** "❌ Failed to register device token" in console

**Solutions:**
1. Check network connectivity
2. Verify backend API endpoint is correct
3. Check authentication token is valid
4. Review backend logs for errors
5. Token will be retried automatically on next app launch

### Notification Tap Not Working

**Symptoms:** Tapping notification doesn't navigate to correct screen

**Solutions:**
1. Verify notification payload includes `type` and `relatedId`
2. Check `NotificationService.handleNotificationResponse()` is called
3. Ensure navigation coordinator is properly set up
4. Add logging to track notification handling flow

## Best Practices

1. **Request Permission at the Right Time**
   - Don't request on first app launch
   - Request after user completes onboarding
   - Explain the value before requesting

2. **Handle Permission Denial Gracefully**
   - App should work without notifications
   - Provide option to enable later
   - Show value of notifications in UI

3. **Test Thoroughly**
   - Test all notification types
   - Test in all app states (foreground, background, not running)
   - Test permission flows
   - Test error scenarios

4. **Monitor and Log**
   - Log device token registration
   - Log notification receipt
   - Log navigation actions
   - Monitor backend registration success rate

5. **Keep Payload Small**
   - APNs has 4KB payload limit
   - Include only essential data
   - Fetch additional data from API if needed

## Security Considerations

1. **Device Token Protection**
   - Device tokens are sensitive
   - Only send over HTTPS
   - Store securely on backend
   - Invalidate tokens on logout

2. **Notification Content**
   - Don't include sensitive data in notifications
   - Use generic messages
   - Fetch details from API after tap

3. **Certificate/Key Management**
   - Keep APNs keys secure
   - Rotate keys periodically
   - Use separate keys for dev/prod
   - Never commit keys to version control

## Requirements Mapping

This implementation satisfies the following requirements:

- **需求 10.6**: WHERE 用户使用 iOS 平台 THEN THE System SHALL 使用 Apple Push Notification Service 发送通知
- **需求 10.7**: THE System SHALL 在用户授予通知权限后发送推送通知
- **需求 10.1**: WHEN 用户收到计划邀请 THEN THE System SHALL 发送推送通知
- **需求 10.2**: WHEN 计划被接受并生效 THEN THE System SHALL 向双方发送推送通知
- **需求 10.3**: WHEN 计划结算完成 THEN THE System SHALL 向双方发送结算结果通知
- **需求 10.4**: WHEN 到达每日打卡时间且用户未打卡 THEN THE System SHALL 发送打卡提醒通知

## Next Steps

After completing this task, the following should be implemented:

1. **Task 37.2**: Implement notification handling UI
   - Create notification list screen
   - Show notification history
   - Mark notifications as read

2. **Task 37.3**: Implement notification permission request flow
   - Add permission request to onboarding
   - Create settings screen for notification preferences
   - Allow users to customize notification types

3. **Integration with Navigation**
   - Implement navigation coordinator
   - Handle deep linking from notifications
   - Ensure proper screen transitions

4. **Backend Integration**
   - Verify backend sends correct notification payloads
   - Test all notification types end-to-end
   - Monitor notification delivery rates

## References

- [Apple Push Notification Service Documentation](https://developer.apple.com/documentation/usernotifications)
- [Firebase Cloud Messaging for iOS](https://firebase.google.com/docs/cloud-messaging/ios/client)
- [UserNotifications Framework](https://developer.apple.com/documentation/usernotifications)
- [Background Execution](https://developer.apple.com/documentation/uikit/app_and_environment/scenes/preparing_your_ui_to_run_in_the_background)
