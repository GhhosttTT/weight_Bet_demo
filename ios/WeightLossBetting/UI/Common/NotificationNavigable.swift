import UIKit

/// 协议：视图控制器如果希望处理来自推送的深度导航，实现此协议
protocol NotificationNavigable: AnyObject {
    func handleNotificationNavigation(type: String, relatedId: String?)
}

extension NotificationNavigable where Self: UIViewController {
    func handleNotificationNavigation(type: String, relatedId: String?) {
        // 默认不做任何事，具体页面按需实现
    }
}

