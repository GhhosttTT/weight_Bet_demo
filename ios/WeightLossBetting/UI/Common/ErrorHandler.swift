import UIKit

/// Centralized error handling and display
class ErrorHandler {
    
    static let shared = ErrorHandler()
    
    private init() {}
    
    // MARK: - Error Display
    
    /// Show an error alert
    func showError(_ error: Error, in viewController: UIViewController, completion: (() -> Void)? = nil) {
        let message = errorMessage(for: error)
        showAlert(title: "错误", message: message, in: viewController, completion: completion)
    }
    
    /// Show a custom error message
    func showError(message: String, in viewController: UIViewController, completion: (() -> Void)? = nil) {
        showAlert(title: "错误", message: message, in: viewController, completion: completion)
    }
    
    /// Show a success message
    func showSuccess(message: String, in viewController: UIViewController, completion: (() -> Void)? = nil) {
        showAlert(title: "成功", message: message, in: viewController, completion: completion)
    }
    
    /// Show a warning message
    func showWarning(message: String, in viewController: UIViewController, completion: (() -> Void)? = nil) {
        showAlert(title: "提示", message: message, in: viewController, completion: completion)
    }
    
    /// Show a confirmation dialog
    func showConfirmation(
        title: String,
        message: String,
        confirmTitle: String = "确定",
        cancelTitle: String = "取消",
        in viewController: UIViewController,
        onConfirm: @escaping () -> Void
    ) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        
        alert.addAction(UIAlertAction(title: cancelTitle, style: .cancel))
        alert.addAction(UIAlertAction(title: confirmTitle, style: .default) { _ in
            onConfirm()
        })
        
        viewController.present(alert, animated: true)
    }
    
    // MARK: - Network Error Handling
    
    /// Show network error with retry option
    func showNetworkError(
        in viewController: UIViewController,
        onRetry: @escaping () -> Void
    ) {
        let alert = UIAlertController(
            title: "网络错误",
            message: "请检查网络连接后重试",
            preferredStyle: .alert
        )
        
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        alert.addAction(UIAlertAction(title: "重试", style: .default) { _ in
            onRetry()
        })
        
        viewController.present(alert, animated: true)
    }
    
    /// Show timeout error
    func showTimeoutError(in viewController: UIViewController, onRetry: @escaping () -> Void) {
        let alert = UIAlertController(
            title: "请求超时",
            message: "服务器响应超时,请稍后重试",
            preferredStyle: .alert
        )
        
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        alert.addAction(UIAlertAction(title: "重试", style: .default) { _ in
            onRetry()
        })
        
        viewController.present(alert, animated: true)
    }
    
    // MARK: - Private Methods
    
    private func showAlert(
        title: String,
        message: String,
        in viewController: UIViewController,
        completion: (() -> Void)? = nil
    ) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default) { _ in
            completion?()
        })
        viewController.present(alert, animated: true)
    }
    
    private func errorMessage(for error: Error) -> String {
        // Check for network errors
        let nsError = error as NSError
        
        switch nsError.code {
        case NSURLErrorNotConnectedToInternet:
            return "无法连接到网络,请检查网络设置"
        case NSURLErrorTimedOut:
            return "请求超时,请稍后重试"
        case NSURLErrorCannotFindHost, NSURLErrorCannotConnectToHost:
            return "无法连接到服务器"
        case NSURLErrorNetworkConnectionLost:
            return "网络连接已断开"
        default:
            break
        }
        
        // Check for HTTP errors
        if let httpError = error as? HTTPError {
            switch httpError {
            case .unauthorized:
                return "登录已过期,请重新登录"
            case .forbidden:
                return "没有权限执行此操作"
            case .notFound:
                return "请求的资源不存在"
            case .serverError:
                return "服务器错误,请稍后重试"
            case .unknown(let message):
                return message
            }
        }
        
        // Default error message
        return error.localizedDescription
    }
}

// MARK: - HTTPError

enum HTTPError: Error {
    case unauthorized
    case forbidden
    case notFound
    case serverError
    case unknown(String)
}

// MARK: - UIViewController Extension

extension UIViewController {
    
    /// Show an error alert
    func showError(_ error: Error, completion: (() -> Void)? = nil) {
        ErrorHandler.shared.showError(error, in: self, completion: completion)
    }
    
    /// Show a custom error message
    func showError(message: String, completion: (() -> Void)? = nil) {
        ErrorHandler.shared.showError(message: message, in: self, completion: completion)
    }
    
    /// Show a success message
    func showSuccess(message: String, completion: (() -> Void)? = nil) {
        ErrorHandler.shared.showSuccess(message: message, in: self, completion: completion)
    }
    
    /// Show a warning message
    func showWarning(message: String, completion: (() -> Void)? = nil) {
        ErrorHandler.shared.showWarning(message: message, in: self, completion: completion)
    }
    
    /// Show a confirmation dialog
    func showConfirmation(
        title: String,
        message: String,
        confirmTitle: String = "确定",
        cancelTitle: String = "取消",
        onConfirm: @escaping () -> Void
    ) {
        ErrorHandler.shared.showConfirmation(
            title: title,
            message: message,
            confirmTitle: confirmTitle,
            cancelTitle: cancelTitle,
            in: self,
            onConfirm: onConfirm
        )
    }
    
    /// Show network error with retry option
    func showNetworkError(onRetry: @escaping () -> Void) {
        ErrorHandler.shared.showNetworkError(in: self, onRetry: onRetry)
    }
    
    /// Show timeout error
    func showTimeoutError(onRetry: @escaping () -> Void) {
        ErrorHandler.shared.showTimeoutError(in: self, onRetry: onRetry)
    }
}
