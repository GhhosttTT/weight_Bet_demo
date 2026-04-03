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
    private var creatorInfoLabel: UILabel!      // 创建者信息（昵称 + 邮箱）
    private var creatorGoalLabel: UILabel!
    private var participantInfoLabel: UILabel!
    private var participantGoalLabel: UILabel!
    private var descriptionLabel: UILabel!
    
    // Action buttons for different states
    private var actionButtonsView: UIView!
    private var cancelButton: UIButton!      // 取消计划（待接受/待二次确认阶段）
    private var acceptButton: UIButton!      // 接受计划（待接受/待二次确认阶段）
    private var rejectButton: UIButton!      // 拒绝计划（待接受阶段）
    private var confirmButton: UIButton!     // 二次确认接受（待二次确认阶段）
    private var checkInButton: UIButton!     // 打卡（进行中阶段）
    private var giveUpButton: UIButton!      // 放弃计划（进行中阶段）
    
    // Accept plan form (for pending plans)
    private var acceptPlanFormView: UIView!
    private var initialWeightTextField: UITextField!
    private var targetWeightTextField: UITextField!
    private var pendingInitialWeight: String? // 余额不足时保存待提交的初始体重
    private var pendingTargetWeight: String? // 余额不足时保存待提交的目标体重
    private var preFillParticipant: (nickname: String, email: String)? // 创建计划时预填充的参与者信息
    
    private var loadingIndicator: UIActivityIndicatorView!
    
    // MARK: - Initialization
    
    init(planId: String, preFillParticipant: (nickname: String, email: String)? = nil) {
        self.viewModel = PlanDetailViewModel(planId: planId)
        self.preFillParticipant = preFillParticipant
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
        viewModel.loadPlanDetail(forceRefresh: true) // 每次进入详情页都拉取最新数据，避免缓存过期
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
        
        // Creator info (name/email)
        let creatorInfoTitleLabel = createTitleLabel(text: "创建者")
        creatorInfoLabel = createValueLabel()
        
        // Creator goal
        let creatorGoalTitleLabel = createTitleLabel(text: "创建者目标")
        creatorGoalLabel = createValueLabel()
        
        // Participant info (name/email)
        let participantInfoTitleLabel = createTitleLabel(text: "参与者")
        participantInfoLabel = createValueLabel()
        
        // Participant goal
        let participantGoalTitleLabel = createTitleLabel(text: "参与者目标")
        participantGoalLabel = createValueLabel()
        
        // Description
        let descriptionTitleLabel = createTitleLabel(text: "计划描述")
        descriptionLabel = createValueLabel()
        descriptionLabel.numberOfLines = 0
        
        // Action buttons view (replaces acceptPlanView)
        actionButtonsView = UIView()
        actionButtonsView.translatesAutoresizingMaskIntoConstraints = false
        actionButtonsView.isHidden = true
        
        // Cancel button (for pending/pendingConfirmation)
        cancelButton = UIButton(type: .system)
        cancelButton.setTitle("取消计划", for: .normal)
        cancelButton.titleLabel?.font = .boldSystemFont(ofSize: 16)
        cancelButton.backgroundColor = .systemGray2
        cancelButton.setTitleColor(.darkText, for: .normal)
        cancelButton.layer.cornerRadius = 10
        cancelButton.addTarget(self, action: #selector(cancelTapped), for: .touchUpInside)
        cancelButton.translatesAutoresizingMaskIntoConstraints = false
        actionButtonsView.addSubview(cancelButton)
        
        // Reject button (for pending only)
        rejectButton = UIButton(type: .system)
        rejectButton.setTitle("拒绝计划", for: .normal)
        rejectButton.titleLabel?.font = .boldSystemFont(ofSize: 16)
        rejectButton.backgroundColor = .systemRed
        rejectButton.setTitleColor(.white, for: .normal)
        rejectButton.layer.cornerRadius = 10
        rejectButton.addTarget(self, action: #selector(rejectTapped), for: .touchUpInside)
        rejectButton.translatesAutoresizingMaskIntoConstraints = false
        actionButtonsView.addSubview(rejectButton)
        
        // Accept/Confirm button (for pending/pendingConfirmation)
        acceptButton = UIButton(type: .system)
        acceptButton.setTitle("接受计划", for: .normal)
        acceptButton.titleLabel?.font = .boldSystemFont(ofSize: 16)
        acceptButton.backgroundColor = .systemGreen
        acceptButton.setTitleColor(.white, for: .normal)
        acceptButton.layer.cornerRadius = 10
        acceptButton.addTarget(self, action: #selector(acceptTapped), for: .touchUpInside)
        acceptButton.translatesAutoresizingMaskIntoConstraints = false
        actionButtonsView.addSubview(acceptButton)
        
        // Confirm button (for pendingConfirmation only)
        confirmButton = UIButton(type: .system)
        confirmButton.setTitle("确认并开始", for: .normal)
        confirmButton.titleLabel?.font = .boldSystemFont(ofSize: 18)
        confirmButton.backgroundColor = .systemGreen
        confirmButton.setTitleColor(.white, for: .normal)
        confirmButton.layer.cornerRadius = 12
        confirmButton.addTarget(self, action: #selector(confirmTapped), for: .touchUpInside)
        confirmButton.translatesAutoresizingMaskIntoConstraints = false
        actionButtonsView.addSubview(confirmButton)
        
        // Check-in button (for active)
        checkInButton = UIButton(type: .system)
        checkInButton.setTitle("打卡", for: .normal)
        checkInButton.titleLabel?.font = .boldSystemFont(ofSize: 18)
        checkInButton.backgroundColor = .systemBlue
        checkInButton.setTitleColor(.white, for: .normal)
        checkInButton.layer.cornerRadius = 12
        checkInButton.addTarget(self, action: #selector(checkInTapped), for: .touchUpInside)
        checkInButton.translatesAutoresizingMaskIntoConstraints = false
        actionButtonsView.addSubview(checkInButton)
        
        // Give-up button (for active)
        giveUpButton = UIButton(type: .system)
        giveUpButton.setTitle("放弃计划", for: .normal)
        giveUpButton.titleLabel?.font = .boldSystemFont(ofSize: 16)
        giveUpButton.backgroundColor = .systemOrange
        giveUpButton.setTitleColor(.white, for: .normal)
        giveUpButton.layer.cornerRadius = 10
        giveUpButton.addTarget(self, action: #selector(giveUpTapped), for: .touchUpInside)
        giveUpButton.translatesAutoresizingMaskIntoConstraints = false
        actionButtonsView.addSubview(giveUpButton)
        
        // Accept plan form view (for entering weight when accepting)
        acceptPlanFormView = UIView()
        acceptPlanFormView.translatesAutoresizingMaskIntoConstraints = false
        acceptPlanFormView.isHidden = true
        
        let formTitleLabel = createTitleLabel(text: "填写你的目标")
        formTitleLabel.font = .boldSystemFont(ofSize: 16)
        
        let initialWeightLabel = createLabel(text: "初始体重 (kg)")
        initialWeightTextField = createTextField(placeholder: "请输入初始体重", keyboardType: .decimalPad)
        
        let targetWeightLabel = createLabel(text: "目标体重 (kg)")
        targetWeightTextField = createTextField(placeholder: "请输入目标体重", keyboardType: .decimalPad)
        
        [formTitleLabel, initialWeightLabel, initialWeightTextField,
         targetWeightLabel, targetWeightTextField].forEach { acceptPlanFormView.addSubview($0) }
        
        // 设置表单内部元素的约束
        NSLayoutConstraint.activate([
            formTitleLabel.topAnchor.constraint(equalTo: acceptPlanFormView.topAnchor, constant: 16),
            formTitleLabel.leadingAnchor.constraint(equalTo: acceptPlanFormView.leadingAnchor, constant: 16),
            formTitleLabel.trailingAnchor.constraint(equalTo: acceptPlanFormView.trailingAnchor, constant: -16),
            
            initialWeightLabel.topAnchor.constraint(equalTo: formTitleLabel.bottomAnchor, constant: 16),
            initialWeightLabel.leadingAnchor.constraint(equalTo: acceptPlanFormView.leadingAnchor, constant: 16),
            initialWeightLabel.trailingAnchor.constraint(equalTo: acceptPlanFormView.trailingAnchor, constant: -16),
            
            initialWeightTextField.topAnchor.constraint(equalTo: initialWeightLabel.bottomAnchor, constant: 8),
            initialWeightTextField.leadingAnchor.constraint(equalTo: acceptPlanFormView.leadingAnchor, constant: 16),
            initialWeightTextField.trailingAnchor.constraint(equalTo: acceptPlanFormView.trailingAnchor, constant: -16),
            initialWeightTextField.heightAnchor.constraint(equalToConstant: 44),
            
            targetWeightLabel.topAnchor.constraint(equalTo: initialWeightTextField.bottomAnchor, constant: 16),
            targetWeightLabel.leadingAnchor.constraint(equalTo: acceptPlanFormView.leadingAnchor, constant: 16),
            targetWeightLabel.trailingAnchor.constraint(equalTo: acceptPlanFormView.trailingAnchor, constant: -16),
            
            targetWeightTextField.topAnchor.constraint(equalTo: targetWeightLabel.bottomAnchor, constant: 8),
            targetWeightTextField.leadingAnchor.constraint(equalTo: acceptPlanFormView.leadingAnchor, constant: 16),
            targetWeightTextField.trailingAnchor.constraint(equalTo: acceptPlanFormView.trailingAnchor, constant: -16),
            targetWeightTextField.heightAnchor.constraint(equalToConstant: 44),
            targetWeightTextField.bottomAnchor.constraint(equalTo: acceptPlanFormView.bottomAnchor, constant: -16)
        ])
        
        // Loading indicator
        loadingIndicator = UIActivityIndicatorView(style: .large)
        loadingIndicator.hidesWhenStopped = true
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false
        
        // Add to content view
        [statusTitleLabel, statusLabel,
         betAmountTitleLabel, betAmountLabel,
         dateRangeTitleLabel, dateRangeLabel,
         creatorInfoTitleLabel, creatorInfoLabel,
         creatorGoalTitleLabel, creatorGoalLabel,
         participantInfoTitleLabel, participantInfoLabel,
         participantGoalTitleLabel, participantGoalLabel,
         descriptionTitleLabel, descriptionLabel,
         acceptPlanFormView, loadingIndicator].forEach { contentView.addSubview($0) }
        // 操作按钮改为悬浮在底部固定显示
        actionButtonsView.backgroundColor = .systemBackground
        actionButtonsView.layer.shadowColor = UIColor.black.cgColor
        actionButtonsView.layer.shadowOpacity = 0.1
        actionButtonsView.layer.shadowOffset = CGSize(width: 0, height: -2)
        actionButtonsView.layer.shadowRadius = 4
        view.addSubview(actionButtonsView)
        
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
            
            betAmountTitleLabel.topAnchor.constraint(equalTo: statusLabel.bottomAnchor, constant: 12),
            betAmountTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            betAmountTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            betAmountLabel.topAnchor.constraint(equalTo: betAmountTitleLabel.bottomAnchor, constant: 6),
            betAmountLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            betAmountLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            dateRangeTitleLabel.topAnchor.constraint(equalTo: betAmountLabel.bottomAnchor, constant: 12),
            dateRangeTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            dateRangeTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            dateRangeLabel.topAnchor.constraint(equalTo: dateRangeTitleLabel.bottomAnchor, constant: 6),
            dateRangeLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            dateRangeLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            creatorInfoTitleLabel.topAnchor.constraint(equalTo: dateRangeLabel.bottomAnchor, constant: 12),
            creatorInfoTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            creatorInfoTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            creatorInfoLabel.topAnchor.constraint(equalTo: creatorInfoTitleLabel.bottomAnchor, constant: 6),
            creatorInfoLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            creatorInfoLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            creatorGoalTitleLabel.topAnchor.constraint(equalTo: creatorInfoLabel.bottomAnchor, constant: 12),
            creatorGoalTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            creatorGoalTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            creatorGoalLabel.topAnchor.constraint(equalTo: creatorGoalTitleLabel.bottomAnchor, constant: 6),
            creatorGoalLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            creatorGoalLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            participantInfoTitleLabel.topAnchor.constraint(equalTo: creatorGoalLabel.bottomAnchor, constant: 12),
            participantInfoTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            participantInfoTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            participantInfoLabel.topAnchor.constraint(equalTo: participantInfoTitleLabel.bottomAnchor, constant: 6),
            participantInfoLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            participantInfoLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            participantGoalTitleLabel.topAnchor.constraint(equalTo: participantInfoLabel.bottomAnchor, constant: 12),
            participantGoalTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            participantGoalTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            participantGoalLabel.topAnchor.constraint(equalTo: participantGoalTitleLabel.bottomAnchor, constant: 6),
            participantGoalLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            participantGoalLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            descriptionTitleLabel.topAnchor.constraint(equalTo: participantGoalLabel.bottomAnchor, constant: 12),
            descriptionTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            descriptionTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            descriptionLabel.topAnchor.constraint(equalTo: descriptionTitleLabel.bottomAnchor, constant: 6),
            descriptionLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            descriptionLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            // 表单区域在描述之后，按钮之前
            acceptPlanFormView.topAnchor.constraint(equalTo: descriptionLabel.bottomAnchor, constant: 16),
            acceptPlanFormView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            acceptPlanFormView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),
            acceptPlanFormView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -100), // 底部预留100px避免被悬浮按钮遮挡
            
            cancelButton.topAnchor.constraint(equalTo: actionButtonsView.topAnchor),
            cancelButton.leadingAnchor.constraint(equalTo: actionButtonsView.leadingAnchor, constant: 16),
            cancelButton.trailingAnchor.constraint(equalTo: actionButtonsView.trailingAnchor, constant: -16),
            cancelButton.heightAnchor.constraint(equalToConstant: 44),
            
            acceptButton.topAnchor.constraint(equalTo: cancelButton.bottomAnchor, constant: 12),
            acceptButton.leadingAnchor.constraint(equalTo: actionButtonsView.leadingAnchor, constant: 16),
            acceptButton.trailingAnchor.constraint(equalTo: actionButtonsView.trailingAnchor, constant: -16),
            acceptButton.heightAnchor.constraint(equalToConstant: 44),
            
            rejectButton.topAnchor.constraint(equalTo: acceptButton.bottomAnchor, constant: 12),
            rejectButton.leadingAnchor.constraint(equalTo: actionButtonsView.leadingAnchor, constant: 16),
            rejectButton.trailingAnchor.constraint(equalTo: actionButtonsView.trailingAnchor, constant: -16),
            rejectButton.heightAnchor.constraint(equalToConstant: 44),
            
            confirmButton.topAnchor.constraint(equalTo: actionButtonsView.topAnchor),
            confirmButton.leadingAnchor.constraint(equalTo: actionButtonsView.leadingAnchor, constant: 16),
            confirmButton.trailingAnchor.constraint(equalTo: actionButtonsView.trailingAnchor, constant: -16),
            confirmButton.heightAnchor.constraint(equalToConstant: 50),
            
            checkInButton.topAnchor.constraint(equalTo: actionButtonsView.topAnchor),
            checkInButton.leadingAnchor.constraint(equalTo: actionButtonsView.leadingAnchor, constant: 16),
            checkInButton.trailingAnchor.constraint(equalTo: actionButtonsView.trailingAnchor, constant: -16),
            checkInButton.heightAnchor.constraint(equalToConstant: 50),
            
            giveUpButton.topAnchor.constraint(equalTo: rejectButton.bottomAnchor, constant: 12),
            giveUpButton.leadingAnchor.constraint(equalTo: actionButtonsView.leadingAnchor, constant: 16),
            giveUpButton.trailingAnchor.constraint(equalTo: actionButtonsView.trailingAnchor, constant: -16),
            giveUpButton.heightAnchor.constraint(equalToConstant: 44),
            giveUpButton.bottomAnchor.constraint(equalTo: actionButtonsView.bottomAnchor)
        ])
        
        // Loading indicator
        NSLayoutConstraint.activate([
            loadingIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            
            // 操作按钮悬浮固定在底部
            actionButtonsView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            actionButtonsView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            actionButtonsView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor)
        ])
        
        // 给scrollView添加底部内边距，避免内容被悬浮按钮遮挡
        scrollView.contentInset = UIEdgeInsets(top: 0, left: 0, bottom: 120, right: 0)
    }
    
    private func setupBindings() {
        viewModel.onPlanUpdated = { [weak self] plan in
            self?.displayPlanDetail(plan)
        }
        
        viewModel.onError = { [weak self] message in
            self?.showError(message)
        }
        
        viewModel.onLoadingChanged = { [weak self] isLoading in
            DispatchQueue.main.async {
                if isLoading {
                    self?.loadingIndicator.startAnimating()
                } else {
                    self?.loadingIndicator.stopAnimating()
                }
                self?.acceptButton.isEnabled = !isLoading
                self?.rejectButton.isEnabled = !isLoading
                self?.confirmButton.isEnabled = !isLoading
                self?.cancelButton.isEnabled = !isLoading
                self?.checkInButton.isEnabled = !isLoading
                self?.giveUpButton.isEnabled = !isLoading
            }
        }
        
        viewModel.onActionSuccess = { [weak self] message in
            self?.showSuccessAndDismiss(message)
        }
        
        viewModel.onPaymentRequired = { [weak self] requiredAmount in
            guard let self = self else { return }
            // 弹出余额不足提示
            let alert = UIAlertController(
                title: "余额不足",
                message: "您的账户余额不足，需要充值¥\(String(format: "%.2f", requiredAmount))元才能参与该计划",
                preferredStyle: .alert
            )
            alert.addAction(UIAlertAction(title: "取消", style: .cancel))
            alert.addAction(UIAlertAction(title: "立即充值", style: .default) { [weak self] _ in
                guard let self = self else { return }
                // 跳转到充值页面
                let chargeVC = ChargeViewController()
                chargeVC.preFillAmount(requiredAmount)
                chargeVC.lockAmount = true
                chargeVC.onChargeSuccess = { [weak self] in
                    guard let self = self,
                          let initialWeight = self.pendingInitialWeight,
                          let targetWeight = self.pendingTargetWeight else { return }
                    // 充值成功后自动返回并重试接受计划
                    DispatchQueue.main.async {
                        self.dismiss(animated: true) {
                            self.viewModel.acceptPlan(initialWeight: initialWeight, targetWeight: targetWeight)
                        }
                    }
                }
                let nav = UINavigationController(rootViewController: chargeVC)
                self.present(nav, animated: true)
            })
            self.present(alert, animated: true)
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
        let currentUserId = AuthRepository.shared.getCurrentUserId() ?? ""
        let isCreator = plan.creatorId == currentUserId
        
        // Status display and button visibility
        switch plan.status {
        case .pending:
            // 待接受阶段
            statusLabel.text = "待接受"
            statusLabel.textColor = .systemOrange
            
            if isCreator {
                // 创建者：只能取消
                showCancelOnly()
            } else {
                // 被邀请者：可以接受或拒绝（强制显示表单，防止身份判断异常）
                showAcceptRejectForm()
                // 额外校验：确保表单和按钮可见
                acceptPlanFormView.isHidden = false
                rejectButton.isHidden = false
                acceptButton.isHidden = false
            }
            
        case .pendingConfirmation:
            // 待二次确认阶段
            statusLabel.text = "待二次确认"
            statusLabel.textColor = .systemPurple
            
            if isCreator {
                // 创建者：可以取消或确认开始
                showCancelConfirmButtons()
            } else {
                // 被邀请者：已接受，等待对方确认
                showWaitingForConfirmation()
            }
            
        case .active:
            // 进行中阶段
            statusLabel.text = "进行中"
            statusLabel.textColor = .systemGreen
            showCheckInGiveUpButtons()
            
        case .completed:
            statusLabel.text = "已完成"
            statusLabel.textColor = .systemGray
            hideAllButtons()
            
        case .cancelled:
            statusLabel.text = "已取消"
            statusLabel.textColor = .systemGray
            hideAllButtons()
            
        case .rejected:
            statusLabel.text = "已拒绝"
            statusLabel.textColor = .systemGray
            hideAllButtons()
            
        case .expired:
            statusLabel.text = "已过期"
            statusLabel.textColor = .systemGray
            hideAllButtons()
        }
        
        // Bet amount
        betAmountLabel.text = "¥\(String(format: "%.2f", plan.betAmount))"
        
        // Date range
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        let startDateStr = dateFormatter.string(from: plan.startDate)
        let endDateStr = dateFormatter.string(from: plan.endDate)
        dateRangeLabel.text = "\(startDateStr) 至 \(endDateStr)"
        
        // Creator info
        let (creatorNickname, creatorEmail) = viewModel.getCreatorNicknameAndEmail()
        if let nickname = creatorNickname, !nickname.isEmpty {
            let creatorText = creatorEmail != nil ? "\(nickname) (\(creatorEmail!))" : nickname
            creatorInfoLabel.text = creatorText
            creatorInfoLabel.isHidden = false
        } else if let email = creatorEmail, !email.isEmpty {
            creatorInfoLabel.text = email
            creatorInfoLabel.isHidden = false
        } else {            // 如果昵称和邮箱都没有，显示“未知用户”
            creatorInfoLabel.text = "未知用户"
            creatorInfoLabel.isHidden = false
        }
        
        // Creator goal
        let creatorWeightLoss = plan.creatorTargetWeightLoss
        creatorGoalLabel.text = "\(String(format: "%.1f", plan.creatorInitialWeight))kg → \(String(format: "%.1f", plan.creatorTargetWeight))kg (减重\(String(format: "%.1f", creatorWeightLoss))kg)"
        
        // Participant info
        let (participantNickname, participantEmail) = viewModel.getParticipantNicknameAndEmail()
        print("🔍 [DEBUG] 参与者信息：nickname=\(participantNickname ?? "nil"), email=\(participantEmail ?? "nil")")
        
        var finalNickname = participantNickname
        var finalEmail = participantEmail
        
        // 如果后端还没返回参与者信息，用预填充的信息
        let hasNoParticipantInfo = (finalNickname == nil || finalNickname!.isEmpty) && (finalEmail == nil || finalEmail!.isEmpty)
        if hasNoParticipantInfo, let preFill = preFillParticipant {
            finalNickname = preFill.nickname
            finalEmail = preFill.email
            print("🔍 [DEBUG] 使用预填充参与者信息：\(finalNickname!) (\(finalEmail!))")
        }
        
        if let nickname = finalNickname, !nickname.isEmpty {
            let participantText = finalEmail != nil ? "\(nickname) (\(finalEmail!))" : nickname
            participantInfoLabel.text = participantText
        } else if let email = finalEmail, !email.isEmpty {
            participantInfoLabel.text = email
        } else {
            // 如果昵称和邮箱都没有，显示“未知用户”
            participantInfoLabel.text = "未知用户"
        }
        // 强制显示，永不隐藏
        participantInfoLabel.isHidden = false
        participantInfoLabel.textColor = .label
        
        // Participant goal
        if let participantInitialWeight = plan.participantInitialWeight,
           let participantTargetWeight = plan.participantTargetWeight,
           let participantWeightLoss = plan.participantTargetWeightLoss {
            participantGoalLabel.text = "\(String(format: "%.1f", participantInitialWeight))kg → \(String(format: "%.1f", participantTargetWeight))kg (减重\(String(format: "%.1f", participantWeightLoss))kg)"
        } else {
            participantGoalLabel.text = "待设置"
        }
        
        // Description
        descriptionLabel.text = plan.description ?? "无描述"
    }
    
    // MARK: - Button Display Methods
    
    private func showCancelOnly() {
        actionButtonsView.isHidden = false
        acceptPlanFormView.isHidden = true
        
        cancelButton.isHidden = true
        rejectButton.isHidden = true
        acceptButton.isHidden = true
        confirmButton.isHidden = true
        checkInButton.isHidden = true
        giveUpButton.isHidden = false
        giveUpButton.setTitle("放弃计划", for: .normal)
        giveUpButton.tintColor = .systemRed
    }
    
    private func showAcceptRejectForm() {
        actionButtonsView.isHidden = false
        acceptPlanFormView.isHidden = false
        
        cancelButton.isHidden = true
        rejectButton.isHidden = false
        acceptButton.isHidden = false
        confirmButton.isHidden = true
        checkInButton.isHidden = true
        giveUpButton.isHidden = true  // 待接受状态不显示放弃按钮
    }
    
    private func showCancelConfirmButtons() {
        actionButtonsView.isHidden = false
        acceptPlanFormView.isHidden = true
        
        cancelButton.isHidden = false
        rejectButton.isHidden = true
        acceptButton.isHidden = true
        confirmButton.isHidden = false
        checkInButton.isHidden = true
        giveUpButton.isHidden = true
    }
    
    private func showWaitingForConfirmation() {
        actionButtonsView.isHidden = true
        acceptPlanFormView.isHidden = true
    }
    
    private func showCheckInGiveUpButtons() {
        actionButtonsView.isHidden = false
        acceptPlanFormView.isHidden = true
        
        cancelButton.isHidden = true
        rejectButton.isHidden = true
        acceptButton.isHidden = true
        confirmButton.isHidden = true
        checkInButton.isHidden = false
        giveUpButton.isHidden = false
    }
    
    private func hideAllButtons() {
        actionButtonsView.isHidden = true
        acceptPlanFormView.isHidden = true
    }
    
    // MARK: - Actions
    
    @objc private func cancelTapped() {
        let alert = UIAlertController(title: "确认", message: "确定要取消这个计划吗？取消后赌金将全额返还。", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        alert.addAction(UIAlertAction(title: "确定", style: .destructive) { [weak self] _ in
            self?.viewModel.cancelPlan()
        })
        present(alert, animated: true)
    }
    
    @objc private func rejectTapped() {
        let alert = UIAlertController(title: "确认", message: "确定要拒绝这个计划吗？", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        alert.addAction(UIAlertAction(title: "确定", style: .destructive) { [weak self] _ in
            self?.viewModel.rejectPlan()
        })
        present(alert, animated: true)
    }
    
    @objc private func acceptTapped() {
        guard let initialWeight = initialWeightTextField.text, !initialWeight.isEmpty else {
            showError("请输入初始体重")
            return
        }
        
        guard let targetWeight = targetWeightTextField.text, !targetWeight.isEmpty else {
            showError("请输入目标体重")
            return
        }
        
        // 保存待提交的体重，用于充值成功后重试
        pendingInitialWeight = initialWeight
        pendingTargetWeight = targetWeight
        
        // 第一步：预校验余额，不足直接弹充值
        showLoading()
        Task {
            guard let userId = AuthRepository.shared.getCurrentUserId() else {
                // 用户ID获取失败，直接提交
                await MainActor.run {
                    self.hideLoading()
                    self.viewModel.acceptPlan(initialWeight: initialWeight, targetWeight: targetWeight)
                }
                return
            }
            
            let result = await PaymentRepository.shared.getBalance(userId: userId, forceRefresh: true)
            await MainActor.run {
                self.hideLoading()
                
                guard case .success(let balance) = result, let plan = self.viewModel.plan else {
                    // 余额查询失败，直接提交
                    self.viewModel.acceptPlan(initialWeight: initialWeight, targetWeight: targetWeight)
                    return
                }
                
                let requiredAmount = plan.betAmount
                if balance.availableBalance < requiredAmount {
                    // 余额不足，直接弹充值
                    let alert = UIAlertController(
                        title: "余额不足",
                        message: "您的账户余额不足，需要充值¥\(String(format: "%.2f", requiredAmount))元才能参与该计划",
                        preferredStyle: .alert
                    )
                    alert.addAction(UIAlertAction(title: "取消", style: .cancel))
                    alert.addAction(UIAlertAction(title: "立即充值", style: .default) { [weak self] _ in
                        guard let self = self else { return }
                        // 跳转到充值页面
                        let chargeVC = ChargeViewController()
                        chargeVC.preFillAmount(requiredAmount)
                        chargeVC.lockAmount = true
                        chargeVC.onChargeSuccess = { [weak self] in
                            guard let self = self,
                                  let initialWeight = self.pendingInitialWeight,
                                  let targetWeight = self.pendingTargetWeight else { return }
                            // 充值成功后自动返回并重试接受计划
                            DispatchQueue.main.async {
                                self.dismiss(animated: true) {
                                    self.viewModel.acceptPlan(initialWeight: initialWeight, targetWeight: targetWeight)
                                }
                            }
                        }
                        let nav = UINavigationController(rootViewController: chargeVC)
                        self.present(nav, animated: true)
                    })
                    self.present(alert, animated: true)
                    return
                }
                
                // 余额足够，正常提交
                self.viewModel.acceptPlan(initialWeight: initialWeight, targetWeight: targetWeight)
            }
        }
    }
    
    @objc private func confirmTapped() {
        let alert = UIAlertController(title: "确认", message: "对方已接受并缴纳赌金，确认开始这个计划吗？", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "再想想", style: .cancel))
        alert.addAction(UIAlertAction(title: "确认开始", style: .default) { [weak self] _ in
            self?.viewModel.confirmPlan()
        })
        present(alert, animated: true)
    }
    
    @objc private func checkInTapped() {
        guard let planId = viewModel.plan?.id else { return }
        let checkInVC = CheckInViewController(planId: planId)
        navigationController?.pushViewController(checkInVC, animated: true)
    }
    
    @objc private func giveUpTapped() {
        guard let plan = viewModel.plan else { return }
        
        let alert = UIAlertController(title: "确认放弃计划？", message: "", preferredStyle: .alert)
        
        // 根据状态生成提示文案
        let betAmount = plan.betAmount
        var message = ""
        if plan.status == .pending {
            message = "放弃后将退还您的赌金 ¥\(String(format: "%.2f", betAmount))"
        } else if plan.status == .active {
            message = "放弃后您将失去赌金 ¥\(String(format: "%.2f", betAmount))，对方将获得全部赌金 ¥\(String(format: "%.2f", betAmount * 2))"
        }
        
        // 添加提示文本
        let messageLabel = UILabel()
        messageLabel.text = message
        messageLabel.numberOfLines = 0
        messageLabel.textAlignment = .center
        messageLabel.font = .systemFont(ofSize: 14)
        if plan.status == .active {
            messageLabel.textColor = .systemRed
        }
        
        // 添加复选框
        let confirmSwitch = UISwitch()
        confirmSwitch.isOn = false
        
        let confirmLabel = UILabel()
        confirmLabel.text = "我已了解后果"
        confirmLabel.font = .systemFont(ofSize: 14)
        
        let switchContainer = UIStackView(arrangedSubviews: [
            confirmLabel,
            confirmSwitch
        ])
        switchContainer.axis = .horizontal
        switchContainer.spacing = 8
        switchContainer.alignment = .center
        
        // 自定义contentView
        let stackView = UIStackView(arrangedSubviews: [messageLabel, switchContainer])
        stackView.axis = .vertical
        stackView.spacing = 16
        stackView.translatesAutoresizingMaskIntoConstraints = false
        
        alert.view.addSubview(stackView)
        
        NSLayoutConstraint.activate([
            stackView.topAnchor.constraint(equalTo: alert.view.topAnchor, constant: 50),
            stackView.leadingAnchor.constraint(equalTo: alert.view.leadingAnchor, constant: 16),
            stackView.trailingAnchor.constraint(equalTo: alert.view.trailingAnchor, constant: -16),
            stackView.bottomAnchor.constraint(equalTo: alert.view.bottomAnchor, constant: -80)
        ])
        
        alert.view.heightAnchor.constraint(equalToConstant: 200).isActive = true
        
        // 取消按钮
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        
        // 确认按钮
        let confirmAction = UIAlertAction(title: "确认放弃", style: .destructive) { [weak self] _ in
            self?.viewModel.abandonPlan(confirmation: true)
        }
        confirmAction.isEnabled = false
        alert.addAction(confirmAction)
        
        // 监听开关状态
        confirmSwitch.addTarget(self, action: #selector(abandonSwitchToggled(_:)), for: .valueChanged)
        objc_setAssociatedObject(alert, &AssociatedKeys.confirmActionKey, confirmAction, .OBJC_ASSOCIATION_RETAIN_NONATOMIC)
        
        present(alert, animated: true)
    }
    
    @objc private func abandonSwitchToggled(_ sender: UISwitch) {
        // 获取alert里的确认按钮
        guard let alert = presentedViewController as? UIAlertController,
              let confirmAction = objc_getAssociatedObject(alert, &AssociatedKeys.confirmActionKey) as? UIAlertAction else { return }
        confirmAction.isEnabled = sender.isOn
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

// MARK: - Associated Keys
private enum AssociatedKeys {
    static var confirmActionKey = "confirmActionKey"
}
