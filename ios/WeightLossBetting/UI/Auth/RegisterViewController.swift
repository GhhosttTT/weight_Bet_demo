import UIKit

class RegisterViewController: UIViewController {
    
    // MARK: - UI Components
    
    private let emailTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Email"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .emailAddress
        textField.autocapitalizationType = .none
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let nicknameTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Nickname"
        textField.borderStyle = .roundedRect
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let passwordTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Password"
        textField.borderStyle = .roundedRect
        textField.isSecureTextEntry = true
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let confirmPasswordTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Confirm Password"
        textField.borderStyle = .roundedRect
        textField.isSecureTextEntry = true
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let genderSegmentedControl: UISegmentedControl = {
        let items = ["男", "女"]
        let segmentedControl = UISegmentedControl(items: items)
        segmentedControl.selectedSegmentIndex = 0
        segmentedControl.translatesAutoresizingMaskIntoConstraints = false
        return segmentedControl
    }()
    
    private let heightTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "身高 (cm)"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .decimalPad
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let weightTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "当前体重 (kg)"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .decimalPad
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let ageTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "年龄"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .numberPad
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let registerButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Register", for: .normal)
        button.backgroundColor = .systemBlue
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 8
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let activityIndicator: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .large)
        indicator.hidesWhenStopped = true
        indicator.translatesAutoresizingMaskIntoConstraints = false
        return indicator
    }()
    
    // MARK: - Properties
    
    private let viewModel = RegisterViewModel()
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupActions()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        title = "Register"
        view.backgroundColor = .systemBackground
        
        view.addSubview(emailTextField)
        view.addSubview(nicknameTextField)
        view.addSubview(passwordTextField)
        view.addSubview(confirmPasswordTextField)
        view.addSubview(genderSegmentedControl)
        view.addSubview(heightTextField)
        view.addSubview(weightTextField)
        view.addSubview(ageTextField)
        view.addSubview(registerButton)
        view.addSubview(activityIndicator)
        
        NSLayoutConstraint.activate([
            emailTextField.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 60),
            emailTextField.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 32),
            emailTextField.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -32),
            emailTextField.heightAnchor.constraint(equalToConstant: 50),
            
            nicknameTextField.topAnchor.constraint(equalTo: emailTextField.bottomAnchor, constant: 16),
            nicknameTextField.leadingAnchor.constraint(equalTo: emailTextField.leadingAnchor),
            nicknameTextField.trailingAnchor.constraint(equalTo: emailTextField.trailingAnchor),
            nicknameTextField.heightAnchor.constraint(equalToConstant: 50),
            
            passwordTextField.topAnchor.constraint(equalTo: nicknameTextField.bottomAnchor, constant: 16),
            passwordTextField.leadingAnchor.constraint(equalTo: emailTextField.leadingAnchor),
            passwordTextField.trailingAnchor.constraint(equalTo: emailTextField.trailingAnchor),
            passwordTextField.heightAnchor.constraint(equalToConstant: 50),
            
            confirmPasswordTextField.topAnchor.constraint(equalTo: passwordTextField.bottomAnchor, constant: 16),
            confirmPasswordTextField.leadingAnchor.constraint(equalTo: emailTextField.leadingAnchor),
            confirmPasswordTextField.trailingAnchor.constraint(equalTo: emailTextField.trailingAnchor),
            confirmPasswordTextField.heightAnchor.constraint(equalToConstant: 50),
            
            genderSegmentedControl.topAnchor.constraint(equalTo: confirmPasswordTextField.bottomAnchor, constant: 16),
            genderSegmentedControl.leadingAnchor.constraint(equalTo: emailTextField.leadingAnchor),
            genderSegmentedControl.trailingAnchor.constraint(equalTo: emailTextField.trailingAnchor),
            genderSegmentedControl.heightAnchor.constraint(equalToConstant: 44),
            
            heightTextField.topAnchor.constraint(equalTo: genderSegmentedControl.bottomAnchor, constant: 16),
            heightTextField.leadingAnchor.constraint(equalTo: emailTextField.leadingAnchor),
            heightTextField.trailingAnchor.constraint(equalTo: emailTextField.trailingAnchor),
            heightTextField.heightAnchor.constraint(equalToConstant: 50),
            
            weightTextField.topAnchor.constraint(equalTo: heightTextField.bottomAnchor, constant: 16),
            weightTextField.leadingAnchor.constraint(equalTo: emailTextField.leadingAnchor),
            weightTextField.trailingAnchor.constraint(equalTo: emailTextField.trailingAnchor),
            weightTextField.heightAnchor.constraint(equalToConstant: 50),
            
            ageTextField.topAnchor.constraint(equalTo: weightTextField.bottomAnchor, constant: 16),
            ageTextField.leadingAnchor.constraint(equalTo: emailTextField.leadingAnchor),
            ageTextField.trailingAnchor.constraint(equalTo: emailTextField.trailingAnchor),
            ageTextField.heightAnchor.constraint(equalToConstant: 50),
            
            registerButton.topAnchor.constraint(equalTo: ageTextField.bottomAnchor, constant: 32),
            registerButton.leadingAnchor.constraint(equalTo: emailTextField.leadingAnchor),
            registerButton.trailingAnchor.constraint(equalTo: emailTextField.trailingAnchor),
            registerButton.heightAnchor.constraint(equalToConstant: 50),
            
            activityIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    private func setupActions() {
        registerButton.addTarget(self, action: #selector(registerButtonTapped), for: .touchUpInside)
    }
    
    // MARK: - Actions
    
    @objc private func registerButtonTapped() {
        guard let email = emailTextField.text, !email.isEmpty,
              let nickname = nicknameTextField.text, !nickname.isEmpty,
              let password = passwordTextField.text, !password.isEmpty,
              let confirmPassword = confirmPasswordTextField.text, !confirmPassword.isEmpty else {
            showAlert(message: "请填写所有字段")
            return
        }
        
        guard password == confirmPassword else {
            showAlert(message: "两次输入的密码不一致")
            return
        }
        
        // Validate height and weight
        guard let heightText = heightTextField.text, !heightText.isEmpty,
              let height = Double(heightText), height > 0 && height < 300 else {
            showAlert(message: "请输入有效的身高（50-250 cm）")
            return
        }
        
        guard let weightText = weightTextField.text, !weightText.isEmpty,
              let weight = Double(weightText), weight > 0 && weight < 500 else {
            showAlert(message: "请输入有效的体重（20-300 kg）")
            return
        }
        
        guard let ageText = ageTextField.text, !ageText.isEmpty,
              let age = Int(ageText), age >= 1 && age <= 150 else {
            showAlert(message: "请输入有效的年龄（1-150 岁）")
            return
        }
        
        // Get selected gender
        let gender: Gender = genderSegmentedControl.selectedSegmentIndex == 0 ? .male : .female
        
        activityIndicator.startAnimating()
        registerButton.isEnabled = false
        
        viewModel.register(email: email, password: password, nickname: nickname, gender: gender, age: age, height: height, currentWeight: weight) { [weak self] result in
            DispatchQueue.main.async {
                self?.activityIndicator.stopAnimating()
                self?.registerButton.isEnabled = true
                
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
        let mainTabBarController = MainTabBarController()
        
        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let window = windowScene.windows.first {
            window.rootViewController = mainTabBarController
            UIView.transition(with: window, duration: 0.3, options: .transitionCrossDissolve, animations: nil) { _ in
                // Request notification permissions after successful registration
                self.requestNotificationPermissionsIfNeeded()
            }
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
                                print("✅ User granted notification permissions after registration")
                            } else {
                                print("⚠️ User denied notification permissions after registration")
                            }
                        }
                    }
                    
                case .denied:
                    // User previously denied - don't show anything now
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
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }
}
