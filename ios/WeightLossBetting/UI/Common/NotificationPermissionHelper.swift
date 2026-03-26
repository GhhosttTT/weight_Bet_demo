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

        alert.addAction(UIAlertAction(title: "Not now", style: .cancel) { _ in
            completion()
        })

        alert.addAction(UIAlertAction(title: "Allow", style: .default) { _ in
            completion()
        })

        DispatchQueue.main.async {
            viewController.present(alert, animated: true, completion: nil)
        }
    }
}

