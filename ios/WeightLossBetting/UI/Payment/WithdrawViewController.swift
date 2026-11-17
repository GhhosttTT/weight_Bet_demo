import UIKit

class WithdrawViewController: UIViewController {
    
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
    
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.text = "Withdrawal Amount"
        label.font = .systemFont(ofSize: 18, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let amountTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Enter withdrawal amount"
        textField.keyboardType = .decimalPad
        textField.borderStyle = .roundedRect
        textField.font = .systemFont(ofSize: 16)
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let availableBalanceLabel: UILabel = {
        let label = UILabel()
        label.text = "Available Balance: ¥0.00"
        label.font = .systemFont(ofSize: 14, weight: .medium)
        label.textColor = AppTheme.Colors.secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let quickAmountStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .horizontal
        stackView.distribution = .fillEqually
        stackView.spacing = 8  // 减小间距到 8px
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private let withdrawButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("确认提现", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 18, weight: .semibold)
        button.backgroundColor = AppTheme.Colors.success  // 使用绿色表示提现
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 10
        button.layer.shadowColor = UIColor.black.cgColor
        button.layer.shadowOffset = CGSize(width: 0, height: 2)
        button.layer.shadowOpacity = 0.15
        button.layer.shadowRadius = 4
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let loadingIndicator: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .medium)
        indicator.hidesWhenStopped = true
        indicator.translatesAutoresizingMaskIntoConstraints = false
        return indicator
    }()
    
    private let noteLabel: UILabel = {
        let label = UILabel()
        label.text = "Note: Withdrawals may take 1-3 business days to process. A withdrawal fee of 2% applies."
        label.font = .systemFont(ofSize: 14)
        label.textColor = AppTheme.Colors.secondaryLabel
        label.numberOfLines = 0
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    // MARK: - Properties
    
    private let viewModel = WithdrawViewModel()
    private let quickAmounts = [50.0, 100.0, 200.0, 500.0]
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupBindings()
        setupKeyboardHandling()
        viewModel.loadAvailableBalance()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        title = "Withdraw"
        view.backgroundColor = AppTheme.Colors.background
        
        // Add subviews
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        contentView.addSubview(titleLabel)
        contentView.addSubview(amountTextField)
        contentView.addSubview(availableBalanceLabel)
        contentView.addSubview(quickAmountStackView)
        contentView.addSubview(noteLabel)
        contentView.addSubview(withdrawButton)
        contentView.addSubview(loadingIndicator)
        
        // Setup quick amount buttons
        for amount in quickAmounts {
            let button = createQuickAmountButton(amount: amount)
            quickAmountStackView.addArrangedSubview(button)
        }
        
        // Setup constraints
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
            
            titleLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 24),
            titleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            titleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            amountTextField.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 16),
            amountTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            amountTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            amountTextField.heightAnchor.constraint(equalToConstant: 50),
            
            availableBalanceLabel.topAnchor.constraint(equalTo: amountTextField.bottomAnchor, constant: 8),
            availableBalanceLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            availableBalanceLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            quickAmountStackView.topAnchor.constraint(equalTo: availableBalanceLabel.bottomAnchor, constant: 20),
            quickAmountStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            quickAmountStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            quickAmountStackView.heightAnchor.constraint(equalToConstant: 44),
            
            noteLabel.topAnchor.constraint(equalTo: quickAmountStackView.bottomAnchor, constant: 24),
            noteLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            noteLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            withdrawButton.topAnchor.constraint(equalTo: noteLabel.bottomAnchor, constant: 24),  // 减小间距到 24
            withdrawButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            withdrawButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            withdrawButton.heightAnchor.constraint(equalToConstant: 50),
            withdrawButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -24),
            
            loadingIndicator.centerXAnchor.constraint(equalTo: withdrawButton.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: withdrawButton.centerYAnchor)
        ])
        
        // Add tap gesture to dismiss keyboard
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        view.addGestureRecognizer(tapGesture)
        
        // Add button actions
        withdrawButton.addTarget(self, action: #selector(withdrawButtonTapped), for: .touchUpInside)
    }
    
    private func createQuickAmountButton(amount: Double) -> UIButton {
        let button = UIButton(type: .system)
        button.setTitle("¥\(Int(amount))", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 15, weight: .medium)  // 稍微缩小字体
        button.backgroundColor = AppTheme.Colors.primary.withAlphaComponent(0.1)  // 使用淡蓝色背景
        button.setTitleColor(AppTheme.Colors.primary, for: .normal)  // 蓝色字体
        button.layer.cornerRadius = 8
        button.layer.borderWidth = 1  // 添加边框
        button.layer.borderColor = AppTheme.Colors.primary.withAlphaComponent(0.3).cgColor
        button.addTarget(self, action: #selector(quickAmountButtonTapped(_:)), for: .touchUpInside)
        button.tag = Int(amount)
        return button
    }
    
    private func setupBindings() {
        viewModel.onWithdrawStateChanged = { [weak self] state in
            DispatchQueue.main.async {
                self?.handleWithdrawState(state)
            }
        }
        
        viewModel.onAvailableBalanceUpdated = { [weak self] balance in
            DispatchQueue.main.async {
                self?.availableBalanceLabel.text = "Available Balance: ¥\(String(format: "%.2f", balance))"
            }
        }
    }
    
    private func setupKeyboardHandling() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(keyboardWillShow),
            name: UIResponder.keyboardWillShowNotification,
            object: nil
        )
        
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(keyboardWillHide),
            name: UIResponder.keyboardWillHideNotification,
            object: nil
        )
    }
    
    // MARK: - Actions
    
    @objc private func quickAmountButtonTapped(_ sender: UIButton) {
        let amount = Double(sender.tag)
        amountTextField.text = String(format: "%.0f", amount)
    }
    
    @objc private func withdrawButtonTapped() {
        guard let amountText = amountTextField.text, !amountText.isEmpty else {
            showAlert(title: "错误", message: "请输入提现金额")
            return
        }
        
        guard let amount = Double(amountText), amount > 0 else {
            showAlert(title: "错误", message: "请输入有效的提现金额")
            return
        }
        
        guard amount <= viewModel.availableBalance else {
            showAlert(title: "错误", message: "提现金额超过可用余额")
            return
        }
        
        guard let userId = AuthRepository.shared.getCurrentUserId(), !userId.isEmpty else {
            showAlert(title: "登录状态已失效", message: "请重新登录后再提现")
            return
        }

        UserRepository.shared.getUserProfile(userId: userId, forceRefresh: true) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let user):
                    guard let paymentMethodId = user.paymentMethod, !paymentMethodId.isEmpty else {
                        self?.showAlert(title: "尚未绑定提现方式", message: "请先在个人资料中绑定支付方式")
                        return
                    }
                    self?.viewModel.withdraw(amount: amount, paymentMethodId: paymentMethodId)
                case .failure(let error):
                    self?.showAlert(title: "读取提现方式失败", message: error.localizedDescription)
                }
            }
        }
    }
    
    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }
    
    @objc private func keyboardWillShow(notification: NSNotification) {
        guard let keyboardFrame = notification.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect else {
            return
        }
        
        let contentInsets = UIEdgeInsets(top: 0, left: 0, bottom: keyboardFrame.height, right: 0)
        scrollView.contentInset = contentInsets
        scrollView.scrollIndicatorInsets = contentInsets
    }
    
    @objc private func keyboardWillHide(notification: NSNotification) {
        scrollView.contentInset = .zero
        scrollView.scrollIndicatorInsets = .zero
    }
    
    // MARK: - State Handling
    
    private func handleWithdrawState(_ state: WithdrawState) {
        switch state {
        case .idle:
            loadingIndicator.stopAnimating()
            withdrawButton.isEnabled = true
            withdrawButton.setTitle("确认提现", for: .normal)
            
        case .loading:
            loadingIndicator.startAnimating()
            withdrawButton.isEnabled = false
            withdrawButton.setTitle("", for: .normal)
            
        case .success(let result):
            loadingIndicator.stopAnimating()
            withdrawButton.isEnabled = true
            withdrawButton.setTitle("确认提现", for: .normal)
            
            showAlert(title: "提现成功", message: "提现金额：¥\(String(format: "%.2f", result.amount))") { [weak self] in
                self?.navigationController?.popViewController(animated: true)
            }
            
        case .error(let message):
            loadingIndicator.stopAnimating()
            withdrawButton.isEnabled = true
            withdrawButton.setTitle("确认提现", for: .normal)
            
            showAlert(title: "提现失败", message: message)
        }
    }
    
    // MARK: - Helper Methods
    
    private func showAlert(title: String, message: String, completion: (() -> Void)? = nil) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default) { _ in
            completion?()
        })
        present(alert, animated: true)
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}
