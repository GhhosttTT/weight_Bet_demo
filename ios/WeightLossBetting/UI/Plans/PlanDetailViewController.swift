import UIKit

class PlanDetailViewController: UIViewController {
    
    // MARK: - Properties
    
    private let viewModel: PlanDetailViewModel
    private var scrollView: UIScrollView!
    private var contentView: UIView!
    
    // Public property to set plan ID from notification navigation
    var planId: String? {
        didSet {
            if let planId = planId, isViewLoaded {
                viewModel.setPlanId(planId)
                viewModel.loadPlanDetail()
            }
        }
    }
    
    private var statusLabel: UILabel!
    private var betAmountLabel: UILabel!
    private var dateRangeLabel: UILabel!
    private var creatorGoalLabel: UILabel!
    private var participantGoalLabel: UILabel!
    private var descriptionLabel: UILabel!
    
    private var acceptPlanView: UIView!
    private var initialWeightTextField: UITextField!
    private var targetWeightTextField: UITextField!
    private var acceptButton: UIButton!
    private var rejectButton: UIButton!
    
    private var loadingIndicator: UIActivityIndicatorView!
    
    // MARK: - Initialization
    
    init(planId: String) {
        self.viewModel = PlanDetailViewModel(planId: planId)
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "计划详情"
        view.backgroundColor = .systemBackground
        
        setupUI()
        setupBindings()
        setupKeyboardHandling()
        viewModel.loadPlanDetail()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        // Scroll view
        scrollView = UIScrollView()
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(scrollView)
        
        contentView = UIView()
        contentView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.addSubview(contentView)
        
        // Status
        let statusTitleLabel = createTitleLabel(text: "状态")
        statusLabel = createValueLabel()
        
        // Bet amount
        let betAmountTitleLabel = createTitleLabel(text: "赌金金额")
        betAmountLabel = createValueLabel()
        betAmountLabel.textColor = .systemRed
        betAmountLabel.font = .boldSystemFont(ofSize: 24)
        
        // Date range
        let dateRangeTitleLabel = createTitleLabel(text: "计划时间")
        dateRangeLabel = createValueLabel()
        
        // Creator goal
        let creatorGoalTitleLabel = createTitleLabel(text: "创建者目标")
        creatorGoalLabel = createValueLabel()
        
        // Participant goal
        let participantGoalTitleLabel = createTitleLabel(text: "参与者目标")
        participantGoalLabel = createValueLabel()
        
        // Description
        let descriptionTitleLabel = createTitleLabel(text: "计划描述")
        descriptionLabel = createValueLabel()
        descriptionLabel.numberOfLines = 0
        
        // Accept plan view (for pending plans)
        acceptPlanView = UIView()
        acceptPlanView.translatesAutoresizingMaskIntoConstraints = false
        acceptPlanView.isHidden = true
        
        let acceptTitleLabel = createTitleLabel(text: "接受计划")
        acceptTitleLabel.font = .boldSystemFont(ofSize: 18)
        
        let initialWeightLabel = createLabel(text: "初始体重 (kg)")
        initialWeightTextField = createTextField(placeholder: "请输入初始体重", keyboardType: .decimalPad)
        
        let targetWeightLabel = createLabel(text: "目标体重 (kg)")
        targetWeightTextField = createTextField(placeholder: "请输入目标体重", keyboardType: .decimalPad)
        
        acceptButton = UIButton(type: .system)
        acceptButton.setTitle("接受计划", for: .normal)
        acceptButton.titleLabel?.font = .boldSystemFont(ofSize: 18)
        acceptButton.backgroundColor = .systemGreen
        acceptButton.setTitleColor(.white, for: .normal)
        acceptButton.layer.cornerRadius = 12
        acceptButton.addTarget(self, action: #selector(acceptTapped), for: .touchUpInside)
        acceptButton.translatesAutoresizingMaskIntoConstraints = false
        
        rejectButton = UIButton(type: .system)
        rejectButton.setTitle("拒绝计划", for: .normal)
        rejectButton.titleLabel?.font = .boldSystemFont(ofSize: 18)
        rejectButton.backgroundColor = .systemRed
        rejectButton.setTitleColor(.white, for: .normal)
        rejectButton.layer.cornerRadius = 12
        rejectButton.addTarget(self, action: #selector(rejectTapped), for: .touchUpInside)
        rejectButton.translatesAutoresizingMaskIntoConstraints = false
        
        [acceptTitleLabel, initialWeightLabel, initialWeightTextField,
         targetWeightLabel, targetWeightTextField,
         acceptButton, rejectButton].forEach { acceptPlanView.addSubview($0) }
        
        // Loading indicator
        loadingIndicator = UIActivityIndicatorView(style: .large)
        loadingIndicator.hidesWhenStopped = true
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false
        
        // Add to content view
        [statusTitleLabel, statusLabel,
         betAmountTitleLabel, betAmountLabel,
         dateRangeTitleLabel, dateRangeLabel,
         creatorGoalTitleLabel, creatorGoalLabel,
         participantGoalTitleLabel, participantGoalLabel,
         descriptionTitleLabel, descriptionLabel,
         acceptPlanView, loadingIndicator].forEach { contentView.addSubview($0) }
        
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
            
            statusTitleLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 20),
            statusTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            statusTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            statusLabel.topAnchor.constraint(equalTo: statusTitleLabel.bottomAnchor, constant: 8),
            statusLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            statusLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            betAmountTitleLabel.topAnchor.constraint(equalTo: statusLabel.bottomAnchor, constant: 20),
            betAmountTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            betAmountTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            betAmountLabel.topAnchor.constraint(equalTo: betAmountTitleLabel.bottomAnchor, constant: 8),
            betAmountLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            betAmountLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            dateRangeTitleLabel.topAnchor.constraint(equalTo: betAmountLabel.bottomAnchor, constant: 20),
            dateRangeTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            dateRangeTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            dateRangeLabel.topAnchor.constraint(equalTo: dateRangeTitleLabel.bottomAnchor, constant: 8),
            dateRangeLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            dateRangeLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            creatorGoalTitleLabel.topAnchor.constraint(equalTo: dateRangeLabel.bottomAnchor, constant: 20),
            creatorGoalTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            creatorGoalTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            creatorGoalLabel.topAnchor.constraint(equalTo: creatorGoalTitleLabel.bottomAnchor, constant: 8),
            creatorGoalLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            creatorGoalLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            participantGoalTitleLabel.topAnchor.constraint(equalTo: creatorGoalLabel.bottomAnchor, constant: 20),
            participantGoalTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            participantGoalTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            participantGoalLabel.topAnchor.constraint(equalTo: participantGoalTitleLabel.bottomAnchor, constant: 8),
            participantGoalLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            participantGoalLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            descriptionTitleLabel.topAnchor.constraint(equalTo: participantGoalLabel.bottomAnchor, constant: 20),
            descriptionTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            descriptionTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            descriptionLabel.topAnchor.constraint(equalTo: descriptionTitleLabel.bottomAnchor, constant: 8),
            descriptionLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            descriptionLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            acceptPlanView.topAnchor.constraint(equalTo: descriptionLabel.bottomAnchor, constant: 30),
            acceptPlanView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            acceptPlanView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),
            acceptPlanView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -20),
            
            loadingIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
        
        // Accept plan view layout
        NSLayoutConstraint.activate([
            acceptTitleLabel.topAnchor.constraint(equalTo: acceptPlanView.topAnchor),
            acceptTitleLabel.leadingAnchor.constraint(equalTo: acceptPlanView.leadingAnchor, constant: 16),
            acceptTitleLabel.trailingAnchor.constraint(equalTo: acceptPlanView.trailingAnchor, constant: -16),
            
            initialWeightLabel.topAnchor.constraint(equalTo: acceptTitleLabel.bottomAnchor, constant: 16),
            initialWeightLabel.leadingAnchor.constraint(equalTo: acceptPlanView.leadingAnchor, constant: 16),
            initialWeightLabel.trailingAnchor.constraint(equalTo: acceptPlanView.trailingAnchor, constant: -16),
            
            initialWeightTextField.topAnchor.constraint(equalTo: initialWeightLabel.bottomAnchor, constant: 8),
            initialWeightTextField.leadingAnchor.constraint(equalTo: acceptPlanView.leadingAnchor, constant: 16),
            initialWeightTextField.trailingAnchor.constraint(equalTo: acceptPlanView.trailingAnchor, constant: -16),
            initialWeightTextField.heightAnchor.constraint(equalToConstant: 44),
            
            targetWeightLabel.topAnchor.constraint(equalTo: initialWeightTextField.bottomAnchor, constant: 16),
            targetWeightLabel.leadingAnchor.constraint(equalTo: acceptPlanView.leadingAnchor, constant: 16),
            targetWeightLabel.trailingAnchor.constraint(equalTo: acceptPlanView.trailingAnchor, constant: -16),
            
            targetWeightTextField.topAnchor.constraint(equalTo: targetWeightLabel.bottomAnchor, constant: 8),
            targetWeightTextField.leadingAnchor.constraint(equalTo: acceptPlanView.leadingAnchor, constant: 16),
            targetWeightTextField.trailingAnchor.constraint(equalTo: acceptPlanView.trailingAnchor, constant: -16),
            targetWeightTextField.heightAnchor.constraint(equalToConstant: 44),
            
            acceptButton.topAnchor.constraint(equalTo: targetWeightTextField.bottomAnchor, constant: 24),
            acceptButton.leadingAnchor.constraint(equalTo: acceptPlanView.leadingAnchor, constant: 16),
            acceptButton.trailingAnchor.constraint(equalTo: acceptPlanView.trailingAnchor, constant: -16),
            acceptButton.heightAnchor.constraint(equalToConstant: 50),
            
            rejectButton.topAnchor.constraint(equalTo: acceptButton.bottomAnchor, constant: 12),
            rejectButton.leadingAnchor.constraint(equalTo: acceptPlanView.leadingAnchor, constant: 16),
            rejectButton.trailingAnchor.constraint(equalTo: acceptPlanView.trailingAnchor, constant: -16),
            rejectButton.heightAnchor.constraint(equalToConstant: 50),
            rejectButton.bottomAnchor.constraint(equalTo: acceptPlanView.bottomAnchor)
        ])
    }
    
    private func setupBindings() {
        viewModel.onPlanUpdated = { [weak self] plan in
            self?.displayPlanDetail(plan)
        }
        
        viewModel.onError = { [weak self] message in
            self?.showError(message)
        }
        
        viewModel.onLoadingChanged = { [weak self] isLoading in
            if isLoading {
                self?.loadingIndicator.startAnimating()
            } else {
                self?.loadingIndicator.stopAnimating()
            }
            self?.acceptButton.isEnabled = !isLoading
            self?.rejectButton.isEnabled = !isLoading
        }
        
        viewModel.onActionSuccess = { [weak self] message in
            self?.showSuccessAndDismiss(message)
        }
    }
    
    private func setupKeyboardHandling() {
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        view.addGestureRecognizer(tapGesture)
        
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillShow), name: UIResponder.keyboardWillShowNotification, object: nil)
        NotificationCenter.default.addObserver(self, selector: #selector(keyboardWillHide), name: UIResponder.keyboardWillHideNotification, object: nil)
    }
    
    // MARK: - Helper Methods
    
    private func createTitleLabel(text: String) -> UILabel {
        let label = UILabel()
        label.text = text
        label.font = .systemFont(ofSize: 14, weight: .medium)
        label.textColor = .secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }
    
    private func createValueLabel() -> UILabel {
        let label = UILabel()
        label.font = .systemFont(ofSize: 16)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }
    
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
    
    private func displayPlanDetail(_ plan: BettingPlan) {
        // Status
        switch plan.status {
        case .pending:
            statusLabel.text = "待接受"
            statusLabel.textColor = .systemOrange
            acceptPlanView.isHidden = false
        case .active:
            statusLabel.text = "进行中"
            statusLabel.textColor = .systemGreen
            acceptPlanView.isHidden = true
        case .completed:
            statusLabel.text = "已完成"
            statusLabel.textColor = .systemGray
            acceptPlanView.isHidden = true
        case .cancelled:
            statusLabel.text = "已取消"
            statusLabel.textColor = .systemGray
            acceptPlanView.isHidden = true
        case .rejected:
            statusLabel.text = "已拒绝"
            statusLabel.textColor = .systemGray
            acceptPlanView.isHidden = true
        }
        
        // Bet amount
        betAmountLabel.text = "¥\(String(format: "%.2f", plan.betAmount))"
        
        // Date range
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        let startDateStr = dateFormatter.string(from: plan.startDate)
        let endDateStr = dateFormatter.string(from: plan.endDate)
        dateRangeLabel.text = "\(startDateStr) 至 \(endDateStr)"
        
        // Creator goal
        let creatorWeightLoss = plan.creatorGoal.targetWeightLoss
        creatorGoalLabel.text = "\(String(format: "%.1f", plan.creatorGoal.initialWeight))kg → \(String(format: "%.1f", plan.creatorGoal.targetWeight))kg (减重\(String(format: "%.1f", creatorWeightLoss))kg)"
        
        // Participant goal
        if let participantGoal = plan.participantGoal {
            let participantWeightLoss = participantGoal.targetWeightLoss
            participantGoalLabel.text = "\(String(format: "%.1f", participantGoal.initialWeight))kg → \(String(format: "%.1f", participantGoal.targetWeight))kg (减重\(String(format: "%.1f", participantWeightLoss))kg)"
        } else {
            participantGoalLabel.text = "待设置"
        }
        
        // Description
        descriptionLabel.text = plan.description ?? "无描述"
    }
    
    // MARK: - Actions
    
    @objc private func acceptTapped() {
        guard let initialWeight = initialWeightTextField.text, !initialWeight.isEmpty else {
            showError("请输入初始体重")
            return
        }
        
        guard let targetWeight = targetWeightTextField.text, !targetWeight.isEmpty else {
            showError("请输入目标体重")
            return
        }
        
        viewModel.acceptPlan(initialWeight: initialWeight, targetWeight: targetWeight)
    }
    
    @objc private func rejectTapped() {
        let alert = UIAlertController(title: "确认", message: "确定要拒绝这个计划吗?", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        alert.addAction(UIAlertAction(title: "确定", style: .destructive) { [weak self] _ in
            self?.viewModel.rejectPlan()
        })
        present(alert, animated: true)
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
    
    private func showError(_ message: String) {
        let alert = UIAlertController(title: "错误", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }
    
    private func showSuccessAndDismiss(_ message: String) {
        let alert = UIAlertController(title: "成功", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default) { [weak self] _ in
            self?.navigationController?.popViewController(animated: true)
        })
        present(alert, animated: true)
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}
