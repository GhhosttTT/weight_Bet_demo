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
        label.textColor = .secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let quickAmountStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .horizontal
        stackView.distribution = .fillEqually
        stackView.spacing = 12
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private let withdrawButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Confirm Withdrawal", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 18, weight: .semibold)
        button.backgroundColor = .systemBlue
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
        label.text = "Note: Withdrawals may take 1-3 business days to process. A withdrawal fee of 2% applies."
        label.font = .systemFont(ofSize: 14)
        label.textColor = .secondaryLabel
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
        view.backgroundColor = .systemBackground
        
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
    
    private func createQuickAmountButton(amount: Double) -> UIButton {
        let button = UIButton(type: .system)
        button.setTitle("¥\(Int(amount))", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 16, weight: .medium)
        button.backgroundColor = .systemGray6
        button.setTitleColor(.label, for: .normal)
        button.layer.cornerRadius = 8
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
            showAlert(title: "Error", message: "Please enter a withdrawal amount")
            return
        }
        
        guard let amount = Double(amountText), amount > 0 else {
            showAlert(title: "Error", message: "Please enter a valid withdrawal amount")
            return
        }
        
        guard amount <= viewModel.availableBalance else {
            showAlert(title: "Error", message: "Withdrawal amount exceeds available balance")
            return
        }
        
        // TODO: In production, get actual bank account details from user's profile
        let bankAccount = BankAccount(
            bankName: "ICBC",
            accountNumber: "6222 0212 0012 3456 789",
            accountHolderName: "张三"
        )
        
        viewModel.withdraw(amount: amount, bankAccount: bankAccount)
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
            withdrawButton.setTitle("Confirm Withdrawal", for: .normal)
            
        case .loading:
            loadingIndicator.startAnimating()
            withdrawButton.isEnabled = false
            withdrawButton.setTitle("", for: .normal)
            
        case .success(let result):
            loadingIndicator.stopAnimating()
            withdrawButton.isEnabled = true
            withdrawButton.setTitle("Confirm Withdrawal", for: .normal)
            
            showAlert(title: "Withdrawal Successful", message: "Withdrawal Amount: ¥\(String(format: "%.2f", result.amount))") { [weak self] in
                self?.navigationController?.popViewController(animated: true)
            }
            
        case .error(let message):
            loadingIndicator.stopAnimating()
            withdrawButton.isEnabled = true
            withdrawButton.setTitle("Confirm Withdrawal", for: .normal)
            
            showAlert(title: "Withdrawal Failed", message: message)
        }
    }
    
    // MARK: - Helper Methods
    
    private func showAlert(title: String, message: String, completion: (() -> Void)? = nil) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default) { _ in
            completion?()
        })
        present(alert, animated: true)
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}