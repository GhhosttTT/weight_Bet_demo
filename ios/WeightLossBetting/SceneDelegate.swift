import UIKit
import UserNotifications

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = (scene as? UIWindowScene) else { return }
        
        window = UIWindow(windowScene: windowScene)
        
        // Check if user is already logged in
        let authRepository = AuthRepository.shared
        let rootViewController: UIViewController
        
        if authRepository.isLoggedIn() {
            // User is logged in, show main screen
            rootViewController = MainTabBarController()
        } else {
            // User is not logged in, show login screen
            let loginVC = LoginViewController()
            rootViewController = UINavigationController(rootViewController: loginVC)
        }
        
        window?.rootViewController = rootViewController
        window?.makeKeyAndVisible()
        
        // Setup notification navigation coordinator
        NotificationNavigationCoordinator.shared.setWindow(window)
        
        // Listen for session expiration
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleSessionExpired),
            name: NSNotification.Name("UserSessionExpired"),
            object: nil
        )
        
        // Handle notification if app was launched from notification
        if let notificationResponse = connectionOptions.notificationResponse {
            handleNotificationResponse(notificationResponse)
        }
    }
    
    @objc private func handleSessionExpired() {
        DispatchQueue.main.async { [weak self] in
            let loginVC = LoginViewController()
            let navController = UINavigationController(rootViewController: loginVC)
            self?.window?.rootViewController = navController
            
            // Show alert
            let alert = UIAlertController(
                title: "Session Expired",
                message: "Your session has expired. Please login again.",
                preferredStyle: .alert
            )
            alert.addAction(UIAlertAction(title: "OK", style: .default))
            navController.present(alert, animated: true)
        }
    }
    
    private func handleNotificationResponse(_ response: UNNotificationResponse) {
        let userInfo = response.notification.request.content.userInfo
        
        guard let type = userInfo["type"] as? String else {
            return
        }
        
        let relatedId = userInfo["relatedId"] as? String
        
        print("🚀 Handling notification response from launch - Type: \(type), ID: \(relatedId ?? "none")")
        
        // Delay to ensure UI is ready
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            NotificationCenter.default.post(
                name: .didTapNotification,
                object: nil,
                userInfo: [
                    "type": type,
                    "relatedId": relatedId as Any
                ]
            )
        }
    }

    func sceneDidDisconnect(_ scene: UIScene) {
    }

    func sceneDidBecomeActive(_ scene: UIScene) {
    }

    func sceneWillResignActive(_ scene: UIScene) {
    }

    func sceneWillEnterForeground(_ scene: UIScene) {
        // Called as the scene transitions from the background to the foreground.
        // Check pending actions if user is logged in
        if AuthRepository.shared.isLoggedIn() {
            PendingActionsService.shared.checkAndHandlePendingActions()
        }
    }

    func sceneDidEnterBackground(_ scene: UIScene) {
        CoreDataManager.shared.saveContext()
    }
}
