import UIKit

class EncouragementHelper {
    
    static let shared = EncouragementHelper()
    private let repository = SocialRepository()
    
    private init() {}
    
    /// Send encouragement to a user
    /// - Parameters:
    ///   - userId: The user ID to encourage
    ///   - from: The view controller to present alerts from
    func sendEncouragement(to userId: String, from viewController: UIViewController) {
        // Show loading indicator
        let loadingAlert = UIAlertController(title: nil, message: "发送中...", preferredStyle: .alert)
        let loadingIndicator = UIActivityIndicatorView(style: .medium)
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false
        loadingIndicator.startAnimating()
        loadingAlert.view.addSubview(loadingIndicator)
        
        NSLayoutConstraint.activate([
            loadingIndicator.centerXAnchor.constraint(equalTo: loadingAlert.view.centerXAnchor),
            loadingIndicator.topAnchor.constraint(equalTo: loadingAlert.view.topAnchor, constant: 50)
        ])
        
        viewController.present(loadingAlert, animated: true)
        
        repository.sendEncouragement(userId: userId) { result in
            DispatchQueue.main.async {
                loadingAlert.dismiss(animated: true) {
                    switch result {
                    case .success:
                        self.showSuccessAnimation(in: viewController)
                    case .failure(let error):
                        self.showError(error.localizedDescription, in: viewController)
                    }
                }
            }
        }
    }
    
    /// Create an encouragement button
    /// - Parameters:
    ///   - userId: The user ID to encourage
    ///   - viewController: The view controller that will present alerts
    /// - Returns: A configured UIButton
    func createEncouragementButton(for userId: String, in viewController: UIViewController) -> UIButton {
        let button = UIButton(type: .system)
        button.setTitle("👍 鼓励", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 14)
        button.backgroundColor = .systemBlue.withAlphaComponent(0.1)
        button.setTitleColor(.systemBlue, for: .normal)
        button.layer.cornerRadius = 8
        button.contentEdgeInsets = UIEdgeInsets(top: 8, left: 16, bottom: 8, right: 16)
        
        button.addAction(UIAction { [weak self] _ in
            self?.sendEncouragement(to: userId, from: viewController)
        }, for: .touchUpInside)
        
        return button
    }
    
    // MARK: - Private Methods
    
    private func showSuccessAnimation(in viewController: UIViewController) {
        // Create success view
        let successView = UIView()
        successView.backgroundColor = UIColor.black.withAlphaComponent(0.7)
        successView.layer.cornerRadius = 12
        successView.translatesAutoresizingMaskIntoConstraints = false
        
        let emojiLabel = UILabel()
        emojiLabel.text = "👍"
        emojiLabel.font = .systemFont(ofSize: 60)
        emojiLabel.textAlignment = .center
        emojiLabel.translatesAutoresizingMaskIntoConstraints = false
        
        let messageLabel = UILabel()
        messageLabel.text = "鼓励已发送"
        messageLabel.font = .boldSystemFont(ofSize: 16)
        messageLabel.textColor = .white
        messageLabel.textAlignment = .center
        messageLabel.translatesAutoresizingMaskIntoConstraints = false
        
        successView.addSubview(emojiLabel)
        successView.addSubview(messageLabel)
        viewController.view.addSubview(successView)
        
        NSLayoutConstraint.activate([
            successView.centerXAnchor.constraint(equalTo: viewController.view.centerXAnchor),
            successView.centerYAnchor.constraint(equalTo: viewController.view.centerYAnchor),
            successView.widthAnchor.constraint(equalToConstant: 200),
            successView.heightAnchor.constraint(equalToConstant: 150),
            
            emojiLabel.centerXAnchor.constraint(equalTo: successView.centerXAnchor),
            emojiLabel.topAnchor.constraint(equalTo: successView.topAnchor, constant: 20),
            
            messageLabel.centerXAnchor.constraint(equalTo: successView.centerXAnchor),
            messageLabel.topAnchor.constraint(equalTo: emojiLabel.bottomAnchor, constant: 12)
        ])
        
        // Animate
        successView.alpha = 0
        successView.transform = CGAffineTransform(scaleX: 0.8, y: 0.8)
        
        UIView.animate(withDuration: 0.3, animations: {
            successView.alpha = 1
            successView.transform = .identity
        }) { _ in
            UIView.animate(withDuration: 0.3, delay: 1.0, options: [], animations: {
                successView.alpha = 0
                successView.transform = CGAffineTransform(scaleX: 1.2, y: 1.2)
            }) { _ in
                successView.removeFromSuperview()
            }
        }
    }
    
    private func showError(_ message: String, in viewController: UIViewController) {
        let alert = UIAlertController(title: "错误", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        viewController.present(alert, animated: true)
    }
}
