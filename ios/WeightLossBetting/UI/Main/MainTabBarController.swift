import UIKit

class MainTabBarController: UITabBarController {
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupTabBar()
        setupViewControllers()
        
        // 全局监听导航通知，避免弹窗通知丢失
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleNavigationNotification(_:)),
            name: NSNotification.Name(rawValue: "navigateToNotificationType"),
            object: nil
        )
    }
    
    // MARK: - Global Notification Navigation
    @objc private func handleNavigationNotification(_ note: Notification) {
        print("🔵 [MainTabBar] 收到全局导航通知：\(note.name.rawValue)")
        guard let userInfo = note.userInfo as? [String: Any],
              let type = userInfo["type"] as? String,
              let planId = userInfo["relatedId"] as? String,
              !planId.isEmpty else {
            print("❌ [MainTabBar] 通知信息格式不正确")
            return
        }
        print("   - 类型：\(type), planId: \(planId)")
        
        // 处理计划相关通知，跳转到计划详情
        if ["invite", "double_check", "plan_active", "settlement"].contains(type) {
            print("🚀 [MainTabBar] 开始导航到计划详情：\(planId)")
            DispatchQueue.main.async { [weak self] in
                guard let self = self else { return }
                // 容错方案1：切到计划tab正常跳转
                self.selectedIndex = 2
                if let plansNav = self.viewControllers?[2] as? UINavigationController {
                    plansNav.popToRootViewController(animated: false)
                    let detailVC = PlanDetailViewController(planId: planId)
                    plansNav.pushViewController(detailVC, animated: true)
                    print("✅ [MainTabBar] 方案1导航成功")
                    return
                }
                
                // 容错方案2：找最顶层的导航控制器直接push
                if let topNav = UIApplication.shared.keyWindow?.rootViewController as? UINavigationController ?? UIApplication.shared.keyWindow?.rootViewController?.navigationController {
                    let detailVC = PlanDetailViewController(planId: planId)
                    topNav.pushViewController(detailVC, animated: true)
                    print("✅ [MainTabBar] 方案2导航成功")
                    return
                }
                
                // 容错方案3：直接present详情页
                let detailVC = PlanDetailViewController(planId: planId)
                let nav = UINavigationController(rootViewController: detailVC)
                self.present(nav, animated: true)
                print("✅ [MainTabBar] 方案3导航成功")
            }
        }
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self)
    }
    
    // MARK: - Setup
    
    private func setupTabBar() {
        tabBar.tintColor = .systemBlue
        tabBar.unselectedItemTintColor = .systemGray
        tabBar.backgroundColor = .systemBackground
        
        // Add shadow
        tabBar.layer.shadowColor = UIColor.black.cgColor
        tabBar.layer.shadowOpacity = 0.1
        tabBar.layer.shadowOffset = CGSize(width: 0, height: -2)
        tabBar.layer.shadowRadius = 4
    }
    
    private func setupViewControllers() {
        // Home Tab
        let homeVC = HomeViewController()
        let homeNav = UINavigationController(rootViewController: homeVC)
        homeNav.tabBarItem = UITabBarItem(
            title: "首页",
            image: UIImage(systemName: "house"),
            selectedImage: UIImage(systemName: "house.fill")
        )
        
        // Coach Tab
        let coachVC = CoachViewController()
        let coachNav = UINavigationController(rootViewController: coachVC)
        coachNav.tabBarItem = UITabBarItem(
            title: "管家",
            image: UIImage(systemName: "heart.fill"),
            selectedImage: UIImage(systemName: "heart.fill")
        )
        
        // Plans Tab
        let plansVC = PlansViewController()
        let plansNav = UINavigationController(rootViewController: plansVC)
        plansNav.tabBarItem = UITabBarItem(
            title: "计划",
            image: UIImage(systemName: "list.bullet"),
            selectedImage: UIImage(systemName: "list.bullet")
        )
        
        // Profile Tab
        let profileVC = ProfileViewController()
        let profileNav = UINavigationController(rootViewController: profileVC)
        profileNav.tabBarItem = UITabBarItem(
            title: "我的",
            image: UIImage(systemName: "person"),
            selectedImage: UIImage(systemName: "person.fill")
        )
        
        viewControllers = [homeNav, coachNav, plansNav, profileNav]
    }
}

// MARK: - HomeViewController

class HomeViewController: UIViewController {
    
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
    
    private let welcomeLabel: UILabel = {
        let label = UILabel()
        label.text = "欢迎来到减肥对赌"
        label.font = .boldSystemFont(ofSize: 24)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let subtitleLabel: UILabel = {
        let label = UILabel()
        label.text = "和朋友一起挑战减肥目标"
        label.font = .systemFont(ofSize: 16)
        label.textColor = .secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let quickActionsStackView: UIStackView = {
        let stack = UIStackView()
        stack.axis = .vertical
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false
        return stack
    }()
    
    // 新增：统计卡片
    private let statsCardView: UIView = {
        let view = UIView()
        view.backgroundColor = UIColor.systemBlue.withAlphaComponent(0.1)
        view.layer.cornerRadius = 12
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private let checkInStatsLabel: UILabel = {
        let label = UILabel()
        label.text = "今日打卡：--"
        label.font = .systemFont(ofSize: 15, weight: .medium)
        label.textColor = .label
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let balanceStatsLabel: UILabel = {
        let label = UILabel()
        label.text = "钱包余额：¥--"
        label.font = .systemFont(ofSize: 15, weight: .medium)
        label.textColor = .label
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let refreshButton: UIButton = {
        let button = UIButton(type: .system)
        button.setImage(UIImage(systemName: "arrow.clockwise"), for: .normal)
        button.tintColor = .systemBlue
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupQuickActions()
        setupStatsCard()
        loadStats()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        title = "首页"
        view.backgroundColor = .systemBackground
        
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        contentView.addSubview(welcomeLabel)
        contentView.addSubview(subtitleLabel)
        contentView.addSubview(statsCardView)
        contentView.addSubview(quickActionsStackView)
        
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
            
            welcomeLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 24),
            welcomeLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            welcomeLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            subtitleLabel.topAnchor.constraint(equalTo: welcomeLabel.bottomAnchor, constant: 8),
            subtitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            subtitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            // 统计卡片在副标题下方
            statsCardView.topAnchor.constraint(equalTo: subtitleLabel.bottomAnchor, constant: 16),
            statsCardView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            statsCardView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            statsCardView.heightAnchor.constraint(equalToConstant: 90),
            
            // 快速操作在统计卡片下方
            quickActionsStackView.topAnchor.constraint(equalTo: statsCardView.bottomAnchor, constant: 24),
            quickActionsStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            quickActionsStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            quickActionsStackView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -24)
        ])
    }
    
    private func setupStatsCard() {
        // 统计卡片的子视图添加和内部布局
        statsCardView.addSubview(checkInStatsLabel)
        statsCardView.addSubview(balanceStatsLabel)
        statsCardView.addSubview(refreshButton)
        
        NSLayoutConstraint.activate([
            checkInStatsLabel.topAnchor.constraint(equalTo: statsCardView.topAnchor, constant: 16),
            checkInStatsLabel.leadingAnchor.constraint(equalTo: statsCardView.leadingAnchor, constant: 16),
            
            balanceStatsLabel.topAnchor.constraint(equalTo: checkInStatsLabel.bottomAnchor, constant: 12),
            balanceStatsLabel.leadingAnchor.constraint(equalTo: statsCardView.leadingAnchor, constant: 16),
            balanceStatsLabel.bottomAnchor.constraint(equalTo: statsCardView.bottomAnchor, constant: -16),
            
            refreshButton.topAnchor.constraint(equalTo: statsCardView.topAnchor, constant: 12),
            refreshButton.trailingAnchor.constraint(equalTo: statsCardView.trailingAnchor, constant: -12),
            refreshButton.widthAnchor.constraint(equalToConstant: 32),
            refreshButton.heightAnchor.constraint(equalToConstant: 32)
        ])
        
        refreshButton.addTarget(self, action: #selector(refreshStatsTapped), for: .touchUpInside)
    }
    
    private func loadStats() {
        guard let userId = UserDefaults.standard.string(forKey: "currentUserId") else {
            return
        }
        
        // 加载打卡统计
        loadCheckInStats(userId: userId)
        
        // 加载钱包余额
        loadBalance(userId: userId)
    }
    
    private func loadCheckInStats(userId: String) {
        APIService.shared.getUserBettingPlans(userId: userId, status: "active") { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let plans):
                    let today = Date()
                    let dateFormatter = DateFormatter()
                    dateFormatter.dateFormat = "yyyy-MM-dd"
                    let todayString = dateFormatter.string(from: today)
                    
                    var checkedInCount = 0
                    
                    let group = DispatchGroup()
                    
                    for plan in plans {
                        group.enter()
                        APIService.shared.getCheckInHistory(planId: plan.id, userId: userId) { checkInResult in
                            if case .success(let checkIns) = checkInResult {
                                let checkedInToday = checkIns.contains { checkIn in
                                    let checkInDateStr = dateFormatter.string(from: checkIn.checkInDate)
                                    return checkInDateStr == todayString && checkIn.userId == userId
                                }
                                if checkedInToday {
                                    checkedInCount += 1
                                }
                            }
                            group.leave()
                        }
                    }
                    
                    group.notify(queue: .main) {
                        self?.checkInStatsLabel.text = "今日打卡：\(checkedInCount)/\(plans.count)"
                    }
                    
                case .failure:
                    self?.checkInStatsLabel.text = "今日打卡：--"
                }
            }
        }
    }
    
    private func loadBalance(userId: String) {
        APIService.shared.getBalance(userId: userId) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let balance):
                    self?.balanceStatsLabel.text = String(format: "钱包余额：¥%.2f", balance.availableBalance)
                case .failure:
                    self?.balanceStatsLabel.text = "钱包余额：--"
                }
            }
        }
    }
    
    @objc private func refreshStatsTapped() {
        loadStats()
    }
    
    private func setupQuickActions() {
        let actions: [(title: String, subtitle: String, icon: String, action: Selector)] = [
            ("创建计划", "发起新的减肥挑战", "plus.circle.fill", #selector(createPlanTapped)),
            ("我的计划", "查看所有对赌计划", "list.bullet", #selector(myPlansTapped)),
            ("打卡", "记录今天的体重", "checkmark.circle.fill", #selector(checkInTapped))
            // 隐藏：我的勋章功能
            // ("我的勋章", "查看获得的成就", "star.fill", #selector(badgesTapped))
        ]
        
        for action in actions {
            let button = createQuickActionButton(
                title: action.title,
                subtitle: action.subtitle,
                icon: action.icon,
                action: action.action
            )
            quickActionsStackView.addArrangedSubview(button)
        }
    }
    
    private func createQuickActionButton(title: String, subtitle: String, icon: String, action: Selector) -> UIButton {
        let button = UIButton(type: .system)
        button.backgroundColor = .secondarySystemBackground
        button.layer.cornerRadius = 12
        button.contentHorizontalAlignment = .left
        button.addTarget(self, action: action, for: .touchUpInside)
        
        let iconImageView = UIImageView(image: UIImage(systemName: icon))
        iconImageView.tintColor = .systemBlue
        iconImageView.contentMode = .scaleAspectFit
        iconImageView.translatesAutoresizingMaskIntoConstraints = false
        
        let titleLabel = UILabel()
        titleLabel.text = title
        titleLabel.font = .boldSystemFont(ofSize: 16)
        titleLabel.translatesAutoresizingMaskIntoConstraints = false
        
        let subtitleLabel = UILabel()
        subtitleLabel.text = subtitle
        subtitleLabel.font = .systemFont(ofSize: 14)
        subtitleLabel.textColor = .secondaryLabel
        subtitleLabel.translatesAutoresizingMaskIntoConstraints = false
        
        let chevronImageView = UIImageView(image: UIImage(systemName: "chevron.right"))
        chevronImageView.tintColor = .tertiaryLabel
        chevronImageView.contentMode = .scaleAspectFit
        chevronImageView.translatesAutoresizingMaskIntoConstraints = false
        
        button.addSubview(iconImageView)
        button.addSubview(titleLabel)
        button.addSubview(subtitleLabel)
        button.addSubview(chevronImageView)
        
        NSLayoutConstraint.activate([
            button.heightAnchor.constraint(equalToConstant: 80),
            
            iconImageView.leadingAnchor.constraint(equalTo: button.leadingAnchor, constant: 16),
            iconImageView.centerYAnchor.constraint(equalTo: button.centerYAnchor),
            iconImageView.widthAnchor.constraint(equalToConstant: 32),
            iconImageView.heightAnchor.constraint(equalToConstant: 32),
            
            titleLabel.leadingAnchor.constraint(equalTo: iconImageView.trailingAnchor, constant: 16),
            titleLabel.topAnchor.constraint(equalTo: button.topAnchor, constant: 20),
            
            subtitleLabel.leadingAnchor.constraint(equalTo: iconImageView.trailingAnchor, constant: 16),
            subtitleLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 4),
            
            chevronImageView.trailingAnchor.constraint(equalTo: button.trailingAnchor, constant: -16),
            chevronImageView.centerYAnchor.constraint(equalTo: button.centerYAnchor),
            chevronImageView.widthAnchor.constraint(equalToConstant: 12),
            chevronImageView.heightAnchor.constraint(equalToConstant: 20)
        ])
        
        return button
    }
    
    // MARK: - Actions
    
    @objc private func createPlanTapped() {
        let createPlanVC = CreatePlanViewController()
        navigationController?.pushViewController(createPlanVC, animated: true)
    }
    
    @objc private func myPlansTapped() {
        tabBarController?.selectedIndex = 2 // Switch to Plans tab (index 2)
    }
    
    @objc private func checkInTapped() {
        // Get active plans and auto-select for check-in
        guard let userId = UserDefaults.standard.string(forKey: "currentUserId") else {
            showAlert(message: "请先登录")
            return
        }
        
        // Fetch active plans from API
        APIService.shared.getUserBettingPlans(userId: userId, status: "active") { [weak self] result in
            DispatchQueue.main.async {
                guard let self = self else { return }
                
                switch result {
                case .success(let plans):
                    if plans.isEmpty {
                        self.showAlert(message: "您当前没有进行中的计划，请先创建一个计划或接受邀请")
                        return
                    }
                    
                    // Check if user has already checked in today
                    let today = Date()
                    let dateFormatter = DateFormatter()
                    dateFormatter.dateFormat = "yyyy-MM-dd"
                    let todayString = dateFormatter.string(from: today)
                    
                    // Check all plans for today's check-in
                    var alreadyCheckedInPlanIds: [String] = []
                    
                    for plan in plans {
                        // Check if already checked in today for this plan
                        APIService.shared.getCheckInHistory(planId: plan.id, userId: userId) { checkInResult in
                            if case .success(let checkIns) = checkInResult {
                                let checkedInToday = checkIns.contains { checkIn in
                                    let checkInDateStr = dateFormatter.string(from: checkIn.checkInDate)
                                    return checkInDateStr == todayString && checkIn.userId == userId
                                }
                                
                                if checkedInToday {
                                    alreadyCheckedInPlanIds.append(plan.id)
                                }
                            }
                            
                            // After checking all plans, show appropriate UI
                            if alreadyCheckedInPlanIds.count == plans.count {
                                // All plans checked in today
                                self.showAlreadyCheckedInAlert()
                            } else {
                                // Show plan selection for check-in
                                self.showPlanSelectionForCheckIn(plans: plans, alreadyCheckedInPlanIds: alreadyCheckedInPlanIds)
                            }
                        }
                    }
                    
                case .failure(let error):
                    self.showAlert(message: "获取计划失败：\(error.localizedDescription)")
                }
            }
        }
    }
    
    private func showPlanSelectionForCheckIn(plans: [BettingPlan], alreadyCheckedInPlanIds: [String]) {
        // 过滤出进行中的计划，且未打卡的
        let availablePlans = plans.filter { 
            $0.status == .active && !alreadyCheckedInPlanIds.contains($0.id) 
        }
        
        guard !availablePlans.isEmpty else {
            showAlreadyCheckedInAlert()
            return
        }
        
        // 与安卓端保持一致：
        // 如果只有 1 个计划，直接进入打卡页面
        // 如果有多个计划，显示选择对话框
        if availablePlans.count == 1 {
            let plan = availablePlans.first!
            print("✅ Only one active plan, auto-select for check-in: \(plan.id)")
            navigateToCheckIn(planId: plan.id)
        } else {
            // 显示选择对话框
            showPlanSelectionDialog(plans: availablePlans)
        }
    }
    
    private func showPlanSelectionDialog(plans: [BettingPlan]) {
        let alert = UIAlertController(title: "选择计划", message: "请选择要进行打卡的计划", preferredStyle: .actionSheet)
        
        for plan in plans {
            let planName = plan.creatorNickname ?? plan.creatorEmail ?? "计划 \(plan.id.prefix(8))"
            alert.addAction(UIAlertAction(title: planName, style: .default) { [weak self] _ in
                self?.navigateToCheckIn(planId: plan.id)
            })
        }
        
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        present(alert, animated: true)
    }
    
    private func showAlreadyCheckedInAlert() {
        let alert = UIAlertController(
            title: "今日已打卡",
            message: "您今天已经完成所有计划的打卡了，明天再来吧！",
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "好的", style: .default))
        present(alert, animated: true)
    }
    
    private func navigateToCheckIn(planId: String) {
        // Navigate to Plans tab first
        tabBarController?.selectedIndex = 2
        
        // Then push check-in view controller after a short delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { [weak self] in
            guard let self = self,
                  let plansNav = self.tabBarController?.viewControllers?[2] as? UINavigationController,
                  let plansVC = plansNav.viewControllers.first as? PlansViewController else {
                return
            }
            
            // Create check-in VC with the selected plan
            let checkInVC = CheckInViewController(planId: planId)
            plansNav.pushViewController(checkInVC, animated: true)
        }
    }
    
    @objc private func badgesTapped() {
        guard let userId = UserDefaults.standard.string(forKey: "userId") else {
            return
        }
        let badgesVC = BadgesViewController(userId: userId)
        navigationController?.pushViewController(badgesVC, animated: true)
    }
    
    // MARK: - Helper
    
    private func showAlert(message: String) {
        let alert = UIAlertController(title: "错误", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }
}
