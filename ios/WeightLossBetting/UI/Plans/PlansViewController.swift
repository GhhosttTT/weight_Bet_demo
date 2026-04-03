import UIKit

class PlansViewController: UIViewController {
    
    // MARK: - Properties
    
    private let viewModel = PlanListViewModel()
    private var tableView: UITableView!
    private var refreshControl: UIRefreshControl!
    private var filterSegmentedControl: UISegmentedControl!
    private var emptyStateLabel: UILabel!
    private var loadingIndicator: UIActivityIndicatorView!
    
    private var userId: String? {
        return AuthRepository.shared.getCurrentUserId()
    }
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "我的对赌计划"
        view.backgroundColor = .systemBackground
        
        // Listen for navigation requests from notifications
        print("🔵 [PlansVC] 正在注册监听通知：navigateToNotificationType")
        // 导航通知已移到MainTabBarController全局监听，避免丢失
        print("✅ [PlansVC] 通知监听器已注册")

        setupUI()
        setupBindings()
        loadPlans()
    }
    
    deinit {
        NotificationCenter.default.removeObserver(self, name: .navigateToNotificationType, object: nil)
    }

    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        // Refresh plans when returning to this screen
        loadPlans(forceRefresh: true)
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        // Filter segmented control
        filterSegmentedControl = UISegmentedControl(items: ["全部", "待接受", "进行中", "已完成"])
        filterSegmentedControl.selectedSegmentIndex = 0
        filterSegmentedControl.addTarget(self, action: #selector(filterChanged), for: .valueChanged)
        filterSegmentedControl.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(filterSegmentedControl)
        
        // Table view
        tableView = UITableView(frame: .zero, style: .plain)
        tableView.delegate = self
        tableView.dataSource = self
        tableView.register(PlanCell.self, forCellReuseIdentifier: "PlanCell")
        tableView.rowHeight = UITableView.automaticDimension
        tableView.estimatedRowHeight = 120
        tableView.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(tableView)
        
        // Refresh control
        refreshControl = UIRefreshControl()
        refreshControl.addTarget(self, action: #selector(handleRefresh), for: .valueChanged)
        tableView.refreshControl = refreshControl
        
        // Empty state label
        emptyStateLabel = UILabel()
        emptyStateLabel.text = "暂无对赌计划"
        emptyStateLabel.textAlignment = .center
        emptyStateLabel.textColor = .secondaryLabel
        emptyStateLabel.font = .systemFont(ofSize: 16)
        emptyStateLabel.isHidden = true
        emptyStateLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(emptyStateLabel)
        
        // Loading indicator
        loadingIndicator = UIActivityIndicatorView(style: .large)
        loadingIndicator.hidesWhenStopped = true
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(loadingIndicator)
        
        // Create plan button
        let createButton = UIBarButtonItem(barButtonSystemItem: .add, target: self, action: #selector(createPlanTapped))
        navigationItem.rightBarButtonItem = createButton
        
        // Layout
        NSLayoutConstraint.activate([
            filterSegmentedControl.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 8),
            filterSegmentedControl.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            filterSegmentedControl.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            
            tableView.topAnchor.constraint(equalTo: filterSegmentedControl.bottomAnchor, constant: 8),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            emptyStateLabel.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            emptyStateLabel.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            
            loadingIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    private func setupBindings() {
        viewModel.onPlansUpdated = { [weak self] in
            self?.tableView.reloadData()
            self?.updateEmptyState()
        }
        
        viewModel.onError = { [weak self] message in
            self?.showError(message)
        }
        
        viewModel.onLoadingChanged = { [weak self] isLoading in
            if isLoading {
                self?.loadingIndicator.startAnimating()
            } else {
                self?.loadingIndicator.stopAnimating()
                self?.refreshControl.endRefreshing()
            }
        }
    }
    
    // MARK: - Actions
    
    @objc private func filterChanged() {
        let status: PlanStatus?
        switch filterSegmentedControl.selectedSegmentIndex {
        case 1: status = .pending
        case 2: status = .active
        case 3: status = .completed
        default: status = nil
        }
        viewModel.filterPlans(by: status)
    }
    
    @objc private func handleRefresh() {
        loadPlans(forceRefresh: true)
    }
    
    @objc private func createPlanTapped() {
        let createVC = CreatePlanViewController()
        let navController = UINavigationController(rootViewController: createVC)
        present(navController, animated: true)
    }
    
    // MARK: - Private Methods
    
    private func loadPlans(forceRefresh: Bool = false) {
        guard let currentUserId = userId, !currentUserId.isEmpty else {
            print("❌ [PlansVC] User ID is empty, cannot load plans")
            // Don't show error if user is not logged in yet
            return
        }
        print("🔵 [PlansVC] Loading plans for user: \(currentUserId)")
        viewModel.loadPlans(userId: currentUserId, forceRefresh: forceRefresh)
    }
    
    private func updateEmptyState() {
        emptyStateLabel.isHidden = !viewModel.filteredPlans.isEmpty
        tableView.isHidden = viewModel.filteredPlans.isEmpty
    }
    
    private func showError(_ message: String) {
        let alert = UIAlertController(title: "错误", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }

    // MARK: - Notification Navigation (已移到MainTabBarController全局处理)
    
    // MARK: - Plans Update Handler
    
    @objc private func handlePlansUpdated() {
        print("📢 [PlansVC] 收到 plansUpdated 通知，刷新列表...")
        loadPlans(forceRefresh: true)
    }
}

// MARK: - UITableViewDataSource

extension PlansViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return viewModel.filteredPlans.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "PlanCell", for: indexPath) as! PlanCell
        let plan = viewModel.filteredPlans[indexPath.row]
        cell.configure(with: plan)
        return cell
    }
}

// MARK: - UITableViewDelegate

extension PlansViewController: UITableViewDelegate {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let plan = viewModel.filteredPlans[indexPath.row]
        let detailVC = PlanDetailViewController(planId: plan.id)
        navigationController?.pushViewController(detailVC, animated: true)
    }
}

// MARK: - PlanCell

class PlanCell: UITableViewCell {
    
    private let statusLabel = UILabel()
    private let betAmountLabel = UILabel()
    private let dateRangeLabel = UILabel()
    private let goalLabel = UILabel()
    
    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupUI() {
        statusLabel.font = .boldSystemFont(ofSize: 14)
        statusLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(statusLabel)
        
        betAmountLabel.font = .systemFont(ofSize: 18, weight: .semibold)
        betAmountLabel.textColor = .systemRed
        betAmountLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(betAmountLabel)
        
        dateRangeLabel.font = .systemFont(ofSize: 14)
        dateRangeLabel.textColor = .secondaryLabel
        dateRangeLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(dateRangeLabel)
        
        goalLabel.font = .systemFont(ofSize: 14)
        goalLabel.textColor = .label
        goalLabel.numberOfLines = 0
        goalLabel.translatesAutoresizingMaskIntoConstraints = false
        contentView.addSubview(goalLabel)
        
        NSLayoutConstraint.activate([
            statusLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 12),
            statusLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            
            betAmountLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 12),
            betAmountLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            dateRangeLabel.topAnchor.constraint(equalTo: statusLabel.bottomAnchor, constant: 8),
            dateRangeLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            dateRangeLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            
            goalLabel.topAnchor.constraint(equalTo: dateRangeLabel.bottomAnchor, constant: 8),
            goalLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            goalLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            goalLabel.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -12)
        ])
    }
    
    func configure(with plan: BettingPlan) {
        // Status
        switch plan.status {
        case .pending:
            statusLabel.text = "待接受"
            statusLabel.textColor = .systemOrange
        case .pendingConfirmation:
            statusLabel.text = "待二次确认"
            statusLabel.textColor = .systemPurple
        case .active:
            statusLabel.text = "进行中"
            statusLabel.textColor = .systemGreen
        case .completed:
            statusLabel.text = "已完成"
            statusLabel.textColor = .systemGray
        case .cancelled:
            statusLabel.text = "已取消"
            statusLabel.textColor = .systemGray
        case .rejected:
            statusLabel.text = "已拒绝"
            statusLabel.textColor = .systemGray
            
        case .expired:
            statusLabel.text = "已过期"
            statusLabel.textColor = .systemGray
        }
        
        // Bet amount
        betAmountLabel.text = "¥\(String(format: "%.2f", plan.betAmount))"
        
        // Date range
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        let startDateStr = dateFormatter.string(from: plan.startDate)
        let endDateStr = dateFormatter.string(from: plan.endDate)
        dateRangeLabel.text = "\(startDateStr) 至 \(endDateStr)"
        
        // Goal
        let weightLoss = plan.creatorTargetWeightLoss
        goalLabel.text = "目标减重：\(String(format: "%.1f", weightLoss))kg"
    }
}
