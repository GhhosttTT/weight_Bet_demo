import UIKit

class ProfileViewController: UIViewController {
    
    // MARK: - UI Components
    
    private let scrollView: UIScrollView = {
        let scrollView = UIScrollView()
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        return scrollView
    }()
    
    private let contentView: UIView = {
        let view = UIView()
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private let nicknameLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 24, weight: .bold)
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let emailLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 16)
        label.textColor = .secondaryLabel
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let infoStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .vertical
        stackView.spacing = 16
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private let editButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("编辑个人资料", for: .normal)
        button.backgroundColor = .systemBlue
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 8
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let paymentButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("管理支付方式", for: .normal)
        button.backgroundColor = .systemGreen
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 8
        button.translatesAutoresizingMaskIntoConstraints = false
        button.isHidden = true  // 隐藏：管理支付方式功能
        return button
    }()
    
    private let notificationButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("通知设置", for: .normal)
        button.backgroundColor = .systemOrange
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 8
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let logoutButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("退出登录", for: .normal)
        button.setTitleColor(.systemRed, for: .normal)
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
    
    private let viewModel = ProfileViewModel()
    private var user: User?
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupActions()
        loadUserProfile()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        loadUserProfile()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        title = "Profile"
        view.backgroundColor = .systemBackground
        
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        contentView.addSubview(nicknameLabel)
        contentView.addSubview(emailLabel)
        contentView.addSubview(infoStackView)
        contentView.addSubview(editButton)
        // contentView.addSubview(paymentButton)  // 隐藏：管理支付方式
        contentView.addSubview(notificationButton)
        contentView.addSubview(logoutButton)
        view.addSubview(activityIndicator)
        
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            contentView.topAnchor.constraint(equalTo: scrollView.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: scrollView.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: scrollView.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
            contentView.widthAnchor.constraint(equalTo: scrollView.widthAnchor),
            
            nicknameLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 32),
            nicknameLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 32),
            nicknameLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -32),
            
            emailLabel.topAnchor.constraint(equalTo: nicknameLabel.bottomAnchor, constant: 8),
            emailLabel.leadingAnchor.constraint(equalTo: nicknameLabel.leadingAnchor),
            emailLabel.trailingAnchor.constraint(equalTo: nicknameLabel.trailingAnchor),
            
            infoStackView.topAnchor.constraint(equalTo: emailLabel.bottomAnchor, constant: 32),
            infoStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 32),
            infoStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -32),
            
            editButton.topAnchor.constraint(equalTo: infoStackView.bottomAnchor, constant: 32),
            editButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 32),
            editButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -32),
            editButton.heightAnchor.constraint(equalToConstant: 50),
            
            // paymentButton 已隐藏，跳过布局约束
            
            notificationButton.topAnchor.constraint(equalTo: editButton.bottomAnchor, constant: 16),
            notificationButton.leadingAnchor.constraint(equalTo: editButton.leadingAnchor),
            notificationButton.trailingAnchor.constraint(equalTo: editButton.trailingAnchor),
            notificationButton.heightAnchor.constraint(equalToConstant: 50),
            
            logoutButton.topAnchor.constraint(equalTo: notificationButton.bottomAnchor, constant: 16),
            logoutButton.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            logoutButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -32),
            
            activityIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    private func setupActions() {
        editButton.addTarget(self, action: #selector(editButtonTapped), for: .touchUpInside)
        paymentButton.addTarget(self, action: #selector(paymentButtonTapped), for: .touchUpInside)
        notificationButton.addTarget(self, action: #selector(notificationButtonTapped), for: .touchUpInside)
        logoutButton.addTarget(self, action: #selector(logoutButtonTapped), for: .touchUpInside)
    }
    
    // MARK: - Data Loading
    
    private func loadUserProfile() {
        print("🔵 Loading user profile...")
        activityIndicator.startAnimating()
        
        viewModel.loadUserProfile { [weak self] result in
            DispatchQueue.main.async {
                self?.activityIndicator.stopAnimating()
                
                switch result {
                case .success(let user):
                    print("✅ User profile loaded: \(user.nickname)")
                    self?.user = user
                    self?.updateUI(with: user)
                    
                case .failure(let error):
                    print("❌ Failed to load user profile: \(error.localizedDescription)")
                    self?.showAlert(message: error.localizedDescription)
                }
            }
        }
    }
    
    private func updateUI(with user: User) {
        nicknameLabel.text = user.nickname
        emailLabel.text = user.email
        
        // Clear existing info views
        infoStackView.arrangedSubviews.forEach { $0.removeFromSuperview() }
        
        // Add user info with Chinese gender mapping (only male/female)
        let genderText = user.gender.rawValue == "male" ? "男" : "女"
        addInfoRow(title: "性别", value: genderText)
        addInfoRow(title: "年龄", value: "\(user.age) 岁")
        addInfoRow(title: "身高", value: String(format: "%.1f cm", user.height))
        addInfoRow(title: "当前体重", value: String(format: "%.1f kg", user.currentWeight))
        
        if let targetWeight = user.targetWeight {
            addInfoRow(title: "目标体重", value: String(format: "%.1f kg", targetWeight))
        }
        
        if let paymentMethod = user.paymentMethod {
            addInfoRow(title: "支付方式", value: paymentMethod)
        }
    }
    
    private func addInfoRow(title: String, value: String) {
        let containerView = UIView()
        containerView.translatesAutoresizingMaskIntoConstraints = false
        
        let titleLabel = UILabel()
        titleLabel.text = title
        titleLabel.font = .systemFont(ofSize: 14, weight: .medium)
        titleLabel.textColor = .secondaryLabel
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        
        let valueLabel = UILabel()
        valueLabel.text = value
        valueLabel.font = .systemFont(ofSize: 16)
        valueLabel.textAlignment = .right
        valueLabel.translatesAutoresizingMaskIntoConstraints = false
        
        containerView.addSubview(titleLabel)
        containerView.addSubview(valueLabel)
        
        NSLayoutConstraint.activate([
            titleLabel.leadingAnchor.constraint(equalTo: containerView.leadingAnchor),
            titleLabel.centerYAnchor.constraint(equalTo: containerView.centerYAnchor),
            
            valueLabel.trailingAnchor.constraint(equalTo: containerView.trailingAnchor),
            valueLabel.centerYAnchor.constraint(equalTo: containerView.centerYAnchor),
            valueLabel.leadingAnchor.constraint(greaterThanOrEqualTo: titleLabel.trailingAnchor, constant: 16),
            
            containerView.heightAnchor.constraint(equalToConstant: 44)
        ])
        
        infoStackView.addArrangedSubview(containerView)
    }
    
    // MARK: - Actions
    
    @objc private func editButtonTapped() {
        print("🔴 Edit button tapped")
        guard let user = user else {
            print("❌ No user data")
            return
        }
        print("✅ Navigating to edit profile for user: \(user.nickname)")
        
        let editVC = EditProfileViewController(user: user)
        navigationController?.pushViewController(editVC, animated: true)
    }
    
    @objc private func paymentButtonTapped() {
        print("🔴 Payment button tapped")
        guard let user = user else {
            print("❌ No user data")
            return
        }
        print("✅ Navigating to payment method for user: \(user.id)")
        
        let paymentVC = PaymentMethodViewController(userId: user.id)
        navigationController?.pushViewController(paymentVC, animated: true)
    }
    
    @objc private func notificationButtonTapped() {
        print("🔴 Notification button tapped")
        // Check current notification permission status
        NotificationService.shared.checkNotificationPermissionStatus { [weak self] status in
            DispatchQueue.main.async {
                guard let self = self else { return }
                
                switch status {
                case .notDetermined:
                    // First time - show explanation and request
                    NotificationPermissionHelper.showPermissionExplanation(from: self) {
                        NotificationService.shared.requestNotificationPermissions { granted in
                            DispatchQueue.main.async {
                                if granted {
                                    self.showAlert(title: "成功", message: "通知权限已成功开启！")
                                } else {
                                    self.showAlert(title: "已拒绝", message: "您可以稍后在 iOS 设置中开启通知权限。")
                                }
                            }
                        }
                    }
                    
                case .denied:
                    // User previously denied - guide them to settings
                    NotificationPermissionHelper.requestPermissionIfNeeded(from: self) { _ in }
                    
                case .authorized, .provisional, .ephemeral:
                    // Already authorized - show status
                    let alert = UIAlertController(
                        title: "已启用通知",
                        message: "您已经在接收通知。如需更改设置，请前往 iOS 设置 > Weight Loss Betting > 通知。",
                        preferredStyle: .alert
                    )
                    alert.addAction(UIAlertAction(title: "好的", style: .default))
                    alert.addAction(UIAlertAction(title: "打开设置", style: .default) { _ in
                        if let settingsUrl = URL(string: UIApplication.openSettingsURLString) {
                            UIApplication.shared.open(settingsUrl)
                        }
                    })
                    self.present(alert, animated: true)
                    
                @unknown default:
                    break
                }
            }
        }
    }
    
    @objc private func logoutButtonTapped() {
        let alert = UIAlertController(
            title: "退出登录",
            message: "确定要退出登录吗？",
            preferredStyle: .alert
        )
        
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        alert.addAction(UIAlertAction(title: "退出登录", style: .destructive) { [weak self] _ in
            self?.performLogout()
        })
        
        present(alert, animated: true)
    }
    
    private func performLogout() {
        viewModel.logout()
        
        // Navigate to login screen
        let loginVC = LoginViewController()
        let navController = UINavigationController(rootViewController: loginVC)
        
        if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
           let window = windowScene.windows.first {
            window.rootViewController = navController
            UIView.transition(with: window, duration: 0.3, options: .transitionCrossDissolve, animations: nil)
        }
    }
    
    // MARK: - Helper
    
    private func showAlert(title: String = "错误", message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }
}
