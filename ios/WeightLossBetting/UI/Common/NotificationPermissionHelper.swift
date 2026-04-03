import UIKit
import UserNotifications

final class NotificationPermissionHelper {
    private init() {}

    /// Show a short explanation before requesting notification permission.
    /// The UI is simple: an alert with explanation and "Allow" / "Not now" actions.
    static func showPermissionExplanation(from viewController: UIViewController, completion: @escaping () -> Void) {
        let alert = UIAlertController(
            title: "允许通知",
            message: "启用通知可以收到打卡提醒、计划更新和重要消息。我们只会在必要时发送通知。是否允许？",
            preferredStyle: .alert
        )

        alert.addAction(UIAlertAction(title: "暂时不", style: .cancel) { _ in
            completion()
        })

        alert.addAction(UIAlertAction(title: "允许", style: .default) { _ in
            completion()
        })

        DispatchQueue.main.async {
            viewController.present(alert, animated: true, completion: nil)
        }
    }
    
    /// Request notification permission if needed.
    static func requestPermissionIfNeeded(from viewController: UIViewController, completion: @escaping (Bool) -> Void) {
        // Check notification permission status
        UNUserNotificationCenter.current().getNotificationSettings { settings in
            switch settings.authorizationStatus {
            case .notDetermined:
                // Request permission
                NotificationService.shared.requestNotificationPermissions { granted in
                    completion(granted)
                }
            case .denied:
                // User previously denied - guide them to settings
                let alert = UIAlertController(
                    title: "通知已禁用",
                    message: "您已禁用通知功能。如需启用通知，请前往 iOS 设置 > 减重打赌 > 通知。",
                    preferredStyle: .alert
                )
                alert.addAction(UIAlertAction(title: "取消", style: .cancel) { _ in
                    completion(false)
                })
                alert.addAction(UIAlertAction(title: "打开设置", style: .default) { _ in
                    if let settingsUrl = URL(string: UIApplication.openSettingsURLString) {
                        UIApplication.shared.open(settingsUrl)
                    }
                    completion(false)
                })
                DispatchQueue.main.async {
                    viewController.present(alert, animated: true)
                }
            case .authorized, .provisional, .ephemeral:
                // Already authorized
                completion(true)
            @unknown default:
                completion(false)
            }
        }
    }
}

