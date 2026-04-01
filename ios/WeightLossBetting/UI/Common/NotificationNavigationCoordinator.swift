import UIKit

final class NotificationNavigationCoordinator {
    static let shared = NotificationNavigationCoordinator()
    private init() {}

    private weak var window: UIWindow?

    func setWindow(_ window: UIWindow?) {
        self.window = window

        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleDidTapNotification(_:)),
            name: .didTapNotification,
            object: nil
        )

        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleDidReceiveRemoteNotification(_:)),
            name: .didReceiveRemoteNotification,
            object: nil
        )
    }

    @objc private func handleDidTapNotification(_ note: Notification) {
        guard let userInfo = note.userInfo as? [String: Any] else { return }
        let type = userInfo["type"] as? String
        let relatedId = userInfo["relatedId"] as? String
        navigateToScreen(type: type, relatedId: relatedId)

        // If this is an invite or double-check, also trigger pending actions check
        if let t = type, t == "invite" || t == "double_check" {
            Task {
                await PendingActionsService.shared.checkAndHandlePendingActions()
            }
        }
    }

    @objc private func handleDidReceiveRemoteNotification(_ note: Notification) {
        guard let userInfo = note.userInfo as? [String: Any] else { return }
        let type = userInfo["type"] as? String
        let relatedId = userInfo["relatedId"] as? String
        // For background/foreground receipt we may want to update badges or cache
        // Broadcast so UI can update without forcing navigation
        NotificationCenter.default.post(name: .notificationReceivedForUI, object: nil, userInfo: userInfo)
        // Do not force navigation on receipt

        // If it's an invite or double-check, schedule a pending actions check
        if let t = type, t == "invite" || t == "double_check" {
            Task {
                await PendingActionsService.shared.checkAndHandlePendingActions()
            }
        }
    }

    private func navigateToScreen(type: String?, relatedId: String?) {
        guard let type = type else { return }

        DispatchQueue.main.async { [weak self] in
            guard let self = self, let root = self.window?.rootViewController else { return }

            // If root is a TabBarController, try to select an appropriate tab
            if let tab = root as? UITabBarController {
                let index = self.tabIndex(for: type)
                if let idx = index, idx < (tab.viewControllers?.count ?? 0) {
                    tab.selectedIndex = idx
                }
            } else if let nav = root as? UINavigationController {
                // If root is a navigation controller, try to pop to root first
                nav.popToRootViewController(animated: false)
            }

            // Broadcast navigation intent so feature modules can present specific screens
            NotificationCenter.default.post(
                name: .navigateToNotificationType,
                object: nil,
                userInfo: ["type": type, "relatedId": relatedId as Any]
            )
        }
    }

    private func tabIndex(for notificationType: String) -> Int? {
        // 保守映射：如果项目实际 tab 顺序不同，模块应监听 navigateToNotificationType 并自行处理
        switch notificationType {
        case "invite":
            return 1 // 可能是 Plans / Social
        case "plan_active":
            return 1 // Plans tab
        case "check_in_reminder":
            return 2 // CheckIn tab
        case "settlement":
            return 3 // Profile / Settlement tab
        default:
            return nil
        }
    }
}

// MARK: - Additional Notification Names
extension Notification.Name {
    static let navigateToNotificationType = Notification.Name("navigateToNotificationType")
    static let notificationReceivedForUI = Notification.Name("notificationReceivedForUI")
}
