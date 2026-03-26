# iOS Notification Permission Implementation Guide

## Overview

This guide explains how notification permissions are implemented in the Weight Loss Betting iOS app and how to use them effectively.

## Architecture

### Components

1. **NotificationService** - Core notification service
   - Manages permission requests
   - Handles device token registration
   - Processes incoming notifications

2. **NotificationPermissionHelper** - UI helper for permissions
   - Shows permission explanation dialogs
   - Guides users to iOS Settings
   - Provides reusable permission UI

3. **View Controllers** - Integration points
   - LoginViewController: Requests after login
   - RegisterViewController: Requests after registration
   - ProfileViewController: Manages permissions anytime

## Permission Request Flow

### When Permissions Are Requested

1. **After Login** (LoginViewController)
   ```swift
   private func navigateToMainScreen() {
       // ... navigation code ...
       UIView.transition(with: window, duration: 0.3, options: .transitionCrossDissolve, animations: nil) {
           self.requestNotificationPermissionsIfNeeded()
       }
   }
   ```

2. **After Registration** (RegisterViewController)
   ```swift
   private func navigateToMainScreen() {
       // ... navigation code ...
       UIView.transition(with: window, duration: 0.3, options: .transitionCrossDissolve, animations: nil) {
           self.requestNotificationPermissionsIfNeeded()
       }
   }
   ```

3. **From Settings** (ProfileViewController)
   ```swift
   @objc private func notificationButtonTapped() {
       NotificationService.shared.checkNotificationPermissionStatus { status in
           // Handle based on current status
       }
   }
   ```

### Permission States

| State | Description | Action |
|-------|-------------|--------|
| `.notDetermined` | User hasn't been asked yet | Show explanation, then request |
| `.denied` | User previously denied | Guide to iOS Settings |
| `.authorized` | User granted permissions | Show status, allow Settings access |
| `.provisional` | iOS 12+ provisional auth | Treat as authorized |
| `.ephemeral` | iOS 14+ ephemeral auth | Treat as authorized |

## Usage Examples

### Check Permission Status

```swift
NotificationService.shared.checkNotificationPermissionStatus { status in
    DispatchQueue.main.async {
        switch status {
        case .notDetermined:
            print("Not asked yet")
        case .denied:
            print("User denied")
        case .authorized:
            print("User granted")
        default:
            break
        }
    }
}
```

### Request Permissions with Explanation

```swift
NotificationPermissionHelper.showPermissionExplanation(from: self) {
    NotificationService.shared.requestNotificationPermissions { granted in
        if granted {
            print("✅ Permissions granted")
        } else {
            print("❌ Permissions denied")
        }
    }
}
```

### Guide User to Settings

```swift
NotificationPermissionHelper.requestPermissionIfNeeded(from: self) { granted in
    // This will show Settings alert if permissions are denied
}
```

## User Experience

### First-Time Flow

1. User logs in or registers
2. App navigates to main screen
3. Explanation dialog appears:
   ```
   Title: "Stay Updated"
   Message: "Enable notifications to receive:
   • Plan invitations from friends
   • Daily check-in reminders
   • Settlement results
   • Encouragement from other users"
   
   Buttons: [Not Now] [Enable]
   ```
4. If user taps "Enable":
   - iOS permission dialog appears
   - User grants or denies
5. If user taps "Not Now":
   - Dialog dismisses
   - Can enable later from Profile

### Re-Enabling Flow

1. User opens Profile tab
2. Taps "Notification Settings" button
3. Sees current status:
   - **If denied**: Alert with "Settings" button
   - **If enabled**: Status message with Settings option
   - **If not set**: Explanation dialog

### Settings Alert (When Denied)

```
Title: "Enable Notifications"
Message: "To receive important updates about your betting plans, 
check-in reminders, and settlement results, please enable 
notifications in Settings."

Buttons: [Cancel] [Settings]
```

## Best Practices

### DO ✅

1. **Request in Context**
   - After login/registration
   - When user performs action requiring notifications
   - With clear explanation of benefits

2. **Handle Denial Gracefully**
   - Don't repeatedly prompt
   - Provide Settings navigation
   - App works without permissions

3. **Provide Value Proposition**
   - Explain specific benefits
   - Use clear, friendly language
   - Show what user will receive

4. **Allow Re-Enablement**
   - Settings button in Profile
   - Clear status indication
   - Easy path to iOS Settings

### DON'T ❌

1. **Don't Request on Launch**
   - No context for user
   - High denial rate
   - Poor user experience

2. **Don't Repeatedly Prompt**
   - Respect user's choice
   - Don't guilt-trip
   - Don't block functionality

3. **Don't Assume Permissions**
   - Always check status
   - Handle all states
   - Graceful degradation

4. **Don't Hide Settings**
   - Make it easy to change
   - Provide clear navigation
   - Show current status

## Testing

### Manual Test Cases

1. **New User Registration**
   ```
   Steps:
   1. Register new account
   2. Complete registration
   3. Observe permission dialog
   4. Tap "Enable"
   5. Grant iOS permission
   
   Expected: Permissions granted, notifications work
   ```

2. **Permission Denial**
   ```
   Steps:
   1. Login/Register
   2. Tap "Not Now" on explanation
   3. Navigate to Profile
   4. Tap "Notification Settings"
   5. Observe Settings alert
   
   Expected: Clear path to enable in Settings
   ```

3. **Already Granted**
   ```
   Steps:
   1. Login with permissions already granted
   2. Navigate to Profile
   3. Tap "Notification Settings"
   4. Observe status message
   
   Expected: Shows enabled status, Settings option
   ```

### Automated Tests

```swift
func testPermissionRequestAfterLogin() {
    // Given: User is on login screen
    // When: User logs in successfully
    // Then: Permission explanation should appear
}

func testPermissionDenialHandling() {
    // Given: User denied permissions
    // When: User taps Notification Settings
    // Then: Settings alert should appear
}

func testPermissionStatusDisplay() {
    // Given: Permissions are granted
    // When: User taps Notification Settings
    // Then: Status message should appear
}
```

## Troubleshooting

### Permission Dialog Not Appearing

**Possible Causes:**
1. Permissions already determined
2. App doesn't have notification capability
3. iOS Settings blocking

**Solutions:**
1. Check permission status first
2. Verify Info.plist has notification keys
3. Reset iOS simulator/device

### Settings Button Not Working

**Possible Causes:**
1. Invalid Settings URL
2. iOS version compatibility
3. App not in Settings

**Solutions:**
1. Verify `UIApplication.openSettingsURLString`
2. Test on iOS 13+
3. Check app is installed properly

### Permissions Not Persisting

**Possible Causes:**
1. App reinstalled
2. iOS Settings reset
3. Simulator reset

**Solutions:**
1. Permissions reset on reinstall (expected)
2. Check iOS Settings > Notifications
3. Test on physical device

## Integration Checklist

- [x] NotificationService configured
- [x] NotificationPermissionHelper implemented
- [x] LoginViewController integrated
- [x] RegisterViewController integrated
- [x] ProfileViewController integrated
- [x] AppDelegate configured
- [x] Info.plist has notification keys
- [x] Capabilities enabled in Xcode
- [x] APNs certificates configured
- [x] Backend device token registration

## Additional Resources

### Apple Documentation
- [Asking Permission to Use Notifications](https://developer.apple.com/documentation/usernotifications/asking_permission_to_use_notifications)
- [UNUserNotificationCenter](https://developer.apple.com/documentation/usernotifications/unusernotificationcenter)
- [Human Interface Guidelines - Notifications](https://developer.apple.com/design/human-interface-guidelines/notifications)

### Related Files
- `ios/WeightLossBetting/AppDelegate.swift`
- `ios/WeightLossBetting/Data/Service/NotificationService.swift`
- `ios/WeightLossBetting/UI/Common/NotificationPermissionHelper.swift`
- `ios/TASK_37.1_SUMMARY.md` - APNs Integration
- `ios/TASK_37.2_SUMMARY.md` - Notification Handling
- `ios/TASK_37.3_SUMMARY.md` - Permission Requests

## Summary

The notification permission implementation provides:

✅ **Contextual Requests** - After login/registration
✅ **Clear Value Proposition** - Explanation of benefits
✅ **Graceful Degradation** - App works without permissions
✅ **Easy Re-Enablement** - Settings button in Profile
✅ **iOS Best Practices** - Follows Apple guidelines
✅ **User-Friendly** - Clear messaging and navigation

This ensures users understand the value of notifications and can easily manage their preferences while maintaining a positive user experience.
