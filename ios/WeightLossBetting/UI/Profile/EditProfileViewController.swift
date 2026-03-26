import UIKit

class EditProfileViewController: UIViewController {
    
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
    
    private let nicknameTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Nickname"
        textField.borderStyle = .roundedRect
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let genderSegmentedControl: UISegmentedControl = {
        let control = UISegmentedControl(items: ["Male", "Female", "Other"])
        control.translatesAutoresizingMaskIntoConstraints = false
        return control
    }()
    
    private let ageTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Age"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .numberPad
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let heightTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Height (cm)"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .decimalPad
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let currentWeightTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Current Weight (kg)"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .decimalPad
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let targetWeightTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Target Weight (kg)"
        textField.borderStyle = .roundedRect
        textField.keyboardType = .decimalPad
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let saveButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("Save Changes", for: .normal)
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
    
    private let viewModel = EditProfileViewModel()
    private let user: User
    
    // MARK: - Initialization
    
    init(user: User) {
        self.user = user
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
        populateFields()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        title = "Edit Profile"
        view.backgroundColor = .systemBackground
        
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        contentView.addSubview(createLabel(text: "Nickname"))
        contentView.addSubview(nicknameTextField)
        contentView.addSubview(createLabel(text: "Gender"))
        contentView.addSubview(genderSegmentedControl)
        contentView.addSubview(createLabel(text: "Age"))
        contentView.addSubview(ageTextField)
        contentView.addSubview(createLabel(text: "Height"))
        contentView.addSubview(heightTextField)
        contentView.addSubview(createLabel(text: "Current Weight"))
        contentView.addSubview(currentWeightTextField)
        contentView.addSubview(createLabel(text: "Target Weight"))
        contentView.addSubview(targetWeightTextField)
        contentView.addSubview(saveButton)
        view.addSubview(activityIndicator)
        
        setupConstraints()
    }
    
    private func createLabel(text: String) -> UILabel {
        let label = UILabel()
        label.text = text
        label.font = .systemFont(ofSize: 14, weight: .medium)
        label.textColor = .secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }
    
    private func setupConstraints() {
        let labels = contentView.subviews.compactMap { $0 as? UILabel }
        
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
            
            labels[0].topAnchor.constraint(equalTo: contentView.topAnchor, constant: 24),
            labels[0].leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 32),
            
            nicknameTextField.topAnchor.constraint(equalTo: labels[0].bottomAnchor, constant: 8),
            nicknameTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 32),
            nicknameTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -32),
            nicknameTextField.heightAnchor.constraint(equalToConstant: 50),
            
            labels[1].topAnchor.constraint(equalTo: nicknameTextField.bottomAnchor, constant: 16),
            labels[1].leadingAnchor.constraint(equalTo: labels[0].leadingAnchor),
            
            genderSegmentedControl.topAnchor.constraint(equalTo: labels[1].bottomAnchor, constant: 8),
            genderSegmentedControl.leadingAnchor.constraint(equalTo: nicknameTextField.leadingAnchor),
            genderSegmentedControl.trailingAnchor.constraint(equalTo: nicknameTextField.trailingAnchor),
            
            labels[2].topAnchor.constraint(equalTo: genderSegmentedControl.bottomAnchor, constant: 16),
            labels[2].leadingAnchor.constraint(equalTo: labels[0].leadingAnchor),
            
            ageTextField.topAnchor.constraint(equalTo: labels[2].bottomAnchor, constant: 8),
            ageTextField.leadingAnchor.constraint(equalTo: nicknameTextField.leadingAnchor),
            ageTextField.trailingAnchor.constraint(equalTo: nicknameTextField.trailingAnchor),
            ageTextField.heightAnchor.constraint(equalToConstant: 50),
            
            labels[3].topAnchor.constraint(equalTo: ageTextField.bottomAnchor, constant: 16),
            labels[3].leadingAnchor.constraint(equalTo: labels[0].leadingAnchor),
            
            heightTextField.topAnchor.constraint(equalTo: labels[3].bottomAnchor, constant: 8),
            heightTextField.leadingAnchor.constraint(equalTo: nicknameTextField.leadingAnchor),
            heightTextField.trailingAnchor.constraint(equalTo: nicknameTextField.trailingAnchor),
            heightTextField.heightAnchor.constraint(equalToConstant: 50),
            
            labels[4].topAnchor.constraint(equalTo: heightTextField.bottomAnchor, constant: 16),
            labels[4].leadingAnchor.constraint(equalTo: labels[0].leadingAnchor),
            
            currentWeightTextField.topAnchor.constraint(equalTo: labels[4].bottomAnchor, constant: 8),
            currentWeightTextField.leadingAnchor.constraint(equalTo: nicknameTextField.leadingAnchor),
            currentWeightTextField.trailingAnchor.constraint(equalTo: nicknameTextField.trailingAnchor),
            currentWeightTextField.heightAnchor.constraint(equalToConstant: 50),
            
            labels[5].topAnchor.constraint(equalTo: currentWeightTextField.bottomAnchor, constant: 16),
            labels[5].leadingAnchor.constraint(equalTo: labels[0].leadingAnchor),
            
            targetWeightTextField.topAnchor.constraint(equalTo: labels[5].bottomAnchor, constant: 8),
            targetWeightTextField.leadingAnchor.constraint(equalTo: nicknameTextField.leadingAnchor),
            targetWeightTextField.trailingAnchor.constraint(equalTo: nicknameTextField.trailingAnchor),
            targetWeightTextField.heightAnchor.constraint(equalToConstant: 50),
            
            saveButton.topAnchor.constraint(equalTo: targetWeightTextField.bottomAnchor, constant: 32),
            saveButton.leadingAnchor.constraint(equalTo: nicknameTextField.leadingAnchor),
            saveButton.trailingAnchor.constraint(equalTo: nicknameTextField.trailingAnchor),
            saveButton.heightAnchor.constraint(equalToConstant: 50),
            saveButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -32),
            
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
    
    private func populateFields() {
        nicknameTextField.text = user.nickname
        
        switch user.gender {
        case .male:
            genderSegmentedControl.selectedSegmentIndex = 0
        case .female:
            genderSegmentedControl.selectedSegmentIndex = 1
        case .other:
            genderSegmentedControl.selectedSegmentIndex = 2
        }
        
        ageTextField.text = "\(user.age)"
        heightTextField.text = String(format: "%.1f", user.height)
        currentWeightTextField.text = String(format: "%.1f", user.currentWeight)
        
        if let targetWeight = user.targetWeight {
            targetWeightTextField.text = String(format: "%.1f", targetWeight)
        }
    }
    
    // MARK: - Actions
    
    @objc private func saveButtonTapped() {
        guard let nickname = nicknameTextField.text, !nickname.isEmpty,
              let ageText = ageTextField.text, let age = Int(ageText),
              let heightText = heightTextField.text, let height = Double(heightText),
              let weightText = currentWeightTextField.text, let weight = Double(weightText) else {
            showAlert(message: "Please fill in all required fields")
            return
        }
        
        let gender: Gender
        switch genderSegmentedControl.selectedSegmentIndex {
        case 0:
            gender = .male
        case 1:
            gender = .female
        default:
            gender = .other
        }
        
        let targetWeight = Double(targetWeightTextField.text ?? "")
        
        activityIndicator.startAnimating()
        saveButton.isEnabled = false
        
        viewModel.updateProfile(
            userId: user.id,
            nickname: nickname,
            gender: gender,
            age: age,
            height: height,
            currentWeight: weight,
            targetWeight: targetWeight
        ) { [weak self] result in
            DispatchQueue.main.async {
                self?.activityIndicator.stopAnimating()
                self?.saveButton.isEnabled = true
                
                switch result {
                case .success:
                    self?.navigationController?.popViewController(animated: true)
                    
                case .failure(let error):
                    self?.showAlert(message: error.localizedDescription)
                }
            }
        }
    }
    
    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }
    
    // MARK: - Helper
    
    private func showAlert(message: String) {
        let alert = UIAlertController(title: "Error", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}
