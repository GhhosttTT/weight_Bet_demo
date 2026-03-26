import UIKit

class PaymentMethodViewController: UIViewController {
    
    // MARK: - UI Components
    
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.text = "Add Payment Method"
        label.font = .systemFont(ofSize: 24, weight: .bold)
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let descriptionLabel: UILabel = {
        let label = UILabel()
        label.text = "Link your payment method to participate in betting plans"
        label.font = .systemFont(ofSize: 14)
        label.textColor = .secondaryLabel
        label.textAlignment = .center
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let cardNumberTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Card Number"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .numberPad
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let expiryTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "MM/YY"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .numberPad
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let cvvTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "CVV"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .numberPad
        textField.isSecureTextEntry = true
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let cardHolderTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Cardholder Name"
        textField.borderStyle = .roundedRect
        textField.autocapitalizationType = .words
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let saveButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Save Payment Method", for: .normal)
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
    
    private let viewModel = PaymentMethodViewModel()
    private let userId: String
    
    // MARK: - Initialization
    
    init(userId: String) {
        self.userId = userId
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupActions()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        title = "Payment Method"
        view.backgroundColor = .systemBackground
        
        view.addSubview(titleLabel)
        view.addSubview(descriptionLabel)
        view.addSubview(cardNumberTextField)
        view.addSubview(expiryTextField)
        view.addSubview(cvvTextField)
        view.addSubview(cardHolderTextField)
        view.addSubview(saveButton)
        view.addSubview(activityIndicator)
        
        NSLayoutConstraint.activate([
            titleLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 32),
            titleLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 32),
            titleLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -32),
            
            descriptionLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 16),
            descriptionLabel.leadingAnchor.constraint(equalTo: titleLabel.leadingAnchor),
            descriptionLabel.trailingAnchor.constraint(equalTo: titleLabel.trailingAnchor),
            
            cardNumberTextField.topAnchor.constraint(equalTo: descriptionLabel.bottomAnchor, constant: 32),
            cardNumberTextField.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 32),
            cardNumberTextField.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -32),
            cardNumberTextField.heightAnchor.constraint(equalToConstant: 50),
            
            expiryTextField.topAnchor.constraint(equalTo: cardNumberTextField.bottomAnchor, constant: 16),
            expiryTextField.leadingAnchor.constraint(equalTo: cardNumberTextField.leadingAnchor),
            expiryTextField.widthAnchor.constraint(equalTo: cardNumberTextField.widthAnchor, multiplier: 0.48),
            expiryTextField.heightAnchor.constraint(equalToConstant: 50),
            
            cvvTextField.topAnchor.constraint(equalTo: expiryTextField.topAnchor),
            cvvTextField.trailingAnchor.constraint(equalTo: cardNumberTextField.trailingAnchor),
            cvvTextField.widthAnchor.constraint(equalTo: expiryTextField.widthAnchor),
            cvvTextField.heightAnchor.constraint(equalToConstant: 50),
            
            cardHolderTextField.topAnchor.constraint(equalTo: expiryTextField.bottomAnchor, constant: 16),
            cardHolderTextField.leadingAnchor.constraint(equalTo: cardNumberTextField.leadingAnchor),
            cardHolderTextField.trailingAnchor.constraint(equalTo: cardNumberTextField.trailingAnchor),
            cardHolderTextField.heightAnchor.constraint(equalToConstant: 50),
            
            saveButton.topAnchor.constraint(equalTo: cardHolderTextField.bottomAnchor, constant: 32),
            saveButton.leadingAnchor.constraint(equalTo: cardNumberTextField.leadingAnchor),
            saveButton.trailingAnchor.constraint(equalTo: cardNumberTextField.trailingAnchor),
            saveButton.heightAnchor.constraint(equalToConstant: 50),
            
            activityIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    private func setupActions() {
        saveButton.addTarget(self, action: #selector(saveButtonTapped), for: .touchUpInside)
        
        // Add tap gesture to dismiss keyboard
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        view.addGestureRecognizer(tapGesture)
    }
    
    // MARK: - Actions
    
    @objc private func saveButtonTapped() {
        guard let cardNumber = cardNumberTextField.text, !cardNumber.isEmpty,
              let expiry = expiryTextField.text, !expiry.isEmpty,
              let cvv = cvvTextField.text, !cvv.isEmpty,
              let cardHolder = cardHolderTextField.text, !cardHolder.isEmpty else {
            showAlert(message: "Please fill in all fields")
            return
        }
        
        activityIndicator.startAnimating()
        saveButton.isEnabled = false
        
        viewModel.bindPaymentMethod(
            userId: userId,
            cardNumber: cardNumber,
            expiry: expiry,
            cvv: cvv,
            cardHolder: cardHolder
        ) { [weak self] result in
            DispatchQueue.main.async {
                self?.activityIndicator.stopAnimating()
                self?.saveButton.isEnabled = true
                
                switch result {
                case .success:
                    self?.showSuccessAndDismiss()
                    
                case .failure(let error):
                    self?.showAlert(message: error.localizedDescription)
                }
            }
        }
    }
    
    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }
    
    private func showSuccessAndDismiss() {
        let alert = UIAlertController(
            title: "Success",
            message: "Payment method added successfully",
            preferredStyle: .alert
        )
        
        alert.addAction(UIAlertAction(title: "OK", style: .default) { [weak self] _ in
            self?.navigationController?.popViewController(animated: true)
        })
        
        present(alert, animated: true)
    }
    
    // MARK: - Helper
    
    private func showAlert(message: String) {
        let alert = UIAlertController(title: "Error", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}
