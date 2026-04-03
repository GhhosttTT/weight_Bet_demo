import UIKit
import UserNotifications

class SceneDelegate: UIResponder, UIWindowSceneDelegate {

    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options connectionOptions: UIScene.ConnectionOptions) {
        guard let windowScene = (scene as? UIWindowScene) else { 
            print("❌ Failed to get window scene")
            return 
        }
        
        print("✅ Got window scene: \(windowScene)")
        window = UIWindow(windowScene: windowScene)
        window?.backgroundColor = .white
        window?.overrideUserInterfaceStyle = .unspecified
        
        // Check if user is already logged in
        let authRepository = AuthRepository.shared
        print("🎯 AuthRepository isLoggedIn(): \(authRepository.isLoggedIn())")
        print("🎯 Access Token: \(authRepository.getAccessToken() ?? "nil")")
        
        let rootViewController: UIViewController
        
        if authRepository.isLoggedIn() {
            // User is logged in, show main screen
            print("🎯 Showing MainTabBarController")
            rootViewController = MainTabBarController()
        } else {
            // User is not logged in, show login screen
            print("🎯 Showing LoginViewController")
            let loginVC = LoginViewController()
            rootViewController = UINavigationController(rootViewController: loginVC)
        }
        
        print("🎯 Setting root view controller: \(rootViewController)")
        window?.rootViewController = rootViewController
        print("🎯 Calling makeKeyAndVisible()")
        window?.makeKeyAndVisible()
        print("🎯 Window isKeyWindow: \(window?.isKeyWindow ?? false)")
        print("🎯 Window frame: \(window?.frame ?? .zero)")
        print("🎯 Root view controller view frame: \(rootViewController.view.frame)")
        print("🎯 Window visible: \(window?.isHidden ?? true)")
        
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
        
        print("✅ Scene setup completed")
    }
    
    @objc private func handleSessionExpired() {
        DispatchQueue.main.async { [weak self] in
            let loginVC = LoginViewController()
            let navController = UINavigationController(rootViewController: loginVC)
            self?.window?.rootViewController = navController
            
            // Show alert
            let alert = UIAlertController(
                title: "登录已过期",
                message: "您的登录已过期，请重新登录。",
                preferredStyle: .alert
            )
            alert.addAction(UIAlertAction(title: "确定", style: .default))
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
