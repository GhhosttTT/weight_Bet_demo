import UIKit
import IQKeyboardManagerSwift
import Alamofire

class LoginViewController: UIViewController {
    
    // MARK: - UI Components
    
    private let logoImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFit
        imageView.translatesAutoresizingMaskIntoConstraints = false
        // Set the logo image (using SF Symbol)
        imageView.image = UIImage(systemName: "target")
        imageView.tintColor = .systemBlue
        return imageView
    }()
    
    private let appTitleLabel: UILabel = {
        let label = UILabel()
        label.text = "BetFit"
        label.font = UIFont.boldSystemFont(ofSize: 36)
        label.textAlignment = .center
        label.textColor = .label
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let appSubtitleLabel: UILabel = {
        let label = UILabel()
        label.text = "减肥对赌挑战"
        label.font = UIFont.systemFont(ofSize: 16, weight: .medium)
        label.textAlignment = .center
        label.textColor = .secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let emailTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "邮箱"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .emailAddress
        textField.autocapitalizationType = .none
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let passwordTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "密码"
        textField.borderStyle = .roundedRect
        textField.isSecureTextEntry = true
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let loginButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("登录", for: .normal)
        button.backgroundColor = .systemBlue
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 8
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let registerButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("没有账号？注册", for: .normal)
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let googleSignInButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("使用 Google 登录", for: .normal)
        button.backgroundColor = .white
        button.setTitleColor(.black, for: .normal)
        button.layer.cornerRadius = 8
        button.layer.borderWidth = 1
        button.layer.borderColor = UIColor.lightGray.cgColor
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let orLabel: UILabel = {
        let label = UILabel()
        label.text = "或者"
        label.textAlignment = .center
        label.textColor = .gray
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let activityIndicator: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .large)
        indicator.hidesWhenStopped = true
        indicator.translatesAutoresizingMaskIntoConstraints = false
        return indicator
    }()
    
    // MARK: - Properties
    
    private let viewModel = LoginViewModel()
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupActions()
        setupDebugButton()
    }
    
    private func setupDebugButton() {
        // 🔧 网络诊断功能已移除
        // 如需测试网络，请使用 curl 或直接访问后端 API
    }
    
    @objc private func showNetworkDebug() {
        // 🔧 网络诊断功能已移除
        print("ℹ️ 网络诊断功能已移除，请使用 curl 测试后端连接")
        // 示例：curl http://192.168.1.10:8000/health
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        IQKeyboardManager.shared.enable = false
    }
    
    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        IQKeyboardManager.shared.enable = true
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        view.backgroundColor = .systemBackground
        
        view.addSubview(logoImageView)
        view.addSubview(appTitleLabel)
        view.addSubview(appSubtitleLabel)
        view.addSubview(emailTextField)
        view.addSubview(passwordTextField)
        view.addSubview(loginButton)
        view.addSubview(orLabel)
        view.addSubview(googleSignInButton)
        view.addSubview(registerButton)
        view.addSubview(activityIndicator)
        
        NSLayoutConstraint.activate([
            logoImageView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 80),
            logoImageView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            logoImageView.widthAnchor.constraint(equalToConstant: 80),
            logoImageView.heightAnchor.constraint(equalToConstant: 80),
            
            appTitleLabel.topAnchor.constraint(equalTo: logoImageView.bottomAnchor, constant: 16),
            appTitleLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            
            appSubtitleLabel.topAnchor.constraint(equalTo: appTitleLabel.bottomAnchor, constant: 8),
            appSubtitleLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            
            emailTextField.topAnchor.constraint(equalTo: appSubtitleLabel.bottomAnchor, constant: 40),
            emailTextField.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 32),
            emailTextField.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -32),
            emailTextField.heightAnchor.constraint(equalToConstant: 50),
            
            passwordTextField.topAnchor.constraint(equalTo: emailTextField.bottomAnchor, constant: 16),
            passwordTextField.leadingAnchor.constraint(equalTo: emailTextField.leadingAnchor),
            passwordTextField.trailingAnchor.constraint(equalTo: emailTextField.trailingAnchor),
            passwordTextField.heightAnchor.constraint(equalToConstant: 50),
            
            loginButton.topAnchor.constraint(equalTo: passwordTextField.bottomAnchor, constant: 32),
            loginButton.leadingAnchor.constraint(equalTo: emailTextField.leadingAnchor),
            loginButton.trailingAnchor.constraint(equalTo: emailTextField.trailingAnchor),
            loginButton.heightAnchor.constraint(equalToConstant: 50),
            
            orLabel.topAnchor.constraint(equalTo: loginButton.bottomAnchor, constant: 16),
            orLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            
            googleSignInButton.topAnchor.constraint(equalTo: orLabel.bottomAnchor, constant: 16),
            googleSignInButton.leadingAnchor.constraint(equalTo: emailTextField.leadingAnchor),
            googleSignInButton.trailingAnchor.constraint(equalTo: emailTextField.trailingAnchor),
            googleSignInButton.heightAnchor.constraint(equalToConstant: 50),
            
            registerButton.topAnchor.constraint(equalTo: googleSignInButton.bottomAnchor, constant: 16),
            registerButton.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            
            activityIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    private func setupActions() {
        loginButton.addTarget(self, action: #selector(loginButtonTapped), for: .touchUpInside)
        googleSignInButton.addTarget(self, action: #selector(googleSignInButtonTapped), for: .touchUpInside)
        registerButton.addTarget(self, action: #selector(registerButtonTapped), for: .touchUpInside)
    }
    
    // MARK: - Actions
    
    @objc private func loginButtonTapped() {
        guard let email = emailTextField.text, !email.isEmpty,
              let password = passwordTextField.text, !password.isEmpty else {
            showAlert(message: "请输入邮箱和密码")
            return
        }
        
        activityIndicator.startAnimating()
        loginButton.isEnabled = false
        
        viewModel.login(email: email, password: password) { [weak self] result in
            DispatchQueue.main.async {
                self?.activityIndicator.stopAnimating()
                self?.loginButton.isEnabled = true
                
                switch result {
                case .success:
                    self?.navigateToMainScreen()
                case .failure(let error):
                    self?.showAlert(message: error.localizedDescription)
                }
            }
        }
    }
    
    @objc private func registerButtonTapped() {
        let registerVC = RegisterViewController()
        navigationController?.pushViewController(registerVC, animated: true)
    }
    
    @objc private func googleSignInButtonTapped() {
        activityIndicator.startAnimating()
        googleSignInButton.isEnabled = false
        
        viewModel.googleSignIn(presentingViewController: self) { [weak self] result in
            DispatchQueue.main.async {
                self?.activityIndicator.stopAnimating()
                self?.googleSignInButton.isEnabled = true
                
                switch result {
                case .success:
                    self?.navigateToMainScreen()
                case .failure(let error):
                    self?.showAlert(message: error.localizedDescription)
                }
            }
        }
    }
    
    // MARK: - Navigation
    
    private func navigateToMainScreen() {
        guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
              let window = windowScene.windows.first else {
            return
        }
        
        let mainTabBarController = MainTabBarController()
        
        UIView.transition(with: window, duration: 0.3, options: .transitionCrossDissolve, animations: nil) { [weak self] _ in
            // Request notification permissions after successful login
            self?.requestNotificationPermissionsIfNeeded()
        }
        
        window.rootViewController = mainTabBarController
        
        // After UI transition and permission flow, check pending actions
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            PendingActionsService.shared.checkAndHandlePendingActions()
        }
    }
    
    private func requestNotificationPermissionsIfNeeded() {
        // Check if we should show the permission request
        NotificationService.shared.checkNotificationPermissionStatus { status in
            DispatchQueue.main.async {
                switch status {
                case .notDetermined:
                    // First time - show explanation and request
                    NotificationPermissionHelper.showPermissionExplanation(from: self) {
                        NotificationService.shared.requestNotificationPermissions { granted in
                            if granted {
                                print("✅ User granted notification permissions after login")
                            } else {
                                print("⚠️ User denied notification permissions after login")
                            }
                        }
                    }
                    
                case .denied:
                    // User previously denied - don't show anything now
                    // They can enable it later from settings
                    print("ℹ️ Notification permissions previously denied")
                    
                case .authorized, .provisional, .ephemeral:
                    // Already authorized
                    print("✅ Notification permissions already granted")
                    
                @unknown default:
                    break
                }
            }
        }
    }
    
    // MARK: - Helper
    
    private func showAlert(message: String) {
        let alert = UIAlertController(title: "错误", message: message, preferredStyle: .alert)
        
        // 如果是网络错误，添加诊断选项
        if message.contains("502") || message.contains("服务器") || message.contains("连接") {
            alert.addAction(UIAlertAction(title: "运行诊断", style: .default) { [weak self] _ in
                self?.showNetworkDebug()
            })
        }
        
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }
}
