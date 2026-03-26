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
        label.text = "提现金额"
        label.font = .systemFont(ofSize: 18, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let amountTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "请输入提现金额"
        textField.keyboardType = .decimalPad
        textField.borderStyle = .roundedRect
        textField.font = .systemFont(ofSize: 16)
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let availableBalanceLabel: UILabel = {
        let label = UILabel()
        label.text = "可用余额: ¥0.00"
        label.font = .systemFont(ofSize: 14)
        label.textColor = .secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let withdrawButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("确认提现", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 18, weight: .semibold)
        button.backgroundColor = .systemOrange
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 12
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
        label.text = "注意:\n1. 提现金额不能超过可用余额\n2. 提现申请将在 1-3 个工作日内处理\n3. 提现手续费根据金额计算"
        label.font = .systemFont(ofSize: 14)
        label.textColor = .secondaryLabel
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    // MARK: - Properties
    
    private let viewModel = WithdrawViewModel()
    private var availableBalance: Double = 0.0
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupBindings()
        setupKeyboardHandling()
        loadBalance()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        title = "提现"
        view.backgroundColor = .systemBackground
        
        // Add subviews
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        contentView.addSubview(titleLabel)
        contentView.addSubview(amountTextField)
        contentView.addSubview(availableBalanceLabel)
        contentView.addSubview(noteLabel)
        contentView.addSubview(withdrawButton)
        contentView.addSubview(loadingIndicator)
        
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
            
            noteLabel.topAnchor.constraint(equalTo: availableBalanceLabel.bottomAnchor, constant: 24),
            noteLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            noteLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            withdrawButton.topAnchor.constraint(equalTo: noteLabel.bottomAnchor, constant: 32),
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
    
    private func setupBindings() {
        viewModel.onBalanceStateChanged = { [weak self] state in
            DispatchQueue.main.async {
                self?.handleBalanceState(state)
            }
        }
        
        viewModel.onWithdrawStateChanged = { [weak self] state in
            DispatchQueue.main.async {
                self?.handleWithdrawState(state)
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
    
    // MARK: - Data Loading
    
    private func loadBalance() {
        // TODO: Get actual user ID from TokenManager
        let userId = "current_user_id"
        viewModel.loadBalance(userId: userId)
    }
    
    // MARK: - Actions
    
    @objc private func withdrawButtonTapped() {
        guard let amountText = amountTextField.text, !amountText.isEmpty else {
            showAlert(title: "错误", message: "请输入提现金额")
            return
        }
        
        guard let amount = Double(amountText), amount > 0 else {
            showAlert(title: "错误", message: "请输入有效的提现金额")
            return
        }
        
        if amount > availableBalance {
            showAlert(title: "错误", message: "提现金额不能超过可用余额")
            return
        }
        
        // Show confirmation dialog
        let alert = UIAlertController(
            title: "确认提现",
            message: "确定要提现 ¥\(String(format: "%.2f", amount)) 吗?",
            preferredStyle: .alert
        )
        
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        alert.addAction(UIAlertAction(title: "确认", style: .default) { [weak self] _ in
            self?.viewModel.withdraw(amount: amount)
        })
        
        present(alert, animated: true)
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
    
    private func handleBalanceState(_ state: BalanceState) {
        switch state {
        case .idle:
            break
            
        case .loading:
            break
            
        case .success(let balance):
            availableBalance = balance.availableBalance
            availableBalanceLabel.text = "可用余额: ¥\(String(format: "%.2f", balance.availableBalance))"
            
        case .error(let message):
            showAlert(title: "加载失败", message: message)
        }
    }
    
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
            
            showAlert(title: "提现申请已提交", message: "提现金额: ¥\(String(format: "%.2f", result.amount))\n请等待审核") { [weak self] in
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
