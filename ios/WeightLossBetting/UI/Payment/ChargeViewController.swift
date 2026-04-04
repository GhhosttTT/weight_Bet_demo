import UIKit

class ChargeViewController: UIViewController {
    
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
        label.text = "充值金额"
        label.font = .systemFont(ofSize: 18, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let amountTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "请输入充值金额"
        textField.keyboardType = .decimalPad
        textField.borderStyle = .roundedRect
        textField.font = .systemFont(ofSize: 16)
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let quickAmountStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .horizontal
        stackView.distribution = .fillEqually
        stackView.spacing = 8  // 减小间距到 8px
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private let chargeButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("确认充值", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 18, weight: .semibold)
        button.backgroundColor = UIColor.systemBlue
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
        label.text = "提示：充值将通过 Stripe 支付网关进行处理"
        label.font = .systemFont(ofSize: 14)
        label.textColor = .secondaryLabel
        label.numberOfLines = 0
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    // MARK: - Properties
    
    private let viewModel = ChargeViewModel()
    private let quickAmounts = [50.0, 100.0, 200.0, 500.0]
    private var preFillAmountValue: Double?  // 存储预填金额
    var onChargeSuccess: (() -> Void)?  // 充值成功回调
    var lockAmount: Bool = false  // 锁定金额，不允许用户修改
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupBindings()
        setupKeyboardHandling()
        
        // 如果有预填金额，在视图加载完成后设置
        if let amount = preFillAmountValue {
            amountTextField.text = String(format: "%.0f", amount)
            print("✅ [ChargeVC] 已预填充值金额：¥\(amount)")
        }
        
        // 锁定金额模式：不允许修改金额
        if lockAmount {
            amountTextField.isEnabled = false
            amountTextField.textColor = .secondaryLabel
            quickAmountStackView.isUserInteractionEnabled = false
            quickAmountStackView.alpha = 0.5
            titleLabel.text = "支付计划保证金"
        }
    }
    
    // Pre-fill amount for charge
    func preFillAmount(_ amount: Double) {
        preFillAmountValue = amount  // 先存储
        // 如果视图已加载，直接设置
        if isViewLoaded {
            amountTextField.text = String(format: "%.0f", amount)
            print("✅ [ChargeVC] 已预填充值金额：¥\(amount)")
        }
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        title = "充值"
        view.backgroundColor = .systemBackground
        
        // Add subviews
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        contentView.addSubview(titleLabel)
        contentView.addSubview(amountTextField)
        contentView.addSubview(quickAmountStackView)
        contentView.addSubview(noteLabel)
        contentView.addSubview(chargeButton)
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
            
            quickAmountStackView.topAnchor.constraint(equalTo: amountTextField.bottomAnchor, constant: 20),
            quickAmountStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            quickAmountStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            quickAmountStackView.heightAnchor.constraint(equalToConstant: 44),
            
            noteLabel.topAnchor.constraint(equalTo: quickAmountStackView.bottomAnchor, constant: 24),
            noteLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            noteLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            chargeButton.topAnchor.constraint(equalTo: noteLabel.bottomAnchor, constant: 24),  // 减小间距到 24
            chargeButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            chargeButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            chargeButton.heightAnchor.constraint(equalToConstant: 50),
            chargeButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -24),
            
            loadingIndicator.centerXAnchor.constraint(equalTo: chargeButton.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: chargeButton.centerYAnchor)
        ])
        
        // Add tap gesture to dismiss keyboard
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        view.addGestureRecognizer(tapGesture)
        
        // Add button actions
        chargeButton.addTarget(self, action: #selector(chargeButtonTapped), for: .touchUpInside)
        
        // Setup navigation bar items
        setupNavigationBar()
    }
    
    private func setupNavigationBar() {
        // Add close button for modal presentation
        navigationItem.leftBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .close,
            target: self,
            action: #selector(closeButtonTapped)
        )
    }
    
    private func createQuickAmountButton(amount: Double) -> UIButton {
        let button = UIButton(type: .system)
        button.setTitle("¥\(Int(amount))", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 15, weight: .medium)  // 稍微缩小字体
        button.backgroundColor = UIColor.systemBlue.withAlphaComponent(0.1)  // 使用淡蓝色背景
        button.setTitleColor(.systemBlue, for: .normal)  // 蓝色字体
        button.layer.cornerRadius = 8
        button.layer.borderWidth = 1  // 添加边框
        button.layer.borderColor = UIColor.systemBlue.withAlphaComponent(0.3).cgColor
        button.addTarget(self, action: #selector(quickAmountButtonTapped(_:)), for: .touchUpInside)
        button.tag = Int(amount)
        return button
    }
    
    private func setupBindings() {
        viewModel.onChargeStateChanged = { [weak self] state in
            DispatchQueue.main.async {
                self?.handleChargeState(state)
            }
        }
        
        // 注意：已移除 onBalanceRefreshWarning 回调，因为余额刷新失败不影响充值成功
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
    
    @objc private func closeButtonTapped() {
        dismiss(animated: true)
    }
    
    @objc private func quickAmountButtonTapped(_ sender: UIButton) {
        let amount = Double(sender.tag)
        amountTextField.text = String(format: "%.0f", amount)
    }
    
    @objc private func chargeButtonTapped() {
        guard let amountText = amountTextField.text, !amountText.isEmpty else {
            showAlert(title: "错误", message: "请输入充值金额")
            return
        }
        
        guard let amount = Double(amountText), amount > 0 else {
            showAlert(title: "错误", message: "请输入有效的充值金额")
            return
        }
        
        // TODO: In production, get actual payment method ID from user's saved payment methods
        let paymentMethodId = "pm_test_card"
        
        viewModel.charge(amount: amount, paymentMethodId: paymentMethodId)
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
    
    private func handleChargeState(_ state: ChargeState) {
        switch state {
        case .idle:
            loadingIndicator.stopAnimating()
            chargeButton.isEnabled = true
            chargeButton.setTitle("确认充值", for: .normal)
            
        case .loading:
            loadingIndicator.startAnimating()
            chargeButton.isEnabled = false
            chargeButton.setTitle("", for: .normal)
            
        case .success(let result):
            print("✅ [ChargeVC] 充值成功回调，金额=¥\(result.amount)")
            
            loadingIndicator.stopAnimating()
            chargeButton.isEnabled = true
            chargeButton.setTitle("确认充值", for: .normal)
            
            // 显示 Toast 提示
            print("💬 [ChargeVC] 显示 Toast 提示")
            showToast(message: "充值成功，正在返回...")
            
            // 调用充值成功回调
            onChargeSuccess?()
            
            // 延迟 1.5 秒后关闭
            print("⏱️ [ChargeVC] 延迟 1.5 秒后关闭充值页面")
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) { [weak self] in
                print("🚪 [ChargeVC] 正在关闭充值页面...")
                self?.dismiss(animated: true)
                print("✅ [ChargeVC] 充值页面已关闭")
            }
            
        case .error(let message):
            loadingIndicator.stopAnimating()
            chargeButton.isEnabled = true
            chargeButton.setTitle("确认充值", for: .normal)
            
            showAlert(title: "充值失败", message: message)
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
    
    private func showToast(message: String, duration: TimeInterval = 2.0) {
        guard Thread.isMainThread else {
            DispatchQueue.main.async { self.showToast(message: message, duration: duration) }
            return
        }
        
        // Remove old toast
        view.viewWithTag(999)?.removeFromSuperview()
        
        // Create toast view
        let toastView = UIView()
        toastView.tag = 999
        toastView.backgroundColor = UIColor.black.withAlphaComponent(0.7)
        toastView.layer.cornerRadius = 8
        toastView.translatesAutoresizingMaskIntoConstraints = false
        
        let label = UILabel()
        label.text = message
        label.textColor = .white
        label.font = .systemFont(ofSize: 14)
        label.textAlignment = .center
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        toastView.addSubview(label)
        
        view.addSubview(toastView)
        
        NSLayoutConstraint.activate([
            label.leadingAnchor.constraint(equalTo: toastView.leadingAnchor, constant: 16),
            label.trailingAnchor.constraint(equalTo: toastView.trailingAnchor, constant: -16),
            label.topAnchor.constraint(equalTo: toastView.topAnchor, constant: 12),
            label.bottomAnchor.constraint(equalTo: toastView.bottomAnchor, constant: -12),
            
            toastView.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            toastView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -100),
            toastView.widthAnchor.constraint(lessThanOrEqualTo: view.widthAnchor, multiplier: 0.8, constant: -32)
        ])
        
    // Auto dismiss
        DispatchQueue.main.asyncAfter(deadline: .now() + duration) {
            toastView.removeFromSuperview()
        }
    }
    
    // MARK: - Deprecated Methods
    
    // showBalanceRefreshWarning 已移除，因为不再需要

    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}