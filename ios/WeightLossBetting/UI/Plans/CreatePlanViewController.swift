import UIKit

class CreatePlanViewController: UIViewController {
    
    // MARK: - Properties
    
    private let viewModel = CreatePlanViewModel()
    private var betAmountTextField: UITextField!
    private var startDateTextField: UITextField!
    private var endDateTextField: UITextField!
    private var initialWeightTextField: UITextField!
    private var targetWeightTextField: UITextField!
    private var descriptionTextView: UITextView!
    private var createButton: UIButton!
    private var loadingIndicator: UIActivityIndicatorView!
    private var scrollView: UIScrollView!

    private var datePicker: UIDatePicker!
    private var startDate: Date?
    private var endDate: Date?
    private var isSelectingStartDate = true

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
        
        let contentView = UIView()
        contentView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.addSubview(contentView)
        
        // Bet amount
        let betAmountLabel = createLabel(text: "赌金金额 (¥)")
        betAmountTextField = createTextField(placeholder: "请输入赌金金额", keyboardType: .decimalPad)
        
        // Date range - two text fields with date picker
        let dateRangeLabel = createLabel(text: "计划周期")
        
        // Start date field
        let startDateLabel = createLabel(text: "开始日期")
        startDateTextField = createTextField(placeholder: "请选择开始日期")
        
        // End date field
        let endDateLabel = createLabel(text: "结束日期")
        endDateTextField = createTextField(placeholder: "请先选择开始日期")
        
        // Setup date picker
        datePicker = UIDatePicker()
        datePicker.datePickerMode = .date
        datePicker.preferredDatePickerStyle = .wheels
        datePicker.minimumDate = Date() // 只能选择今天及以后的日期
        datePicker.translatesAutoresizingMaskIntoConstraints = false
        
        // Add toolbar with done button
        let toolbar = UIToolbar()
        toolbar.sizeToFit()
        toolbar.setItems([
            UIBarButtonItem(barButtonSystemItem: .flexibleSpace, target: nil, action: nil),
            UIBarButtonItem(title: "确定", style: .done, target: self, action: #selector(datePickerDoneTapped))
        ], animated: false)
        
        // Initially show start date picker
        startDateTextField.inputView = datePicker
        startDateTextField.inputAccessoryView = toolbar
        endDateTextField.inputView = datePicker
        endDateTextField.inputAccessoryView = toolbar
        
        // Add tap gestures to handle date selection
        let startTapGesture = UITapGestureRecognizer(target: self, action: #selector(startDateFieldTapped))
        startDateTextField.addGestureRecognizer(startTapGesture)
        
        let endTapGesture = UITapGestureRecognizer(target: self, action: #selector(endDateFieldTapped))
        endDateTextField.addGestureRecognizer(endTapGesture)
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
         dateRangeLabel, startDateLabel, startDateTextField,
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
            
            dateRangeLabel.topAnchor.constraint(equalTo: betAmountTextField.bottomAnchor, constant: 20),
            dateRangeLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            dateRangeLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            startDateLabel.topAnchor.constraint(equalTo: dateRangeLabel.bottomAnchor, constant: 16),
            startDateLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            
            startDateTextField.topAnchor.constraint(equalTo: startDateLabel.bottomAnchor, constant: 8),
            startDateTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            startDateTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            startDateTextField.heightAnchor.constraint(equalToConstant: 44),
            
            endDateLabel.topAnchor.constraint(equalTo: startDateTextField.bottomAnchor, constant: 16),
            endDateLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            
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
            self?.handlePlanCreated(plan: plan)
        }
        
        viewModel.onError = { [weak self] message in
            self?.showError(message)
        }
        
        // Handle insufficient balance - navigate to charge page
        viewModel.onInsufficientBalance = { [weak self] amountNeeded in
            self?.handleInsufficientBalance(amountNeeded: amountNeeded)
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
    
    @objc private func datePickerDoneTapped() {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        
        if isSelectingStartDate {
            startDate = datePicker.date
            startDateTextField.text = formatter.string(from: datePicker.date)
            
            // Enable end date field and switch to it
            endDateTextField.isEnabled = true
            endDateTextField.placeholder = "请选择结束日期"
            isSelectingStartDate = false
            
            // Update date picker minimum date to start date + 1 day
            if let startDate = startDate {
                let nextDay = Calendar.current.date(byAdding: .day, value: 1, to: startDate) ?? Date()
                datePicker.minimumDate = nextDay
                datePicker.setDate(nextDay, animated: true)
                endDate = nil
            }
            
            // Focus end date field
            endDateTextField.becomeFirstResponder()
        } else {
            endDate = datePicker.date
            endDateTextField.text = formatter.string(from: datePicker.date)
            view.endEditing(true)
        }
    }
    
    @objc private func startDateFieldTapped() {
        guard !startDateTextField.isFirstResponder else { return }
        
        isSelectingStartDate = true
        datePicker.minimumDate = Date() // Reset to today
        if let startDate = startDate {
            datePicker.setDate(startDate, animated: false)
        }
        
        startDateTextField.becomeFirstResponder()
    }
    
    @objc private func endDateFieldTapped() {
        guard !endDateTextField.isFirstResponder else { return }
        guard startDate != nil else {
            // If start date not selected, focus start date
            startDateFieldTapped()
            return
        }
        
        isSelectingStartDate = false
        if let endDate = endDate {
            datePicker.setDate(endDate, animated: false)
        } else if let startDate = startDate {
            let nextDay = Calendar.current.date(byAdding: .day, value: 1, to: startDate) ?? Date()
            datePicker.minimumDate = nextDay
            datePicker.setDate(nextDay, animated: false)
        }
        
        endDateTextField.becomeFirstResponder()
    }
    
    @objc private func cancelTapped() {
        // Try to pop from navigation stack first, fallback to dismiss
        if let nav = navigationController, nav.viewControllers.count > 1 {
            navigationController?.popViewController(animated: true)
        } else {
            dismiss(animated: true)
        }
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
        
        // ✅ 新流程：先验证余额，再邀请好友，最后创建计划
        print("💰 [CreatePlanVC] 开始验证余额...")
        
        // 使用 Task 调用异步方法
        Task {
            await checkBalanceAndProceed(
                betAmount: betAmount,
                startDate: startDate,
                endDate: endDate,
                initialWeight: initialWeight,
                targetWeight: targetWeight,
                description: description.isEmpty ? nil : description
            )
        }
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
    
    /// 验证余额并根据结果执行下一步
    private func checkBalanceAndProceed(
        betAmount: String,
        startDate: Date,
        endDate: Date,
        initialWeight: String,
        targetWeight: String,
        description: String?
    ) async {
        print("💰 [CreatePlanVC] 开始验证余额...")
        
        // 获取当前用户余额
        guard let userId = AuthRepository.shared.getCurrentUserId() else {
            await MainActor.run {
                self.showError("无法获取用户信息")
            }
            return
        }
        
        var currentBalance: Double? = nil
        
        // 先尝试从缓存获取余额
        if let cached: Balance = CacheManager.shared.get(forKey: "balance_\(userId)") {
            currentBalance = cached.availableBalance
            print("💰 [CreatePlanVC] 从缓存获取到余额：¥\(currentBalance ?? 0)")
        }
        
        // 如果缓存不存在或已过期，调用后端 API 获取
        if currentBalance == nil {
            print("📡 [CreatePlanVC] 缓存不存在，调用后端 API 获取余额...")
            do {
                let result = try await PaymentRepository().getBalance(userId: userId, forceRefresh: true)
                switch result {
                case .success(let balance):
                    currentBalance = balance.availableBalance
                    print("💰 [CreatePlanVC] 从后端获取到余额：¥\(balance.availableBalance)")
                case .failure(let error):
                    print("❌ [CreatePlanVC] 获取余额失败：\(error.localizedDescription)")
                    await MainActor.run {
                        self.showError("获取余额失败，请重试")
                    }
                    return
                case .loading:
                    break
                }
            } catch {
                print("❌ [CreatePlanVC] 获取余额异常：\(error.localizedDescription)")
                await MainActor.run {
                    self.showError("获取余额失败，请重试")
                }
                return
            }
        }
        
        let balanceValue = currentBalance ?? 0.0
        let betAmountValue = Double(betAmount) ?? 0.0
        
        print("💵 [CreatePlanVC] 当前余额：¥\(balanceValue), 需要赌金：¥\(betAmountValue)")
        
        await MainActor.run {
            if balanceValue >= betAmountValue {
                // ✅ 余额充足，进入邀请好友流程
                print("✅ [CreatePlanVC] 余额充足，进入邀请好友流程")
                self.showInvitePage(
                    betAmount: betAmount,
                    startDate: startDate,
                    endDate: endDate,
                    initialWeight: initialWeight,
                    targetWeight: targetWeight,
                    description: description
                )
            } else {
                // ❌ 余额不足，需要充值
                let amountNeeded = betAmountValue - balanceValue
                print("❌ [CreatePlanVC] 余额不足，需要充值：¥\(amountNeeded)")
                self.handleInsufficientBalance(amountNeeded: amountNeeded)
            }
        }
    }
    
    /// 显示邀请好友页面
    private func showInvitePage(
        betAmount: String,
        startDate: Date,
        endDate: Date,
        initialWeight: String,
        targetWeight: String,
        description: String?
    ) {
        print("👥 [CreatePlanVC] 打开邀请好友页面...")
        
        let inviteVC = InviteViewController(onInviteSelected: { [weak self] inviteeId in
            guard let self = self else { return }
            // 用户已选择邀请对象，创建计划
            print("✅ [CreatePlanVC] 用户已选择邀请对象，开始创建计划...")
            self.viewModel.createPlan(
                betAmount: betAmount,
                startDate: startDate,
                endDate: endDate,
                initialWeight: initialWeight,
                targetWeight: targetWeight,
                description: description,
                inviteeId: inviteeId
            )
        })
        let nav = UINavigationController(rootViewController: inviteVC)
        present(nav, animated: true)
    }
    
    private func handleInsufficientBalance(amountNeeded: Double) {
        print("💰 [CreatePlanVC] 余额不足，需要充值：¥\(amountNeeded)")
        
        // 显示 Toast 浮窗提示
        showToast(message: "余额不足，正在跳转到充值页面...")
        
        // 延迟 0.5 秒后自动跳转到充值页面，并传入创建计划的参数
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            print("🔄 [CreatePlanVC] 开始跳转到充值页面...")
            // 从实例变量中获取参数
            let betAmount = self?.betAmountTextField.text ?? "0"
            let startDate = self?.startDate
            let endDate = self?.endDate
            let initialWeight = self?.initialWeightTextField.text ?? "0"
            let targetWeight = self?.targetWeightTextField.text ?? "0"
            let descriptionText = self?.descriptionTextView.text.trimmingCharacters(in: .whitespacesAndNewlines) ?? ""
            
            self?.navigateToChargePage(
                amount: amountNeeded,
                betAmount: betAmount,
                startDate: startDate,
                endDate: endDate,
                initialWeight: initialWeight,
                targetWeight: targetWeight,
                description: descriptionText.isEmpty ? nil : descriptionText
            )
        }
    }
    
    private func navigateToChargePage(amount: Double, betAmount: String? = nil, startDate: Date? = nil, endDate: Date? = nil, initialWeight: String? = nil, targetWeight: String? = nil, description: String? = nil) {
        print("🚀 [CreatePlanVC] 模态弹出充值页面，金额=¥\(amount)")
        
        // 直接模态弹出充值页面，不切换到 Payment tab
        let chargeVC = ChargeViewController()
        chargeVC.preFillAmount(amount)
        
        // 设置充值成功回调：返回后进入邀请好友流程
        chargeVC.onChargeSuccess = { [weak self] in
            print("✅ [CreatePlanVC] 充值成功回调，准备进入邀请好友流程")
            // 充值成功后，清除缓存
            CacheManager.shared.invalidateAllCache()
            
            // 如果提供了创建计划的参数，直接进入邀请流程
            if let betAmount = betAmount,
               let startDate = startDate,
               let endDate = endDate,
               let initialWeight = initialWeight,
               let targetWeight = targetWeight {
                print("✅ [CreatePlanVC] 充值成功，进入邀请好友流程")
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    self?.showInvitePage(
                        betAmount: betAmount,
                        startDate: startDate,
                        endDate: endDate,
                        initialWeight: initialWeight,
                        targetWeight: targetWeight,
                        description: description
                    )
                }
            }
        }
        
        // 包装在导航控制器中
        let navController = UINavigationController(rootViewController: chargeVC)
        present(navController, animated: true)
        print("✅ [CreatePlanVC] 充值页面已显示")
    }
    
    private func showSuccess() {
        // Deprecated: creation no longer directly presents Invite page
    }

    private func handlePlanCreated(plan: BettingPlan) {
        // Called when createPlan succeeded
        showToast(message: "计划创建成功", duration: 1.0)
        // Close CreatePlanViewController and navigate to plan detail
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
            guard let self = self else { return }
            // Dismiss create VC then navigate to detail
            if let nav = self.navigationController, nav.viewControllers.count > 1 {
                // If pushed, pop to previous then push detail
                self.navigationController?.popViewController(animated: false)
            } else {
                self.dismiss(animated: true, completion: nil)
            }
            // Navigate to plan detail via main navigation
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                if let sceneDelegate = UIApplication.shared.connectedScenes.first?.delegate as? SceneDelegate,
                   let window = sceneDelegate.window,
                   let rootViewController = window.rootViewController {
                    if let mainNav = rootViewController as? UINavigationController {
                        let planDetailVC = PlanDetailViewController(planId: plan.id)
                        mainNav.pushViewController(planDetailVC, animated: true)
                    } else if let tabBar = rootViewController as? UITabBarController,
                              let mainNav = tabBar.selectedViewController as? UINavigationController {
                        let planDetailVC = PlanDetailViewController(planId: plan.id)
                        mainNav.pushViewController(planDetailVC, animated: true)
                    } else {
                        print("❌ [CreatePlanVC] 无法找到主导航控制器来推送计划详情")
                    }
                }
            }
        }
    }
    
    // MARK: - Private Methods
    
    /// 执行创建计划
    private func proceedCreatePlan(
        betAmount: String,
        startDate: Date,
        endDate: Date,
        initialWeight: String,
        targetWeight: String,
        description: String?
    ) {
        viewModel.createPlan(
            betAmount: betAmount,
            startDate: startDate,
            endDate: endDate,
            initialWeight: initialWeight,
            targetWeight: targetWeight,
            description: description
        )
    }
    
    private func showError(_ message: String) {
        // 对于余额不足的错误，使用 Toast 浮窗并自动跳转
        if message.contains("余额不足") || message.contains("请先充值") {
            // Extract amount from message if possible
            let pattern = "\\d+\\.?\\d*"
            var amount: Double? = nil
            if let range = message.range(of: pattern, options: .regularExpression),
               let extractedAmount = Double(message[range]) {
                amount = extractedAmount
            }
            
            showToast(message: "余额不足，正在跳转到充值页面...")
            
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) { [weak self] in
                self?.navigateToChargePage(amount: amount ?? 200.0)
            }
        } else {
            // 其他错误也使用 Toast 提示，不需要用户点击确认
            showToast(message: message)
        }
    }
    
    private func showToast(message: String, duration: TimeInterval = 2.0) {
        guard Thread.isMainThread else {
            DispatchQueue.main.async { self.showToast(message: message, duration: duration) }
            return
        }
        
        // 移除旧的 toast
        view.viewWithTag(999)?.removeFromSuperview()
        
        // 创建 Toast 视图
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
        
        // 自动消失
        DispatchQueue.main.asyncAfter(deadline: .now() + duration) {
            toastView.removeFromSuperview()
        }
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}
