# iOS Notifications Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### 1. Enable Push Notifications in Xcode

1. Open project in Xcode
2. Select target → **Signing & Capabilities**
3. Click **+ Capability**
4. Add **Push Notifications**

### 2. Configure Apple Developer Account

**Option A: APNs Authentication Key (Recommended)**
1. Go to [Apple Developer Portal](https://developer.apple.com/account)
2. Certificates, Identifiers & Profiles → **Keys**
3. Create new key with **APNs** enabled
4. Download `.p8` file
5. Note **Key ID** and **Team ID**
6. Upload to your backend

**Option B: APNs Certificate**
1. Go to [Apple Developer Portal](https://developer.apple.com/account)
2. Certificates, Identifiers & Profiles → **Certificates**
3. Create **Apple Push Notification service SSL** certificate
4. Download and install in Keychain
5. Export as `.p12` file
6. Upload to your backend

### 3. Test on Physical Device

```bash
# 1. Connect iPhone via USB
# 2. Select device in Xcode
# 3. Build and run (Cmd+R)
# 4. Grant notification permission when prompted
# 5. Check console for: "✅ Successfully registered for remote notifications"
```

## 📱 Basic Usage

### Request Permission After Login

```swift
import UIKit

class LoginViewController: UIViewController {
    
    func handleSuccessfulLogin() {
        // Request notification permission
        NotificationPermissionHelper.requestPermissionIfNeeded(from: self) { granted in
            if granted {
                print("✅ Notifications enabled")
            }
            // Continue to main screen
            self.navigateToMainScreen()
        }
    }
}
```

### Handle Notification Taps

```swift
import UIKit

class MainViewController: UIViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Listen for notification taps
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
        
        // Navigate based on type
        switch type {
        case "invite":
            showPlanInvitation(planId: relatedId)
        case "plan_active":
            showActivePlan(planId: relatedId)
        case "settlement":
            showSettlement(settlementId: relatedId)
        case "check_in_reminder":
            showCheckIn(planId: relatedId)
        default:
            break
        }
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}
```

### Update Badge Count

```swift
// Set badge count
NotificationService.shared.updateBadgeCount(5)

// Clear badge
NotificationService.shared.clearBadge()
```

## 🧪 Testing

### Test Local Notification (Works on Simulator)

```swift
import UserNotifications

func sendTestNotification() {
    let content = UNMutableNotificationContent()
    content.title = "Test Notification"
    content.body = "This is a test notification"
    content.sound = .default
    content.badge = 1
    content.userInfo = [
        "type": "invite",
        "relatedId": "test_plan_123"
    ]
    
    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
    let request = UNNotificationRequest(
        identifier: UUID().uuidString,
        content: content,
        trigger: trigger
    )
    
    UNUserNotificationCenter.current().add(request) { error in
        if let error = error {
            print("Error: \(error)")
        } else {
            print("Test notification scheduled")
        }
    }
}
```

### Test Remote Notification (Requires Physical Device)

1. **Get Device Token**
   - Run app on device
   - Check Xcode console for device token
   - Copy the hex string

2. **Send Test via Backend**
   ```bash
   curl -X POST https://your-backend.com/api/notifications/send \
     -H "Content-Type: application/json" \
     -d '{
       "device_token": "YOUR_DEVICE_TOKEN",
       "title": "Test Notification",
       "body": "Testing APNs",
       "type": "invite",
       "relatedId": "test_123"
     }'
   ```

3. **Or Use Firebase Console**
   - Go to Firebase Console → Cloud Messaging
   - Click "Send your first message"
   - Enter title and body
   - Select iOS app
   - Add custom data: `type`, `relatedId`
   - Send to device token

## 🔍 Debugging

### Check Permission Status

```swift
NotificationService.shared.checkNotificationPermissionStatus { status in
    switch status {
    case .authorized:
        print("✅ Authorized")
    case .denied:
        print("❌ Denied")
    case .notDetermined:
        print("⚠️ Not requested yet")
    case .provisional:
        print("⚠️ Provisional")
    case .ephemeral:
        print("⚠️ Ephemeral")
    @unknown default:
        print("❓ Unknown")
    }
}
```

### Common Issues

**Device Token Not Received**
```
❌ Problem: didRegisterForRemoteNotificationsWithDeviceToken not called
✅ Solution: 
   1. Test on physical device (not simulator)
   2. Check Push Notifications capability is enabled
   3. Verify valid provisioning profile
   4. Check internet connection
```

**Notifications Not Appearing**
```
❌ Problem: Notifications sent but not displayed
✅ Solution:
   1. Check Settings → App → Notifications
   2. Verify device token registered with backend
   3. Check notification payload format
   4. Verify APNs certificate/key is valid
```

**Backend Registration Fails**
```
❌ Problem: "Failed to register device token" in console
✅ Solution:
   1. Check network connectivity
   2. Verify API endpoint is correct
   3. Check authentication token
   4. Token will retry automatically
```

## 📋 Notification Types

| Type | Title Example | Body Example | Action |
|------|---------------|--------------|--------|
| `invite` | "New Plan Invitation" | "John invited you to join..." | Open plan details |
| `plan_active` | "Plan Started!" | "Your challenge with John..." | Open active plan |
| `settlement` | "Challenge Complete" | "You won $100!" | Open settlement |
| `check_in_reminder` | "Time to Check In" | "Don't forget to log..." | Open check-in |

## 🔐 Backend Payload Format

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

## 📚 Additional Resources

- **Full Documentation**: See `APNS_INTEGRATION_GUIDE.md`
- **Implementation Summary**: See `TASK_37.1_SUMMARY.md`
- **Apple Docs**: [UserNotifications Framework](https://developer.apple.com/documentation/usernotifications)
- **Firebase Docs**: [FCM for iOS](https://firebase.google.com/docs/cloud-messaging/ios/client)

## 🆘 Need Help?

1. Check `APNS_INTEGRATION_GUIDE.md` for detailed troubleshooting
2. Review console logs for error messages
3. Verify all setup steps completed
4. Test with local notifications first
5. Ensure physical device for APNs testing

## ✅ Checklist

Before deploying to production:

- [ ] Push Notifications capability enabled
- [ ] APNs certificate/key configured
- [ ] Device token registration tested
- [ ] All notification types tested
- [ ] Permission flows tested
- [ ] Navigation from notifications works
- [ ] Badge updates work
- [ ] Error handling tested
- [ ] Backend integration verified
- [ ] Production APNs certificate uploaded

---

**Quick Links:**
- [Apple Developer Portal](https://developer.apple.com/account)
- [Firebase Console](https://console.firebase.google.com)
- [APNs Documentation](https://developer.apple.com/documentation/usernotifications)
