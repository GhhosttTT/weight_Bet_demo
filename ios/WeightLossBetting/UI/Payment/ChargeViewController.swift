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
        label.text = "Charge Amount"
        label.font = .systemFont(ofSize: 18, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let amountTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Enter charge amount"
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
        stackView.spacing = 12
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private let chargeButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Confirm Charge", for: .normal)
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
        label.text = "Note: Charges will be processed through the Stripe payment gateway"
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
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupBindings()
        setupKeyboardHandling()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        title = "Charge"
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
            
            chargeButton.topAnchor.constraint(equalTo: noteLabel.bottomAnchor, constant: 32),
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
        viewModel.onChargeStateChanged = { [weak self] state in
            DispatchQueue.main.async {
                self?.handleChargeState(state)
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
    
    @objc private func chargeButtonTapped() {
        guard let amountText = amountTextField.text, !amountText.isEmpty else {
            showAlert(title: "Error", message: "Please enter a charge amount")
            return
        }
        
        guard let amount = Double(amountText), amount > 0 else {
            showAlert(title: "Error", message: "Please enter a valid charge amount")
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
            chargeButton.setTitle("Confirm Charge", for: .normal)
            
        case .loading:
            loadingIndicator.startAnimating()
            chargeButton.isEnabled = false
            chargeButton.setTitle("", for: .normal)
            
        case .success(let result):
            loadingIndicator.stopAnimating()
            chargeButton.isEnabled = true
            chargeButton.setTitle("Confirm Charge", for: .normal)
            
            showAlert(title: "Charge Successful", message: "Charge Amount: ¥\(String(format: "%.2f", result.amount))") { [weak self] in
                self?.navigationController?.popViewController(animated: true)
            }
            
        case .error(let message):
            loadingIndicator.stopAnimating()
            chargeButton.isEnabled = true
            chargeButton.setTitle("Confirm Charge", for: .normal)
            
            showAlert(title: "Charge Failed", message: message)
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