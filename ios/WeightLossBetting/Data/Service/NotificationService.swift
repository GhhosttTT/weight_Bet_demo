import Foundation
import UserNotifications
import UIKit

class NotificationService {
    static let shared = NotificationService()
    
    private let notificationRepository = NotificationRepository()
    private var deviceToken: String?
    
    private init() {}
    
    // MARK: - Device Token Management
    
    func setDeviceToken(_ token: Data) {
        let tokenString = token.map { String(format: "%02.2hhx", $0) }.joined()
        self.deviceToken = tokenString
        
        // Register with backend
        Task {
            await registerDeviceTokenWithBackend(tokenString)
        }
    }
    
    private func registerDeviceTokenWithBackend(_ token: String) async {
        let result = await notificationRepository.registerDeviceToken(token: token)
        
        switch result {
        case .success:
            print("✅ Device token registered successfully with backend")
        case .failure(let error):
            print("❌ Failed to register device token: \(error.localizedDescription)")
            // Store token locally to retry later
            UserDefaults.standard.set(token, forKey: "pending_device_token")
        case .loading:
            break
        }
    }
    
    func retryPendingTokenRegistration() async {
        guard let pendingToken = UserDefaults.standard.string(forKey: "pending_device_token") else {
            return
        }
        
        await registerDeviceTokenWithBackend(pendingToken)
        
        // Clear pending token after successful registration
        UserDefaults.standard.removeObject(forKey: "pending_device_token")
    }
    
    // MARK: - Notification Permissions
    
    func requestNotificationPermissions(completion: @escaping (Bool) -> Void) {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { granted, error in
            if let error = error {
                print("❌ Notification permission error: \(error.localizedDescription)")
                completion(false)
                return
            }
            
            if granted {
                print("✅ Notification permission granted")
                DispatchQueue.main.async {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            } else {
                print("⚠️ Notification permission denied")
            }
            
            completion(granted)
        }
    }
    
    func checkNotificationPermissionStatus(completion: @escaping (UNAuthorizationStatus) -> Void) {
        UNUserNotificationCenter.current().getNotificationSettings { settings in
            completion(settings.authorizationStatus)
        }
    }
    
    // MARK: - Notification Handling
    
    func handleNotification(_ notification: UNNotification) {
        let userInfo = notification.request.content.userInfo
        
        guard let type = userInfo["type"] as? String else {
            print("⚠️ Notification missing type")
            return
        }
        
        let relatedId = userInfo["relatedId"] as? String
        
        print("📬 Received notification - Type: \(type), RelatedId: \(relatedId ?? "none")")
        
        // Post notification for app to handle
        NotificationCenter.default.post(
            name: .didReceiveRemoteNotification,
            object: nil,
            userInfo: [
                "type": type,
                "relatedId": relatedId as Any,
                "notification": notification
            ]
        )
    }
    
    func handleNotificationResponse(_ response: UNNotificationResponse) {
        let userInfo = response.notification.request.content.userInfo
        
        guard let type = userInfo["type"] as? String else {
            print("⚠️ Notification response missing type")
            return
        }
        
        let relatedId = userInfo["relatedId"] as? String
        
        print("👆 User tapped notification - Type: \(type), RelatedId: \(relatedId ?? "none")")
        
        // Post notification for app to handle navigation
        NotificationCenter.default.post(
            name: .didTapNotification,
            object: nil,
            userInfo: [
                "type": type,
                "relatedId": relatedId as Any
            ]
        )
        
        // Navigate based on notification type
        navigateToScreen(type: type, relatedId: relatedId)
    }
    
    private func navigateToScreen(type: String, relatedId: String?) {
        // Navigation will be handled by NotificationNavigationCoordinator
        // This method is kept for logging purposes
        switch type {
        case "invite":
            if let planId = relatedId {
                print("📍 Navigate to plan invitation: \(planId)")
            }
        case "plan_active":
            if let planId = relatedId {
                print("📍 Navigate to active plan: \(planId)")
            }
        case "settlement":
            if let settlementId = relatedId {
                print("📍 Navigate to settlement: \(settlementId)")
            }
        case "check_in_reminder":
            if let planId = relatedId {
                print("📍 Navigate to check-in for plan: \(planId)")
            }
        default:
            print("📍 Unknown notification type: \(type)")
        }
    }
    
    // MARK: - Badge Management
    
    func updateBadgeCount(_ count: Int) {
        DispatchQueue.main.async {
            UIApplication.shared.applicationIconBadgeNumber = count
        }
    }
    
    func clearBadge() {
        updateBadgeCount(0)
    }
}

// MARK: - Notification Names

extension Notification.Name {
    static let didReceiveRemoteNotification = Notification.Name("didReceiveRemoteNotification")
    static let didTapNotification = Notification.Name("didTapNotification")
}
