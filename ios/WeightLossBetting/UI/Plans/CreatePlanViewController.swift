import UIKit

class CreatePlanViewController: UIViewController {
    
    // MARK: - Properties
    
    private let viewModel = CreatePlanViewModel()
    private var scrollView: UIScrollView!
    private var contentView: UIView!
    
    private var betAmountTextField: UITextField!
    private var startDateTextField: UITextField!
    private var endDateTextField: UITextField!
    private var initialWeightTextField: UITextField!
    private var targetWeightTextField: UITextField!
    private var descriptionTextView: UITextView!
    private var createButton: UIButton!
    private var loadingIndicator: UIActivityIndicatorView!
    
    private var startDatePicker: UIDatePicker!
    private var endDatePicker: UIDatePicker!
    
    private var startDate: Date?
    private var endDate: Date?
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "创建对赌计划"
        view.backgroundColor = .systemBackground
        
        setupUI()
        setupBindings()
        setupKeyboardHandling()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        // Navigation bar
        navigationItem.leftBarButtonItem = UIBarButtonItem(barButtonSystemItem: .cancel, target: self, action: #selector(cancelTapped))
        
        // Scroll view
        scrollView = UIScrollView()
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(scrollView)
        
        contentView = UIView()
        contentView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.addSubview(contentView)
        
        // Bet amount
        let betAmountLabel = createLabel(text: "赌金金额 (¥)")
        betAmountTextField = createTextField(placeholder: "请输入赌金金额", keyboardType: .decimalPad)
        
        // Start date
        let startDateLabel = createLabel(text: "开始日期")
        startDateTextField = createTextField(placeholder: "请选择开始日期")
        startDatePicker = createDatePicker()
        startDatePicker.addTarget(self, action: #selector(startDateChanged), for: .valueChanged)
        startDateTextField.inputView = startDatePicker
        
        // End date
        let endDateLabel = createLabel(text: "结束日期")
        endDateTextField = createTextField(placeholder: "请选择结束日期")
        endDatePicker = createDatePicker()
        endDatePicker.addTarget(self, action: #selector(endDateChanged), for: .valueChanged)
        endDateTextField.inputView = endDatePicker
        
        // Initial weight
        let initialWeightLabel = createLabel(text: "初始体重 (kg)")
        initialWeightTextField = createTextField(placeholder: "请输入初始体重", keyboardType: .decimalPad)
        
        // Target weight
        let targetWeightLabel = createLabel(text: "目标体重 (kg)")
        targetWeightTextField = createTextField(placeholder: "请输入目标体重", keyboardType: .decimalPad)
        
        // Description
        let descriptionLabel = createLabel(text: "计划描述 (可选)")
        descriptionTextView = UITextView()
        descriptionTextView.font = .systemFont(ofSize: 16)
        descriptionTextView.layer.borderColor = UIColor.systemGray4.cgColor
        descriptionTextView.layer.borderWidth = 1
        descriptionTextView.layer.cornerRadius = 8
        descriptionTextView.textContainerInset = UIEdgeInsets(top: 8, left: 8, bottom: 8, right: 8)
        descriptionTextView.translatesAutoresizingMaskIntoConstraints = false
        
        // Create button
        createButton = UIButton(type: .system)
        createButton.setTitle("创建计划", for: .normal)
        createButton.titleLabel?.font = .boldSystemFont(ofSize: 18)
        createButton.backgroundColor = .systemBlue
        createButton.setTitleColor(.white, for: .normal)
        createButton.layer.cornerRadius = 12
        createButton.addTarget(self, action: #selector(createTapped), for: .touchUpInside)
        createButton.translatesAutoresizingMaskIntoConstraints = false
        
        // Loading indicator
        loadingIndicator = UIActivityIndicatorView(style: .medium)
        loadingIndicator.hidesWhenStopped = true
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false
        
        // Add to content view
        [betAmountLabel, betAmountTextField,
         startDateLabel, startDateTextField,
         endDateLabel, endDateTextField,
         initialWeightLabel, initialWeightTextField,
         targetWeightLabel, targetWeightTextField,
         descriptionLabel, descriptionTextView,
         createButton, loadingIndicator].forEach { contentView.addSubview($0) }
        
        // Layout
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
            
            betAmountLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 20),
            betAmountLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            betAmountLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            betAmountTextField.topAnchor.constraint(equalTo: betAmountLabel.bottomAnchor, constant: 8),
            betAmountTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            betAmountTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            betAmountTextField.heightAnchor.constraint(equalToConstant: 44),
            
            startDateLabel.topAnchor.constraint(equalTo: betAmountTextField.bottomAnchor, constant: 20),
            startDateLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            startDateLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            startDateTextField.topAnchor.constraint(equalTo: startDateLabel.bottomAnchor, constant: 8),
            startDateTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            startDateTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            startDateTextField.heightAnchor.constraint(equalToConstant: 44),
            
            endDateLabel.topAnchor.constraint(equalTo: startDateTextField.bottomAnchor, constant: 20),
            endDateLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            endDateLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            endDateTextField.topAnchor.constraint(equalTo: endDateLabel.bottomAnchor, constant: 8),
            endDateTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            endDateTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            endDateTextField.heightAnchor.constraint(equalToConstant: 44),
            
            initialWeightLabel.topAnchor.constraint(equalTo: endDateTextField.bottomAnchor, constant: 20),
            initialWeightLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            initialWeightLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            initialWeightTextField.topAnchor.constraint(equalTo: initialWeightLabel.bottomAnchor, constant: 8),
            initialWeightTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            initialWeightTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            initialWeightTextField.heightAnchor.constraint(equalToConstant: 44),
            
            targetWeightLabel.topAnchor.constraint(equalTo: initialWeightTextField.bottomAnchor, constant: 20),
            targetWeightLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            targetWeightLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            targetWeightTextField.topAnchor.constraint(equalTo: targetWeightLabel.bottomAnchor, constant: 8),
            targetWeightTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            targetWeightTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            targetWeightTextField.heightAnchor.constraint(equalToConstant: 44),
            
            descriptionLabel.topAnchor.constraint(equalTo: targetWeightTextField.bottomAnchor, constant: 20),
            descriptionLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            descriptionLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            descriptionTextView.topAnchor.constraint(equalTo: descriptionLabel.bottomAnchor, constant: 8),
            descriptionTextView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            descriptionTextView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            descriptionTextView.heightAnchor.constraint(equalToConstant: 100),
            
            createButton.topAnchor.constraint(equalTo: descriptionTextView.bottomAnchor, constant: 30),
            createButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            createButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            createButton.heightAnchor.constraint(equalToConstant: 50),
            createButton.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -30),
            
            loadingIndicator.centerXAnchor.constraint(equalTo: createButton.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: createButton.centerYAnchor)
        ])
    }
    
    private func setupBindings() {
        viewModel.onSuccess = { [weak self] plan in
            self?.showSuccess()
        }
        
        viewModel.onError = { [weak self] message in
            self?.showError(message)
        }
        
        viewModel.onLoadingChanged = { [weak self] isLoading in
            self?.createButton.isEnabled = !isLoading
            if isLoading {
                self?.loadingIndicator.startAnimating()
                self?.createButton.setTitle("", for: .normal)
            } else {
                self?.loadingIndicator.stopAnimating()
                self?.createButton.setTitle("创建计划", for: .normal)
            }
        }
    }
    
    private func setupKeyboardHandling() {
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        view.addGestureRecognizer(tapGesture)
        
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillShow), name: UIResponder.keyboardWillShowNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillHide), name: UIResponder.keyboardWillHideNotification, object: nil)
    }
    
    // MARK: - Helper Methods
    
    private func createLabel(text: String) -> UILabel {
        let label = UILabel()
        label.text = text
        label.font = .systemFont(ofSize: 16, weight: .medium)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }
    
    private func createTextField(placeholder: String, keyboardType: UIKeyboardType = .default) -> UITextField {
        let textField = UITextField()
        textField.placeholder = placeholder
        textField.borderStyle = .roundedRect
        textField.keyboardType = keyboardType
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }
    
    private func createDatePicker() -> UIDatePicker {
        let picker = UIDatePicker()
        picker.datePickerMode = .date
        picker.preferredDatePickerStyle = .wheels
        picker.minimumDate = Date()
        return picker
    }
    
    // MARK: - Actions
    
    @objc private func cancelTapped() {
        dismiss(animated: true)
    }
    
    @objc private func startDateChanged() {
        startDate = startDatePicker.date
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        startDateTextField.text = formatter.string(from: startDatePicker.date)
        
        // Update end date picker minimum date
        endDatePicker.minimumDate = startDatePicker.date
    }
    
    @objc private func endDateChanged() {
        endDate = endDatePicker.date
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        endDateTextField.text = formatter.string(from: endDatePicker.date)
    }
    
    @objc private func createTapped() {
        guard let betAmount = betAmountTextField.text, !betAmount.isEmpty else {
            showError("请输入赌金金额")
            return
        }
        
        guard let startDate = startDate else {
            showError("请选择开始日期")
            return
        }
        
        guard let endDate = endDate else {
            showError("请选择结束日期")
            return
        }
        
        guard let initialWeight = initialWeightTextField.text, !initialWeight.isEmpty else {
            showError("请输入初始体重")
            return
        }
        
        guard let targetWeight = targetWeightTextField.text, !targetWeight.isEmpty else {
            showError("请输入目标体重")
            return
        }
        
        let description = descriptionTextView.text.trimmingCharacters(in: .whitespacesAndNewlines)
        
        viewModel.createPlan(
            betAmount: betAmount,
            startDate: startDate,
            endDate: endDate,
            initialWeight: initialWeight,
            targetWeight: targetWeight,
            description: description.isEmpty ? nil : description
        )
    }
    
    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }
    
    @objc private func keyboardWillShow(notification: NSNotification) {
        guard let keyboardFrame = notification.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect else { return }
        let contentInset = UIEdgeInsets(top: 0, left: 0, bottom: keyboardFrame.height, right: 0)
        scrollView.contentInset = contentInset
        scrollView.scrollIndicatorInsets = contentInset
    }
    
    @objc private func keyboardWillHide(notification: NSNotification) {
        scrollView.contentInset = .zero
        scrollView.scrollIndicatorInsets = .zero
    }
    
    // MARK: - UI Feedback
    
    private func showSuccess() {
        let alert = UIAlertController(title: "成功", message: "计划创建成功", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "稍后邀请", style: .cancel) { [weak self] _ in
            self?.dismiss(animated: true)
        })
        alert.addAction(UIAlertAction(title: "立即邀请", style: .default) { [weak self] _ in
            guard let self = self, let plan = self.viewModel.plan else {
                self?.dismiss(animated: true)
                return
            }
            let inviteVC = InviteViewController(planId: plan.id)
            let navController = UINavigationController(rootViewController: inviteVC)
            self.present(navController, animated: true)
        })
        present(alert, animated: true)
    }
    
    private func showError(_ message: String) {
        let alert = UIAlertController(title: "错误", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}
