import UIKit

class BalanceViewController: UIViewController {
    
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
    
    private let balanceCardView: UIView = {
        let view = UIView()
        view.backgroundColor = .systemBlue
        view.layer.cornerRadius = 16
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private let availableBalanceLabel: UILabel = {
        let label = UILabel()
        label.text = "可用余额"
        label.font = .systemFont(ofSize: 14)
        label.textColor = .white.withAlphaComponent(0.9)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let availableAmountLabel: UILabel = {
        let label = UILabel()
        label.text = "¥0.00"
        label.font = .systemFont(ofSize: 36, weight: .bold)
        label.textColor = .white
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let frozenBalanceLabel: UILabel = {
        let label = UILabel()
        label.text = "冻结余额: ¥0.00"
        label.font = .systemFont(ofSize: 14)
        label.textColor = .white.withAlphaComponent(0.8)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let buttonStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .horizontal
        stackView.distribution = .fillEqually
        stackView.spacing = 16
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private let chargeButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("充值", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 16, weight: .semibold)
        button.backgroundColor = .systemGreen
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 12
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let withdrawButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("提现", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 16, weight: .semibold)
        button.backgroundColor = .systemOrange
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 12
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let transactionTitleLabel: UILabel = {
        let label = UILabel()
        label.text = "交易历史"
        label.font = .systemFont(ofSize: 18, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let tableView: UITableView = {
        let tableView = UITableView()
        tableView.register(TransactionCell.self, forCellReuseIdentifier: "TransactionCell")
        tableView.separatorStyle = .singleLine
        tableView.translatesAutoresizingMaskIntoConstraints = false
        return tableView
    }()
    
    private let emptyLabel: UILabel = {
        let label = UILabel()
        label.text = "暂无交易记录"
        label.font = .systemFont(ofSize: 16)
        label.textColor = .secondaryLabel
        label.textAlignment = .center
        label.isHidden = true
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let refreshControl = UIRefreshControl()
    
    // MARK: - Properties
    
    private let viewModel = BalanceViewModel()
    private var transactions: [Transaction] = []
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupBindings()
        loadData()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        // Refresh data when returning to this screen
        loadData(forceRefresh: true)
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        title = "我的余额"
        view.backgroundColor = .systemBackground
        
        // Add subviews
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        contentView.addSubview(balanceCardView)
        balanceCardView.addSubview(availableBalanceLabel)
        balanceCardView.addSubview(availableAmountLabel)
        balanceCardView.addSubview(frozenBalanceLabel)
        
        contentView.addSubview(buttonStackView)
        buttonStackView.addArrangedSubview(chargeButton)
        buttonStackView.addArrangedSubview(withdrawButton)
        
        contentView.addSubview(transactionTitleLabel)
        contentView.addSubview(tableView)
        contentView.addSubview(emptyLabel)
        
        // Setup table view
        tableView.delegate = self
        tableView.dataSource = self
        tableView.refreshControl = refreshControl
        
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
            
            balanceCardView.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 16),
            balanceCardView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            balanceCardView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            balanceCardView.heightAnchor.constraint(equalToConstant: 160),
            
            availableBalanceLabel.topAnchor.constraint(equalTo: balanceCardView.topAnchor, constant: 20),
            availableBalanceLabel.leadingAnchor.constraint(equalTo: balanceCardView.leadingAnchor, constant: 20),
            
            availableAmountLabel.topAnchor.constraint(equalTo: availableBalanceLabel.bottomAnchor, constant: 8),
            availableAmountLabel.leadingAnchor.constraint(equalTo: balanceCardView.leadingAnchor, constant: 20),
            
            frozenBalanceLabel.topAnchor.constraint(equalTo: availableAmountLabel.bottomAnchor, constant: 12),
            frozenBalanceLabel.leadingAnchor.constraint(equalTo: balanceCardView.leadingAnchor, constant: 20),
            
            buttonStackView.topAnchor.constraint(equalTo: balanceCardView.bottomAnchor, constant: 20),
            buttonStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            buttonStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            buttonStackView.heightAnchor.constraint(equalToConstant: 50),
            
            transactionTitleLabel.topAnchor.constraint(equalTo: buttonStackView.bottomAnchor, constant: 32),
            transactionTitleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            transactionTitleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            tableView.topAnchor.constraint(equalTo: transactionTitleLabel.bottomAnchor, constant: 16),
            tableView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor),
            tableView.heightAnchor.constraint(equalToConstant: 400),
            tableView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -20),
            
            emptyLabel.centerXAnchor.constraint(equalTo: tableView.centerXAnchor),
            emptyLabel.centerYAnchor.constraint(equalTo: tableView.centerYAnchor)
        ])
        
        // Add button actions
        chargeButton.addTarget(self, action: #selector(chargeButtonTapped), for: .touchUpInside)
        withdrawButton.addTarget(self, action: #selector(withdrawButtonTapped), for: .touchUpInside)
        refreshControl.addTarget(self, action: #selector(refreshData), for: .valueChanged)
    }
    
    private func setupBindings() {
        viewModel.onBalanceStateChanged = { [weak self] state in
            DispatchQueue.main.async {
                self?.handleBalanceState(state)
            }
        }
        
        viewModel.onTransactionsStateChanged = { [weak self] state in
            DispatchQueue.main.async {
                self?.handleTransactionsState(state)
            }
        }
    }
    
    // MARK: - Data Loading
    
    private func loadData(forceRefresh: Bool = false) {
        // TODO: Get actual user ID from TokenManager
        let userId = "current_user_id"
        
        viewModel.loadBalance(userId: userId, forceRefresh: forceRefresh)
        viewModel.loadTransactions(userId: userId, forceRefresh: forceRefresh)
    }
    
    @objc private func refreshData() {
        loadData(forceRefresh: true)
    }
    
    // MARK: - Actions
    
    @objc private func chargeButtonTapped() {
        let chargeVC = ChargeViewController()
        navigationController?.pushViewController(chargeVC, animated: true)
    }
    
    @objc private func withdrawButtonTapped() {
        let withdrawVC = WithdrawViewController()
        navigationController?.pushViewController(withdrawVC, animated: true)
    }
    
    // MARK: - State Handling
    
    private func handleBalanceState(_ state: BalanceState) {
        switch state {
        case .idle:
            break
            
        case .loading:
            break
            
        case .success(let balance):
            refreshControl.endRefreshing()
            availableAmountLabel.text = "¥\(String(format: "%.2f", balance.availableBalance))"
            frozenBalanceLabel.text = "冻结余额: ¥\(String(format: "%.2f", balance.frozenBalance))"
            
        case .error(let message):
            refreshControl.endRefreshing()
            showAlert(title: "加载失败", message: message)
        }
    }
    
    private func handleTransactionsState(_ state: TransactionsState) {
        switch state {
        case .idle:
            break
            
        case .loading:
            break
            
        case .success(let transactions):
            refreshControl.endRefreshing()
            self.transactions = transactions
            tableView.reloadData()
            
            emptyLabel.isHidden = !transactions.isEmpty
            tableView.isHidden = transactions.isEmpty
            
        case .error(let message):
            refreshControl.endRefreshing()
            showAlert(title: "加载失败", message: message)
        }
    }
    
    // MARK: - Helper Methods
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - UITableViewDelegate & UITableViewDataSource

extension BalanceViewController: UITableViewDelegate, UITableViewDataSource {
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return transactions.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "TransactionCell", for: indexPath) as! TransactionCell
        let transaction = transactions[indexPath.row]
        cell.configure(with: transaction)
        return cell
    }
    
    func tableView(_ tableView: UITableView, heightForRowAt indexPath: IndexPath) -> CGFloat {
        return 80
    }
}

// MARK: - TransactionCell

class TransactionCell: UITableViewCell {
    
    private let typeLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 16, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let dateLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 14)
        label.textColor = .secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let amountLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 18, weight: .bold)
        label.textAlignment = .right
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let statusLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 12)
        label.textAlignment = .right
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupUI() {
        contentView.addSubview(typeLabel)
        contentView.addSubview(dateLabel)
        contentView.addSubview(amountLabel)
        contentView.addSubview(statusLabel)
        
        NSLayoutConstraint.activate([
            typeLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 12),
            typeLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            
            dateLabel.topAnchor.constraint(equalTo: typeLabel.bottomAnchor, constant: 4),
            dateLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 20),
            
            amountLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 12),
            amountLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20),
            
            statusLabel.topAnchor.constraint(equalTo: amountLabel.bottomAnchor, constant: 4),
            statusLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -20)
        ])
    }
    
    func configure(with transaction: Transaction) {
        // Set type
        typeLabel.text = getTypeText(transaction.type)
        
        // Set date
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd HH:mm"
        dateLabel.text = dateFormatter.string(from: transaction.createdAt)
        
        // Set amount
        let prefix = getAmountPrefix(transaction.type)
        amountLabel.text = "\(prefix)¥\(String(format: "%.2f", transaction.amount))"
        amountLabel.textColor = getAmountColor(transaction.type)
        
        // Set status
        statusLabel.text = getStatusText(transaction.status)
        statusLabel.textColor = getStatusColor(transaction.status)
    }
    
    private func getTypeText(_ type: TransactionType) -> String {
        switch type {
        case .freeze: return "冻结"
        case .unfreeze: return "解冻"
        case .transfer: return "转账"
        case .withdraw: return "提现"
        case .refund: return "退款"
        }
    }
    
    private func getAmountPrefix(_ type: TransactionType) -> String {
        switch type {
        case .freeze, .withdraw: return "-"
        case .unfreeze, .transfer, .refund: return "+"
        }
    }
    
    private func getAmountColor(_ type: TransactionType) -> UIColor {
        switch type {
        case .freeze, .withdraw: return .systemRed
        case .unfreeze, .transfer, .refund: return .systemGreen
        }
    }
    
    private func getStatusText(_ status: TransactionStatus) -> String {
        switch status {
        case .pending: return "处理中"
        case .completed: return "已完成"
        case .failed: return "失败"
        }
    }
    
    private func getStatusColor(_ status: TransactionStatus) -> UIColor {
        switch status {
        case .pending: return .systemOrange
        case .completed: return .systemGreen
        case .failed: return .systemRed
        }
    }
}
