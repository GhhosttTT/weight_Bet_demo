import UIKit
import UserNotifications
import IQKeyboardManagerSwift

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        print("🚀 [AppDelegate] application:didFinishLaunchingWithOptions called")
        
        // CoreData 已禁用，移除相关初始化
        // _ = CoreDataManager.shared.persistentContainer
        // Configure IQKeyboardManager
        IQKeyboardManager.shared.enable = true
        IQKeyboardManager.shared.enableAutoToolbar = true
        IQKeyboardManager.shared.shouldResignOnTouchOutside = true
        
        print("✅ [AppDelegate] IQKeyboardManager configured")
        
        // Configure APNs
        configureAPNs(application)
        
        // Retry registering any pending device token saved from previous failures
        Task {
            await NotificationService.shared.retryPendingTokenRegistration()
        }

        // Check if app was launched from notification
        if let notification = launchOptions?[.remoteNotification] as? [String: Any] {
            handleLaunchFromNotification(notification)
        }
        
        // If user already logged in at cold start, check pending actions once
        if AuthRepository.shared.isLoggedIn() {
            Task {
                PendingActionsService.shared.checkAndHandlePendingActions()
            }
        }

        print("✅ [AppDelegate] didFinishLaunchingWithOptions completed")
        return true
    }
    
    // MARK: - APNs Configuration
    
    private func configureAPNs(_ application: UIApplication) {
        // Set notification center delegate
        UNUserNotificationCenter.current().delegate = self
        
        // Don't request permissions immediately on app launch
        // Permissions will be requested after login or at appropriate times
        // This provides better user experience and context
        print("✅ APNs delegate configured")
    }
    
    private func handleLaunchFromNotification(_ userInfo: [String: Any]) {
        print("🚀 App launched from notification")
        
        // Delay handling to ensure app is fully initialized
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            NotificationCenter.default.post(
                name: .didTapNotification,
                object: nil,
                userInfo: userInfo
            )
        }
    }

    // MARK: UISceneSession Lifecycle

    func application(_ application: UIApplication, configurationForConnecting connectingSceneSession: UISceneSession, options: UIScene.ConnectionOptions) -> UISceneConfiguration {
        print("🎬 [AppDelegate] configurationForConnecting called")
        print("   - Session role: \(connectingSceneSession.role.rawValue)")
        print("   - Options: \(options)")
        let config = UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
        print("   - Created configuration: \(config)")
        return config
    }

    func application(_ application: UIApplication, didDiscardSceneSessions sceneSessions: Set<UISceneSession>) {
        print("🗑️ [AppDelegate] didDiscardSceneSessions: \(sceneSessions.count) sessions")
    }
    
    // MARK: - URL Handling

    func application(_ app: UIApplication, open url: URL, options: [UIApplication.OpenURLOptionsKey : Any] = [:]) -> Bool {
        // URL handling will be implemented as needed
        return false
    }

    // MARK: - Remote Notifications
    
    func application(_ application: UIApplication, didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data) {
        print("✅ Successfully registered for remote notifications")
        
        // Register device token with backend
        NotificationService.shared.setDeviceToken(deviceToken)
    }
    
    func application(_ application: UIApplication, didFailToRegisterForRemoteNotificationsWithError error: Error) {
        print("❌ Failed to register for remote notifications: \(error.localizedDescription)")
    }
    
    // Handle notification when app is in background
    func application(_ application: UIApplication,
                    didReceiveRemoteNotification userInfo: [AnyHashable: Any],
                    fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void) {
        print("📬 Received remote notification in background")
        
        // Handle the notification
        if let type = userInfo["type"] as? String {
            print("Notification type: \(type)")
        }
        
        completionHandler(.newData)
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension AppDelegate: UNUserNotificationCenterDelegate {
    // Handle notification when app is in foreground
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                willPresent notification: UNNotification,
                                withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void) {
        print("📬 Received notification while app is in foreground")
        
        // Handle the notification
        NotificationService.shared.handleNotification(notification)
        
        // Show notification banner and play sound even when app is in foreground
        if #available(iOS 14.0, *) {
            completionHandler([.banner, .sound, .badge])
        } else {
            completionHandler([.alert, .sound, .badge])
        }
    }
    
    // Handle notification tap
    func userNotificationCenter(_ center: UNUserNotificationCenter,
                                didReceive response: UNNotificationResponse,
                                withCompletionHandler completionHandler: @escaping () -> Void) {
        print("👆 User tapped on notification")
        
        // Handle notification response
        NotificationService.shared.handleNotificationResponse(response)
        
        completionHandler()
    }
}
